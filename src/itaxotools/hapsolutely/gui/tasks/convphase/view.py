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

from PySide6 import QtCore, QtGui, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.convphase_gui.task.view import (
    InputSequencesSelector, OutputFormatCard, ParameterCard)
from itaxotools.convphase_gui.task.view import View as _View
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.cards import Card

from itaxotools.hapsolutely.gui import resources

from ..common.view import GraphicTitleCard
from . import long_description, pixmap_medium, title


class PhaseResultViewer(Card):
    view = QtCore.Signal(str, Path)
    save = QtCore.Signal(str, Path)

    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.setContentsMargins(6, 2, 6, 2)
        self.text = label_text
        self.path = None

        label = QtWidgets.QLabel(label_text)
        label.setStyleSheet("""font-size: 16px;""")

        check = QtWidgets.QLabel('\u2714')
        check.setStyleSheet("""font-size: 16px; color: Palette(Shadow);""")

        visualize = QtWidgets.QPushButton('Visualize')
        analyze = QtWidgets.QPushButton('Analyze')

        self.add_pixmap_to_button(visualize, resources.task_pixmaps_small.nets.resource)
        self.add_pixmap_to_button(analyze, resources.task_pixmaps_small.stats.resource)

        view = QtWidgets.QPushButton('Preview')
        view.clicked.connect(self.handleView)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(label)
        layout.addSpacing(12)
        layout.addWidget(check)
        layout.addStretch(1)
        layout.addWidget(visualize)
        layout.addSpacing(16)
        layout.addWidget(analyze)
        layout.addSpacing(16)
        layout.addWidget(view)
        self.addLayout(layout)

        self.controls.view = view
        self.controls.visualize = visualize
        self.controls.analyze = analyze

    def setPath(self, path):
        self.path = path
        self.setVisible(path is not None)

    def handleView(self):
        self.view.emit(self.text, self.path)

    def add_pixmap_to_button(self, button, pixmap):
        icon = QtGui.QIcon(pixmap)
        button.setIcon(icon)
        button.setIconSize(pixmap.size())


class View(_View):

    def draw(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.results = PhaseResultViewer('Phased sequences', self)
        self.cards.progress_matrix = ProgressCard(self)
        self.cards.progress_mcmc = ProgressCard(self)
        self.cards.input_sequences = InputSequencesSelector('Input sequences', self)
        self.cards.output_format = OutputFormatCard(self)
        self.cards.parameters = ParameterCard(self)

        layout = QtWidgets.QVBoxLayout()
        for card in self.cards:
            layout.addWidget(card)
        layout.addStretch(1)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)
        self.setLayout(layout)
