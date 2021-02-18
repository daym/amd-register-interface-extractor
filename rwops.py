#!/usr/bin/env python3

rwops = {"Read-write",
         "Read-only",
         #"Reset",
         "Read,Write-1-to-clear",
         "Volatile",
         "Read-write,Volatile",
         "Inaccessible",
         "Write-only",
         "Write-1-to-clear",
         "Read-only,Volatile",
         "Read-write,Read,Write-1-to-clear",
         "Read,Write-1-to-clear,Volatile",
         "Read-write,Reserved"}

def strip_off_rwops(item):
    ops = {
    }
    item = item.strip()
    for rwop in rwops:
        if item.startswith(rwop + "."):
            item = item[len(rwop + "."):].strip()
            ops[rwop] = True
        if item.startswith("Reset:"):
            i = item.find(".")
            assert i != -1
            ops["Reset"] = item[:i].strip()
            item = item[i + len("."):].strip()
    return ops, item
