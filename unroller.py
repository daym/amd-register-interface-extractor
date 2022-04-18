#!/usr/bin/env python3

import sys
import pdb
import re
import sys
import logging
from io import StringIO
from collections import namedtuple
from settings import settings
from logging import debug, info, warning, error, critical

#RegisterInstanceSpec = namedtuple("RegisterInstanceSpec", ["logical_mnemonic", "physical_mnemonic", "variable_definitions"])

re_DataPortWrite_pattern = re.compile(r"^(.*)_x([0-9A-Fa-f_]+)$")

class RegisterInstanceSpec(namedtuple("RegisterInstanceSpec", ["logical_mnemonic", "physical_mnemonic", "variable_definitions"])):
	def resolve_physical_mnemonic(self, data_port_encoder):
		physical_mnemonic = self.physical_mnemonic
		for definition in self.variable_definitions:
			if definition.startswith("FabricIndirectConfigAccessAddress["):
				lhs_spec = "FabricIndirectConfigAccessAddress" # TODO: keep sanitized definition (spec)
				rhs_spec = "0" # dummy
			else:
				lhs_spec, rhs_spec = definition.split("=", 1)
			lhs = unroll_inst_item_pattern(lhs_spec.replace("::", "**"))
			if rhs_spec.find("::") != -1 or rhs_spec.find("{") != -1:
				rhs = unroll_inst_item_pattern("=" + rhs_spec.replace("::", "**"))
			else:
				# Rome PPR _aliasSMN likes to use patterns in values of variables, so we need to resolve those--if possible.
				rhs = ["=" + c for c in unroll_inst_item_pattern(rhs_spec.replace("::", "**"))]
			assert len(lhs) == len(rhs), (self.physical_mnemonic, lhs_spec, rhs_spec, lhs, rhs)
			for l, r in zip(lhs, rhs):
				l = l.replace("**", "::")
				r = r.replace("**", "::").lstrip("=")
				if physical_mnemonic.startswith(l + "x"):
					physical_mnemonic = r + " + " + physical_mnemonic[len(l + "x"):]
					break
				elif physical_mnemonic.startswith(l):
					tail = physical_mnemonic[len(l):].strip()
					# Some (few) registers have no "x..." part at all--assume offset 0.
					if tail == "":
						tail = "0"
					physical_mnemonic = r + " + " + tail
					break
		DataPortWrite_match = re_DataPortWrite_pattern.match(physical_mnemonic)
		if DataPortWrite_match:
			spec_inside = DataPortWrite_match.group(1)
			data_port_write = int(DataPortWrite_match.group(2), 16)
			data_port_write = data_port_encoder(spec_inside, data_port_write)
			if isinstance(data_port_write, str):
				physical_mnemonic = data_port_write
			else:
				physical_mnemonic = "{:X}".format(data_port_write)
		for k, v in settings:
			physical_mnemonic = physical_mnemonic.replace(k, v)
		return physical_mnemonic

def unroll_inst_item_pattern(spec):
	"""
	>>> list(unroll_inst_item_pattern("_inst[INTSBDEVINDCFG0,NBIF[1:0]DEVINDCFG0,PCIE1DEVINDCFG[7:0],PCIE0DEVINDCFG[7:0]]_aliasSMN"))
	['_instINTSBDEVINDCFG0_aliasSMN', '_instNBIF1DEVINDCFG0_aliasSMN', '_instNBIF0DEVINDCFG0_aliasSMN', '_instPCIE1DEVINDCFG7_aliasSMN', '_instPCIE1DEVINDCFG6_aliasSMN', '_instPCIE1DEVINDCFG5_aliasSMN', '_instPCIE1DEVINDCFG4_aliasSMN', '_instPCIE1DEVINDCFG3_aliasSMN', '_instPCIE1DEVINDCFG2_aliasSMN', '_instPCIE1DEVINDCFG1_aliasSMN', '_instPCIE1DEVINDCFG0_aliasSMN', '_instPCIE0DEVINDCFG7_aliasSMN', '_instPCIE0DEVINDCFG6_aliasSMN', '_instPCIE0DEVINDCFG5_aliasSMN', '_instPCIE0DEVINDCFG4_aliasSMN', '_instPCIE0DEVINDCFG3_aliasSMN', '_instPCIE0DEVINDCFG2_aliasSMN', '_instPCIE0DEVINDCFG1_aliasSMN', '_instPCIE0DEVINDCFG0_aliasSMN']
	>>> list(unroll_inst_item_pattern("IOHCDEVINDx[0000_C004,0000_9004,0000_8004,0000_[[4:1][C,8,4,0]]04]"))
	['IOHCDEVINDx0000_C004', 'IOHCDEVINDx0000_9004', 'IOHCDEVINDx0000_8004', 'IOHCDEVINDx0000_4C04', 'IOHCDEVINDx0000_4804', 'IOHCDEVINDx0000_4404', 'IOHCDEVINDx0000_4004', 'IOHCDEVINDx0000_3C04', 'IOHCDEVINDx0000_3804', 'IOHCDEVINDx0000_3404', 'IOHCDEVINDx0000_3004', 'IOHCDEVINDx0000_2C04', 'IOHCDEVINDx0000_2804', 'IOHCDEVINDx0000_2404', 'IOHCDEVINDx0000_2004', 'IOHCDEVINDx0000_1C04', 'IOHCDEVINDx0000_1804', 'IOHCDEVINDx0000_1404', 'IOHCDEVINDx0000_1004']
	>>> list(unroll_inst_item_pattern("_c2t1[UMCWPHY[A:0]]_aliasSMN"))
	['_c2t1UMCWPHYA_aliasSMN', '_c2t1UMCWPHY9_aliasSMN', '_c2t1UMCWPHY8_aliasSMN', '_c2t1UMCWPHY7_aliasSMN', '_c2t1UMCWPHY6_aliasSMN', '_c2t1UMCWPHY5_aliasSMN', '_c2t1UMCWPHY4_aliasSMN', '_c2t1UMCWPHY3_aliasSMN', '_c2t1UMCWPHY2_aliasSMN', '_c2t1UMCWPHY1_aliasSMN', '_c2t1UMCWPHY0_aliasSMN']
	>>> list(unroll_inst_item_pattern("_ccd11_instGMIC13KPXSLV_lane[BC,15:0]_aliasSMN"))
	['_ccd11_instGMIC13KPXSLV_laneBC_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane15_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane14_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane13_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane12_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane11_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane10_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane9_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane8_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane7_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane6_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane5_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane4_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane3_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane2_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane1_aliasSMN', '_ccd11_instGMIC13KPXSLV_lane0_aliasSMN']
	"""
	#>>> list(unroll_inst_item_pattern("_inst[TCDX[15:0],SPF[15:0],PFX[7:0],CNLI[3:0],CAKE[7:0],PIE0,ICNG[3:0],IOS[3:0],IOM[3:0],NCM[3:0],ACM[3:0],CCM[7:0],CMP[3:0],CS[11:0]]_n1__aliasSMN"))
	#[]
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
	logical_context = spec.startswith("_")
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
					radix = 16
					if logical_context:
						radix = 10
					else:
						radix = 16
					try:
						beginning = int(beginning, radix)
						end = int(end, radix)
					except ValueError:
						info("Spec for error below is: {}".format(spec))
						raise
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
		nonlocal logical_context
		old_logical_context = logical_context
		if scanner.c and scanner.c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ": # physical
			# This is AMD using "FOO[15:3]" as a physical subexpression in the logical expression "_bla[FOO[15:3]]".
			# Note: It's also possible that they use "BC,15:0" and then it should mean "BC", "15", "14", "13", ..., "0"--i.e. "BC" is a literal (and not a reference to a physical register).
			logical_context = False
		a = parse_range()
		logical_context = old_logical_context # Note: First alternative is special
		while scanner.c == ",":
			scanner.consume()
			b = parse_range()
			a = a + b
		logical_context = old_logical_context
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
	# list(unroll_inst_pattern("_inst[TCDX[15:0],SPF[15:0],PFX[7:0],CNLI[3:0],CAKE[7:0],PIE0,ICNG[3:0],IOS[3:0],IOM[3:0],NCM[3:0],ACM[3:0],CCM[7:0],CMP[3:0],CS[11:0]]_n1__aliasSMN; D18F3x00000834_x[60:00]; D18F3=4900_3000h; FabricIndirectConfigAccessAddress[CfgRegInstID=0x[60:00], IndCfgAccFuncNum=0,IndCfgAccRegNum=0x20D]"))
	insts = []
	physs = []
	for item in spec.split(";"):
		item = item.strip()
		if item.find("=") != -1: # local variable definition
			physs.append(item)
			#variable_definitions.append(item)
		else:
			# Those are the only NON-implicit ccd patterns (which should, after all, be unrolled).  So mask them from what follows... (Rome)
			item = item.replace("_ccd[7:0]_pcs", "_nonimplicitccd[7:0]_pcs")
			# Note: Suffix is usually "_n".
			implicit_patterns = ["_ccd[7:0]_lthree0_core[7:0]_thread[1:0]", "_ccd[7:0]_lthree0_core[7:0]", "_ccd[7:0]_lthree0",
			"_ccd[7:0]_lthree[1:0]_core[3:0]_inst0_thread[1:0]", # Rome MSR
			"_ccd[7:0]_lthree[1:0]_core[3:0]_inst1_thread[1:0]", # Rome MSR
			"_ccd[7:0]_lthree[1:0]_core[3:0]_inst2_thread[1:0]", # Rome MSR
			"_ccd[7:0]_lthree[1:0]_core[3:0]_inst3_thread[1:0]", # Rome MSR
			"_ccd[7:0]_lthree[1:0]_core[3:0]_inst4_thread[1:0]", # Rome MSR
			"_ccd[7:0]_lthree[1:0]_core[3:0]_inst5_thread[1:0]", # Rome MSR
			"_ccd[7:0]_lthree[1:0]_core[3:0]_inst6_thread[1:0]", # Rome MSR
			"_ccd[7:0]_lthree[1:0]_core[3:0]_thread[1:0]", "_ccd[7:0]_lthree[1:0]_core[3:0]", "_ccd[7:0]_lthree[1:0]", "_ccd[7:0]", # Rome
			# doesn't work "_ccd[7:0]_inst", # Rome MSR
			"_ccd[1:0]_lthree[1:0]_core[3:0]_thread[1:0]", "_ccd[1:0]_lthree[1:0]_core[3:0]", "_ccd[1:0]_lthree[1:0]", "_ccd[1:0]", # Ryzen 7
			"_lthree[1:0]_core[3:0]_thread[1:0]", "_lthree[1:0]_core[3:0]", "_lthree[1:0]", # Naples
			"_lthree0_core[3:0]_thread[1:0]", "_lthree0_core[3:0]", "_lthree0", # Ryzen APU NRB
			"_ccd[11:0]_lthree0_core[7:0]_thread[1:0]", "_ccd[11:0]_lthree0_core[7:0]", "_ccd[11:0]_lthree0", "_ccd[11:0]"] # Genoa
			for implicit_pattern in implicit_patterns:
				if item.startswith(implicit_pattern):
					new_pattern = implicit_pattern.replace("[", "").replace(":", ".").replace("]", "")
					item = new_pattern + item[len(implicit_pattern):]
			item = item.replace("_nonimplicitccd[7:0]_pcs", "_ccd[7:0]_pcs")
			item = item.replace("IOS3,IOM3,IOS2,IOM2,IOS1,IOM1,IOS0,IOM0", "IOMS3,IOMS2,IOMS1,IOMS0") # Rome; these are actually master and slave in one, each
			try:
				x = list(unroll_inst_item_pattern(item))
			except:
				info("Item for failure below is: {}".format(item))
				raise
			def reinstate_implicit_patterns(item):
				for implicit_pattern in implicit_patterns:
					new_pattern = implicit_pattern.replace("[", "").replace(":", ".").replace("]", "")
					if item.startswith(new_pattern):
						item = implicit_pattern + item[len(new_pattern):]
				return item
			x = [reinstate_implicit_patterns(c) for c in x]
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
			error("Unrolling did not work: logical instances are {!r} but physical instances are {!r} (raw: {!r})--which is impossible (lengths {} vs {}). Original pattern: {}".format(insts, ps, physs, len(insts), len(ps), spec))
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
			warning("Not enough phys entries, log={!r}; Note: all_physs={!r}".format(logical_mnemonic, physs))

if __name__ == "__main__":
	import doctest
	doctest.testmod()
