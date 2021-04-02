#!/usr/bin/env python3

# Assumption: Input SVD has only absolute addresses--and those are in <addressOffset>

from lxml import etree
import sys
import settings
import logging
from logging import debug, info, warning, error, critical

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

def traverse(source_root, parent_name, peripheral_name):
    """ Traverses source_root and modifies it in place to cluster things together that belong together. """
    has_any_register = len([child for child in source_root if child.tag == "register"]) > 0
    if has_any_register:
        registers = sorted((eval_int(child.find("addressOffset")), eval_int(child.find("size")), child.find("name").text, child) for child in source_root if child.tag == "register")
        addressOffset = -1
        cluster = None
        addressLimits = []
        def add_to_cluster(x_child):
            source_root.remove(x_child)
            cluster.append(x_child)
        def update_addressLimits(x_child):
            nonlocal addressLimits
            if x_child.attrib.get("derivedFrom") is not None:
                return
            #addressLimits = []
            x_child_name = x_child.find("name").text
            assert x_child_name
            found = False
            instances = [y_child for (_, _, _, y_child) in registers if y_child is x_child or y_child.attrib.get("derivedFrom") == x_child_name]
            i = instances.index(x_child)
            for j in range(i + 1, len(instances)):
                next_register = instances[j]
                assert next_register.tag == "register"
                next_register_addressOffset = eval_int(next_register.find("addressOffset"))
                if next_register_addressOffset > x_addressOffset:
                    assert next_register_addressOffset > x_addressOffset, (next_register.find("name").text, x_child_name)
                    while j >= len(addressLimits):
                        addressLimits.append(2**32)
                    if next_register_addressOffset < addressLimits[j]:
                        addressLimits[j] = next_register_addressOffset
        def finish_cluster():
            nonlocal cluster
            nonlocal addressLimits
            if cluster is not None and len([node for node in cluster if node.tag != "name"]) > 0:
                if len([node for node in cluster if node.tag != "name"]) == 1:
                    for node in cluster:
                        if node.tag == "name":
                            pass
                        elif node.tag == "register":
                            cluster.remove(node)
                            source_root.append(node)
                            cluster_name = cluster.find("name").text
                            if not cluster_name.endswith("_unsorted"):
                                info("Eliding cluster {!r} grouping because there's only one node in it".format(cluster_name))
                            else:
                                # generated and then elided agai
                                pass # no one cares

                            break
                        else:
                            assert False, node.tag
                else:
                    source_root.append(cluster)
            cluster = etree.Element("cluster")
            addressLimits = []
        def calculate_cluster_name(name, fallback=True):
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
            return settings.phase4_cluster_names.get(peripheral_name, {}).get(name, (name + "_unsorted") if fallback else None)
        finish_cluster()
        addressOffset, first_size, first_name, first_child = registers[0]
        new_cluster_name_text = calculate_cluster_name(first_name, True)
        cluster_name = etree.Element("name")
        cluster_name.text = new_cluster_name_text
        cluster.append(cluster_name)
        previous_addressOffset = -1
        for x_addressOffset, x_size, x_name, x_child in registers:
            #if x_name.find("FabricIndirectConfigAccessDataLo_n0") != -1:
            #    import pdb
            #    pdb.set_trace()
            dim = x_child.find("dim")
            if dim is not None:
                x_size = x_size * eval_int(dim)
            update_addressLimits(x_child)
            new_cluster_name_text = calculate_cluster_name(x_name, False)
            if x_addressOffset == previous_addressOffset:
                assert new_cluster_name_text is None
            elif x_addressOffset < addressOffset or x_addressOffset > addressOffset + 8 or (addressLimits != [] and x_addressOffset >= addressLimits[0]) or new_cluster_name_text is not None: # next register instance is not where we expected it to be, or we are outside that instance now, or user requested new cluster.
                new_cluster_name_text = calculate_cluster_name(x_name, True)
                if addressLimits != [] and x_addressOffset >= addressLimits[0]:
                    #new_cluster_name_text = new_cluster_name_text + "_{}".format(addressLimits[0])
                    addressLimits = addressLimits[1:]
                cluster_name = cluster.find("name") if cluster is not None else None
                cluster_name_text = cluster_name.text if cluster_name is not None else None
                if cluster_name_text != new_cluster_name_text:
                    finish_cluster()
                    cluster_name = etree.Element("name")
                    cluster_name.text = new_cluster_name_text
                    cluster.append(cluster_name)
                else: # if x_addressOffset >= addressLimit:
                    addressLimits = []
                    update_addressLimits(x_child)
                addressOffset = x_addressOffset
            add_to_cluster(x_child)
            previous_addressOffset = x_addressOffset
            addressOffset = x_addressOffset + x_size//8
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
            if source_root.tag == "peripheral":
                peripheral_name = name
        else:
            name = parent_name
        for child in source_root:
            traverse(child, name, peripheral_name)

def fixup_cluster_baseAddress(root, container_node, indent=0):
    """ Given a tree with a lot of registers and clusters, moves up the addressOffset of the first register to the containing cluster (or peripheral if there is no cluster).  This is done recursively, depth-first.  Assumption is that the clusters and peripherals don't have an address yet. """
    if root.tag != "register": # leaf
        for child in root:
            fixup_cluster_baseAddress(child, root if root.tag in ["cluster", "peripheral"] else container_node, indent + 2)
        if root.tag in ["cluster", "peripheral"]:
            newAddressOffset = root.find("newAddressOffset")
            addressOffset = root.find("baseAddress" if root.tag == "peripheral" else "addressOffset")
            if addressOffset is None:
                addressOffset = etree.Element("baseAddress" if root.tag == "peripheral" else "addressOffset")
                root.append(addressOffset)
            addressOffset.text = newAddressOffset.text
            root.remove(newAddressOffset)
    child = root
    if child.tag in ["register", "cluster"]:
        try:
            child_addressOffset = child.find("addressOffset")
            addressOffset = eval_int(child_addressOffset)
        except:
            info("Child for failure below is: {} {!r}".format(child.tag, child.find("name").text))
            raise
        if container_node is not None:
            container_addressOffset = container_node.find("baseAddress") if container_node.tag == "peripheral" else container_node.find("addressOffset")
            container_addressOffset_value = eval_int(container_addressOffset) if container_addressOffset is not None else 0
            container_newAddressOffset = container_node.find("newAddressOffset")
            if container_newAddressOffset is None:
                container_newAddressOffset = etree.Element("newAddressOffset")
                container_newAddressOffset.text = "0x{:X}".format(container_addressOffset_value + addressOffset)
                container_node.append(container_newAddressOffset)
            child_addressOffset.text = "0x{:X}".format(addressOffset - (eval_int(container_newAddressOffset) - container_addressOffset_value))

logging.basicConfig(level=logging.INFO)
tree = etree.parse(sys.stdin if len(sys.argv) == 1 else open(sys.argv[-1]))
root = tree.getroot()

traverse(root, "", None)

# Make all the offsets relative.
fixup_cluster_baseAddress(root, root)

tree.write(sys.stdout.buffer, pretty_print=True)
sys.stdout.flush()
