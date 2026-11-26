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

## Aktuelle Bewertung und geprüfter Eingang

Die aktive Bewertung steht im Feld `difficulty` des [Rätselrecords](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md#2-aktuelle-inhalte-als-einzige-bestandsautorität). Seine vier Felder sind `rating_revision,logic_binding,rating,compact_analysis`. Methode, vollständige innere Hashes und ursprünglicher Bewertungsinput bleiben Teil der eingebetteten Fachwerte. Die positive Ratingrevision reicht bis 1.000.000. Bei 0.3 enthält die Logikbindung Matrix- und Analysehash. Bei 0.4 stammt letzterer aus `compact_analysis.analysis_hash`. Der Reader prüft die aktuelle Definition einschließlich Geometrie, Matrix und erforderlicher R4-Profile. Die ursprüngliche Bewertungsquelle darf bei unveränderter Logik von der aktuellen Definition abweichen.

Der aktuelle Integrationsinput transportiert die geprüfte Bewertung als `picross-current-difficulty-v1`. Bei Registrierung werden die Fachwerte einmal in den Rätselrecord übernommen. Name, Kategorie, Bilder und Datum lassen die Bewertung unverändert. Die Runtime v9 projiziert die sechs Spielerfelder. Eine Änderung der Defaultmethode wirkt auf künftige Bewertungen.

## Auswahlbericht und getrennte Übernahme

`catalog_analysis.preview` MUSS die explizite ID-Auswahl und tatsächlich geprüfte
Vorschauwerte liefern. `adopt` übernimmt ausschließlich unveränderte geprüfte
Arbeitsdaten. Aktuelle Quellenbindungen umfassen Kategorien, Runtime, ausgewählte Records und Definitionen sowie die aktive Methode.

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

`picross-puzzle-catalog-journal-v1` hat exakt
`format,operation,old,new,retained`. Grenze **24 MiB**; der Writer schreibt
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

Die aktuelle Quellenmenge enthält beide Katalogprofile je ID. Ihre Strukturgrenze beträgt 110.005 Quellen. Der aktuelle Difficultybericht und der Methodenplan haben jeweils 16 MiB, der Datumsplan 8 MiB und das Katalogjournal 24 MiB Budget. Vor Publikation zählen die vollständigen kanonischen Seiten einschließlich Berichten. Eine technische Profiländerung erfordert keine Neubewertung.
