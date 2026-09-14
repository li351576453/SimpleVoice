from PyQt6.QtWidgets import QMainWindow, QToolBar, QWidget, QVBoxLayout
from PyQt6.QtGui import QAction

from ui.main_window.editor_panel import EditorPanel
from ui.main_window.transport_bar import TransportBar
from core.note_store import NoteStore
from core.transport import Transport
from synth import Synth


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SimpleVoice")
        self.resize(1200, 700)

        self.note_store = NoteStore()
        self.transport = Transport()

        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)
        toolbar.addAction(QAction("新建", self))
        toolbar.addAction(QAction("打开", self))
        toolbar.addAction(QAction("保存", self))

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.transport_bar = TransportBar(self.transport)
        root.addWidget(self.transport_bar)

        self.editor = EditorPanel(self.note_store, self.transport)
        root.addWidget(self.editor, stretch=1)

        self.synth = Synth()
        self.synth.start()

        self.editor.notePressed.connect(self.synth.note_on)
        self.editor.noteReleased.connect(self.synth.note_off)

        self.transport.positionChanged.connect(self._on_playhead)

    def _on_playhead(self, cell):
        active = self.note_store.active_at(cell)
        for midi in active:
            if midi not in self.synth.active_notes:
                self.synth.note_on(midi)
        for midi in list(self.synth.active_notes):
            if midi not in active:
                self.synth.note_off(midi)

    def closeEvent(self, event):
        self.transport.stop()
        self.synth.stop()
        event.accept()