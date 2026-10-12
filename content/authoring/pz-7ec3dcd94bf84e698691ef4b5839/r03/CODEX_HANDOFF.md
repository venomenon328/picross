# Codex-Übergabe · Grüne Erbse · r03 / h01

Status **motif_approved**. Diese Übergabe beendet den Auftrag vom 12.10.2026: **noch keine Rasterproduktion**. Keine Werkzeugänderungen, Runtime-Registrierung, Release oder Deployment. Die Freigaben erlauben keine automatische Weiterarbeit über diesen Auftragsumfang hinaus.

## Quelle und tatsächliche Dateien

Repository `venomenon328/picross`, geprüfter Quellstand `main@a7ae17bfadd9ba916a6db17641c168de06b6a103`. Stabile ID `pz-7ec3dcd94bf84e698691ef4b5839`, Kategorie `gemuese-pilze-kraeuter`. Aktuelle AGENTS.md und Pflichtquellen erneut gegen main geprüft; unverändert. Regelwerk 0.4.1 / Dokumentrevision 4, SHA-256 `c6636824924c6ba784bfcffd19ccbf3aeeaa481e2533d623299b84165f3cb4e8`. PR #82 bereits gemergt, schlanke Inhalts-CI vorhanden.

Einstieg über `content/authoring/index.json` → r03/record.json. Das bereits auf main liegende Paket wird bytegleich wiederverwendet:

- ZIP: `content/authoring/pz-7ec3dcd94bf84e698691ef4b5839/r03/package.zip`; 2613224 Bytes; SHA-256 `6f248d3bcfe68441bbb9b92ae14db6f7b7f5cd74d72012e5b4049910bba9bf42`.
- Lesbare Handoffkopie: `content/authoring/pz-7ec3dcd94bf84e698691ef4b5839/r03/handoff.json`; SHA-256 `222facbb7484b0950e0a128f83a411a38d81458117654a21c216ca32d78d06fd`.
- Inventar im ZIP: `inventory.json`; SHA-256 `97e52a7b6e2225b0783bc687df9428e37095c108eadec6cc470bf9ec2937853e`.

| Darstellung | Tatsächliche Datei im ZIP | SHA-256 |
| --- | --- | --- |
| Abschlussbild A-r02 | `reveal/A-r02.png` | `1fb67e28c130e50eeafd3aac92e575d83688d95e752e0cfe8361ceb8b15e29e8` |
| Motivvorlage MA-r01 | `motif/MA-r01.png` | `c9ec8c9f026b0642abaa61f71e499e8b0493e3efb00d17f0889f96821eb55751` |

Beide sind RGB-PNG, 1254 × 1254, unverändert. Keine neue Bildrevision erzeugt. Freigaben sind getrennt:

- Abschlussbild: `content/authoring/pz-7ec3dcd94bf84e698691ef4b5839/r02/reveal-approval.json`, SHA-256 `77cab784e5bc8ed93334202783c3370589ebc55fd921a2c005126b2cb72f0ee1`; identische Kopie bereits im ZIP unter `approvals/reveal-A-r02.json`. Menschliche Erklärung vom 12.10.2026, 17:30:05 UTC.
- Abstraktion: `content/authoring/pz-7ec3dcd94bf84e698691ef4b5839/r03/motif-approval.json`, SHA-256 `dace99a2e57ef7b7427628e165da013f396c7fde142caac4ee878da0813fe485`; menschliche Erklärung vom 12.10.2026, 17:45:14 UTC, gebunden an **beide** Bilddateien und das Paket.
- Aktueller maschinenlesbarer Übergabestand: `codex-handoff.json`. Originalhandoff, Inventar und ZIP bleiben versiegelt; ihre damaligen pending-Felder sind historische Zustände. Die späteren Freigaben stehen bewusst außen.

## Verbindlich und noch offen

Freigegeben sind genau MA-r01, die gestalterische Referenz A-r02 und **24 × 24, farbig** (576 Zellen). Identität, Perspektive, Proportionen und wichtige Negativflächen bewahren. Abschlussbild stets farbig und detailliert erhalten.

Drei Vordergrundgrüntöne plus Leerfläche sind die bisherige Empfehlung, keine wörtlich erteilte zusätzliche Palettefreigabe. Konkrete Farbwerte und Crop sind noch nicht festgelegt. Kein Croprecht aus der Freigabe erfinden; nötigen Cropkorridor vor künftigem Beschnitt/Import klären. Auch Maße nicht stillschweigend ändern. Die Abstraktion enthält noch sanfte Farbverläufe und schmale Spitzen rechts; sie ist keine Zellmatrix. Detailverluste und visueller Vergleich stehen in `report.md`. Original-Prompt, Herkunft und Nutzungsgrundlage liegen in `provenance/`.

## Wiederaufnahme durch Codex

1. Aktuelles main, AGENTS.md, Workflow, Profil, PUZZLE_AUTHORING (mindestens Dokumentrevision 4) und Pflichtquellen lesen. Index auflösen, Record und diese äußere Übergabe laden. Bereits vorhandene zugängliche Pakete selbst laden, keinen erneuten Upload verlangen.
2. Genau das genannte ZIP laden; Paket-/Inventar-/Handoffhash, exakte Dateimenge, alle Payloadgrößen/-hashes und beide separaten Freigabebelege gegen die tatsächlich geladenen Dateien prüfen. PNGs dekodieren. Keine Freigabe aus einem pass-Flag allein ableiten.
3. Für diesen Auftrag hier stoppen: Übergabe vollständig, keine Matrix, Hinweise, Kandidaten, Rasteransichten, Imports, Solver-/Proofläufe oder Exporte erstellen. Erst ein späterer ausdrücklicher Produktionsauftrag eröffnet die Ausführung.
4. Bei später beauftragter Produktion den bestätigten Parameterkorridor und geschützte Merkmale einhalten. Notwendige Palette/Normalisierung/Crop vor Import deklarieren; materielle Abweichungen benötigen erneute Freigabe. Bestehende Produktionswerkzeuge und Verträge verwenden; weder neue Toolfunktion noch Modell-API ergänzen.
5. Neue Rasterrevisionen samt Herkunft, vollständigem Logiknachweis, unabhängiger Prüfung, Randregel, visueller Konsistenz und Schwierigkeit gemäß Regelwerk prüfen. Sämtliche konkreten Rätselprüfungen im Produktionsauftrag, keine rätselspezifischen Unit-/CI-Tests und keine erneuten Bestandsrätselprüfungen. Inhaltspfad nur docs + ci-required, sofern content_only=true bestätigt.

Die jetzige Freigabe ist **keine** Raster-/Endabnahme und keine Katalogfähigkeit. Technische Produktionsgates bleiben pending. Keine ZA-1-Zertifizierung in dieser frühen Phase. Menschliches Probespielen ist optional. Bearbeitungszeit und Schwierigkeit nicht geschätzt. In diesem Schritt: 0 neue Bildaufrufe, 0 Imports, 0 Reparaturen, 0 Raster.

## Ablage und Nachweise

Branch `chore/pea-motif-approval-h01`, Draft-PR mit vollständigem Diff-/Selbstreview und CI; bedingter Merge vom Nutzer ausdrücklich beauftragt. Endgültige Commit-/Run-/Mergebelege stehen im PR, außerhalb des versiegelten ZIPs. Kein neuer Indexeintrag nötig: bestehender r03-Eintrag verweist auf den aktualisierten äußeren Record. Kein neues ZIP und keine Bildduplikate im Repository.
