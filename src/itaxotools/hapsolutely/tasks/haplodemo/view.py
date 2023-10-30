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
from itaxotools.common.utility import AttrDict, override
from itaxotools.common.widgets import HLineSeparator
from itaxotools.fitchi.types import HaploNode
from itaxotools.haplodemo.dialogs import (
    EdgeLengthDialog, EdgeStyleDialog, FontDialog, LabelFormatDialog,
    NodeSizeDialog, OptionsDialog, PenWidthDialog, ScaleMarksDialog)
from itaxotools.haplodemo.scene import GraphicsScene, GraphicsView, Settings
from itaxotools.haplodemo.types import HaploGraph
from itaxotools.haplodemo.views import ColorDelegate, DivisionView, MemberView
from itaxotools.haplodemo.visualizer import Visualizer
from itaxotools.haplodemo.widgets import PaletteSelector
from itaxotools.haplodemo.widgets import PartitionSelector as PartitionComboBox
from itaxotools.haplodemo.widgets import ToggleButton
from itaxotools.haplodemo.zoom import ZoomControl
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.tasks.common.view import (
    InputSelector, PartitionSelector)
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.tasks import TaskView
from itaxotools.taxi_gui.view.widgets import (
    DisplayFrame, RadioButtonGroup, RichRadioButton, ScrollArea)

from ..common.view import GraphicTitleCard, PhasedSequenceSelector
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


class MemberPanel(QtWidgets.QFrame):
    def __init__(self, settings: Settings):
        super().__init__()
        self.setStyleSheet('MemberPanel {background: Palette(Window);}')

        view = MemberView(settings.members)
        view.setIndentation(17)

        label = QtWidgets.QLabel('Node members')
        label.setStyleSheet('QLabel {background: Palette(Shadow); color: Palette(Light); padding-top: 5px; padding-bottom: 5px; padding-left: 0px;}')
        font = label.font()
        font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1)
        label.setFont(font)

        arrow = QtWidgets.QLabel('\u276F')
        arrow.setStyleSheet('QLabel {background: Palette(Shadow); color: Palette(Light); padding-left: 4px; padding-top: 5px; padding-bottom: 5px; padding-right: 0px;}')
        font = arrow.font()
        font.setBold(True)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        font.setHintingPreference(QtGui.QFont.PreferNoHinting)
        arrow.setFont(font)

        label_layout = QtWidgets.QHBoxLayout()
        label_layout.addWidget(arrow)
        label_layout.addWidget(label, 1)

        export = QtWidgets.QPushButton('Export all')

        export_layout = QtWidgets.QVBoxLayout()
        export_layout.setContentsMargins(8, 8, 8, 8)
        export_layout.addWidget(export)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(label_layout)
        layout.addWidget(view)
        layout.addLayout(export_layout)

        self.controls = AttrDict()
        self.controls.view = view
        self.controls.export = export


class HaploView(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.draw()

    def draw(self, opengl=False):
        settings = Settings()

        scene = GraphicsScene(settings)
        visualizer = Visualizer(scene, settings)

        scene_view = GraphicsView(scene, opengl)
        scene_view.setMinimumHeight(400)
        scene_view.setMinimumWidth(400)

        partition_selector = PartitionComboBox(settings.partitions)

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
        toggle_snapping = ToggleButton('Enable snapping')
        toggle_field_groups = ToggleButton('Show groups')
        toggle_field_isolated = ToggleButton('Show isolated')

        member_panel = MemberPanel(settings)

        partition_widget = QtWidgets.QWidget()
        partitions_layout = QtWidgets.QVBoxLayout(partition_widget)
        partitions_layout.setContentsMargins(0, 0, 0, 0)
        partitions_layout.addWidget(partition_selector)
        partitions_layout.addSpacing(4)
        partitions_layout.addWidget(HLineSeparator(1))
        partitions_layout.addSpacing(4)

        dialogs = QtWidgets.QVBoxLayout()
        dialogs.addWidget(mass_resize_nodes)
        dialogs.addWidget(mass_resize_edges)
        dialogs.addWidget(mass_style_edges)
        dialogs.addWidget(style_pens)
        dialogs.addWidget(style_scale)
        dialogs.addWidget(mass_format_labels)
        dialogs.addWidget(select_colors)
        dialogs.addWidget(select_font)

        field_toggles = QtWidgets.QWidget()
        field_toggles_layout = QtWidgets.QVBoxLayout(field_toggles)
        field_toggles_layout.setContentsMargins(0, 0, 0, 0)
        field_toggles_layout.addSpacing(4)
        field_toggles_layout.addWidget(HLineSeparator(1))
        field_toggles_layout.addSpacing(4)
        field_toggles_layout.addWidget(toggle_field_groups)
        field_toggles_layout.addWidget(toggle_field_isolated)

        toggles = QtWidgets.QVBoxLayout()
        toggles.addWidget(toggle_scene_rotation)
        toggles.addWidget(toggle_snapping)
        toggles.addWidget(toggle_lock_distances)
        toggles.addWidget(toggle_lock_labels)
        toggles.addWidget(field_toggles)
        toggles.addSpacing(4)
        toggles.addWidget(HLineSeparator(1))
        toggles.addSpacing(4)
        toggles.addWidget(toggle_legend)
        toggles.addWidget(toggle_scale)

        sidebar_layout = QtWidgets.QVBoxLayout()
        sidebar_layout.setContentsMargins(8, 16, 8, 16)
        sidebar_layout.addWidget(partition_widget)
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

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(scene_view)
        splitter.addWidget(member_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 0)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, True)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(sidebar)
        layout.addWidget(splitter, 1)
        self.setLayout(layout)

        zoom_control = ZoomControl(scene_view, self)

        self.scene = scene
        self.scene_view = scene_view
        self.visualizer = visualizer
        self.zoom_control = zoom_control
        self.settings = settings
        self.divisions = settings.divisions
        self.toggle_lock_distances = toggle_lock_distances
        self.field_toggles = field_toggles
        self.member_view = member_panel.controls.view
        self.splitter = splitter
        self.sidebar = sidebar

        self.partition_widget = partition_widget
        self.partition_selector = partition_selector

        self.binder = Binder()

        self.binder.bind(settings.partitions.partitionsChanged, partition_widget.setVisible, lambda partitions: len(partitions) > 0)
        self.binder.bind(partition_selector.modelIndexChanged, settings.properties.partition_index)
        self.binder.bind(settings.properties.partition_index, partition_selector.setModelIndex)

        self.binder.bind(visualizer.nodeIndexSelected, member_panel.controls.view.select)
        self.binder.bind(member_panel.controls.view.nodeSelected, visualizer.select_node_by_name)

        self.binder.bind(settings.properties.rotational_movement, toggle_lock_distances.setChecked)
        self.binder.bind(settings.properties.recursive_movement, toggle_lock_distances.setChecked)
        self.binder.bind(toggle_lock_distances.toggled, settings.properties.rotational_movement)
        self.binder.bind(toggle_lock_distances.toggled, settings.properties.recursive_movement)

        self.binder.bind(settings.properties.label_movement, toggle_lock_labels.setChecked, lambda x: not x)
        self.binder.bind(toggle_lock_labels.toggled, settings.properties.label_movement, lambda x: not x)

        self.binder.bind(settings.fields.properties.show_groups, toggle_field_groups.setChecked)
        self.binder.bind(toggle_field_groups.toggled, settings.fields.properties.show_groups)

        self.binder.bind(settings.fields.properties.show_isolated, toggle_field_isolated.setChecked)
        self.binder.bind(toggle_field_isolated.toggled, settings.fields.properties.show_isolated)

        self.binder.bind(settings.properties.show_legend, toggle_legend.setChecked)
        self.binder.bind(toggle_legend.toggled, settings.properties.show_legend)

        self.binder.bind(settings.properties.show_scale, toggle_scale.setChecked)
        self.binder.bind(toggle_scale.toggled, settings.properties.show_scale)

        self.binder.bind(settings.properties.rotate_scene, toggle_scene_rotation.setChecked)
        self.binder.bind(toggle_scene_rotation.toggled, settings.properties.rotate_scene)

        self.binder.bind(settings.properties.snapping_movement, toggle_snapping.setChecked)
        self.binder.bind(toggle_snapping.toggled, settings.properties.snapping_movement)

    @override
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_zoom_control_geometry()

    def update_zoom_control_geometry(self):
        gg = self.geometry()
        gg = QtCore.QRect(
            gg.bottomLeft().x() + self.sidebar.width() + 24,
            gg.bottomLeft().y() - self.zoom_control.height() - 24,
            self.sidebar.width(),
            self.sidebar.height(),
        )
        self.zoom_control.setGeometry(gg)

    def update_splitter_sizes(self):
        self.splitter.setSizes([1, self.member_view.sizeHint().width()])

    def set_spartitions(self, spartitions: dict[str, dict[str, str]], spartition: str):
        self.visualizer.set_partitions(spartitions.items())
        self.visualizer.set_partition(spartitions[spartition])
        index = list(spartitions.keys()).index(spartition)
        self.partition_selector.setCurrentIndex(index)

    def reset_settings(self):
        self.settings.reset()

        self.settings.rotational_movement = True
        self.settings.recursive_movement = True

        self.settings.show_legend = True
        self.settings.show_scale = True

        self.settings.edge_length = 40
        self.settings.node_label_template = 'WEIGHT'


class NetworkAlgorithmSelector(Card):
    valueChanged = QtCore.Signal(NetworkAlgorithm)

    resetScores = QtCore.Signal()
    algorithms = list(NetworkAlgorithm)

    def __init__(self, parent=None):
        super().__init__(parent)

        label = QtWidgets.QLabel('Network algorithm:')
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
        title.setMinimumWidth(180)

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


class HaplowebSelector(Card):
    toggled = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        title = QtWidgets.QCheckBox('  Draw haploweb:')
        title.setStyleSheet("""font-size: 16px;""")
        title.toggled.connect(self.toggled)
        title.setMinimumWidth(180)

        description = QtWidgets.QLabel('Connect haplotypes found co-occurring in heterozygous individuals.')
        description.setStyleSheet("""padding-top: 2px;""")
        description.setWordWrap(True)

        warning = QtWidgets.QLabel('Sequences must be phased into alleles.')
        warning.setStyleSheet("""padding-top: 2px; padding-bottom: 4px;""")
        warning.setWordWrap(True)
        warning.setVisible(False)

        spacer = QtWidgets.QSpacerItem(120, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(title, 0, 0)

        layout.setColumnMinimumWidth(1, 16)

        layout.addWidget(description, 0, 2)
        layout.addWidget(warning, 1, 2)
        layout.setColumnStretch(2, 1)

        layout.addItem(spacer, 0, 3)
        self.addLayout(layout)

        self.controls.title = title
        self.controls.warning = warning

    def setChecked(self, checked: bool):
        self.controls.title.setChecked(checked)


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
        self.cards.input_sequences = PhasedSequenceSelector('Input sequences', self)
        self.cards.input_species = PartitionSelector('Species partition', 'Species', 'Individuals', self)
        self.cards.draw_haploweb = HaplowebSelector(self)
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

        self.binder.bind(self.cards.draw_haploweb.toggled, object.properties.draw_haploweb)
        self.binder.bind(object.properties.draw_haploweb, self.cards.draw_haploweb.setChecked)
        self.binder.bind(object.properties.input_is_phased, self.cards.draw_haploweb.roll_animation.setAnimatedVisible)

        self.binder.bind(object.haplo_ready, self.show_haplo_network)

        self.binder.bind(object.properties.can_lock_distances, self.haplo_view.toggle_lock_distances.setVisible)
        self.binder.bind(object.properties.draw_haploweb, self.haplo_view.field_toggles.setVisible)

        self._bind_phased_input_selector(self.cards.input_sequences, object.input_sequences, object.subtask_sequences)
        self._bind_input_selector(self.cards.input_species, object.input_species, object.subtask_species)
        self._bind_input_selector(self.cards.input_tree, object.input_tree, object.subtask_tree)

    def _bind_phased_input_selector(self, card, object, subtask):
        self.binder.bind(card.addInputFile, subtask.start)
        self.binder.bind(card.indexChanged, object.set_index_phased)
        self.binder.bind(object.properties.model, card.set_model)
        self.binder.bind(object.properties.index, card.set_index)
        self.binder.bind(object.properties.object, card.bind_object)

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
            'Proceed anyway?\n'
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
        visualizer = view.visualizer

        view.reset_settings()

        # print(get_fitchi_string(haplo_tree))

        visualizer.visualize_tree(haplo_tree)
        view.update_splitter_sizes()
        view.update_zoom_control_geometry()

        if self._should_draw_haploweb():
            visualizer.visualize_haploweb()

        self._visualize_spartitions()

    def show_haplo_graph(self, haplo_graph: HaploGraph):
        if haplo_graph is None:
            return

        view = self.haplo_view
        visualizer = view.visualizer

        view.reset_settings()

        # print(haplo_graph)

        visualizer.visualize_graph(haplo_graph)
        view.update_splitter_sizes()
        view.update_zoom_control_geometry()

        if self._should_draw_haploweb():
            visualizer.visualize_haploweb()

        self._visualize_spartitions()

    def _should_draw_haploweb(self) -> bool:
        if not self.object:
            return False
        return self.object.input_is_phased and self.object.draw_haploweb

    def _visualize_spartitions(self):
        spartitions = self.object.spartitions
        spartition = self.object.spartition
        if spartitions and spartition:
            self.haplo_view.set_spartitions(spartitions, spartition)

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
