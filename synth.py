import numpy as np
import sounddevice as sd

SAMPLE_RATE = 48000
BLOCK_SIZE = 512


def midi_to_freq(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


class Synth:
    """最简单的正弦波合成器，支持同时按多个键"""

    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.active_notes = {}      # {midi: phase}
        self.stream = None
        self.master_volume = 0.3

    def start(self):
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            blocksize=BLOCK_SIZE,
            callback=self._callback,
        )
        self.stream.start()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def note_on(self, midi):
        self.active_notes[midi] = 0.0

    def note_off(self, midi):
        self.active_notes.pop(midi, None)

    def _callback(self, outdata, frames, time_info, status):
        outdata.fill(0)
        if not self.active_notes:
            return

        mono = outdata[:, 0]
        for midi, phase in list(self.active_notes.items()):
            freq = midi_to_freq(midi)
            step = freq / self.sample_rate
            phases = phase + step * np.arange(frames)
            wave = np.sin(2 * np.pi * phases).astype(np.float32)
            mono += wave
            self.active_notes[midi] = float(phases[-1] % 1.0)

        mono *= self.master_volume
        np.clip(mono, -1.0, 1.0, out=mono)