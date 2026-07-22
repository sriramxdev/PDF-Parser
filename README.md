# 📄 PDF Parser

A clean, modern, and production-ready Web UI built with **Streamlit** and **PyMuPDF** for extracting structured text, detailed page metrics, and metadata from PDF files into standardized JSON format. Ready for 1-click deployment on **Streamlit Community Cloud**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=flat-square&logo=streamlit)
![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.24%2B-red?style=flat-square)
![License](https://img.shields.io/badge/License-AGPLv3-blue?style=flat-square)

---

## ✨ Features

- **🎨 Native Dual-Theme Web UI**: Auto-adapts to system light/dark mode out of the box.
- **🛡️ Multi-Layer File Validation**:
  - File uploader restrictions (`.pdf` only).
  - Maximum size cap (`25 MB` limit) to preserve memory runtime.
  - **Magic Header Check**: Verifies `%PDF-` bytes to block non-PDF files disguised with a `.pdf` extension.
- **🔒 Encrypted & Corrupted PDF Protection**: Gracefully catches password-protected files, 0-byte files, and broken structures into JSON error responses without crashing the app.
- **📊 Comprehensive Extraction**:
  - Document-level metadata (Title, Author, Subject, Creation Date, Producer).
  - Page-level breakdown (Exact word count, character count, and raw text).
  - Handles scanned/empty pages safely.
- **📥 One-Click JSON Download**: View interactive tree-structured JSON and download formatted `.json` files directly.

---

## 📂 Repository Structure

```text
.
├── .streamlit/
│   └── config.toml     # Custom theme configuration
├── app.py              # Main Streamlit application
├── requirements.txt    # Dependencies
├── LICENSE             # GNU AGPLv3 License
└── README.md           # Documentation
