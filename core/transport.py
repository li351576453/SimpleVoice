from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from core.constants import NUM_CELLS, DEFAULT_PPQ


class Transport(QObject):
    positionChanged = pyqtSignal(int)
    started = pyqtSignal()
    stopped = pyqtSignal()
    timeSignatureChanged = pyqtSignal(int, int)
    ppqChanged = pyqtSignal(int)
    bpmChanged = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.bpm = 120
        self.ppq = DEFAULT_PPQ
        self.time_sig_num = 4
        self.time_sig_den = 4
        self.current_cell = 0
        self.playing = False

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)

    # ---------- 设置 ----------
    def set_bpm(self, bpm: int):
        bpm = max(20, min(400, bpm))
        if bpm == self.bpm:
            return
        self.bpm = bpm
        if self.playing:
            self._restart_timer()
        self.bpmChanged.emit(bpm)

    def set_ppq(self, ppq: int):
        ppq = max(1, min(16, ppq))
        if ppq == self.ppq:
            return
        self.ppq = ppq
        if self.playing:
            self._restart_timer()
        self.ppqChanged.emit(ppq)

    def set_time_signature(self, num: int, den: int):
        num = max(1, min(16, num))
        den = max(1, min(16, den))
        self.time_sig_num = num
        self.time_sig_den = den
        self.timeSignatureChanged.emit(num, den)

    # ---------- 派生量 ----------
    def cells_per_bar(self) -> int:
        """一小节多少格"""
        return int(self.time_sig_num * 4 / self.time_sig_den * self.ppq)

    def cell_duration_sec(self) -> float:
        """一格时长（秒）"""
        return 60.0 / self.bpm / self.ppq

    # ---------- 播放控制 ----------
    def start(self):
        if self.playing:
            return
        self.playing = True
        self._restart_timer()
        self.started.emit()
        self.positionChanged.emit(self.current_cell)

    def stop(self):
        if not self.playing:
            return
        self.playing = False
        self.timer.stop()
        self.stopped.emit()

    def toggle(self):
        if self.playing:
            self.stop()
        else:
            self.start()

    def set_position(self, cell: int):
        self.current_cell = max(0, min(NUM_CELLS - 1, cell))
        self.positionChanged.emit(self.current_cell)

    def _restart_timer(self):
        interval_ms = max(5, int(self.cell_duration_sec() * 1000))
        self.timer.start(interval_ms)

    def _tick(self):
        self.current_cell += 1
        if self.current_cell >= NUM_CELLS:
            self.current_cell = 0
        self.positionChanged.emit(self.current_cell)