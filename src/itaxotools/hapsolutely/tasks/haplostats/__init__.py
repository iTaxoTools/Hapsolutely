from itaxotools.hapsolutely.resources import task_pixmaps_large, task_pixmaps_medium

title = "Haplotype statistics"
description = "Haplotype insights per subset"

pixmap = task_pixmaps_large.stats
pixmap_medium = task_pixmaps_medium.stats

long_description = (
    "Identify unique haplotypes in the sequence data. "
    "List haplotypes per subset and haplotypes shared between subsets. "
    "Determine fields for recombination (FFRs). "
    "List haplotypes and subset occurences per FFR. "
    "List FFR occurences per subset and FFRs shared between subsets. "
    "\n\n"
    "Input can be in TSV, FASTA or SPART/XML format. Output is in YAML. "
    "\n"
    "Bulk mode available only for SPART/XML."
)
