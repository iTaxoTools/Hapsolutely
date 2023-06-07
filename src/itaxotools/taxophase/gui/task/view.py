# -----------------------------------------------------------------------------
# TaxoPhase - Reconstruct haplotypes and produce genealogy graphs
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

from itaxotools.common.utility import AttrDict
from itaxotools.haplodemo import Window

from itaxotools.taxi_gui.view.tasks import TaskView
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.tasks.common.view import (
    SequenceSelector, PartitionSelector, TitleCard
)


class HaploCard(Card):
    def __init__(self):
        super().__init__()
        widget = Window()
        widget.setWindowFlags(QtCore.Qt.WindowFlags.Widget)
        widget.setContentsMargins(0, 0, 0, 0)
        self.addWidget(widget)
        self.setContentsMargins(0, 0, 0, 0)


class View(TaskView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw()

    def draw(self):
        self.cards = AttrDict()
        self.cards.title = TitleCard(
            'TaxoPhase',
            'Reconstruct haplotypes and produce genealogy graphs from population data.',
            self)
        self.cards.input_sequences = SequenceSelector('Input sequences', self)
        self.cards.input_species = PartitionSelector('Species partition', 'Species', 'Individuals', self)
        self.cards.haplo_view = HaploCard()

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
        self.binder.bind(object.properties.editable, self.setEditable)
        self.binder.bind(object.properties.done, self.setDone)

        self.binder.bind(object.properties.name, self.cards.title.setTitle)
        self.binder.bind(object.properties.busy, self.cards.title.setBusy)

        self.binder.bind(object.subtask_sequences.properties.busy, self.cards.input_sequences.set_busy)
        self.binder.bind(object.subtask_species.properties.busy, self.cards.input_species.set_busy)

        self._bind_input_selector(self.cards.input_sequences, object.input_sequences, object.subtask_sequences)
        self._bind_input_selector(self.cards.input_species, object.input_species, object.subtask_species)


    def _bind_input_selector(self, card, object, subtask):
        self.binder.bind(card.addInputFile, subtask.start)
        self.binder.bind(card.indexChanged, object.set_index)
        self.binder.bind(object.properties.model, card.set_model)
        self.binder.bind(object.properties.index, card.set_index)
        self.binder.bind(object.properties.object, card.bind_object)

    def setDone(self, done):
        for card in self.cards:
            card.setVisible(not done)
        self.cards.haplo_view.setVisible(done)

    def setEditable(self, editable: bool):
        for card in self.cards:
            card.setEnabled(editable)
        self.cards.title.setEnabled(True)
        self.cards.haplo_view.setEnabled(not editable)
