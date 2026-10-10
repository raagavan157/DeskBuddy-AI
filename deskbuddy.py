import os
import sys
import math
import time
import threading
import subprocess
import webbrowser
import queue

import numpy as np
import sounddevice as sd
import speech_recognition as sr
import pyttsx3
import requests

from PySide6.QtCore import Qt, QTimer, QPointF, QObject, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont, QLinearGradient
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QMessageBox, QCheckBox
)


APP_NAME = "DeskBuddy AI"


class Cartoon(QWidget):
    """A lightweight animated cartoon placeholder; no 3D/GPU engine required."""
    def __init__(self):
        super().__init__()
        self.setMinimumSize(280, 330)
        self.phase = 0.0
        self.energy = 0.0
        self.dancing = False
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def set_energy(self, value):
        self.energy = max(0.0, min(1.0, float(value)))
        if self.energy > 0.08:
            self.dancing = True
        self.update()

    def tick(self):
        self.phase += 0.16 + self.energy * 0.24
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        cx = w / 2
        bounce = math.sin(self.phase * 2.0) * (8 + self.energy * 10) if self.dancing else math.sin(self.phase) * 2
        sway = math.sin(self.phase) * (10 + self.energy * 12) if self.dancing else 0
        yoff = bounce

        # Soft floor glow
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(48, 105, 255, 45))
        p.drawEllipse(QPointF(cx, h - 18), 76, 13)

        # Legs and shoes
        leg_y = h * 0.70 + yoff
        p.setPen(QPen(QColor("#263b69"), 16, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(QPointF(cx - 18 + sway * 0.25, leg_y), QPointF(cx - 24 - sway * 0.55, h - 43 + yoff))
        p.drawLine(QPointF(cx + 18 + sway * 0.25, leg_y), QPointF(cx + 24 + sway * 0.55, h - 43 + yoff))
        p.setPen(QPen(QColor("#f4f7ff"), 10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(QPointF(cx - 24 - sway * 0.55, h - 43 + yoff), QPointF(cx - 42 - sway * 0.55, h - 39 + yoff))
        p.drawLine(QPointF(cx + 24 + sway * 0.55, h - 43 + yoff), QPointF(cx + 42 + sway * 0.55, h - 39 + yoff))

        # Arms
        p.setPen(QPen(QColor("#e8a77f"), 13, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        arm_angle = math.sin(self.phase * 2) * (34 if self.dancing else 8)
        p.drawLine(QPointF(cx - 33 + sway * 0.2, h * 0.53 + yoff),
                   QPointF(cx - 55 - arm_angle * 0.4, h * 0.62 - arm_angle + yoff))
        p.drawLine(QPointF(cx + 33 + sway * 0.2, h * 0.53 + yoff),
                   QPointF(cx + 55 + arm_angle * 0.4, h * 0.62 + arm_angle + yoff))

        # Hoodie body
        grad = QLinearGradient(cx - 50, h * .43, cx + 50, h * .72)
        grad.setColorAt(0, QColor("#4f8cff"))
        grad.setColorAt(1, QColor("#7657e8"))
        p.setBrush(QBrush(grad))
        p.setPen(QPen(QColor("#a9c8ff"), 2))
        p.drawRoundedRect(int(cx - 39 + sway * .15), int(h * .43 + yoff), 78, 100, 24, 24)

        # Neck
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#e8a77f"))
        p.drawRoundedRect(int(cx - 12 + sway * .15), int(h * .37 + yoff), 24, 25, 8, 8)

        # Head
        head_x = cx + sway * .12
        head_y = h * .27 + yoff
        p.setBrush(QColor("#f1bd96"))
        p.setPen(QPen(QColor("#d9946e"), 1.5))
        p.drawEllipse(QPointF(head_x, head_y), 43, 47)

        # Hair
        p.setBrush(QColor("#20283b"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawChord(int(head_x - 44), int(head_y - 53), 88, 63, 0 * 16, 180 * 16)
        p.drawEllipse(int(head_x - 43), int(head_y - 25), 15, 23)
        p.drawEllipse(int(head_x + 28), int(head_y - 24), 15, 22)

        # Eyes, eyebrows, smile
        p.setBrush(QColor("#ffffff"))
        p.drawEllipse(QPointF(head_x - 15, head_y + 1), 8, 10)
        p.drawEllipse(QPointF(head_x + 15, head_y + 1), 8, 10)
        p.setBrush(QColor("#20283b"))
        p.drawEllipse(QPointF(head_x - 13, head_y + 3), 3.5, 5)
        p.drawEllipse(QPointF(head_x + 17, head_y + 3), 3.5, 5)
        p.setPen(QPen(QColor("#8d493d"), 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(int(head_x - 13), int(head_y + 12), 26, 17, 200 * 16, 140 * 16)

        # Headphones
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor("#26e0d0"), 5))
        p.drawArc(int(head_x - 45), int(head_y - 47), 90, 79, 0, 180 * 16)
        p.setBrush(QColor("#26e0d0"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(int(head_x - 48), int(head_y - 9), 12, 27, 5, 5)
        p.drawRoundedRect(int(head_x + 36), int(head_y - 9), 12, 27, 5, 5)

        # Hoodie drawstrings
        p.setPen(QPen(QColor("#dce8ff"), 2))
        p.drawLine(QPointF(cx - 8 + sway * .15, h * .49 + yoff), QPointF(cx - 8 + sway * .15, h * .57 + yoff))
        p.drawLine(QPointF(cx + 8 + sway * .15, h * .49 + yoff), QPointF(cx + 8 + sway * .15, h * .57 + yoff))

        # Status label
        p.setPen(QColor("#dce7ff"))
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        status = "DANCING 🎵" if self.energy > 0.08 else "DESKBUDDY"
        p.drawText(0, h - 3, w, 20, Qt.AlignmentFlag.AlignHCenter, status)
        p.end()


class UiBridge(QObject):
    call = Signal(object)


class DeskBuddy(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(440, 720)
        self.setMinimumSize(400, 640)
        self.setStyleSheet("""
            QWidget { background: #0c1224; color: #edf2ff; font-family: 'Segoe UI'; }
            QLabel#title { font-size: 23px; font-weight: 700; color: #ffffff; }
            QLabel#muted { color: #9eadd1; }
            QPushButton { background: #315be8; border: 0; border-radius: 10px; padding: 10px; font-weight: 600; }
            QPushButton:hover { background: #4772ff; }
            QPushButton:disabled { background: #35405e; color: #9eadd1; }
            QLineEdit, QTextEdit { background: #151e36; border: 1px solid #2b395d; border-radius: 9px; padding: 9px; }
            QCheckBox { spacing: 8px; color: #cbd6f4; }
        """)
        self.energy_queue = queue.Queue()
        self.ui_bridge = UiBridge()
        self.ui_bridge.call.connect(self._run_ui_callback)
        self.audio_stream = None
        self.audio_enabled = False
        self.listening = False
        self.speech_engine = None
        try:
            self.speech_engine = pyttsx3.init()
            self.speech_engine.setProperty("rate", 175)
        except Exception:
            self.speech_engine = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        title = QLabel("DeskBuddy AI")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Your little desktop companion")
        subtitle.setObjectName("muted")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        self.cartoon = Cartoon()
        layout.addWidget(self.cartoon, 1)

        self.status = QLabel("Ready • Turn on music mode to react to sound")
        self.status.setObjectName("muted")
        self.status.setWordWrap(True)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status)

        controls = QHBoxLayout()
        self.music_btn = QPushButton("🎵 Start music mode")
        self.music_btn.clicked.connect(self.toggle_music)
        controls.addWidget(self.music_btn)
        self.listen_btn = QPushButton("🎙 Listen")
        self.listen_btn.clicked.connect(self.listen_once)
        controls.addWidget(self.listen_btn)
        layout.addLayout(controls)

        self.command = QLineEdit()
        self.command.setPlaceholderText("Try: open Chrome / what time is it?")
        self.command.returnPressed.connect(self.handle_text_command)
        layout.addWidget(self.command)

        send_row = QHBoxLayout()
        self.send_btn = QPushButton("Send command")
        self.send_btn.clicked.connect(self.handle_text_command)
        send_row.addWidget(self.send_btn)
        self.voice_check = QCheckBox("Speak replies")
        self.voice_check.setChecked(True)
        send_row.addWidget(self.voice_check)
        layout.addLayout(send_row)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setMaximumHeight(125)
        self.chat.append("DeskBuddy: Hi! Click Listen and speak, or type a command below.")
        layout.addWidget(self.chat)

        note = QLabel("Privacy: microphone access is used only for music-level detection or when you press Listen.")
        note.setObjectName("muted")
        note.setWordWrap(True)
        note.setStyleSheet("font-size: 11px;")
        layout.addWidget(note)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.cartoon.tick)
        self.anim_timer.start(35)

        self.level_timer = QTimer(self)
        self.level_timer.timeout.connect(self.update_audio_level)
        self.level_timer.start(100)

    def say(self, text):
        if self.voice_check.isChecked() and self.speech_engine:
            def speak():
                try:
                    self.speech_engine.say(text)
                    self.speech_engine.runAndWait()
                except Exception:
                    pass
            threading.Thread(target=speak, daemon=True).start()

    def reply(self, user_text, answer):
        self.chat.append(f"You: {user_text}")
        self.chat.append(f"DeskBuddy: {answer}")
        self.status.setText(answer[:100])
        self.say(answer)

    def toggle_music(self):
        if not self.audio_enabled:
            try:
                self.audio_stream = sd.InputStream(
                    channels=1, samplerate=16000, blocksize=1024,
                    callback=self.audio_callback
                )
                self.audio_stream.start()
                self.audio_enabled = True
                self.music_btn.setText("⏹ Stop music mode")
                self.status.setText("Music mode on • Play YouTube through your speakers")
            except Exception as e:
                QMessageBox.warning(
                    self, "Microphone unavailable",
                    "DeskBuddy could not open the microphone.\n\nCheck Windows Settings > Privacy & security > Microphone, then try again.\n\nDetails: " + str(e)
                )
        else:
            self.stop_audio()
            self.music_btn.setText("🎵 Start music mode")
            self.status.setText("Music mode off")

    def stop_audio(self):
        if self.audio_stream is not None:
            try:
                self.audio_stream.stop()
                self.audio_stream.close()
            except Exception:
                pass
            self.audio_stream = None
        self.audio_enabled = False
        self.cartoon.set_energy(0)

    def audio_callback(self, indata, frames, time_info, status):
        try:
            rms = float(np.sqrt(np.mean(np.square(indata))))
            self.energy_queue.put(min(1.0, rms * 10))
        except Exception:
            pass

    def update_audio_level(self):
        latest = None
        try:
            while True:
                latest = self.energy_queue.get_nowait()
        except queue.Empty:
            pass
        if latest is not None and self.audio_enabled:
            self.cartoon.set_energy(latest)
            if latest > 0.08:
                self.status.setText("Music/sound detected • I'm dancing!")
            else:
                self.status.setText("Listening for music through your microphone…")

    def listen_once(self):
        if self.listening:
            return
        self.listening = True
        self.listen_btn.setEnabled(False)
        self.status.setText("Listening… speak now")
        if self.audio_enabled:
            self.stop_audio()
            self.music_btn.setText("🎵 Start music mode")
        threading.Thread(target=self._recognize_speech, daemon=True).start()

    def _recognize_speech(self):
        recognizer = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            words = recognizer.recognize_google(audio)
            self.call_ui(lambda: self.process_recognized(words))
        except sr.WaitTimeoutError:
            self.call_ui(lambda: self.reply("voice", "I didn't hear anything. Press Listen and try again."))
        except sr.UnknownValueError:
            self.call_ui(lambda: self.reply("voice", "I couldn't understand that. Please try again."))
        except Exception as e:
            msg = "Speech recognition failed. Check your microphone and internet connection. " + str(e)[:120]
            self.call_ui(lambda: self.reply("voice", msg))
        finally:
            self.call_ui(self.finish_listening)

    def call_ui(self, fn):
        self.ui_bridge.call.emit(fn)

    def _run_ui_callback(self, fn):
        fn()

    def finish_listening(self):
        self.listening = False
        self.listen_btn.setEnabled(True)
        self.status.setText("Ready")

    def handle_text_command(self):
        text = self.command.text().strip()
        if not text:
            return
        self.command.clear()
        self.process_recognized(text)

    def process_recognized(self, text):
        low = text.lower().strip()
        if low.startswith("open ") or low.startswith("launch "):
            target = low.replace("launch ", "", 1).replace("open ", "", 1).strip()
            answer = self.open_app(target)
        elif "time" in low:
            answer = "It is " + time.strftime("%I:%M %p") + "."
        elif low in ("hello", "hi", "hey", "hey buddy", "hello buddy"):
            answer = "Hey! I'm DeskBuddy. Ask me to open an app or ask a question."
        elif "dance" in low or "music mode" in low:
            if not self.audio_enabled:
                self.toggle_music()
            answer = "Music mode is ready. Play music through your laptop speakers and I'll react to the sound."
        elif low in ("stop", "stop music", "stop dancing"):
            self.stop_audio()
            self.music_btn.setText("🎵 Start music mode")
            answer = "Okay, music mode is stopped."
        elif low in ("help", "what can you do"):
            answer = "I can open Chrome, Edge, VS Code, Calculator, Notepad, File Explorer, and YouTube. I can also tell the time. Add an AI API key to enable AI answers."
        else:
            answer = self.ask_ai(text)
        self.reply(text, answer)

    def open_app(self, target):
        aliases = {
            "chrome": ["chrome", "google chrome", "browser"],
            "edge": ["edge", "microsoft edge"],
            "vs code": ["vs code", "vscode", "visual studio code", "code"],
            "calculator": ["calculator", "calc"],
            "notepad": ["notepad", "text editor"],
            "file explorer": ["file explorer", "explorer", "files"],
            "youtube": ["youtube"],
        }
        chosen = None
        for app, names in aliases.items():
            if target in names:
                chosen = app
                break
        try:
            if chosen == "chrome":
                # Open Chrome if installed; otherwise open YouTube in default browser.
                candidates = [
                    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                    os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
                ]
                exe = next((p for p in candidates if os.path.exists(p)), None)
                if exe:
                    subprocess.Popen([exe])
                else:
                    webbrowser.open("https://www.google.com")
                return "Opening Chrome."
            if chosen == "edge":
                subprocess.Popen(["cmd", "/c", "start", "", "msedge"], shell=False)
                return "Opening Microsoft Edge."
            if chosen == "vs code":
                subprocess.Popen(["cmd", "/c", "code"], shell=False)
                return "Opening VS Code. If it doesn't open, enable the VS Code command-line PATH option."
            if chosen == "calculator":
                subprocess.Popen(["calc.exe"])
                return "Opening Calculator."
            if chosen == "notepad":
                subprocess.Popen(["notepad.exe"])
                return "Opening Notepad."
            if chosen == "file explorer":
                subprocess.Popen(["explorer.exe"])
                return "Opening File Explorer."
            if chosen == "youtube":
                webbrowser.open("https://www.youtube.com")
                return "Opening YouTube."
            return "I don't know that app yet. Try Chrome, VS Code, Calculator, Notepad, File Explorer, Edge, or YouTube."
        except Exception as e:
            return f"I couldn't open {target}. Check that it is installed. Details: {str(e)[:100]}"

    def ask_ai(self, prompt):
        # Optional OpenAI-compatible chat API. Set OPENAI_API_KEY in Windows environment.
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            return ("I can open apps and handle basic commands, but smart AI answers need an API key. "
                    "Set OPENAI_API_KEY in your Windows environment to connect an AI model. "
                    "For now, try 'help' or 'open Chrome'.")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are DeskBuddy, a friendly concise desktop assistant. Do not claim to perform actions you have not performed."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                },
                timeout=25
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return "I couldn't reach the AI service. Check the API key, internet connection, model access, and billing settings. " + str(e)[:120]

    def closeEvent(self, event):
        self.stop_audio()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = DeskBuddy()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
