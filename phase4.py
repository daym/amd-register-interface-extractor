#!/usr/bin/env python3

from lxml import etree
import sys

def eval_int(element):
    """ Given a SVD node, extracts the integer from its text. """
    s = element.text
    if s.startswith("0x"):
        return int(s[len("0x"):], 16)
    else:
        return int(s)

def traverse(source_root):
    """ Traverses source_root and modifies it in place to cluster things together that belong together. """
    has_any_register = len([child for child in source_root if child.tag == "register"]) > 0
    if has_any_register:
        registers = sorted((eval_int(child.find("addressOffset")), eval_int(child.find("size")), child.find("name").text, child) for child in source_root if child.tag == "register")
        #first_addressOffset, first_size, first_name, first_child = registers[0]
        addressOffset = -1
        cluster = None
        def add_to_cluster(x_child):
            source_root.remove(x_child)
            cluster.append(x_child)
        def finish_cluster():
            nonlocal cluster
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
        finish_cluster()
        for x_addressOffset, x_size, x_name, x_child in registers:
            dim = x_child.find("dim")
            if dim is not None:
                x_size = x_size * eval_int(dim)
            if x_addressOffset != addressOffset:
                finish_cluster()
                cluster_name = etree.Element("name")
                cluster_name.text = x_name + "X" # TODO: Be nicer.
                cluster.append(cluster_name)
                addressOffset = x_addressOffset
            add_to_cluster(x_child)
            addressOffset = addressOffset + x_size//8
        finish_cluster()
    else:
        for child in source_root:
            traverse(child)

tree = etree.parse(sys.stdin)
root = tree.getroot()

traverse(root)

tree.write(sys.stdout.buffer, pretty_print=True)
sys.stdout.flush()
