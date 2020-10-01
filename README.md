# amd-register-interface-extractor

Extracts register descriptions from an AMD PPR PDF (data sheet) and generates accessors for them.

Tested with ZP B2 (Naples).

# Usage

Download 54945_ppr_ZP_B2_specl_nda.pdf from AMD devhub and place it into working directory.

Then invoke:

    ./configure 54945_ppr_ZP_B2_specl_nda.pdf
    make
