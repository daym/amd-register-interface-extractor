#!/usr/bin/env python3

from lxml import etree
import sys
import re
import logging
logging.basicConfig(level=logging.INFO)
from logging import debug, info, warning, error, critical

fontspec_to_meaning = [
     ({'size': '10', 'family': 'GAAAAA+Carlito', 'color': '#000000'}, "itemization"),
     ({'size': '12', 'family': 'BAAAAA+LiberationSerif', 'color': '#000000'}, "itemization-register-cell-_inst"),
     ({'size': '12', 'family': 'BAAAAA+LiberationSerif', 'color': '#000080'}, "memory-map-table"),
     ({'size': '12', 'family': 'CAAAAA+LiberationSerif', 'color': '#000000'}, "bitfield-description"),
     ({'size': '12', 'family': 'FAAAAA+Carlito', 'color': '#006fc0'}, "bitfield-description"),
     ({'size': '12', 'family': 'GAAAAA+Carlito', 'color': '#000000'}, "bitfield-description"),
     ({'size': '12', 'family': 'IAAAAA+LiberationSans', 'color': '#000000'}, None),
     ({'size': '14', 'family': 'FAAAAA+Carlito', 'color': '#006fc0'}, None),
     ({'size': '16', 'family': 'BAAAAA+LiberationSerif', 'color': '#000000'}, "register-cell-description"),
     ({'size': '16', 'family': 'BAAAAA+LiberationSerif', 'color': '#000080'}, "h1"),
     ({'size': '16', 'family': 'CAAAAA+LiberationSerif', 'color': '#000000'}, "table-caption"), # Also in register tables (for first table header line)
     ({'size': '16', 'family': 'DAAAAA+LiberationSerif', 'color': '#000000'}, "table-caption"), # Table 13
     ({'size': '16', 'family': 'EAAAAA+LiberationMono', 'color': '#000000'}, "source-code"),
     ({'size': '16', 'family': 'FAAAAA+Carlito', 'color': '#000000'}, "itemization-register-cell-_inst"),
     ({'size': '16', 'family': 'FAAAAA+Carlito', 'color': '#ffffff'}, None),
     ({'size': '18', 'family': 'BAAAAA+LiberationSerif', 'color': '#000000'}, None),
     ({'size': '18', 'family': 'DAAAAA+LiberationSerif', 'color': '#000000'}, None),
     ({'size': '18', 'family': 'FAAAAA+Carlito', 'color': '#006fc0'}, None),
     ({'size': '18', 'family': 'FAAAAA+Carlito', 'color': '#ffffff'}, None),
     ({'size': '18', 'family': 'JAAAAA+VL-Gothic', 'color': '#000000'}, None),
     ({'size': '18', 'family': 'KAAAAA+UMingHK', 'color': '#000000'}, "bitfield"), # etc
     ({'size': '20', 'family': 'FAAAAA+Carlito', 'color': '#006fc0'}, None),
     ({'size': '21', 'family': 'BAAAAA+LiberationSerif', 'color': '#000000'}, None),
     ({'size': '21', 'family': 'FAAAAA+Carlito', 'color': '#bebebe'}, None),
     ({'size': '21', 'family': 'FAAAAA+Carlito', 'color': '#ffffff'}, None),
     ({'size': '22', 'family': 'FAAAAA+Carlito', 'color': '#bebebe'}, None),
     ({'size': '22', 'family': 'FAAAAA+Carlito', 'color': '#ffffff'}, None),
     ({'size': '23', 'family': 'FAAAAA+Carlito', 'color': '#006fc0'}, None),
     ({'size': '23', 'family': 'FAAAAA+Carlito', 'color': '#bebebe'}, None),
     ({'size': '23', 'family': 'FAAAAA+Carlito', 'color': '#ffffff'}, None),
     ({'size': '24', 'family': 'CAAAAA+LiberationSerif', 'color': '#000000'}, "namespace-table"),
     ({'size': '27', 'family': 'FAAAAA+Carlito', 'color': '#bebebe'}, None),
     ({'size': '27', 'family': 'FAAAAA+Carlito', 'color': '#ffffff'}, None),
     ({'size': '42', 'family': 'CAAAAA+LiberationSerif', 'color': '#000000'}, None),
     ({'size': '54', 'family': 'CAAAAA+LiberationSerif', 'color': '#000000'}, None),
     ({'size': '5', 'family': 'FAAAAA+Carlito', 'color': '#000000'}, None),
     ({'size': '5', 'family': 'HAAAAA+DejaVuSans', 'color': '#000000'}, None),
     ({'size': '5', 'family': 'HAAAAA+DejaVuSans', 'color': '#ff0000'}, None),
     ({'size': '6', 'family': 'FAAAAA+Carlito', 'color': '#000000'}, None),
     ({'size': '8', 'family': 'FAAAAA+Carlito', 'color': '#000000'}, None),
     ({'size': '9', 'family': 'BAAAAA+LiberationSerif', 'color': '#000000'}, "normal-paragraph-text"),
     ({'size': '9', 'family': 'FAAAAA+Carlito', 'color': '#000000'}, None),
     ({'size': '9', 'family': 'IAAAAA+LiberationSans', 'color': '#000000'}, "bitfield-description"),

     # Naples:
     ({'size': '11', 'family': 'FAAAAA+Carlito', 'color': '#0070c0'}, None),
     ({'size': '12', 'family': 'FAAAAA+Carlito', 'color': '#0070c0'}, "bitfield-description"), # header
     ({'size': '14', 'family': 'FAAAAA+Carlito', 'color': '#0070c0'}, None), # very rare and useless
     ({'size': '18', 'family': 'FAAAAA+Carlito', 'color': '#0070c0'}, None), # very rare and useless
     ({'size': '18', 'family': 'KAAAAA+WenQuanYiZenHeiSharp', 'color': '#000000'}, "bitfield-description"),
     ({'size': '20', 'family': 'FAAAAA+Carlito', 'color': '#0070c0'}, None), # very rare and useless
     ({'size': '21', 'family': 'FAAAAA+Carlito', 'color': '#bfbfbf'}, None), # very rare and useless
     ({'size': '22', 'family': 'FAAAAA+Carlito', 'color': '#bfbfbf'}, None), # very rare and useless
     ({'size': '23', 'family': 'FAAAAA+Carlito', 'color': '#0070c0'}, None), # very rare and useless
     ({'size': '23', 'family': 'FAAAAA+Carlito', 'color': '#bfbfbf'}, None), # very rare and useless
     ({'size': '27', 'family': 'FAAAAA+Carlito', 'color': '#bfbfbf'}, None), # very rare and useless

     # Rome:
     ({'size': '12', 'family': 'CAAAAA+LiberationSerif', 'color': '#000080'}, None), # very rare and useless
     ({'size': '11', 'family': 'EAAAAA+Carlito', 'color': '#000000'}, None),
     ({'size': '16', 'family': 'CAAAAA+LiberationSerif', 'color': '#000080'}, None), # very rare and useless
     ({'size': '16', 'family': 'EAAAAA+Carlito', 'color': '#000000'}, None), # very rare and useless
     ({'size': '16', 'family': 'FAAAAA+LiberationMono', 'color': '#000000'}, None),
     ({'size': '16', 'family': 'GAAAAA+Carlito', 'color': '#000000'}, "bitfield-description"),
     # Ryzen:
     ({'size': '6', 'family': 'GAAAAA+Carlito', 'color': '#000000'}, "itemization-register-cell-_inst"), # "some" headlines
     ({'size': '7', 'family': 'GAAAAA+Carlito', 'color': '#000000'}, None), # rare
     ({'size': '11', 'family': 'JAAAAA+LiberationSans', 'color': '#000000'}, None), # ?
     ({'size': '11', 'family': 'FAAAAA+Carlito', 'color': '#006fc0'}, "headline"),
     ({'size': '15', 'family': 'JAAAAA+LiberationSans', 'color': '#000000'}, None), # "AMD Confidential"
     ({'size': '15', 'family': 'Arial', 'color': '#ffaa00'}, None), # Ryzen 7
     ({'size': '16', 'family': 'GHJJRM+LiberationSerif', 'color': '#000000'}, None), # rare
     ({'size': '16', 'family': 'QIKLDH+LiberationSerif', 'color': '#000000'}, "headline"),
     ({'size': '18', 'family': 'IAAAAA+UMingHK', 'color': '#000000'}, "headline"), # N
     ({'size': '18', 'family': 'HAAAAA+VL-Gothic', 'color': '#000000'}, None), # rare and useless
]

def hashable_fontspec(d):
  result = tuple(sorted(d.items()))
  return result

def xdict(fontspec_to_meaning):
  return dict([(hashable_fontspec(k),v) for k, v in fontspec_to_meaning])

# Check for dupes
assert len(xdict(fontspec_to_meaning)) == len(fontspec_to_meaning)
fontspec_to_meaning = xdict(fontspec_to_meaning)

def table_without_column_header_1_text_P(caption):
  # Note: Document-specific.  Please adapt.
  return caption.startswith("Table 19:") or caption.startswith("Table 20:") or caption.startswith("Table 21:") or caption.startswith("Table 22:") or caption.startswith("Table 23:") or caption.startswith("Table 24:") or caption.startswith("Table 82:") or caption.startswith("Table 212:")

with open(sys.argv[1]) as f:
  tree = etree.parse(f)

def resolve_fontspec(fontspecs, id):
  # Note: Would work completely: just return (('color', '#000080'), ('family', 'BAAAAA+LiberationSerif'), ('size', '12'))
  for xid, xfontspec in fontspecs:
    # fontspec  {'id': '0', 'size': '21', 'family': 'BAAAAA+LiberationSerif', 'color': '#000000'}
    if xid == id:
      xfontspec = hashable_fontspec(xfontspec)
      return xfontspec
  assert False, (id, fontspecs)

re_table_caption = re.compile(r"^(Table [0-9]+: [A-Za-z]|List of Namespaces|Memory Map -)")
re_section_headline = re.compile(r"^([0-9]+[.][0-9]+([.][0-9]+)*|Table [0-9]+:.*|LEGACYIOx00.*|GPUF0REGx[0-9A-F]+.* [(])$")
re_register_caption = re.compile(r"^[A-Z][]A-Z_n0-9.[]+[^ ]*x.|CPUID_Fn[08]00000[0-9A-F][0-9A-F]_E|MSR[0-9A-F_]+")
# TODO: "XGBEDWAPBI2C Registers".
re_bitfield_table_starts = re.compile(r"^(HDAx[02]...|USBCONTAINERx....|USBDWCHOSTx........|USBDWCx........|XGBEMMIO0x........|CPUID_Fn.*|PHYLANEx0\[0...C\]18|USBPHYCTRLx0|USBLANCTRLx0|ENET\[0[.][.][.]3\]BAR0x1D...|ENET\[[0123][.][.][.][0123]\]BAR0x[01].... [(]X?GMACDWCXGMAC[:][:]|[ ]?[(]XGBE[A-Z0-9]*::|ENET\[[0123][.][.][.][0123]\]BAR0x[01]....)") # CPUID_ entry is useless, I think.
# Note: Now also Milan, Ryzen 7
re_rome_vol2_misdetected_table_header = re.compile(r"^([A-Z]+.*[(].*::.*[)].*|NBIO0NBIFGDCRAS0x00000...[.][.][.].*|IOx00C01_x0.*|ABx0000[04].*|FCHSDPx00000_.*|IOAPICx00000010_indirectaddressoffset.*|I2Cx\[2[.][.][.]B\]0[0-9A-F][0-9A-F].*|UARTx\[[0-9A-F][0-9A-F]*[.][.][.][0-9A-F][0-9A-F]*\][0-F].*|PMx5F_x.*|USBCONTAINER\[[0-9A-F][0-9A-F]*[.][.][.][0-9A-F][0-9A-F]*\]x.*|MSR[0-9A-F][0-9A-F][0-9A-F][0-9A-F]_[0-9A-F][0-9A-F][0-9A-F][0-9A-F][.][.][.]MSR[0-9A-F][0-9A-F][0-9A-F][0-9A-F]_[0-9A-F][0-9A-F][0-9A-F][0-9A-F].*|MSR[0-9A-F][0-9A-F][0-9A-F][0-9A-F]_[0-9A-F][0-9A-F][][0-9A-F.]*|HDTx[0-9A-F]*|HDTx[0-9A-F]*_hdtcmd[0-9]*|SMMx[0-9A-F]*|APICx[][0-9A-F.]*|CPUID_Fn[08]00000[0-9A-F][0-9A-F]_E[A-Zx_0-9]*|PMCx[0-9A-F]+|L3PMCx[0-9A-F]*|IOHCMISC3x[0-9A-F]*|MCAPCIEx[0-9A-F]*[.][.][.]NBIO3PCIMCA0x[0-9A-F]*|IOx0[0-9A-F]*|BXXD0.*)$")
#re_bitfield_headlines = re.compile(r"^XGBEDWAPBI2C Registers$")

# Removed the bitfield table start (because it starts it too early): ENET\[[0123][.][.][.][0123]\]BAR0x[01].... ; Example: ENET[0...3]BAR0x1E000; it's now the .* (XGMACDWC entry)

# Should be two columns.
re_bits_description_broken_header = re.compile(r"^Bits Description")
re_bitrange = re.compile(r"^[0-9]+:[0-9]+")

def meaning_of_fontspec(fontspec, xx):
  try:
    meaning = fontspec_to_meaning[fontspec]
  except KeyError:
    warning("Font {!r} was unknown.  Assuming it's uninteresting.".format(dict(fontspec)))
    meaning = None
  if meaning == "table-caption":
    if xx == {"b"}: # misdetected headline
      meaning = "h1"
    else:
      assert xx == {"i"} or xx == set(), xx
  elif meaning == "headline" and not (xx == {"b"}):
    meaning = None
  return meaning

class State(object):
  def __init__(self):
    self.result = [("junk", )]
    self.page = 0
    self.headline = "junk"
    self.headline_type = None
    self.headline_left = 0
    self.in_table = False
    self.table_caption_left = 0
    self.in_table_header = False
    self.in_table_header_column_left = 0
    self.in_table_prefix = False
    self.table_column_starts = []
    self.table_column_header_texts = []
  def find_table_column_at(self, position):
    if not self.in_table:
      return None
    for i in range(len(self.table_column_starts) - 1, -1, -1):
      if position >= self.table_column_starts[i]:
        return i
    return None
  def finish_row(self):
      headline, cells = self.result[-1]
      print("// FINISH: %r, %s" % (headline, ",".join(map(repr, cells))))
      for cell in cells:
        print("//   cell: %r" % (cell, ))
  def start_new_cell(self, text, attrib):
    # Start new thing (headline or not)
    if True:
        if self.in_table and self.in_table_prefix:
          if text == "Bits" or text == "Bits Description":
            self.in_table_prefix = False
            print("// TABLE PREFIX ENDS")
            self.in_table_header = True
            # prefix is its own row.
            #? self.result.append((self.in_table, []))
            # Often, the column Bits is center-justified.  So don't use its text beginning.
            if attrib["left"] > self.in_table_header_column_left + 1:
              attrib["left"] = self.in_table_header_column_left + 1
            if attrib["left"] > self.in_table_header_column_left: # Next column
              self.table_column_starts.append(attrib["left"])
              self.table_column_header_texts.append("Bits")
              self.in_table_header_column_left = attrib["left"]
              #if self.in_table_header_column_left < self.table_caption_left:
              #  self.table_caption_left = self.in_table_header_column_left
              if self.in_table == "MSR0000_044B...MSRC000_2123":
                  #self.table_column_starts[0] = 58
                  self.table_caption_left = self.table_caption_left - 1 # = 58 # self.table_column_starts[0]
                  #self.headline_left = 58
                  #self.in_table_header_column_left = 58
              print("// table_column_starts: Added %d (%s)" % (attrib["left"], text))
              if text == "Bits Description":
                self.table_column_starts.append(105)
                self.table_column_header_texts.append("Description")
                print("// table_column_starts: Added %d (%s)" % (105, "Description"))
                self.in_table_header = False
                print("// not in table header anymore (left = %d, in_table_header_column_left = %d)" % (attrib["left"], self.in_table_header_column_left))
        elif self.in_table and self.in_table_header and not text.startswith(" "): # If we are in a table header # See Table 19 bold text for why the latter.
          if attrib["left"] > self.in_table_header_column_left:
            self.table_column_starts.append(attrib["left"])
            self.table_column_header_texts.append(text)
            self.in_table_header_column_left = attrib["left"]
            print("// table_column_starts: Added %d (%s)" % (attrib["left"], text))
          elif attrib["left"] == self.in_table_header_column_left: # column title is too long and spread over two lines.
            pass
          else:
            self.in_table_header = False
            print("// not in table header anymore (left = %d, in_table_header_column_left = %d)" % (attrib["left"], self.in_table_header_column_left))
        else:
          #if not self.in_table and re_bits_description_broken_header.match(text):
          #    self.in_table = True
          #    self.in_table_prefix = False
          #    self.in_table_header = True
          assert not re_bits_description_broken_header.match(text), (text, self.in_table_prefix, self.in_table_header, self.headline, self.in_table)
    return self.in_table
  def finish_this_table(self):
    if self.in_table:
      self.in_table = False
      self.in_table_header = False
      self.in_table_prefix = False
      self.finish_row()
      self.result.append(("EOT", [])) # not actually necessary--but nice.
  def finish_this_headline(self):
    if self.headline:
      self.headline = self.headline.strip()
      print("// FINISH: %r" % (self.result[-1], ))
      print("// END OF HEADLINE", self.headline)
      in_table = re_table_caption.match(self.headline) or re_register_caption.match(self.headline)
      if in_table: # If the headline we are finishing is a table caption
        assert not self.in_table # ... and we aren't in a table
        assert self.headline_left > 0 # ... and we didn't fuck up our internal state
        self.table_caption_left = self.headline_left
        self.in_table_header_column_left = self.table_caption_left - 1 # The first table column starts has to start to the right of that
        print("TABLE_CAPTION_LEFT", self.table_caption_left, self.headline)
        self.table_column_starts = [] # Remember where all the table columns start
        self.in_table = self.headline # True
        if re_register_caption.match(self.headline):
          self.in_table_header = False
          self.in_table_prefix = True
          print("// IN TABLE PREFIX of %r" % (self.in_table, ))
        else:
          self.in_table_header = True # We expect a table header next
          self.in_table_prefix = False
          #self.
          #self.result.append((self.headline, []))
          print("// IN TABLE HEADER")
        print("// TABLE STARTS (in_table_header=%d, in_table_prefix=%d)" % (self.in_table_header, self.in_table_prefix))
        if table_without_column_header_1_text_P(self.headline.strip()):
          print("// table_column_starts: Added %d (%s)" % (59, ""))
          self.table_column_starts.append(59)
          self.table_column_header_texts.append("")
      elif self.in_table and self.headline_left < self.table_caption_left: # If there's something that is left to the table caption, the table is done.
        print("// TABLE ENDS IN HEADLINE")
        self.finish_this_table()
        assert False
      self.result.append([self.headline, []])
      self.headline = ""
      self.headline_type = None
  def process_text(self, text, attrib, xx):
    #print("XXTEXT", text, attrib)
    # Naples: page >= 27
    if attrib["top"] >= 75 and attrib["top"] < 1136: # inside payload area of page
      if attrib["meaning"]:
          if text == "Processor Cores and Downcoring" or text == "Downcoring within a Core Complex" or text == "Downcoring within a Processor Die" or text == "Downcoring within a Multi-Node System" or text == "Downcoring within a Multi-Node System" or text == "CPUID Instruction Functions": # bad special case!
            attrib["meaning"] = "h1"
          elif attrib["left"] in [54, 58, 59, 76] and re_section_headline.match(text) and xx == {"b"}: # catches a lot of misdetections, like 2.1.10, 2.1.10.1, 2.1.10.2; does not catch 3.8.2 because its still in the table prefix of "Unexpected Completion".
            #assert text != "3.8.2", attrib
            attrib["meaning"] = "headline"
          if text.endswith(".") and len(text) > 15 and attrib["meaning"] in ["headline", "h1"]: # # example: "Soft down core needs to follow the same symmetric guidelines used for fused down core." (not really--that would be a bitfield-description)
            attrib["meaning"] = None
          if text == "Soft down core needs to follow the same symmetric guidelines used for fused down core." and attrib["meaning"] == "bitfield-description":
            attrib["meaning"] = None
          if attrib["meaning"] == "h1":
            if attrib["left"] == 54 or attrib["left"] == 59: # The latter for 11.13.2's UMCPMCx1
              if xx == {"i"}:
                attrib["meaning"] = "italic-headline"
              elif xx == {"b"} and (len(text) > 0 and (text[0] == text[0].upper() or text.find(" ") != -1)):
                attrib["meaning"] = "headline"
              else:
                attrib["meaning"] = None
            else: # h1 headline continuation
              if xx == {"i"}:
                attrib["meaning"] = "italic-h1"
              elif xx == {"b"}:
                attrib["meaning"] = "h1"
              else:
                attrib["meaning"] = None
      if attrib["meaning"] == "headline" and (text == "Read-only" or text == "Read-write" or text.startswith("doc")):
        attrib["meaning"] = None
      if attrib["meaning"] == "namespace-table":
        if text == "List of Namespaces":
          #self.finish_this_table()
          attrib["meaning"] = "headline"
        else:
          attrib["meaning"] = "bitfield-description"
      if attrib["meaning"] == "memory-map-table" or (attrib["meaning"] == "bitfield-description" and int(attrib["left"]) == 76):
        if text.startswith("Memory Map - ") or text.strip() == "List of Definitions":
          #self.finish_this_table()
          attrib["meaning"] = "headline"
        else:
          attrib["meaning"] = "bitfield-description"
      if not attrib['meaning'] and re_table_caption.match(text) and xx == {"i"} and int(attrib["left"]) == 54: # Milan
        # That will explicitly match register descriptions that start with "Table "... those have probably been written differently for a reason? Who knows.  Even if not, still good to be able to process those.
        attrib['meaning'] = 'table-caption'

      meaning = attrib.get("meaning")
      if meaning == "headline" \
      or meaning == "italic-headline" \
      or (meaning == "table-caption" and int(attrib["left"]) < 100 and text != "•" and xx == {"i"}) \
      or (meaning == "bitfield-description" and ((int(attrib["left"]) in [58, 59] and not re_bitrange.match(text)) or (int(attrib["left"]) == 54 and re_section_headline.match(text)))) \
      or (meaning == "itemization-register-cell-_inst" and (text in ["IOx0CF8", "IOx0CFC"] or re_rome_vol2_misdetected_table_header.match(text) or re_section_headline.match(text))) \
      or (meaning in ["normal-paragraph-text", "register-cell-description"] and re_rome_vol2_misdetected_table_header.match(text) and xx == {"b"}) \
      or (meaning in ["bitfield"] and re_bitfield_table_starts.match(text)):
        if self.in_table and not self.in_table_prefix and \
        ((meaning == "bitfield-description" and ((int(attrib["left"]) in [54, 58] and len(text) > 3 and xx == {"b"}) or (int(attrib["left"]) == 59 and xx == {"b"} and ((text.find("x") > 1 and not text.endswith("x")) or text.startswith("CPUID_Fn") or text.startswith("MSR")))) and not self.in_table.startswith("Table 85:") and not re_bitrange.match(text)) \
         or (meaning != "bitfield-description")):
          self.finish_this_table()
          print("// TABLE ENDS BECAUSE OF NEW HEADLINE OR TABLE CAPTION", text, attrib, meaning)
        self.finish_this_headline() # headline after headline
        if not self.start_new_cell(text, attrib):
          self.headline = text
          self.headline_type = meaning
          self.headline_left = attrib["left"]
          return
      elif meaning == "h1":
        #if attrib["left"] == self.headline_left + 5 and self.headline_type == "italic-headline": table row
        if self.headline_type == "headline": # continues the same kind of headline
          if not self.start_new_cell(text, attrib): # XXX
            self.headline = (self.headline or "") + " " + text
            return
          assert False
        else: # misdetected--actually a start of a new kind of headline
          self.finish_this_headline() # headline after headline
          if re_section_headline.match(text):
            self.finish_this_table()
            assert False, (text, meaning, attrib)
          if not self.start_new_cell(text, attrib):
            self.headline = text
            self.headline_type = "headline"
            self.headline_left = attrib["left"]
            return
      elif meaning == "italic-h1":
        if self.headline_type == "italic-headline":
          if not self.start_new_cell(text, attrib):
            self.headline = self.headline + " " + text
            return
          assert False
        else: # misdetected--actually a start of a new kind of headline
          self.finish_this_headline() # headline after headline
          if not self.start_new_cell(text, attrib):
            self.headline = text
            self.headline_type = "italic-headline"
            self.headline_left = attrib["left"]
            return
          assert False
      else:
        #print("// end-of-headline because", meaning, text, attrib)
        self.finish_this_headline() # end of headline
        self.start_new_cell(text, attrib) # TODO: Check for "bitfield" 'headlines'.
      if True:
        if self.in_table and attrib["left"] < self.table_caption_left and not self.in_table_prefix: # If there's something that is left to the table caption, the table is done.
          print("// TABLE ENDS BECAUSE {} < {}".format(attrib["left"], self.table_caption_left))
          self.finish_this_table()
        column_i = self.find_table_column_at(attrib["left"]) or 0
        if len(self.result[-1][1]) > 1 and column_i == 0: # new row
          self.finish_row()
          self.result.append((self.result[-1][0], []))
        while column_i >= len(self.result[-1][1]):
          self.result[-1][1].append("")
        if self.result[-1][1][column_i]:
          separator = " "
          if self.in_table and self.in_table_prefix and int(attrib["left"]) in [54, 58, 59]:
            assert column_i == 0
            #assert text.startswith("_") or text.startswith("Read-write."), text
            separator = "\u00b6" # paragraph sign
          self.result[-1][1][column_i] = self.result[-1][1][column_i] + separator + text
        else:
          self.result[-1][1][column_i] = text
        #print("PROC", text, attrib, self.headline_type, self.headline)

def traverse(state, root, indent = 0, fontspecs = []): # fontspecs: [(id, node with attribs: size, family, color)]
  for node in root.iterchildren(): # DFS
    attrib = node.attrib # filter it!
    if node.tag == "fontspec":
      # need to mutate because scoping rules are that way
      xnode = dict(node.attrib)
      del xnode["id"]
      fontspecs.insert(0, (node.attrib["id"], xnode))
    xx = set(xnode.tag for xnode in node.iterchildren() if xnode.tag != "a")
    if node.tag == "text":
      attrib = dict([(k,v) for k, v in attrib.items() if k not in ["top", "left", "width", "height"]])
      x = list(attrib.keys())
      assert x == ["font"] or x == []
      if node.text is None or set(xnode.tag for xnode in node.iterchildren() if xnode.tag == "a"): # for example if there are <a ...>
        text = "".join(text for text in node.itertext()) # XXX maybe recurse
      else:
        text = node.text
      if "font" in attrib: # resolve reference
        font_id = attrib["font"]
        fontspec = resolve_fontspec(fontspecs, font_id)
        try:
          attrib["meaning"] = meaning_of_fontspec(fontspec, xx)
        except KeyError as e:
          info("Text for failure below is: {}".format(text))
          raise e
        if not attrib["meaning"]:
          attrib["font"] = fontspec
        else:
          del attrib["font"]
      #top, left, width, height, font
    # Node: text, font="<id>"; see fontspec
    if node.tag == "text":
      attrib["left"] = int(node.attrib["left"])
      attrib["top"] = int(node.attrib["top"])
      attrib["width"] = int(node.attrib["width"])
      attrib["height"] = int(node.attrib["height"])
    elif node.tag == "page" and node.attrib["number"]:
      state.page = int(node.attrib["number"])
    if node.tag == "text" and state.page >= 27 and int(attrib["top"]) >= 75 and int(attrib["top"]) < 1136: # inside payload area of page
      print("// %*s" % (indent, ""), "TEXT", text if node.tag == "text" else "", attrib)
    elif node.tag != "fontspec" and state.page >= 27:
      print("// %*s" % (indent, ""), node.tag, text if node.tag == "text" else "", attrib)
    if node.tag == "text":
      state.process_text(text, attrib, xx)
    traverse(state, node, indent + 4, fontspecs)
    # node.tag, node.attrib

root = tree.getroot()
state = State()
traverse(state, root)
state.finish_this_table()
