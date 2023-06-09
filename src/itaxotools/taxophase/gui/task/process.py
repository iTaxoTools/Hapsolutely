# -----------------------------------------------------------------------------
# TaxoPhase - Reconstruct haplotypes and produce genealogy graphs
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
from typing import NamedTuple

from itaxotools.common.utility import AttrDict
from itaxotools.fitchi.types import HaploNode


class Results(NamedTuple):
    seconds_taken: float
    haplo_tree: HaploNode


def initialize():
    import itaxotools
    itaxotools.progress_handler('Initializing...')
    from itaxotools.taxophase import subtasks  # noqa


def execute(

    work_dir: Path,

    input_sequences: AttrDict,
    input_species: AttrDict,

) -> tuple[Path, float]:

    from itaxotools.taxi2.partitions import Partition
    from itaxotools.taxophase.subtasks import phase_sequences, phase_partition, make_tree_nj, make_haplo_tree
    from itaxotools.taxi_gui.tasks.common.process import partition_from_model, sequences_from_model
    from time import sleep

    sequences = sequences_from_model(input_sequences)
    phased_sequences = phase_sequences(sequences)

    tree = make_tree_nj(phased_sequences)

    partition = partition_from_model(input_species)
    partition = phase_partition(partition)

    haplo_tree = make_haplo_tree(phased_sequences, partition, tree)

    sleep(0.42)

    return Results(0.42, haplo_tree)