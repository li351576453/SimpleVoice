from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSpinBox, QLabel, QComboBox
)


class TransportBar(QWidget):
    def __init__(self, transport, parent=None):
        super().__init__(parent)
        self.transport = transport

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        self.btn_play = QPushButton("▶")
        self.btn_play.setFixedWidth(40)
        self.btn_play.clicked.connect(self.transport.toggle)
        layout.addWidget(self.btn_play)

        layout.addWidget(QLabel("BPM:"))
        self.bpm_spin = QSpinBox()
        self.bpm_spin.setRange(20, 400)
        self.bpm_spin.setValue(self.transport.bpm)
        self.bpm_spin.valueChanged.connect(self.transport.set_bpm)
        layout.addWidget(self.bpm_spin)

        layout.addWidget(QLabel("PPQ:"))
        self.ppq_spin = QSpinBox()
        self.ppq_spin.setRange(1, 16)
        self.ppq_spin.setValue(self.transport.ppq)
        self.ppq_spin.valueChanged.connect(self.transport.set_ppq)
        layout.addWidget(self.ppq_spin)

        layout.addWidget(QLabel("拍号:"))
        self.num_spin = QSpinBox()
        self.num_spin.setRange(1, 16)
        self.num_spin.setValue(self.transport.time_sig_num)
        layout.addWidget(self.num_spin)

        layout.addWidget(QLabel("/"))

        self.den_combo = QComboBox()
        self.den_combo.addItems(["1", "2", "4", "8", "16"])
        self.den_combo.setCurrentText(str(self.transport.time_sig_den))
        layout.addWidget(self.den_combo)

        self.num_spin.valueChanged.connect(self._on_time_sig)
        self.den_combo.currentTextChanged.connect(self._on_time_sig)

        layout.addStretch()

        self.transport.started.connect(lambda: self.btn_play.setText("⏸"))
        self.transport.stopped.connect(lambda: self.btn_play.setText("▶"))

    def _on_time_sig(self):
        num = self.num_spin.value()
        den = int(self.den_combo.currentText())
        self.transport.set_time_signature(num, den)