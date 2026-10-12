# Knoblauch r03: Integration zur Draft-Abnahme

12.10.2026 · Basis `main@0da2bb67f15c3fad90ed276518b3d31f225d9c41` ·
Regelwerk PUZZLE_AUTHORING 0.4.1, Dokumentrevision 2 · ZA-1.

Das redaktionell abgenommene Paket ist auf `feat/knoblauch-r03-integration`
registriert. Es ergänzt den Katalog um ein siebtes Rätsel, ungelöst als
`Blatt 10 · 40 × 40`. Die neun historischen IDs/Slots bleiben unverändert.
Merge, Release und Deployment sind nicht beauftragt. Aktueller Head, getesteter
CI-Integrationsstand und Checkresultate werden im zugehörigen Draft-PR geführt.

| Bindung | Wert / Beleg |
| --- | --- |
| Produktions-ID | `pz-3a744ae1b7cb4d38b0ac29d030ef`, Paket `r03` |
| Runtime | Revision `1`, Stem und eigener Save-Slot `knoblauch_001` |
| Eingang | [Repositoryrecord](../content/authoring/pz-3a744ae1b7cb4d38b0ac29d030ef/r03/record.json), [kompaktes ZIP](../content/authoring/pz-3a744ae1b7cb4d38b0ac29d030ef/r03/package.zip) |
| ZIP-SHA-256 | `7fbadeefe46870d297619fc07511b2665822bea55730221965eec0d3d5b6457e` |
| Original-ZIP-SHA-256 | `7013d5b29a0dda5ad9a5047730a1e71b4d06596aa284ee8a3cbdad9184dc23f1` |
| Originalinventar-SHA-256 | `57af3c9c896edfbccfeef50aff235d467aef7fc3acb345a7c626d8282ee52d07` |
| Endfreigabe | [Erklärung und exakte Bindungen](../content/authoring/pz-3a744ae1b7cb4d38b0ac29d030ef/r03/approval.json), [Aufzeichnungskontext](../content/authoring/pz-3a744ae1b7cb4d38b0ac29d030ef/r03/approval-context.json) |
| Export | [Unverändertes ZA-1-Manifest](../content/packages/pz-3a744ae1b7cb4d38b0ac29d030ef/r03/manifest.json), SHA-256 `3ebdfb29b23bbc5e3c4ee455ac5abeaadc2b82751b99b596ed4fd34f506fd0a4` |

Die tatsächliche neue menschliche Endabnahme lautet: „Das angehängt Paket ist
abgenommen.“ Sie ist separat an Originalhandoff, Inventar, `candidate-002`,
Matrix, Logik und A-r01 gebunden. Der UTC-Wert dokumentiert den tatsächlichen
Aufzeichnungszeitpunkt; eine nicht verfügbare Chatnachrichtenzeit wird nicht
erfunden. Der versiegelte historische Handoff bleibt unverändert. Seine damaligen
Freigabe-/Adapterblocker sind durch den äußeren Record und die frischen Belege
fortgeschrieben. Angehängte Dokumente erteilen keine zusätzlichen Arbeitsaufträge.

Die [vollständige Eingangsprüfung](evidence/knoblauch-r03/full-input-verification.json)
bestätigt alle 180 Originalinventareinträge und 93 bytegleiche übernommene Dateien.
[Inspect](evidence/knoblauch-r03/inspect-approved.json) rekonstruiert Import und
begrenzte Reparatur, prüft Herkunft, Bildableitung, Randregel, exakte Hinweise und
vollständige deduktive Lösung mit unabhängigem Nachweisprüfer:
40×40, 1.600 Zellen, 795 gefüllt, monochrom; `full-line-mono/1`, Start unbekannt,
297 Schritte, keine Suche. Keine neue Motivänderung oder Reparatur.
Schwierigkeit bleibt die begründete redaktionelle Schätzung L3, Bereich L2–L4,
Vertrauen niedrig; menschliche Lösungszeit nicht geschätzt, Probespiel optional.
[Qualitätsbericht](../content/packages/pz-3a744ae1b7cb4d38b0ac29d030ef/r03/input/quality-report.md)
und ursprüngliche Freigaben bleiben im Prüfexport erhalten.

[Verify-export](evidence/knoblauch-r03/verify-export.json), der vorab geprüfte
[Plan](evidence/knoblauch-r03/registration-plan.json), die
[Registrierung](evidence/knoblauch-r03/registration.json) und die erneute
[Checkoutprüfung mit Replay](evidence/knoblauch-r03/checkout-verification.json)
bestätigen exakt die drei neuen Runtime-Dateien, den Prüfexport und die beiden
Registryprojektionen. Sämtliche neun alten Registryeinträge sind identisch.
ZA-1-Produktionsadapter und der Produktharness bleiben unverändert.

Fünf isolierte native Windows-Prozesse mit Godot 4.7.2 prüfen den neuen Inhalt
über die reguläre Szene und Mausaktionen: Kontrollstände alter Slots, Auswahl und
40×40-Maße, eigener falscher Teilstand samt Undo/Redo, echte Prozessneustarts,
Abschluss erst beim Loslassen, Album und Reset nur des neuen Slots. Alle
[Phasen](evidence/knoblauch-r03/native-phases-v3.json) und
[Einzelberichte](evidence/knoblauch-r03/native/finish.json) bestehen; die fremden
Save-Dateien bleiben jeweils hashgleich. Die 1.600 Rasterzellen werden gegen das
freigegebene Raster pixelgeprüft. A-r01 bleibt bytegleich und proportional.
Die echte [ungelöste Ansicht](evidence/knoblauch-r03/native/unstarted-context.png),
[eigene Teilminiatur](evidence/knoblauch-r03/native/partial-own-miniature.png),
[Abschlussansicht](evidence/knoblauch-r03/native/completion-context.png) und
[verdiente Albumgrafik](evidence/knoblauch-r03/native/album-artwork.png) wurden
zusätzlich visuell geprüft. Vor Abschluss fehlen Motivname und Reveal-Payload.

Der echte exportierte Windows-PCK besteht den
[nativen Ressourcencheck](evidence/knoblauch-r03/native/v3-actual-pck.log) mit
sieben Inhalten; Runtimeassets/Nutzungshinweise sind vorhanden, Testskripte,
Produktionspakete, Proofs, Freigaben und ausgeblendete Pilotassets ausgeschlossen.
Die [exportierte EXE startet](evidence/knoblauch-r03/native/v3-exported-windows-start.log).
Diagnostikskripte und Belege liegen außerhalb von `game/`;
das [Belegmanifest](evidence/knoblauch-r03/manifest.json) bindet ihre Dateien.

Ausdrücklich erlaubte Prüfanpassungen: Die zwei festen Sechser-Assertions folgen
der Registry und sichern den historischen Sechserpräfix. Nur die lokale
Linkprüfung erkennt bytegleich manifestgebundene ZA-1-Eingangsoriginale als
historisch; Textkonventionen und vollständige Exportprüfung bleiben verbindlich.
Vier Positiv-/Negativtests sichern diese Grenze. Weitere ausdrücklich erlaubte
Korrekturen ergänzen den isolierten Testfixture-Checkout um registrierte
Runtime-Dateien und passen den VS2-Nachweisprüfer samt zwei Regressionstests an
echte Registry-IDs an. Zwei zugehörige Fixture-Annahmen im Adaptertest verwenden
den tatsächlichen Ausgangsbestand und bereits vorhandene Verzeichnisse.
Schnelle Werkzeugsuite: 128 Tests erfolgreich, ein Windows-Symlinktest nicht ausführbar.
Dokumentprüfung erfolgreich; native Kernsuite: 5.506 Prüfungen erfolgreich.
Die vollständigen ausgewählten CI-Prüfungen müssen am finalen PR-Head bestehen.

Die ersten lokalen Gesamtläufe deckten die feste F-/VS-ID-/256-Fall-Annahme und
den unvollständigen Testfixture-Checkout auf. Nach ausdrücklicher Zustimmung
prüft VS2 nun alle 272 echten Geometriefälle einschließlich der neuen Produktions-ID;
der historische Sechserpräfix bleibt verbindlich. Der eigenständige ZA-1-Replay
mit vier Testpaketen besteht. Historische Fehlschläge bleiben lokal erhalten.
Die vollständige Produktionssuite mit 124 Tests und der vollständige Produktlauf
werden für den finalen Head durch die ausgewählte CI belegt; ältere grüne
Teilprüfungen werden nicht als dieser Gesamtnachweis ausgegeben.

Offen vor Merge: erfolgreiche Pflicht-CI, Review des benannten PR-Stands und
ausdrückliche Mergefreigabe. Ergebnisse und Quellbindung stehen in
[Draft-PR #77](https://github.com/venomenon328/picross/pull/77).
Die redaktionelle Inhaltsfreigabe ist vorhanden; fehlendes menschliches
Probespielen ist kein Gate. Vollständige lokale Laufbelege und ursprüngliche
Diagnosefehlschläge liegen in `Picross_Knoblauch_Integration_20261012` außerhalb
des Repositorys; keine davon wird als erfolgreicher Pflichtcheck ausgegeben.
