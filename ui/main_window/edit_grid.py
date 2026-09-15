from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QKeySequence

from core.constants import (
    CELL_WIDTH, NUM_CELLS, KEY_HEIGHT, TOP_MIDI, TOTAL_MIDI,
    MIN_CELL_WIDTH, MAX_CELL_WIDTH, MIN_KEY_HEIGHT, MAX_KEY_HEIGHT,
)
from core.notes import Note
from ui.main_window.piano_keys import note_name


class EditGrid(QWidget):
    cellWidthChanged = pyqtSignal(int)
    keyHeightChanged = pyqtSignal(int)

    def __init__(self, note_store, transport, parent=None):
        super().__init__(parent)
        self.note_store = note_store
        self.transport = transport
        self.note_store.changed.connect(self.update)

        self.cell_width = CELL_WIDTH
        self.key_height = KEY_HEIGHT
        self._update_size()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.drag_mode = None
        self.drag_note = None
        self.drag_start_cell = 0
        self.drag_start_midi = 0

        self.selection_rect = None
        self.selected: list[Note] = []

        self.move_offset_cell = 0
        self.move_offset_midi = 0

        self.clipboard: list[Note] = []
        self.playhead_cell = None
        self.undo_stack: list[list[Note]] = []
        self.redo_stack: list[list[Note]] = []

        transport.timeSignatureChanged.connect(lambda *_: self.update())
        transport.ppqChanged.connect(lambda *_: self.update())

    def _update_size(self):
        self.setFixedWidth(NUM_CELLS * self.cell_width)
        self.setFixedHeight(TOTAL_MIDI * self.key_height)

    def set_cell_width(self, w: int):
        w = max(MIN_CELL_WIDTH, min(MAX_CELL_WIDTH, w))
        if w == self.cell_width:
            return
        self.cell_width = w
        self._update_size()
        self.cellWidthChanged.emit(w)
        self.update()

    def set_key_height(self, h: int):
        h = max(MIN_KEY_HEIGHT, min(MAX_KEY_HEIGHT, h))
        if h == self.key_height:
            return
        self.key_height = h
        self._update_size()
        self.keyHeightChanged.emit(h)
        self.update()

    def wheelEvent(self, e):
        mods = e.modifiers()
        delta = e.angleDelta().y()
        if mods & Qt.KeyboardModifier.ControlModifier:
            step = 4 if delta > 0 else -4
            self.set_cell_width(self.cell_width + step)
            e.accept()
        elif mods & Qt.KeyboardModifier.ShiftModifier:
            step = 2 if delta > 0 else -2
            self.set_key_height(self.key_height + step)
            e.accept()
        else:
            super().wheelEvent(e)

    def set_playhead(self, cell):
        self.playhead_cell = cell
        self.update()

    def _snapshot(self):
        return [Note(midi=n.midi, start=n.start, length=n.length)
                for n in self.note_store.notes]

    def _push_undo(self):
        self.undo_stack.append(self._snapshot())
        self.redo_stack.clear()
        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)

    def _restore(self, snapshot):
        self.note_store.notes = [
            Note(midi=n.midi, start=n.start, length=n.length)
            for n in snapshot
        ]
        self.selected.clear()
        self.note_store.changed.emit()
        self.update()

    def undo(self):
        if not self.undo_stack:
            return
        self.redo_stack.append(self._snapshot())
        self._restore(self.undo_stack.pop())

    def redo(self):
        if not self.redo_stack:
            return
        self.undo_stack.append(self._snapshot())
        self._restore(self.redo_stack.pop())

    def clear_selection(self):
        if self.selected or self.selection_rect:
            self.selected.clear()
            self.selection_rect = None
            self.update()

    def _pos_to_cell_midi(self, x, y):
        cell = int(x // self.cell_width)
        row = int(y // self.key_height)
        midi = TOP_MIDI - row
        return cell, midi

    def _midi_to_y(self, midi):
        return (TOP_MIDI - midi) * self.key_height

    def _note_at(self, midi, cell):
        for n in self.note_store.notes:
            if n.midi == midi and n.start <= cell < n.end():
                return n
        return None

    def _is_selected(self, note):
        return note in self.selected

    def mousePressEvent(self, e):
        cell, midi = self._pos_to_cell_midi(e.position().x(), e.position().y())
        if not (0 <= midi < TOTAL_MIDI and 0 <= cell < NUM_CELLS):
            return

        if e.button() == Qt.MouseButton.RightButton:
            self.drag_mode = "select"
            self.selection_rect = (e.position().x(), e.position().y(),
                                   e.position().x(), e.position().y())
            self.selected.clear()
            self.update()
            return

        if e.button() == Qt.MouseButton.LeftButton:
            hit = self._note_at(midi, cell)

            if hit and self._is_selected(hit):
                self.drag_mode = "move"
                self.drag_start_cell = cell
                self.drag_start_midi = midi
                self.move_offset_cell = 0
                self.move_offset_midi = 0
                return

            if hit:
                self._push_undo()
                self.note_store.remove_at(midi, cell)
                return

            self.clear_selection()
            self._push_undo()
            note = Note(midi=midi, start=cell, length=1)
            self.note_store.notes.append(note)
            self.note_store.changed.emit()
            self.drag_mode = "create"
            self.drag_note = note
            self.drag_start_cell = cell
            self.drag_start_midi = midi

    def mouseMoveEvent(self, e):
        x, y = e.position().x(), e.position().y()

        if self.drag_mode == "create" and self.drag_note:
            cur_cell, _ = self._pos_to_cell_midi(x, y)
            length = max(1, cur_cell - self.drag_start_cell + 1)
            if length != self.drag_note.length:
                self.drag_note.length = length
                self.note_store.changed.emit()

        elif self.drag_mode == "select":
            x1, y1, _, _ = self.selection_rect
            self.selection_rect = (x1, y1, x, y)
            self.update()

        elif self.drag_mode == "move":
            cur_cell, cur_midi = self._pos_to_cell_midi(x, y)
            self.move_offset_cell = cur_cell - self.drag_start_cell
            self.move_offset_midi = cur_midi - self.drag_start_midi
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.RightButton and self.drag_mode == "select":
            self._finish_selection()
            self.drag_mode = None
            self.selection_rect = None
            self.update()

        elif e.button() == Qt.MouseButton.LeftButton:
            if self.drag_mode == "move":
                self._apply_move()
            self.drag_mode = None
            self.drag_note = None
            self.update()

    def _finish_selection(self):
        if not self.selection_rect:
            return
        x1, y1, x2, y2 = self.selection_rect
        rx1, rx2 = sorted((x1, x2))
        ry1, ry2 = sorted((y1, y2))

        self.selected = []
        for n in self.note_store.notes:
            nx1 = n.start * self.cell_width
            nx2 = n.end() * self.cell_width
            ny1 = self._midi_to_y(n.midi)
            ny2 = ny1 + self.key_height
            if nx1 < rx2 and nx2 > rx1 and ny1 < ry2 and ny2 > ry1:
                self.selected.append(n)
        self.update()

    def _apply_move(self):
        if not self.selected:
            return
        dc = self.move_offset_cell
        dm = self.move_offset_midi
        if dc == 0 and dm == 0:
            return
        self._push_undo()
        for n in self.selected:
            n.start = max(0, min(NUM_CELLS - 1, n.start + dc))
            n.midi = max(0, min(TOTAL_MIDI - 1, n.midi + dm))
        self.note_store.changed.emit()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.clear_selection()
            return
        if e.matches(QKeySequence.StandardKey.Undo):
            self.undo()
            return
        if e.matches(QKeySequence.StandardKey.Redo):
            self.redo()
            return
        if e.matches(QKeySequence.StandardKey.Copy):
            self.clipboard = [
                Note(midi=n.midi, start=n.start, length=n.length)
                for n in self.selected
            ]
            return
        if e.matches(QKeySequence.StandardKey.Paste):
            self._paste()
            return
        if e.matches(QKeySequence.StandardKey.Delete) or e.key() == Qt.Key.Key_Backspace:
            if self.selected:
                self._push_undo()
                for n in self.selected:
                    if n in self.note_store.notes:
                        self.note_store.notes.remove(n)
                self.selected.clear()
                self.note_store.changed.emit()
            return
        super().keyPressEvent(e)

    def _paste(self):
        if not self.clipboard:
            return
        self._push_undo()
        base_cell = self.playhead_cell if self.playhead_cell is not None else 0
        min_start = min(n.start for n in self.clipboard)
        new_notes = []
        for n in self.clipboard:
            new_n = Note(
                midi=n.midi,
                start=base_cell + (n.start - min_start),
                length=n.length,
            )
            self.note_store.notes.append(new_n)
            new_notes.append(new_n)
        self.selected = new_notes
        self.note_store.changed.emit()
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        rect = event.rect()
        p.fillRect(rect, QColor(25, 25, 35))

        bar_cells = self.transport.cells_per_bar()
        beat_cells = self.transport.ppq

        first_row = max(0, rect.top() // self.key_height)
        last_row = min(TOTAL_MIDI, rect.bottom() // self.key_height + 2)
        for i in range(first_row, last_row):
            y = i * self.key_height
            midi = TOP_MIDI - i
            if midi % 12 == 0:
                p.setPen(QColor(90, 90, 110))
            else:
                p.setPen(QColor(45, 45, 55))
            p.drawLine(rect.left(), y, rect.right(), y)

        first_col = max(0, rect.left() // self.cell_width)
        last_col = min(NUM_CELLS, rect.right() // self.cell_width + 2)
        for i in range(first_col, last_col):
            x = i * self.cell_width
            if i % bar_cells == 0:
                p.setPen(QColor(120, 120, 150))
            elif i % beat_cells == 0:
                p.setPen(QColor(70, 70, 90))
            else:
                p.setPen(QColor(45, 45, 55))
            p.drawLine(x, rect.top(), x, rect.bottom())

        for n in self.note_store.notes:
            x = n.start * self.cell_width
            y = self._midi_to_y(n.midi)
            w = n.length * self.cell_width
            h = self.key_height

            if self.drag_mode == "move" and self._is_selected(n):
                x += self.move_offset_cell * self.cell_width
                y -= self.move_offset_midi * self.key_height

            if x + w < rect.left() or x > rect.right():
                continue
            if y + h < rect.top() or y > rect.bottom():
                continue

            is_sel = self._is_selected(n)
            fill = QColor(255, 180, 80) if is_sel else QColor(90, 180, 255)
            border = QColor(200, 130, 30) if is_sel else QColor(40, 100, 170)

            p.fillRect(x + 1, y + 1, w - 2, h - 2, fill)
            p.setPen(border)
            p.drawRect(x + 1, y + 1, w - 2, h - 2)

            if w >= 24:
                p.setPen(QColor(20, 20, 30))
                p.drawText(int(x) + 4, int(y) + int(h / 2) + 4, note_name(n.midi))

        if self.selection_rect:
            x1, y1, x2, y2 = self.selection_rect
            rx = int(min(x1, x2))
            ry = int(min(y1, y2))
            rw = int(abs(x2 - x1))
            rh = int(abs(y2 - y1))
            p.setPen(QPen(QColor(120, 220, 120), 1, Qt.PenStyle.DashLine))
            p.setBrush(QColor(120, 220, 120, 40))
            p.drawRect(rx, ry, rw, rh)
            p.setBrush(Qt.BrushStyle.NoBrush)

        if self.playhead_cell is not None:
            x = self.playhead_cell * self.cell_width
            p.setPen(QPen(QColor(255, 80, 80), 2))
            p.drawLine(int(x), rect.top(), int(x), rect.bottom())