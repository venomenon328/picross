# SD-Catalog: aktive Bewertung und Katalogübernahme

- Dokument-ID: `SD-CATALOG`.
- Status: aktiver Katalogvertrag nach RI-ONE.
- Dokumentstand: 17.11.2026.
- Zuständigkeit: aktuelle Ratinghülle, Quellenpriorität, Übernahme und Katalogjournal.
- Normsprache: MUSS ist verpflichtend; DARF NICHT ist ein Verbot; DARF erlaubt eine Option.

## Quellen und Geltung

[SD](PUZZLE_DIFFICULTY.md) führt gemeinsame fachliche Grenzen,
[SD2](PUZZLE_DIFFICULTY_V2.md) die aktuelle Methode. Formeln, Referenzen und
Freezes gehören allein zu den verlinkten Kalibrierverträgen.
[SD2-Integration](SD2_INTEGRATION.md) definiert Methodenunterformen, historische
Reader, Auswahlberichte und Defaultrecord. Dieser Vertrag kopiert sie nicht.

Erstintegration folgt [RI](../production/PUZZLE_INTEGRATION.md) und
[RI-ONE](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md). Gezielte Pflege folgt
[Editor §13](../tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).
Die gemeinsamen Difficultyalgorithmen, Labels und Abnahmegrenzen bleiben dabei
unverändert. Historische Produktions-/Export-/Recoverygenerationen sind abgelöst.

## Aktive Hülle und geprüfter Arbeitsinput

Neue Integration und Ratingadoption MÜSSEN `picross-current-difficulty-v1`
verwenden. Die Hülle hat exakt:

| Feld | Bedeutung |
| --- | --- |
| `format` | `picross-current-difficulty-v1` |
| `method` | `picross-difficulty-0.3` oder `picross-difficulty-0.4` |
| `production_mode` | Ausdrücklich aktueller Modus `mono`/`color`; keine Herkunft oder Palettenableitung |
| `current_source` | Bindung an die endgültige aktuelle Definition gemäß SD2-Integration |
| `logic_binding` | Methodenspezifische Analyse-/Matrixbindung gemäß SD2-Integration |
| `rating` | Geschlossene eingebettete Bewertung der angegebenen Methode |
| `compact_analysis` | Geschlossener kompakter Befund derselben Methode |
| `rating_revision` | Ganze Zahl 1…1000000 |
| `record_hash` | Kanonischer SHA-256 aller übrigen Felder |

Dateigrenze **96 KiB**, eingebettete Bewertung **64 KiB**. Die Unterformen sind
in SD2-Integration definiert. Unbekannte Felder sind unzulässig. Die Hülle
verlangt einen gültigen vollständigen Befund mit `status=rated`.

`current_rating.validate` prüft Form, Werte, Hashes, Methodenkonsistenz,
Definition/Modus, Geometrie, Hinweise und erforderliche R4-Profile.
`current_rating.from_checked` übernimmt bereits tatsächlich geprüfte Werte
in diese Hülle; es berechnet keine neue Stufe und erfindet keine Herkunft.
Ein Analyzer-Checked-Bericht bleibt Arbeitsmaterial. Der aktuelle Integrator
verlangt weder dessen historischen Producer noch frühere Werkzeugdateien,
Quellenbilder oder Originalexport.

Bestehende gültige Ratings bleiben in ihren tatsächlich unterstützten Formen
lesbar; SD2-Integration führt die Readerliste. Bei der einmaligen RI-ONE-
Bestandsumstellung blieben ihre Bytes, Methodenmischung und Revisionen erhalten.
Neue Neuregistrierungen benötigen die aktive Defaultmethode. Eine spätere
Defaultänderung bewertet identische bereits registrierte Ergebnisse nicht neu.

## Quellenpriorität und Projektion

Aktuelle Definition und ausdrücklich aktueller Entry-Modus sind die Eingänge
einer beauftragten Neubewertung. `catalog_rating.load_sources` MUSS die aktiven
Ratingdateien der gewählten Katalogautorität direkt an diesen Definitionen prüfen.
Fehlende/ungültige erforderliche aktuelle Werte sind Fehler; `entry.production`
ist keine alternative Quelle. Historische Berichte werden nicht nachgespielt.

Neue Rasterlogik benötigt neue passende Analyse und vollständigen unabhängigen
Proof. Name/Kategorie/Bilder allein ändern weder Rating noch Added-Datum oder
Saves. Die Runtime v8 erhält ausschließlich die bestehende kleine Projektion
aus SD2-Integration, keine Produktionsnotizen oder Werkzeughüllen.

`catalog_added.load_sources` liest die aktuellen Datumsdateien. Dort gespeicherte
historische Referenzen verpflichten nicht zum erneuten Lesen früherer Reports.
Datumsrekonstruktion bleibt eine eigene beauftragte Operation mit aktuellem Plan
und tatsächlich verfügbaren historischen Datumsbelegen; sie ist keine Registrierung
oder Produktionswiederholung.

## Auswahlbericht und getrennte Übernahme

`catalog_analysis.preview` MUSS die explizite ID-Auswahl und tatsächlich geprüfte
Vorschauwerte liefern. `adopt` übernimmt ausschließlich unveränderte geprüfte
Arbeitsdaten. Aktuelle Quellenbindungen umfassen Indizes, Definitionen,
Bildsources und Livebilder, Ratings, Added-Dateien, aktive Methode sowie die
benötigten aktuellen Capability-/Noticewerte und Abwesenheiten.

Diese Katalogoperation bindet den aktuellen Katalogstand. Sie erteilt keine
Pflicht zum Lesen alter Archive/Produzenten und erweitert nicht die gezielten
Lesegrenzen von RI oder Editor §13. Ein dauerhaftes Berichtsinventar ist keine
zweite Bewertungsautorität.

Gespeicherte Pläne MÜSSEN vor Mutation frisch verglichen werden. Gleiches bereits
übernommenes Ergebnis samt Report ist No-op. Konflikte werden weder neu berechnet
noch überschrieben. Abgebrochene Analyse bewahrt gültige Altwerte und erfindet
keine L5. Neue aktive Hüllen entstehen über `current_rating`; identische Werte
behalten die vorhandene Revision, tatsächlich neue Werte erhöhen sie um eins.

Methodenaktivierung ist eine eigene ausdrückliche Operation nach
[SD2-Integration](SD2_INTEGRATION.md#c-v01-04--explizite-aktivierung).
Sie ändert keine bisherigen Ratings. Auswahlberichte, Aktivierungsplan und
Defaultrecord besitzen jeweils eigene geschlossene Formate; ihre strukturelle
historische Lesbarkeit erlaubt keine Übernahme eines alten Plans.

## Aktuelle Katalogjournale

`picross-current-catalog-journal-v2` hat exakt
`format,operation,report_run,old,new,retained,additions,replacements`.
`additions` und `replacements` sind leer. Grenze **24 MiB**; der Writer schreibt
nur aktuelle Katalogtexte und projiziert die Runtime. Zulässige Operationen:

| Operation | Autorisiertes fachliches Delta |
| --- | --- |
| `metadata` | Aktuelle Inhalts-/Kategorienmetadaten und ihre Runtimeprojektion |
| `adoption` | Ausgewählte Ratings, gebundener Dauerbericht und Difficultyprojektion |
| `added-adoption` | Beauftragte Datumswerte, zugehöriger Bericht und Datumsprojektion |
| `method-activation` | Ausschließlich neuer Defaultrecord; Runtime bytegleich |
| `sync` | Projektion aus unveränderten aktuellen Quellen |

Keine Operation registriert eine neue ID oder ändert Definitionen/Bilder.
Alt-/Neuansichten werden vollständig aus aktuellen Daten projiziert. Aktive
Bilder und alle nicht autorisierten Werte bleiben gebunden. Gemeinsamer Lock,
dauerhaftes Journal vor Mutation, frischer Phasenvergleich, atomare Veröffentlichung,
Readback und Runtime zuletzt sind Pflicht. Recovery prüft eigene tatsächliche
Alt-/Neu-/temporäre Bytes und unveränderte Abhängigkeiten, erhält Fremdänderungen
und ist wiederholbar. Alte Journalgenerationen werden nicht unterstützt.

Erstintegration hat ausschließlich den RI-Writer und sein eigenes Journal.
Gezielte Editoränderungen haben ausschließlich den kleinen aktuellen Editorplan
und dessen Journal. Die früheren gemeinsamen Export-/Package-/Receiptmatrizen
sind keine weiteren Schreibwege.

## Nachweise und Lebenszyklus

Kleine unabhängige synthetische Fälle prüfen Methoden-/Modebindung, beide
Methoden, Aktivierung, Adoption/No-op, tatsächlich betroffene Pflege und Recovery.
Der einmalige RI-ONE-Bestandsvergleich erhält Bewertungs-/Datumsbytes und
Runtimewerte. Er ist kein dauerhafter Korpusreplay und beauftragt weder
Neubewertung noch echten Savezugriff.

Der [historische Vertragsstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/SD_CATALOG.md)
und ältere Gitstände erhalten frühere Lieferungen; sie begründen keine neuen
Readerpflichten. Aktuelle Nachweise beziehen sich auf den konkreten Auftrag,
Diff und [CI-Vertrag](../ci/CI_WORKFLOW_V2.md).

## Katalogprofile für Abschlussbilder

Die aktuelle Quellenmenge enthält beide Katalogprofile je ID. Ihre Strukturgrenze beträgt 110.005 Quellen. Difficultybericht v7 und Aktivierungsplan v4 haben jeweils 16 MiB, Added-Plan v6 hat 8 MiB und Katalogjournal v2 hat 24 MiB Budget. Vor Publikation zählen die vollständigen kanonischen Seiten einschließlich Berichten. Eine technische Profiländerung erfordert keine Neubewertung.
