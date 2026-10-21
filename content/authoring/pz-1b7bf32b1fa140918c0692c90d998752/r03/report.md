# Chupacabra · r03 · content_ready · 21.10.2026

ID `pz-1b7bf32b1fa140918c0692c90d998752`. Authoring 0.5.0 / Dokumentrevision 22;
Tool-/Regelwerkscommit `b903f91472a1d8d00f34f37aee9202529b431d9d`. Inventarhash: äußeres record.json bzw. handoff.json; keine zirkuläre Selbstbindung.

**Endauswahl:** [31×40/Alpha96](imports/31x40-alpha96/area-raster.png),
[ohne Glättung](final-nearest.png), [mit Gitter](final-grid.png),
[A-r01/MA-r01/Raster](final-comparison.png). Farbig, 1240 Zellen, 551 gefüllt/689 leer.
Vier gewünschte und vier verwendete Farben: Oliv 381 (Körper), Ocker 118 (Bauch/Schnauze),
Dunkelgrün 51 (Kontur/Klauen), Rot 1 (charakteristische Augenmarke).
Die Einzelzelle ist motivisch begründet; keine neue Farbe als Logikanker.

**Freigaben:** A-r01 tatsächlich freigegeben in [Bildfreigabe](approvals/reveal-approval.json),
MA-r01 und r02-Korridor tatsächlich freigegeben in [Motivfreigabe](approvals/motif-approval.json).
Beide Bilder bytegleich erhalten. **Endabnahme offen**; keine Runtimeintegration oder Export.

**Vergleich:** [vier Erstkandidaten](four-candidates.png), [Entscheidungen](decisions.json).
31×40/Alpha128 bleibt unabhängig bestätigt `stalled`; beide 33×42-Importe sind gelöst,
verlieren aber Augenrot (nur drei Farben). Alle vier Matrizen sind verschieden.
Keine Reparaturrunde: geeigneter zertifizierter Direktimport vorhanden (§4.4).
Kein manueller Zell-Diff, keine Motivänderung, kein Paar-/Suchlauf erforderlich.

**Pflichtprüfungen:** Maße/Korridor/Farbzahl/Randregel erfüllt ([Qualität](quality.json)).
Rand: links/rechts/oben belegt, unten leer; Formel erfüllt, keine Ausnahme.
Quelle → Normalisierung → Matrix → Hinweise rekonstruiert, alle Manifestdateien geprüft
([Herkunft](origin-checks.json)). `full-line-color` vollständig vom unbekannten Start,
278 Proofschritte; [frischer unabhängiger Prozess](imports/31x40-alpha96-verification.json),
Enddomains exakt gleich Matrix. Vollständige Deduktion belegt Eindeutigkeit.
Statische Sichtung groß/klein/Gitter: Pose, Stachelrücken, Bauch und offene Schwanz-/Gliedmaßenräume
erhalten; feine Finger/Fangzähne und zweites Auge nicht separat auflösbar. [Kriterien](quality.json).
Transparentes A-r01 auf tatsächlichem Projektpapier groß und bei 112/140 px gesichtet.

**Schwierigkeit:** [geprüfte aktuelle Methode 0.3](analysis/checked.json): L3 Mittel,
Punktbereich L3–L3, instrumentiert/medium; logische Basis 3, Größenbeitrag 0.
31 Wellen (8 R0, 13 R1, 10 R2), keine definierte Engstelle, kein R3/R4 nötig.
Modellschätzung, nicht menschlich kalibriert. Historische ZA-1-Begleitform 0.1 getrennt
in [difficulty.json](difficulty.json). Umfang: 1240 Zellen, 433 Hinweisblöcke;
Lösungszeit nicht geschätzt, Probespiel optional/nicht durchgeführt.

**Herkunft/Aufwand:** beauftragte native KI-Neuschöpfung ohne fremde Vorlage;
[Provenienz](provenance/motif.json), [Prompts](prompts.json). Drei frühere Revealaufrufe,
ein Motivaufruf, vier Rasterimporte, eine SD-Analyse; aktive Menschenzeit nicht erfasst.
Keine neuen Bildaufrufe. [Aufwand](effort.json).

**Ablage/Weiter:** alle technischen/redaktionellen Produktionsgates erfüllt;
geschriebenes ZIP wird separat mit ZA-1 `inspect` geprüft. Prüfbericht neben dem ZIP;
einziger erwarteter Freigabeblocker: fehlende menschliche Endabnahme.
Schlanke Inhalts-CI und getrennter Diff-Selbstreview im Ablage-PR.
Native Spiel-/Windows-/PCK-Prüfung: nicht erforderlich, reine Authoringablage.
Nächster Schritt: **4 · Abnehmen & ins Spiel integrieren** nach tatsächlicher Endabnahme.
