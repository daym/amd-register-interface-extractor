#!/usr/bin/env python3

"""This phase infers arrays when there are large clusters of similar things around"""

import copy
from lxml import etree
import sys
import logging
from logging import debug, info, warning, error, critical
from collections import OrderedDict
from pprint import pprint
import re

re_index = re.compile(r"^([0-9]+)$")

def eval_int(element):
    """ Given a SVD node, extracts the integer from its text. """
    s = element.text
    if s.startswith("0x"):
        return int(s[len("0x"):], 16)
    else:
        return int(s)

def path_string(node):
    """ Returns the path to the given NODE as a str. """
    if node is None:
        return ""
    else:
        return path_string(node.getparent()) + "/" + (node.find("name").text if node.find("name") is not None else "*")

registers = {}

def register_registers(root):
    """ Starting at ROOT, finds all <register>s and registers them in REGISTERS, recursively. """
    if root.tag == "register":
        name_node = root.find("name")
        name = name_node.text if name_node is not None else None
        registers[name] = root
    for child in root:
        register_registers(child)

def normalize(root):
    # TODO: Normalize (at least down to the actual registers)
    # TODO: Order tags in a standard way (any way)
    # TODO: If <displayName> exists, get rid of <name>
    for tag in ["name", "displayName", "description", "addressOffset", "size"]:
        orig = root.find(tag)
        if orig is not None:
            root.append(orig) # This re-inserts the Element at an ordered location
    if root.find("displayName") is not None:
        name_node = root.find("name")
        if name_node is not None:
            root.remove(name_node)
    for child in root:
        normalize(child)
    return root

def extract_array_element_contents(root):
    """ Returns a new XML element with just the actual child elements (excluding pseudo attributes). """
    result = etree.Element(root.tag)
    for child in root:
        if child.tag in ["name", "addressOffset"]: # skip array index and addressOffset--both of which are very likely different
            continue
        # This also unlinks the child from the original document!
        result.append(child)
    return result

def xml_elements_eqP(a, b):
    """ Returns whether A and B are equal. """
    return etree.tostring(a, pretty_print=False) == etree.tostring(b, pretty_print=False)

def flatten(root):
    """ If there's a derivedFrom, resolves it.  FIXME: Recursively """
    derivedFrom = root.attrib.get("derivedFrom")
    if derivedFrom is not None:
        reference = registers[derivedFrom]
        del root.attrib["derivedFrom"]
        # Add stuff from REFERENCE that we don't already have
        known_attrs = [child.tag for child in root]
        # known_attrs == ['name', 'addressOffset', 'size', 'displayName']
        #print("KNOWN", known_attrs)
        for child in reference:
            if child.tag not in known_attrs:
                root.append(copy.deepcopy(child))
    for child in root:
        flatten(child)
    return root

def create_array_cluster(addressOffset, displayName, dim, dimIncrement, dimIndex, name):
    result = etree.Element("cluster")
    addressOffset_node = etree.Element("addressOffset")
    addressOffset_node.text = "0x{:x}".format(addressOffset)
    result.append(addressOffset_node)
    displayName_node = etree.Element("displayName")
    assert displayName is None
    displayName_node.text = "QQQ" # displayName # FIXME if that's None, it does not fail.
    result.append(displayName_node)
    dim_node = etree.Element("dim")
    dim_node.text = str(dim)
    result.append(dim_node)
    dimIncrement_node = etree.Element("dimIncrement")
    dimIncrement_node.text = "0x{:x}".format(dimIncrement)
    result.append(dimIncrement_node)
    dimIndex_node = etree.Element("dimIndex")
    dimIndex_node.text = dimIndex
    result.append(dimIndex_node)
    name_node = etree.Element("name")
    name_node.text = name
    result.append(name_node)
    return result

def calculate_increments(items):
    reference = None
    dimIncrements = []
    for item in items:
        if reference is None:
             reference = item
        dimIncrement = item - reference
        reference = item
        dimIncrements.append(dimIncrement)
    return dimIncrements[1:]

def infer_arrays(root):
    name_node = root.find("name")
    name = name_node.text if name_node is not None else None
    root_name = name
    indexed_stuff = {}
    has_indexed_child = False
    has_non_indexed_child = False
    addresses_disjunct = True
    for child in root:
        if child.tag in ["name", "addressOffset", "size", "displayName"]: # logically those are attributes
            continue
        name_node = child.find("name")
        name = name_node.text if name_node is not None else None
        if name is not None and re_index.match(name):
            # FIXME: assert mode is None or mode == "indexing", root_name
            has_indexed_child = True
            assert root.tag == "cluster"
            assert child.tag == "cluster"
            assert root_name is not None and root_name.startswith("_"), etree.tostring(root, pretty_print=True).decode("utf-8")
            #print(root.find("name").text, name)
            index = int(name)
            child_addressOffset = eval_int(child.find("addressOffset"))
            if child_addressOffset in indexed_stuff:
                logging.warning("Same value for addressOffset ({!r}) is used multiple times, among others at {!r}".format(child.find("addressOffset").text, path_string(child)))
                addresses_disjunct = False
            indexed_stuff[child_addressOffset] = normalize(flatten(copy.deepcopy(child))), index, child
        else:
            #print("NON-INDEXED")
            #print(etree.tostring(child, pretty_print=True))
            has_non_indexed_child = True
            infer_arrays(child)
    if root_name is not None and root_name.startswith("_"):
        assert has_indexed_child
    if has_indexed_child or has_non_indexed_child:
        assert has_indexed_child ^ has_non_indexed_child, path_string(root)
    if indexed_stuff and addresses_disjunct:
        all_similar = True
        reference_element = None
        for child_addressOffset, (flattened_child, index, child) in sorted(indexed_stuff.items()):
            #print(index)
            contents = extract_array_element_contents(flattened_child)
            if reference_element is None:
                reference_element = contents
            if not xml_elements_eqP(reference_element, contents):
                all_similar = False
            #print(etree.tostring(contents, pretty_print=True).decode("utf-8"))
        if all_similar:
            child_addressOffsets = [child_addressOffset for child_addressOffset, _ in sorted(indexed_stuff.items())]
            increments = calculate_increments(child_addressOffsets)
            if len(set(increments)) == 1:
                dimIncrement = increments[0]
                dimIndex = [index for child_addressOffset, (flattened_child, index, child) in sorted(indexed_stuff.items())]
                assert len(dimIndex) == len(set(dimIndex))
                logging.info("Inferring array for {!r}.".format(path_string(root)))
                # Remove the array elements from XML; FIXME: Insert array element to correct place.
                array_cluster = create_array_cluster(eval_int(root.find("addressOffset")), root.find("displayName"), dim=len(dimIndex), dimIncrement=dimIncrement, dimIndex=",".join([str(x) for x in dimIndex]), name="[%s]")
                for child in reference_element:
                    assert child.tag != "name"
                    array_cluster.append(child)
                first = True
                for child_addressOffset, (flattened_child, index, child) in sorted(indexed_stuff.items()):
                    if first:
                        first = False
                        # Insert array_cluster before where the elements were
                        child.addprevious(array_cluster)
                    root.remove(child)
            else:
                logging.warning("Not inferring {!r} since there are different increments between consecutive addressOffsets of the array elements ({!r}).".format(path_string(root), increments))
        else:
            logging.warning("Not inferring {!r} since there are too many differences between the array elements.".format(path_string(root)))

logging.basicConfig(level=logging.INFO)
parser = etree.XMLParser(remove_blank_text=True)
#with (sys.stdin if len(sys.argv) == 1 else open(sys.argv[-1])) as f:
#    data = f.read()
#tree = etree.XML(data, parser=parser)
#print(tree)

tree = etree.parse(sys.stdin if len(sys.argv) == 1 else open(sys.argv[-1]), parser=parser)
root = tree.getroot()

# Make all the offsets relative.
register_registers(root)
infer_arrays(root)

tree.write(sys.stdout.buffer, pretty_print=True)
sys.stdout.flush()
