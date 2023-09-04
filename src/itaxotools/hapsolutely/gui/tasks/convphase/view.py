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

from PySide6 import QtWidgets

from itaxotools.common.utility import AttrDict
from itaxotools.convphase_gui.task.view import (
    InputSequencesSelector, OutputFormatCard, ParameterCard, ResultViewer)
from itaxotools.convphase_gui.task.view import View as _View
from itaxotools.taxi_gui.tasks.common.view import ProgressCard

from ..common.view import GraphicTitleCard
from . import long_description, pixmap_medium, title


class View(_View):

    def draw(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.results = ResultViewer('Phased sequences', self)
        self.cards.progress_matrix = ProgressCard(self)
        self.cards.progress_mcmc = ProgressCard(self)
        self.cards.input_sequences = InputSequencesSelector('Input sequences', self)
        self.cards.output_format = OutputFormatCard(self)
        self.cards.parameters = ParameterCard(self)

        layout = QtWidgets.QVBoxLayout()
        for card in self.cards:
            layout.addWidget(card)
        layout.addStretch(1)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)
        self.setLayout(layout)
