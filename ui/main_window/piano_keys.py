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
    notePressed = pyqtSignal(int)
    noteReleased = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(PIANO_WIDTH)
        self.scroll_offset = 0
        self.key_height = KEY_HEIGHT
        self.pressed = set()

    def set_key_height(self, h: int):
        if h == self.key_height:
            return
        self.key_height = h
        self.update()

    def set_scroll_offset(self, offset: int):
        if offset != self.scroll_offset:
            self.scroll_offset = offset
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(30, 30, 40))

        h = self.height()
        kh = self.key_height
        first_visible_index = self.scroll_offset // kh
        last_visible_index = (self.scroll_offset + h) // kh + 1

        for i in range(first_visible_index, last_visible_index + 1):
            midi = TOP_MIDI - i
            if midi < 0 or midi >= TOTAL_MIDI:
                continue
            y = i * kh - self.scroll_offset
            rect = QRect(0, y, PIANO_WIDTH, kh)

            if is_black_key(midi):
                base = QColor(40, 40, 50)
                pressed_color = QColor(70, 140, 210)
                text_color = QColor(180, 180, 190)
            else:
                base = QColor(240, 240, 245)
                pressed_color = QColor(120, 200, 255)
                text_color = QColor(70, 70, 80)

            color = pressed_color if midi in self.pressed else base
            p.fillRect(rect, color)
            p.setPen(QColor(80, 80, 90))
            p.drawRect(rect)

            p.setPen(text_color)
            p.drawText(6, y + kh - 6, note_name(midi))

    def _hit_test(self, y_local: int) -> int:
        y_global = y_local + self.scroll_offset
        i = y_global // self.key_height
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