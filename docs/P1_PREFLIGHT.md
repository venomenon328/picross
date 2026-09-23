# P1.0: Godot-/Windows-Toolchain-Preflight

Stand: 22.09.2026 · technischer Untersuchungsnachweis zu [Issue #7](https://github.com/venomenon328/picross/issues/7)

## Ergebnis und Grenze

Der reproduzierbare lokale Windows-Pfad für Godot Standard 4.7.2-stable ist positiv: offizielle Editor- und Exportvorlagen-Archive wurden tatsächlich heruntergeladen, gegen die SHA-256-Digests der GitHub-Release-Metadaten geprüft und in einem temporären, vom Nutzerprofil isolierten Verzeichnis verwendet. Import, positiver Test, absichtlich fehlschlagender Test, kontrollierter Headless-Start, Windows-x86_64-Debugexport und Start des exportierten Windows-Konsolenprogramms funktionieren.

Der gleichartige Linux-CI-Pfad und sein herunterladbares Windows-Smoke-Artefakt wurden für PR #13 / Head `9dc214005cc6c82adebd983d972f97af1b2217b7` erfolgreich geprüft und als `7f5f945edecdad0c5b86ecbe66ab3d81c7bfedac` gemergt. Das technische P1.0-Gate ist damit positiv. Die ursprünglich offene Controllergerät-/Testerentscheidung wurde später durch D-06 in #5/#8 ausdrücklich für P1 aufgehoben; alternative Eingaben bleiben spätere Produktarbeit.

Dies ist kein P1-Spiel, kein Beleg für einen sichtbaren Windows-GUI-Start und keine Bedien-, Controller-, Rätsel- oder Produktabnahme. Der Smoke greift nicht auf `prototypes/p1/` oder echte Spielstände zu.

## Gebundene offizielle Assets

Primärquelle ist der unveränderte [Godot-Release 4.7.2-stable](https://github.com/godotengine/godot-builds/releases/tag/4.7.2-stable), veröffentlicht am 18.08.2026, `draft=false`, `prerelease=false`. `tools/p1_preflight.py` lädt die Release-Metadaten bei jedem Lauf neu, verlangt die folgenden dort veröffentlichten Digests und hasht anschließend die vollständigen lokalen Archive selbst.

| Verwendung | Asset | SHA-256 | Größe |
| --- | --- | --- | ---: |
| Windows-amd64-Editor, lokal geprüft | `Godot_v4.7.2-stable_win64.exe.zip` | `731980f9608d61333e5baf54a2ef17210acc7a538446c0cb9969f002aca1e953` | 86.013.866 Bytes |
| Linux-x86_64-Editor, CI | `Godot_v4.7.2-stable_linux.x86_64.zip` | `cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4` | 77.860.424 Bytes |
| Standard-Exportvorlagen, beide Pfade | `Godot_v4.7.2-stable_export_templates.tpz` | `f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011` | 1.281.349.702 Bytes |

Der lokale Editor meldete `4.7.2.stable.official.ed1daf0bf`. Binärarchive, extrahierte Engine-Dateien und Exportvorlagen werden nicht eingecheckt.

## Reproduzierbarer Ablauf

Voraussetzungen sind Python 3.11 oder neuer, Netzwerkzugriff auf GitHub und ungefähr 1,5 GB Download- sowie zusätzlicher temporärer Speicherplatz. Der Download ist auf 1.200 Sekunden pro Asset, jeder Godot-Prozess standardmäßig auf 300 Sekunden und der CI-Job auf 40 Minuten begrenzt. Ein bereits vorhandener Cache wird vor Wiederverwendung vollständig gehasht.

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

## Geprüfte Pfade

| Schritt | Lokales Windows-Ergebnis | Erfolgskriterium |
| --- | --- | --- |
| Release-Metadaten und Downloads | bestanden | Tag/Status, Assetnamen und veröffentlichte Digests stimmen; beide vollständigen Dateien haben den erwarteten SHA-256-Wert. |
| Versionsausgabe | Exit 0 | Exakt `4.7.2.stable.official.ed1daf0bf`. |
| Import | Exit 0 | Godot importiert das isolierte Projekt ohne Fehler. |
| Positivtest | Exit 0 | Marker `P1_PREFLIGHT_TEST_OK`. |
| Beabsichtigter Negativtest | Exit 23, vom Harness als Erfolg bewertet | Marker `P1_PREFLIGHT_EXPECTED_FAILURE`; ein unerwarteter Exit 0 macht den Gesamt-Preflight rot. |
| Kontrollierter Quellprojekt-Start | Exit 0 | Marker `P1_PREFLIGHT_START_OK`, danach sofortiges Beenden. |
| Windows-x86_64-Debugexport | Exit 0 | Erwartete Haupt- und Konsolen-EXE, keine fremden Ausgabedateien. |
| Exportierter Windows-Start | Exit 0 | Unter Windows Start der Konsolen-EXE mit demselben Startmarker und sofortigem Beenden. Unter Linux nicht als Windows-Lauf simuliert. |

Die Offline-Tests prüfen zusätzlich korrekte und falsche Hashes, abweichende Release-Metadaten, Prerelease-Ablehnung, Archivpfad-Traversal, die Windows-Editorpaarung und erlaubte Artefaktinhalte. Der bestehende Dokumentprüfweg bleibt unverändert zusätzlich erforderlich.

## CI und Artefakt

Die separate [P1-Preflight-CI](../.github/workflows/p1-preflight.yml) läuft auf `ubuntu-24.04` für Pull Requests und manuelle Starts mit ausschließlich lesendem Repositoryrecht. Sie lädt den offiziellen Linux-Editor und dieselben Standard-Exportvorlagen, führt alle auf Linux möglichen Schritte aus und exportiert Windows x86_64. Der erwartete Negativtest muss dort ebenfalls ungleich null enden. Die CI behauptet keinen Start der Windows-Datei auf Linux.

Bei Erfolg wird für sieben Tage ein Artefakt `p1-preflight-windows-x86_64-<commit>` bereitgestellt. Darin liegen:

- `p1-preflight-windows-x86_64.zip` mit Haupt-EXE, Konsolen-EXE, Kurzanleitung und eingebettetem Bericht;
- `preflight-report.json` mit Quellcommit, Host, Engineversion, tatsächlich geprüften Assethashes, Exitcodes und CI-Laufkennung.

Das ZIP ist nur die isolierte technische Probe. Es ist kein Release und kein P1-Testartefakt nach A-07.

## Startentscheidung und verbleibende Gates

Der lokale Windows-Toolchainpfad ist technisch geeignet. Für eine positive Gesamtentscheidung von #7 müssen auf dem konkreten PR-Head zusätzlich die Preflight-CI, die bestehende Setup-CI, der vollständige Diffcheck und der Selbstreview grün sein. Fehlt einer dieser Nachweise, bleibt #7 entsprechend offen; ältere Dokument-CI zählt nicht als Ersatz.

D-06 hebt das frühere Controller-Startgate ausdrücklich auf. Für die gesamte P1-Lieferung gelten am echten `prototypes/p1` A-01 bis A-07 und M-01 bis M-04, M-06/M-07; M-05 ist nicht anwendbar. Der Preflight selbst ändert weder Engineversion noch Fachverträge. Der echte P1.1-Produktweg und die offene Eigentümer-Mausprobe K-06 stehen im [P1.1-Prüfbericht](P1_1_VERIFICATION.md).
