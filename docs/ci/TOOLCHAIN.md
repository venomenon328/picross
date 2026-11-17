# Toolchain · Godot-/Windows-Preflight

## Geltung und Zuständigkeit

Dieses Dokument bindet Enginearchive, reproduzierbaren Aufruf und Erfolgskriterien
von `tools/p1_preflight.py`. Ein erfolgreicher Preflight belegt ausschließlich
Import, Test-Exitcodes, Startmarker und Export der isolierten Smoke-Anwendung.
Spielverhalten, sichtbarer Windows-GUI-Start und persönliche Bedienabnahme
benötigen ihre eigenen Nachweise. Der Smoke verwendet `tools/p1_preflight_smoke/`
und greift nicht auf echte Spielstände zu.

## Gebundene offizielle Assets

Primärquelle ist der unveränderte [Godot-Release 4.7.2-stable](https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable), veröffentlicht am 18.08.2026, `draft=false`, `prerelease=false`. `tools/p1_preflight.py` lädt die Release-Metadaten bei jedem Lauf neu, verlangt die folgenden dort veröffentlichten Digests und hasht anschließend die vollständigen lokalen Archive selbst.

| Verwendung | Asset | SHA-256 | Größe |
| --- | --- | --- | ---: |
| Windows-amd64-Editor | `Godot_v4.7.2-stable_win64.exe.zip` | `731980f9608d61333e5baf54a2ef17210acc7a538446c0cb9969f002aca1e953` | 86.013.866 Bytes |
| Linux-x86_64-Editor, CI | `Godot_v4.7.2-stable_linux.x86_64.zip` | `cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4` | 77.860.424 Bytes |
| Standard-Exportvorlagen, beide Pfade | `Godot_v4.7.2-stable_export_templates.tpz` | `f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011` | 1.281.349.702 Bytes |

Die erwartete Versionsausgabe ist `4.7.2.stable.official.ed1daf0bf`. Binärarchive, extrahierte Engine-Dateien und Exportvorlagen werden nicht eingecheckt.

## Reproduzierbarer Ablauf

Voraussetzungen sind Python 3.11 oder neuer, Netzwerkzugriff auf GitHub und ungefähr 1,5 GB Download- sowie zusätzlicher temporärer Speicherplatz. Der Download ist auf 1.200 Sekunden pro Asset, jeder Godot-Prozess standardmäßig auf 300 Sekunden begrenzt. Dies sind Prozess-/Netzwerkgrenzen, kein CI-Gesamtlaufzeitgate. Ein bereits vorhandener Cache wird vor Wiederverwendung vollständig gehasht.

Windows PowerShell:

```powershell
$preflightCache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_preflight.py --cache-dir $preflightCache --output-dir artifacts/p1-preflight --download-timeout-seconds 1200 --process-timeout-seconds 300
```

Linux/CI:

```sh
python3 tools/p1_preflight.py \
  --cache-dir "${TMPDIR:-/tmp}/picross-p1-preflight-cache" \
  --output-dir artifacts/p1-preflight \
  --download-timeout-seconds 1200 \
  --process-timeout-seconds 300
```

Der Ablauf arbeitet in einem neuen temporären Verzeichnis, setzt unter Windows eigene `APPDATA`-/`LOCALAPPDATA`-Pfade und unter Linux eigene XDG-Pfade, installiert nichts global und entfernt die Arbeitskopie am Ende. Die kleine Probe unter `tools/p1_preflight_smoke/` enthält nur Startmarker, Test-Exitcode und Exportpreset.

## Erfolgskriterien des Preflight

| Schritt | Erwarteter Exit | Erfolgskriterium |
| --- | --- | --- |
| Release-Metadaten und Downloads | 0 | Tag/Status, Assetnamen und veröffentlichte Digests stimmen; beide vollständigen Dateien haben den erwarteten SHA-256-Wert. |
| Versionsausgabe | Exit 0 | Exakt `4.7.2.stable.official.ed1daf0bf`. |
| Import | Exit 0 | Godot importiert das isolierte Projekt ohne Fehler. |
| Positivtest | Exit 0 | Marker `P1_PREFLIGHT_TEST_OK`. |
| Beabsichtigter Negativtest | Exit 23, vom Harness als Erfolg bewertet | Marker `P1_PREFLIGHT_EXPECTED_FAILURE`; ein unerwarteter Exit 0 macht den Gesamt-Preflight rot. |
| Kontrollierter Quellprojekt-Start | Exit 0 | Marker `P1_PREFLIGHT_START_OK`, danach sofortiges Beenden. |
| Windows-x86_64-Debugexport | Exit 0 | Erwartete Haupt- und Konsolen-EXE, keine fremden Ausgabedateien. |
| Exportierter Windows-Start | Exit 0 | Unter Windows Start der Konsolen-EXE mit demselben Startmarker und sofortigem Beenden. Unter Linux nicht als Windows-Lauf simuliert. |

Die Offline-Tests prüfen zusätzlich korrekte und falsche Hashes, abweichende Release-Metadaten, Prerelease-Ablehnung, Archivpfad-Traversal, die Windows-Editorpaarung und erlaubte Artefaktinhalte. Der tatsächliche Paketplan bestimmt die zusätzlich ausgewählten Prüfungen.

## CI-Einbindung und Artefakte

Der Paketplan wählt `preflight` bei begründetem Toolchain-/Harnessbedarf.
[Package CI](CI_WORKFLOW_V2.md) führt den Smoke in einem eigenen temporären
Laufordner aus. Das reguläre Windows-Spielerpaket ist davon getrennt.
Unter Linux wird kein Windows-Start behauptet.

[p1-preflight.yml](../../.github/workflows/p1-preflight.yml) ist ein manueller bzw.
wiederverwendbarer Diagnoseworkflow ohne eigenen PR-/Push-Trigger. Seine
konkreten Timeout-Overrides und Uploads stehen in der Workflowdatei;
Aufbewahrung und Prüfbedarf folgen dem aktuellen CI-Vertrag.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#7](https://github.com/venomenon328/picross/issues/7) und [PR #13](https://github.com/venomenon328/picross/pull/13).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/P1_PREFLIGHT.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
