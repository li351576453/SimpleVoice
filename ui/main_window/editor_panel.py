from PyQt6.QtWidgets import QWidget, QScrollArea, QGridLayout
from PyQt6.QtCore import Qt

from core.constants import PIANO_WIDTH, TIMELINE_HEIGHT
from ui.main_window.piano_keys import PianoKeys
from ui.main_window.timeline import Timeline
from ui.main_window.edit_grid import EditGrid


class EditorPanel(QWidget):
    """把 钢琴键 + 时间轴 + 编辑网格 拼成标准 DAW 布局，
    并处理三个区域的滚动联动。"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # ---- 组件 ----
        self.piano = PianoKeys()
        self.timeline = Timeline()
        self.grid = EditGrid()

        self.corner = QWidget()
        self.corner.setFixedSize(PIANO_WIDTH, TIMELINE_HEIGHT)
        self.corner.setStyleSheet("background: #2a2a35;")

        # ---- 滚动区 ----
        self.timeline_scroll = QScrollArea()
        self.timeline_scroll.setWidget(self.timeline)
        self.timeline_scroll.setWidgetResizable(False)
        self.timeline_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.timeline_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.timeline_scroll.setFixedHeight(TIMELINE_HEIGHT)

        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidget(self.grid)
        self.grid_scroll.setWidgetResizable(False)

        # ---- 布局 ----
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.corner,          0, 0)
        layout.addWidget(self.timeline_scroll, 0, 1)
        layout.addWidget(self.piano,           1, 0)
        layout.addWidget(self.grid_scroll,     1, 1)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(1, 1)

        # ---- 联动 ----
        self._connect_scroll()

    def _connect_scroll(self):
        grid_h = self.grid_scroll.horizontalScrollBar()
        grid_v = self.grid_scroll.verticalScrollBar()

        grid_h.valueChanged.connect(self.timeline_scroll.horizontalScrollBar().setValue)
        grid_v.valueChanged.connect(self.piano.set_scroll_offset)

        self.piano.set_scroll_offset(grid_v.value())