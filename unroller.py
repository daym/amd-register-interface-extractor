#!/usr/bin/env python3

import sys
import pdb
import sys
from io import StringIO

def unroll_inst_item_pattern(spec):
	"""
	>>> list(unroll_inst_item_pattern("_inst[INTSBDEVINDCFG0,NBIF[1:0]DEVINDCFG0,PCIE1DEVINDCFG[7:0],PCIE0DEVINDCFG[7:0]]_aliasSMN"))
	['_instINTSBDEVINDCFG0_aliasSMN', '_instNBIF1DEVINDCFG0_aliasSMN', '_instNBIF0DEVINDCFG0_aliasSMN', '_instPCIE1DEVINDCFG7_aliasSMN', '_instPCIE1DEVINDCFG6_aliasSMN', '_instPCIE1DEVINDCFG5_aliasSMN', '_instPCIE1DEVINDCFG4_aliasSMN', '_instPCIE1DEVINDCFG3_aliasSMN', '_instPCIE1DEVINDCFG2_aliasSMN', '_instPCIE1DEVINDCFG1_aliasSMN', '_instPCIE1DEVINDCFG0_aliasSMN', '_instPCIE0DEVINDCFG7_aliasSMN', '_instPCIE0DEVINDCFG6_aliasSMN', '_instPCIE0DEVINDCFG5_aliasSMN', '_instPCIE0DEVINDCFG4_aliasSMN', '_instPCIE0DEVINDCFG3_aliasSMN', '_instPCIE0DEVINDCFG2_aliasSMN', '_instPCIE0DEVINDCFG1_aliasSMN', '_instPCIE0DEVINDCFG0_aliasSMN']
	>>> list(unroll_inst_item_pattern("IOHCDEVINDx[0000_C004,0000_9004,0000_8004,0000_[[4:1][C,8,4,0]]04]"))
	['IOHCDEVINDx0000_C004', 'IOHCDEVINDx0000_9004', 'IOHCDEVINDx0000_8004', 'IOHCDEVINDx0000_4C04', 'IOHCDEVINDx0000_4804', 'IOHCDEVINDx0000_4404', 'IOHCDEVINDx0000_4004', 'IOHCDEVINDx0000_3C04', 'IOHCDEVINDx0000_3804', 'IOHCDEVINDx0000_3404', 'IOHCDEVINDx0000_3004', 'IOHCDEVINDx0000_2C04', 'IOHCDEVINDx0000_2804', 'IOHCDEVINDx0000_2404', 'IOHCDEVINDx0000_2004', 'IOHCDEVINDx0000_1C04', 'IOHCDEVINDx0000_1804', 'IOHCDEVINDx0000_1404', 'IOHCDEVINDx0000_1004']
	"""
	class Scanner(object):
		def __init__(self, input_data):
			self.input_data = input_data
			self.c = self.input_data[0]
		def consume(self):
			self.input_data = self.input_data[1:]
			self.c = self.input_data[0] if self.input_data != "" else None
	scanner = Scanner("[{}]".format(spec))
	def parse_item(): # "02432432foo[2:1] -> [02432432foo2, 02432432foo1]",  "5:[2,1]"
		item = StringIO("")
		while scanner.c and scanner.c not in ":,]=":
			if scanner.c == "[":
				prefix = item.getvalue()      # "foo[..." => "foo"
				scanner.consume()
				values = parse_alternatives()
				assert scanner.c == "]", scanner.input_data
				scanner.consume()
				suffixes = parse_item()
				result = []
				for v in values:
					for x in suffixes:
						result.append("{}{}{}".format(prefix, v, x))
				#item = StringIO("")
				assert not (scanner.c and scanner.c not in ":,]"), "would stop anyway"
				return result
			else:
				item.write(scanner.c)
				scanner.consume()
		if scanner.c == "=": # after that, none of the stuff is supposed to do anything special!
			while scanner.c and scanner.c not in ":,]":
				item.write(scanner.c)
				scanner.consume()
		return [item.getvalue()]
	def parse_range(): # "a:b" or "a";   a*b   [3+2]*8
		a_s = parse_item()
		if scanner.c == ":":
			scanner.consume()
			b_s = parse_item()
			result = []
			for a in a_s:
				for b in b_s:
					beginning, end = a, b
					radix = 10
					short = len(beginning) == 1 and len(end) == 1 # cannot be misinterpreted
					# The idea is to prefer to interpret things as decimal, but fall back to hexadecimal if we must.
					radix = 10
					if spec.find("x") != -1:
						radix = 16
						assert not spec.startswith("_")
					else:
						assert spec.startswith("_"), spec

					beginning = int(beginning, radix)
					end = int(end, radix)
					assert beginning >= end
					for i in range(beginning, end - 1, -1):
						if radix == 16:
							result.append("{:X}".format(i))
						elif radix == 10:
							result.append("{}".format(i))
						else:
							assert False
			return result
		else:
			return a_s
	def parse_alternatives(): # "a,b" or "a";    a+b
		a = parse_range()
		while scanner.c == ",":
			scanner.consume()
			b = parse_range()
			a = a + b
		return a
	#pdb.set_trace()
	return [choice for choice in parse_item()]

def unroll_inst_pattern(spec):
	#"""
	#>>> unroll_inst_pattern("_inst[INTSBDEVINDCFG0,NBIF[1:0]DEVINDCFG0,PCIE1DEVINDCFG[7:0],PCIE0DEVINDCFG[7:0]]_aliasSMN; IOHCDEVINDx[0000_C004,0000_9004,0000_8004,0000_[[4:1][C,8,4,0]]04]; IOHCDEVIND=13B3_0000h")
	#"""
	variable_definitions = []
	insts = []
	accesses = []
	for item in spec.split(";"):
		item = item.strip()
		if item.find("=") != -1: # local variable definition
			variable_definitions.append(item)
		else:
			try:
				x = list(unroll_inst_item_pattern(item))
			except:
				print("ITEM", item, file=sys.stderr)
				raise
			while len(x) > 0 and x[-1] == "": # TODO: Be nicer about this.
				x = x[:-1]
			if item.find("_alias") != -1: # alias beginning
				insts += x
			else: # expression
				accesses += x
	#print(variable_definitions)
	#print(insts)
	#print(accesses)
	#FIXME: assert len(insts) == len(accesses), (insts, accesses)
	if len(insts) != len(accesses):
		if insts == [] and accesses != []:
			pass
		elif insts != [] and accesses == []:
			pass
		else:
			print("ERROR", insts, accesses)
                # else who knows

	return insts, accesses

if __name__ == "__main__":
	import doctest
	doctest.testmod()
