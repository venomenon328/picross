# ZS-1 · Entscheidungsvorlage

Stand: 07.10.2026 · zwei Studienvarianten, Eigentümerwahl **offen**

Die native Probe und die [Eigentümeranleitung](ZS1_OWNER_TRIAL.md) gehören zu
[#52](https://github.com/venomenon328/picross/issues/52). Vertrag ist
[ZS-D01 bis D10](UI_DRAWING_STYLE.md), übernommen aus der gebundenen Fassung
`c82ae74f794936bca93d45f5f505ba283e971227` / Dokumentations-PR #54.
Produktbasis ist `ec99954268f1ad959d9ea779dbbd9e28edf7d8fa`, nicht der Dokumentationsbranch.

| Parameter | Aktuelle Baseline | Tinte | Stift |
| --- | --- | --- | --- |
| Hinweisfont | IBM Plex Sans 600 | Fraunces 750, opsz 9, SOFT 20, WONK 1 | Fraunces 650, opsz 9, SOFT 70, WONK 1 |
| Ziffernform | Sans | kompakte kräftige Serifenziffern | weichere verwandte Serifenziffern |
| Breitenfaktor | 1 | 0,86 | 0,86 |
| Schriftgrad bei 24er-Zelle/UI 100 % | 14 | 16 | 16 |
| Kleine Zellen | bestehende Begrenzung | höchstens Zellabstand − 3, mindestens 8 | wie Tinte |
| Gemeinsame Slots | Zeile 30, Spalte 18 × UI | unverändert | unverändert |
| Füllung | flache Originalfarbe | stabile innere Kontur, drei feine helle Schraffuren | stabile innere Kontur, drei weiche Auftragsspuren |
| Textur | keine | 15 % Weiß, 0,8 px | 12 % Weiß, 1,2 px; dunklere Eigenfarbkontur |
| X | gerades X, 1,2 px | zwei leicht gebogene Striche, höchstens 2 px, 68 % | höchstens 1,7 px, 60 % |
| Vorschau | bisherige Kontur | Zielmarkierung mit 56 % Alpha; Radieren nur neutrale Kontur | wie Tinte |
| Commit | ohne Effekt | 140 ms Verdichtung, Entfernen 80 ms Konturauslauf | wie Tinte |
| Kleine Zellen/Gesamtansicht | bisherig | unter 18 px/Übersicht keine Textur; Miniatur unverändert ruhig | wie Tinte |

Alle drei Hinweiszustände behalten jeweils dieselbe Schrift/Größe/Position;
gesetzt bleibt bei 78 %. Originalfarben und C1-Semantik bleiben erhalten.
Keine andere Slotvariante ist eingeführt: Die gewählte Form und der optische
Schriftgrad werden zuerst verglichen. Auch die Maximalzahl `100` wird in der
beschrifteten nativen Schriftprobe gezeigt; F-03 selbst enthält nur Einerfolgen.

Die Tintenempfehlung bleibt eine Empfehlung: Sie grenzt die Flächen deutlicher
ab und verwendet wenige gerichtete Spuren. Stift bietet eine weichere Alternative.
Die native Beurteilung kleiner Serifenziffern und heller Farben sowie schneller
F-03-Gesten bleibt ausdrücklich Teil der Eigentümerwahl. Eine Mischkombination
ist möglich, muss aber konkret benannt werden; keine Auswahl wird hier vorweggenommen.

## Herkunft und Rechte

Keine neuen Fremdassets oder Systemfonts. Die unveränderten, bereits offline
gebündelten Fontdateien samt OFL und SHA-256 stehen im
[Z2-Ressourcenmanifest](../prototypes/p1/art/book/manifest.json). Die exakten
Upstream-URLs/Commits stehen im historischen
[Font-Lock](design/book_inventory/composition/inputs/fonts.json).
Fraunces SHA-256: `177ff6c0f14e5550a3c624247cd1189611d4eb65d000b14944c63d967958abbb`;
Plex Sans: `3b031aa4216174205bd8471f88a49b91f093169e9e87bd5262242bc5967fe2e3`.
Variation erfolgt zur Laufzeit; keine veränderte Fontdatei wird verteilt.

Konturen, Schraffuren, X und die wenigen statischen Striche an Werkzeugmulden
und Miniaturkarte sind eigene prozedurale Zeichenbefehle in
[study/marks.gd](../prototypes/p1/study/marks.gd) und
[study/details.gd](../prototypes/p1/study/details.gd). Der Zellindex bestimmt
Variation stabil; Zeit, Neuzeichnen und Zoom würfeln keine Textur neu.
Bei schmalem Fenster oder Zoom über 100 % entfallen die Randdetails.
Das unveränderte A-Arbeitsbild behält seine dokumentierte BP-2-Herkunft und
Auflösungsgrenze. Historische Designpakete und Rätselproofs werden nicht verändert.
Squeakross liefert weder Code noch Bilder, Fontformen oder Layoutassets.

## Messung und Entscheidung

`zs1-study.json` enthält den tatsächlich verwendeten Renderer, Zeitstempel der
Bewegungsbilder, die Verzögerung bis zur zweiten Geste, native Zellzeichenzeiten
und den 100-Zellen-F-03-Eingabeweg. CPU-Zeichenzeit, vollständige Eingabe inklusive
bestehendem Save, Frameabstände und reale Mauswahrnehmung sind verschiedene Werte.
Der Animationstakt zeichnet ausschließlich die Zellschicht; er löst keine neuen
Hinweisanalysen, UI-/Miniaturrefreshes oder Saves aus und endet bei leerer Effektliste.
Die bestehende synchrone Hinweis-/Speicherarbeit ist kein FPS-Versprechen.
Aktuelle Messwerte und ihre Grenzen stehen in [Prüfzuordnung](ZS1_VERIFICATION.md)
und im commitgebundenen Draft-PR/Artefakt.

**ZS1-M01:** offen. Eigentümer wählt am benannten Windows-ZIP Ziffern, Zellform,
Texturen, X, Randdetails, Vorschaukontrast und Bewegungswerte. Unabhängiges Review
und ausdrückliche Mergefreigabe bleiben getrennte Gates; #53 beginnt danach.
