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

from collections import Counter
from io import StringIO

from Bio.Align import MultipleSeqAlignment
from Bio.Phylo import NewickIO
from Bio.Phylo.BaseTree import Clade
from Bio.Phylo.TreeConstruction import (
    DistanceCalculator, DistanceTreeConstructor)
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from itaxotools.convphase.phase import iter_phase
from itaxotools.convphase.types import UnphasedSequence
from itaxotools.fitchi import compute_fitchi_tree
from itaxotools.haplodemo.types import (
    HaploGraph, HaploGraphEdge, HaploGraphNode, HaploNode)
from itaxotools.popart_networks.types import Network
from itaxotools.taxi2.partitions import Partition
from itaxotools.taxi2.sequences import Sequence, Sequences


def phase_sequences(sequences: Sequences) -> Sequences:
    unphased = (UnphasedSequence(x.id, x.seq) for x in sequences)
    phased = iter_phase(unphased)
    results = []
    for x in phased:
        results.append(Sequence(x.id + 'a', x.data_a))
        results.append(Sequence(x.id + 'b', x.data_b))
    return Sequences(results)


def phase_partition(partition: Partition) -> Partition:
    result = Partition()
    for k, v in partition.items():
        result[k + 'a'] = v
        result[k + 'b'] = v
    return result


def _format_clades(clade: Clade) -> Clade:
    if not clade.is_terminal():
        clade.name = ''
    clade.branch_length = ''
    for branch in clade:
        _format_clades(branch)


def _format_newick_for_fitchi(newick_string: str) -> str:
    newick_string = newick_string.strip()
    newick_string = newick_string.removesuffix(';')
    newick_string = f'({newick_string})'
    return newick_string


def make_tree_nj(sequences: Sequences) -> str:
    align = MultipleSeqAlignment([
        SeqRecord(Seq(x.seq), id=x.id) for x in sequences
    ])
    calculator = DistanceCalculator('identity')
    constructor = DistanceTreeConstructor(calculator, 'nj')
    tree = constructor.build_tree(align)
    _format_clades(tree.root)
    newick_io = StringIO()
    NewickIO.write([tree], newick_io)
    newick_string = newick_io.getvalue()
    return _format_newick_for_fitchi(newick_string)


def make_haplo_tree(sequences: Sequences, partition: Partition, tree: str, transversions_only: bool) -> HaploNode:
    sequence_dict = {x.id: x.seq for x in sequences}
    return compute_fitchi_tree(sequence_dict, partition, tree, transversions_only)


def make_haplo_net(graph: Network) -> HaploGraph:
    return HaploGraph(
        [
            HaploGraphNode(
                f'node_{i}',
                Counter({
                    color.color: color.weight
                    for color in node.colors
                })
            )
            for i, node in enumerate(graph.vertices)
        ],
        [
            HaploGraphEdge(edge.u, edge.v, edge.d)
            for edge in graph.edges
        ],
    )
