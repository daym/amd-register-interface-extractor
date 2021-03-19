# amd-register-interface-extractor

This project provides a tool to extract register definitions in a machine-readable form from AMD PPR (datasheet) PDFs.

The result can be used by `svd2rust` or similar SVD tools to generate source (header) code.

Tested with ZP B2 (Naples), SSP B0 (Rome) and GN B1 (Milan) PPR PDFs.

# Usage

Download the PPR PDFs for your CPU from AMD devhub and place them into the working directory (or a subdirectory of it).

Then invoke something like (using the name of the first PDF file as argument):

    ./configure 54945_ppr_ZP_B2_specl_nda.pdf
    make

The result is in `phase4_host.svd`.
It's also useful to `import phase2_result` in a Python interpreter and look around.

A rudimentary SVD viewer is also included, so you can inspect the result graphically using `python3 svd_viewer.py phase4_host.svd` or similar.
