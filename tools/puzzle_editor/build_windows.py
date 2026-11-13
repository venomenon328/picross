"""Portable, windowed and fully bound PE bundle. Run from a clean source commit."""
import argparse
import hashlib
import importlib.metadata as metadata
import json
import platform
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from . import VERSION

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).parent


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def build(output):
    if sys.platform != "win32" or platform.python_version() != "3.13.14" or platform.machine().lower() not in ("amd64", "x86_64"):
        raise ValueError("CPython 3.13.14 Windows x64 erforderlich.")
    import tkinter
    import PIL
    if tkinter.Tcl().eval("info patchlevel") != "8.6.15" or PIL.__version__ != "12.3.0":
        raise ValueError("Tcl/Tk 8.6.15 und Pillow 12.3.0 erforderlich.")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT).strip():
        raise ValueError("Bau benötigt einen sauberen, vollständig committeten Programmstand.")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    output = output.absolute()
    if output.exists() or output.is_relative_to(ROOT): raise ValueError("Neues Ausgabeziel außerhalb des Programms wählen.")
    versions = {}
    for line in (PACKAGE/"requirements-windows.txt").read_text().splitlines():
        if not line or line.startswith("#"): continue
        name, expected = line.split("==")
        if metadata.version(name) != expected: raise ValueError("Abhängigkeit passt nicht: "+name)
        versions[name] = expected
    output.mkdir(parents=True)
    work = output/"build"; work.mkdir()
    source = ROOT/"tools/puzzle_production"
    source_data = work/"puzzle_production"; source_data.mkdir()
    # Frozen methods verify real .py/JSON bytes; include those exact trusted sources.
    for file in source.iterdir():
        if file.is_file() and file.suffix in (".py", ".json", ".md"):
            shutil.copyfile(file, source_data/file.name)
    env = os.environ.copy()
    env["PYINSTALLER_CONFIG_DIR"] = str(work/"cache")
    subprocess.run([sys.executable, "-m", "PyInstaller", "--clean", "--noconfirm", "--onedir", "--windowed", "--noupx",
        "--name", "Picross-Bestandseditor", "--distpath", str(output/"dist"), "--workpath", str(work/"pyinstaller"),
        "--specpath", str(work), "--paths", str(ROOT), "--collect-submodules", "tools.puzzle_production",
        "--hidden-import", "tools.puzzle_editor.worker", "--hidden-import", "tkinter.filedialog", "--hidden-import", "tkinter.messagebox",
        "--add-data", str(PACKAGE/"ui")+":tools/puzzle_editor/ui",
        "--add-data", str(source_data)+":tools/puzzle_production", str(PACKAGE/"desktop_entry.py")], check=True, cwd=ROOT, env=env)
    app = output/"dist/Picross-Bestandseditor"
    required = ["Picross-Bestandseditor.exe", "_internal/python313.dll", "_internal/_tkinter.pyd",
                "_internal/tools/puzzle_editor/ui/index.html", "_internal/tools/puzzle_editor/ui/app.js",
                "_internal/tools/puzzle_editor/ui/style.css", "_internal/tools/puzzle_production/sd2_method_0_4.json"]
    for name in required:
        if not (app/name).is_file(): raise ValueError("Unvollständiges Bundle: "+name)
    from PyInstaller.archive.readers import ZlibArchiveReader
    modules = set(ZlibArchiveReader(str(work/"pyinstaller/Picross-Bestandseditor/PYZ-00.pyz")).toc)
    for name in ("tools.puzzle_editor.server", "tools.puzzle_editor.worker", "tools.puzzle_editor.desktop",
                 "tools.puzzle_production.catalog_metadata", "tools.puzzle_production.catalog_images", "tools.puzzle_production.catalog_raster", "PIL.Image", "tkinter"):
        if name not in modules: raise ValueError("Frozen-Modul fehlt: "+name)
    for file in source_data.iterdir():
        if sha(file) != sha(app/"_internal/tools/puzzle_production"/file.name): raise ValueError("Geänderte Fachquelle im Bundle.")
    licenses = app/"LICENSES"; licenses.mkdir()
    shutil.copyfile(Path(sys.base_prefix)/"LICENSE.txt", licenses/"Python.txt")
    # Existing unchanged official runtime licenses, no PW program or update dependency.
    for name in ("Tcl-8.6.15.txt", "OpenSSL-3.0.21.txt", "Expat-2.8.1.txt", "zlib-1.3.1.txt", "bzip2-1.0.8.txt", "xz-5.2.5.txt", "mpdecimal-4.0.0.txt"):
        shutil.copyfile(ROOT/"tools/production_workspace/licenses"/name, licenses/name)
    for file in (Path(sys.base_prefix)/"tcl/tk8.6").glob("*license*"):
        shutil.copyfile(file, licenses/("Tk-"+file.name+".txt"))
    if not list(licenses.glob("Tk-*")): raise ValueError("Tk-Original-Lizenz fehlt.")
    for name in ("Pillow", "PyInstaller"):
        dist = metadata.distribution(name); copied = False
        for file in dist.files:
            path = str(file).replace("\\", "/")
            if ".dist-info/licenses/" in path:
                target = licenses/name/path.split("licenses/", 1)[1]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(dist.locate_file(file), target); copied = True
        if not copied: raise ValueError("Lizenzinventar fehlt: "+name)
    shutil.copyfile(PACKAGE/"README.md", app/"START.md")
    components = {"format": "picross-pe-build-v1", "version": VERSION, "commit": commit,
                  "python": platform.python_version(), "tk": tkinter.Tcl().eval("info patchlevel"), "dependencies": versions}
    (app/"components.json").write_text(json.dumps(components, indent=2)+"\n", encoding="utf-8")
    files = [{"file": p.relative_to(app).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(app.rglob("*")) if p.is_file()]
    (app/"inventory.json").write_text(json.dumps({"commit": commit, "files": files}, indent=2)+"\n", encoding="utf-8")
    archive = output/"Picross-Bestandseditor-windows-x64.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as stream:
        for p in sorted(app.rglob("*")):
            if p.is_file(): stream.write(p, "Picross-Bestandseditor/"+p.relative_to(app).as_posix())
    report = {**components, "zip_sha256": sha(archive), "zip_bytes": archive.stat().st_size,
              "exe_sha256": sha(app/"Picross-Bestandseditor.exe"), "files": len(files)}
    (output/"delivery.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, required=True)
    build(parser.parse_args().output)
