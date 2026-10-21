# Chupacabra · r04 · raster_review · 21.10.2026

ID `pz-1b7bf32b1fa140918c0692c90d998752`; Authoring 0.5.0 / Dokumentrevision22.
Tool-/Quellcommit `6ae7725ad481a2556fcfeb1e0e974e5c3430ef51`; Inventarhash in äußerem Record/Handoff.

**Korrektur:** [r03/r04](eyes-comparison.png), [Original/Motiv/Endraster](final-comparison.png),
[Endraster mit Gitter](final-grid.png), [ohne Glättung](final-nearest.png), [Zell-Diff](cell-diff.png).
Genau Z8/S11 Oliv→Rot; zwei getrennte rote Augen in Z8/S8 und Z8/S11.
Alle übrigen 1239 Zellen unverändert, einschließlich aller Negativräume und Konturen.
31×40, 1240 Zellen, 551 gefüllt/689 leer; vier gewünschte und vier verwendete Farben:
Oliv380 Körper, Ocker118 Bauch/Schnauze, Dunkelgrün51 Kontur/Klauen, Rot2 Augen.

**Freigaben:** A-r01 und MA-r01 samt ursprünglichen Bild-/Motivfreigaben unverändert.
Tatsächlicher Korrekturauftrag: [Nutzererklärung](edits/owner-request.json).
Feste Farbableitung nach bestehendem ZA-1-v4-Weg, kein unveränderter Motivdirektimport.
**Menschliche Endabnahme r04 offen**; der Korrekturauftrag nimmt das Ergebnis nicht vorweg.

**Prüfungen:** [fester Plan](edits/second-eye-plan.json) vor Bearbeitung gespeichert;
1239 gefüllte/leere Zellen geschützt, eine Änderung erlaubt, keine Suche/Seed.
[Replayrecord](edits/second-eye-record.json), [Herkunft/Endmatrix](origin-checks.json).
Vollständiger Eltern- und Kindimport frisch rekonstruiert, gespeicherte Proofs unabhängig geprüft.
Neu: `full-line-color`, 279 Schritte, [frischer unabhängiger Prozess](edits/second-eye-verification.json).
Enddomains exakt gleich Endmatrix; vollständige Deduktion belegt Eindeutigkeit.
Nur Zeilenhinweise8/Spaltenhinweise11 geändert. Rand links/rechts/oben belegt,
unten leer; Randformel erfüllt. Maße, Palette und ursprüngliche Korridorbindung erhalten.
Sichtprüfung: zwei erkennbare Augen, unveränderte Proportionen, Stachelreihe und offene
Arm-/Bein-/Schwanzräume. Feine Fangzähne und Finger bleiben abstrahiert ([Qualität](quality.json)).
Keine zusätzliche Logikreparatur erforderlich; keine weiteren Rastervarianten.

**Schwierigkeit:** [frisch geprüfte Methode0.3](analysis/checked.json), L3 Mittel,
Punktbereich L3–L3, instrumentiert/medium; Basis3 + Größe0, R2 erforderlich,
keine definierte Engstelle, kein R3/R4. Keine menschliche Kalibrierung;
Bearbeitungsumfang1240 Zellen, Lösungszeit nicht geschätzt, Probespiel optional/nicht durchgeführt.
ZA-1-0.1-Begleitform bleibt separat in difficulty.json, keine Umetikettierung der Methode.

**Ablage/Adapter:** neues schlankes r04; r03 und seine vier Erstkandidaten bleiben
unverändert im Git-Quellstand. Aktuell nur nötige vollständige Eltern-/Kindbündel,
Bild-/Freigabe-/Nutzungsbelege und neue SD-Belege. Keine Export-/Registrierungsbehauptung.
ZA-1-v4 verlangt echte Endabnahme samt externer Autorisierung auch vor inspect;
deshalb kein vorgezogener Adapter-inspect und keine erfundene Ownerfreigabe.
Die technischen APIs wurden wie oben vollständig geprüft. Nächster Schritt nach
Endfreigabe: passende v4-Hülle binden und regulär exportieren/integrieren.

**Aufwand/Rechte:** ein neuer fester Import, eine neue SD-Analyse; keine neue Bildgenerierung,
keine Reparatursuche. Aktive Menschenzeit nicht erfasst. Beauftragte KI-Neuschöpfung ohne
fremde Vorlage; ursprüngliche Provenienz/Nutzungsgrundlage erhalten.
Pflicht-CI und getrennter Selbstreview im Ablage-PR; keine Spieler-/Windows-/PCK-Probe
erforderlich für diese reine Authoringkorrektur.
