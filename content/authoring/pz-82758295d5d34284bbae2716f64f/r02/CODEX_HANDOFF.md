# Codex-Übergabe · Schachspringer · r02 / h01

Status **motif_approved**, 12.10.2026. Dieser Auftrag endet mit vollständiger Übergabe und geprüfter Archivablage: **noch keine Rasterproduktion**. Keine Werkzeugänderung, Spielkatalogaufnahme, Release oder Deployment. Erst ein weiterer ausdrücklicher Produktionsauftrag erlaubt den Rasterlauf.

## Tatsächliche Quelle und Dateipaket

Repository `venomenon328/picross`, geprüfte Quelle `main@12220735706b6930162f14b4a964dfddefe94bf6`. ID `pz-82758295d5d34284bbae2716f64f`, Kategorie `sport-spiele`. Aktuelles main/Index zuerst gelesen, AGENTS und Pflichtquellen auf unveränderte tatsächliche Bytes gegenüber dem vollständig gelesenen Snapshot geprüft. Regelwerk 0.4.1 / Dokumentrevision 4, SHA-256 `c6636824924c6ba784bfcffd19ccbf3aeeaa481e2533d623299b84165f3cb4e8`. Schlanke Inhalts-CI aus dem bereits gemergten PR #82 vorhanden.

Index → `content/authoring/pz-82758295d5d34284bbae2716f64f/r02/record.json`. Originalpaket und lesbare Handoffkopie bleiben unverändert:

- ZIP: `content/authoring/pz-82758295d5d34284bbae2716f64f/r02/package.zip`; 2655445 Bytes; SHA-256 `850b3a2b71d7193fd92b3ba71eda54b9f5b309353d9e7e186754289a7b781dd5`.
- Originalhandoff: `content/authoring/pz-82758295d5d34284bbae2716f64f/r02/handoff.json`; SHA-256 `5c46d971a5b7e0da8a059cbf870f8dc8cc8387e92bcfe220fa4ccf84068b5e52`.
- Inventar im ZIP `inventory.json`; SHA-256 `967aa23b3729039a64ceacdc96fd5ae19484dabd049d58594072c3b31b403368`.

| Darstellung | Tatsächliche Datei im ZIP | SHA-256 |
| --- | --- | --- |
| Freigegebenes farbiges Abschlussbild A-r01 | `reveal/A-r01.png` | `cc126391c1835f9eba7721d09bee3a3a86abfc0582785ddd75ceef170605ff89` |
| Freigegebene monochrome Motivvorlage MA-r01 | `motif/MA-r01.png` | `21847d0e6bb804a2d3eafc5a1fc783d21166d68195cdcc11e7e9b1548c5832b0` |

Beide tatsächlichen Bilder sind RGB8-PNG, 1254×1254, unverändert. Monochrom bezeichnet die Motivzeichnung und den vereinbarten Rätselmodus, nicht das PNG-Kanalformat. Die beiden Bilddateien sind vollständig im vorhandenen ZIP enthalten. Keine erneute Bildgenerierung, keine Duplikatbilder oder neues ZIP erforderlich.

## Getrennte menschliche Freigaben

- Abschlussbild: `content/authoring/pz-82758295d5d34284bbae2716f64f/r01/reveal-approval.json`, SHA-256 `be490ece290ebf5b10ada0160bdd475adb49c7ad86851f15a488475f671a1040`. Tatsächliche Erklärung vom 12.10.2026 20:48:01 UTC; identische Belegkopie im ZIP unter `approvals/reveal-A-r01.json`. A-r01 bleibt verbindliche farbige detaillierte Referenz. Identität, Perspektive, Bildaufbau, Hauptproportionen und wichtige Negativflächen gemäß ursprünglicher Revealfreigabe erhalten.
- Motivvorlage: `content/authoring/pz-82758295d5d34284bbae2716f64f/r02/motif-approval.json`, SHA-256 `ff4e33da34514e5d2cc0b7d1be6f1f10781d7628bc5e677befcf801d98069b6d`. Tatsächliche Erklärung vom 12.10.2026 21:06:59 UTC; bindet MA-r01 und A-r01 mit ihren getrennten Dateihashes, Originalpaket/Handoff/Inventar und dem Korridor **24×36**.
- Aktuelle maschinenlesbare Übergabe `codex-handoff.json` ergänzt die spätere tatsächliche Freigabe außerhalb des versiegelten Pakets. Weder das Originalhandoff noch Inventar, ZIP oder historische Belege umschreiben.

## Verbindlicher Korridor und offene Angaben

**Breite 24, Höhe 36, monochrom; 864 Zellen.** Mono bleibt aus den ausdrücklichen vorherigen Aufträgen verbindlich. Ein Vordergrund plus Leer gemäß Mono-Vertrag. Die bisherige 32×48-Empfehlung im Originalpaket ist historisch und nicht freigegeben. Keine stillschweigende Vergrößerung auf 28×42 oder 32×48.

Identität, Perspektive, Proportionen und wichtige Negativflächen bewahren. Insbesondere: linke Blickrichtung, beide Ohrspitzen und deren Trennung, Auge/Nüster/Mundposition, freie Fläche unter der Schnauze, Halsbogen und gestufter Sockel. Das farbige Abschlussbild unverändert lassen. Holzmaserung/feine Schatten sind in MA bereits abstrahiert, keine nachträgliche Änderung des Abschlussbilds zur Rechtfertigung einer Rasteränderung.

Konkrete Cropkoordinaten, Normalisierung und Importparameter sind nicht freigegeben. Kein pauschales Croprecht aus 24×36 ableiten. Nötigen motivtreuen Cropkorridor vor künftigem Beschnitt/Import klären; keine Streckung oder Entfernung geschützter Figurenteile. Dünne Gesichtskonturen, Auge und Sockeltrennungen sind bei 24×36 besondere spätere Prüfpunkte; Detail-/Lösbarkeitsrisiko offen. Die jetzige Bildfreigabe ist keine Zusage, dass ein valides Raster technisch möglich ist.

## Wiederaufnahme und Auftragsgrenze

1. Aktuelles main, AGENTS.md, Workflow, Profil, PUZZLE_AUTHORING (mindestens Dokumentrevision 4) und auftragsbezogene Pflichtquellen lesen. Index auflösen, Record, Originalhandoff und äußere Übergabe laden. Zugängliche Pakete selbst laden, nicht erneut als Upload verlangen.
2. Paket-/Handoff-/Inventarhash und vollständige Dateimenge/-größen/-hashes prüfen. Beide tatsächlichen PNGs aus dem ZIP laden und dekodieren. Beide getrennten menschlichen Freigabebelege gegen die Datei-/Ableitungshashes und echten Erklärungen prüfen, kein pass-Flag als menschliche Erklärung behandeln.
3. **Für diesen Auftrag hier stoppen:** keine Imports, Zellmatrix, Hinweise, Rasteransichten, Kandidaten, Solver-/Proofläufe, Reparaturen oder Exporte. Beide Bildfreigaben sind protokolliert, aber ein eigener Produktionsauftrag fehlt in diesem Schritt ausdrücklich.
4. Bei später tatsächlich beauftragter Rasterproduktion den bestätigten 24×36-mono-Korridor einhalten. Import/Crop/Normalisierung vorab deklarieren; erforderliche neue Entscheidungen und materielle Abweichungen vor der betroffenen Umsetzung klären. Vorhandene deterministische Werkzeuge nutzen; keine Werkzeug-/Modell-API-Erweiterung.
5. Neue Revisionen nach Regelwerk vollständig auf Herkunft, Randregel, deduktive Lösbarkeit, unabhängig geprüften geschriebenen Proof, Endmatrixgleichheit, Motivkonsistenz und begründete Schwierigkeit prüfen. Nur im Produktionsauftrag, keine rätselspezifischen Unit-/CI-Tests oder Bestands-Replays hinzufügen. Reine Inhalts-CI nur docs + ci-required bei tatsächlich bestätigtem content_only=true.

Keine Raster-/Endabnahme, ZA-1-Zertifizierung, Katalogfähigkeit oder Integration vorhanden. Technische Produktionsgates bleiben pending. Schwierigkeit und Lösungszeit nicht geschätzt. Menschliches Probespiel optional. Diese Phase: 0 neue Bildaufrufe, 0 Imports, 0 Raster, 0 Reparaturen, 0 Solver-/Exportläufe.

## Ablage

Arbeitsbranch `content/knight-motif-approval-h01`, Draft-PR mit vollständigem Diff/Selbstreview und ausgewählten Pflichtchecks. Nutzer beauftragt den Merge dieser Archivablage ausdrücklich bedingt; danach tatsächliches main verifizieren. Finale PR-/Head-/CI-/Mergebelege stehen im PR und äußeren Record, ohne das versiegelte ZIP zu ändern. Bestehender r02-Indexeintrag bleibt korrekt und unverändert. Kein neuer Spielkatalogeintrag.
