# amd-register-interface-extractor

This project provides a tool to extract register definitions in a machine-readable form from AMD PPR (datasheet) PDFs.

The result can be used by `svd2rust` or similar SVD tools (note: lots of generators to generate C header files from SVD exists in the world) to generate source (header) code.

Tested with ZP B2 (Naples), SSP B0 (Rome) and GN B1 (Milan) PPR PDFs.

# Usage

Download the PPR PDFs for your CPU from AMD devhub and place them into the working directory (or a subdirectory of it).

Then invoke something like (using the name of the first PDF file as argument):

    ./configure 54945_ppr_ZP_B2_specl_nda.pdf
    make

The result is in `phase4_host.svd`.
It's also useful to `import phase2_result` in a Python interpreter and look around.

A rudimentary SVD viewer is also included, so you can inspect the result graphically using `python3 svd_viewer.py phase4_host.svd` or similar.

There are phase4 results for all the different access methods--one file per access method and `DataPortWrite` (named `phase4_io.svd` and so on).

# What does it do

This tool first extracts all the register instances and all the other tables from the PPR, then emits tables for those (result: `phase2_result.py`).

These tables are then read in the next stage in order to generate SVD files without adding anything--but if requested (option `-a`) while removing redundant aliases (result: `phase3_*.svd`).

This is then processed in the next stage, adding (if necessary guessing) a lot of context that is not spelled out in the PPRs (result: `phase4_*.svd`).  You should edit `settings.py` if you want the result of `phase4_*.svd` to be nice.  Otherwise you'll have a lot of `_unsorted` clusters which mean that this has been automatically grouped--even the cluster name is kinda weird then, and often the end of the cluster is not autodetected correctly; the beginning usually is autodetected.  Grouping is usually done by address adjacency--which works pretty well but obviously sometimes overshoots--in that case enter the thing that should be in a new cluster into `settings.py` under `phase4_cluster_names` and the peripheral and the register name, and then the (new) cluster name.

So, in your further development steps, if you want a very close analog to the PPRs use `phase3*.svd`--and if you want a human-readable, maintainable, version, use `phase4*.svd`.
