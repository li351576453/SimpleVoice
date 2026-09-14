# core/notes.py
from dataclasses import dataclass


@dataclass
class Note:
    midi: int          # 音高
    start: int         # 起始格（第几格）
    length: int        # 长度（占几格）

    def end(self) -> int:
        return self.start + self.length