# -----------------------------------------------------------------------------
# Hapsolutely - Reconstruct haplotypes and produce genealogy graphs
# Copyright (C) 2023  Patmanidis Stefanos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

from __future__ import annotations

from itaxotools.taxi2.partitions import Partition
from itaxotools.taxi2.sequences import Sequences


def scan_sequences(sequences: Sequences) -> list[str]:
    ambiguity = set()
    for sequence in sequences:
        for character in sequence.seq:
            if character not in 'ACGT':
                ambiguity.add(character)
    if ambiguity:
        codes = ''.join(c for c in ambiguity)
        return [f'Ambiguity codes detected: {repr(codes)}']
    return []


def match_partition_to_phased_sequences(partition: Partition, sequences: Sequences) -> tuple[Partition, list[str]]:
    """
    It is possible that the allele markers (a/b) are suffixed to the
    individuals name in the partition but not the sequences, or vice versa.
    Detect such mismatches and return a partition suitable for the sequences.
    If some individuals could not be matched, return a warning.
    """

    matched = dict()
    unknowns = set()

    def has_subset(index: str, partition: Partition) -> bool:
        if not index in partition:
            return False
        if not partition[index]:
            return False
        return True

    for sequence in sequences:
        if has_subset(sequence.id, partition):
            matched[sequence.id] = partition[sequence.id]
            continue
        if sequence.id[-1] in 'ab':
            if has_subset(sequence.id[:-1], partition):
                matched[sequence.id] = partition[sequence.id[:-1]]
                continue
        matched[sequence.id] = 'unknown'
        unknowns.add(sequence.id)

    if unknowns:
        unknowns = list(unknowns)
        unknowns_str = ', '.join(repr(id) for id in unknowns[:3])
        if len(unknowns) > 3:
            unknowns_str += f' and {len(unknowns) - 3} more'
        warns = [f'Could not match individuals to partition: {unknowns_str}']
    else:
        warns = []

    return matched, warns
