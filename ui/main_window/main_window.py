from PyQt6.QtWidgets import QMainWindow, QToolBar, QWidget, QVBoxLayout
from PyQt6.QtGui import QAction

from ui.main_window.editor_panel import EditorPanel
from ui.main_window.transport_bar import TransportBar
from core.note_store import NoteStore
from core.transport import Transport
from synth import Synth
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from core import project_io


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SimpleVoice")
        self.resize(1200, 700)

        self.note_store = NoteStore()
        self.transport = Transport()

        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)
        act_new = QAction("新建", self)
        act_open = QAction("打开", self)
        act_save = QAction("保存", self)
        act_new.triggered.connect(self._on_new)
        act_open.triggered.connect(self._on_open)
        act_save.triggered.connect(self._on_save)
        toolbar.addAction(act_new)
        toolbar.addAction(act_open)
        toolbar.addAction(act_save)

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
        # 1. 停掉已经不在当前格响的音
        for midi in list(self.synth.active_notes):
            still_playing = any(
                n.midi == midi and n.start <= cell < n.end()
                for n in self.note_store.notes
            )
            if not still_playing:
                self.synth.note_off(midi)

        # 2. 触发从当前格开始的音符
        for n in self.note_store.notes:
            if n.start == cell:
                if n.midi in self.synth.active_notes:
                    self.synth.note_off(n.midi)
                self.synth.note_on(n.midi)

    def _on_new(self):
        self.transport.stop()
        self.note_store.set_notes([])
        self.transport.set_position(0)

    def _on_save(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "保存工程", "", "SimpleVoice 工程 (*.json)"
        )
        if not path:
            return
        if not path.endswith(".json"):
            path += ".json"
        try:
            project_io.save_project(path, self.note_store, self.transport)
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))

    def _on_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "打开工程", "", "SimpleVoice 工程 (*.json)"
        )
        if not path:
            return
        self.transport.stop()
        try:
            project_io.load_project(path, self.note_store, self.transport)
            self.transport.set_position(0)
        except Exception as e:
            QMessageBox.critical(self, "打开失败", str(e))

    def closeEvent(self, event):
        self.transport.stop()
        self.synth.stop()
        event.accept()