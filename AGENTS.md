# Positron contributor guide

## Project scope

Positron is a small Python and pywebview runtime for static HTML applications and
React/Vite development servers. It also exposes a native file-saving API and can
watch completed downloads. Keep changes focused: the project intentionally uses
the Python standard library where possible and has no application framework
beyond pywebview.

Read `README.md` before changing public behavior, setup steps, CLI options, or
packaging.

## Repository map

- `positron`: main Python entrypoint. Static mode serves `www/` on
  `127.0.0.1:7000`; React mode starts `npm run dev` from the project root.
- `make_bundle`: creates a self-extracting Python launcher containing the runner
  and a selected `www/` directory.
- `www/`: source for the bundled Memory example.
- `memory`, `memory.py`, and `memory.pyw`: generated Memory bundles.
- `positron-hello`: generated hello example with its own embedded web payload.
- `positron.tar.xz`: generated source distribution.
- `install`: POSIX setup and launch helper.
- `tests/test_project.py`: regression and artifact-consistency tests.
- `.venv/`: local environment; never commit it.

The extensionless Python entrypoints are intentional. Do not rename them to
`.py` without updating the CLI documentation, bundle stub, tests, and artifacts.

## Runtime invariants

- Static HTTP traffic stays bound to loopback. Do not expose it to the LAN by
  default.
- Static apps use port 7000 so their browser origin remains stable.
- Persistent browser data stays under `~/.positron/<bundle-name>` with
  `private_mode=False`.
- React server output must be consumed while the process runs. Use the URL
  reported by the server, do not attach to a port that was already occupied,
  and always stop the complete process tree when the window closes.
- A bundle must store its runner as `positron`, regardless of the input
  filename, because the extraction stub looks for that name.
- `window.pywebview.api.save_file` must always require a user-selected native
  destination. The download watcher deletes a new source download when the user
  cancels; tests for it must use a temporary `--watch-dir`, never the real
  Downloads directory.
- Generated executables and directories use mode 755; regular project files use
  mode 644. Do not restore group or world write access.

## Change workflow

For a bug fix, add or update a regression test first, confirm it fails for the
expected reason, then make the smallest implementation change that passes it.

Use these paths for common changes:

- Runtime, CLI, server, window, or persistence behavior: edit `positron`.
- Bundle layout or extraction behavior: edit `make_bundle`.
- Memory UI or game logic: edit `www/index.html`, then rebuild both Memory
  bundles.
- Installation or platform requirements: edit `install`, `requirements.txt`,
  and the matching README section together.

Do not edit base64 payloads inside generated bundles by hand. Rebuild Memory
artifacts with:

```bash
./make_bundle --positron ./positron --www ./www --out ./memory
./make_bundle --positron ./positron --www ./www --out ./memory.py
./make_bundle --positron ./positron --www ./www --out ./memory.pyw
```

When refreshing only the runner in `positron-hello`, preserve its existing
embedded `www/` payload. Rebuild the source archive with:

```bash
tar -cJf positron.tar.xz requirements.txt positron make_bundle install README.md LICENSE
chmod 644 positron.tar.xz
```

After changing `positron`, refresh every generated artifact. The regression
suite verifies that each artifact embeds the current runner.

## Verification

Run the complete automated suite:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v
```

Run syntax and smoke checks relevant to the files changed:

```bash
PYTHONPYCACHEPREFIX=/tmp/positron-pycache .venv/bin/python -m py_compile positron make_bundle tests/test_project.py
bash -n install
sed -n '/<script>/,/<\/script>/p' www/index.html | sed '1d;$d' | node --check -
./positron --help
./memory --help
./positron-hello --help
```

The React integration test requires `npm`; it is skipped when npm is absent.
On Linux, also verify that the selected pywebview backend imports from the
virtual environment when setup instructions change.

## Completion criteria

A change is complete when its regression test passes, relevant syntax and smoke
checks pass, generated artifacts are synchronized, permissions remain safe, and
`README.md` reflects every user-visible workflow or behavior change.
