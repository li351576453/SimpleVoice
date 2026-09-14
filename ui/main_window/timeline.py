from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor

from core.constants import CELL_WIDTH, NUM_CELLS, TIMELINE_HEIGHT, BEATS_PER_BAR


class Timeline(QWidget):
    """顶部时间轴。宽度 = 总格数 × 格宽，被 QScrollArea 包裹，
    横向滚动条与主编辑区同步。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(TIMELINE_HEIGHT)
        self.setFixedWidth(NUM_CELLS * CELL_WIDTH)

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(event.rect(), QColor(45, 45, 55))

        left = event.rect().left()
        right = event.rect().right()
        first = max(0, left // CELL_WIDTH)
        last = min(NUM_CELLS, right // CELL_WIDTH + 2)

        for i in range(first, last):
            x = i * CELL_WIDTH
            if i % BEATS_PER_BAR == 0:
                p.setPen(QColor(200, 200, 200))
                p.drawLine(x, 0, x, TIMELINE_HEIGHT)
                p.drawText(x + 4, 18, str(i // BEATS_PER_BAR + 1))
            else:
                p.setPen(QColor(80, 80, 90))
                p.drawLine(x, TIMELINE_HEIGHT - 8, x, TIMELINE_HEIGHT)