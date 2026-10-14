# Efeutute r03 · Endabnahmevorlage

`pz-8ea7f3dacdcc428a9fcff7a735bc` · 13.10.2026 · `content_ready` · Regelwerk 0.4.1, Dokumentrevision 5.
Toolcommit `ac3d1b504c3cbab9480e29764bbc107a4cbec470`. Inventar `inventory.json`; sein SHA-256 steht ohne
Selbstreferenz in `handoff.json` und im äußeren Endabnahmebericht.

A-r01 ist menschlich freigegeben ([Beleg](approvals/reveal-A-r01.json));
MA-r01 und feste 35×35 sind im aktuellen Auftrag freigegeben
([Originalerklärung](approvals/motif-user-statement.txt), [Bindung](approvals/motif-MA-r01.json)).
**Endabnahme offen.** [Echtes Endraster](final/raster-35x35.png),
[ohne Glättung](final/raster-nearest.png), [Gitter](final/raster-grid.png),
[Abschlussbild](reveal/A-r01.png), [Bildvergleich](final/comparison.png).

Auswahl `a-center`: 35×35 = 1.225 Zellen, Farbe, 733 gefüllt / 492 leer (59,84 %).
Palette: `dark #25452d`, `green #508943`, `gold #e2c85b`, `pot #bf7248`, Leer `#ffffff`.
Vier exakte unterschiedliche Kandidaten; zwei zertifiziert, zwei bestätigte unvollständige
Fixpunkte. `b-lower` wegen geringerer Blattmasse/stärkerer Farbfragmentierung verworfen;
alle Entscheidungen und ursprünglichen Bündel in [decisions.json](decisions.json).
Keine Reparatur oder Zelländerung. Weiche Ausnahmen: eine diagonale goldene Blattspitze,
82 gleichfarbig isolierte Binnenzellen, reduzierte Konturen und wenige quantisierte
Terrakottarandzellen in Blättern. Identitätskern bleibt erhalten
([Sichturteile](quality-review.json), [Metriken](audit/raster-metrics.json)).

**Prüfungen bestanden:** Produktmaße/Formate/Palette; Randregel (alle vier Kanten belegt);
Original→Normalisierung→Matrix→Hinweise frisch rekonstruiert; vollständige Deduktion vom
unbekannten Start unter `full-line-color` v1 ohne Suche; geschriebener Proof im frischen
unabhängigen Prüferprozess akzeptiert; alle Enddomains exakt gleich der Matrix.
[Herkunft](audit/origin-verification.json), [frischer Proof](audit/proof-verification.json).
Ein vollständiger gültiger Deduktionsnachweis belegt zugleich Eindeutigkeit.

**Schwierigkeit L3**, plausibel L2–L4, `editorial_estimate`, Vertrauen `low`,
`picross-difficulty-0.1`: frühe eng gepackte Farbblöcke liefern Überlappungsanker,
Blattbereiche erfordern voraussichtlich kombinierte Block-/Farbzuordnung. Keine initialen
R0-Voll-/Leerlinien; mindestens zehn produktive Linien vor dem Restaufräumen, keine
definierte Engstelle im geprüften Verlauf. R2-Notwendigkeit/-Suffizienz nicht formal
gegen schwächere Familien belegt ([Bewertung](difficulty.json), [190 Wissensstände](audit/difficulty-checkpoints.json)).
Bearbeitungsumfang 1.225 Zellen / 190 Proofschritte, Lösungszeit nicht geschätzt.

Nutzungsgrundlage: native OpenAI-Bilder im Nutzerauftrag ohne Fremdreferenzen
([Reveal](provenance/reveal.json), [Motiv](provenance/motif.json), [Prompts/Einstellungen](generation.json)).
Diese Phase: 0 Bildaufrufe, 4 Imports, 0 Reparaturen; insgesamt 4 Bildaufrufe;
aktive Menschenzeit nicht erfasst. Probespiel nicht durchgeführt, optional.

ZA-1-Inspektion des geschriebenen ZIPs folgt im äußeren `inspection.json`;
technische Freigabefähigkeit wird geprüft, Export/Registrierung stehen aus.
Nächster erlaubter Schritt: menschliche Endabnahme dieses Inventars;
Standardauftrag 4 benötigt zusätzlich Integrationsauftrag. Draft-PR #108, kein Merge.
