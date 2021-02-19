# amd-register-interface-extractor

Extracts register descriptions from AMD PPR PDFs (data sheet) and generates accessors for them.

Tested with ZP B2 (Naples) and SSP B0 (Rome).

# Usage

Download 54945_ppr_ZP_B2_specl_nda.pdf from AMD devhub and place it into working directory.

Then invoke:

    ./configure 54945_ppr_ZP_B2_specl_nda.pdf
    make
