# Marie Curie · r05 · Endabnahmevorlage

**content_ready**, 17.10.2026 · pz-d829eb9b83e94f9c9357ee5ab9c9e359 · Kategorie menschen-berufe.
Regelwerk 0.5.0 / Dokumentrevision 14; Tool-/Quellcommit 4d073bdc238ae6c49edcc4a3d19fec6358d6499f.
Inventar-SHA-256 in handoff.json / äußerem record.json (keine Selbstreferenz).

**Auswahl:** [30×45, vier Farben](production/c30x45-4c/area-raster.png), 1350 Zellen,
981 gefüllt (72,67 %). [Vergleich](comparison.png), [vergrößert](audit/c30x45-4c-large.png),
[Gitter](audit/c30x45-4c-grid.png), [Abschlussbild B-r02](reveal/B-r02.png).
B-r02 und MA-r04 tatsächlich freigegeben (reveal-approval.json / motif-approval.json).
**Gesonderte Endabnahme offen.** Größenwahl innerhalb des bestätigten Korridors.

30×45 erhält die sichtbarste helle Kragenfront und unterscheidbare Nasen-/Mundmarken.
Augen, Stirn, Gesicht, Dutt rechts und Schulterumriss bleiben erkennbar. Deutliche
Detailverluste: stark vereinfachtes Gesicht, wenige Haartrennungen, Kragenkurve
nicht durchgehend, Nase/Mund links durch Terrakotta verbunden, warme Randmischzellen. Visuelle Kriterien und Einzelzellen in
visual-review.json; keine leeren Innenlinien. 26×39 gelöst, aber Kragenverlust;
beide 28×42 stalled und gestalterisch schwächer, drei Farben verschmelzen Schatten/Haar.

Wunsch ungefähr vier, tatsächlich vier Vordergrundfarben: Aubergine 562 (Kleid/Kontur),
Braun 175 (Haar), Pfirsich 172 (Haut), Terrakotta 72 (Gesicht/Hals); Leer 369.
Keine Zelländerung, kein Reparaturdiff, keine neue Bildgenerierung. Vier Direktimporte;
RP-5 und Paarprüfung entfallen, da visuell geeigneter Direktimport vollständig gelöst ist.

**Pflichtprüfungen bestanden:** Produktmaße, Randregel (alle vier Kanten belegt),
Quell-/Normalisierungs-/Matrix-/Hinweisrekonstruktion, vollständiger deduktiver
Proof full-line-color ohne Suche, frische unabhängige Verifikation und exakte
Singleton-Endmatrix. Vollständiger Proof belegt Eindeutigkeit. Belege: audit/c30x45-4c-verification.json,
production/c30x45-4c/area-proof.json und provenance-check.json; alle vier Bündel erhalten.

**Schwierigkeit L3**, plausibel L2–L4, editorial_estimate / picross-difficulty-0.1,
Vertrauen low. Vollflächen und Blockabschluss liefern einfache Anker, kombinierte
Farbzuordnung im Kopfbereich; R3-Notwendigkeit ungeprüft. Vor Restaufräumen mindestens
13 produktive Linien im vollständigen Supportprofil, keine numerische Engstelle;
kein validierter R0–R3-Analysator. Großer Eingabeumfang ist getrennt von Logik;
Lösungszeit nicht geschätzt, menschliche Spielprobe nicht durchgeführt und optional.

Nutzung: neu generierter Projektinhalt gemäß Provenienz, keine übernommenen Fremdassets.
Aktive Menschenzeit nicht erfasst. ZA-1-inspect des geschriebenen ZIPs ist vor Ablagemerge
Pflicht; sein tatsächlicher Bericht liegt daneben in inspection.json und wird im Record gebunden.
Kein Export/Runtimeeintrag. Einziger erwarteter Abnahmestopp: menschliche Endfreigabe.
**Nächster Schritt: 4 · Abnehmen & ins Spiel integrieren** – genau dieses Inventar,
Endraster und B-r02 gemeinsam abnehmen. Ablagemerge ersetzt diese Entscheidung nicht.
