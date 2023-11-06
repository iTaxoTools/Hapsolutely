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

from PySide6 import QtWidgets

from itaxotools.common.widgets import HLineSeparator


class CategoryFrame(QtWidgets.QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel(text + ' : ')
        label.setStyleSheet('color: Palette(Dark); padding-left: 2px;')

        title = QtWidgets.QVBoxLayout()
        title.addWidget(label)
        title.addWidget(HLineSeparator(1))
        title.setContentsMargins(0, 0, 0, 0)
        title.setSpacing(1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(title)
        layout.addSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._layout = layout

    def addWidget(self, widget):
        self._layout.addWidget(widget)

    def addLayout(self, layout):
        self._layout.addLayout(layout)

    def addSpacing(self, spacing):
        self._layout.addSpacing(spacing)
