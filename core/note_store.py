from PyQt6.QtCore import QObject, pyqtSignal
from core.notes import Note


class NoteStore(QObject):
    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.notes: list[Note] = []

    def add(self, note: Note):
        self.notes.append(note)
        self.changed.emit()

    def remove_at(self, midi: int, cell: int) -> bool:
        before = len(self.notes)
        self.notes = [
            n for n in self.notes
            if not (n.midi == midi and n.start <= cell < n.end())
        ]
        if len(self.notes) != before:
            self.changed.emit()
            return True
        return False

    def note_at(self, midi: int, cell: int):
        for n in self.notes:
            if n.midi == midi and n.start <= cell < n.end():
                return n
        return None

    def active_at(self, cell: int) -> set:
        """返回当前格正在响的所有 midi 集合"""
        return {n.midi for n in self.notes if n.start <= cell < n.end()}

    def set_notes(self, notes: list[Note]):
        """批量替换所有音符（用于加载工程）"""
        self.notes = notes
        self.changed.emit()