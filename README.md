# amd-register-interface-extractor

This project provides a tool to extract register definitions in a machine-readable form from AMD PPR (datasheet) PDFs.

The result can be used by `svd2rust` or similar SVD tools (note: lots of generators to generate C header files from SVD exists in the world) to generate source (header) code.

Tested with ZP B2 (Naples), SSP B0 (Rome) and GN B1 (Milan) PPR PDFs.

# Usage

Download the PPR PDFs for your CPU from AMD devhub and place them into the working directory (or a subdirectory of it).

Then invoke something like (using the name of the first PDF file as argument):

    ./configure 54945_ppr_ZP_B2_specl_nda.pdf
    make

The result is in `phase7_host.svd`.
It's also useful to `import phase2_result` in a Python interpreter and look around.

A rudimentary SVD viewer is also included, so you can inspect the result graphically using `./svd_viewer phase7_host.svd` (after `make svd_viewer`) or similar.

There are phase7 results for all the different access methods--one file per access method and `DataPortWrite` (for example `phase7_io.svd` and so on).

# What does it do

This tool first extracts all the register instances and all the other tables from the PPR, then emits tables for those (result: `phase2_result.py`).

These tables are then read in the next stage in order to generate SVD files without adding anything--but if requested (option `-a`) while removing redundant aliases (result: `phase3_*.svd`).

This is then processed in the next stage, trying to infer arrays where possible (in order to reduce the amount of SVD nodes).

So, in your further development steps, if you want a very close analog to the PPRs use `phase3*.svd`--and if you want a human-readable, maintainable, version, use `phase7*.svd`.

# svd2rust tips

If you do use `svd2rust`, it is recommended to use at least version `0.17.0` and give it the `--const-generic` option so that it will emit an ArrayProxy instead of array if the respective address space is sparsely populated in hardware.
