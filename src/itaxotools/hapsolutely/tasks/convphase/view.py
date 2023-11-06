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
from itaxotools.convphase_gui.task.view import WarningViewer
from itaxotools.taxi_gui import app as global_app
from itaxotools.taxi_gui.tasks.common.view import ProgressCard
from itaxotools.taxi_gui.view.cards import Card

from itaxotools.hapsolutely import app, resources

from ..common.view import GraphicTitleCard
from ..haplodemo.model import Model as VisualizeModel
from ..haplostats.model import Model as AnalyzeModel
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
        font = check.font()
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        font.setHintingPreference(QtGui.QFont.PreferNoHinting)
        check.setFont(font)

        cross = QtWidgets.QLabel('\u2718')
        cross.setStyleSheet("""font-size: 16px; color: Palette(Shadow);""")
        font = cross.font()
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        font.setHintingPreference(QtGui.QFont.PreferNoHinting)
        cross.setFont(font)

        visualize = QtWidgets.QPushButton('Visualize')
        analyze = QtWidgets.QPushButton('Analyze')

        visualize.clicked.connect(self.handle_visualize)
        analyze.clicked.connect(self.handle_analyze)

        self.add_pixmap_to_button(visualize, resources.task_pixmaps_small.nets.resource)
        self.add_pixmap_to_button(analyze, resources.task_pixmaps_small.stats.resource)

        view = QtWidgets.QPushButton('Preview')
        view.clicked.connect(self.handleView)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(label)
        layout.addSpacing(12)
        layout.addWidget(check)
        layout.addWidget(cross)
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
        self.controls.check = check
        self.controls.cross = cross

    def setPath(self, path):
        self.path = path
        self.setVisible(path is not None)

    def handleView(self):
        self.view.emit(self.text, self.path)

    def add_pixmap_to_button(self, button, pixmap):
        icon = QtGui.QIcon(pixmap)
        button.setIcon(icon)
        button.setIconSize(pixmap.size())

    def handle_visualize(self):
        self.propagate_reults_to_model(VisualizeModel)

    def handle_analyze(self):
        self.propagate_reults_to_model(AnalyzeModel)

    def propagate_reults_to_model(self, klass):
        model_index = global_app.model.items.find_task(klass)
        if model_index is None:
            model_index = global_app.model.items.add_task(klass())
        item = global_app.model.items.data(
            model_index, role=global_app.model.items.ItemRole)
        input_sequences = item.object.input_sequences
        proxy = input_sequences.model
        source_index = app.phased_results.index
        proxy_index = proxy.mapFromSource(source_index)
        input_sequences.set_index(proxy_index)
        item.object.clear()
        global_app.model.items.focus(model_index)


class View(_View):

    def draw(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.results = PhaseResultViewer('Phased sequences', self)
        self.cards.warnings = WarningViewer(self)
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
