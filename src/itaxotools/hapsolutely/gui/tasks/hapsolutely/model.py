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

from datetime import datetime
from pathlib import Path

from itaxotools.common.bindings import Property
from itaxotools.haplodemo.types import HaploGraph, HaploNode
from itaxotools.taxi_gui.loop import DataQuery
from itaxotools.taxi_gui.model.partition import PartitionModel
from itaxotools.taxi_gui.model.sequence import SequenceModel
from itaxotools.taxi_gui.model.tasks import SubtaskModel, TaskModel
from itaxotools.taxi_gui.tasks.common.model import (
    FileInfoSubtaskModel, ImportedInputModel, ItemProxyModel)
from itaxotools.taxi_gui.types import FileFormat, Notification
from itaxotools.taxi_gui.utility import human_readable_seconds

from . import process
from .types import NetworkAlgorithm


class Model(TaskModel):
    task_name = 'Hapsolutely'

    request_confirmation = QtCore.Signal(object, object, object)

    haplo_tree = Property(HaploNode, None)
    haplo_net = Property(HaploGraph, None)

    input_sequences = Property(ImportedInputModel, ImportedInputModel(SequenceModel))
    input_species = Property(ImportedInputModel, ImportedInputModel(PartitionModel, 'species'))

    network_algorithm = Property(NetworkAlgorithm, NetworkAlgorithm.Fitchi)

    transversions_only = Property(bool, False)
    epsilon = Property(int, 0)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = True

        self.subtask_init = SubtaskModel(self, bind_busy=False)
        self.subtask_sequences = FileInfoSubtaskModel(self)
        self.subtask_species = FileInfoSubtaskModel(self)

        self.binder.bind(self.subtask_sequences.done, self.input_sequences.add_info)
        self.binder.bind(self.subtask_species.done, self.input_species.add_info)

        self.binder.bind(self.input_sequences.notification, self.notification)
        self.binder.bind(self.input_species.notification, self.notification)

        self.binder.bind(self.input_sequences.properties.index, self.propagate_input_index)

        self.binder.bind(self.query, self.on_query)

        for handle in [
            self.properties.busy_subtask,
            self.input_sequences.updated,
            self.input_species.updated,
        ]:
            self.binder.bind(handle, self.checkReady)

        self.subtask_init.start(process.initialize)

    def isReady(self):
        if self.busy_subtask:
            return False
        if not self.input_sequences.is_valid():
            return False
        if not self.input_species.is_valid():
            return False
        return True

    def start(self):
        super().start()
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        work_dir = self.temporary_path / timestamp
        work_dir.mkdir()

        self.exec(
            process.execute,
            work_dir=work_dir,

            input_sequences=self.input_sequences.as_dict(),
            input_species=self.input_species.as_dict(),

            network_algorithm=self.network_algorithm,
            transversions_only=self.transversions_only,
            epsilon=self.epsilon,
        )

    def on_query(self, query: DataQuery):
        warns = query.data
        if not warns:
            self.answer(True)
        else:
            self.request_confirmation.emit(
                warns,
                lambda: self.answer(True),
                lambda: self.answer(False),
            )

    def propagate_input_index(self, index):
        if not index:
            return
        if not index.isValid():
            return

        item = self.input_sequences.model.data(index, ItemProxyModel.ItemRole)
        if not item:
            self.perform_species = False
            self.perform_genera = False
            return

        info = item.object.info

        if info.format in [FileFormat.Tabfile, FileFormat.Fasta]:
            self.input_species.set_index(index)

    def onDone(self, report):
        time_taken = human_readable_seconds(report.result.seconds_taken)
        self.notification.emit(Notification.Info(f'{self.name} completed successfully!\nTime taken: {time_taken}.'))
        self.dummy_time = report.result.seconds_taken
        self.haplo_tree = report.result.haplo_tree
        self.haplo_net = report.result.haplo_net
        self.properties.haplo_tree.update()
        self.properties.haplo_net.update()
        self.busy = False
        self.done = True

    def clear(self):
        self.haplo_tree = None
        self.dummy_time = None
        self.done = False

    def open(self, path: Path):
        self.clear()
        self.subtask_sequences.start(path)
