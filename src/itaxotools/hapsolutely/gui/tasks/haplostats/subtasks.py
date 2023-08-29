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
from typing import TextIO

import yaml
from itaxotools.common.utility import AttrDict
from itaxotools.haplostats import HaploStats
from itaxotools.taxi2.partitions import Partition
from itaxotools.taxi2.sequences import Sequences

from .types import Entry


def _dict_representer(dumper, data):
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())


yaml.add_representer(dict, _dict_representer)


def _yamlify(data, title: str = None) -> str:
    if title:
        data = {title: data}
    return yaml.dump(data, default_flow_style=False)


def write_all_stats_to_file(name: str, stats: HaploStats, file: TextIO):

    print(file=file)
    partition = yaml.dump({'Partition': name}, default_flow_style=False)
    print(partition, file=file)

    data = stats.get_dataset_sizes()
    print(_yamlify(data, 'Dataset size'), file=file)

    data = stats.get_haplotypes()
    print(_yamlify(data, 'Haplotype sequences'), file=file)

    data = stats.get_haplotypes_per_subset()
    print(_yamlify(data, 'Haplotypes per subsets'), file=file)

    data = stats.get_haplotypes_shared_between_subsets()
    print(_yamlify(data, 'Haplotypes shared between subsets'), file=file)

    data = stats.get_fields_of_recombination()
    print(_yamlify(data, 'Fields of recombination'), file=file)

    data = stats.get_subsets_per_field_of_recombination()
    print(_yamlify(data, 'Subsets count per FOR'), file=file)

    data = stats.get_fields_of_recombination_per_subset()
    print(_yamlify(data, 'FOR count per subsets'), file=file)

    data = stats.get_fields_of_recombination_shared_between_subsets()
    print(_yamlify(data, 'FORs shared between subsets'), file=file)


def bundle_entries(

    sequences: Sequences,
    partition: Partition

) -> iter[Entry]:

    cached_id = None
    cached_subset = None
    cached_seq_a = None
    cached_seq_b = None

    for sequence in sequences:
        if 'allele' in sequence.extras:
            id = sequence.id
            allele = sequence.extras['allele']
        else:
            id = sequence.id[:-1]
            allele = sequence.id[-1]
        subset = partition[sequence.id]

        if id != cached_id and cached_id is not None:
            yield Entry(
                cached_id,
                cached_subset,
                cached_seq_a,
                cached_seq_b,
            )

        cached_id = id
        cached_subset = subset

        match allele:
            case 'a':
                cached_seq_a = sequence.seq
            case 'b':
                cached_seq_b = sequence.seq
            case _:
                raise ValueError(f"Could not determine alleles for individual {repr(sequence.id)}. Is the input phased?")

    yield Entry(
        cached_id,
        cached_subset,
        cached_seq_a,
        cached_seq_b,
    )


def write_stats_to_path(sequences: Sequences, partition: Partition, name: str, path: Path):

    stats = HaploStats()
    for entry in bundle_entries(sequences, partition):
        stats.add(entry.subset, [entry.seq_a, entry.seq_b])

    with open(path, 'w') as file:
        write_all_stats_to_file(name, stats, file)


def write_bulk_stats_to_path(sequences: Sequences, partitions: iter[Partition], names: list[str], path: Path):

    with open(path, 'w') as file:
        for partition, name in zip(partitions, names):

            print('---', file=file)

            stats = HaploStats()
            for entry in bundle_entries(sequences, partition):
                stats.add(entry.subset, [entry.seq_a, entry.seq_b])

            write_all_stats_to_file(name, stats, file)


def get_all_possible_partition_models(input: AttrDict) -> iter[AttrDict]:
    for partition in input.info.spartitions:
        model = AttrDict(input)
        model.spartition = partition
        yield model
