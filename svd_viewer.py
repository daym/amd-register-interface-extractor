#!/usr/bin/env python3

import os
import sys
import gi
import lxml
from copy import deepcopy
from lxml import etree
gi.require_version("Gtk", "3.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gtk
from gi.repository import GLib

model = Gtk.TreeStore(str, str, str) # type, name, tooltip

# Note: optional: device: vendor, vendorID, series, licenseText, access.
type_to_pseudo_attributes = {
	"cluster": ["name", "addressOffset", "size", "dim", "dimIncrement", "dimIndex", "dimName", "dimArrayIndex", "access", "resetValue", "resetMask", "alternateCluster", "description"],
	"device": ["name", "version", "addressUnitBits", "width", "size", "resetValue", "resetMask", "vendor", "vendorID", "series", "licenseText", "access", "description"],
	"peripheral": ["name", "groupName", "baseAddress", "addressBlock", "resetValue", "resetMask", "access", "modifiedWriteValues", "description"],
	"register": ["name", "displayName", "alternateRegister", "addressOffset", "size", "dim", "dimIncrement", "dimIndex", "dimName", "dimArrayIndex", "access", "resetValue", "resetMask", "alternateRegister", "description"],
	"field": ["name", "bitOffset", "bitWidth", "access", "bitRange", "msb", "lsb", "description"], # note: bitRange, msb and lsb are optional.
	"interrupt": ["name", "value", "description"],
}

scroller = Gtk.ScrolledWindow()
scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
col0 = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=1)

tree = Gtk.TreeView()
tree.props.model = model
tree.props.tooltip_column = 2
tree.props.headers_visible = False
tree.props.search_column = 1
#tree.props.has_tooltip = True
tree.append_column(col0)
#tree.expand_all()

def resolve_derivedFrom(root):
  """ If ROOT has a 'derivedFrom' attribute, find an element with that name and copy all its children--except for the ones ROOT already has"""
  derivedFrom = root.attrib.get("derivedFrom")
  if derivedFrom:
    reference = root.find("..//register[name={!r}]".format(derivedFrom))
    if reference is not None:
      resolve_derivedFrom(reference)
      for node in reference:
        if etree.iselement(node):
          tag = node.tag
          if tag not in root:
              root.append(deepcopy(node))

def traverse(root, store_parent):
  type = root.tag if etree.iselement(root) else None
  if etree.iselement(root):
    resolve_derivedFrom(root)
  type = str(type)
  names = root.xpath("name/text()")
  name = names[0] if len(names) > 0 else (type or str(root))
  type = type or "?"
  name = str(name)
  tooltip = "Type: {}\n".format(type) + "\n".join([
    "{}: {}".format(cname, root.find(cname).text) for cname in type_to_pseudo_attributes.get(type, []) if root.find(cname) is not None
  ])
  tooltip = tooltip.strip()
  tooltip = GLib.markup_escape_text(tooltip, -1)
  # TODO: root.attrib
  store_root = model.append(store_parent, (type, name, tooltip))
  if type == "registers":
    tree.expand_to_path(model.get_path(store_root))
  for child in root:
    if etree.iselement(child) and child.tag in type_to_pseudo_attributes.get(type, []):
      pass
    else:
      traverse(child, store_root)

# FIXME: dtd_validation=True
parser = etree.XMLParser(ns_clean=True, attribute_defaults=True, remove_blank_text=True)
with open(sys.argv[1]) as f:
  svd = etree.parse(f, parser)
root = svd.getroot()
traverse(root, None)

scroller.add(tree)

win = Gtk.Window()
win.props.title = "{} - {}".format(os.path.realpath(sys.argv[1]), sys.argv[0])
win.connect("destroy", Gtk.main_quit)
win.add(scroller)
win.show_all()
Gtk.main()
