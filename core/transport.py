import time
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, Qt
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

        # 高精度时钟相关
        self._start_time = 0.0
        self._start_wall = 0.0
        self._start_cell = 0
        self._tick_count = 0
        self._tick_wall_start = 0.0

        self.timer = QTimer()
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self._tick)

    # ---------- 设置 ----------
    def set_bpm(self, bpm: int):
        bpm = max(20, min(400, bpm))
        if bpm == self.bpm:
            return
        self.bpm = bpm
        if self.playing:
            self._rebase()
        self.bpmChanged.emit(bpm)

    def set_ppq(self, ppq: int):
        ppq = max(1, min(16, ppq))
        if ppq == self.ppq:
            return
        self.ppq = ppq
        if self.playing:
            self._rebase()
        self.ppqChanged.emit(ppq)

    def set_time_signature(self, num: int, den: int):
        num = max(1, min(16, num))
        den = max(1, min(16, den))
        self.time_sig_num = num
        self.time_sig_den = den
        self.timeSignatureChanged.emit(num, den)

    # ---------- 派生量 ----------
    def cells_per_bar(self) -> int:
        return int(self.time_sig_num * 4 / self.time_sig_den * self.ppq)

    def cell_duration_sec(self) -> float:
        return 60.0 / self.bpm / self.ppq

    # ---------- 播放控制 ----------
    def start(self):
        if self.playing:
            return
        self.playing = True
        self._start_time = time.perf_counter()
        self._start_wall = time.time()
        self._start_cell = self.current_cell
        self._tick_count = 0
        self._tick_wall_start = time.perf_counter()
        self.timer.start(10)
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
        if self.playing:
            self._start_time = time.perf_counter()
            self._start_wall = time.time()
            self._start_cell = self.current_cell
        self.positionChanged.emit(self.current_cell)

    def _rebase(self):
        """BPM/PPQ 变化时，重设基准，避免跳格"""
        self._start_time = time.perf_counter()
        self._start_wall = time.time()
        self._start_cell = self.current_cell

    def _tick(self):
        if not self.playing:
            return

        elapsed = time.perf_counter() - self._start_time
        elapsed_wall = time.time() - self._start_wall

        cell_dur = self.cell_duration_sec()
        if cell_dur <= 0:
            return

        cell = self._start_cell + int(elapsed / cell_dur)
        if cell >= NUM_CELLS:
            cell %= NUM_CELLS

        if cell != self.current_cell:
            self.current_cell = cell
            self.positionChanged.emit(cell)

            # ---- 诊断打印：每 16 格一次 ----
            self._tick_count += 1
            if self._tick_count % 16 == 0:
                diff_ms = (elapsed - elapsed_wall) * 1000
                print(f"[{self._tick_count:4d}格] "
                      f"perf={elapsed:.3f}s  wall={elapsed_wall:.3f}s  "
                      f"diff={diff_ms:+.1f}ms  "
                      f"cell_dur={cell_dur*1000:.3f}ms")