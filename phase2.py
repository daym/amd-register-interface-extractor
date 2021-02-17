#!/usr/bin/env python3

import string
import re
import sys

# result.txt has been generated by extract.py

resulting_name_to_full_name_map = dict()

# ['31:16 Reserved.  15', 'HdtBdcst :  core broadcast . Read-write.
# Example: APICx0A0, APICx340
# "10:2 blah. 3:4"
re_mistaken_pattern_1 = re.compile(r"^([0-9]+:[0-9]+)[ ]+([^.]*[.])  ([0-9]+(:[0-9]+)?)[ ]*$")

# "10 blah. 3  "
re_mistaken_pattern_2 = re.compile(r"^([0-9]+)[ ]+([^.]*[.])  ([0-9]+(:[0-9]+)?)[ ]*$")

# "10:3 <one-word>. <whatever> 5:2".
re_mistaken_pattern_3 = re.compile(r"^([0-9]+:[0-9]+)[ ]+([^.]*[.].*) ([0-9]+(:[0-9]+)?)$")
# "10:3 <one-word>. <whatever>"
re_mistaken_pattern_4 = re.compile(r"^([0-9]+:[0-9]+)[ ]+([^.]*[.].*)()$")
# "10:3 Reserved.  <whatever>"
re_mistaken_pattern_reserved = re.compile(r"^([0-9]+:[0-9]+)[ ]+(Reserved[.]( Read-[a-zA-Z0-9-,]+[.] (Reset: [^.]*[.])?)?) (.*)")

# Note: \u00b6 is the paragraph sign, used in place of "\n" (because re handles the latter really badly).
re_table_prefix = re.compile(r"^(.*)[ \u00b6](Bits Description.*)$")
re_table_prefix_nice_names = re.compile(r"^[ ]*([[][^(]* []])[ \u00b6]+([(][A-Za-z0-9]+::[A-Za-z0-9:_]+[)])(.*)$")
re_table_prefix_nice_name = re.compile(r"^([ \u00b6]*)([(][A-Za-z0-9]+::[A-Za-z0-9:_]+[)])(.*)$")
re_deparen = re.compile(r"[(]([^]:]+)[)]")

re_bit_ranges = re.compile(r"([0-9]+(:[0-9]+)?) ")

def start_table(current_table, prefix):
	print("# %s" % (current_table, ))
	name = current_table
	# Simplify name (use end-user-friendly name, not address).
	if name.find("::") != -1 and name.find(".") == -1 and name.find("[") == -1:
		_, name = name.split("(", 1)
		name, *_ = name.split(")", 1)
		assert name.find("::") != -1
	escaped_name = "".join(c if c in string.ascii_letters + string.digits else "_" for c in name.replace(" ", "_"))
	# FIXME: Fix those.
	assert escaped_name not in resulting_name_to_full_name_map or escaped_name in ["D18F0x050", "D18F1x200"] or escaped_name.startswith("UARTx_9___F_"), (escaped_name, name)
	resulting_name_to_full_name_map[escaped_name] = current_table
	print("%s = %r, [" % (escaped_name, prefix))

def finish_table(current_table):
	if current_table:
		print("]")
		print("")

def process_table_row(current_table, cells):
	cells = [cell.replace("Read- write", "Read-write") for cell in cells]
	print(cells, end="")
	print(",")

def remove_cosmetic_line_breaks(header):
    """ Accessor lists are often so long that they have a line wrap in it in the middle of a number.  That line wrap is virtual.  Remove it. """
    if header.find("\n") == -1:
        return header
    for j in range(10):
        header = header.replace(",\n{:X}".format(j), ",{:X}".format(j))
        for i in range(16):
            header = header.replace(",{:X}\n{:X}".format(i, j), ",{:X}{:X}".format(i, j))
    for i in range(16):
        for j in range(16):
            for k in range(10):
                header = header.replace(",{:X}\n{:X}{:X}".format(i, j, k), ",{:X}{:X}{:X}".format(i, j, k))
    return header

current_table = None
name_to_nice_name_table_references = {}
model = None
for line in open("result.txt", "r"):
	line = line.strip()
	if model is None and line.startswith("//      text PPR for "):
		model = line[len("//      text PPR for "):].strip()
		model, *rest = model.split("{", 1)
		model = model.strip()
		print("__model = {!r}".format(model))
	elif model is None and line.startswith("//      text PPR Vol 1 for "):
		model = line[len("//      text PPR Vol 1 for "):].strip()
		model, *rest = model.split("{", 1)
		model = model.strip()
		print("__model = {!r}".format(model))
	if line.startswith("// FINISH:"): # or line.startswith("//   cell:"):
		row = eval(line[len("// FINISH:"):])
		if len(row) == 1:
			table_reference = row[0]
			cells = []
		else:
			table_reference, *cells = row
		EOT = table_reference == "EOT"
		if EOT: # process the long tail!
			table_reference = current_table
			cells = []
		if name_to_nice_name_table_references.get(table_reference, table_reference) != current_table:
			finish_table(current_table)
			current_table = table_reference
			if len(cells) > 1:
				prefix_metadata = ""
				if len(cells) >= 1 and cells[0].find("\n") and cells[0].find("Bits Description") != -1:
					assert re_table_prefix.match(cells[0]), repr(cells[0])
				if len(cells) >= 1 and re_table_prefix.match(cells[0]):
					x = re_table_prefix.match(cells[0])
					prefix = x.group(1)
					suffix = x.group(2)
					prefix_metadata = prefix
					# work around limitation of regexes (recursive nesting not supported)
					prefix = re_deparen.sub(", \\1", prefix)
					prefix = prefix.replace("(ASCII Bytes ", ", ASCII Bytes").replace("(Bytes ", ", Bytes ")
					nice_names = re_table_prefix_nice_names.match(prefix) or re_table_prefix_nice_name.match(prefix)
					# Add nice name to CURRENT_TABLE.
					if not current_table.strip().endswith(")") or current_table.find("::") == -1:
						assert nice_names, (table_reference, prefix)
						if nice_names:
							extra = nice_names.group(1)
							nice_name = nice_names.group(2)
							x = current_table
							current_table = current_table + nice_name
							name_to_nice_name_table_references[x] = current_table
							cells[0] = nice_names.group(3)
							# TODO: Preserve cells[0]--which sometimes contains the reset value.
							#assert not table_reference.startswith("APICx090"), (cells[0])
					#if table_reference.startswith("MSR0000_0259"):
					#	import pdb
					#	pdb.set_trace()
					if (cells[0].find("Bits Description") == -1 and suffix.find("Bits Description") == -1) or cells[0].find("Bits Description") == 0:
						pass
					else:
						#sys.stderr.write("Warning: Fixed up cell 0: {}\n".format(cells[0]))
						cells[0] = suffix
					#print(prefix, file=sys.stderr)
					#sys.exit(1)
				start_table(current_table, remove_cosmetic_line_breaks(prefix_metadata.replace("\u00b6", "\n")))
			else: # ignore trivial "tables"
				current_table = None
		if current_table:
			if len(cells) >= 1 and cells[0].startswith("Bits Description "):
				process_table_row(current_table, ["Bits", "Description"])
				cells = [cells[0][len("Bits Description "):]] + cells[1:]
			# 'APICx090', ' [ Arbitration Priority ]  (Core::X86::Apic::Arbitration Priority) Read-only,Volatile. Reset: 0000_0000h.  _lthree[1:0]_core[3:0]_thread[1:0]; APICx090; APIC={Core::X86::Msr::APIC_BAR[ApicBar[47:12]] , 000h} Bits Description 31:8 Reserved.  7:0','Priority . Read-only,Volatile. Reset: 00h. Indicates the current priority for a pending interrupt, or a task or  interrupt being serviced by the core. The priority is used to arbitrate between cores to determine which accepts a  lowest-priority interrupt request.'
			mistaken_pattern_1 = re_mistaken_pattern_1.match(cells[0]) if len(cells) >= 1 else None
			if mistaken_pattern_1:
				OK1 = mistaken_pattern_1.group(1)
				OK2 = mistaken_pattern_1.group(2)
				too_early = mistaken_pattern_1.group(3)
				process_table_row(current_table, [OK1.strip(), OK2.strip()])
				#sys.stderr.write("YEP " + current_table + "\n")
				cells = [too_early] + cells[1:]
			mistaken_pattern_2 = re_mistaken_pattern_2.match(cells[0]) if len(cells) >= 1 else None
			assert not mistaken_pattern_2

			# Handle case: '15:11 Reserved. Read-only. Reset: 00h.  10:9 Reserved.  8' (always "Reserved")
			if len(cells) >= 1 and len(re_bit_ranges.findall(cells[0] + " ")) > 2:
				#print("MULTI RANGE IN {}: {!r}".format(current_table, cells[0]), file=sys.stderr)
				while True:
					match = re_mistaken_pattern_reserved.match(cells[0].strip())
					if match is None:
						break
					OK1 = match.group(1)
					OK2 = match.group(2)
					process_table_row(current_table, [OK1.strip(), OK2.strip()])
					too_early = match.group(5) # RECURSIVE ?
					cells[0] = too_early.strip()
				# Left over too_early !
			mistaken_pattern_3 = (re_mistaken_pattern_3.match(cells[0]) or re_mistaken_pattern_4.match(cells[0])) if len(cells) >= 1 else None
			if mistaken_pattern_3:
				OK1 = mistaken_pattern_3.group(1)
				OK2 = mistaken_pattern_3.group(2)
				too_early = mistaken_pattern_3.group(3)
				process_table_row(current_table, [OK1.strip(), OK2.strip()])
				if too_early:
					cells = [too_early] + cells[1:]
					process_table_row(current_table, cells)
			else:
				process_table_row(current_table, cells)
		if EOT:
			if current_table in name_to_nice_name_table_references:
				del name_to_nice_name_table_references[current_table] # Make overloads possible
			finish_table(current_table)
			current_table = None
#grep -E '\<(FINISH:|cell:)' result.txt
finish_table(current_table)
print("__names = %r" % (resulting_name_to_full_name_map, ))

