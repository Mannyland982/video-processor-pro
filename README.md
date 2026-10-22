# Video Processor Pro

A multi-threaded desktop GUI for batch video transcoding, resolution downscaling, and audio stripping powered by **FFmpeg**. Features hardware acceleration via NVIDIA NVENC and Intel QuickSync, atomic file writes to prevent corruption, custom naming rules, dark mode, and runtime bilingual support (English / Italian).

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![FFmpeg Dependency](https://img.shields.io/badge/dependency-FFmpeg-red)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- **Hardware Acceleration:** Choose between NVIDIA NVENC (`h264_nvenc`), Intel QSV (`h264_qsv`), or CPU (`libx264`) for rendering speeds up to 10x faster.
- **Direct Stream Copy:** Ultra-fast remuxing without re-encoding when audio removal or container repacking is needed.
- **10-bit / HDR Fix:** Automatically converts high-bit-depth video profiles to standard 8-bit `yuv420p` for maximum playback compatibility across older hardware.
- **Audio Track Stripping:** Toggle audio removal (`-an`) with a single click across any batch job.
- **Atomic File Writing:** Converts files into isolated temporary buffers (`.tmp`) before moving them to the destination path, ensuring no file corruption if aborted or interrupted.
- **Flexible Naming Rules:** Fully customize file prefixes and suffixes or leave them blank.
- **Safe In-Place Overwrites:** Optional mode to directly replace original video files in source directories.
- **Bilingual Interface:** Real-time toggle between Italian (`ITA`) and English (`ENG`).
- **Dark Mode UI:** Modern dark aesthetic with native Windows 10/11 dark title bar support.

---

## 📋 Prerequisites

1. **Python 3.9+** (uses the Python standard library; no extra pip packages required).
2. **FFmpeg & FFprobe:** 
   - Ensure `ffmpeg` and `ffprobe` are added to your system `PATH`, or browse to the executable directly from the **Advanced Settings** tab inside the app.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone [https://github.com/Mannyland982/video-processor-pro.git](https://github.com/Mannyland982/video-processor-pro.git)
cd video-processor-pro

🎯 Conversion PresetsPresetEncoderRecommended Use CaseCompress 1080p / 720p (NVIDIA)h264_nvencMaximum compression speed on NVIDIA GeForce/RTX GPUsCompress 1080p / 720p (Intel)h264_qsvFast hardware compression on Intel CPUs with integrated graphicsCompress 1080p / 720p (CPU)libx264Maximum compression efficiency and image quality (software encoding)Copy Video StreamcopyInstant remuxing or audio removal without re-encoding video
