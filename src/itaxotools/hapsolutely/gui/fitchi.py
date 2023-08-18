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

from io import StringIO

from itaxotools.fitchi import HaploNode


def get_fitchi_string(haplo_tree: HaploNode) -> str:
    haplo_string = StringIO()
    haplo_tree.print(file=haplo_string)
    return haplo_string.getvalue()


def _recursive_update_divisions(divisions: set, node: HaploNode):
    divisions.update(node.pops.keys())
    for child in node.children:
        _recursive_update_divisions(divisions, child)


def get_fitchi_divisions(haplo_tree: HaploNode) -> set[str]:
    divisions = set()
    _recursive_update_divisions(divisions, haplo_tree)
    return list(divisions)
