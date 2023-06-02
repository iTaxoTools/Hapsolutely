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

from io import StringIO

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Align import MultipleSeqAlignment
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
from Bio.Phylo import NewickIO

from itaxotools.taxi2.sequences import Sequence, Sequences
from itaxotools.convphase.phase import iter_phase
from itaxotools.convphase.types import PhasedSequence, UnphasedSequence


def phase(sequences: Sequences) -> Sequences:
    unphased = (UnphasedSequence(x.id, x.seq) for x in sequences)
    phased = iter_phase(unphased)
    results = []
    for x in phased:
        results.append(Sequence(x.id + 'a', x.data_a))
        results.append(Sequence(x.id + 'b', x.data_b))
    return Sequences(results)


def make_tree_nj(sequences: Sequences) -> str:
    align = MultipleSeqAlignment([
        SeqRecord(Seq(x.seq), id=x.id) for x in sequences
    ])
    calculator = DistanceCalculator('identity')
    constructor = DistanceTreeConstructor(calculator, 'nj')
    tree = constructor.build_tree(align)
    newick_io = StringIO()
    NewickIO.write([tree], newick_io)
    newick_string = newick_io.getvalue()
    return newick_string
