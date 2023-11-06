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

from itaxotools.common.resources import get_common, get_local
from itaxotools.common.widgets import VectorIcon, VectorPixmap
from itaxotools.taxi_gui.app import skin
from itaxotools.taxi_gui.app.resources import LazyResourceCollection


class Size(Enum):
    Large = QtCore.QSize(128, 128)
    Medium = QtCore.QSize(64, 64)
    Small = QtCore.QSize(16, 16)

    def __init__(self, size):
        self.size = size


def text_from_path(path) -> str:
    with open(path, 'r') as file:
        return file.read()


documents = LazyResourceCollection(
    about = lambda: text_from_path(
        get_local(__package__, 'documents/about.html')),
    phase = lambda: text_from_path(
        get_local(__package__, 'documents/phase.html')),
    nets = lambda: text_from_path(
        get_local(__package__, 'documents/nets.html')),
)


icons = LazyResourceCollection(
    hapsolutely = lambda: QtGui.QIcon(
        get_local(__package__, 'logos/hapsolutely.ico')),

    arrow = lambda: VectorIcon(
        get_common('icons/svg/arrow-right.svg'), skin.colormap, Size.Small.size),

    undo = lambda: VectorIcon(
        get_local(__package__, 'icons/undo.svg'), skin.colormap, Size.Small.size),
    redo = lambda: VectorIcon(
        get_local(__package__, 'icons/redo.svg'), skin.colormap, Size.Small.size),
    rotate = lambda: VectorIcon(
        get_local(__package__, 'icons/rotate.svg'), skin.colormap, Size.Small.size),
    snap = lambda: VectorIcon(
        get_local(__package__, 'icons/snap.svg'), skin.colormap, Size.Small.size),
    lock_labels = lambda: VectorIcon(
        get_local(__package__, 'icons/lock_labels.svg'), skin.colormap, Size.Small.size),
    lock_distances = lambda: VectorIcon(
        get_local(__package__, 'icons/lock_distances.svg'), skin.colormap, Size.Small.size),

    scheme = lambda: VectorIcon(
        get_local(__package__, 'icons/scheme.svg'), skin.colormap, Size.Small.size),
    resize_node = lambda: VectorIcon(
        get_local(__package__, 'icons/resize_node.svg'), skin.colormap, Size.Small.size),
    resize_edge = lambda: VectorIcon(
        get_local(__package__, 'icons/resize_edge.svg'), skin.colormap, Size.Small.size),
    edge_style = lambda: VectorIcon(
        get_local(__package__, 'icons/edge_style.svg'), skin.colormap, Size.Small.size),
    pen = lambda: VectorIcon(
        get_local(__package__, 'icons/pen.svg'), skin.colormap, Size.Small.size),
    scale = lambda: VectorIcon(
        get_local(__package__, 'icons/scale.svg'), skin.colormap, Size.Small.size),
    template = lambda: VectorIcon(
        get_local(__package__, 'icons/template.svg'), skin.colormap, Size.Small.size),
    font = lambda: VectorIcon(
        get_local(__package__, 'icons/font.svg'), skin.colormap, Size.Small.size),


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
