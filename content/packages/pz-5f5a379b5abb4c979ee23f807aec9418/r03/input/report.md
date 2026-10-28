# Chocolate Hills · Endabnahmevorlage r03

`pz-5f5a379b5abb4c979ee23f807aec9418` · `content_ready` · 28.10.2026 · Authoring 0.5.0.
Tool-/Regelstand `3cc1ba6b944135be489c7feccdb80de325918435`; Inventarhash im Handoff/äußeren Record.

**Endraster: 36×16, 576 Zellen, vier Vordergrundfarben, L4 · Schwer.**
A-r01 und M-r01 tatsächlich menschlich freigegeben; Endabnahme dieses Pakets offen.
[Raster](review/final-raster.png), [Gitter](review/final-grid.png),
[Bildvergleich](review/reveal-motif-raster.png), [Varianten](review/candidate-comparison.png).

Gewählt `production/c36x16-4c`, Variante `area`: zwei Braunrollen erhalten Rundung
und Staffelung besser als drei Farben; 27×12 verliert mehr kleine Hintergrundkegel.
Alle vier Kandidaten sind vollständig mit `full-line-color` vom unbekannten Start
deduktiv gelöst, jeweils in frischem unabhängigen Prozess bestätigt und aus den
Bildbytes rekonstruiert. Enddomains entsprechen exakt den Matrizen; eindeutige
Lösung folgt daraus, keine separate Suche nötig. Gewählter Proof: 74 Schritte.
Randregel bestanden: rechts und unten belegt; links/oben leer. Maße, Farbwerte,
Hinweise, Normalisierung und Herkunft: [technischer Beleg](review/c36x16-4c-verification.json).
Keine Reparatur-/Paarläufe: geeigneter Direktkandidat bereits vollständig zertifiziert.

Vier benutzte Rollen: Hügellicht #bf8545 (67), Hügelschatten #805333 (98),
Tal #91a25a (37), Vegetation #3e6141 (193); 181 Leerzellen. Farbzahlwunsch offen,
freigegebener Korridor drei/vier, Ist vier. Belegung 395/576 = 68,6 %.
Fünf Gestaltungskriterien erfüllt; Hauptformen/Talraum/Staffelung erhalten.
33 gleichfarbig isolierte Zellen sind ferne Gipfel, Vegetationsreste und Konturen;
keine zusätzlichen Logikanker. Die zweite leere Zeile liegt wie die erste oberhalb
des Motivs, kein innerer Motivstreifen. Alle Warnanlässe motivbezogen geprüft.
Keine Logik-/Matrix-/Bildänderung, keine harte Ausnahme.

Aktuelle Methode [0.4](analysis/checked.json): instrumented/medium, L4,
Punktprojektion L4–L4 (kein menschliches Unsicherheitsintervall), Score 2213/672.
Beiträge Denkanspruch 61/28, Suche 83/96, Umfang 1/4; auch ohne Umfang L4.
14 geprüfte Wellen: 7 E0, 6 E1, 1 E2, keine E3; eine enge Suchwelle.
Modellschätzung ohne menschliche Kalibrierung, Lösungszeit nicht geschätzt.
Arbeitsumfang: 395 Füll- und 181 Leerzellen, 285 Hinweise, 285 Strichproxies.
Die separate historische [0.1-Begleitschätzung](difficulty.json) dient nur dem
unveränderten ZA-1-Metadatenvertrag und ersetzt die tatsächliche 0.4-Bewertung nicht.

Herkunft/Nutzungsgrundlage: im Nutzerauftrag nativ erzeugte Illustrationen,
keine importierten Fremdbildpixel, keine Exklusivität behauptet. Diese Phase:
0 Bildaufrufe, 4 Importe, 4 unabhängige Rekonstruktionen, 1 aktuelle Analyse;
aktive Menschenzeit nicht erfasst. Probespielen optional, nicht durchgeführt.
ZIP-Inventar/Handoff und ZA-1-Inspektion werden nach dem Packen außen belegt;
Export/Registrierung bleiben bis Endabnahme offen. Native Tests nicht erforderlich:
reine Inhaltsproduktion/-ablage. Pflicht-CI folgt dem schlanken Inhaltspfad.

Nächster Schritt: **4 · Abnehmen & ins Spiel integrieren**. Eigentümer nimmt genau
das versiegelte r03-Inventar samt Endraster, Abschlussbild und Prüfbelegen ab;
erst danach separate Endfreigabe, Export, Rating-Rebind und Registrierung.
