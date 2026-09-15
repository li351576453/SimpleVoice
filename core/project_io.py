import json

from core.notes import Note


FORMAT_NAME = "simplevoice"
FORMAT_VERSION = 1


def save_project(path: str, note_store, transport):
    data = {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "bpm": transport.bpm,
        "ppq": transport.ppq,
        "time_sig_num": transport.time_sig_num,
        "time_sig_den": transport.time_sig_den,
        "notes": [
            {"midi": n.midi, "start": n.start, "length": n.length}
            for n in note_store.notes
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_project(path: str, note_store, transport):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("format") != FORMAT_NAME:
        raise ValueError("不是 SimpleVoice 工程文件")

    # 先设 transport（会触发 UI 更新）
    transport.set_bpm(int(data.get("bpm", 120)))
    transport.set_ppq(int(data.get("ppq", 4)))
    transport.set_time_signature(
        int(data.get("time_sig_num", 4)),
        int(data.get("time_sig_den", 4)),
    )

    # 再设音符
    notes = [
        Note(midi=int(d["midi"]),
             start=int(d["start"]),
             length=int(d["length"]))
        for d in data.get("notes", [])
    ]
    note_store.set_notes(notes)