"""Exercise real Win32 mouse delivery against a commit-bound exported player.

Uses the existing Python standard library only. OS-injected stimuli are reported
as such; this is never an owner or physical-mouse acceptance claim.
"""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes as w
import json
import os
from pathlib import Path
import platform
import subprocess
import time

import p1_preflight as toolchain

ROOT = Path(__file__).resolve().parents[1]


def probe(player: Path, output: Path, expected_head: str) -> None:
    if platform.system() != "Windows":
        raise RuntimeError("Native Windows required; no simulated substitute")
    report = json.loads((player.parent / "product-report.json").read_text(encoding="utf-8"))
    if report["source_commit"] != expected_head or report["source_tree_dirty"]:
        raise RuntimeError("Expected a clean, commit-bound Product export")
    for name, digest in report["export_files"].items():
        toolchain.verify_sha256(player.parent / name, digest)
    output.mkdir(parents=True, exist_ok=False)
    environment = toolchain.isolated_environment(output / "profile", "Windows")
    environment["ZR_WINDOWS_OUTPUT"] = str(output)
    script = ROOT / "game/tests/zr_windows_probe.gd"
    log = (output / "native.log").open("w", encoding="utf-8")
    process = subprocess.Popen([str(player), "--rendering-driver", "opengl3", "--audio-driver", "Dummy",
                                "--script", str(script), "--", "--p1-capture"],
                               cwd=player.parent, env=environment, stdout=log,
                               stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
    user = ctypes.windll.user32
    user.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    user.ClientToScreen.argtypes = [w.HWND, ctypes.POINTER(w.POINT)]
    user.GetForegroundWindow.restype = w.HWND
    user.SetForegroundWindow.argtypes = [w.HWND]
    user.GetDpiForWindow.argtypes = [w.HWND]
    original_cursor = w.POINT()
    user.GetCursorPos(ctypes.byref(original_cursor))
    command_id = 0
    results = []
    held = set()

    def status(predicate=lambda _: True, timeout=10):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                data = json.loads((output / "status.json").read_text())
                if predicate(data):
                    return data
            except (OSError, ValueError):
                pass
            time.sleep(.05)
        raise RuntimeError("Native state did not reach expected result")

    def command(op, **values):
        nonlocal command_id
        command_id += 1
        temp = output / "command.tmp"
        temp.write_text(json.dumps(dict(id=command_id, op=op, **values)), encoding="utf-8")
        temp.replace(output / "command.json")
        if op != "quit":
            return status(lambda data: data["command_id"] == command_id)

    def move(local):
        if not user.SetCursorPos(origin.x + round(local[0]), origin.y + round(local[1])):
            raise RuntimeError("Native cursor move failed")
        time.sleep(.15)

    def button(right, down):
        # Native Win32 input route; no Input.parse_input_event/Viewport events.
        user.mouse_event((0x8 if down else 0x10) if right else (0x2 if down else 0x4), 0, 0, 0, 0)
        held.add(right) if down else held.discard(right)
        time.sleep(.15)

    def require(condition, label, data):
        results.append(dict(label=label, passed=bool(condition), state=data))
        if not condition:
            raise RuntimeError(label)

    binding = dict(source_commit=expected_head, base_commit=report["base_commit"],
                   tested_checkout_commit=report["tested_checkout_commit"],
                   github_run_id=report.get("github_run_id"), export_files=report["export_files"],
                   platform=platform.platform(), stimulus="Win32 OS-injected mouse, actual native HWND/PCK",
                   owner_ZR_M01="OPEN", physical_mouse_acceptance="OPEN: owner",
                   script_sha256=toolchain.sha256_file(script), results=results)
    try:
        initial = status()
        if any(user.GetAsyncKeyState(key) & 0x8000 for key in (1, 2)):
            raise RuntimeError("Mouse button already held; native probe did not take input")
        hwnd = initial["hwnd"]
        origin = w.POINT(0, 0)
        if not user.ClientToScreen(hwnd, ctypes.byref(origin)):
            raise RuntimeError("Cannot resolve actual Win32 client origin")
        binding.update(client=initial["client"], screen=initial["screen"], ui=initial["ui"],
                       renderer=initial["renderer"], windows_dpi=user.GetDpiForWindow(hwnd),
                       native_client_origin=[origin.x, origin.y])
        user.SetForegroundWindow(hwnd)
        for right in (False, True):
            for direction in (-1, 1):
                command("reset")
                state = status()
                start = state["starts"][0 if direction > 0 else 1]
                outside = [-100 if direction < 0 else state["client"][0] + 100, start[1]]
                move(start)
                button(right, True)
                status(lambda data: data["active"])
                move(outside)
                active = status(lambda data: data["length"] == 26)
                require(active["focus"] and active["counter"] and active["mouse_mode"] == 0,
                        f"outside-held right={right} dir={direction}", active)
                command("capture", name=f"outside-{int(right)}-{direction}")
                button(right, False)
                final = status(lambda data: not data["active"])
                count = final["empty"] if right else final["filled"]
                delivered = any(e.get("button") == (2 if right else 1) and e.get("pressed") is False
                                and e["focus"] and (e["position"][0] < 0 or e["position"][0] >= final["client"][0])
                                for e in final["events"])
                require(delivered and final["history"] == 1 and count == 26 and not final["counter"] and final["focus"],
                        f"outside-release right={right} dir={direction}", final)
                move(start)
                back = status()
                require(not back["active"] and back["history"] == 1 and not back["blocked"],
                        f"return-after-release right={right} dir={direction}", back)
                for action, expected in enumerate((0, 26)):
                    move(back["actions"][action])
                    button(False, True)
                    button(False, False)
                    history = status(lambda data: data["history_cursor"] == action)
                    require((history["empty"] if right else history["filled"]) == expected,
                            f"native-history action={action} right={right} dir={direction}", history)

            command("reset")
            start = status()["starts"][0]
            move(start)
            button(right, True)
            move([initial["client"][0]+100, start[1]])
            status(lambda data: data["length"] == 26)
            move(start)
            back = status(lambda data: data["length"] == 1)
            require(back["active"] and not back["counter"], f"return-held right={right}", back)
            move(status()["starts"][2])
            button(right, False)
            final = status(lambda data: not data["active"])
            require(final["history"] == 1 and (final["empty"] if right else final["filled"]) == 5,
                    f"return-held-reorients right={right}", final)

        # Own harmless focus target: never send keys to another application.
        user.CreateWindowExW.restype = w.HWND
        target = user.CreateWindowExW(0, "STATIC", "ZR focus target", 0x10CF0000,
                                     origin.x+40, origin.y+40, 200, 100, None, None, None, None)
        if not target:
            raise RuntimeError("Cannot create owned focus target")
        try:
            user.SetForegroundWindow(hwnd)
            command("reset")
            start = status()["starts"][0]
            move(start)
            button(False, True)
            move([initial["client"][0]+100,start[1]])
            status(lambda data: data["length"] == 26)
            user.SetForegroundWindow(target)
            lost = status(lambda data: not data["focus"] and not data["active"])
            require(lost["history"] == 0 and not lost["counter"], "focus-loss-aborts", lost)
            button(False, False)
            user.SetForegroundWindow(hwnd)
            move(start)
            back = status(lambda data: data["focus"])
            require(not back["active"] and back["history"] == 0 and not back["blocked"], "focus-return-no-phantom", back)
            button(False, True)
            button(False, False)
            fresh = status(lambda data: data["history"] == 1)
            require(not fresh["active"], "fresh-down-after-focus", fresh)
        finally:
            user.DestroyWindow(target)
        binding["status"] = "success"
        command("quit")
        process.wait(timeout=10)
    except Exception as exc:
        binding.update(status="failure", error=str(exc))
        raise
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)
        for right in held:
            user.mouse_event(0x10 if right else 0x4, 0, 0, 0, 0)
        log.close()
        user.SetCursorPos(original_cursor.x, original_cursor.y)
        binding["images"] = {p.name: toolchain.sha256_file(p) for p in output.glob("*.png")}
        (output / "zr-windows-report.json").write_text(json.dumps(binding, ensure_ascii=False, indent=2)+"\n",
                                                    encoding="utf-8", newline="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--player", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--head", required=True)
    args = parser.parse_args()
    probe(args.player.resolve(), args.output_dir.resolve(), args.head)
