# Positron

A tiny **Electron-like** runtime built with **Python + pywebview**.

- Serves files from `./www` at `http://127.0.0.1:7000`
- Opens a native window that loads that URL
- **Persistence** (localStorage/cookies/IndexedDB) per bundle
- **Download helper**: moves files from Downloads with *Save As…* dialog  
  - asks if you want to overwrite  
  - auto-renames if you say no  
  - deletes the file if you cancel the dialog  
- **Self-extracting bundle**: a single file that extracts `positron` + `www` to a temporary folder and runs the app
- **Cross-platform**: Linux, Windows, macOS

---

## Project structure

```

.
├── positron            # runner (Python script / executable)
├── make\_bundle         # creates self-extracting bundle
├── www/                # your web app (index.html, css, js, …)
└── requirements.txt    # Python dependencies (pywebview)

````

---

## Requirements

### Common

- Python 3.9+ recommended (3.8+ usually works)  
- `pywebview`:

```bash
pip install -r requirements.txt
# or
pip install pywebview
````

### Linux

* Backend **GTK/WebKit2** (recommended) **or** **Qt WebEngine**

Debian/Ubuntu/Mint:

```bash
sudo apt install python3-gi gir1.2-webkit2-4.1 libwebkit2gtk-4.1-0
# if 4.1 is missing:
sudo apt install python3-gi gir1.2-webkit2-4.0 libwebkit2gtk-4.0-37
```

Alternative Qt backend:

```bash
pip install PyQt5 PyQtWebEngine
```

Arch/Fedora: install `webkit2gtk` + `python-gobject`, or Qt packages.

### Windows

* `pip install pywebview`
* **Microsoft Edge WebView2 Runtime** (usually preinstalled on Win10/11).
* Alternatively: `pip install PyQt5 PyQtWebEngine` and run with `--gui qt`.

⚠️ Do **not** install the package `webview` (different project). Use **`pywebview`**.

### macOS

* `pip install pywebview pyobjc`
* Alternatively: `pip install PyQt5 PyQtWebEngine` and run with `--gui qt`.

---

## Quick start (without bundle)

```bash
# Linux/macOS
python3 positron

# Windows
py positron
```

A window opens on `http://127.0.0.1:7000` serving files from `./www`.
On first run, a default `www/index.html` is created.

---

## Useful options

```bash
# window size and position
./positron --size 1200x800 --pos 100,50

# minimum size
./positron --min-size 800x600

# fullscreen
./positron --fullscreen

# non-resizable
./positron --fixed

# force backend
./positron --gui gtk           # Linux GTK/WebKit
./positron --gui qt            # Qt WebEngine (all platforms)
./positron --gui edgechromium  # Windows WebView2
./positron --gui cocoa         # macOS Cocoa/WebKit

# debug console
./positron --debug
```

---

## Creating a self-extracting bundle

```bash
# Linux/macOS
./make_bundle --positron ./positron --www ./www --out ./myapp

# Windows (.pyw recommended for double-click without console)
py make_bundle.py --positron .\positron --www .\www --out .\myapp.pyw
```

Run:

```bash
# Linux/macOS
./myapp --size 1200x800 --pos 100,50

# Windows
pyw myapp.pyw --size 1200x800 --gui edgechromium
# if a .bat wrapper was created
myapp.bat --size 1200x800 --gui edgechromium
```

> The bundle forwards **all CLI arguments** to the inner runner.

---

## Persistence (localStorage/IndexedDB)

* Enabled in the runner with `private_mode=False` and `storage_path` per bundle.
* Data stored in:

  * Linux/macOS: `~/.positron/<bundle-name>`
  * Windows: `C:\Users\<User>\.positron\<bundle-name>`
* Always use the same origin (`http://127.0.0.1:7000`) for persistence.

---

## Download watcher

* Watches your system’s default **Downloads** directory
* Detects finished files (`.part`, `.crdownload`, etc. are ignored)
* Opens a **Save As…** dialog:

  * If file exists → asks to overwrite
  * If you click *No* → renames as `file (1).ext`
  * If you *cancel* → file is **deleted** from Downloads

---

## Window title

Default = bundle filename.
Override with env var:

```bash
POSITRON_TITLE="Custom Title" ./myapp
```

---

## Environment variables

* `POSITRON_TITLE` – force window title
* `POSITRON_KEEP=1` – don’t delete extracted temp dir after exit
* `POSITRON_DEBUG=1` – enable pywebview debug mode
* `POSITRON_VERBOSE=1` – extra logs from stub

---

## Packaging into native executables

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

Alternative with py2app:

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

## Troubleshooting

* **`ModuleNotFoundError: No module named 'webview'`**
  → Wrong package. Use `pywebview`, not `webview`.

  ```bash
  pip uninstall -y webview
  pip install pywebview
  ```

* **JavaScript doesn’t run / `evaluate_js` fails**
  → Install a backend with JS support:

  * Linux: WebKit2 (`python3-gi + webkit2gtk`) or Qt (`PyQt5 + PyQtWebEngine`)
  * Windows: Edge WebView2 Runtime or Qt
  * macOS: `pyobjc` (Cocoa/WebKit) or Qt

* **LocalStorage/IndexedDB doesn’t persist**
  → Ensure `private_mode=False` and `storage_path` set
  → Use consistent origin (`http://127.0.0.1:7000`)

* **Windows: “not a valid Win32 application”**
  → `.pyw` file is not an `.exe`.

  * Launch with `py myapp.pyw`
  * Double-click `.pyw`
  * Or build `.exe` with PyInstaller

---

## Security

* HTTP server binds only to **127.0.0.1** (loopback).
* Bundle extracts to a unique temporary folder and cleans up on exit (unless `POSITRON_KEEP=1`).

---

## License

MIT (or any you choose).

---

## Why Positron?

Because it’s **tiny**, **simple**, and already **cross-platform**:
Write HTML/CSS/JS in `www/`, and you have a desktop app with persistence, file download handling, and single-file packaging.
