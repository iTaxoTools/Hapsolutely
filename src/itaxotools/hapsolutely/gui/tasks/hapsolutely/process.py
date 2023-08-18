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

from .types import Results, NetworkAlgorithm


def initialize():
    import itaxotools
    itaxotools.progress_handler('Initializing...')
    import itaxotools.popart_networks  # noqa
    import itaxotools.taxi_gui.tasks.common.process  # noqa

    from ..common.subtasks import scan_sequences
    from . import subtasks  # noqa


def execute(

    work_dir: Path,

    input_sequences: AttrDict,
    input_species: AttrDict,

    network_algorithm: NetworkAlgorithm,

) -> tuple[Path, float]:

    from itaxotools import abort, get_feedback

    from itaxotools.taxi_gui.tasks.common.process import (
        partition_from_model, sequences_from_model)
    from itaxotools.popart_networks import build_msn, build_mjn, build_tsw, build_tcs
    from itaxotools.popart_networks import Sequence

    from ..common.subtasks import scan_sequences
    from .subtasks import make_haplo_tree, make_haplo_net, make_tree_nj

    haplo_tree = None
    haplo_net = None

    ts = perf_counter()

    sequences = sequences_from_model(input_sequences)
    warns = scan_sequences(sequences)

    if warns:
        answer = get_feedback(warns)
        if not answer:
            abort()

    partition = partition_from_model(input_species)

    if network_algorithm == NetworkAlgorithm.Fitchi:
        tree = make_tree_nj(sequences)
        haplo_tree = make_haplo_tree(sequences, partition, tree)
    else:
        build_method = {
            NetworkAlgorithm.MSN: build_msn,
            NetworkAlgorithm.MJN: build_mjn,
            NetworkAlgorithm.TCS: build_tcs,
            NetworkAlgorithm.TSW: build_tsw,
        }[network_algorithm]

        graph = build_method(
            Sequence(
                sequence.id,
                sequence.seq,
                partition.get(sequence.id, 'unknown')
            )
            for sequence in sequences)
        haplo_net = make_haplo_net(graph)

    tf = perf_counter()

    return Results(haplo_tree, haplo_net, tf - ts)
