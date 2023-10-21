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

from itertools import chain
from pathlib import Path
from time import perf_counter

from itaxotools.common.utility import AttrDict

from .types import Results


def initialize():
    import itaxotools
    itaxotools.progress_handler('Initializing...')
    from . import work  # noqa


def execute(

    work_dir: Path,

    input_sequences: AttrDict,
    input_species: AttrDict,

    bulk_mode: bool,

) -> tuple[Path, float]:

    if not bulk_mode:
        return execute_single(
            work_dir=work_dir,
            input_sequences=input_sequences,
            input_species=input_species,
        )
    else:
        return execute_bulk(
            work_dir=work_dir,
            input_sequences=input_sequences,
            input_species=input_species,
        )


def execute_single(

    work_dir: Path,

    input_sequences: AttrDict,
    input_species: AttrDict,

) -> tuple[Path, float]:

    from itaxotools.taxi_gui.tasks.common.process import partition_from_model

    from itaxotools import abort, get_feedback

    from ..common.work import (
        match_partition_to_phased_sequences, scan_sequence_ambiguity)
    from .work import (
        get_sequences_from_phased_model, scan_sequence_alleles,
        write_stats_to_path)

    haplotype_stats = work_dir / 'out'

    ts = perf_counter()

    is_phased = input_sequences.is_phased

    sequences = get_sequences_from_phased_model(input_sequences)
    ambiguity_warns = scan_sequence_ambiguity(sequences)

    allele_warns = scan_sequence_alleles(sequences) if is_phased else []

    partition = partition_from_model(input_species)
    partition, partition_warns = match_partition_to_phased_sequences(partition, sequences)

    warns = ambiguity_warns + allele_warns + partition_warns

    tm = perf_counter()

    if warns:
        answer = get_feedback(warns)
        if not answer:
            abort()

    tx = perf_counter()

    partition_name = input_species.partition_name
    write_stats_to_path(sequences, is_phased, partition, partition_name, haplotype_stats)

    tf = perf_counter()

    return Results(haplotype_stats, tm - ts + tf - tx)


def execute_bulk(

    work_dir: Path,

    input_sequences: AttrDict,
    input_species: AttrDict,

) -> tuple[Path, float]:

    from itaxotools.taxi_gui.tasks.common.process import partition_from_model

    from itaxotools import abort, get_feedback

    from ..common.work import (
        match_partition_to_phased_sequences, scan_sequence_ambiguity)
    from .work import (
        get_all_possible_partition_models, get_sequences_from_phased_model,
        scan_sequence_alleles, write_bulk_stats_to_path)

    haplotype_stats = work_dir / 'out'

    ts = perf_counter()

    is_phased = input_sequences.is_phased
    names = input_species.info.spartitions

    sequences = get_sequences_from_phased_model(input_sequences)
    ambiguity_warns = scan_sequence_ambiguity(sequences)

    allele_warns = scan_sequence_alleles(sequences) if is_phased else []

    models = get_all_possible_partition_models(input_species)
    partitions = (partition_from_model(model) for model in models)
    partitions, partition_warns = zip(*(
        match_partition_to_phased_sequences(partition, sequences)
        for partition in partitions))

    partition_warns = list(set(chain(*partition_warns)))

    warns = ambiguity_warns + allele_warns + partition_warns

    tm = perf_counter()

    if warns:
        answer = get_feedback(warns)
        if not answer:
            abort()

    tx = perf_counter()

    write_bulk_stats_to_path(sequences, is_phased, partitions, names, haplotype_stats)

    tf = perf_counter()

    return Results(haplotype_stats, tm - ts + tf - tx)
