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

from collections import Counter
from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.haplostats import HaploStats
from itaxotools.taxi2.file_types import FileFormat
from itaxotools.taxi2.partitions import Partition
from itaxotools.taxi2.sequences import Sequence, Sequences
from itaxotools.taxi_gui.tasks.common.process import sequences_from_model

from itaxotools.hapsolutely.yamlify import dump, yamlify

from .types import Entry


def write_all_stats_to_file(name: str, stats: HaploStats, file: TextIO):

    print(file=file)
    partition = dump({'Partition': name})
    print(partition, file=file)

    data = stats.get_dataset_sizes()
    print(yamlify(data, 'Dataset size'), file=file)

    data = stats.get_haplotypes()
    print(yamlify(data, 'Haplotype sequences'), file=file)

    data = stats.get_haplotypes_per_subset()
    print(yamlify(data, 'Haplotypes per subsets'), file=file)

    data = stats.get_haplotypes_shared_between_subsets()
    print(yamlify(data, 'Haplotypes shared between subsets'), file=file)

    data = stats.get_fields_of_recombination()
    print(yamlify(data, 'Fields of recombination'), file=file)

    data = stats.get_subsets_per_field_of_recombination()
    print(yamlify(data, 'Subsets count per FOR'), file=file)

    data = stats.get_fields_of_recombination_per_subset()
    print(yamlify(data, 'FOR count per subsets'), file=file)

    data = stats.get_fields_of_recombination_shared_between_subsets()
    print(yamlify(data, 'FORs shared between subsets'), file=file)


def write_partition_stats_to_file(name: str, stats: HaploStats, file: TextIO):

    print(file=file)
    partition = dump({'Partition': name})
    print(partition, file=file)

    data = stats.get_dataset_sizes()
    del data['FORs']
    print(yamlify(data, 'Dataset size'), file=file)

    data = stats.get_haplotypes()
    print(yamlify(data, 'Haplotype sequences'), file=file)

    data = stats.get_haplotypes_per_subset()
    print(yamlify(data, 'Haplotypes per subsets'), file=file)

    data = stats.get_haplotypes_shared_between_subsets()
    print(yamlify(data, 'Haplotypes shared between subsets'), file=file)


def write_phasing_stats_to_file(name: str, stats: HaploStats, file: TextIO):

    print(file=file)
    partition = dump({'Partition': name})
    print(partition, file=file)

    data = stats.get_dataset_sizes()
    del data['subsets']
    print(yamlify(data, 'Dataset size'), file=file)

    data = stats.get_haplotypes()
    print(yamlify(data, 'Haplotype sequences'), file=file)

    data = stats.get_fields_of_recombination()
    print(yamlify(data, 'Fields of recombination'), file=file)


def write_basic_stats_to_file(name: str, stats: HaploStats, file: TextIO):

    print(file=file)
    partition = dump({'Partition': name})
    print(partition, file=file)

    data = stats.get_dataset_sizes()
    del data['FORs']
    del data['subsets']
    print(yamlify(data, 'Dataset size'), file=file)

    data = stats.get_haplotypes()
    print(yamlify(data, 'Haplotype sequences'), file=file)


def write_stats_to_file(phased: bool, partitioned: bool, name: str, stats: HaploStats, file: TextIO):
    match phased, partitioned:
        case True, True:
            return write_all_stats_to_file(name, stats, file)
        case False, True:
            return write_partition_stats_to_file(name, stats, file)
        case True, False:
            return write_phasing_stats_to_file(name, stats, file)
    return write_basic_stats_to_file(name, stats, file)


def bundle_entries(sequences: Sequences, partition: Partition) -> iter[Entry]:

    cached_id = None
    cached_subset = None
    cached_seqs = None

    for sequence in sequences:

        if sequence.id == cached_id:
            cached_seqs.append(sequence.seq)
            continue

        if cached_id is not None:
            yield Entry(cached_id, cached_subset, cached_seqs)

        cached_id = sequence.id
        cached_subset = partition[sequence.id]
        cached_seqs = [sequence.seq]

    yield Entry(cached_id, cached_subset, cached_seqs)


def write_stats_to_path(sequences: Sequences, phased: bool, partitioned: bool, partition: Partition, name: str, path: Path):

    stats = HaploStats()
    for entry in bundle_entries(sequences, partition):
        stats.add(entry.subset, entry.seqs)

    with open(path, 'w') as file:
        write_stats_to_file(phased, partitioned, name, stats, file)


def write_bulk_stats_to_path(sequences: Sequences, phased: bool, partitions: iter[Partition], names: list[str], path: Path):

    with open(path, 'w') as file:
        for partition, name in zip(partitions, names):

            print('---', file=file)

            stats = HaploStats()
            for entry in bundle_entries(sequences, partition):
                stats.add(entry.subset, entry.seqs)

            write_stats_to_file(phased, True, name, stats, file)


def _check_fasta_allele_definitions(sequences: Sequences):
    previous_id = None
    cached_alleles = set()
    cached_ids = set()
    for sequence in sequences:
        *segments, allele = sequence.id.split('_')
        new_id = '_'.join(segments)

        if not new_id:
            raise Exception(f'Could not parse allele for identifier: {repr(sequence.id)}')

        if new_id == previous_id:
            if allele in cached_alleles:
                raise Exception(f'Duplicate allele entry for individual {repr(new_id)} and allele {repr(allele)}')
        else:
            cached_alleles.clear()
            if new_id in cached_ids:
                raise Exception(f'Out of order definition: {repr(new_id)}, {repr(allele)}')

        previous_id = new_id
        cached_alleles.add(allele)
        cached_ids.add(new_id)


def _check_tabfile_allele_definitions(sequences: Sequences, header: str):
    previous_id = None
    cached_alleles = set()
    cached_ids = set()
    for sequence in sequences:
        allele = sequence.extras[header]
        new_id = sequence.id

        if new_id == previous_id:
            if allele in cached_alleles:
                raise Exception(f'Duplicate allele entry for individual {repr(new_id)} and allele {repr(allele)}')
        else:
            cached_alleles.clear()
            if new_id in cached_ids:
                raise Exception(f'Out of order definition: {repr(new_id)}, {repr(allele)}')

        previous_id = new_id
        cached_alleles.add(allele)
        cached_ids.add(new_id)


def _rename_allele_header(sequences: Sequences, before: str, after: str) -> Sequences:
    for sequence in sequences:
        yield Sequence(sequence.id, sequence.seq, {after: sequence.extras[before]})


def _extract_alleles_from_ids(sequences: Sequences, header: str) -> Sequences:
    for sequence in sequences:
        *segments, allele = sequence.id.split('_')
        new_id = '_'.join(segments)
        yield Sequence(new_id, sequence.seq, {header: allele})


def _get_phased_sequences_from_phased_model(input: AttrDict) -> Sequences:
    sequences = sequences_from_model(input)

    if input.info.format == FileFormat.Tabfile:
        allele_header = input.info.headers[input.allele_column]
        _check_tabfile_allele_definitions(sequences, allele_header)
        return Sequences(_rename_allele_header, sequences, allele_header, 'allele')

    if input.info.format == FileFormat.Fasta:
        _check_fasta_allele_definitions(sequences)
        return Sequences(_extract_alleles_from_ids, sequences, 'allele')


def get_sequences_from_phased_model(input: AttrDict) -> Sequences:
    if input.is_phased:
        return _get_phased_sequences_from_phased_model(input)
    return sequences_from_model(input)


def scan_sequence_alleles(sequences: Sequences) -> list[str]:
    alleles = set()
    counters = Counter()
    for sequence in sequences:
        alleles.add(sequence.extras['allele'])
        counters[sequence.id] += 1

    warns = []

    unexpected_alleles = alleles - set(['a', 'b'])
    if unexpected_alleles:
        unexpected_alleles_str = ', '.join(repr(a) for a in unexpected_alleles)
        warns += [f'Unexpected alleles (not \'a\' or \'b\'): {unexpected_alleles_str}']

    single_allele_ids = [id for id, alleles in counters.items() if alleles == 1]
    if single_allele_ids:
        single_allele_ids_str = ', '.join(repr(id) for id in single_allele_ids[:3])
        if len(single_allele_ids) > 3:
            single_allele_ids_str += f' and {len(single_allele_ids) - 3} more'
        s = 's' if len(single_allele_ids) > 1 else ''
        warns += [f'Only a single allele defined for individual{s}: {single_allele_ids_str}']

    many_allele_ids = [id for id, alleles in counters.items() if alleles > 2]
    if many_allele_ids:
        many_allele_ids_str = ', '.join(repr(id) for id in many_allele_ids[:3])
        if len(many_allele_ids) > 3:
            many_allele_ids_str += f' and {len(many_allele_ids) - 3} more'
        s = 's' if len(many_allele_ids) > 1 else ''
        warns += [f'More than two alleles defined for individual{s}: {many_allele_ids_str}']

    return warns
