from PyQt6.QtWidgets import QWidget, QScrollArea, QGridLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

from core.constants import PIANO_WIDTH, TIMELINE_HEIGHT
from ui.main_window.piano_keys import PianoKeys
from ui.main_window.timeline import Timeline
from ui.main_window.edit_grid import EditGrid


class EditorPanel(QWidget):
    notePressed = pyqtSignal(int)
    noteReleased = pyqtSignal(int)

    def __init__(self, note_store, transport, parent=None):
        super().__init__(parent)
        self.note_store = note_store
        self.transport = transport

        self.piano = PianoKeys()
        self.timeline = Timeline(transport)
        self.grid = EditGrid(note_store, transport)

        self.btn_reset = QPushButton("⟲")
        self.btn_reset.setFixedSize(PIANO_WIDTH, TIMELINE_HEIGHT)
        self.btn_reset.setToolTip("重置播放进度")
        self.btn_reset.clicked.connect(self._on_reset)

        self.timeline_scroll = QScrollArea()
        self.timeline_scroll.setWidget(self.timeline)
        self.timeline_scroll.setWidgetResizable(False)
        self.timeline_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.timeline_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.timeline_scroll.setFixedHeight(TIMELINE_HEIGHT)

        self.grid_scroll = QScrollArea()
        self.grid_scroll.setWidget(self.grid)
        self.grid_scroll.setWidgetResizable(False)

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.btn_reset,       0, 0)
        layout.addWidget(self.timeline_scroll, 0, 1)
        layout.addWidget(self.piano,           1, 0)
        layout.addWidget(self.grid_scroll,     1, 1)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(1, 1)

        self._connect_scroll()
        self.piano.notePressed.connect(self.notePressed.emit)
        self.piano.noteReleased.connect(self.noteReleased.emit)

        self.transport.positionChanged.connect(self.grid.set_playhead)
        self.timeline.seekRequested.connect(self.transport.set_position)

        self.grid.cellWidthChanged.connect(self.timeline.set_cell_width)
        self.grid.keyHeightChanged.connect(self._on_key_height_changed)

    def _on_reset(self):
        self.transport.set_position(0)

    def _on_key_height_changed(self, h):
        self.piano.set_key_height(h)
        self.grid_scroll.verticalScrollBar().setValue(0)
        self.piano.set_scroll_offset(0)

    def _connect_scroll(self):
        grid_h = self.grid_scroll.horizontalScrollBar()
        grid_v = self.grid_scroll.verticalScrollBar()

        grid_h.valueChanged.connect(self.timeline_scroll.horizontalScrollBar().setValue)
        grid_v.valueChanged.connect(self.piano.set_scroll_offset)

        self.piano.set_scroll_offset(grid_v.value())