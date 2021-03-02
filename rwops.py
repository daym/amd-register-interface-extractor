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
         "Read-write,Reserved",
         "Read,Error-on-write-1"}

def strip_off_rwops(item):
    ops = {
    }
    item = item.strip()
    for rwop in rwops:
        if item.startswith(rwop + "."):
            item = item[len(rwop + "."):].strip()
            assert "access" not in ops, item
            ops["access"] = rwop
            #ops[rwop] = True
        if item.startswith("Reset:"):
            i = item.find(".")
            assert i != -1
            value = item[:i].strip()
            if value.startswith("Reset:"):
                value = value[len("Reset:"):].strip()
            if value.startswith("Fixed,"):
                value = value[len("Fixed,"):].strip()
            if value.startswith("Cold,"):
                value = value[len("Cold,"):].strip()
            ops["Reset"] = value
            item = item[i + len("."):].strip()
    return ops, item
