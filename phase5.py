#!/usr/bin/env python3

"""This phase creates clusters and subclusters for all the instances of a register as appropriate.

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

What we want is the following structure:

   instance
      0
        A
        B
      1
        A
        B
      2
        A
        B

This phase tries to build such a structure.
"""

from lxml import etree
import sys
import settings
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

def isolate_array_spec(name):
    """
    >>> isolate_array_spec("a_n0_ccd1")
    ["a", ("_n", 0), ("_ccd", 1)]
    >>> isolate_array_spec("STATUS_nbio3_instNBIF2")
    [('_nbio', 3), ('_instNBIF', 2)])
    """
    levels = []
    while True:
        matched_any = False
        for pattern in settings.phase4_array_inference_patterns:
            match = pattern.match(name)
            if match:
                matched_any = True
                name, subname, index = match.groups()
                index = int(index.strip()) if index else 0
                levels.append((subname, index))
                break
        if not matched_any:
            break
    return name, list(reversed(levels))

def first_register_address(cluster_or_register):
    """ Given a cluster or register, figures out the addressOffset of the first register--walking the clusters if necessary. """
    if cluster_or_register.tag == "register":
        return eval_int(child.find("addressOffset").text)
    elif cluster_or_register.tag == "cluster":
        for child in cluster_or_register:
            result = first_register_address(cluster_or_register)
            if result is not None:
                return result
    return None

def create_cluster(name):
    cluster = etree.Element("cluster")
    name_node = etree.Element("name")
    name_node.text = name
    cluster.append(name_node)
    addressOffset_node = etree.Element("addressOffset") # it is mandatory
    addressOffset_node.text = "0x0"
    cluster.append(addressOffset_node)
    return cluster

def create_displayName(name):
    result = etree.Element("displayName")
    result.text = name
    return result

def infer_arrays(root):
    """ Given a container cluster, infers arrays inside and exposes them as "dim"ed subclusters.  Note that this mostly identifies INSTANCES--we don't care about other arrays (it wouldn't be safe enough to identify anyway).
        Side-effect: Modifies ROOT's children in-place """
    children = [child for child in root if child.tag in ["register", "cluster"]]
    similar_children = OrderedDict()
    similar_shape_groups = OrderedDict()
    for child in children:
        assert child.tag != "cluster"
        group_tag = child.attrib.get("derivedFrom") or child.find("name").text
        group_tag, indices = isolate_array_spec(group_tag)
        shape = tuple(name for name, index in indices)
        if shape not in similar_shape_groups:
            similar_shape_groups[shape] = []
        similar_shape_groups[shape].append(child)
        if group_tag not in similar_children:
            similar_children[group_tag] = []
        similar_children[group_tag].append(child)
        root.remove(child)

    target_clusters = {(): root}
    def resolve_indices(indices):
        path = []
        for k, v in indices:
            path.append(k)
            path.append(v)

        previous_cluster = root
        prefix = []
        for item in path:
            cluster_name = str(item)
            prefix.append(cluster_name)
            if tuple(prefix) not in target_clusters:
                cluster = create_cluster(cluster_name)
                target_clusters[tuple(prefix)] = cluster
                previous_cluster.append(cluster)
            else:
                cluster = target_clusters[tuple(prefix)]
            previous_cluster = cluster
        return previous_cluster

    for shape, registers in similar_shape_groups.items():
        for register in registers:
            raw_name = register.find("name").text
            name, indices = isolate_array_spec(raw_name)
            assert register.find("displayName") is None, register
            if name != raw_name:
                register.append(create_displayName(name))
            cluster = resolve_indices(indices)
            cluster.append(register)

def infer_arrays0(root):
    """ Given a container cluster, infers arrays inside and exposes them as "dim"ed subclusters.  Note that this mostly identifies INSTANCES--we don't care about other arrays (it wouldn't be safe enough to identify anyway).
        Side-effect: Modifies ROOT's children in-place """
    for child in root:
        assert child.tag != "cluster"
        if child.tag in ["cluster", "register"]:
            name, indices = isolate_array_spec(child.find("name").text)

            derivedFrom = child.attrib.get("derivedFrom")
            if derivedFrom is not None:
                x_name, x_indices = isolate_array_spec(derivedFrom)
                if name.startswith("FabricBlockInstanceInformation") and x_name.startswith("FabricBlockInstanceInformation"): # bad bad
                    pass
                elif (name.endswith("_CS0") or name.endswith("_CS1") or name.endswith("_CS2") or name.endswith("_CS3") or name.endswith("_CS4") or name.endswith("_CS5") or name.endswith("_CS6") or name.endswith("_CS7") or name.endswith("_CCIX0") or name.endswith("_CCIX1") or name.endswith("_CCIX2") or name.endswith("_CCIX3") or name.endswith("_CCM0") or name.endswith("_CCM1") or name.endswith("_CCM2") or name.endswith("_CCM3") or name.endswith("_CCM4") or name.endswith("_CCM5") or name.endswith("_CCM6") or name.endswith("_CCM7") or name.endswith("_IOS0") or name.endswith("_IOM0") or name.endswith("_IOMS0") or name.endswith("_IOS1") or name.endswith("_IOM1") or name.endswith("_IOMS1") or name.endswith("_IOS2") or name.endswith("_IOM2") or name.endswith("_IOMS2") or name.endswith("_IOS3") or name.endswith("_IOM3") or name.endswith("_IOMS3") or name.endswith("_PIE0") or name.endswith("_CAKE0") or name.endswith("_CAKE1") or name.endswith("_CAKE2") or name.endswith("_CAKE3") or name.endswith("_CAKE4") or name.endswith("_CAKE5") or name.endswith("_TCDX0") or name.endswith("_TCDX1") or name.endswith("_TCDX2") or name.endswith("_TCDX3") or name.endswith("_TCDX4") or name.endswith("_TCDX5") or name.endswith("_TCDX6") or name.endswith("_TCDX7") or name.endswith("_TCDX8") or name.endswith("_TCDX9") or name.endswith("_TCDX10") or name.endswith("_TCDX11")) and x_name.endswith("_BCST"): # bad bad
                    pass
                else:
                    assert x_name == name, (name, x_name)
                    assert len(x_indices) == len(indices), (name, x_name)
                    assert all(a[0] == b[0] for a,b in zip(x_indices, indices)), (name, x_name, indices, x_indices)
            #info("infer_arrays: {}: {}".format(name, indices))

logging.basicConfig(level=logging.INFO)
tree = etree.parse(sys.stdin if len(sys.argv) == 1 else open(sys.argv[-1]))
root = tree.getroot()

def traverse(root):
    has_cluster = False
    has_registers = None
    for child in root:
        if child.tag in ["peripherals", "peripheral", "cluster"]:
            has_cluster = True
            traverse(child)
        elif child.tag == "registers":
            has_registers = child
        else:
            assert child.tag in ["vendor", "vendorID", "name", "series", "version", "description", "licenseText", "addressUnitBits", "width", "size", "access", "resetMask", "groupName", "baseAddress", "register"], child.tag

    if has_registers is not None:
        assert not has_cluster, root
        infer_arrays(has_registers)

traverse(root)

tree.write(sys.stdout.buffer, pretty_print=True)
sys.stdout.flush()
