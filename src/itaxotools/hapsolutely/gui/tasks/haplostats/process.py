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

from pathlib import Path
from time import perf_counter

from itaxotools.common.utility import AttrDict

from .types import Results


def initialize():
    import itaxotools
    itaxotools.progress_handler('Initializing...')
    from . import subtasks  # noqa


def execute(

    work_dir: Path,

    input_sequences: AttrDict,
    input_species: AttrDict,

    bulk_mode: bool,

) -> tuple[Path, float]:

    from itaxotools.taxi_gui.tasks.common.process import (
        partition_from_model, sequences_from_model)

    from itaxotools import abort, get_feedback

    from ..common.subtasks import scan_sequences
    from .subtasks import (
        get_all_possible_partition_models, write_bulk_stats_to_path,
        write_stats_to_path)

    haplotype_stats = work_dir / 'out'

    ts = perf_counter()

    sequences = sequences_from_model(input_sequences)
    warns = scan_sequences(sequences)

    if warns:
        answer = get_feedback(warns)
        if not answer:
            abort()

    if not bulk_mode:
        partition = partition_from_model(input_species)
        partition_name = input_species.spartition
        write_stats_to_path(sequences, partition, partition_name, haplotype_stats)
    else:
        models = get_all_possible_partition_models(input_species)
        partitions = (partition_from_model(model) for model in models)
        names = input_species.info.spartitions
        write_bulk_stats_to_path(sequences, partitions, names, haplotype_stats)

    tf = perf_counter()

    return Results(haplotype_stats, tf - ts)
