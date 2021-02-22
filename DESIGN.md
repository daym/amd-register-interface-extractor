# Extractor Design

The extractor proceeds in multiple phases.

## Phase 0: poppler's pdftohtml

This uses poppler's `pdftohtml -xml` tool in order to convert a PDF to XML in pdftohtml-xml format.

## Phase 1: extract.py

This takes a pdftohtml-xml format file and outputs an intermediate `txt` file for later phases.
The things it does is the identification of headlines, the collection of data for each table into a single data item in the output.  It also drops a lot of useless information that was still in the pdftohtml-xml input.

## Phase 2: phase2.py

This takes the concatenation of multiple `txt` files from the previous phase and emits Python source code that provides variables that have all the register definitions spelled out in nice actual tables (Python lists).  It also includes all the non-register tables from the PPR.

It also removes virtual newlines from lists of numbers, fixes up a few table row matching problems.

The resulting Python source code is called `phase2_result.py`.

It is very useful to import this `phase2_result` from your own Python programs (and/or from the Python interpreter) and explore those.

## Phase 3: phase3.py

This imports a `phase2_result.py`, uses reflection to find all the tables, collects them into a tree-shaped namespace and then emits actual CMSIS SVD XML nodes for each of the peripherals in the tree.  Note that it only keeps entries with the access method specified in selected_access_method (usually `HOST`).

The outputs are usually called `phase3_host.svd` for the HOST access method, and `phase3_io.svd` for the IO access method.

After that, you can use `svd2rust` or similar tools to generate header files or similar files that allow you to access those registers using human-readable constructs.

## Collecting it all together

This is all automated using GNU Make, so just `make` is enough to make it go through all the phases.
