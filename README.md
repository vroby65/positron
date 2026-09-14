

# 🪐 Positron

A tiny **Electron-like runtime** built with **Python + pywebview**.

- Serves files from `./www` at `http://127.0.0.1:7000`

- Opens a native window that loads that URL

- Supports both **static HTML apps** and **React/Vite dev servers**

- **Persistent storage** (localStorage / cookies / IndexedDB) per bundle

- Native `save_file` API and optional Downloads watcher with a **Save As** dialog

- **Self-extracting bundle**: one single file that extracts `positron` + `www` to a temporary folder and runs automatically

- **Cross-platform**: Linux, Windows, macOS

---

## 📁 Project structure

```
.
├── positron            # main runner (Python script / executable)
├── make_bundle         # creates self-extracting bundle
├── www/                # your web app (index.html, css, js, …)
└── requirements.txt    # Python dependencies (pywebview)
```

---

## ⚙️ Requirements

### Common

- **Python 3.9+** recommended (3.8+ often works)

- **pywebview**:

```bash
python3 -m venv --system-site-packages .venv
. .venv/bin/activate
pip install -r requirements.txt
# or
pip install pywebview
```

---

### Linux

Backend options:

- ✅ **GTK/WebKit2** (recommended)

- ⚙️ or **Qt WebEngine**

For Debian / Ubuntu / Mint:

```bash
sudo apt install python3-gi gir1.2-webkit2-4.1 libwebkit2gtk-4.1-0
# if 4.1 is not available:
sudo apt install python3-gi gir1.2-webkit2-4.0 libwebkit2gtk-4.0-37
```

Alternative Qt backend:

```bash
pip install PyQt5 PyQtWebEngine
```

On Arch / Fedora: install `webkit2gtk` + `python-gobject`, or the Qt packages.

---

### Windows

- `pip install pywebview`

- Requires **Microsoft Edge WebView2 Runtime** (preinstalled on Win10/11)

- Or use Qt backend:

  ```bash
  pip install PyQt5 PyQtWebEngine
  ./positron --gui qt
  ```

⚠️ **Important:** Do *not* install the package `webview` — it’s a different project.
Use **`pywebview`**.

---

### macOS

```bash
pip install pywebview pyobjc
# or
pip install PyQt5 PyQtWebEngine
```

Run with `--gui qt` if you prefer Qt WebEngine.

---

## 🚀 Quick start (without bundling)

```bash
# Linux/macOS
python3 positron

# Windows
py positron
```

A native window opens at `http://127.0.0.1:7000` serving files from `./www`.
On first run, a default `www/index.html` will be created automatically.

---

## 🧭 Useful options

```bash
# window size and position
./positron --size 1200x800 --pos 100,50

# minimum size
./positron --min-size 800x600

# fullscreen
./positron --fullscreen

# non-resizable
./positron --fixed

# choose backend
./positron --gui gtk           # Linux GTK/WebKit
./positron --gui qt            # Qt WebEngine (cross-platform)
./positron --gui edgechromium  # Windows WebView2
./positron --gui cocoa         # macOS Cocoa/WebKit

# enable debug console
./positron --debug

# override browser profile or watched download directory
./positron --profile-dir ~/.positron/my-profile
./positron --watch-dir ~/Downloads
```

---

## ⚛️ React / Vite support

Positron automatically detects a **React/Vite project** if a `package.json` file exists.

| Scenario              | Behavior                                                                                |
| --------------------- | --------------------------------------------------------------------------------------- |
| `www/index.html` only | Serves static files at `http://127.0.0.1:7000`                                          |
| `package.json` exists | Runs `npm run dev` and connects to the URL reported by the dev server                    |
| `--react` flag        | Forces React/Vite mode even without detection                                           |

```bash
# example: run Vite + React app
./positron --react
```

If `node_modules` are missing, Positron automatically runs `npm install` before starting the dev server.

---

## 💾 Native file saving and download watcher

Pages can open a native **Save As** dialog through the pywebview bridge:

```javascript
const result = await window.pywebview.api.save_file("notes.txt", "Hello");
```

Positron also watches the system Downloads directory, or the directory selected
with `--watch-dir`. Completed downloads open a **Save As** dialog. Existing
destinations require confirmation; declining creates a numbered filename.
Cancelling deletes the newly downloaded source file.

---

## 📦 Creating a self-extracting bundle

Bundle your app into a **single Python file** that unpacks itself on launch.

```bash
# Linux/macOS
./make_bundle --positron ./positron --www ./www --out ./myapp

# Windows (.pyw recommended for double-click without console)
py .\make_bundle --positron .\positron --www .\www --out .\myapp.pyw
```

Then run:

```bash
# Linux/macOS
./myapp --size 1200x800 --pos 100,50

# Windows
pyw myapp.pyw --size 1200x800 --gui edgechromium
# or via .bat wrapper (auto-created)
myapp.bat --size 1200x800 --gui edgechromium
```

> The bundle forwards all CLI arguments to the inner `positron` runner.

---

## 📥 Releases

Source archives such as `positron.tar.xz` are published as assets on the
[GitHub Releases page](https://github.com/vroby65/positron/releases) and are not
stored in the repository.

---

## 💾 Persistent storage

- Each app keeps its own persistent data (localStorage, cookies, IndexedDB).

- Persistence is handled by pywebview (`private_mode=False`, `storage_path` per bundle).

Stored under:

- **Linux/macOS:** `~/.positron/<bundle-name>`

- **Windows:** `C:\Users\<User>\.positron\<bundle-name>`

Static apps always use `http://127.0.0.1:7000`. React/Vite storage belongs to the port chosen by its dev server.

---

## 🧰 Environment variables

| Variable             | Description                                |
| -------------------- | ------------------------------------------ |
| `POSITRON_TITLE`     | Custom window title                        |
| `POSITRON_KEEP=1`    | Keep extracted temp dir after exit         |
| `POSITRON_DEBUG=1`   | Enable pywebview debug mode                |
| `POSITRON_VERBOSE=1` | Verbose logs from the self-extracting stub |
| `POSITRON_PROFILE_DIR` | Override the browser storage directory   |

Example:

```bash
POSITRON_TITLE="My Cool App" ./myapp
```

---

## 🛠 Packaging into native executables

### Windows (.exe)

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed `
  --name MyApp `
  --collect-all webview `
  --hidden-import webview `
  myapp.pyw
```

### macOS (.app)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name MyApp --collect-all webview myapp
```

Alternative with **py2app**:

```bash
pip install py2app
python setup.py py2app
```

### Linux

```bash
pip install pyinstaller
pyinstaller --onefile --name myapp --collect-all webview positron
```

---

## 🧩 Security model

- The HTTP server binds only to **127.0.0.1** (loopback only).

- Self-extracting bundles unpack to a unique random temp directory.

- The temp directory is deleted automatically when the app exits (unless `POSITRON_KEEP=1`).

---

## 🚑 Troubleshooting

### “`ModuleNotFoundError: No module named 'webview'`”

You installed the wrong package.
Run:

```bash
pip uninstall -y webview
pip install pywebview
```

### JavaScript or `evaluate_js` not working

Install a backend that supports JS:

- Linux: WebKit2 (`python3-gi + webkit2gtk`) or Qt (`PyQt5 + PyQtWebEngine`)

- Windows: Edge WebView2 Runtime or Qt backend

- macOS: `pyobjc` (Cocoa/WebKit) or Qt backend

### LocalStorage / IndexedDB doesn’t persist

Ensure `private_mode=False` and `storage_path` are set, and always use `http://127.0.0.1:7000`.

### “Not a valid Win32 application”

`.pyw` files are not `.exe`.
Use:

- `py myapp.pyw`

- Double-click `.pyw`

- Or build an `.exe` with PyInstaller

---

## 🧠 Why Positron?

Because it’s **tiny**, **clean**, and already **cross-platform**.
Write your UI once (HTML/CSS/JS in `www/`), and get:

- Native window + persistence

- Local HTTP serving

- Optional React/Vite integration

- One-file packaging via `make_bundle`

💡 It’s like Electron — but 100× smaller and pure Python.

---

## 🪪 License

MIT. See [`LICENSE`](LICENSE).

---
