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

from enum import Enum

from itaxotools.common.resources import get_local
from itaxotools.common.widgets import VectorPixmap
from itaxotools.taxi_gui.app import skin
from itaxotools.taxi_gui.app.resources import LazyResourceCollection


class Size(Enum):
    Large = QtCore.QSize(128, 128)
    Medium = QtCore.QSize(64, 64)
    Small = QtCore.QSize(16, 16)

    def __init__(self, size):
        self.size = size


icons = LazyResourceCollection(
    hapsolutely = lambda: QtGui.QIcon(
        get_local(__package__, 'logos/hapsolutely.ico')),
)


pixmaps = LazyResourceCollection(
    hapsolutely = lambda: VectorPixmap(
        get_local(__package__, 'logos/hapsolutely.svg'),
        size=QtCore.QSize(192, 48),
        colormap=skin.colormap_icon),
)


task_pixmaps_large = LazyResourceCollection(
    about = lambda: VectorPixmap(
        get_local(__package__, 'graphics/about.svg'), Size.Large.size),
    nets = lambda: VectorPixmap(
        get_local(__package__, 'graphics/nets.svg'), Size.Large.size),
    phase = lambda: VectorPixmap(
        get_local(__package__, 'graphics/phase.svg'), Size.Large.size),
    stats = lambda: VectorPixmap(
        get_local(__package__, 'graphics/stats.svg'), Size.Large.size),
)


task_pixmaps_medium = LazyResourceCollection(
    about = lambda: VectorPixmap(
        get_local(__package__, 'graphics/about.svg'), Size.Medium.size),
    nets = lambda: VectorPixmap(
        get_local(__package__, 'graphics/nets.svg'), Size.Medium.size),
    phase = lambda: VectorPixmap(
        get_local(__package__, 'graphics/phase.svg'), Size.Medium.size),
    stats = lambda: VectorPixmap(
        get_local(__package__, 'graphics/stats.svg'), Size.Medium.size),
)


task_pixmaps_small = LazyResourceCollection(
    about = lambda: VectorPixmap(
        get_local(__package__, 'graphics/about.svg'), Size.Small.size),
    nets = lambda: VectorPixmap(
        get_local(__package__, 'graphics/nets.svg'), Size.Small.size),
    phase = lambda: VectorPixmap(
        get_local(__package__, 'graphics/phase.svg'), Size.Small.size),
    stats = lambda: VectorPixmap(
        get_local(__package__, 'graphics/stats.svg'), Size.Small.size),
)