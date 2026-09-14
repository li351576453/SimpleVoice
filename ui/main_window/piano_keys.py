from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QColor

from core.constants import TOP_MIDI, KEY_HEIGHT, PIANO_WIDTH, TOTAL_MIDI


def is_black_key(midi: int) -> bool:
    return (midi % 12) in (1, 3, 6, 8, 10)


def note_name(midi: int) -> str:
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{names[midi % 12]}{midi // 12 - 1}"


class PianoKeys(QWidget):
    """左侧钢琴键侧栏。固定宽度，不自己滚动，
    由外部通过 set_scroll_offset 控制画哪些音。"""

    notePressed = pyqtSignal(int)
    noteReleased = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(PIANO_WIDTH)
        self.scroll_offset = 0
        self.pressed = set()

    def set_scroll_offset(self, offset: int):
        if offset != self.scroll_offset:
            self.scroll_offset = offset
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(30, 30, 40))

        h = self.height()
        first_visible_index = self.scroll_offset // KEY_HEIGHT
        last_visible_index = (self.scroll_offset + h) // KEY_HEIGHT + 1

        for i in range(first_visible_index, last_visible_index + 1):
            midi = TOP_MIDI - i
            if midi < 0 or midi >= TOTAL_MIDI:
                continue
            y = i * KEY_HEIGHT - self.scroll_offset
            rect = QRect(0, y, PIANO_WIDTH, KEY_HEIGHT)

            if is_black_key(midi):
                color = QColor(60, 130, 200) if midi in self.pressed else QColor(25, 25, 30)
                black_rect = QRect(PIANO_WIDTH // 2, y, PIANO_WIDTH // 2, KEY_HEIGHT - 2)
                p.fillRect(black_rect, color)
                p.setPen(QColor(0, 0, 0))
                p.drawRect(black_rect)
            else:
                color = QColor(120, 200, 255) if midi in self.pressed else QColor(240, 240, 245)
                p.fillRect(rect, color)
                p.setPen(QColor(80, 80, 90))
                p.drawRect(rect)

            if midi % 12 == 0:
                p.setPen(QColor(90, 90, 90))
                p.drawText(4, y + KEY_HEIGHT - 5, note_name(midi))

    def _hit_test(self, y_local: int) -> int:
        y_global = y_local + self.scroll_offset
        i = y_global // KEY_HEIGHT
        midi = TOP_MIDI - i
        if 0 <= midi < TOTAL_MIDI:
            return midi
        return -1

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            midi = self._hit_test(int(e.position().y()))
            if midi >= 0:
                self.pressed.add(midi)
                self.notePressed.emit(midi)
                self.update()

    def mouseReleaseEvent(self, e):
        for midi in list(self.pressed):
            self.noteReleased.emit(midi)
        self.pressed.clear()
        self.update()