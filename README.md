# amd-register-interface-extractor

This project provides a tool to extract register definitions in a machine-readable form from AMD PPR (datasheet) PDFs.

The result can be used by `svd2rust` or similar SVD tools to generate source (header) code.

Tested with ZP B2 (Naples) and SSP B0 (Rome) PPR PDFs.

# Usage

Download the PPR PDFs for your CPU from AMD devhub and place them into the working directory (or a subdirectory of it).

Then invoke something like (using the name of the first PDF file as argument):

    ./configure 54945_ppr_ZP_B2_specl_nda.pdf
    make

The result is in `phase3_result.svd`.
It's also useful to `import phase2_result` in a Python interpreter and look around.
