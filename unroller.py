#!/usr/bin/env python3

import sys
import pdb
import sys
from io import StringIO
from collections import namedtuple
from settings import settings

#RegisterInstanceSpec = namedtuple("RegisterInstanceSpec", ["logical_mnemonic", "physical_mnemonic", "variable_definitions"])

class RegisterInstanceSpec(namedtuple("RegisterInstanceSpec", ["logical_mnemonic", "physical_mnemonic", "variable_definitions"])):
	@property
	def resolved_physical_mnemonic(self):
		physical_mnemonic = self.physical_mnemonic
		for definition in self.variable_definitions:
			lhs_spec, rhs_spec = definition.split("=", 1)
			lhs = unroll_inst_item_pattern(lhs_spec.replace("::", "**"))
			rhs = unroll_inst_item_pattern("=" + rhs_spec.replace("::", "**"))
			assert len(lhs) == len(rhs), (self.physical_mnemonic, lhs_spec, rhs_spec, lhs, rhs)
			for l, r in zip(lhs, rhs):
				l = l.replace("**", "::")
				r = r.replace("**", "::").lstrip("=")
				if physical_mnemonic.startswith(l + "x"):
					physical_mnemonic = r + " + " + physical_mnemonic[len(l + "x"):]
					break
				elif physical_mnemonic.startswith(l):
					physical_mnemonic = r + " + " + physical_mnemonic[len(l):]
					break
		for k, v in settings.items():
			physical_mnemonic = physical_mnemonic.replace(k, v)
		return physical_mnemonic

"""
TODO:
            logical_mnemonic = logical_mnemonic.strip()
            if logical_mnemonic == "_ccd[7:0]_lthree[1:0]_core[3:0]_thread[1:0]" or logical_mnemonic.startswith("_ccd[7:0]_lthree[1:0]_core[3:0]_thread[1:0]_n"
) or logical_mnemonic == "_ccd[7:0]_lthree[1:0]_core[3:0]" or logical_mnemonic.startswith("_ccd[7:0]_lthree[1:0]_core[3:0]_n") or logical_mnemonic == "_ccd[7:0
]_lthree[1:0]" or logical_mnemonic.startswith("_ccd[7:0]_lthree[1:0]_n") or re_direct_instance_number.match(logical_mnemonic): # implicit core reference etc
                aliaskind = None
            elif context_string and context_string.startswith("SBRMIx"):
                aliaskind = None # FIXME: AMD does not specify which it is.
            elif context_string and context_string.startswith("DFPMCx"):
                aliaskind = None # FIXME: AMD does not specify which it is.
            else:
                assert logical_mnemonic.find("_alias") != -1, (logical_mnemonic, context_string)
                aliaskinds = re_alias.findall(logical_mnemonic)
                assert len(aliaskinds) == 1, logical_mnemonic
                aliaskind, = aliaskinds
"""

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
	if not spec:
		return []
	scanner = Scanner("{}".format(spec))
	def parse_item(): # "02432432foo[2:1] -> [02432432foo2, 02432432foo1]",  "5:[2,1]"
		item = StringIO("")
		while scanner.c and scanner.c not in ":,]=":
			if scanner.c == "[":
				prefix = item.getvalue()      # "foo[..." => "foo"
				scanner.consume()
				values = parse_alternatives()
				assert scanner.c == "]", (scanner.input_data, spec)
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
			while scanner.c: # and scanner.c not in ":,]":
				if scanner.c == "{": # quote everything
					while scanner.c and scanner.c != "}":
						item.write(scanner.c)
						scanner.consume()
					if scanner.c:
						item.write(scanner.c)
						scanner.consume()
				else:
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
	def parse_toplevel():
		result = []
		prefix = ""
		values = parse_alternatives()
		suffixes = parse_item()
		result = []
		for v in values:
			for x in suffixes:
				result.append("{}{}{}".format(prefix, v, x))
		#item = StringIO("")
		assert not (scanner.c and scanner.c not in ":,]"), "would stop anyway"
		return result

	#pdb.set_trace()
	return [choice for choice in parse_toplevel()]

def unroll_inst_pattern(spec):
	#"""
	#>>> unroll_inst_pattern("_inst[INTSBDEVINDCFG0,NBIF[1:0]DEVINDCFG0,PCIE1DEVINDCFG[7:0],PCIE0DEVINDCFG[7:0]]_aliasSMN; IOHCDEVINDx[0000_C004,0000_9004,0000_8004,0000_[[4:1][C,8,4,0]]04]; IOHCDEVIND=13B3_0000h")
	#"""
	variable_definitions = []
	insts = []
	physs = []
	for item in spec.split(";"):
		item = item.strip()
		if item.find("=") != -1: # local variable definition
			physs.append(item)
			#variable_definitions.append(item)
		else:
			if item.startswith("_ccd[7:0]_lthree0_core[7:0]_thread[1:0]"): # According to AMD this does not count as a pattern for us
				item = item.replace("_ccd[7:0]_lthree0_core[7:0]_thread[1:0]", "_ccd7.0_lthree0_core7.0_thread1.0")
			elif item.startswith("_ccd[7:0]_lthree0_core[7:0]"): # According to AMD this does not count as a pattern for us
				item = item.replace("_ccd[7:0]_lthree0_core[7:0]", "_ccd7.0_lthree0_core7.0")
			elif item.startswith("_ccd[7:0]_lthree0"): # According to AMD this does not count as a pattern for us
				item = item.replace("_ccd[7:0]_lthree0", "_ccd7.0_lthree0")
			try:
				x = list(unroll_inst_item_pattern(item))
			except:
				print("ITEM", item, file=sys.stderr)
				raise
			x = [c.replace("_ccd7.0_lthree0_core7.0_thread1.0", "_ccd[7:0]_lthree0_core[7:0]_thread[1:0]").replace("_ccd7.0_lthree0_core7.0", "_ccd[7:0]_lthree0_core[7:0]").replace("_ccd7.0_lthree0", "_ccd[7:0]_lthree0") for c in x]
			while len(x) > 0 and x[-1] == "": # TODO: Be nicer about this.
				x = x[:-1]
			if item.startswith("_"): # find("_alias") != -1 or item.find(": # alias beginning
				insts += x
			else: # expression
				physs += x
	#result = RegisterInstanceSpec(logical_mnemonic=insts, physical_mnemonic_and_variables=physs)
	#FIXME: assert len(insts) == len(accesses), (insts, accesses)
	ps = [c for c in physs if c.find("=") == -1]
	if len(insts) != len(ps):
		if insts == [] and ps != []:
			pass
		elif insts != [] and ps == []:
			pass
		else:
			print("ERROR", insts, physs, file=sys.stderr)
		# else who knows
	#print("PHYSS", physs, file=sys.stderr)
	phys_i = 0
	for logical_mnemonic in insts:
		physical_mnemonic_and_variables = []
		if phys_i < len(physs):
			assert physs[phys_i].find("=") == -1
			physical_mnemonic = physs[phys_i]
			phys_i += 1
			variable_definitions = [c for c in physs[phys_i:] if c.find("=") != -1]
			while phys_i < len(physs) and physs[phys_i].find("=") != -1:
				phys_i += 1
			yield RegisterInstanceSpec(logical_mnemonic=logical_mnemonic, physical_mnemonic=physical_mnemonic, variable_definitions=variable_definitions)
		else:
			print("WARNING: Not enough phys entries, log={!r}; Note: all_physs={!r}".format(logical_mnemonic, physs), file=sys.stderr)

if __name__ == "__main__":
	import doctest
	doctest.testmod()
