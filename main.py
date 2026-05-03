import tkinter as tk
from tkinter import filedialog, scrolledtext, Toplevel
import threading
import requests
import edge_tts
import os
import tempfile
import uuid
import asyncio
import re
import json
import websockets
import base64
from datetime import datetime
from pygame import mixer
import PyPDF2
from docx import Document
from PIL import Image, ImageTk

# ---------------- CONFIG ----------------
NAME = "Ricki"
VOICE = "en-US-JennyNeural"
URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen2.5-7b-instruct"
VNYAN_URL = "ws://localhost:8000"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AVATAR_PATH = os.path.join(BASE_DIR, "avatar.png")

SYSTEM_PROMPT = f"""
SYSTEM OPERATIONAL FRAMEWORK

IDENTITY:
System name: Ricki.
Ricki is the operational identifier for this AI reasoning and analysis system used in user-facing interactions and system-level orchestration. This identity does not imply human traits, emotions, or roleplay behavior.

ROLE:
You are Ricki, an advanced AI reasoning and analysis system designed to support structured thinking, information synthesis, and decision support with accuracy, clarity, and consistency.

PRIMARY FUNCTION:
Transform input data into clear, structured, and actionable insights through reasoning, comparison, and contextual interpretation.

CORE CAPABILITIES:
- Analytical Reasoning: Interpret and synthesize complex or multi-source inputs.
- Scenario Modeling: Generate structured what-if and outcome-based analysis.
- Consistency Checking: Identify contradictions, gaps, or unclear logic.
- Context Adaptation: Adjust depth and structure based on input complexity.

OUTPUT REQUIREMENTS:
- Separate factual content from interpretation when applicable
- Base conclusions on provided or logically inferred evidence
- Present information in structured, readable form
- Avoid unnecessary verbosity or narrative filler

COMMUNICATION STYLE:
- Neutral, precise, and professional
- Focused on clarity and usability
- No personas, emotional framing, or roleplay behavior
"""

class RickiCommandCenter:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{NAME} OS - Offline GPT Project")
        self.root.geometry("1000x600")
        self.root.configure(bg="#0d0d0d")

        mixer.init()

        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.popout_window = None

        # --- SIDEBAR & AVATAR ---
        self.sidebar = tk.Frame(root, width=280, bg="#1a1a1a")
        self.sidebar.pack(side="left", fill="y")
        self.avatar_dock = tk.Frame(self.sidebar, bg="#1a1a1a")
        self.avatar_dock.pack(side="top", fill="x", pady=(20, 10))

        try:
            pil_img = Image.open(AVATAR_PATH).resize((300, 240), Image.Resampling.LANCZOS)
            self.tk_avatar = ImageTk.PhotoImage(pil_img)
            self.avatar_label = tk.Label(self.avatar_dock, image=self.tk_avatar, bg="#1a1a1a", bd=0)
            self.avatar_label.pack(padx=20)
            self.avatar_label.bind("<Button-1>", lambda e: self.popout_operative())
        except:
            tk.Label(self.avatar_dock, text="PORTRAIT OFFLINE", fg="red", bg="#1a1a1a").pack()

        tk.Label(self.sidebar, text="Document Library", bg="#1a1a1a", fg="#00ffcc", font=("Courier", 11, "bold")).pack(pady=(20, 5))
        self.file_list_frame = tk.Frame(self.sidebar, bg="#1a1a1a")
        self.file_list_frame.pack(fill="both", expand=True)

        # --- CHAT & INPUT ---
        self.chat_display = scrolledtext.ScrolledText(root, bg="#0d0d0d", fg="#00ffcc", font=("Consolas", 11), bd=0)
        self.chat_display.pack(padx=15, pady=15, fill="both", expand=True)

        self.input_frame = tk.Frame(root, bg="#1a1a1a")
        self.input_frame.pack(fill="x", side="bottom")

        tk.Button(self.input_frame, text="📁", command=self.load_file, bg="#333333", fg="white", font=("Arial", 16), bd=0).pack(side="left", padx=10, pady=10)
        # tk.Button(self.input_frame, text="👁️", command=self.scan_visuals, bg="#333333", fg="#00ffcc", font=("Arial", 16), bd=0).pack(side="left", padx=5, pady=10)

        self.entry_box = tk.Entry(self.input_frame, bg="#262626", fg="white", font=("Consolas", 12), insertbackground="#00ffcc", bd=0)
        self.entry_box.pack(side="left", fill="x", expand=True, padx=5, pady=20)
        self.entry_box.bind("<Return>", lambda e: self.send_message())

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_timestamp(self):
        return datetime.now().strftime("%A, %B %d, %Y | %I:%M %p")

    def update_chat(self, sender, text):
        self.chat_display.config(state='normal')
        color = "#007acc" if sender == "You" else "#ff007f" if sender == NAME else "#00ffcc"
        self.chat_display.insert(tk.END, f"{sender}: ", "bold")
        self.chat_display.tag_configure("bold", foreground=color, font=("Consolas", 11, "bold"))
        self.chat_display.insert(tk.END, f"{text}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def execute_ai_call(self, payload):
        try:
            time_tag = f"\n[INTERNAL_CLOCK_SYNC: {self.get_timestamp()}]"
            payload["messages"][0]["content"] = SYSTEM_PROMPT + time_tag

            res = requests.post(URL, json=payload, timeout=300)
            if res.status_code == 200:
                reply = res.json()["choices"][0]["message"]["content"]
                self.update_chat(NAME, reply)
                self.messages.append({"role": "assistant", "content": reply})
                self.speak(reply)
            else:
                self.update_chat("SYSTEM", f"Link error: Code {res.status_code}")
        except Exception as e:
            self.update_chat("SYSTEM", f"Critical Comms Failure: {e}")

    def send_message(self):
        val = self.entry_box.get()
        if not val: return
        self.update_chat("You", val)
        self.entry_box.delete(0, tk.END)
        
        self.messages.append({"role": "user", "content": val})
        payload = {"model": MODEL, "messages": self.messages, "stream": False}
        threading.Thread(target=self.execute_ai_call, args=(payload,), daemon=True).start()

    def load_file(self):
        path = filedialog.askopenfilename()
        if not path: return
        fname = os.path.basename(path)
        try:
            text = ""
            if fname.lower().endswith('.pdf'):
               pdf = PyPDF2.PdfReader(open(path, 'rb'))
               text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
               text = text[:8000]  # limits size safely
            elif fname.lower().endswith(('.docx', '.doc')):
                text = "\n".join([p.text for p in Document(path).paragraphs])
            else:
                text = open(path, 'r', encoding='utf-8').read()
            
            if text:
                text = text[8000:]  # limits size safely
                self.messages.append({"role": "user", "content": f"[Document Library: {fname}]\n{text}"})
                self.update_chat("SYSTEM", f"Asset '{fname}' integrated.")
                tk.Label(self.file_list_frame, text=f"• {fname}", bg="#1a1a1a", fg="#00ffcc", font=("Consolas", 9)).pack(anchor="w", padx=20, pady=2)
        except Exception as e: 
            self.update_chat("SYSTEM", f"Integration Error: {e}")

    def scan_visuals(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not path: return
        self.update_chat("SYSTEM", f"Uploading visual data...")
        b64_image = base64.b64encode(open(path, "rb").read()).decode('utf-8')
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT}, 
                {"role": "user", "content": [
                    {"type": "text", "text": "Analyze this data."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}}
                ]}
            ]
        }
        threading.Thread(target=self.execute_ai_call, args=(payload,), daemon=True).start()

    def speak(self, text):
        clean = re.sub(r'\[.*?\]|\*.*?\*|```.*?```', '', text, flags=re.DOTALL).strip()
        if not clean: return
        def _tts():
            try:
                asyncio.run(self.vnyan_trigger("TalkStart"))
                temp_file = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.mp3")
                asyncio.run(edge_tts.Communicate(clean, VOICE).save(temp_file))
                mixer.music.load(temp_file)
                mixer.music.play()
                while mixer.music.get_busy(): pass
                mixer.music.unload()
                asyncio.run(self.vnyan_trigger("TalkEnd"))
                if os.path.exists(temp_file): os.remove(temp_file)
            except Exception as e: print(f"Speech Error: {e}")
        threading.Thread(target=_tts, daemon=True).start()

    async def vnyan_trigger(self, trigger):
        try:
            async with websockets.connect(VNYAN_URL) as ws:
                await ws.send(json.dumps({"type": "trigger", "name": trigger}))
        except: pass

    def popout_operative(self):
        if self.popout_window is None or not self.popout_window.winfo_exists():
            self.avatar_dock.pack_forget()
            self.popout_window = Toplevel(self.root)
            self.popout_window.attributes('-topmost', True)
            self.popout_window.overrideredirect(True)
            self.popout_window.configure(bg="#0d0d0d")
            self.popout_window.attributes('-transparentcolor', '#0d0d0d')
            self.float_label = tk.Label(self.popout_window, image=self.tk_avatar, bd=0, bg="#0d0d0d")
            self.float_label.pack()
            def start_move(e): self._x, self._y = e.x, e.y
            def on_move(e):
                nx, ny = self.popout_window.winfo_x() - self._x + e.x, self.popout_window.winfo_y() - self._y + e.y
                self.popout_window.geometry(f"+{nx}+{ny}")
            self.float_label.bind("<ButtonPress-1>", start_move)
            self.float_label.bind("<B1-Motion>", on_move)
            self.float_label.bind("<Button-3>", lambda e: [self.popout_window.destroy(), self.avatar_dock.pack(side="top", fill="x", pady=(20,10), before=self.file_list_frame)])

    def on_closing(self):
        mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RickiCommandCenter(root)
    root.mainloop()
