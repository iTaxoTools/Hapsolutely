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
from itaxotools.taxi_gui.tasks.common.view import SequenceSelector
from itaxotools.taxi_gui.types import FileFormat
from itaxotools.taxi_gui.utility import human_readable_size
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import NoWheelComboBox


class PhasedSequenceSelector(SequenceSelector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_phasing_optional = False
        self.object = None

    def draw_config_tabfile(self):
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        column = 0

        type_label = QtWidgets.QLabel("File format:")
        size_label = QtWidgets.QLabel("File size:")

        layout.addWidget(type_label, 0, column)
        layout.addWidget(size_label, 1, column)
        column += 1

        layout.setColumnMinimumWidth(column, 8)
        column += 1

        type_label_value = QtWidgets.QLabel("Tabfile")
        size_label_value = QtWidgets.QLabel("42 MB")

        layout.addWidget(type_label_value, 0, column)
        layout.addWidget(size_label_value, 1, column)
        column += 1

        layout.setColumnMinimumWidth(column, 4)
        column += 1

        index_label = QtWidgets.QLabel("Indices:")
        sequence_label = QtWidgets.QLabel("Sequences:")
        allele_label = QtWidgets.QLabel("Alleles:")

        layout.addWidget(index_label, 0, column)
        layout.addWidget(sequence_label, 1, column)
        layout.addWidget(allele_label, 2, column)
        column += 1

        layout.setColumnMinimumWidth(column, 8)
        column += 1

        index_combo = NoWheelComboBox()
        sequence_combo = NoWheelComboBox()
        allele_combo = NoWheelComboBox()

        layout.addWidget(index_combo, 0, column)
        layout.addWidget(sequence_combo, 1, column)
        layout.addWidget(allele_combo, 2, column)
        layout.setColumnStretch(column, 1)
        column += 1

        layout.setColumnMinimumWidth(column, 16)
        column += 1

        view = QtWidgets.QPushButton("View")
        view.setVisible(False)

        layout.addWidget(view, 0, column)
        layout.setColumnMinimumWidth(column, 80)
        column += 1

        spacer = QtWidgets.QSpacerItem(
            146, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        layout.addItem(spacer, 0, 0, 2, 3)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.controls.tabfile = AttrDict()
        self.controls.tabfile.widget = widget
        self.controls.tabfile.index_combo = index_combo
        self.controls.tabfile.sequence_combo = sequence_combo
        self.controls.tabfile.allele_combo = allele_combo
        self.controls.tabfile.file_format = type_label_value
        self.controls.tabfile.file_size = size_label_value
        self.controls.config.addWidget(widget)

    def draw_config_fasta(self):
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        column = 0

        type_label = QtWidgets.QLabel("File format:")
        size_label = QtWidgets.QLabel("File size:")

        layout.addWidget(type_label, 0, column)
        layout.addWidget(size_label, 1, column)
        column += 1

        layout.setColumnMinimumWidth(column, 8)
        column += 1

        type_label_value = QtWidgets.QLabel("Tabfile")
        size_label_value = QtWidgets.QLabel("42 MB")

        layout.addWidget(type_label_value, 0, column)
        layout.addWidget(size_label_value, 1, column)
        column += 1

        layout.setColumnMinimumWidth(column, 4)
        column += 1

        parse_alleles = QtWidgets.QCheckBox("Sequences are phased")
        parse_organism = QtWidgets.QCheckBox("Sequences are partitioned")

        parse_pattern_arrow = QtWidgets.QLabel("\u2937")
        font = parse_pattern_arrow.font()
        font.setPixelSize(14)
        font.setBold(True)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        font.setHintingPreference(QtGui.QFont.PreferNoHinting)
        parse_pattern_arrow.setFont(font)

        parse_pattern = QtWidgets.QLabel(
            'Parse identifiers as "individual_allele|taxon"'
        )

        parse_pattern_all = QtWidgets.QWidget()
        pattern_layout = QtWidgets.QHBoxLayout(parse_pattern_all)
        pattern_layout.addSpacing(2)
        pattern_layout.addWidget(parse_pattern_arrow)
        pattern_layout.addWidget(parse_pattern, 1)
        pattern_layout.setContentsMargins(0, 0, 0, 0)
        pattern_layout.setSpacing(6)

        layout.addWidget(parse_alleles, 0, column + 0)
        layout.addWidget(parse_organism, 0, column + 2)
        layout.addWidget(parse_pattern_all, 1, column, 1, 4)
        layout.setColumnMinimumWidth(column + 1, 16)
        layout.setColumnMinimumWidth(column + 3, 4)
        layout.setColumnStretch(column + 3, 1)
        column += 4

        layout.setColumnMinimumWidth(column, 16)
        layout.setColumnStretch(column, 1)
        column += 1

        view = QtWidgets.QPushButton("View")
        view.setVisible(False)

        layout.addWidget(view, 0, column)
        layout.setColumnMinimumWidth(column, 80)
        column += 1

        spacer = QtWidgets.QSpacerItem(
            146, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        layout.addItem(spacer, 0, 0, 2, 3)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.controls.fasta = AttrDict()
        self.controls.fasta.widget = widget
        self.controls.fasta.file_format = type_label_value
        self.controls.fasta.file_size = size_label_value
        self.controls.fasta.parse_organism = parse_organism
        self.controls.fasta.parse_alleles = parse_alleles
        self.controls.fasta.parse_pattern = parse_pattern
        self.controls.config.addWidget(widget)

    def bind_object(self, object):
        self.binder.unbind_all()
        self.object = object
        format = object.info.format if object else None
        {
            FileFormat.Tabfile: self._bind_tabfile,
            FileFormat.Fasta: self._bind_fasta,
            None: self._bind_none,
        }[format](object)
        self.update()

    def _bind_tabfile(self, object):
        self.binder.bind(
            object.properties.is_phasing_optional, self.set_is_phasing_optional
        )
        self._populate_headers(object.info.headers)

        self.binder.bind(
            object.properties.index_column,
            self.controls.tabfile.index_combo.setCurrentIndex,
        )
        self.binder.bind(
            self.controls.tabfile.index_combo.currentIndexChanged,
            object.properties.index_column,
        )
        self.binder.bind(
            object.properties.sequence_column,
            self.controls.tabfile.sequence_combo.setCurrentIndex,
        )
        self.binder.bind(
            self.controls.tabfile.sequence_combo.currentIndexChanged,
            object.properties.sequence_column,
        )
        self.binder.bind(
            object.properties.allele_column,
            self.controls.tabfile.allele_combo.setCurrentIndex,
            lambda x: x if not self.is_phasing_optional else x + 1,
        )
        self.binder.bind(
            self.controls.tabfile.allele_combo.currentIndexChanged,
            object.properties.allele_column,
            lambda x: x if not self.is_phasing_optional else x - 1,
        )
        self.binder.bind(
            object.properties.info,
            self.controls.tabfile.file_size.setText,
            lambda info: human_readable_size(info.size),
        )

        self.controls.tabfile.file_format.setText(object.info.format.label)

        self.controls.config.setCurrentWidget(self.controls.tabfile.widget)
        self.controls.config.setVisible(True)

    def _bind_fasta(self, object):
        self.binder.bind(
            object.properties.has_subsets, self.controls.fasta.parse_organism.setEnabled
        )
        self.binder.bind(
            object.properties.parse_subset,
            self.controls.fasta.parse_organism.setChecked,
        )
        self.binder.bind(
            self.controls.fasta.parse_organism.toggled, object.properties.parse_subset
        )
        self.binder.bind(
            object.properties.is_phased, self.controls.fasta.parse_alleles.setChecked
        )
        self.binder.bind(
            self.controls.fasta.parse_alleles.toggled, object.properties.is_phased
        )
        self.binder.bind(
            object.properties.subset_separator, self._update_fasta_parse_pattern
        )
        self.binder.bind(
            object.properties.parse_subset, self._update_fasta_parse_pattern
        )
        self.binder.bind(object.properties.is_phased, self._update_fasta_parse_pattern)
        self.binder.bind(
            object.properties.info,
            self.controls.fasta.file_size.setText,
            lambda info: human_readable_size(info.size),
        )

        self.controls.fasta.file_format.setText(object.info.format.label)

        self.controls.config.setCurrentWidget(self.controls.fasta.widget)
        self.controls.config.setVisible(True)

    def _bind_none(self, object):
        self.controls.config.setVisible(False)

    def _populate_headers(self, headers):
        self.controls.tabfile.index_combo.clear()
        self.controls.tabfile.sequence_combo.clear()
        self.controls.tabfile.allele_combo.clear()

        if self.is_phasing_optional:
            self.controls.tabfile.allele_combo.addItem("---")

        for header in headers:
            self.controls.tabfile.index_combo.addItem(header)
            self.controls.tabfile.sequence_combo.addItem(header)
            self.controls.tabfile.allele_combo.addItem(header)

    def set_is_phasing_optional(self, value):
        self.is_phasing_optional = value

    def _update_fasta_parse_pattern(self, *args, **kwargs):
        pattern = "individual"
        if self.object.is_phased:
            pattern += "_allele"
        if self.object.parse_subset:
            separator = self.object.subset_separator or "/"
            pattern += separator + "organism"
        text = f'Parse identifiers as "{pattern}"'
        self.controls.fasta.parse_pattern.setText(text)


class GraphicTitleCard(Card):
    def __init__(self, title, description, pixmap, parent=None):
        super().__init__(parent)

        label_title = QtWidgets.QLabel(title)
        font = label_title.font()
        font.setPixelSize(18)
        font.setBold(True)
        font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1)
        label_title.setFont(font)

        label_description = QtWidgets.QLabel(description)
        label_description.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        label_description.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        label_description.setWordWrap(True)

        label_pixmap = QtWidgets.QLabel()
        label_pixmap.setPixmap(pixmap)
        label_pixmap.setFixedSize(pixmap.size())

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setContentsMargins(0, 6, 0, 4)
        text_layout.addWidget(label_title)
        text_layout.addWidget(label_description, 1)
        text_layout.setSpacing(8)

        pixmap_layout = QtWidgets.QVBoxLayout()
        pixmap_layout.setContentsMargins(0, 8, 0, 4)
        pixmap_layout.addWidget(label_pixmap)
        pixmap_layout.addStretch(1)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(16)
        layout.addLayout(pixmap_layout)
        layout.addLayout(text_layout, 1)
        layout.addSpacing(100)

        self.addLayout(layout)

        self.controls.title = label_title
        self.controls.description = label_description
        self.controls.pixmap = label_pixmap

    def setTitle(self, text):
        self.controls.title.setText(text)

    def setBusy(self, busy: bool):
        self.setEnabled(not busy)
