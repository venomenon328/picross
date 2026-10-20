# HZ-A · native Originalbelege

Diese unveränderten Originaldateien ergänzen [HZ-A-T01](../../HZ_A_VERIFICATION.md) und
[Draft-PR #288](https://github.com/venomenon328/picross/pull/288). Die endgültige
Head-/CI-Bindung steht im PR; die folgenden Producer werden nicht umetikettiert.

## Windows-Spieler und Katalog

- Quellhead und tatsächlicher lokaler Checkout: `f78936bc7fc1b62b2fa31671ed0906ccf6c66f87` (sauber).
- Basis: `862d2e5a939af81f0462536aa930d86eb7fffffb`.
- Tatsächlicher CI-Checkout: `8bb3bae1a4fe693ca5decde5a4f062b2852c4b0d`.
- Head-/Test-Merge-Dateibaum: `50d7c558501af30e39eeaabfaab6a2df3e5d1b26` (identisch).
- [CI 39464865493](https://github.com/venomenon328/picross/actions/runs/39464865493), Product-Versuch 1, Job `118775147134` erfolgreich.
- Godot `4.7.2.stable.official.ed1daf0bf`, Windows 11, OpenGL/NVIDIA GeForce RTX 3070.
- Original-EXE ohne Testargumente gestartet; nur deren eigenes HWND aufgenommen.
- 120 Prüfungen am tatsächlichen heruntergeladenen PCK, 6.409 Katalogprüfungen
  in elf nativen Modi; keine Fehler. KK/HZ umfasst 2.186 Prüfungen.
- Alle 1.002 gelieferten nativen CI-Technikdateien vor Verwendung hashgeprüft.

| Archiv | Originaldateien | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| [windows-pck.zip](windows-pck.zip) · [Inventar](windows-pck-inventory.json) | 37 | 22040410 | `6fea6c1b493bc2ce0103bf0a5c085d9569d21deaf9fa91b9028d90ae89c59fd8` |
| [windows-catalog.zip](windows-catalog.zip) · [Inventar](windows-catalog-inventory.json) | 319 | 40116829 | `3be2e8c1b2266dc24bc2e55dad4d3c76bb93237e3f9bd5d85b3fefd830f8a54d` |

`windows-pck.zip` enthält die vollständige `windows-binding.json`, den regulären
EXE-Start, sämtliche zehn PCK-Originalansichten, externe synthetische Eingänge
und die vollständigen nativen Prozesslogs. Die Bindung enthält Artifact-IDs/-Digests,
EXE-/PCK-Hashes, Toolchainidentität, Prüfphasen und sämtliche lokalen Dateihashes.

`windows-catalog.zip` enthält alle Katalogberichte, alle originalen Control-/Titel-
und Pixelvergleichsbilder sowie die 18 HZ-Ansichten. Nur 36 wiederholte vollständige
`-layout.png`-Ansichten sind aus diesem ergänzenden Repositoryarchiv ausgelassen;
sie bleiben lokal erhalten und in `windows-binding.json` hashgebunden. Die drei
HZ-Katalogkontexte und alle HZ-Menü-/Tooltip-/Auswahl-/Dialog-/Hilfebilder bleiben
vollständig enthalten. Kein Resize, keine Bildbearbeitung, keine Ersetzung eines
CI-Pflichtbilds. Die vollständigen CI-Artefakte bleiben am oben genannten Lauf.

Nach dem Entpacken liegen die HZ-Bilder unter `source-native/kat2/hz-*.png`,
die PCK-Ansichten unter `native/` und der echte Start unter `direct-start.png`.

## Geschützte Windows-Regressionen

[Originalberichte und Logs](windows-regressions-1c5d6f6.zip) ·
[Dateiinventar](windows-regressions-1c5d6f6-inventory.json).

Dieser separate lokale Lauf prüfte den sauberen Head/Checkout
`1c5d6f6aae70bd5c9ed4fbee9e71f9261d423203` auf derselben Basis:
Core, Completion und Graphics erfolgreich in 642,11 Sekunden. EA: 2.327 native
Prüfungen und zehn Neustartprüfungen ohne Fehler; HF: 2.531, HN: 31.495 und
PERF-B: 332 Prüfungen ohne Fehler. Die UI-/Font-/Rendererdateien sind seit diesem
Lauf unverändert; die folgenden Änderungen betreffen Browser-/PCK-Prüfharness und
Dokumentation. Die 80 Originalberichte/Logs sind hier archiviert; die vollständigen
lokalen Bildausgaben wurden ebenfalls erhalten. Das ist kein umbenannter CI-Lauf.

## Gates

Diese Ablage dokumentiert ausgeführte native Prüfungen. Sie behauptet für sich
allein keinen erfolgreichen Gesamt-CI-Lauf und keine persönliche Abnahme.
Die aus dem vollständigen finalen Diff ausgewählte Pflicht-CI, aktuelle Chromium-
Originale und der Übergabestand werden in PR #288 gebunden. HZ-A-R01 und HZ-A-M01
bleiben offen. Kein Merge, Deployment oder Issue-Abschluss.
