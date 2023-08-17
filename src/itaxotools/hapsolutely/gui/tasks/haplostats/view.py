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

from itaxotools.common.utility import AttrDict
from itaxotools.convphase_gui.task.view import ResultDialog, ResultViewer
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import (
    PartitionSelector, SequenceSelector, TitleCard)
from itaxotools.taxi_gui.view.tasks import TaskView


class TightResultViewer(ResultViewer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(0, 0, 0, 0)


class View(TaskView):

    def __init__(self, parent):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = TitleCard(
            'Haplostats',
            'Find unique haplotypes, fields of recombination and subset sharing.',
            self)
        self.cards.results = TightResultViewer('Haplotype statistics', self)
        self.cards.input_sequences = SequenceSelector('Input sequences', self)
        self.cards.input_species = PartitionSelector('Species partition', 'Species', 'Individuals', self)

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

        self.binder.bind(object.properties.haplotype_stats, self.cards.results.setPath)
        self.binder.bind(object.properties.haplotype_stats, self.cards.results.setVisible, lambda x: x is not None)

        self.binder.bind(self.cards.results.view, self.view_results)
        self.binder.bind(self.cards.results.save, self.save_results)

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
            'Procceed anyway?\n'
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
