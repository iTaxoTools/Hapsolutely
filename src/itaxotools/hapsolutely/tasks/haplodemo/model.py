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
from itaxotools.haplodemo.types import HaploGraph, HaploTreeNode
from itaxotools.taxi_gui.loop import DataQuery
from itaxotools.taxi_gui.model.partition import PartitionModel
from itaxotools.taxi_gui.model.tasks import SubtaskModel, TaskModel
from itaxotools.taxi_gui.model.tree import TreeModel
from itaxotools.taxi_gui.tasks.common.model import ImportedInputModel
from itaxotools.taxi_gui.types import FileFormat, Notification
from itaxotools.taxi_gui.utility import human_readable_seconds

from itaxotools.hapsolutely.model.phased_sequence import PhasedSequenceModel

from ..common.model import (
    PhasedFileInfoSubtaskModel, PhasedInputModel, PhasedItemProxyModel)
from . import process, title
from .types import NetworkAlgorithm


class Model(TaskModel):
    task_name = title

    request_confirmation = QtCore.Signal(object, object, object)
    haplo_ready = QtCore.Signal()

    haplo_tree = Property(HaploTreeNode, None)
    haplo_graph = Property(HaploGraph, None)
    spartitions = Property(dict, None)
    spartition = Property(str, None)

    can_lock_distances = Property(bool, False)

    input_sequences = Property(PhasedInputModel, PhasedInputModel(PhasedSequenceModel, is_phasing_optional=True))
    input_species = Property(PhasedInputModel, PhasedInputModel(PartitionModel, 'species'))
    input_tree = Property(ImportedInputModel, ImportedInputModel(TreeModel))

    network_algorithm = Property(NetworkAlgorithm, NetworkAlgorithm.Fitchi)

    transversions_only = Property(bool, False)
    epsilon = Property(int, 0)

    input_is_phased = Property(bool, False)
    draw_haploweb = Property(bool, True)

    def __init__(self, name=None):
        super().__init__(name)
        self.can_open = True
        self.can_save = True

        self.input_tree.model.unselected = 'Generate from input sequences using Neighbour Joining'

        self.subtask_init = SubtaskModel(self, bind_busy=False)
        self.subtask_sequences = PhasedFileInfoSubtaskModel(self)
        self.subtask_species = PhasedFileInfoSubtaskModel(self)
        self.subtask_tree = PhasedFileInfoSubtaskModel(self)

        self.binder.bind(self.subtask_sequences.done, self.input_sequences.add_phased_info)
        self.binder.bind(self.subtask_species.done, self.input_species.add_info)
        self.binder.bind(self.subtask_tree.done, self.input_tree.add_info)

        self.binder.bind(self.input_sequences.notification, self.notification)
        self.binder.bind(self.input_species.notification, self.notification)
        self.binder.bind(self.input_tree.notification, self.notification)

        self.binder.bind(self.input_sequences.properties.index, self.propagate_input_index)
        self.binder.bind(self.input_sequences.updated, self.update_input_is_phased)

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
            input_tree=self.input_tree.as_dict(),

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

        item = self.input_sequences.model.data(index, PhasedItemProxyModel.ItemRole)
        if not item:
            self.perform_species = False
            self.perform_genera = False
            return

        info = item.object.info

        if info.format == FileFormat.Tabfile:
            if any((info.header_species, info.header_genus, info.header_organism)):
                self.input_species.set_index(index)
        elif info.format == FileFormat.Fasta:
            if info.has_subsets:
                self.input_species.set_index(index)

    def update_input_is_phased(self):
        if not self.input_sequences.object:
            self.input_is_phased = False
            return
        self.input_is_phased = self.input_sequences.object.is_phased

    def onDone(self, report):
        time_taken = human_readable_seconds(report.result.seconds_taken)
        self.notification.emit(Notification.Info(f'{self.name} completed successfully!\nTime taken: {time_taken}.'))

        self.haplo_tree = report.result.haplo_tree
        self.haplo_graph = report.result.haplo_graph
        self.spartitions = report.result.spartitions
        self.spartition = report.result.spartition

        self.can_lock_distances = bool(self.haplo_tree is not None)

        self.haplo_ready.emit()
        self.busy = False
        self.done = True

    def clear(self):
        self.haplo_tree = None
        self.haplo_graph = None
        self.spartitions = None
        self.spartition = None
        self.done = False

    def open(self, path: Path):
        self.clear()
        self.subtask_sequences.start(path)

    def save(self, path: Path):
        pass
