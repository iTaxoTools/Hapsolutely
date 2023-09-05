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

from itaxotools.common.bindings import Binder, Instance, Property
from itaxotools.taxi_gui.app.model import items
from itaxotools.taxi_gui.model.common import Object
from itaxotools.taxi_gui.model.input_file import InputFileModel
from itaxotools.taxi_gui.types import FileInfo


class PhasedResultsModel(Object):

    info = Property(FileInfo, None)
    model = Property(InputFileModel, None)
    index = Property(QtCore.QModelIndex, Instance)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.binder = Binder()

    def update_results(self, info: FileInfo):
        if info is None:
            self.info = None
            self.model = None
            self.index = None
            return
        self.info = info
        model = InputFileModel(info)
        model.name = 'Previously phased sequences'
        self.model = model
        self.index = items.add_sequence(model)
