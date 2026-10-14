# Motivgeschützte Reparatur: technischer Vertrag

Dieser Vertrag beschreibt das weiterhin verwendete allgemeine Reparaturformat.
Die abgeschlossene RP5-Vergleichsproduktion und ihre Ergebnisse liegen im
[gebundenen historischen Stand](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/examples/rp5/README.md).
Sie werden nicht mitgeliefert oder in CI wiederholt.

## Suchverfahren

Die aktuelle Produktion legt Referenz, vollständige boolesche Schutzmaske,
Änderungsabstand, Seed sowie Such-/Prüfparameter vor der Suche ausdrücklich fest.
`true` schützt Farbe und Leerzustand gleichermaßen.

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
Linie oder begrenzte Datei-/Bildoperation kann das Limit überschreiten.
Es wird kein OS-RSS-Limit der Reparatur behauptet. Gleicher Seed und Zeitlimit
versprechen auf anderer Hardware keinen gleichen Suchausgang. Während der
Produktion bleiben geschriebene Teilfolgen unabhängig prüfbar. Nach finaler
Integration gilt die Bereinigung aus PUZZLE_AUTHORING §9.

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

Der v1-`export-p1` weist Reparaturbundles am abweichenden Manifest zurück.
Kein Reparaturraster darf als unveränderter `picross-image-candidate-v1`
ausgegeben werden. Der spätere Adaptervertrag für Reparatur- und manuelle
Ableitungen steht in [ZA-1](../../docs/ZA1_ADAPTER.md).

## Befehle und Exitcodes

Aus der isolierten Image-Umgebung mit Pillow exakt 12.3.0:

```sh
python -m tools.puzzle_production.repair search --reference <aktuelles-importbundle> --plan <reparaturplan.json> --output-dir <neues-reparaturbundle>
python -m tools.puzzle_production.repair verify --reference <aktuelles-importbundle> --bundle <reparaturbundle> --report <neuer-pruefbericht.json>
python -m unittest discover -s tests/puzzle_production -p 'test_repair.py' -v
```

Jedes Ausgabeziel muss neu sein. `repair search`: 0 für Fund/Suchbudget erschöpft,
2 ungültiger Eingang, 3 ungültiger Nachweis, 4 Abbruch, 5 technischer Fehler.
`repair verify`: 0 für korrekt rekonstruierbares Bundle, auch für regulär
gespeicherten Nichtfund/Abbruch; `certified` bleibt das Originalergebnis.
Abbruch schon während Eingangsprüfung liefert JSON/4 ohne behauptetes gültiges
Rasterbundle. Harte Prozessbeendigung kann keine Abschlussdatei garantieren.
