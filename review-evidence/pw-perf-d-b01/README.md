# PW-PERF-D-B01 · technische Nacharbeit

Produkthead `c22674012acd7d42d65edb345fcf90db3c0f9d5b`, Basis
`a559e8b38be7e658ff1d3d2aa667380657c89f4d`, PR #658.
Quelle: [Review 5910720341](https://github.com/venomenon328/picross/pull/658#pullrequestreview-5910720341).
Implementierer behebt ausschließlich B01; A01 bleibt beim unabhängigen Reviewer.
Empfänger: Reviewer mit Repositoryzugang. Ablauf 2026-11-22 oder Abschluss A01;
danach diesen temporären Ref im beauftragten Rückbau entfernen. Kein Merge-PR.

## B01 und getrennter Selbstreview

Schritt 3 §4.3 verlangt nun v2 mit vollständigem rulebook-v2 in binding.rulebook
für Handoff v5/Rev7; historische Originale verwenden v1. Negative Befunde,
sämtliche Paar-/Kandidaten-/Quell-/Handoff-/Inventar-/Paketbindungen,
echte Endfreigabe und übrige harte Gates bleiben erforderlich.
Der Nacharbeitsdiff gegen 77392b2b betrifft nur diesen Absatz und die begründete
Prüfentscheidung im Paketplan. Kein konsumierender Code oder integriertes Original
geändert. Absatz 720 → 703 UTF-8-Bytes; alle Quellenbudgets bleiben erfüllt.
Selbstreview ist keine unabhängige Freigabe; das frühere Reviewurteil bleibt gültig
für seinen damaligen Head. Kein Merge.

## T01/T02

Die [ursprünglichen T01-Originale](https://github.com/venomenon328/picross/blob/c4f422aecddef159007c90ae3481f333802069d1/review-evidence/pw-perf-d/README.md)
bleiben unverändert. Alle sechs alten Manifestdateien wurden erneut byte-/hashgeprüft.
`t01-delta.json` bindet den aktuellen Text und den generationsspezifischen semantischen
Nachtrag; 31 Überschriften/123 Autoritäten/76 aktive Links am neuen Stand ohne
fehlende Datei oder Anker nachgeprüft. Keine erneute Gleichwertigkeitsbehauptung
für die im Review beanstandete frühere v1-Anweisung.

`b01_probe.py` und `b01-probe.log`: ein gezielter Test mit echten kleinen negativen
3×3-Farbeingängen, v5-Snapshotcapture und Package-/Adapterdiagnose. Ein negatives
Paar, S=180046475; vollständige acht Regelquellen. Der native Ausnahmereader akzeptiert
v2 und weist v1, fehlende Regelquelle, unvollständige Paare, fehlende Freigabe und
falschen Freigabehash zurück. Messbefund und Original-ZIP bleiben unverändert.
Die Freigabehash-Eingabe dieses kleinen Grenztests ist synthetisch; er belegt
keine echte menschliche Entscheidung und keinen vollständigen negativen Export.
Die vorhandenen Builder-/Finalizer-/Export-/Historikregressionen laufen unverändert
im gewählten production.adapter-Modul der aktuellen Package-CI.
Keine neue Dauerregression oder Galerie. Frühe lokale Harnessversuche wurden wegen
zu breiter Discovery bzw. ungeeigneter Builder-Entwurfszulassung korrigiert;
das veröffentlichte Protokoll zeigt den abgeschlossenen gezielten Grenztest.

Reproduktion am Produkthead mit Python 3.13 und isoliertem Pillow 12.3.0:
`python b01_probe.py <produktcheckout>`; TEMP/TMP auf eigene temporäre Ablage setzen.
`core.log`: 21 kleine Plan-/Ergebnisregressionen erfolgreich; Dokumentvalidator
und git diff --check erfolgreich. Aktuelle CI und Testmerge im PR-Lieferkommentar:
[Package CI #394](https://github.com/venomenon328/picross/actions/runs/43715394041).

## T03 am finalen Produkthead

Unveränderter ursprünglicher `source_probe.py`, gleiche Basis und Auswahlmethodik;
101 vorab festgelegte alternierende Paare, warmer Python-/NTFS-Kanal, gleiche
Pfadtiefe, kein Ergebniscache. Setup separat, kein kalter Start oder API-Zeit.
`source-map.json` enthält jede Auswahl/Hash/Bytezahl und sämtliche Einzelzeiten.

| Phase | Vorher | Nachher | Budget | Abrufe vorher → nachher |
| --- | ---: | ---: | ---: | ---: |
| 1 | 35494 | 29442 | 35494 | 5 → 6 |
| 2 | 33552 | 27873 | 33552 | 4 → 5 |
| 3 Mono | 56378 | 56353 | 56378 | 4 → 5 |
| 3 Farbe | 78413 | 63479 | 67593 | 4 → 5 |
| 4 | 46592 | 45686 | 46592 | 5 → 6 |
| 5 | 35761 | 33687 | 35761 | 3 → 4 |

Summierte Abruf-/Auswahlzeit 1,7508948 → 0,9952276 s; jedes Paar und die
Einzelphasen separat im Original. 0 Routine-Historienabrufe, 0 abgeschnittene
Auswahlantworten, 0 ungeplante Wiederholungen innerhalb dieser Probe.
Das ist keine Aussage über Entwicklungslektüre, Modelltokens, Solver, Register
oder Gesamtauftragszeit. `technical-sources.json` bestätigt unveränderte getrennte
technische Zusatzquellen gegen Gitbytes des neuen Heads; diese bleiben vor ihren
Operationen Pflicht. Reproduktion: `python source_probe.py <produktcheckout>` in
eigener temporärer Ablage, danach probe-before/probe-after und Originale bereinigen.
