#!/usr/bin/env python3

import phase2_result
import unroller

for name in dir(phase2_result):
    try:
        header, items = getattr(phase2_result, name)
    except (ValueError, TypeError):
        continue
    if header.find("_alias") != -1:
        for item in header.split("\n"):
            x = unroller.unroll_inst_pattern(item)
            print(x)
