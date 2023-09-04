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

from PySide6 import QtCore, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.convphase_gui.task.view import ResultDialog
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import PartitionSelector
from itaxotools.taxi_gui.types import FileFormat
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.tasks import ScrollTaskView

from ..common.view import GraphicTitleCard, PhasedSequenceSelector
from . import long_description, pixmap_medium, title


class BulkModeSelector(Card):
    toggled = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        title = QtWidgets.QCheckBox('  Bulk mode:')
        title.setStyleSheet("""font-size: 16px;""")
        title.toggled.connect(self.toggled)
        title.setMinimumWidth(140)

        description = QtWidgets.QLabel('Get statistics for each spartition in the SPART file.')
        description.setStyleSheet("""padding-top: 2px;""")
        description.setWordWrap(True)

        contents = QtWidgets.QHBoxLayout()
        contents.addWidget(title)
        contents.addWidget(description, 1)
        contents.setSpacing(16)

        layout = QtWidgets.QHBoxLayout()
        layout.addLayout(contents, 1)
        layout.addSpacing(80)
        self.addLayout(layout)

        self.controls.title = title

    def setChecked(self, checked: bool):
        self.controls.title.setChecked(checked)


class StatsResultViewer(Card):
    view = QtCore.Signal(str, Path)

    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.text = label_text
        self.path = None

        label = QtWidgets.QLabel(label_text)
        label.setStyleSheet("""font-size: 16px;""")

        check = QtWidgets.QLabel('\u2714')
        check.setStyleSheet("""font-size: 16px; color: Palette(Shadow);""")

        view = QtWidgets.QPushButton('Preview')
        view.clicked.connect(self.handleView)

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(label)
        layout.addSpacing(12)
        layout.addWidget(check)
        layout.addStretch(1)
        layout.addWidget(view)
        self.addLayout(layout)

        self.controls.view = view

    def setPath(self, path):
        self.path = path
        self.setVisible(path is not None)

    def handleView(self):
        self.view.emit(self.text, self.path)


class View(ScrollTaskView):

    def __init__(self, parent):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.results = StatsResultViewer('Haplotype statistics', self)
        self.cards.input_sequences = PhasedSequenceSelector('Input sequences', self)
        self.cards.input_species = PartitionSelector('Input partition', 'Partition', 'Individuals', self)
        self.cards.bulk_mode = BulkModeSelector(self)

        layout = QtWidgets.QVBoxLayout()
        for card in self.cards:
            layout.addWidget(card)
        layout.addStretch(1)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        self.setLayout(layout)

    def setObject(self, object):
        self.object = object
        self.binder.unbind_all()

        self.binder.bind(object.notification, self.showNotification)
        self.binder.bind(object.request_confirmation, self.requestConfirmation)
        self.binder.bind(object.properties.editable, self.setEditable)

        self.binder.bind(object.properties.name, self.cards.title.setTitle)
        self.binder.bind(object.properties.busy, self.cards.title.setBusy)

        self.binder.bind(object.subtask_sequences.properties.busy, self.cards.input_sequences.set_busy)
        self.binder.bind(object.subtask_species.properties.busy, self.cards.input_species.set_busy)

        self.binder.bind(self.cards.bulk_mode.toggled, object.properties.bulk_mode)
        self.binder.bind(object.properties.bulk_mode, self.cards.bulk_mode.setChecked)
        self.binder.bind(
            self.cards.bulk_mode.toggled,
            self.cards.input_species.controls.spart.spartition.setEnabled,
            lambda bulk: not bulk)
        self.binder.bind(
            object.input_species.properties.format,
            self.cards.bulk_mode.roll_animation.setAnimatedVisible,
            lambda format: format == FileFormat.Spart)

        self.binder.bind(object.properties.haplotype_stats, self.cards.results.setPath)
        self.binder.bind(object.properties.haplotype_stats, self.cards.results.setVisible, lambda x: x is not None)

        self.binder.bind(self.cards.results.view, self.view_results)

        self._bind_input_selector(self.cards.input_sequences, object.input_sequences, object.subtask_sequences)
        self._bind_input_selector(self.cards.input_species, object.input_species, object.subtask_species)

    def _bind_input_selector(self, card, object, subtask):
        self.binder.bind(card.addInputFile, subtask.start)
        self.binder.bind(card.indexChanged, object.set_index)
        self.binder.bind(object.properties.model, card.set_model)
        self.binder.bind(object.properties.index, card.set_index)
        self.binder.bind(object.properties.object, card.bind_object)

    def requestConfirmation(self, warns, callback, abort):
        msgBox = QtWidgets.QMessageBox(self.window())
        msgBox.setWindowTitle(f'{app.config.title} - Warning')
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)

        text = (
            'Problems detected with input file: \n\n' +
            '\n'.join('- ' + str(warn) for warn in warns) + '\n\n'
            'The program may produce false results. \n'
            'Proceed anyway?\n'
        )
        msgBox.setText(text)

        result = self.window().msgShow(msgBox)
        if result == QtWidgets.QMessageBox.Ok:
            callback()
        else:
            abort()

    def setEditable(self, editable: bool):
        self.cards.title.setEnabled(True)
        self.cards.results.setEnabled(True)
        self.cards.input_sequences.setEnabled(editable)
        self.cards.input_species.setEnabled(editable)
        self.cards.bulk_mode.setEnabled(editable)

    def view_results(self, text, path):
        dialog = ResultDialog(text, path, self.window())
        dialog.save.connect(self.save_results)
        self.window().msgShow(dialog)

    def save_results(self):
        path = self.getSavePath('Save statistics', str(self.object.suggested_results))
        if path:
            self.object.save(path)

    def save(self):
        self.save_results()
