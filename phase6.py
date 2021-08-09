#!/usr/bin/env python3

"""This phase makes all the addressOffsets relative to the respective cluster"""

from lxml import etree
import sys
import logging
from logging import debug, info, warning, error, critical
from collections import OrderedDict
from pprint import pprint

def eval_int(element):
    """ Given a SVD node, extracts the integer from its text. """
    s = element.text
    if s.startswith("0x"):
        return int(s[len("0x"):], 16)
    else:
        return int(s)

def extract_addressOffset_rec(root):
    """ Extract addressOffset of ROOT.  If that's not possible, finds a child register that has it, recursively.  A cluster without addressOffset is thus represented by its lowest-addressOffset child register """
    attr_node = root.find("addressOffset")
    if attr_node is None:
        attr_node = root.find("baseAddress")
    if attr_node is not None:
        addressOffset = eval_int(attr_node)
        if root.tag == "cluster":
            # Assume that we don't yet have any offsets in the cluster.
            assert addressOffset == 0
        else:
            return addressOffset
    #print(etree.tostring(root, pretty_print=True), file=sys.stderr)
    try:
        addressOffset = min(o for o in [extract_addressOffset_rec(child) for child in root if child.tag not in ["name", "addressOffset"]] if o is not None)
    except ValueError:
        print(etree.tostring(root).decode("utf-8"), file=sys.stderr)
        raise
    return addressOffset

def fixup_cluster_baseAddress(root, container_node, indent=0):
    """ Given a tree with a lot of registers and clusters, moves up the addressOffset of the lowest-addressOffset register to the containing cluster (or peripheral if there is no cluster).  This is done recursively, depth-first.  Assumption is that the clusters and peripherals don't have an address yet. """
    if root.tag != "register": # not leaf
        nodes = root
        if root.tag in ["registers", "cluster"]:
            nodes = list(sorted([c for c in root if c.tag not in ["name", "addressOffset"]], key=extract_addressOffset_rec))
        for child in nodes:
            fixup_cluster_baseAddress(child, root if root.tag in ["cluster", "peripheral"] else container_node, indent + 2)
        if root.tag in ["cluster", "peripheral"]:
            # if <newAddressOffset> exists, move it into <addressOffset> instead.
            newAddressOffset = root.find("newAddressOffset")
            if newAddressOffset is not None:
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
                # Default the container'\s <newAddressOffset> to the child's addressOffset [possibly relative]
                container_newAddressOffset = etree.Element("newAddressOffset")
                container_newAddressOffset.text = "0x{:X}".format(container_addressOffset_value + addressOffset)
                container_node.append(container_newAddressOffset)
            # Make our own addressOffset relative to that container <newAddressOffset> instead of that container <addressOffset> like it was
            child_addressOffset.text = "0x{:X}".format(addressOffset - (eval_int(container_newAddressOffset) - container_addressOffset_value))
            assert not child_addressOffset.text.startswith("0x-"), etree.tostring(child)

logging.basicConfig(level=logging.INFO)
tree = etree.parse(sys.stdin if len(sys.argv) == 1 else open(sys.argv[-1]))
root = tree.getroot()

# Make all the offsets relative.
fixup_cluster_baseAddress(root, root)

tree.write(sys.stdout.buffer, pretty_print=True)
sys.stdout.flush()
