from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor

from core.constants import CELL_WIDTH, NUM_CELLS, TIMELINE_HEIGHT


class Timeline(QWidget):
    seekRequested = pyqtSignal(int)

    def __init__(self, transport, parent=None):
        super().__init__(parent)
        self.transport = transport
        self.cell_width = CELL_WIDTH
        self.setFixedHeight(TIMELINE_HEIGHT)
        self.setFixedWidth(NUM_CELLS * self.cell_width)
        self._dragging = False

        transport.timeSignatureChanged.connect(lambda *_: self.update())
        transport.ppqChanged.connect(lambda *_: self.update())

    def set_cell_width(self, w: int):
        self.cell_width = w
        self.setFixedWidth(NUM_CELLS * w)
        self.update()

    def _x_to_cell(self, x: float) -> int:
        cell = int(x // self.cell_width)
        return max(0, min(NUM_CELLS - 1, cell))

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self.seekRequested.emit(self._x_to_cell(e.position().x()))

    def mouseMoveEvent(self, e):
        if self._dragging:
            self.seekRequested.emit(self._x_to_cell(e.position().x()))

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._dragging = False

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(event.rect(), QColor(45, 45, 55))

        bar_cells = self.transport.cells_per_bar()
        left = event.rect().left()
        right = event.rect().right()
        first = max(0, left // self.cell_width)
        last = min(NUM_CELLS, right // self.cell_width + 2)

        for i in range(first, last):
            x = i * self.cell_width
            if i % bar_cells == 0:
                p.setPen(QColor(200, 200, 200))
                p.drawLine(x, 0, x, TIMELINE_HEIGHT)
                p.drawText(x + 4, 18, str(i // bar_cells + 1))
            else:
                p.setPen(QColor(80, 80, 90))
                p.drawLine(x, TIMELINE_HEIGHT - 8, x, TIMELINE_HEIGHT)