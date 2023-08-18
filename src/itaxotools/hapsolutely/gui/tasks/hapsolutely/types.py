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

from typing import NamedTuple
from enum import Enum

from itaxotools.fitchi.types import HaploNode


class Results(NamedTuple):
    haplo_tree: HaploNode
    haplo_net: object
    seconds_taken: float


class NetworkAlgorithm(Enum):
    Fitchi = 'Fitchi', 'Haplotype genealogies based on Fitch distances'
    TCS = 'TCS', 'Templeton, Crandall, and Sing network (slow)'
    TSW = 'TSW', 'Tight span walker (from PopArt)'
    MST = 'MST', 'Minimum spanning network'
    MJ = 'MJ', 'Median joining network'

    def __init__(self, label, description):
        self.label = label
        self.description = description
