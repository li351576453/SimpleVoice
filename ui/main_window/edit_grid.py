from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor

from core.constants import (
    CELL_WIDTH, NUM_CELLS, KEY_HEIGHT, TOP_MIDI, TOTAL_MIDI, BEATS_PER_BAR
)


class EditGrid(QWidget):
    """中央编辑网格。宽度 = 总格数 × 格宽，高度 = 总半音数 × 键高。
    被 QScrollArea 包裹，横向 + 纵向都滚动。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(NUM_CELLS * CELL_WIDTH)
        self.setFixedHeight(TOTAL_MIDI * KEY_HEIGHT)

    def paintEvent(self, event):
        p = QPainter(self)
        rect = event.rect()
        p.fillRect(rect, QColor(25, 25, 35))

        # ---- 横线 ----
        first_row = max(0, rect.top() // KEY_HEIGHT)
        last_row = min(TOTAL_MIDI, rect.bottom() // KEY_HEIGHT + 2)
        for i in range(first_row, last_row):
            y = i * KEY_HEIGHT
            midi = TOP_MIDI - i
            if midi % 12 == 0:
                p.setPen(QColor(90, 90, 110))
            else:
                p.setPen(QColor(45, 45, 55))
            p.drawLine(rect.left(), y, rect.right(), y)

        # ---- 竖线 ----
        first_col = max(0, rect.left() // CELL_WIDTH)
        last_col = min(NUM_CELLS, rect.right() // CELL_WIDTH + 2)
        for i in range(first_col, last_col):
            x = i * CELL_WIDTH
            if i % BEATS_PER_BAR == 0:
                p.setPen(QColor(90, 90, 110))
            else:
                p.setPen(QColor(45, 45, 55))
            p.drawLine(x, rect.top(), x, rect.bottom())