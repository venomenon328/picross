# Kaktus – Endabnahmevorlage r03 · 16.10.2026

`pz-a358a1bf1b994efcbebeb55abf825789` · **content_ready** · Regelwerk 0.5.0 / Revision 14 · Toolcommit `35465bed49055b01583a20aab7add9b37536c129`.
Inventar-SHA-256: nach Versiegelung exakt unter [handoff.json](handoff.json), Feld `inventory.sha256`, und im äußeren Record; keine selbstreferentielle Hashbindung im inventarisierten Bericht.

**Freigaben:** [A-r01](reveal-approval.json) und [MA-r01 samt Korridor](motif-approval.json) tatsächlich menschlich freigegeben. **Endabnahme offen**, keine Spielregistrierung. [Bildvergleich](previews/final-comparison.png), [Raster mit exakten Hinweisen](previews/final-raster-clues.png), [1 Pixel je Zelle](import-15x22/area-112-raster.png).

**Auswahl:** `import-15x22/area-112`, 15 × 22 = 330 Zellen, 154 gefüllt / 176 leer (46,7 %), Mono. Nutzer-Farbwunsch offen; verwendet genau eine Farbe `ink/#000000` für den ganzen Kaktus, Leer separat. Kein Farbkonflikt. Die vier unterschiedlichen Kandidaten sind vollständig zertifiziert. Die 14 × 20-Fassungen zeichnen Ellenbogen und Stamm gröber; 160 verdickt Arme und verengt Zwischenräume. [Entscheidungen](decisions.json), [Vergleich](previews/candidate-comparison.png).

**Qualität/Änderungen:** fünf Kriterien für Reveal, Motiv und Raster erfüllt; höchster Stamm, Armhöhen, beide offenen Negativräume und gebogene Ellenbogen erhalten. Keine Reparatur, null Zelländerungen, leerer Reparaturdiff: geeigneter zertifizierter Direktimport bereits vorhanden. Keine weichen Ausnahmen, isolierten Zellen oder leeren Innenlinien. Leere Außenzeile 22 bewahrt contain-Proportionen; nicht entfernt. [Visueller Bericht](visual-review.json).

**Pflichtprüfung bestanden:** Produktmaße/Palette; Rand links/rechts/oben belegt (unten leer), Formel wahr; Original → Normalisierung → exakte Matrix → neu abgeleitete Hinweise rekonstruiert; alle gespeicherten Proofs in frischen unabhängigen Prozessen bestätigt; vollständige Enddomains exakt gleich Matrix. Profil `full-line-mono` v1, unbekannter Start, kein Raten/Startfelder, 60 Schritte: beweist zugleich Eindeutigkeit. [Herkunft und Kandidaten](audit/candidates.json), [frischer Endproofcheck](audit/verify-15x22-112.json), [Eingangsbindungen](audit/input-bindings.json). Kein Paarprofil/Suchlauf nötig. Das geschriebene ZIP wird anschließend durch ZA-1 inspect geprüft; der äußere Record bindet dessen Bericht.

**Schwierigkeit:** L2, plausibel L1–L4, `editorial_estimate`, Vertrauen low. Lange Einblockspalten/Überlappungen dominieren; keine validierte R0–R3-Notwendigkeitsklassifikation. Alle 37 Linien vor jedem der 60 Schritte geprüft, mindestens 5 produktive Linien vor Aufräumen: keine numerische Engstelle im geprüften Verlauf. Umfang 330 Zellen; menschliche Lösungszeit **nicht geschätzt**. [Bewertung](difficulty.json), [Checkpoints](audit/difficulty-checkpoints.json), [Stichproben](audit/difficulty-samples.json).

**Nutzung/Aufwand:** Beauftragte native KI-Illustration und Ableitung, beide Provenienzen gebunden. Diese Revision: 0 Bildaufrufe, 1 KI-Produktionsdurchlauf, 2 Importe / 4 Kandidaten, 0 Reparaturrunden; aktive Menschenzeit nicht erfasst. [Aufwand](effort.json), [Quellen](sources.json).

**Offen/nächster Schritt:** gebundene menschliche Endabnahme dieser r03-Auswahl vor Standardauftrag **4 · Abnehmen & ins Spiel integrieren**. Zieladapterexport ausstehend, durch fehlende Endabnahme gesperrt. Probespiel optional/nicht durchgeführt. Godot/Windows/PCK/Build nicht erforderlich: reine Produktionsablage. Ablagemerge und Endabnahme sind getrennt.
