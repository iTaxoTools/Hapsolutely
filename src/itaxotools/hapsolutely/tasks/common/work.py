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

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi2.file_types import FileFormat
from itaxotools.taxi2.files import get_info
from itaxotools.taxi2.handlers import FileHandler
from itaxotools.taxi2.partitions import Partition
from itaxotools.taxi2.sequences import SequenceHandler, Sequences

from .types import PhasedFileInfo


def _guess_if_sequence_ids_include_alleles(sequences: Sequences) -> bool:
    for sequence in sequences:
        *segments, allele = sequence.id.split('_')
        if len(segments) < 1:
            return False
        if len(allele) > 1:
            return False
    return True


def get_phased_file_info(path: Path) -> PhasedFileInfo:
    info = get_info(path)
    is_phased = False

    if info.format == FileFormat.Tabfile:
        headers = FileHandler.Tabfile(path, has_headers=True).headers
        is_phased = bool('allele' in headers)

    elif info.format == FileFormat.Fasta:
        sequences = Sequences.fromPath(
            info.path,
            SequenceHandler.Fasta,
            parse_organism=info.has_subsets,
            organism_separator=info.subset_separator,
            organism_tag='organism',
        )
        is_phased = _guess_if_sequence_ids_include_alleles(sequences)

    return PhasedFileInfo(info, is_phased)


def scan_sequence_ambiguity(sequences: Sequences) -> list[str]:
    ambiguity = set()
    for sequence in sequences:
        for character in sequence.seq:
            if character not in 'ACGT':
                ambiguity.add(character)
    if ambiguity:
        codes = ''.join(c for c in ambiguity)
        return [f'Ambiguity codes detected: {repr(codes)}']
    return []


def match_partition_to_phased_sequences(partition: Partition, sequences: Sequences, allele_header='allele') -> tuple[Partition, list[str]]:
    """
    It is possible that the allele markers are suffixed to the
    individuals name in the partition but not the sequences, or vice versa.
    Detect such mismatches and return a partition suitable for the sequences.
    If some individuals could not be matched, return a warning.
    """

    matched = dict()
    unknowns = set()

    def has_subset(index: str, partition: Partition) -> bool:
        if index not in partition:
            return False
        if not partition[index]:
            return False
        return True

    for sequence in sequences:

        if has_subset(sequence.id, partition):
            matched[sequence.id] = partition[sequence.id]
            continue

        if has_subset(sequence.id[:-1], partition):
            matched[sequence.id] = partition[sequence.id[:-1]]
            continue

        segments = sequence.id.split('_')[:-1]
        stripped_id = '_'.join(segments)
        if has_subset(stripped_id, partition):
            matched[sequence.id] = partition[stripped_id]
            continue

        if allele_header in sequence.extras:
            allele = sequence.extras[allele_header]
            suffixed_id = sequence.id + '_' + allele
            if has_subset(suffixed_id, partition):
                matched[sequence.id] = partition[suffixed_id]
                continue

        matched[sequence.id] = 'unknown'
        unknowns.add(sequence.id)

    if unknowns:
        unknowns = list(unknowns)
        unknowns_str = ', '.join(repr(id) for id in unknowns[:3])
        if len(unknowns) > 3:
            unknowns_str += f' and {len(unknowns) - 3} more'
        s = 's' if len(unknowns) > 1 else ''
        warns = [f'Could not match individual{s} to partition: {unknowns_str}']
    else:
        warns = []

    return matched, warns


def _get_sequence_pairs(sequences: Sequences):
    try:
        sequences = iter(sequences)
        while True:
            a = next(sequences)
            b = next(sequences)
            yield (a, b)
    except StopIteration:
        return


def _get_phased_fasta_warns(sequences: Sequences) -> list[str]:
    for sequence in sequences:
        if not sequence.id[-2] == '_':
            return [f'Sequence identifier(s) not ending with allele: {repr(sequence.id)} instead of {repr(sequence.id + "_a")}']

    for a, b in _get_sequence_pairs(sequences):
        if a.id[:-2] != b.id[:-2]:
            return [f'Mismatched pair identifiers for phased input: {repr(a.id)}, {repr(b.id)}']

    return []


def check_is_input_phased(input: AttrDict, sequences: Sequences) -> tuple[bool, list[str]]:
    if input.info.format == FileFormat.Fasta:
        if input.is_phased:
            warns = _get_phased_fasta_warns(sequences)
            return (True, warns)
        return (False, [])
    return (input.is_phased, [])


def get_all_possible_partition_models(input: AttrDict) -> iter[AttrDict]:
    for partition in input.info.spartitions:
        model = AttrDict(input)
        model.spartition = partition
        yield model
