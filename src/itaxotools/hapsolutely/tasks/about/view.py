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
from itaxotools.common.widgets import VLineSeparator
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.tasks import ScrollTaskView

from itaxotools.hapsolutely import resources

from . import homepage_url, itaxotools_url, pixmap_medium, title


class HtmlLabel(QtWidgets.QLabel):
    def __init__(self, text):
        super().__init__(text)

        self.setTextFormat(QtCore.Qt.RichText)
        self.setOpenExternalLinks(True)
        self.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByMouse |
            QtCore.Qt.LinksAccessibleByMouse)
        self.setWordWrap(True)

        # fix italics kerning
        font = self.font()
        font.setHintingPreference(QtGui.QFont.HintingPreference.PreferNoHinting)
        self.setFont(font)


class AboutTitleCard(Card):
    def __init__(self, title, description, pixmap, parent=None):
        super().__init__(parent)

        label_title = QtWidgets.QLabel(title)
        font = label_title.font()
        font.setPixelSize(18)
        font.setBold(True)
        font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1)
        label_title.setFont(font)

        label_description = HtmlLabel(description)

        separator = VLineSeparator(1)

        homepage = QtWidgets.QPushButton('Homepage')
        itaxotools = QtWidgets.QPushButton('iTaxoTools')

        label_pixmap = QtWidgets.QLabel()
        label_pixmap.setPixmap(pixmap)
        label_pixmap.setFixedSize(pixmap.size())

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setContentsMargins(0, 10, 0, 8)
        text_layout.addWidget(label_title)
        text_layout.addWidget(label_description, 1)
        text_layout.setSpacing(8)

        pixmap_layout = QtWidgets.QVBoxLayout()
        pixmap_layout.setContentsMargins(0, 8, 0, 4)
        pixmap_layout.addWidget(label_pixmap)
        pixmap_layout.addStretch(1)

        buttons = QtWidgets.QVBoxLayout()
        buttons.setContentsMargins(0, 10, 0, 4)
        buttons.setSpacing(8)
        buttons.addWidget(homepage)
        buttons.addWidget(itaxotools)
        buttons.addStretch(1)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.addLayout(pixmap_layout)
        layout.addLayout(text_layout, 1)
        layout.addWidget(separator, 0)
        layout.addLayout(buttons)

        self.addLayout(layout)

        homepage.clicked.connect(self.openHomepage)
        itaxotools.clicked.connect(self.openItaxotools)

        self.controls.title = label_title
        self.controls.description = label_description
        self.controls.pixmap = label_pixmap

    def openHomepage(self):
        QtGui.QDesktopServices.openUrl(homepage_url)

    def openItaxotools(self):
        QtGui.QDesktopServices.openUrl(itaxotools_url)


class DocumentCard(Card):
    def __init__(self, title, description, parent=None):
        super().__init__(parent)

        label_title = QtWidgets.QLabel(title)
        font = label_title.font()
        font.setPixelSize(16)
        font.setBold(True)
        font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1)
        label_title.setFont(font)

        label_description = HtmlLabel(description)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(8, 12, 100, 12)
        layout.addWidget(label_title)
        layout.addWidget(label_description)
        layout.setSpacing(16)
        self.addLayout(layout)


class View(ScrollTaskView):

    def __init__(self, parent):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = AboutTitleCard(
            title,
            resources.documents.about.resource,
            pixmap_medium.resource,
            self)
        self.cards.phase = DocumentCard(
            'Sequence phasing',
            resources.documents.phase.resource,
            self)
        self.cards.nets = DocumentCard(
            'Network visualization',
            resources.documents.nets.resource,
            self)

        layout = QtWidgets.QVBoxLayout()
        for card in self.cards:
            layout.addWidget(card)
        layout.addStretch(1)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        self.setLayout(layout)
