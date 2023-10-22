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

from itaxotools.convphase_gui.task import process
from itaxotools.convphase_gui.task.model import Model as _Model
from itaxotools.taxi_gui.model.tasks import SubtaskModel, TaskModel

from itaxotools.hapsolutely import app

from ..common.model import PhasedFileInfoSubtaskModel
from . import title


class Model(_Model):
    task_name = title

    def __init__(self, name=None):
        TaskModel.__init__(self, name)
        self.can_open = True
        self.can_save = True

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        self.subtask_sequences = PhasedFileInfoSubtaskModel(self)
        self.binder.bind(self.subtask_sequences.done, self.input_sequences.add_info)

        self.binder.bind(self.input_sequences.properties.object, self.output_options.set_input_object)
        self.binder.bind(self.input_sequences.notification, self.notification)

        self.binder.bind(self.query, self.on_query)

        self.binder.bind(self.input_sequences.updated, self.checkReady)

        self.binder.bind(self.properties.phased_info, app.phased_results.update_results)

        self.checkReady()

        self.subtask_init.start(process.initialize)
