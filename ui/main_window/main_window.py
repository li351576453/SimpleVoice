from PyQt6.QtWidgets import QMainWindow, QToolBar
from PyQt6.QtGui import QAction

from ui.main_window.editor_panel import EditorPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SimpleVoice")
        self.resize(1200, 700)

        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)
        toolbar.addAction(QAction("新建", self))
        toolbar.addAction(QAction("打开", self))
        toolbar.addAction(QAction("保存", self))
        toolbar.addSeparator()
        toolbar.addAction(QAction("播放", self))

        self.editor = EditorPanel()
        self.setCentralWidget(self.editor)