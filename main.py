"""
Video Processor Pro
A multi-threaded desktop GUI for batch video compression, format conversion, 
and audio stripping using FFmpeg with hardware acceleration (NVENC, QSV, CPU).
"""

import os
import glob
import subprocess
import platform
import webbrowser
import re 
import ctypes
import tempfile
from datetime import datetime
from tkinter import (Tk, Label, Button, filedialog, messagebox, ttk, Text,
                     Scrollbar, Checkbutton, IntVar, Entry, Frame, BOTH, X, Y,
                     LEFT, RIGHT, END, DISABLED, NORMAL, FLAT)
from tkinter.ttk import Notebook
from threading import Thread
from typing import List, Tuple, Optional, Dict, Callable
import shutil

# =============================================================================
# LOCALIZATION DICTIONARY (IT / EN)
# =============================================================================
LANG = {
    "IT": {
        "title": "Video Processor Pro",
        "tab1": " 🎬 Elaborazione Principale ",
        "tab2": " ⚙️ Impostazioni Avanzate ",
        "f_in_out": "1. Seleziona Cartelle",
        "f_action": "2. Azione di Conversione",
        "f_ffmpeg": "Percorso FFmpeg / FFprobe",
        "f_ext": "Formati da Scansionare",
        "f_naming": "Nomenclatura (Prefisso / Suffisso) e Sovrascrittura",
        "lbl_in": "Cartella Input",
        "lbl_out": "Cartella Output",
        "lbl_ffmpeg": "Percorso FFmpeg",
        "lbl_pref": "Prefisso:",
        "lbl_suff": "Suffisso:",
        "btn_browse_dir": "Scegli Cartella",
        "btn_browse_file": "Sfoglia...",
        "btn_start": "🚀 AVVIA PROCESSO",
        "btn_stop": "⏹ INTERROMPI",
        "btn_log": "📄 APRI LOG",
        "chk_audio": "Rimuovi Traccia Audio (-an)",
        "chk_overwrite": "Sovrascrivi direttamente i file originali (In-place)",
        "not_selected": "(non selezionata)",
        "ff_not_selected": "(non selezionato, usa 'ffmpeg' di sistema)",
        "waiting": "In attesa...",
        "processing": "Elaborando File {current}/{total}: {filename}",
        "completed": "Completato!",
        "interrupted": "Interrotto!",
        "err": "Errore.",
        "msg_in_prompt": "Seleziona la cartella contenente i file video",
        "msg_out_prompt": "Seleziona la cartella dove salvare i file modificati",
        "msg_ff_prompt": "Seleziona l'eseguibile ffmpeg",
        "msg_confirm_stop": "Vuoi interrompere il processo?\nIl file in elaborazione verrà scartato e rimosso.",
        "msg_stop_info": "Processo interrotto. L'ultimo file parziale è stato rimosso.",
        "msg_no_log": "File di log inesistente o cartella non selezionata.",
        "msg_ff_err": "ERRORE FFMPEG: Eseguibile non valido o non trovato nel PATH.",
        "msg_in_err": "ERRORE INPUT: Seleziona una cartella valida.",
        "msg_out_err": "ERRORE OUTPUT: Seleziona una cartella o abilita la sovrascrittura.",
        "msg_action_err": "ERRORE: Seleziona un'azione valida.",
        "msg_overwrite_warn": "ATTENZIONE: Sovrascriverai i file originali. Sei sicuro di voler continuare?",
        "msg_overwrite_on": "Sovrascrittura In-place ATTIVA. I nuovi file sostituiranno gli originali.",
        "msg_overwrite_off": "Sovrascrittura disattivata.",
        "same_as_in": "(identica a Input)",
        "act_nv_1080": "Comprimi 1080p (Veloce - NVIDIA)",
        "act_nv_720":  "Comprimi 720p (Veloce - NVIDIA)",
        "act_qsv_1080": "Comprimi 1080p (Veloce - Intel)",
        "act_qsv_720":  "Comprimi 720p (Veloce - Intel)",
        "act_cpu_1080": "Comprimi 1080p (Qualità - CPU)",
        "act_cpu_720":  "Comprimi 720p (Qualità - CPU)",
        "act_copy":     "Copia Flusso Video (Veloce, No Riconversione)",
        "log_title": "Log Console",
        "rep_final": "--- Report Finale ---",
        "rep_found": "File trovati",
        "rep_done": "Elaborati",
        "rep_saved": "Spazio netto risparmiato"
    },
    "EN": {
        "title": "Video Processor Pro",
        "tab1": " 🎬 Main Processing ",
        "tab2": " ⚙️ Advanced Settings ",
        "f_in_out": "1. Select Folders",
        "f_action": "2. Conversion Action",
        "f_ffmpeg": "FFmpeg / FFprobe Path",
        "f_ext": "Formats to Scan",
        "f_naming": "Naming (Prefix / Suffix) and Overwrite Rules",
        "lbl_in": "Input Folder",
        "lbl_out": "Output Folder",
        "lbl_ffmpeg": "FFmpeg Path",
        "lbl_pref": "Prefix:",
        "lbl_suff": "Suffix:",
        "btn_browse_dir": "Choose Folder",
        "btn_browse_file": "Browse...",
        "btn_start": "🚀 START PROCESSING",
        "btn_stop": "⏹ STOP",
        "btn_log": "📄 OPEN LOG",
        "chk_audio": "Remove Audio Track (-an)",
        "chk_overwrite": "Overwrite original files directly (In-place)",
        "not_selected": "(not selected)",
        "ff_not_selected": "(not selected, system 'ffmpeg' will be used)",
        "waiting": "Waiting...",
        "processing": "Processing File {current}/{total}: {filename}",
        "completed": "Completed!",
        "interrupted": "Interrupted!",
        "err": "Error.",
        "msg_in_prompt": "Select the folder containing the video files",
        "msg_out_prompt": "Select the folder to save modified files",
        "msg_ff_prompt": "Select the ffmpeg executable",
        "msg_confirm_stop": "Do you want to stop the process?\nThe file currently being processed will be discarded.",
        "msg_stop_info": "Process interrupted. The last partial file was discarded.",
        "msg_no_log": "Error log not found or input folder not selected.",
        "msg_ff_err": "FFMPEG ERROR: Executable invalid or not found in PATH.",
        "msg_in_err": "INPUT ERROR: Please select a valid input folder.",
        "msg_out_err": "OUTPUT ERROR: Please select an output folder or enable overwrite.",
        "msg_action_err": "ERROR: Select a valid action.",
        "msg_overwrite_warn": "WARNING: You are about to overwrite original files. Are you sure?",
        "msg_overwrite_on": "In-place Overwrite ENABLED. Original files will be replaced.",
        "msg_overwrite_off": "Overwrite disabled.",
        "same_as_in": "(same as Input)",
        "act_nv_1080": "Compress 1080p (Fast - NVIDIA)",
        "act_nv_720":  "Compress 720p (Fast - NVIDIA)",
        "act_qsv_1080": "Compress 1080p (Fast - Intel)",
        "act_qsv_720":  "Compress 720p (Fast - Intel)",
        "act_cpu_1080": "Compress 1080p (Quality - CPU)",
        "act_cpu_720":  "Compress 720p (Quality - CPU)",
        "act_copy":     "Copy Video Stream (Fast, No Re-encode)",
        "log_title": "Console Log",
        "rep_final": "--- Final Report ---",
        "rep_found": "Files found",
        "rep_done": "Processed",
        "rep_saved": "Net space saved"
    }
}

# Dark theme palette
BG_COLOR = "#141518"
CARD_BG = "#1c1d22"
INPUT_BG = "#101114"
BORDER_COLOR = "#2e3138"
TEXT_COLOR = "#e6e8eb"
TEXT_MUTED_COLOR = "#8b929e"
BUTTON_BG = "#2a2d35"
BUTTON_ACTIVE_BG = "#383c47"
BUTTON_DISABLED_BG = "#1f2127"
BUTTON_DISABLED_FG = "#525763"
ACCENT_COLOR = "#00bc8c"
ACCENT_ACTIVE = "#009970"
ACCENT_FG = "#ffffff"
WARN_COLOR = "#e74c3c"
WARN_ACTIVE = "#c0392b"
WARN_DISABLED_COLOR = "#3d2222"
WARN_INTERRUPT_FG = "#e67e22"
INFO_COLOR = "#3498db"
SUCCESS_COLOR = "#00bc8c"
ERROR_COLOR = "#e74c3c"

FONT_DEFAULT = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI", 10)
FONT_BUTTON = ("Segoe UI", 9, "bold")
FONT_BUTTON_ACTION = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_LOG = ("Consolas", 9)
FONT_PROGRESS = ("Segoe UI", 10, "bold")

DEFAULT_SUFFIX = "_output"
ERROR_LOG_FILENAME = "video_processor_error_log.txt"
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']

ACTION_KEYS = [
    "act_nv_1080", "act_nv_720", "act_qsv_1080", "act_qsv_720",
    "act_cpu_1080", "act_cpu_720", "act_copy"
]

ACTION_INTERNAL_MAP = {
    "act_nv_1080": "comprimi_1080p_nvenc",
    "act_nv_720": "comprimi_720p_nvenc",
    "act_qsv_1080": "comprimi_1080p_qsv",
    "act_qsv_720": "comprimi_720p_qsv",
    "act_cpu_1080": "comprimi_1080p_cpu",
    "act_cpu_720": "comprimi_720p_cpu",
    "act_copy": "copia_flusso_video"
}

# =============================================================================
# PROCESSING ENGINE (FFmpeg interface)
# =============================================================================
class VideoProcessor:
    def __init__(self):
        self.interrompi: bool = False
        self.ultimo_output_temp_path: Optional[str] = None
        self.time_regex = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d+)")

    def _parse_time(self, time_str: str) -> float:
        match = self.time_regex.search(time_str)
        if match:
            h, m, s, ms = map(int, match.groups())
            return (h * 3600) + (m * 60) + s + (ms / 100.0)
        return 0.0

    def _esegui_ffmpeg(self, comando: List[str], update_cb=None, total_dur=0.0) -> subprocess.CompletedProcess:
        cflags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        stderr_output = []
        return_code = 1 
        try:
            process = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                       text=True, encoding='utf-8', errors='replace', creationflags=cflags)
            for line in iter(process.stdout.readline, ''):
                if self.interrompi:
                    process.terminate() 
                    break
                stderr_output.append(line)
                if update_cb and total_dur > 0:
                    c_sec = self._parse_time(line)
                    if c_sec > 0:
                        update_cb(int((c_sec / total_dur) * 100))
            process.stdout.close()
            return_code = process.wait()
        except Exception as e:
            stderr_output.append(f"\nERROR: {e}\n")
        return subprocess.CompletedProcess(args=comando, returncode=return_code, stdout="", stderr="".join(stderr_output))

    def copia_flusso_video(self, ff, inf, outf, rm_aud):
        cmd_aud = ['-an'] if rm_aud else ['-c:a', 'copy']
        return self._esegui_ffmpeg([ff, "-y", "-hide_banner", "-i", inf, "-c:v", "copy", *cmd_aud, outf])

    def comprimi_video(self, ff, inf, outf, height, rm_aud, encoder, cb, dur):
        cmd_aud = ['-an'] if rm_aud else ['-c:a', 'aac', '-b:a', '128k']
        vf = f'scale=-2:{height},format=yuv420p'
        cmd = [ff, '-y', '-hide_banner', '-i', inf, '-c:v', encoder]
        if "nvenc" in encoder:
            cmd += ['-preset', 'p5', '-rc', 'constqp', '-qp', '23']
        elif "qsv" in encoder:
            cmd += ['-preset', 'medium', '-global_quality', '23']
        else:
            cmd += ['-crf', '23', '-preset', 'fast']
        cmd += ['-vf', vf, *cmd_aud, '-progress', 'pipe:1', outf]
        return self._esegui_ffmpeg(cmd, cb, dur)

    def verifica_ffmpeg(self, path: str) -> bool:
        try:
            res = subprocess.run([path, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def get_duration(self, ffp, inf) -> float:
        cmd = [ffp, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", inf]
        cflags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=cflags, timeout=10) 
            return float(res.stdout.strip())
        except Exception:
            return 0.0

    def avvia(self, t: dict, opz: dict, cb_prog, cb_file, log_w) -> tuple:
        self.interrompi = False
        self.ultimo_output_temp_path = None
        ffprobe_path = "ffprobe"
        
        if opz["ff"] != "ffmpeg" and (opz["ff"].endswith(".exe") or "bin" in opz["ff"]):
            ffprobe_path = os.path.join(os.path.dirname(opz["ff"]), "ffprobe.exe" if platform.system() == "Windows" else "ffprobe")

        video_files = []
        for ext in opz["exts"]:
            video_files.extend(glob.glob(os.path.join(opz["in_d"], '**', f'*{ext}'), recursive=True))
        video_files = sorted(list(set(video_files)))

        if not video_files:
            return 0, 0, 0.0, ["Nessun file video trovato con le estensioni selezionate."]

        spazio = 0.0
        elaborati = 0
        errs = []
        tot = len(video_files)
        
        target_dir = opz["in_d"] if opz["ovr"] else opz["out_d"]
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            
        log_path = os.path.join(opz["in_d"], ERROR_LOG_FILENAME)
        try:
            with open(log_path, "w", encoding='utf-8') as lf:
                lf.write(f"Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        except:
            pass

        for idx, vf in enumerate(video_files):
            if self.interrompi:
                break
            
            nome = os.path.basename(vf)
            base, ext = os.path.splitext(nome)
            out_ext = ".mp4" if opz["act"].startswith("comprimi_") else ext
            
            if opz["ovr"]:
                final_dest = os.path.join(os.path.dirname(vf), f"{base}{out_ext}")
            else:
                final_dest = os.path.join(target_dir, f"{opz['pref']}{base}{opz['suff']}{out_ext}")

            work_dir = os.path.dirname(final_dest)
            temp_fd, tmp_out = tempfile.mkstemp(prefix="vproc_tmp_", suffix=out_ext, dir=work_dir)
            os.close(temp_fd)
            self.ultimo_output_temp_path = tmp_out
            
            try:
                cb_prog(idx + 1, tot, nome)
                orig_sz = os.path.getsize(vf)
                dur = self.get_duration(ffprobe_path, vf) if opz["act"].startswith("comprimi_") else 0.0
                
                if opz["act"] == "copia_flusso_video":
                    res = self.copia_flusso_video(opz["ff"], vf, tmp_out, opz["rm_aud"])
                else:
                    enc = "h264_nvenc" if "nvenc" in opz["act"] else ("h264_qsv" if "qsv" in opz["act"] else "libx264")
                    h = "1080" if "1080" in opz["act"] else "720"
                    res = self.comprimi_video(opz["ff"], vf, tmp_out, h, opz["rm_aud"], enc, cb_file, dur)

                if res.returncode == 0 and os.path.exists(tmp_out) and os.path.getsize(tmp_out) > 0:
                    cb_file(100)
                    
                    if os.path.abspath(final_dest) == os.path.abspath(vf):
                        try:
                            os.remove(vf)
                        except OSError:
                            pass
                    
                    shutil.move(tmp_out, final_dest)
                    self.ultimo_output_temp_path = None
                    spazio += (orig_sz - os.path.getsize(final_dest))
                    elaborati += 1
                    self.log(log_w, f"OK: {nome} -> {os.path.basename(final_dest)}", "INFO")
                else:
                    err_msg = res.stderr.strip()[:140] if res.stderr else "Errore sconosciuto."
                    errs.append(f"{nome}: {err_msg}")
                    self.log(log_w, f"ERROR su {nome}", "ERROR")
                    if os.path.exists(tmp_out):
                        os.remove(tmp_out)
            except Exception as e:
                errs.append(f"{nome}: {e}")
                self.log(log_w, f"CRITICAL: {nome} - {e}", "ERROR")
                if os.path.exists(tmp_out):
                    os.remove(tmp_out)

        if self.interrompi and self.ultimo_output_temp_path and os.path.exists(self.ultimo_output_temp_path):
            try:
                os.remove(self.ultimo_output_temp_path)
            except:
                pass
            
        return tot, elaborati, (spazio / (1024 * 1024)), errs

    def log(self, w, msg, lvl):
        ts = datetime.now().strftime('%H:%M:%S')
        s = f"[{ts}] {lvl}: {msg}\n"
        if w:
            w.insert(END, s, lvl)
            w.see(END)


# =============================================================================
# APPLICATION GUI
# =============================================================================
class AppGUI:
    def __init__(self, root: Tk):
        self.root = root
        self.processor = VideoProcessor()
        self.lang = "EN"
        
        self.root.title(LANG[self.lang]["title"])
        self.root.geometry("860x800")
        self.root.configure(bg=BG_COLOR)
        self.root.minsize(680, 640)
        self._apply_dark_title_bar()
        self._setup_styles()
        self._build_ui()
        self._update_texts()
        self._aggiorna_stato_avvia()

    def _apply_dark_title_bar(self):
        try:
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            v = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(v), ctypes.sizeof(v))
        except:
            pass

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use('clam')
        s.configure(".", background=BG_COLOR, foreground=TEXT_COLOR)
        s.configure("TLabelFrame", background=BG_COLOR, foreground=ACCENT_COLOR, font=(FONT_DEFAULT[0], 10, "bold"), bordercolor=BORDER_COLOR)
        s.configure("TLabelFrame.Label", background=BG_COLOR, foreground=ACCENT_COLOR)
        s.configure("TFrame", background=BG_COLOR)
        s.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        s.configure("TNotebook.Tab", font=("Segoe UI", 9, "bold"), padding=[14, 6], background=CARD_BG, foreground=TEXT_MUTED_COLOR, bordercolor=BORDER_COLOR)
        s.map("TNotebook.Tab", background=[("selected", BG_COLOR), ("active", BUTTON_BG)], foreground=[("selected", ACCENT_COLOR), ("active", TEXT_COLOR)])
        s.configure("TCombobox", fieldbackground=INPUT_BG, background=BUTTON_BG, foreground=TEXT_COLOR, bordercolor=BORDER_COLOR, arrowcolor=TEXT_COLOR)
        s.map("TCombobox", fieldbackground=[('readonly', INPUT_BG)], foreground=[('readonly', TEXT_COLOR)])
        s.configure("TProgressbar", thickness=16, background=ACCENT_COLOR, troughcolor=INPUT_BG, borderwidth=0)
        self.root.option_add('*TCombobox*Listbox.background', INPUT_BG)
        self.root.option_add('*TCombobox*Listbox.foreground', TEXT_COLOR)
        self.root.option_add('*TCombobox*Listbox.selectBackground', ACCENT_COLOR)

    def _build_ui(self):
        head = Frame(self.root, bg=BG_COLOR)
        head.pack(fill=X, padx=20, pady=(16, 8))
        self.lbl_title = Label(head, font=FONT_TITLE, bg=BG_COLOR, fg=TEXT_COLOR)
        self.lbl_title.pack(side=LEFT)
        l_frame = Frame(head, bg=BG_COLOR)
        l_frame.pack(side=RIGHT, pady=4)
        self.btn_it = Button(l_frame, text="ITA", command=lambda: self._set_lang("IT"), font=("Segoe", 8, "bold"), relief=FLAT, bg=BUTTON_BG, fg=TEXT_MUTED_COLOR)
        self.btn_it.pack(side=LEFT, padx=2)
        self.btn_en = Button(l_frame, text="ENG", command=lambda: self._set_lang("EN"), font=("Segoe", 8, "bold"), relief=FLAT, bg=ACCENT_COLOR, fg=ACCENT_FG)
        self.btn_en.pack(side=LEFT, padx=2)

        self.nb = Notebook(self.root)
        self.nb.pack(fill=X, expand=True, padx=20, pady=5)
        self.t1 = ttk.Frame(self.nb, padding=12)
        self.t2 = ttk.Frame(self.nb, padding=12)
        self.nb.add(self.t1, text="")
        self.nb.add(self.t2, text="")

        # TAB 1
        self.lf_inout = ttk.LabelFrame(self.t1, padding=14)
        self.lf_inout.pack(fill=X, pady=4)
        r_in = Frame(self.lf_inout, bg=BG_COLOR)
        r_in.pack(fill=X, pady=4)
        self.lbl_in = Label(r_in, font=FONT_LABEL, bg=BG_COLOR, fg=TEXT_COLOR, anchor='w')
        self.lbl_in.pack(side=LEFT, fill=X, expand=True)
        self.val_in = ""
        self.btn_in = Button(r_in, command=lambda: self._pick_dir('in'), font=FONT_BUTTON, bg=BUTTON_BG, fg=TEXT_COLOR, relief=FLAT, padx=12)
        self.btn_in.pack(side=RIGHT)
        
        r_out = Frame(self.lf_inout, bg=BG_COLOR)
        r_out.pack(fill=X, pady=4)
        self.lbl_out = Label(r_out, font=FONT_LABEL, bg=BG_COLOR, fg=TEXT_COLOR, anchor='w')
        self.lbl_out.pack(side=LEFT, fill=X, expand=True)
        self.val_out = ""
        self.btn_out = Button(r_out, command=lambda: self._pick_dir('out'), font=FONT_BUTTON, bg=BUTTON_BG, fg=TEXT_COLOR, relief=FLAT, padx=12)
        self.btn_out.pack(side=RIGHT)

        self.lf_act = ttk.LabelFrame(self.t1, padding=14)
        self.lf_act.pack(fill=X, pady=6)
        self.combo = ttk.Combobox(self.lf_act, font=FONT_DEFAULT, state="readonly")
        self.combo.pack(fill=X, pady=4)
        self.var_aud = IntVar(value=0)
        self.chk_aud = Checkbutton(self.lf_act, variable=self.var_aud, font=FONT_LABEL, bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=INPUT_BG, anchor='w')
        self.chk_aud.pack(fill=X, pady=(6, 0))

        # TAB 2
        self.lf_ff = ttk.LabelFrame(self.t2, padding=14)
        self.lf_ff.pack(fill=X, pady=4)
        r_ff = Frame(self.lf_ff, bg=BG_COLOR)
        r_ff.pack(fill=X)
        self.lbl_ff = Label(r_ff, font=FONT_LABEL, bg=BG_COLOR, fg=TEXT_MUTED_COLOR, anchor='w')
        self.lbl_ff.pack(side=LEFT, fill=X, expand=True)
        self.val_ff = ""
        self.btn_ff = Button(r_ff, command=self._pick_ff, font=FONT_BUTTON, bg=BUTTON_BG, fg=TEXT_COLOR, relief=FLAT, padx=12)
        self.btn_ff.pack(side=RIGHT)

        self.lf_ext = ttk.LabelFrame(self.t2, padding=14)
        self.lf_ext.pack(fill=X, pady=6)
        r_ext = Frame(self.lf_ext, bg=BG_COLOR)
        r_ext.pack(fill=X)
        self.vars_ext = {}
        for i, ext in enumerate(VIDEO_EXTENSIONS):
            v = IntVar(value=1)
            c = Checkbutton(r_ext, text=ext, variable=v, font=FONT_LABEL, bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=INPUT_BG)
            c.grid(row=i//3, column=i%3, padx=12, pady=4, sticky='w')
            self.vars_ext[ext] = v

        self.lf_name = ttk.LabelFrame(self.t2, padding=14)
        self.lf_name.pack(fill=X, pady=6)
        rn = Frame(self.lf_name, bg=BG_COLOR)
        rn.pack(fill=X, pady=2)
        
        self.l_pref = Label(rn, font=FONT_LABEL, bg=BG_COLOR, fg=TEXT_COLOR)
        self.l_pref.pack(side=LEFT, padx=(0, 4))
        self.e_pref = Entry(rn, font=FONT_DEFAULT, width=14, bg=INPUT_BG, fg=TEXT_COLOR, 
                            insertbackground=TEXT_COLOR, relief=FLAT, highlightthickness=1, 
                            highlightbackground=BORDER_COLOR)
        self.e_pref.pack(side=LEFT, padx=(0, 16))
        
        self.l_suff = Label(rn, font=FONT_LABEL, bg=BG_COLOR, fg=TEXT_COLOR)
        self.l_suff.pack(side=LEFT, padx=(0, 4))
        self.e_suff = Entry(rn, font=FONT_DEFAULT, width=16, bg=INPUT_BG, fg=TEXT_COLOR, 
                            insertbackground=TEXT_COLOR, relief=FLAT, highlightthickness=1, 
                            highlightbackground=BORDER_COLOR)
        self.e_suff.insert(0, DEFAULT_SUFFIX)
        self.e_suff.pack(side=LEFT)

        self.var_ovr = IntVar(value=0)
        self.chk_ovr = Checkbutton(self.lf_name, variable=self.var_ovr, font=FONT_LABEL, bg=BG_COLOR, fg=TEXT_COLOR, selectcolor=INPUT_BG, anchor='w', command=self._toggle_ovr)
        self.chk_ovr.pack(fill=X, pady=(8, 0))

        # ACTION BUTTONS
        fa = Frame(self.root, bg=BG_COLOR)
        fa.pack(fill=X, padx=20, pady=10)
        self.b_start = Button(fa, command=self._start, font=FONT_BUTTON_ACTION, relief=FLAT, pady=8)
        self.b_start.pack(side=LEFT, fill=X, expand=True, padx=(0, 6))
        self.b_stop = Button(fa, command=self._stop, font=FONT_BUTTON_ACTION, relief=FLAT, pady=8)
        self.b_stop.pack(side=LEFT, fill=X, expand=True, padx=6)
        self.b_log = Button(fa, command=self._open_log, font=FONT_BUTTON_ACTION, relief=FLAT, pady=8, bg=BUTTON_BG, fg=TEXT_COLOR)
        self.b_log.pack(side=LEFT, fill=X, expand=True, padx=(6, 0))

        # PROGRESS BAR & STATUS
        self.pbar = ttk.Progressbar(self.root, mode="determinate")
        self.pbar.pack(fill=X, padx=20, pady=(6, 2))
        self.l_stat = Label(self.root, font=FONT_PROGRESS, bg=BG_COLOR, fg=TEXT_MUTED_COLOR)
        self.l_stat.pack(pady=4)

        # LOG BOX
        self.lf_log = ttk.LabelFrame(self.root, padding=10)
        self.lf_log.pack(fill=BOTH, expand=True, padx=20, pady=(4, 16))
        scr = Scrollbar(self.lf_log, bg=CARD_BG, troughcolor=BG_COLOR, bd=0)
        scr.pack(side=RIGHT, fill=Y)
        self.txt = Text(self.lf_log, wrap="word", yscrollcommand=scr.set, font=FONT_LOG, bg=INPUT_BG, fg="#d1d5db", insertbackground=TEXT_COLOR, relief=FLAT)
        self.txt.pack(side=LEFT, fill=BOTH, expand=True)
        scr.config(command=self.txt.yview)
        self.txt.tag_config('INFO', foreground='#e6e8eb')
        self.txt.tag_config('WARN', foreground='#f39c12')
        self.txt.tag_config('ERROR', foreground='#e74c3c', font=(FONT_LOG[0], FONT_LOG[1], "bold"))

    def _set_lang(self, l: str):
        self.lang = l
        if l == "IT":
            self.btn_it.config(bg=ACCENT_COLOR, fg=ACCENT_FG)
            self.btn_en.config(bg=BUTTON_BG, fg=TEXT_MUTED_COLOR)
        else:
            self.btn_en.config(bg=ACCENT_COLOR, fg=ACCENT_FG)
            self.btn_it.config(bg=BUTTON_BG, fg=TEXT_MUTED_COLOR)
        self._update_texts()
        
    def _update_texts(self):
        t = LANG[self.lang]
        self.lbl_title.config(text=t["title"])
        self.nb.tab(0, text=t["tab1"])
        self.nb.tab(1, text=t["tab2"])
        
        self.lf_inout.config(text=t["f_in_out"])
        self.lf_act.config(text=t["f_action"])
        self.lf_ff.config(text=t["f_ffmpeg"])
        self.lf_ext.config(text=t["f_ext"])
        self.lf_name.config(text=t["f_naming"])
        self.lf_log.config(text=t["log_title"])

        v_in = self.val_in if self.val_in else t["not_selected"]
        self.lbl_in.config(text=f"{t['lbl_in']}: {v_in}")
        
        if self.var_ovr.get() == 1:
            v_out = t["same_as_in"]
        else:
            v_out = self.val_out if self.val_out else t["not_selected"]
        self.lbl_out.config(text=f"{t['lbl_out']}: {v_out}")
        
        v_ff = self.val_ff if self.val_ff else t["ff_not_selected"]
        self.lbl_ff.config(text=f"{t['lbl_ffmpeg']}: {v_ff}")
        
        self.btn_in.config(text=t["btn_browse_dir"])
        self.btn_out.config(text=t["btn_browse_dir"])
        self.btn_ff.config(text=t["btn_browse_file"])
        self.b_start.config(text=t["btn_start"])
        self.b_stop.config(text=t["btn_stop"])
        self.b_log.config(text=t["btn_log"])
        
        self.l_pref.config(text=t["lbl_pref"])
        self.l_suff.config(text=t["lbl_suff"])
        self.chk_aud.config(text=t["chk_audio"])
        self.chk_ovr.config(text=t["chk_overwrite"])
        
        if not self.processor.interrompi and self.pbar["value"] == 0:
            self.l_stat.config(text=t["waiting"])

        idx = self.combo.current() if self.combo.current() >= 0 else 0
        vals = [t[k] for k in ACTION_KEYS]
        self.combo.config(values=vals)
        self.combo.current(idx)

    def _pick_dir(self, target):
        t = LANG[self.lang]
        d = filedialog.askdirectory(title=t["msg_in_prompt"] if target=='in' else t["msg_out_prompt"])
        if d:
            if target == 'in':
                self.val_in = d
            else:
                self.val_out = d
        self._update_texts()
        self._aggiorna_stato_avvia()

    def _pick_ff(self):
        t = LANG[self.lang]
        p = filedialog.askopenfilename(title=t["msg_ff_prompt"])
        if p:
            self.val_ff = p
        self._update_texts()
        self._aggiorna_stato_avvia()

    def _toggle_ovr(self):
        t = LANG[self.lang]
        if self.var_ovr.get() == 1:
            self.btn_out.config(state=DISABLED)
            messagebox.showinfo("Info", t["msg_overwrite_on"])
        else:
            self.btn_out.config(state=NORMAL)
            messagebox.showinfo("Info", t["msg_overwrite_off"])
        self._update_texts()
        self._aggiorna_stato_avvia()

    def _aggiorna_stato_avvia(self):
        ok = bool(self.val_in) and (bool(self.val_out) or self.var_ovr.get() == 1)
        if self.val_ff:
            ok = ok and self.processor.verifica_ffmpeg(self.val_ff)
        if ok:
            self.b_start.config(state=NORMAL, bg=ACCENT_COLOR, fg=ACCENT_FG)
        else:
            self.b_start.config(state=DISABLED, bg=BUTTON_DISABLED_BG, fg=BUTTON_DISABLED_FG)

    def _open_log(self):
        t = LANG[self.lang]
        if not self.val_in:
            messagebox.showinfo("Info", t["msg_no_log"])
            return
        p = os.path.join(self.val_in, ERROR_LOG_FILENAME)
        if os.path.exists(p):
            webbrowser.open(p)
        else:
            messagebox.showinfo("Info", t["msg_no_log"])

    def _enable_ui(self, en: bool):
        st = NORMAL if en else DISABLED
        self.b_start.config(state=st)
        self.b_stop.config(state=NORMAL if not en else DISABLED, bg=WARN_COLOR if not en else WARN_DISABLED_COLOR, fg=ACCENT_FG if not en else BUTTON_DISABLED_FG)
        self.btn_in.config(state=st)
        self.btn_out.config(state=st if not self.var_ovr.get() else DISABLED)
        self.btn_ff.config(state=st)
        self.e_pref.config(state=st)
        self.e_suff.config(state=st)
        self.chk_ovr.config(state=st)
        self.combo.config(state="readonly" if en else DISABLED)
        self.chk_aud.config(state=st)
        if en:
            self._aggiorna_stato_avvia()

    def _stop(self):
        t = LANG[self.lang]
        if messagebox.askyesno("Stop", t["msg_confirm_stop"]):
            self.processor.interrompi = True
            self.b_stop.config(state=DISABLED, bg=WARN_DISABLED_COLOR)
            self.l_stat.config(text=t["interrupted"], fg=WARN_INTERRUPT_FG)

    def _start(self):
        t = LANG[self.lang]
        if not self.val_in:
            messagebox.showerror(t["err"], t["msg_in_err"])
            return
        if not self.var_ovr.get() and not self.val_out:
            messagebox.showerror(t["err"], t["msg_out_err"])
            return

        exts = [k for k, v in self.vars_ext.items() if v.get()]
        idx = self.combo.current()
        opz = {
            "in_d": self.val_in,
            "out_d": self.val_in if self.var_ovr.get() else self.val_out,
            "ff": self.val_ff if self.val_ff else "ffmpeg",
            "exts": exts,
            "pref": self.e_pref.get().strip(),
            "suff": self.e_suff.get().strip(),
            "ovr": self.var_ovr.get() == 1,
            "act": ACTION_INTERNAL_MAP[ACTION_KEYS[idx]],
            "rm_aud": self.var_aud.get() == 1
        }
        
        if opz["ovr"] and not messagebox.askyesno("Conferma", t["msg_overwrite_warn"]):
            return
        
        self._enable_ui(False)
        self.pbar["value"] = 0
        self.txt.delete(1.0, END)
        self.root.config(cursor="watch")
        
        def _cb_prog(c, tot, nm):
            self.root.after(0, lambda: self.pbar.config(value=0))
            self.root.after(0, lambda: self.l_stat.config(text=t["processing"].format(current=c, total=tot, filename=nm), fg=TEXT_COLOR))
        
        def _cb_file(p):
            self.root.after(0, lambda: self.pbar.config(value=max(0, min(100, p))))

        def _run():
            try:
                t_files, elab, space, errs = self.processor.avvia(t, opz, _cb_prog, _cb_file, self.txt)
                self.root.after(0, lambda: self._post_run(t, t_files, elab, space, errs))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(t["err"], f"{e}"))
                self.root.after(0, lambda: self._enable_ui(True))
                self.root.after(0, lambda: self.root.config(cursor=""))

        Thread(target=_run, daemon=True).start()

    def _post_run(self, t, tot, elab, spc, errs):
        rep = f"\n[{datetime.now().strftime('%H:%M:%S')}] {t['rep_final']}\n"
        rep += f"{t['rep_found']}: {tot} | {t['rep_done']}: {elab}\n"
        rep += f"{t['rep_saved']}: {spc:.2f} MB\n"

        if self.processor.interrompi:
            self.l_stat.config(text=t["interrupted"], fg=WARN_INTERRUPT_FG)
            messagebox.showinfo("Info", t["msg_stop_info"])
        elif errs:
            self.l_stat.config(text=f"{t['err']} ({len(errs)})", fg=WARN_INTERRUPT_FG)
            messagebox.showerror("Error", f"{len(errs)} {t['err']}. Log: {ERROR_LOG_FILENAME}")
        else:
            self.l_stat.config(text=t["completed"], fg=SUCCESS_COLOR)
            messagebox.showinfo("OK", t["completed"])

        self.txt.insert(END, rep, "INFO")
        self.txt.see(END)
        self.pbar["value"] = 100 if not self.processor.interrompi and not errs else 0
        self._enable_ui(True)
        self.root.config(cursor="")

if __name__ == "__main__":
    root = Tk()
    app = AppGUI(root)
    root.mainloop()
