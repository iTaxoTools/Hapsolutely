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

from itaxotools.common.bindings import Binder
from itaxotools.common.utility import AttrDict
from itaxotools.common.widgets import HLineSeparator
from itaxotools.fitchi.types import HaploNode
from itaxotools.haplodemo.dialogs import (
    EdgeLengthDialog, EdgeStyleDialog, FontDialog, LabelFormatDialog,
    NodeSizeDialog, OptionsDialog, PenWidthDialog, ScaleMarksDialog)
from itaxotools.haplodemo.scene import GraphicsScene, GraphicsView, Settings
from itaxotools.haplodemo.types import HaploGraph
from itaxotools.haplodemo.widgets import (
    ColorDelegate, DivisionView, PaletteSelector, ToggleButton)
from itaxotools.haplodemo.zoom import ZoomControl
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import (
    InputSelector, PartitionSelector, SequenceSelector)
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.tasks import TaskView
from itaxotools.taxi_gui.view.widgets import (
    DisplayFrame, RadioButtonGroup, RichRadioButton, ScrollArea)

from itaxotools.hapsolutely.gui.fitchi import get_fitchi_divisions
from itaxotools.hapsolutely.gui.graphs import get_graph_divisions

from ..common.view import GraphicTitleCard
from . import long_description, pixmap_medium, title
from .types import NetworkAlgorithm


class ColorDialog(OptionsDialog):
    def __init__(self, parent, settings):
        super().__init__(parent)

        self.setWindowTitle(f'{app.config.title} - Subset colors')

        self.settings = settings
        self.binder = Binder()

        contents = self.draw_contents()
        self.draw_dialog(contents)
        self.hintedResize(280, 60)

    def draw_contents(self):
        label = QtWidgets.QLabel(
            'Select a color theme for population subsets. '
            'Double-click a subset to customize its color.'
        )
        label.setWordWrap(True)
        palette_selector = PaletteSelector()
        division_view = DivisionView(self.settings.divisions)

        self.binder.bind(palette_selector.currentValueChanged, self.settings.properties.palette)
        self.binder.bind(self.settings.properties.palette, palette_selector.setValue)
        self.binder.bind(self.settings.properties.palette, ColorDelegate.setCustomColors)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)
        layout.addWidget(label)
        layout.addSpacing(8)
        layout.addWidget(palette_selector)
        layout.addWidget(division_view)
        return layout

    def draw_dialog(self, contents):
        ok = QtWidgets.QPushButton('OK')

        ok.clicked.connect(self.accept)
        ok.setAutoDefault(True)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(ok)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(contents, 1)
        layout.addSpacing(8)
        layout.addLayout(buttons)
        self.setLayout(layout)


class HaploView(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.draw()

    def draw(self, opengl=False):
        settings = Settings()

        scene = GraphicsScene(settings)

        scene.style_labels(settings.node_label_template, settings.edge_label_template)

        scene_view = GraphicsView(scene, opengl)

        self.node_size_dialog = NodeSizeDialog(self, scene, settings.node_sizes)
        self.edge_style_dialog = EdgeStyleDialog(self, scene)
        self.edge_length_dialog = EdgeLengthDialog(self, scene, settings)
        self.scale_style_dialog = ScaleMarksDialog(self, scene, settings.scale)
        self.pen_style_dialog = PenWidthDialog(self, scene, settings)
        self.label_format_dialog = LabelFormatDialog(self, scene, settings)
        self.color_dialog = ColorDialog(self, settings)
        self.font_dialog = FontDialog(self, settings)

        self.node_size_dialog.setWindowTitle(f'{app.config.title} - Node size')
        self.edge_style_dialog.setWindowTitle(f'{app.config.title} - Edge styles')
        self.edge_length_dialog.setWindowTitle(f'{app.config.title} - Edge lengths')
        self.scale_style_dialog.setWindowTitle(f'{app.config.title} - Scale marks')
        self.pen_style_dialog.setWindowTitle(f'{app.config.title} - Pen width')
        self.label_format_dialog.setWindowTitle(f'{app.config.title} - Label format')
        self.color_dialog.setWindowTitle(f'{app.config.title} - Subset colors')
        self.font_dialog.setWindowTitle(f'{app.config.title} - Select font')

        mass_resize_nodes = QtWidgets.QPushButton('Set node size')
        mass_resize_nodes.clicked.connect(self.node_size_dialog.show)

        mass_resize_edges = QtWidgets.QPushButton('Set edge length')
        mass_resize_edges.clicked.connect(self.edge_length_dialog.show)

        mass_style_edges = QtWidgets.QPushButton('Set edge styles')
        mass_style_edges.clicked.connect(self.edge_style_dialog.show)

        style_pens = QtWidgets.QPushButton('Set pen width')
        style_pens.clicked.connect(self.pen_style_dialog.show)

        style_scale = QtWidgets.QPushButton('Set scale marks')
        style_scale.clicked.connect(self.scale_style_dialog.show)

        mass_format_labels = QtWidgets.QPushButton('Set label format')
        mass_format_labels.clicked.connect(self.label_format_dialog.show)

        select_colors = QtWidgets.QPushButton('Set subset colors')
        select_colors.clicked.connect(self.color_dialog.show)

        select_font = QtWidgets.QPushButton('Set font')
        select_font.clicked.connect(self.font_dialog.exec)

        toggle_lock_distances = ToggleButton('Lock distances')
        toggle_lock_labels = ToggleButton('Lock labels')
        toggle_legend = ToggleButton('Show legend')
        toggle_scale = ToggleButton('Show scale')
        toggle_scene_rotation = ToggleButton('Rotate scene')

        dialogs = QtWidgets.QVBoxLayout()
        dialogs.addWidget(mass_resize_nodes)
        dialogs.addWidget(mass_resize_edges)
        dialogs.addWidget(mass_style_edges)
        dialogs.addWidget(style_pens)
        dialogs.addWidget(style_scale)
        dialogs.addWidget(mass_format_labels)
        dialogs.addWidget(select_colors)
        dialogs.addWidget(select_font)

        toggles = QtWidgets.QVBoxLayout()
        toggles.addWidget(toggle_scene_rotation)
        toggles.addWidget(toggle_lock_distances)
        toggles.addWidget(toggle_lock_labels)
        toggles.addWidget(toggle_legend)
        toggles.addWidget(toggle_scale)

        sidebar_layout = QtWidgets.QVBoxLayout()
        sidebar_layout.setContentsMargins(8, 16, 8, 16)
        sidebar_layout.addLayout(dialogs)
        sidebar_layout.addSpacing(4)
        sidebar_layout.addWidget(HLineSeparator(1))
        sidebar_layout.addSpacing(4)
        sidebar_layout.addLayout(toggles)
        sidebar_layout.addStretch(1)

        sidebar = QtWidgets.QFrame()
        sidebar.setStyleSheet('QFrame {background: Palette(window);}')
        sidebar.setLayout(sidebar_layout)
        sidebar.setFixedWidth(192)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(sidebar)
        layout.addWidget(scene_view, 1)
        self.setLayout(layout)

        zoom_control = ZoomControl(scene_view, self)

        self.scene = scene
        self.scene_view = scene_view
        self.zoom_control = zoom_control
        self.settings = settings
        self.divisions = settings.divisions
        self.toggle_lock_distances = toggle_lock_distances

        self.binder = Binder()

        self.binder.bind(settings.properties.rotational_movement, toggle_lock_distances.setChecked)
        self.binder.bind(settings.properties.recursive_movement, toggle_lock_distances.setChecked)
        self.binder.bind(toggle_lock_distances.toggled, settings.properties.rotational_movement)
        self.binder.bind(toggle_lock_distances.toggled, settings.properties.recursive_movement)

        self.binder.bind(settings.properties.label_movement, toggle_lock_labels.setChecked, lambda x: not x)
        self.binder.bind(toggle_lock_labels.toggled, settings.properties.label_movement, lambda x: not x)

        self.binder.bind(settings.properties.show_legend, toggle_legend.setChecked)
        self.binder.bind(toggle_legend.toggled, settings.properties.show_legend)

        self.binder.bind(settings.properties.show_scale, toggle_scale.setChecked)
        self.binder.bind(toggle_scale.toggled, settings.properties.show_scale)

        self.binder.bind(settings.properties.rotate_scene, toggle_scene_rotation.setChecked)
        self.binder.bind(toggle_scene_rotation.toggled, settings.properties.rotate_scene)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        gg = self.scene_view.geometry()
        gg.setTopLeft(QtCore.QPoint(
            gg.bottomRight().x() - self.zoom_control.width() - 16,
            gg.bottomRight().y() - self.zoom_control.height() - 16,
        ))
        self.zoom_control.setGeometry(gg)

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

    def __init__(self, parent=None, max_width=920):
        super().__init__(parent)
        self.max_width = max_width

        self.stack = QtWidgets.QStackedLayout(self)
        self.stack.setContentsMargins(0, 0, 0, 0)

        self.area = ScrollArea(self)
        self.haplo_view = HaploView()

        self.stack.addWidget(self.haplo_view)
        self.stack.addWidget(self.area)

        self.frame = DisplayFrame(stretch=999, center_vertical=False)
        self.inner_frame = DisplayFrame(stretch=99, center_vertical=False)
        self.inner_frame.setStyleSheet('DisplayFrame {background: Palette(mid);}')
        self.inner_frame.setMaximumWidth(self.max_width)
        self.inner_frame.setContentsMargins(4, 8, 4, 8)
        self.area.setWidget(self.frame)
        self.frame.setWidget(self.inner_frame)

        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
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

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.inner_frame.setWidget(widget)

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

        self.binder.bind(object.haplo_ready, self.show_haplo_network)

        self.binder.bind(object.properties.can_lock_distances, self.haplo_view.toggle_lock_distances.setVisible)

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

    def show_haplo_network(self):
        wait_cursor = QtGui.QCursor(QtCore.Qt.WaitCursor)
        QtGui.QGuiApplication.setOverrideCursor(wait_cursor)

        if self.object.haplo_tree is not None:
            self.show_fitchi_tree(self.object.haplo_tree)
        if self.object.haplo_graph is not None:
            self.show_haplo_graph(self.object.haplo_graph)

        QtGui.QGuiApplication.restoreOverrideCursor()

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

    def save(self):
        path = Path(self.object.input_sequences.object.info.path)
        path = path.with_name(f'{path.stem}.network')
        scene_view = self.haplo_view.scene_view
        filters = {
            'PNG Files (*.png)': scene_view.export_png,
            'SVG Files (*.svg)': scene_view.export_svg,
            'PDF Files (*.pdf)': scene_view.export_pdf,
        }
        filename, format = QtWidgets.QFileDialog.getSaveFileName(
            self.window(), f'{app.config.title} - Export Network',
            dir=str(path), filter=';;'.join(filters.keys()))
        if not filename:
            return None
        filters[format](filename)
