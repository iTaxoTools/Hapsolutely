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

from __future__ import annotations

from PySide6 import QtCore

from typing import Type

from itaxotools.common.bindings import Binder, Property
from itaxotools.common.utility import AttrDict, override
from itaxotools.taxi_gui import app as global_app
from itaxotools.taxi_gui.model.common import ItemModel, Object
from itaxotools.taxi_gui.model.input_file import InputFileModel
from itaxotools.taxi_gui.tasks.common.model import DataFileProtocol
from itaxotools.taxi_gui.types import FileFormat, FileInfo, Notification

from itaxotools.hapsolutely.gui import app


class PhasedItemProxyModel(QtCore.QAbstractProxyModel):
    ItemRole = ItemModel.ItemRole

    def __init__(self, model=None, root=None):
        super().__init__()
        self.unselected = '---'
        self.root = None

        self.phased_index = QtCore.QModelIndex()
        self.phased_model = None
        self.extra_rows = 1

        self.binder = Binder()
        self.binder.bind(app.phased_results.properties.index, self.update_phased_results)

        if model and root:
            self.setSourceModel(model, root)

    def update_phased_results(self, index: QtCore.QModelIndex):
        self.phased_model = app.phased_results.model
        if index.isValid() and not self.phased_index.isValid():
            self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
            self.phased_index = index
            self.extra_rows = 2
            self.endInsertRows()
        if not index.isValid() and self.phased_index.isValid():
            self.beginRemoveRows(QtCore.QModelIndex(), 0, 0)
            self.phased_index = index
            self.extra_rows = 1
            self.endRemoveRows()

    def sourceDataChanged(self, topLeft, bottomRight):
        self.dataChanged.emit(self.mapFromSource(topLeft), self.mapFromSource(bottomRight))

    def add_file(self, file: InputFileModel):
        index = self.source.add_file(file, focus=False)
        return self.mapFromSource(index)

    @override
    def setSourceModel(self, model, root):
        super().setSourceModel(model)
        self.root = root
        self.source = model
        model.dataChanged.connect(self.sourceDataChanged)

    @override
    def mapFromSource(self, sourceIndex):
        item = sourceIndex.internalPointer()
        if sourceIndex == self.phased_index:
            return self.createIndex(0, 0, item)
        if not item or item.parent != self.root:
            return QtCore.QModelIndex()
        return self.createIndex(item.row + self.extra_rows, 0, item)

    @override
    def mapToSource(self, proxyIndex):
        if not proxyIndex.isValid():
            return QtCore.QModelIndex()
        true_row = proxyIndex.row() - self.extra_rows
        if true_row == -1:
            return QtCore.QModelIndex()
        if true_row == -2:
            return self.phased_index
        item = proxyIndex.internalPointer()
        source = self.sourceModel()
        return source.createIndex(item.row, 0, item)

    @override
    def index(self, row: int, column: int, parent=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        if parent.isValid() or column != 0:
            return QtCore.QModelIndex()
        if row < 0 or row > len(self.root.children) + self.extra_rows - 1:
            return QtCore.QModelIndex()
        true_row = row - self.extra_rows
        if true_row == -1:
            return self.createIndex(row, 0)
        if true_row == -2:
            item = self.phased_index.internalPointer()
            return self.createIndex(row, 0, item)
        return self.createIndex(row, 0, self.root.children[true_row])

    @override
    def parent(self, index=QtCore.QModelIndex()) -> QtCore.QModelIndex:
        return QtCore.QModelIndex()

    @override
    def rowCount(self, parent=QtCore.QModelIndex()) -> int:
        return len(self.root.children) + self.extra_rows

    @override
    def columnCount(self, parent=QtCore.QModelIndex()) -> int:
        return 1

    @override
    def data(self, index: QtCore.QModelIndex, role: QtCore.Qt.ItemDataRole):
        if not index.isValid():
            return None
        true_row = index.row() - self.extra_rows
        if true_row == -1:
            if role == QtCore.Qt.DisplayRole:
                return self.unselected
            return None
        return super().data(index, role)

    @override
    def flags(self, index: QtCore.QModelIndex):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        true_row = index.row() - self.extra_rows
        if true_row == -1 or true_row == -2:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        return super().flags(index)


class PhasedInputModel(Object):
    notification = QtCore.Signal(Notification)
    updated = QtCore.Signal()

    model = Property(QtCore.QAbstractItemModel, None)
    index = Property(QtCore.QModelIndex, None)
    object = Property(DataFileProtocol, None)
    format = Property(FileFormat, None)

    def __init__(self, cast_type: Type[DataFileProtocol], *cast_args, **cast_kwargs):
        super().__init__()
        self.cast_type = cast_type
        self.cast_args = cast_args
        self.cast_kwargs = cast_kwargs

        item_model = global_app.model.items
        self.model = PhasedItemProxyModel(item_model, item_model.files)
        self.binder = Binder()

    def add_info(self, info: FileInfo):
        index = self.model.add_file(InputFileModel(info))
        self.set_index(index)

    def set_index(self, index: QtCore.QModelIndex):
        if index == self.index:
            return
        try:
            object = self._cast_from_index(index)
        except Exception:
            self.notification.emit(Notification.Warn('Unexpected file format.'))
            self.properties.index.update()
            self.properties.object.update()
            self.properties.format.update()
            return

        self.index = index
        self._set_object(object)

    def _set_object(self, object: DataFileProtocol):
        if object == self.object:
            return
        self.format = object.info.format if object else None
        self.binder.unbind_all()
        if object:
            for property in object.properties:
                self.binder.bind(property, self.updated)
        self.object = object
        self.updated.emit()

    def _cast_from_index(self, index: QtCore.QModelIndex) -> DataFileProtocol | None:
        if not index:
            return
        item = self.model.data(index, PhasedItemProxyModel.ItemRole)
        if not item:
            return None
        info = item.object.info
        return self.cast_type.from_file_info(
            info, *self.cast_args, **self.cast_kwargs)

    def is_valid(self) -> bool:
        if self.object:
            return self.object.is_valid()
        return False

    def as_dict(self) -> AttrDict | None:
        if self.object:
            return self.object.as_dict()
        return None
