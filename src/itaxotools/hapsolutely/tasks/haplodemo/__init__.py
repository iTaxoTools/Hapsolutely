from itaxotools.hapsolutely.resources import task_pixmaps_large, task_pixmaps_medium

title = "Haplotype visualization"
description = "Haplotype networks and genealogies"

pixmap = task_pixmaps_large.nets
pixmap_medium = task_pixmaps_medium.nets

long_description = (
    "Generate and visualize haplotype networks or genealogies from sequence data. "
    "Nodes are colorized by partition subset. "
    "Optionally draw a haploweb if input sequences are phased into alleles. "
    "After generation, configure the graph style and node positions interactively. "
    "If species are given in SPART/XML, you may dynamically select the visualized partition. "
    "\n\n"
    "Input can be in TSV, FASTA or SPART/XML format. "
    "Input trees for Fitchi must be in Newick format. "
    "\n"
    "Graphs can be exported as PNG, SVG or PDF files. "
)
