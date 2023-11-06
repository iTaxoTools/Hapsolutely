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

from itaxotools.common.widgets import HLineSeparator

from itaxotools.hapsolutely.resources import icons


class CategoryFrame(QtWidgets.QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)

        label = QtWidgets.QLabel(text + ' : ')
        label.setStyleSheet('color: Palette(Dark); padding-left: 2px;')

        title = QtWidgets.QVBoxLayout()
        title.addWidget(label)
        title.addWidget(HLineSeparator(1))
        title.setContentsMargins(0, 0, 0, 0)
        title.setSpacing(1)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(title)
        layout.addSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._layout = layout

    def addWidget(self, widget):
        self._layout.addWidget(widget)

    def addLayout(self, layout):
        self._layout.addLayout(layout)

    def addSpacing(self, spacing):
        self._layout.addSpacing(spacing)


class SidebarArea(QtWidgets.QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.extent_metric = self.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent) + 1
        self.target_width = 100

    def setWidget(self, widget):
        super().setWidget(widget)
        self.target_width = widget.width()
        self.setFixedWidth(self.target_width)

    def event(self, event):
        if event.type() == QtCore.QEvent.Show:
            self.update_width()
        return super().event(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_width()

    def update_width(self):
        if self.verticalScrollBar().isVisible():
            self.widget().setFixedWidth(self.target_width - self.extent_metric)
        else:
            self.widget().setFixedWidth(self.target_width)

        self.update()


class SidePushButton(QtWidgets.QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("text-align: left; padding-left: 4px;")
        self.setIcon(icons.arrow.resource)
        self.setFixedHeight(24)


class SideToggleButton(QtWidgets.QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("text-align: left; padding-left: 4px;")
        self.clicked.connect(self.handle_clicked)
        self.setIcon(icons.arrow.resource)
        self.setFixedHeight(24)
        self.setCheckable(False)
        self.checked = False

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        palette = QtGui.QGuiApplication.palette()
        outline = palette.color(QtGui.QPalette.Text)
        painter.setPen(QtGui.QPen(outline, 1.0))

        rect = self.rect().adjusted(0, 6, -6, -6)
        rect.setLeft(rect.right() - 20)

        if self.isChecked():
            self.paint_checked(painter, palette, rect)
        else:
            self.paint_unchecked(painter, palette, rect)

        painter.end()

    def paint_checked(self, painter: QtGui.QPainter, palette: QtGui.QPalette, rect: QtCore.QRect):

        bg_rect = rect.adjusted(2, 2, -2, -2)
        radius = bg_rect.height() / 2
        bg_color = palette.color(QtGui.QPalette.Highlight)
        painter.setBrush(QtGui.QBrush(bg_color))
        painter.drawRoundedRect(bg_rect, radius, radius)

        fg_rect = rect.adjusted(2, 2, -2, -2)
        fg_rect.setLeft(fg_rect.right() - fg_rect.height())
        fg_color = palette.color(QtGui.QPalette.Light)
        painter.setBrush(QtGui.QBrush(fg_color))
        painter.drawEllipse(fg_rect)

    def paint_unchecked(self, painter: QtGui.QPainter, palette: QtGui.QPalette, rect: QtCore.QRect):
        bg_rect = rect.adjusted(2, 2, -2, -2)
        radius = bg_rect.height() / 2
        bg_color = palette.color(QtGui.QPalette.Mid)
        painter.setBrush(QtGui.QBrush(bg_color))
        painter.drawRoundedRect(bg_rect, radius, radius)

        fg_rect = rect.adjusted(2, 2, -2, -2)
        fg_rect.setRight(fg_rect.left() + fg_rect.height())
        fg_color = palette.color(QtGui.QPalette.Light)
        painter.setBrush(QtGui.QBrush(fg_color))
        painter.drawEllipse(fg_rect)

    def sizeHint(self):
        return super().sizeHint() + QtCore.QSize(32, 0)

    def setChecked(self, value):
        self.checked = value
        self.update()

    def isChecked(self):
        return self.checked

    def handle_clicked(self):
        self.checked = not self.checked
        self.toggled.emit(self.checked)
