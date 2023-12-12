from itaxotools.hapsolutely.resources import task_pixmaps_large, task_pixmaps_medium

title = "Phase sequences"
description = "Reconstruct haplotypes"

pixmap = task_pixmaps_large.phase
pixmap_medium = task_pixmaps_medium.phase

long_description = "Reconstruct haplotypes from population data..."
long_description = (
    "Reconstruct haplotypes from sequence data. "
    "Output may still contain ambiguity codes, in which case "
    "you could try configuring the phase parameters and try again. "
    "\n\n"
    "Input and output can be in TSV or FASTA format. "
)
