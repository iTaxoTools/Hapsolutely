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

from itaxotools.common.utility import AttrDict
from itaxotools.haplodemo import Window

from itaxotools.taxi_gui.view.tasks import TaskView
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import ScrollArea
from itaxotools.taxi_gui.tasks.common.view import (
    SequenceSelector, PartitionSelector, TitleCard
)

from itaxotools.hapsolutely.gui.fitchi import get_fitchi_string, get_fitchi_divisions, get_fitchi_layout
from itaxotools.fitchi.types import HaploNode


class HaploView(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()

        widget = Window()
        widget.layout().setContentsMargins(8, 8, 8, 8)
        self.setWindowFlags(QtCore.Qt.WindowFlags.Widget)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)

        self.settings = widget.settings
        self.divisions = widget.settings.divisions
        self.scene = widget.scene

    def reset_settings(self):
        self.settings.rotational_movement = False
        self.settings.recursive_movement = False
        self.settings.node_a = 0.0
        self.settings.node_e = 5.0
        self.settings.node_f = 10.0

        self.scene.styleNodes(
            self.settings.node_a,
            self.settings.node_b,
            self.settings.node_c,
            self.settings.node_d,
            self.settings.node_e,
            self.settings.node_f,
        )


class View(TaskView):

    def __init__(self, parent):
        super().__init__(parent)

        self.stack = QtWidgets.QStackedLayout(self)
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.area = ScrollArea(self)
        self.haplo_view = HaploView()

        self.stack.addWidget(self.haplo_view)
        self.stack.addWidget(self.area)

        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = TitleCard(
            'TaxoPhase',
            'Reconstruct haplotypes and produce genealogy graphs from population data.',
            self)
        self.cards.input_sequences = SequenceSelector('Input sequences', self)
        self.cards.input_species = PartitionSelector('Species partition', 'Species', 'Individuals', self)

        layout = QtWidgets.QVBoxLayout()
        for card in self.cards:
            layout.addWidget(card)
        layout.addStretch(1)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        self.area.setLayout(layout)

    def ensureVisible(self):
        self.area.ensureVisible(0, 0)

    def start(self):
        self.area.ensureVisible(0, 0)
        super().start()

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

        # self.binder.bind(object.properties.fitchi_tree, self.show_fitchi_tree)

        self._bind_input_selector(self.cards.input_sequences, object.input_sequences, object.subtask_sequences)
        self._bind_input_selector(self.cards.input_species, object.input_species, object.subtask_species)


    def _bind_input_selector(self, card, object, subtask):
        self.binder.bind(card.addInputFile, subtask.start)
        self.binder.bind(card.indexChanged, object.set_index)
        self.binder.bind(object.properties.model, card.set_model)
        self.binder.bind(object.properties.index, card.set_index)
        self.binder.bind(object.properties.object, card.bind_object)

    def setDone(self, done):
        widget = self.haplo_view if done else self.area
        self.stack.setCurrentWidget(widget)

    def setEditable(self, editable: bool):
        for card in self.cards:
            card.setEnabled(editable)
        self.cards.title.setEnabled(True)
        self.haplo_view.setEnabled(not editable)

    def show_fitchi_tree(self, fitchi_tree: HaploNode):
        view = self.haplo_view
        scene = self.haplo_view.scene
        divisions = self.haplo_view.divisions

        scene.clear()
        if fitchi_tree is None:
            return

        print(get_fitchi_string(fitchi_tree))
        fitchi_layout = get_fitchi_layout(fitchi_tree)
        fitchi_divisions = get_fitchi_divisions(fitchi_tree)

        self.add_fitchi_nodes(scene, fitchi_layout, fitchi_tree)
        divisions.set_divisions_from_keys(fitchi_divisions)
        view.reset_settings()

    def add_fitchi_nodes(self, scene, layout, node: HaploNode):
        self._add_fitchi_node_recursive(scene, layout, None, node)

    def _add_fitchi_node_recursive(self, scene, layout, parent, node):
        x, y = layout[node.id]

        if node.pops.total() > 0:
            item = scene.create_node(x, y, node.pops.total(), node.id, dict(node.pops))
        else:
            item = scene.create_vertex(x, y)

        if parent:
            scene.add_child(parent, item, node.mutations)
        else:
            scene.addItem(item)

        for child in node.children:
            self._add_fitchi_node_recursive(scene, layout, item, child)
