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

from PySide6 import QtCore

from itaxotools.common.bindings import Binder
from itaxotools.taxi_gui.app.model import items
from itaxotools.taxi_gui.model.common import Object, Property
from itaxotools.taxi_gui.model.input_file import InputFileModel
from itaxotools.taxi_gui.types import FileInfo


class PhasedResultsModel(Object):

    info = Property(FileInfo, None)
    model = Property(InputFileModel, None)
    index = Property(QtCore.QModelIndex, None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.binder = Binder()
        self.binder.bind(self.properties.info, self.update_model)

    def update_model(self, info: FileInfo):
        if info is None:
            self.model = None
            self.index = None
            return
        model = InputFileModel(info)
        model.name = 'Previously phased sequences'
        self.model = model
        self.index = items.add_sequence(model)
