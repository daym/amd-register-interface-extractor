#!/usr/bin/env python3

# Assumption: Input SVD has only absolute addresses--and those are in <addressOffset>

from lxml import etree
import sys

def eval_int(element):
    """ Given a SVD node, extracts the integer from its text. """
    s = element.text
    if s.startswith("0x"):
        return int(s[len("0x"):], 16)
    else:
        return int(s)

"""
Let's say there's a hypothetical peripheral FOO with these registers:

   A at offset 0
   B at offset 4

and there are 3 instances of that peripheral.

Then, phase3 (and, really, AMD) arranges the registers like this:

   A:
     instance0 at offset 0    (derivedFrom not set)
     instance1 at offset 8    (derivedFrom set to A.instance0)
     instance2 at offset 16   (derivedFrom set to A.instance0)
   B:
     instance0 at offset 4    (derivedFrom not set)
     instance1 at offset 12   (derivedFrom set to B.instance0)
     instance2 at offset 20   (derivedFrom set to B.instance0)

What we ideally want is the first structure.  Phase4 tries to collect clusters together in order to get the first structure.

To that end, if this node has no derivedFrom, it's good to know what the first item derived from this one is going to be.
For example, after A.instance0 there comes A.instance1, and that gives you the maximal cluster size for this peripheral cluster.
"""

def traverse(source_root, parent_name):
    """ Traverses source_root and modifies it in place to cluster things together that belong together. """
    has_any_register = len([child for child in source_root if child.tag == "register"]) > 0
    if has_any_register:
        registers = sorted((eval_int(child.find("addressOffset")), eval_int(child.find("size")), child.find("name").text, child) for child in source_root if child.tag == "register")
        addressOffset = -1
        cluster = None
        addressLimit = 2**32
        def add_to_cluster(x_child):
            source_root.remove(x_child)
            cluster.append(x_child)
        def update_addressLimit(x_child):
            nonlocal addressLimit
            x_child_name = x_child.find("name").text
            assert x_child_name
            found = False
            instances = [y_child for (_, _, _, y_child) in registers if y_child is x_child or y_child.attrib.get("derivedFrom") == x_child_name]
            i = instances.index(x_child)
            if i + 1 < len(instances):
                next_register = instances[i + 1]
                assert next_register.tag == "register"
                next_register_addressOffset = eval_int(next_register.find("addressOffset"))
                if next_register_addressOffset > x_addressOffset:
                    assert next_register_addressOffset > x_addressOffset, (next_register.find("name").text, x_child_name)
                    if next_register_addressOffset < addressLimit:
                        addressLimit = next_register_addressOffset
        def finish_cluster():
            nonlocal cluster
            nonlocal addressLimit
            if cluster is not None and len([node for node in cluster if node.tag != "name"]) > 0:
                if len([node for node in cluster if node.tag != "name"]) == 1:
                    for node in cluster:
                        if node.tag == "name":
                            pass
                        elif node.tag == "register":
                            cluster.remove(node)
                            source_root.append(node)
                            break
                        else:
                            assert False, node.tag
                else:
                    source_root.append(cluster)
            cluster = etree.Element("cluster")
            addressLimit = 2**32
        def create_cluster_name(name):
            cluster_name = etree.Element("name")
            if name.startswith(parent_name):
                name = name[len(parent_name):]
                while name.startswith("_"):
                    name = name[1:]
            else:
                parent_basename = parent_name.split("_")[-1]
                if name.replace("_", "").startswith(parent_basename):
                    name = name.replace("_", "")[len(parent_basename):]
                    while name.startswith("_"):
                        name = name[1:]
            cluster_name.text = name + "X" # TODO: Be nicer.
            cluster.append(cluster_name)
        finish_cluster()
        first_addressOffset, first_size, first_name, first_child = registers[0]
        for x_addressOffset, x_size, x_name, x_child in registers:
            dim = x_child.find("dim")
            if dim is not None:
                x_size = x_size * eval_int(dim)
            if x_child.attrib.get("derivedFrom") is None:
                update_addressLimit(x_child)
            if x_addressOffset < addressOffset or x_addressOffset > addressOffset + 8 or x_addressOffset >= addressLimit: # next register instance is not where we expected it to be, or we are outside that instance now.
                finish_cluster()
                create_cluster_name(x_name)
                addressOffset = x_addressOffset
            add_to_cluster(x_child)
            addressOffset = addressOffset + x_size//8
        finish_cluster()
        if len([x_child for x_child in source_root]) == 1 and source_root[0].tag == "cluster": # There's only one cluster
            for x_child in source_root:
                source_root.remove(x_child)
                for y_child in x_child:
                    if y_child.tag in ["cluster", "register"]:
                        source_root.append(y_child)
                break
    else:
        name = source_root.find("name")
        if name is not None:
            name = name.text
        else:
            name = parent_name
        for child in source_root:
            traverse(child, name)

tree = etree.parse(sys.stdin)
root = tree.getroot()

traverse(root, "")

tree.write(sys.stdout.buffer, pretty_print=True)
sys.stdout.flush()
