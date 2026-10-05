# RP-5: motivgeschützte Reparatur und Baselinevergleich

Auftrag [#39](https://github.com/venomenon328/picross/issues/39), vollständiger Body
einschließlich Umsetzungsvorbereitung vom 05.10.2026. Branch
`feat/39-motif-repair-search` von `main@80ae2c19eb6f85bbac58a247badf65b3e0669132`.
Bei Start keine neueren Main-Änderungen, RP-5-Branches/PRs oder späteren
Kommentarentscheidungen. [Parent #34](https://github.com/venomenon328/picross/issues/34)
bleibt offen. Unabhängiges technisches/visuelles Review bleibt separates Mergegate.

## Festlegung vor dem ersten Vergleichslauf

[plans.json](plans.json) bindet genau die neun im Issue festgelegten Referenzen,
ihre unveränderten RP-3-Kandidaten und Manifestbytes sowie vollständige boolesche
Masken. `true` schützt sowohl Farben als auch Leerzellen. Die halboffenen
Rechtecke in nullbasierten Zellkoordinaten stehen im Lock; die eigentliche
Maske steht je Referenz unter `plans/`. Alle neun Maskenansichten wurden vor dem
ersten Suchlauf tatsächlich geöffnet. Die Schutzbereiche umfassen Mast/Segellücke,
Stiel/Blattanschlüsse, Augen/Gesicht/Schnabel, Füße/Astkontakt, Gesicht/Kamera/
Stativinnenräume, Tassenrand/-innenraum/Henkel/Löffel und Gesicht/Halsring/Visier.
Nach dieser Sichtung wurde der Schutz am vollständigen stilisierten Tassenrand
und den linken Halsringrändern erweitert, vor irgendeinem Reparaturlauf.

| Referenz | Maximal geänderte Zellpositionen |
| --- | ---: |
| i02-direct-60x40 | 2 |
| i03-direct-40x40 | 2 |
| a01-direct-40x40 | 2 |
| a01-direct-100x100 | 8 |
| p01-stylized-40x40 | 4 |
| p02-direct-100x100 | 4 |
| p02-stylized-100x100 | 4 |
| h02-direct-50x50 | 1 |
| h02-stylized-50x50 | 4 |

Kleine Reste erhalten kleine Änderungsbudgets; die texturreiche große Eule acht,
Fotograf und weitere Fotos vier, der empfindliche direkte Porträtfall nur eine
Zelle. Alle neun: einzelner Zelloperator, Seed 39, `seeded-frontier-v1`, höchstens
96 Vorschläge und 16 begonnene Bewertungen einschließlich unveränderter Referenz.
30 s / 250000 Linienarbeit für die Suche einschließlich Importrekonstruktion,
Solve, Dateischreiben und unabhängiger Kandidatenprüfung; separat 10 s / 100000
Linien für frischen Solve und Prüfung des geschriebenen Endnachweises.
Keine Lockerung nach einem ungünstigen Ergebnis.

Vorschläge priorisieren Manhattan-Abstand zu den ursprünglich offenen Zellen.
Innerhalb desselben Abstands sortiert kanonisches SHA-256 von Seed und
Zellposition/Zielwert; volle Palette plus Leer, ohne aktuellen Wert. Beste
Eltern zuerst nach verbliebenen Domainwerten, offenen Zellen, Änderungsabstand,
danach Bewertungsindex. Schlechtere Stände bleiben in der Frontier, solange das
Budget reicht. Das ist eine kleine begrenzte Suche, keine Vollständigkeitszusage.
Schutz greift vor Bewertung, unabhängig vom Score. Größe, Palette, Ausschnitt,
Bildformat und Stilisierung bleiben im unveränderten Referenzvertrag gebunden.

Jeder Vorschlag verbraucht einen Suchschritt, auch bei Duplikat, Rücknahme,
erneut besuchtem Zustand oder Überschreitung des Änderungsabstands. Duplikate
werden nicht erneut bewertet. Kandidaten zählen begonnene Bewertungen; abgebrochene
Bewertungen zählen mit. Mehrfaches Umfärben derselben Zelle zählt im Abstand nur
einmal; Rücknahme auf Referenzwert reduziert den Abstand, niemals Suchzähler.
Ein gemeinsames `Budget` begrenzt alle Linien der Suche; kein Reset je Kandidat.

Zeitgrenzen sind kooperativ an Linien-/Phasengrenzen; eine laufende polynomiale
Linie oder begrenzte Datei-/Bildoperation kann das Limit überschreiten. Der
separate CI-Job hat ein hartes Limit von zehn Minuten. Kein OS-RSS-Limit der
Reparatur wird behauptet. Ausgangsprüfung, Suche und Abschlussprüfung werden
gemessen; Ausgabe-/Bildarbeit gehört zur Gesamtdauer. Gleicher Seed mit Zeitlimit
verspricht auf anderer Hardware keinen gleichen Suchausgang. Gespeicherte
Teilfolgen bleiben unabhängig rekonstruierbar und prüfbar.

## Eigener Reparaturvertrag

`picross-repair-plan-v1`, `picross-repair-v1` und
`picross-repair-manifest-v1`, Werkzeug `rp5-single-cell-1`.
Plan maximal 256 KiB, Verlauf/Ergebnis jeweils 2 MiB, 128 Kandidaten,
1024 Vorschläge, 100×100 Zellen und acht Vordergrundfarben. Logik-/Prooflimits
bleiben RP-1/RP-2-konform; gesamtes Reparaturbundle höchstens 256 MiB.
Unbekannte Schlüssel, falsche Masken/Referenzen und ungültige Zahlen scheitern.

Die kanonische Reparatur-ID bindet Planhash, tatsächliche Referenz, Eltern/
Änderungen, vollständige Vorschlagsfolge, Kandidatenmatrix-/Logikhashes, getrennte
Fortschritts-/Abweichungsmerkmale, gewählte Endmatrix und vollständige Änderungen.
Laufzeiten, Linienmessung und Original-Abbruchstatus stehen separat im Ergebnis;
Dateihashes binden sämtliche tatsächlich geschriebenen Dateien einschließlich
dieses Ergebnisses. Rehashen allein legitimiert keine manipulierten Eltern,
Vorschläge, Masken, Bilder oder Proofs. Replay rekonstruiert den Import über
`images.inspect_candidate`, jede Matrix über ihre Eltern und jeden geschriebenen
Proof über den unabhängigen Blockintervallprüfer. Hinweise werden jedes Mal neu
abgeleitet; keine neuen Zertifizierungsregeln, Startfelder oder Proofcaches.

Nur `found` mit vollständig unabhängig geprüftem frischen Endproof vom
unbekannten Raster und exakt gleichen Singleton-Enddomains bedeutet logische
Freigabe. `budget_exhausted` ist ein reguläres Ergebnis, kein Nichtexistenzbeweis;
`aborted` erhält Teilfolge und Grund. Späteres erfolgreiches Replay wertet einen
ursprünglichen Abbruch nicht zur Freigabe auf. Redaktionelle Freigabe ist immer
separat. Manuelle Korrektur: geändertes Bild als neue Datei/Importrevision führen,
neuen Plan und neue vollständige Prüfung erstellen; Bundle nicht nachträglich
umetikettieren.

P1 bleibt unverändert. Der bestehende `export-p1` weist Reparaturbundles am
abweichenden Manifest zurück. Kein Reparaturraster wird als unveränderter
`picross-image-candidate-v1` ausgegeben. Eine spätere Exportanbindung muss den
gesamten Reparaturvertrag prüfen; sie gehört nicht zu dieser Lieferung.

## Befehle

Aus der vorhandenen isolierten Image-Umgebung mit Pillow exakt 12.3.0:

```sh
python -m tools.puzzle_production.repair search --reference examples/rp4/baseline/i02-direct-60x40 --plan examples/rp5/plans/i02-direct-60x40.json --output-dir artifacts/rp5-boat
python -m tools.puzzle_production.repair verify --reference examples/rp4/baseline/i02-direct-60x40 --bundle artifacts/rp5-boat --report artifacts/rp5-boat-replay.json
python -m tools.puzzle_production.rp5 produce --output-dir artifacts/rp5-new
python -m tools.puzzle_production.rp5 verify --output-dir artifacts/rp5-replay
python -m unittest discover -s tests/puzzle_production -p 'test_repair.py' -v
```

Jedes Ausgabeziel muss neu sein. `repair search`: 0 für Fund/Suchbudget erschöpft,
2 ungültiger Eingang, 3 ungültiger Nachweis, 4 Abbruch, 5 technischer Fehler.
`repair verify`: 0 für korrekt rekonstruierbares Bundle, auch für regulär
gespeicherten Nichtfund/Abbruch; `certified` bleibt das Originalergebnis.
Abbruch schon während Eingangsprüfung liefert JSON/4 ohne behauptetes gültiges
Rasterbundle. Harte Prozessbeendigung kann keine Abschlussdatei garantieren.
`rp5 verify` verlangt alle neun Bundles, vollständige 48er-Vergleichsübersicht
und dateigebundene Sichturteile. Ein aktueller erfolgreicher CI-Lauf und die
[Prüfzuordnung](../../docs/RP5_VERIFICATION.md) binden den Abschlussstand.
