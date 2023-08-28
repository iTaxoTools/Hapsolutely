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
from itaxotools.fitchi.types import HaploNode
from itaxotools.haplodemo import Window
from itaxotools.haplodemo.types import HaploGraph
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import (
    InputSelector, PartitionSelector, SequenceSelector, TitleCard)
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.tasks import TaskView
from itaxotools.taxi_gui.view.widgets import (
    RadioButtonGroup, RichRadioButton, ScrollArea)

from itaxotools.hapsolutely.gui.fitchi import get_fitchi_divisions
from itaxotools.hapsolutely.gui.graphs import get_graph_divisions

from .types import NetworkAlgorithm


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
        self.settings.rotational_movement = True
        self.settings.recursive_movement = True

        self.settings.show_legend = True
        self.settings.show_scale = True

        self.settings.node_sizes.a = 20
        self.settings.node_sizes.b = 10
        self.settings.node_sizes.c = 1
        self.settings.node_sizes.d = 0
        self.settings.node_sizes.e = 0
        self.settings.node_sizes.f = 20

        self.settings.pen_width_nodes = 1
        self.settings.pen_width_edges = 2

        self.settings.edge_length = 40
        self.settings.node_label_template = 'WEIGHT'

        self.settings.font = QtGui.QFont('Arial', 14)


class NetworkAlgorithmSelector(Card):
    valueChanged = QtCore.Signal(NetworkAlgorithm)

    resetScores = QtCore.Signal()
    algorithms = list(NetworkAlgorithm)

    def __init__(self, parent=None):
        super().__init__(parent)

        label = QtWidgets.QLabel('Network algorithm')
        label.setStyleSheet("""font-size: 16px;""")

        description = QtWidgets.QLabel(
            'Select the algorithm that will be used for building the haplotype network.')
        description.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        layout.addSpacing(4)
        layout.addWidget(description)
        layout.setSpacing(8)

        group = RadioButtonGroup()
        group.valueChanged.connect(self.valueChanged)
        self.controls.algorithm = group

        radios = QtWidgets.QVBoxLayout()
        radios.setSpacing(8)
        for algorithm in self.algorithms:
            button = RichRadioButton(f'{algorithm.label}:', algorithm.description, self)
            radios.addWidget(button)
            group.add(button, algorithm)
        layout.addLayout(radios)
        layout.setContentsMargins(0, 0, 0, 0)

        self.addLayout(layout)

    def setValue(self, value: NetworkAlgorithm):
        self.controls.algorithm.setValue(value)


class TransversionsOnlySelector(Card):
    toggled = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        title = QtWidgets.QCheckBox('  Transversions only:')
        title.setStyleSheet("""font-size: 16px;""")
        title.toggled.connect(self.toggled)
        title.setMinimumWidth(140)

        description = QtWidgets.QLabel('Ignore transitions and show transversions only (default: off).')
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


class EpsilonSelector(Card):
    def __init__(self, parent=None):
        super().__init__(parent)

        title = QtWidgets.QLabel('Epsilon parameter:')
        title.setStyleSheet("""font-size: 16px;""")
        title.setMinimumWidth(140)

        description = QtWidgets.QLabel('Mutation cost weighting in median vector calculation (default: 0).')
        description.setStyleSheet("""padding-top: 2px;""")
        description.setWordWrap(True)

        control = QtWidgets.QSpinBox()
        control.setFixedWidth(80)
        control.setMinimum(0)
        control.setMaximum(9)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(title)
        layout.addWidget(description, 1)
        layout.addWidget(control)
        layout.setSpacing(16)
        self.addLayout(layout)

        self.controls.epsilon = control


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
            'Create haplotype networks from phased sequences.',
            self)
        self.cards.input_sequences = SequenceSelector('Input sequences', self)
        self.cards.input_species = PartitionSelector('Species partition', 'Species', 'Individuals', self)
        self.cards.network_algorithm = NetworkAlgorithmSelector(self)
        self.cards.input_tree = InputSelector('Fitchi tree', self)
        self.cards.transversions_only = TransversionsOnlySelector(self)
        self.cards.epsilon = EpsilonSelector(self)

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
        self.binder.bind(object.request_confirmation, self.requestConfirmation)
        self.binder.bind(object.properties.editable, self.setEditable)
        self.binder.bind(object.properties.done, self.setDone)

        self.binder.bind(object.properties.name, self.cards.title.setTitle)
        self.binder.bind(object.properties.busy, self.cards.title.setBusy)

        self.binder.bind(object.subtask_sequences.properties.busy, self.cards.input_sequences.set_busy)
        self.binder.bind(object.subtask_species.properties.busy, self.cards.input_species.set_busy)

        self.binder.bind(object.properties.network_algorithm, self.cards.network_algorithm.setValue)
        self.binder.bind(self.cards.network_algorithm.valueChanged, object.properties.network_algorithm)

        self.binder.bind(self.cards.epsilon.controls.epsilon.valueChanged, object.properties.epsilon)
        self.binder.bind(object.properties.epsilon, self.cards.epsilon.controls.epsilon.setValue)
        self.binder.bind(
            object.properties.network_algorithm,
            self.cards.epsilon.roll_animation.setAnimatedVisible,
            lambda algo: algo == NetworkAlgorithm.MJN)

        self.binder.bind(self.cards.transversions_only.toggled, object.properties.transversions_only)
        self.binder.bind(object.properties.transversions_only, self.cards.transversions_only.setChecked)

        self.binder.bind(
            object.properties.network_algorithm,
            self.cards.input_tree.roll_animation.setAnimatedVisible,
            lambda algo: algo == NetworkAlgorithm.Fitchi)

        self.binder.bind(
            object.properties.network_algorithm,
            self.cards.transversions_only.roll_animation.setAnimatedVisible,
            lambda algo: algo == NetworkAlgorithm.Fitchi)

        self.binder.bind(object.properties.haplo_tree, self.show_fitchi_tree)
        self.binder.bind(object.properties.haplo_net, self.show_haplo_graph)

        self._bind_input_selector(self.cards.input_sequences, object.input_sequences, object.subtask_sequences)
        self._bind_input_selector(self.cards.input_species, object.input_species, object.subtask_species)
        self._bind_input_selector(self.cards.input_tree, object.input_tree, object.subtask_tree)

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
            'The program may fail or produce false results. \n'
            'Procceed anyway?\n'
        )
        msgBox.setText(text)

        result = self.window().msgShow(msgBox)
        if result == QtWidgets.QMessageBox.Ok:
            callback()
        else:
            abort()

    def setDone(self, done):
        widget = self.haplo_view if done else self.area
        self.stack.setCurrentWidget(widget)

    def setEditable(self, editable: bool):
        for card in self.cards:
            card.setEnabled(editable)
        self.cards.title.setEnabled(True)
        self.haplo_view.setEnabled(not editable)

    def show_fitchi_tree(self, haplo_tree: HaploNode):
        if haplo_tree is None:
            return

        view = self.haplo_view
        scene = self.haplo_view.scene
        divisions = self.haplo_view.divisions

        scene.clear()
        view.reset_settings()

        # print(get_fitchi_string(haplo_tree))

        fitchi_divisions = get_fitchi_divisions(haplo_tree)
        divisions.set_divisions_from_keys(fitchi_divisions)

        scene.add_nodes_from_tree(haplo_tree)

    def show_haplo_graph(self, haplo_graph: HaploGraph):
        if haplo_graph is None:
            return

        view = self.haplo_view
        scene = self.haplo_view.scene
        divisions = self.haplo_view.divisions

        scene.clear()
        view.reset_settings()

        # print(haplo_graph)

        graph_divisions = get_graph_divisions(haplo_graph)
        divisions.set_divisions_from_keys(graph_divisions)

        scene.add_nodes_from_graph(haplo_graph)
