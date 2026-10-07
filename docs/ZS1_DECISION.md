# ZS-1 · Eigentümerentscheidung und Nacharbeitsstand

Stand: 07.10.2026 · E1: Stift und Timing gewählt; N03 / Abschlussbestätigung offen

[ZS1-E1](https://github.com/venomenon328/picross/pull/55#issuecomment-6040480659)
und [#52](https://github.com/venomenon328/picross/issues/52) sind maßgeblich.
R1 ohne B-/O-Befunde gilt ausschließlich für den ursprünglichen Head
`4ae4f5a20273808f99d257a3812da86d72307a5f`. Neue Eigentümeranforderungen sind keine
rückwirkenden R1-Codefehler. Basis bleibt `ec99954268f1ad959d9ea779dbbd9e28edf7d8fa`.
Die übernommenen sechs Dokumente aus #54/`c82ae74f` werden durch E1 gezielt
fortgeschrieben; #54 bleibt offen und ist keine Produktbasis.

| Gegenstand | Verbindliche Wahl / aktueller Stand |
| --- | --- |
| Füllform | Stift gewählt; satte Originalfarben, bisherige Kontur und drei weiche Auftragsspuren bleiben im ruhenden Endbild erhalten. Historische Tinte ist kein offener Kandidat mehr. |
| X | Zwei quadratische Bézierzüge, je acht kurze Segmente; begrenzte Unterschiede in Endpunkten, Krümmung und Stärke aus der Zell-ID. Gleiche Geometrie bei Pan/Zoom/Restore, korrekt geclippt. Eigentümerbestätigung des neuen X offen. |
| Füllanimation | Sechs kurze abwechselnd nach rechts/links fortschreitende Stiftbahnen verdichten räumlich die statische Zielvorschau. Endfüllung liegt vor ihrem Strichfortschritt nur abgeschwächt vor. Kein globales Fade. |
| X-Animation | Erster Zug in der ersten Hälfte, zweiter in der zweiten Hälfte; noch ungezeichnete Abschnitte bleiben als hellere Zielvorschau sichtbar. |
| Zeit | 140 ms insgesamt Setzen/Umwandeln, 80 ms Entfernen beibehalten. Alle wirksamen Zellen eines Strichs starten gleichzeitig. Positives Timingurteil liegt bereits vor. |
| Vorschau | Statisch, 56 %; keine zusätzliche Einzelabnahme behauptet. Radieren zeigt unbekannt mit neutraler Kontur, keine alte Markierung kehrt zurück. |
| Kleine Zellen / Miniatur | Unter 18 px und in Gesamtansicht vereinfachte Füllung; Miniatur zeigt eigene Werte unmittelbar ohne Animation. |
| Rand-UI | Zusätzlichen Studien-Zeichenlayer entfernt; funktionale Buchmontierungen/Controls und Hintergrund bleiben. Keine neue Hintergrundproduktion. |
| Hinweisfonts | Genau Bakso Daging Regular und Chalkboard Regular vorgesehen. TTFs vorhanden und gegen Eigentümerquellen bytebestätigt; notwendige Rechtebelege fehlen. N03 und kombinierter Fontvergleich offen. |
| Teilstudie ohne Kandidaten | Bisherige Plex-Sans-Referenz und identische Slots; ausdrücklich keine Ersatzfont als Kandidat. Fraunces-Titel und übrige UI erhalten. |

[Fontinput und konkreter Bedarf](ZS1_FONT_INPUT.md),
[Identitäten/Hashes](zs1-font-input.json). Keine ungeklärten Fontbytes in Git/CI/Export.
Die tatsächlich verwendeten vorhandenen Fonts und OFL bleiben im
[Z2-Ressourcenmanifest](../prototypes/p1/art/book/manifest.json) und im historischen
[Font-Lock](design/book_inventory/composition/inputs/fonts.json) gebunden.
Füllkontur/Textur und X sind eigene prozedurale Zeichenbefehle in
[marks.gd](../prototypes/p1/study/marks.gd). Historische Designpakete, Rätseldaten,
Proofs, ursprüngliche Paletten und Saveformat sind unverändert.

Die Erstlieferung mit Baseline/Tinte/Stift und Fraunces-Hinweisvarianten ist über
[den historischen Head](https://github.com/venomenon328/picross/blob/4ae4f5a20273808f99d257a3812da86d72307a5f/docs/ZS1_DECISION.md)
weiter nachvollziehbar. Ihre 42 Bilder und Fade-Zeitfolgen beweisen nicht E1.

`zs1-study.json` trennt native Echtzeitfolge und kontrollierte Effektzeitpunkte.
Letztere belegen Geometrie/Zugreihenfolge mit unverändertem Zeichenpfad, keine FPS.
CPU-Zeichenzeit, Eingabe einschließlich synchronem Save, vollständige Frameabstände
und reale Mauswahrnehmung sind getrennte Messgrenzen. Der Effekt-Takt erneuert nur
die Zellschicht, keine Hinweise, Miniatur, Saves oder Modellwerte.

**ZS1-M01:** Rückmeldung erfolgt; endgültige Hinweisfont, neues X und Strichaufbau
nach vollständigem Vergleich noch bestätigen. Stift/Timing nicht erneut wählen.
Unabhängiges Review des neuen Heads und ausdrückliche Mergefreigabe bleiben nötig.
[Eigentümeranleitung](ZS1_OWNER_TRIAL.md), [Prüfzuordnung](ZS1_VERIFICATION.md).
#52 bleibt offen, #53 wird nicht vorgezogen.
