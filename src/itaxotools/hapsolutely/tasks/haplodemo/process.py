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

from .types import NetworkAlgorithm, Results


def initialize():
    import itaxotools
    itaxotools.progress_handler('Initializing...')
    import itaxotools.popart_networks  # noqa
    import itaxotools.taxi_gui.tasks.common.process  # noqa

    from ..common.work import scan_sequence_ambiguity  # noqa
    from . import work  # noqa


def execute(

    work_dir: Path,

    input_sequences: AttrDict,
    input_species: AttrDict,
    input_tree: AttrDict,

    network_algorithm: NetworkAlgorithm,
    transversions_only: bool,
    epsilon: int,

) -> tuple[Path, float]:

    from itaxotools.popart_networks import (
        Sequence, build_mjn, build_msn, build_tcs, build_tsw)
    from itaxotools.taxi_gui.tasks.common.process import (
        partition_from_model, sequences_from_model)

    from itaxotools import abort, get_feedback

    from ..common.work import (
        check_is_input_phased, match_partition_to_phased_sequences,
        scan_sequence_ambiguity)
    from .work import (
        append_alleles_to_sequence_ids, get_newick_string_from_tree,
        get_tree_from_model, make_haplo_graph, make_haplo_tree, make_tree_nj,
        prune_alleles_from_haplo_graph, prune_alleles_from_haplo_tree,
        retrieve_spartitions, validate_sequences_in_tree, prune_alleles_from_spartitions)

    haplo_tree = None
    haplo_graph = None

    ts = perf_counter()

    sequences = sequences_from_model(input_sequences)
    sequence_warns = scan_sequence_ambiguity(sequences)

    is_phased, phased_warns = check_is_input_phased(input_sequences, sequences)

    sequences, allele_warns = append_alleles_to_sequence_ids(input_sequences, sequences)

    partition = partition_from_model(input_species)
    partition, partition_warns = match_partition_to_phased_sequences(partition, sequences)

    if network_algorithm == NetworkAlgorithm.Fitchi and input_tree is not None:
        tree = get_tree_from_model(input_tree)
        tree_warns = validate_sequences_in_tree(sequences, tree)
    else:
        tree_warns = []

    warns = sequence_warns + phased_warns + allele_warns + partition_warns + tree_warns

    tm = perf_counter()

    if warns:
        answer = get_feedback(warns)
        if not answer:
            abort()

    tx = perf_counter()

    if network_algorithm == NetworkAlgorithm.Fitchi:
        if input_tree is None:
            newick_string = make_tree_nj(sequences)
        else:
            newick_string = get_newick_string_from_tree(tree)
        haplo_tree = make_haplo_tree(sequences, partition, newick_string, transversions_only)

        if is_phased:
            prune_alleles_from_haplo_tree(haplo_tree)
    else:
        build_method, args = {
            NetworkAlgorithm.MSN: (build_msn, []),
            NetworkAlgorithm.MJN: (build_mjn, [epsilon]),
            NetworkAlgorithm.TCS: (build_tcs, []),
            NetworkAlgorithm.TSW: (build_tsw, []),
        }[network_algorithm]

        popart_sequences = (
            Sequence(
                sequence.id,
                sequence.seq,
                partition.get(sequence.id, 'unknown')
            )
            for sequence in sequences
        )

        graph = build_method(popart_sequences, *args)

        haplo_graph = make_haplo_graph(graph)

        if is_phased:
            prune_alleles_from_haplo_graph(haplo_graph)

    spartitions, spartition = retrieve_spartitions(input_species, sequences)

    if is_phased:
        spartitions = prune_alleles_from_spartitions(spartitions)

    tf = perf_counter()

    return Results(haplo_tree, haplo_graph, spartitions, spartition, tm - ts + tf - tx)
