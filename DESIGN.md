# Extractor Design

The extractor proceeds in multiple phases.

## Phase 0: poppler's pdftohtml

This uses poppler's `pdftohtml -xml` tool in order to convert a PDF to XML in pdftohtml-xml format.

Output files are in directory `partsvol1`, `partsvol2` etc.

## Phase 1: extract.py

This takes a pdftohtml-xml format file and outputs an intermediate `txt` file for later phases.

It does:

* Identify headlines and table headers (using the font used, the "left" coordinate or special keywords)
* Collect each table row into a single data item in the output
* Drop a lot of useless information that was still in the pdftohtml-xml input

Note that, if necessary, resolve_fontspec could be changed to always return the first font (NOT A MATCH), without any loss of functionality.

Output files are in regular files `resultvol1.txt`, `resultvol2.txt` etc.

`fontspec_to_meaning`: Contains a map of fontspec to meaning.  (For now, it is expected that all fonts used by the PDF content are listed in there)

Meanings:

    itemization
    itemization-register-cell-_inst
    memory-map-table (If that's "Memory Map - " or "List of Definitions", that is a headline, otherwise bitfield-description)
    bitfield-description
    register-cell-description
    headline
    h1 (this is a continuation of a headline, or when you are not sure that it's a headline)
    table-caption
    source-code
    bitfield
    namespace-table (if "List of Namespaces" then that's a headline, otherwise a bitfield-description)
    normal-paragraph-text

Note that the `meaning` can be (and usually is) refined by further routines, for example by `meaning_of_fontspec` (which takes into account text attributes).

### `State`: Class managing the state necessary.

`result`: list of `("table id", "text")`--one for each row.  That is actually used little.  More used is the text printed the stdout
`page`: Current page number
`headline`: Current headline we are in
`headline_type`: What kind of headline we are in
`headline_left`: Where the headline started (horizontal absolute position)
`in_table`: Whether we are in a table, and in which table we are
`table_caption_left`: If there is a table caption, where is it (horizontal absolute position)
`in_table_header`: Whether we are in a table header (that's the column headers)
`in_table_header_column_left`: Where the table header column starts
`in_table_prefix`: Whether we are in a table prefix (the big explanation blob before it)
`table_column_starts`: Where does each column start (horizontal absolute position)
`table_column_header_texts`: What are the column header titles

`find_table_column_at`: Given a horizontal absolute position, finds the index of the column that position is in, if any.  Otherwise, returns None.
`finish_row`: Prints out a row that we finished
`start_new_cell`
`finish_this_table`: If there is a table, finish it (print its last row out, too).
`finish_this_headline`: If there is a headline, finish it (print it out).  If we are finishing a table (or register) caption (see `re_table_caption` and `re_register_caption`, respectively), then record where the table caption starts--and also start the first table header column.  If it's a `re_register_caption` match, then expect a table prefix next--otherwise a table header.  If we are in the table an a headline starts, finish the table first.

`process_text`: Processes text if inside payload area.  Fixes up `meaning` depending on attributes (like position and boldness).  Headlines that end in `.` are no headlines.  `h1` can upgrade to `italic-headline` or `headline` if conditions are right.  Also can downgrade to `None` if conditions are wrong (not bold or italic).

`traverse`: Traverses the XML file.  This is the entry point.  Remembers `<fontspec>`.  Processes `<text>`, `<font>` and `<page>`.  Note: Hard-coded 27 page skip at the beginning for `TEXT` output.  Calls `process_text` for all text.

If there's an assertion failure in this phase, you can examine the `resultvol`*`.txt.new` file (note `.new`) for the context.

## Phase 2: phase2.py

This takes the concatenation of multiple `txt` files from the previous phase and emits Python source code that provides variables that have all the register definitions spelled out in nice actual tables (Python lists).  It also includes all the non-register tables from the PPR.

It also removes virtual newlines from lists of numbers, fixes up a few table row matching problems.

The resulting output Python source code is called `phase2_result.py`.

It is very useful to import this `phase2_result` from your own Python programs (and/or from the Python interpreter) and explore those.

## Phase 3: phase3.py

This imports a `phase2_result.py`, uses reflection to find all the tables, collects them into a tree-shaped namespace and then emits actual CMSIS SVD XML nodes for each of the peripherals in the tree.  Note that it only keeps entries with the access method specified in selected_access_method (usually `HOST`).

In order to unroll instance specifiers into actual instances, it uses `unroller.py`.  Sometimes, the PPRs list something that looks like a pattern to unroll, but the core can really only see one of the many instances of the register.  Those are listed in the variable `implicit_patterns` in `unroller.py` in order to prevent them from being unrolled (it's expected for the resulting SVD files to be used from the CPU core--and from its point of view, the other instances don't matter to this specific core).

The outputs are usually called `phase3_host.svd` for the HOST access method and `phase3_io.svd` for the IO access method.

After that, you can use `svd2rust` or similar tools to generate header files or similar files that allow you to access those registers using human-readable constructs.

There's also files `phase3_host_ficaa.svd` and `phase3_smn_ficaa.svd` which can't be used with `svd2rust` but which list data fabric registers that are beind a FICAA indirect access.  The field `addressOffset` already contains the FICAA field as it is supposed to be programmed.
Because of the way this indirect access is to be done, it's not possible to represent any of those peripherals as a continuous (bigger than 32 bit long) struct in memory.

## Phase 4: Identifying register blocks (not used anymore)

Phase 4 identifies register blocks and collects those into clusters.

If the collection into clusters is done automatically (rather than by
configuration), then the cluster name with have the suffix "_unsorted".

Registers with adjacent addresses are collected into clusters.

The collection proceeds greedily and if in doubt, collects more into fewer clusters.

It's a good idea to edit `phase4_cluster_names` in `settings.py` to set up which things start a new cluster.

Finally, if a cluster contains only one register, the cluster level is elided and the register is represented without extra cluster.

## Phase 5: Grouping register block instances into clusters

This phase filters the phase3 result such that a register block is represented as a cluster.
It also adds `<displayName>` nodes with a more human-readable name if it's different (i.e. shorter) than the original register name.

## Phase 6: Making all the addressOffsets relative to the respective cluster

This phase makes all the addressOffsets relative to the cluster they are in.
Some tools expect this--but it's harder for a human to understand the resulting SVD file than if it was just absolute addresses.

## Collecting it all together

This is all automated using GNU Make, so just `make` is enough to make it go through all the necessary phases.
