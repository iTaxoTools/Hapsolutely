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

from PySide6 import QtCore, QtGui

from itaxotools.common.resources import get_local
from itaxotools.common.widgets import VectorPixmap
from itaxotools.taxi_gui.app.resources import LazyResourceCollection
from itaxotools.taxi_gui.app import skin


icons = LazyResourceCollection(
    hapsolutely = lambda: QtGui.QIcon(
        get_local(__package__, 'logos/hapsolutely.ico')),
)


pixmaps = LazyResourceCollection(
    hapsolutely = lambda: VectorPixmap(
        get_local(__package__, 'logos/hapsolutely.svg'),
        size=QtCore.QSize(192, 48),
        colormap=skin.colormap_icon),
    about = lambda: VectorPixmap(
        get_local(__package__, 'graphics/about.svg'),
        size=QtCore.QSize(128, 128)),
    nets = lambda: VectorPixmap(
        get_local(__package__, 'graphics/nets.svg'),
        size=QtCore.QSize(128, 128)),
    phase = lambda: VectorPixmap(
        get_local(__package__, 'graphics/phase.svg'),
        size=QtCore.QSize(128, 128)),
    stats = lambda: VectorPixmap(
        get_local(__package__, 'graphics/stats.svg'),
        size=QtCore.QSize(128, 128)),
)
