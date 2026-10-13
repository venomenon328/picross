# Kölner Dom r04 – Endabnahmevorlage

pz-e45e2e0d67a34f6aa8368f477454 · **content_ready** · 14.10.2026 (Europe/Berlin) · Regelwerk 0.4.1 / Dokumentrevision 5 · Toolcommit 149f3d9e2fda926fc36843f7e4ee2856c31fe3ea. Inventarhash steht unveränderlich in `handoff.json.inventory.sha256` und der äußeren Endabnahmevorlage; keine selbstreferenzielle Hashbindung.

F-r01 ausdrücklich freigegeben; MA-r02 aus Paket r03 durch tatsächlichen Nutzerauftrag für **30 × 50 Mono** freigegeben. [Bildfreigabe](approvals/reveal-approval.json), [Motivfreigabe](approvals/motif-approval.json), [Herkunft](audit/source-validation.json). **Endabnahme offen**.

Ausgewählt **area-140-fit**, 1500 Zellen, 747 schwarz / 753 leer (49,8 %), Palette `ink=#000000`, Leer `#ffffff`. [Echtes Raster](views/final-raster.png), [Gitter](views/final-grid.png), [Abschlussbild](reveal/F-r01.png), [direkter Vergleich](views/final-comparison.png). Vier erste Varianten trotz Zertifikat wegen Randregel verworfen; fünfte wegen isolierter Turmspitzen. Sechste bewahrt die zusammenhängenden Türme, Zwischenraum, Fenster und drei Portale. [Entscheidungen](decisions.json), [alle Varianten](audit/candidate-comparison.json).

Nur Weißraumcrop [56,0,968,1520], exakt 3:5, ohne Streckung; keine Bildänderung, keine Zellkorrektur oder Reparatur. Erste Außenzeile leer, Randregel links/rechts/unten erfüllt. Keine weichen Ausnahmen; Fensterbögen und kleine Kreuz-/Schwellendetails werden auf Zellmaß reduziert. [Visuelle Selbstprüfung](audit/visual-review.json).

Maße, Randregel, Herkunft, deterministische Hinweise und exakte Proof-Endmatrix bestanden. `full-line-mono` v1, unbekannter Start, keine Suche/Annahme; 126 Schritte. [Frischer unabhängiger Prüferprozess](audit/final-verify.json), [RP-3-Rekonstruktion](audit/origin-verification.json), [Prüfübersicht](audit/final-checks.json). Vollständiger deduktiver Nachweis belegt Eindeutigkeit.

**L2 (leicht), plausibel L2–L4**, `picross-difficulty-0.1`, `editorial_estimate`, Vertrauen `low`. Breite Überlappungen langer Blöcke dominieren; vor Aufräumen stets mindestens 16 produktive Linien. Schwächere Regelfamilien nicht vollständig validiert. [Begründung](difficulty.json), [126 Checkpoints](audit/difficulty-checkpoints.json). Arbeitsumfang 1500 Zellen; Lösungszeit nicht geschätzt, aktive Menschenzeit nicht erfasst; Probespiel optional/nicht durchgeführt.

Nutzungsgrundlage: beauftragte KI-Illustration/-Ableitung ohne Fremdassets; Originalprompts, bekannte Einstellungen und tatsächliche Bildbytes erhalten. Keine neuen Bildaufrufe; zwei Imports, sechs Kandidaten, keine Reparatur. [Aufwand](effort.json). ZA-1 unterstützt den Zielstand; geschriebene ZIP wird außen inspiziert. Export/Registrierung noch nicht ausgeführt. Nächster Schritt: genau r04 samt Inventar redaktionell endabnehmen; anschließend Standardauftrag 4 bei Integrationsauftrag. Draft-PR, kein Merge.
