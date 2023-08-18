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
    import itaxotools.taxi_gui.tasks.common.process  # noqa

    from . import subtasks  # noqa


def execute(

    work_dir: Path,

    input_sequences: AttrDict,
    input_species: AttrDict,

) -> tuple[Path, float]:

    from itaxotools.taxi_gui.tasks.common.process import (
        partition_from_model, sequences_from_model)

    # from ..common.subtasks import bundle_entries
    from .subtasks import make_haplo_tree, make_tree_nj

    ts = perf_counter()

    sequences = sequences_from_model(input_sequences)
    partition = partition_from_model(input_species)

    tree = make_tree_nj(sequences)

    haplo_tree = make_haplo_tree(sequences, partition, tree)

    tf = perf_counter()

    return Results(haplo_tree, tf - ts)
