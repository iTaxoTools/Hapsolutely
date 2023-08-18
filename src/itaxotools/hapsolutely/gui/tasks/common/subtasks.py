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

from itaxotools.taxi2.partitions import Partition
from itaxotools.taxi2.sequences import Sequences

from .types import Entry


def bundle_entries(

    sequences: Sequences,
    partition: Partition

) -> iter[Entry]:

    cached_id = None
    cached_seq_a = None
    cached_seq_b = None

    for sequence in sequences:
        id = sequence.id[:-1]
        allele = sequence.id[-1]

        if id != cached_id and cached_id is not None:
            yield Entry(
                partition[cached_id + 'a'],
                cached_seq_a,
                cached_seq_b,
            )

        cached_id = id

        match allele:
            case 'a':
                cached_seq_a = sequence.seq
            case 'b':
                cached_seq_b = sequence.seq
            case _:
                raise ValueError(f"Individual {repr(sequence.id)} not ending with 'a' or 'b'. Is the input phased?")

    yield Entry(
        partition[cached_id + 'a'],
        cached_seq_a,
        cached_seq_b,
    )
