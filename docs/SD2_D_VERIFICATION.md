# SD2-D-V01 · Gebundener Bestandsvergleich und Übernahmevorschau

Historischer V01-Lieferstand. [SD2-D-OM01](SD2_D_OM_FOLLOWUP.md) dokumentiert
die spätere Eigentümerabnahme der 44 Vorschläge, den ausdrücklichen Verzicht
auf VR01 und den neuen erfolgreichen Om-Nachweis samt vollständiger Vorschau.
Die nachfolgenden V01-Aussagen bleiben an ihren damaligen Stand gebunden.

Stand: 26.10.2026. Auftrag [#406, Umsetzungsvorbereitung V1](https://github.com/venomenon328/picross/issues/406),
ausdrücklich ausgeführt **nur bis SD2-D-V01** auf
`chore/406-sd2-bestandsumstellung`, Ziel `main`.

**Ergebnis:** Alle 45 gebundenen sichtbaren IDs sind untersucht. 44 haben einen
geprüften Vorschlag der unveränderten Methode 0.4, ein Fall bleibt mit belegtem
Ressourcenabbruch offen. Der technische Plan ist eine Teilvorschau, keine
vollständige Übernahmefähigkeit oder Teilübernahmefreigabe. Aktive Ratings,
Runtime-v4 und Produktionsdefault bleiben 0.3. Hier endet V01; **SD2-D-VR01
ist nicht durchgeführt**, Übernahme/Aktivierung und Merge sind nicht beauftragt.

## Ausgangsbasis und Quellen

`git fetch origin` bestätigte vor Branchanlage den vorbereiteten Stand
`main@4e23e644f3457362e02b75f78fdb575a99265494`; derselbe Commit ist Werkzeugbasis.
Der damalige Arbeitsbaum enthielt keine versionierten Änderungen. Die fremden
unversionierten Pfade `docs/design/book_inventory/production/production.zip`
und `docs/design/z1_1/` wurden nicht aufgenommen oder verändert.

SD2-A/PR #408 und B/PR #409 sind nach getrennten Reviews integriert; C/PR #410
ist auf dieser Basis integriert. [C-R01](https://github.com/venomenon328/picross/pull/410#pullrequestreview-5645588795)
und die [Eigentümerausnahme zu #410](https://github.com/venomenon328/picross/pull/410#issuecomment-6404111838)
wurden gelesen. Die Ausnahme akzeptierte ausschließlich dort das fehlende
finale Gesamt-CI-/Chromium-Gate; sie ist weder ein grüner Gesamtlauf noch eine
Ausnahme für #406. Historische A/B/C-T01-Berichte bleiben unverändert.

Vor Analyse wurden die vollständige sortierte ID-Liste, Definitionsbytes,
Puzzle-Revisionen, tatsächlichen Produktionsmodi, aktiven 0.3-Projektionen,
Ratingrevisionen und Recordhashes sowie alle T-/K-Snapshotquellen gebunden.
Alle 45 Ratingrevisionen waren 1. Die **322 Bindungen** umfassen 302 vorhandene
Dateien und 20 ausdrücklich fehlende Quellen, einschließlich des fehlenden
`content/difficulty-method.json`. Alle vorhandenen Bytes stimmen mit dem
Quellcommit überein. Katalog, AT, Added, Freigaben, historische Berichte und
Namespaces sind eingeschlossen. Alle Produktionspakete sind kompakte
Integrationsbelege; keine Archive oder alten Proofpakete wurden rekonstruiert.

| Methode | Unveränderter Freeze |
| --- | --- |
| `picross-difficulty-0.3` | `8f7efa0d5ac76a1bd73fbae3618fec18dba28cf704887188eba2fcf020b9df79` |
| `picross-difficulty-0.4` | `5508f0742aa858a6adc31aa621433e68298b915fb0fd6b8d9e74e576ba87caaf` |

Die vollständigen Bindungen, ID-Zuordnung und Hashes stehen im
[Belegindex](evidence/sd2-d-v01/BINDINGS.md). Python 3.13.14 in der vorhandenen
isolierten `.venv/za1`, Pillow 12.3.0; keine globale Installation.

## Ausführung und Budgets

`catalog_analysis preview --method picross-difficulty-0.4 --all` lief einmal
auf dem gebundenen Checkout, Run-ID `sd2-d-20261026-v01-initial`.
Start/Ende UTC: 25.10.2026 23:12:19–23:16:35. Exit 0 bedeutet hier eine
vollständige Vorschau mit ausdrücklich unbewerteten Fällen, keine Freigabe
aller Ratings. Alle 45 Checked-Dateien wurden erzeugt: 43 bewertete
Linienlösungen und zwei vollständig geprüfte `stalled`-Fixpunkte.

Je ID waren Analyse und unabhängige Verifikation vorab separat gebunden:
120 s, 100.000 Linien, 20.000.000 Regeloperationen, 80.000 Wellen,
20.000.000 Paaroperationen und 250.000 Paarrecords. Alle sechs normalen und
alle sechs `--verify-*`-Flags wurden ausdrücklich gesetzt. Der unveränderte
Werkzeugweg verwendet für den anschließenden Checked-Import nochmals ein
eigenes Prüfbudget; das ist keine Wiederholung einer abgebrochenen Analyse.
Datei-/Tracegrenzen wurden nicht verändert. Laufbefehle, Zeiten und Exitcodes
liegen vollständig im externen Belegstand.

Für genau die zwei unabhängig bestätigten `stalled`-IDs erfolgte je ein neuer
Versuch. Es lagen keine passenden frischen Paarbelege vor. Verwendet wurde die
validierte innere `.logic` aus dem normalisierten SD2-Input; auch Mono wird zu
Logik-v2/`color-gap-v1` normalisiert. Der CLI-Aufruf war jeweils:

```text
python -m tools.puzzle_production solve --input <neue logic.json>
  --profile paired-lines-color --order rows-first --output-dir <neuer Ordner>
  --seconds 120 --max-lines 100000 --max-pair-work 20000000
  --max-pair-records 250000
```

Dies ist ein **einziges kumulatives Budget** für Baselineerzeugung,
Baselineprüfung, Paarerzeugung und Paarprüfung; keine `--verify-*`-Flags,
keine Suche, kein Retry, keine Budgeterhöhung.

| ID / Definition | Ergebnis des frischen Versuchs | Anschluss |
| --- | --- | --- |
| `pz-87bf2975c82540a399a3d0c7fa180a25` / Om | Exit 4, `aborted: pair_work_limit`; 20.000.000 Paaroperationen, Peak 7.462 Records, 2.472 Linienauswertungen, etwa 13,52 s. Baseline unabhängig bestätigt `stalled`, Paarproof abgebrochen und nicht vollständig geprüft. | Keiner; 0.4 bleibt `unrated: incomplete_line`. Altes aktives L5 bleibt erhalten. |
| `pz-9be288b9b5104da88fc8464184647ae7` / Game Boy | Exit 0, Baseline geprüft `stalled`, Paarproof geprüft `solved`, R4 notwendig; kumulativ 3.820.536 Paaroperationen, Peak 1.371 Records, 3.002 Linienauswertungen, etwa 3,30 s. | Genau ein neuer expliziter 0.4-`analyze` mit beiden Belegen, gleicher Definition, Modus `mono` und neuen Bundle-/Checked-Pfaden; Exit 0, L5. |

Der erfolgreiche R4-Anschluss verwendet dieselben getrennten SD2-Budgets.
Sein D=9/2, S=W=0 ist der eingefrorene R4-Anker; S/W sind **keine vollständige
Paarmessung**. Der ältere Zertifikatsbericht benennt vertragsgemäß 0.2/R4;
erst der unabhängig geprüfte neue SD2-Anschluss liefert die 0.4-Bewertung.
Die alten geschlossenen Bundles wurden nicht nachträglich verändert.

Die finale Run-ID `sd2-d-20261026-v01-r4` entstand ausschließlich durch
`preview-checked --method picross-difficulty-0.4 --all`: 44 ursprüngliche
Checked-Dateien unverändert wiederverwendet, nur Game Boy durch seinen
erfolgreichen neuen Anschluss ersetzt. Alle 45 Eingänge existieren; der im
Issue beschriebene Sonderfall „Missing checked input for selected ID“ trat
nicht ein. Om behält seinen geprüften offenen Linienstatus; der gesonderte
Paarabbruch wird hier und im Einzelvergleich zusätzlich erhalten.

## Vergleich und Plausibilität

[Vollständiger Einzelvergleich](evidence/sd2-d-v01/COMPARISON.md) mit 45 IDs,
exakten D/S/W-Brüchen, Score, Grenzen, höchster Technikfamilie, Wellenverlauf,
Hinweisstruktur, Prüfstatus, Unsicherheit und Blockern.
[Initiale Vorschau](evidence/sd2-d-v01/INITIAL_PREVIEW.md) und
[finale Vorschau](evidence/sd2-d-v01/FINAL_PREVIEW.md) sind bytegleiche
Dokumentationskopien der erzeugten Markdownberichte, keine adoptierten Berichte.

| Stufe | Aktiv 0.3 | Vorschlag 0.4 |
| --- | --- | --- |
| L1 | 0 | 4 |
| L2 | 0 | 9 |
| L3 | 32 | 6 |
| L4 | 10 | 23 |
| L5 | 3 | 2 |
| Offen | 0 | 1 |

Von den alten 32 L3-Fällen bleiben sechs L3; vier werden L1, neun L2 und
13 L4. Alle zehn alten L4 bleiben L4. Zwei der drei alten L5 erhalten einen
gültigen L5-Vorschlag, Om bleibt offen. Diese Verteilung wird beobachtet,
nicht als Sollquote oder Kalibrierungsgrundlage verwendet.

- **Größe allein trägt keine hohe Note:** Pfirsich (32×32) wird mit flüssigen
  E1-Wellen L1 (D=0,25, S≈0,371, W=0), Kölner Dom (30×50) L2
  (E1, Score≈1,7404). Die zwei größten Raster (Ho Chi Minh, José Rizal)
  sind L4 wegen E2 plus Suchanteil; W ist jeweils auf 0,25 begrenzt.
- **Kleine Rätsel können höhere Anforderungen haben:** Ankh (10×15) benötigt
  E2 und wird L3 (Score≈2,7030, W=0,015625). Banane (12×20) bleibt bei E1,
  hat aber einen höheren Suchanteil; Score≈2,0556 und L3. Das ist die nächste
  beobachtete Stufengrenze: Abstand≈0,0556 oberhalb 2. Der begrenzte W-Anteil
  hebt hier L2 auf L3. Das ist ein prüfenswerter Modellfall, keine bewiesene
  menschliche Fehlbewertung. Auch Jinja steigt durch W von L3 auf L4;
  keine bloße Umfangsanhebung erzeugt L5.
- **Modus und Hinweisstruktur:** Die 26 Mono-Fälle verteilen sich auf
  0/9/5/10/1/offen 1, die 19 Color-Fälle auf 4/0/1/13/1/offen 0.
  Vier Color-Fälle erfüllen die flüssige E1-Bedingung. Alle sieben Rätsel
  mit mehr als 400 Hinweisen liegen bei L4; kurze Blöcke sind häufiger in
  den höheren Gruppen vertreten, aber kein alleiniger Stufenschlüssel.
  Die Gruppen sind klein und motivabhängig; daraus folgt keine allgemeine
  Aussage „Farbe leichter/schwerer“ oder ein empirischer Zusammenhang.
- **L5-Gründe bleiben getrennt:** Rote Nelke löst mit E3 und hohem Suchanteil
  (Score≈4,6429); Game Boy hat frischen R4-Notwendigkeitsnachweis und den
  festen Score 4,5. Om bekommt aus dem alten R4-Vermerk keine neue Note.
- **Eigentümervergleich:** Die vom Eigentümer beschriebenen konkreten
  20×20-/30×40-Rätsel sind nicht mit IDs benannt. Keine Zuordnung anhand
  ähnlicher Dimensionen, keine erfundene Zielnote oder Probespielabnahme.

Die automatisierte Korrektheit belegt die Regeln und den gebundenen Verlauf,
nicht menschliche Lösungszeiten oder subjektive Schwierigkeit. Für alle
gültigen Vorschläge gilt `confidence=medium`, synthetische Modellschätzung;
keine freiwilligen menschlichen Vergleichslösungen liegen vor. Offene
Ressourcenbelege werden nicht zu einer Schwierigkeitsstufe umgedeutet.

## Planungsstand und spätere Gates

`catalog_analysis plan-adoption` wurde gegen die finale Vorschau ohne
`adopt` ausgeführt. Der genaue technische Plan wird unter
[Planungsbeleg](evidence/sd2-d-v01/PLAN.md) dokumentiert. Er ist an den
vollständigen Quellsnapshot und die finale Ergebnisbindung gekoppelt.
Ein Plan mit `open_ids` ist keine Freigabe seiner gültigen Teilmenge.

**Offener Blocker D-V01-B01:** Om hat keinen vollständigen neuen Paarproof
innerhalb des erlaubten einmaligen Budgets. D01 ist durch den konkreten
offenen Status abgedeckt; **D03 bleibt unerfüllt**. V01 darf so abgeschlossen
werden. Eine neue Strategie, ein weiteres Budget, Methodenentwicklung oder
Teilübernahme erfordert einen gesonderten begrenzten Auftrag.

| Nachweis / Gate | Zustand und vorgesehene Prüfung |
| --- | --- |
| V01 technische Nachweise | Gebundener Gesamtlauf, zwei begrenzte Paarversuche, ein zulässiger Anschluss, vollständige Vorschau, Plan und Quelleninvarianz. |
| Getrenntes Selbstreview | Dokumentierter eigener Prüfschritt unten; keine unabhängige Zweitprüfung. |
| SD2-D-VR01 | Offen, nicht ausgeführt. Separater qualifizierter Reviewer prüft am konkreten Head alle 45 IDs, den offenen Fall, Quellen/Proofs, Plausibilität und Plan; Gate vor Übernahme/Aktivierung. |
| SD2-D-F01 / T01 | Nicht beauftragt. Erst nach VR01 und passendem Folgeauftrag; ohne begrenzte Teilfreigabe alle IDs gültig. Ratingübernahme → unmittelbarer echter No-op → frischer Aktivierungsplan auf übernommenem Stand → Aktivierung → deren echter No-op. |
| SD2-D-R01 und Merge | Offen, erst am finalen Daten-/Integrationshead mit damaliger CI und eigenständiger Mergefreigabe. |

Kein Aktivierungsplan wurde vorweg erzeugt. Es wurden weder aktive Ratings
noch Runtimeprojektion oder Default geschrieben; keine Berichte unter
`content/difficulty/reports/` veröffentlicht. Es gab keine Savezugriffe,
Bildproduktion, Fehlerinjektion, Deployment oder Issue-Schließung.

## Belege, technische Prüfung und Selbstreview

Der vollständige Belegroot liegt auf dem gemeinsamen Arbeitsplatz unter
`E:/Zeuch/Coding/picross-sd2d-evidence/sd2-d-20261026-v01`.
Er enthält sämtliche 45 Ausgangsbundles/Checked-Dateien, beide frischen
Baseline-/Paarversuche einschließlich Abbruch, den erfolgreichen neuen
Anschluss, finale Checked-Dateien, Maschinenberichte, Befehle, Logs und
Quellenbindung. Das [Arbeitsbelegverzeichnis](evidence/sd2-d-v01/WORK_EVIDENCE.md)
bindet das vollständige portable Archiv und seine Dateien. Es bleibt bis
zum separaten Review erhalten. Die Vollbelege sind lokal verfügbar; der PR
veröffentlicht die kompakten Berichte und Bindungen. Ein Reviewer außerhalb
dieses Arbeitsplatzes benötigt das dort bezeichnete Archiv.

Die Lieferung ändert ausschließlich Markdown-Dokumentation und SD2-Statusstellen.
Keine neuen Tests aus realen Rätseln, keine Werkzeug-/Methodenänderungen.
CI wird anhand des vollständigen Basis-/Head-Diffs ausgewählt. Der **Web-Job
wird gemäß Auftrag nicht ausgeführt**; es gibt keinen erweiterten manuellen
CI-Start. Der genaue Head-/CI-Stand wird im Draft-PR geführt.

Der getrennte eigene Prüfschritt kontrolliert nach fertiger Dokumentation
alle IDs und Bindungen, Auswahlwiederverwendung, Paarversuchszahl und
Anschlussberechtigung, genaue rationale Summen/Grenzen, unveränderte Quellen
einschließlich mtimes, beide Freezes, Berichtskopien und gesamten Git-Diff.
Er führt keine weitere Deduktionssuche aus. Das konkrete Ergebnis steht im
[Selbstreview](evidence/sd2-d-v01/SELF_REVIEW.md).
