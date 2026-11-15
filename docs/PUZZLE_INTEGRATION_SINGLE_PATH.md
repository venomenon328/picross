# Ein aktueller Integrationsweg für neue Rätsel

## Freigabe, Geltung und ausführbarer Stand

**RI-ONE · 15.11.2026 · [Issue #660](https://github.com/venomenon328/picross/issues/660).**
Der Eigentümer hat diesen Sollumfang nach der Beratung freigegeben. Das erste
Umsetzungspaket heißt RI-ONE. Diese Dokumentlieferung implementiert nichts,
migriert keine Daten und erteilt keinen Mergeauftrag.

Geprüfte Basis ist `main@aac669b5e3df7a1c095b93d054fbd9a68db3f99f`.
Dort ist die begrenzte v10-Erstregistrierung vorhanden, zugleich sind historische
Export-, Registrierungs- und Recoveryvarianten sowie Produktionspaketbindungen
ausführbar. Die konkrete v9-Dispatchlücke des Fliegenpilzversuchs wurde durch
#652/PR #654 behoben; #646/PW3-B betraf Projektor-/Detailreaderarbeit.
[Ursachenbericht](https://github.com/venomenon328/picross/pull/603#issuecomment-6886252211)
und [v10-Lieferung](https://github.com/venomenon328/picross/pull/656) bleiben
historisch gebundene Belege, keine neue Abnahme dieses Umbaus.

**Vor der technischen Umschaltung** gelten für laufende Produktionen weiterhin
die tatsächlich implementierten Verträge. **Für die Entwicklung von RI-ONE**
hat dieser freigegebene Sollvertrag im folgenden Umfang Vorrang vor den
historischen Kompatibilitäts-, Replay- und Herkunftspflichten der Fachquellen.
Die Umschaltung beginnt erst nach der im Issue festgehaltenen Startbedingung
RI-ONE-S01. Keine vorherige Umdeutung gespeicherter Freigaben oder Arbeitsstände.

## 1. Ziel und Paketgrenze

Für neue Rätsel gibt es genau eine aktuelle Integration, ihre identische
Wiederholung, ihre aktuelle Recovery und ihren Abschluss. Assistent, CLI und
Batch verwenden denselben fachlichen Kern. Lesende Planung und autorisiertes
Schreiben sind Betriebsarten; Mono/Farbe und Hintergrund selected/none/standard
sind Datenvarianten. Ein gemeinsamer Befehlsname vor mehreren alten Writern
erfüllt das Ziel nicht.

Das erste Paket umfasst gemeinsam:

- den aktuellen Eingang und Export/Übernahme;
- den Inhaltsindex und die direkt benötigten aktuellen Quellen;
- Erstregistrierung, Wiederholung, aktuelle Recovery und Abschluss;
- die einmalige Überführung integrierter Bestandsdaten und ihre direkten Leser;
- die zugehörigen Produktionsaufträge, Normtexte und gezielten Tests.

Eigenständige Editor-, Raster- und Bildänderungen behalten ihre fachliche
Bedeutung und greifen auf dieselbe aktuelle Inhaltsautorität zu. Ein neuer
Spieler, geänderte Spielmechanik, neue Solver-/Difficultyalgorithmen, Editor-UX,
Datenbank, Cacheplattform, allgemeine CI-Neuordnung und Release/Deployment
gehören nicht zum Paket. Kreative Werkzeuge dürfen unterschiedliche Verfahren
verwenden, solange sie denselben finalen Integrationsinput liefern.

## 2. Aktuelle Inhalte als einzige Bestandsautorität

Der aktuelle Inhaltsindex bleibt `content/registry.json`. Seine
Identitäts-/Pfadfelder und die bestehende Metadatenzuordnung werden weiter
verwendet; das historische `entry.production` ist keine Pflicht mehr und wird
aus dem normalen Bestand entfernt. Insbesondere entfallen Paketpfad/-hash,
ursprünglicher Exportanker, Produktionsrevision/-status/-blocker und
historische Produktions-Difficulty als zweite Autorität.

| Benötigte Information | Verbindliche aktuelle Autorität |
| --- | --- |
| ID, Key, Save-Slot, Definitionspfad, Sichtbarkeit | Aktueller Inhaltsindex; bisherige Identitäten bleiben erhalten |
| Runtime-Rätselrevision, Raster, Hinweise, Palette und Maße | Tatsächliche aktuelle Definition; keine Ableitung aus Produktionshistorie |
| Mono-/Farbmodus | Aktuelles Feld `mode` im Inhaltsindex und Integrationsinput; bei Überführung den vorhandenen wirksamen Modus erhalten |
| Name und Kategorie | Bestehende aktuelle Metadaten und Kategorienzuordnung |
| Reveal und Hintergrundpräferenz/-asset | Aktuelle Bildquellen und Livebytes; nur der derzeit wirksame Zustand |
| Schwierigkeit und Hinzugefügt-Datum | Aktuelle fachliche Bewertungs-/Datumdaten; kein historischer Erzeugerreplay |
| Nutzungsgrundlage | Tatsächlich benötigte aktuelle Rechte-/Attributionsangaben und Notices |

Aktuelle Reveal-/Hintergrundquellen bauen auf dem vorhandenen schlanken
`binding/current`-Prinzip auf. Die Bindung darf aktuelle ID, Definition,
Runtime-Rätselrevision und das aktuelle Asset referenzieren. Sie enthält keine
Kopie von `entry.production`, keinen Originalexport und keine historische
Integrationskette. Aktuelle Inhaltsprüfsummen zur Datei-/Änderungszuordnung
sind zulässig; sie werden nicht zu einem Herkunftsausweis ausgebaut.

`production.package` wird nicht durch eine neue obligatorische Receipt-,
Zertifikats- oder „Aktuellbeleg“-Datei ersetzt. Maße werden aus der Definition gelesen. Der Modus wird als aktuelles Feld
`mode` mit den bisherigen Werten `mono` oder `color` im Inhaltsindex erhalten;
bei der einmaligen Überführung wird der bestehende wirksame Wert aus
`production.mode` übernommen. Definitionen enthalten heute kein eindeutiges
Modusfeld: Einfarbiges Color darf nicht allein wegen der Palettengröße zu Mono
werden. Bereits bestehende aktuelle
Metadaten-, Rating- und Datumquellen werden wiederverwendet, ohne eine zweite
bearbeitbare Datenhaltung aufzubauen.

Die Runtimeprojektion `picross-runtime-registry-v8` bleibt in Form und
Bedeutung unverändert. Bei der Bestandsüberführung bleiben ihre bestehenden
Bytes erhalten; die Projektion des neuen Readers muss dieselben Werte liefern.
Aktive Definitionen/Bilder/Notices, Save-Slots, IDs und Runtime-Rätselrevisionen
werden nicht wegen der Werkzeugumstellung geändert. Auch manuelle aktuelle
Namen/Kategorien, Bewertungen, Datumwerte und Bildpräferenzen bleiben erhalten.

Die Bezeichnung einer fachlichen Difficulty-Methode bleibt zur Bedeutung
einer Bewertung erhalten. Sie verlangt keinen alten Gitcommit oder bytegleichen
historischen Werkzeugstand. Neue Rätsel erhalten weiterhin die aktuelle
fachliche Bewertung; bestehende Rätsel werden nicht ungefragt neu bewertet.

## 3. Ein aktueller Integrationsinput

Der Eingang transportiert die ausgewählten finalen Nutzdaten, ihre benötigten
aktuellen Qualitätsnachweise und die tatsächliche Freigabe. Er besteht aus:

1. vollständiger finaler Definition einschließlich Matrix/Hinweisen/Palette,
   ausdrücklichem aktuellem Modus sowie gewünschter aktueller Identität und
   Pfad-/Save-Slotzuordnung;
2. gewähltem Reveal, Hintergrundpräferenz und gegebenenfalls gewähltem Asset,
   jeweils mit benötigter aktueller Nutzungsgrundlage;
3. Name, gültiger Kategorie und passender aktueller Difficulty;
4. vollständigem am finalen Raster prüfbarem Logiknachweis und der konkreten
   menschlichen Inhalts-/Integrationsentscheidung.

Originalauthoring-ZIP, Kandidatenbaum, Reparaturentstehung, Regelwerkssnapshot,
Producercommit, alte Tool-/Codec-/Modulhashes und der ursprüngliche Exportweg
sind keine Pflichtbestandteile. Aktuelle Arbeitsunterlagen dürfen diese
Informationen für ihre Arbeit enthalten; der Integrator benötigt und erzeugt
daraus keine Produktionsherkunftsautorität.

Es gibt genau eine aktuelle Feldstruktur. Fehlende oder ungültige Nutzdaten
führen zu einem konkreten fachlichen Fehler. Ein Formatbezeichner darf die
aktuelle Struktur benennen, steuert aber keine Liste früherer Generationen.
Keine Herkunftsallowlist, kein Fremdrätsel-Zulassungsprozess und kein
`trusted`-/`skip_checks`-Ersatz für tatsächliche Inhaltsprüfung.

Geprüft werden aktuelle Definitions-/Hinweis-/Farbkonsistenz, Logiknachweis,
Bilddaten, relevante Darstellungsvorgaben, aktuelle Kategorie/Bewertung und
die tatsächlich getroffene Freigabe. Ein gültiger vollständiger
Deduktionsnachweis darf am finalen Raster verifiziert werden; eine zusätzliche
gleiche Eindeutigkeitssuche ist nicht allein zur Herkunftsbestätigung nötig.
Weder Import, Reparatur noch frühere Bildableitung werden dazu nachgespielt.
Unveränderte Raster-/Bildauswahl verlangt keine erneute kreative Abnahme.

Die fünf Produktionsschritte liefern diesen aktuellen Eingang. Der Integrator
muss die bisherige Phasen- oder Paketgeschichte nicht verstehen. Produktive
alte Export- und Parservarianten werden entfernt; keine parallele neue
Kompatibilitätsschicht bleibt zurück.

## 4. Ein Kern, begrenzte Transaktion, aktuelle Wiederholung

Die vorhandene begrenzte v10-Registrierung ist Ausgangsbasis für den Umbau.
Der Kern verarbeitet ausschließlich die aktuelle Struktur des Zielbestands.
Er prüft gemeinsame Indizes, die betroffene ID und ihre tatsächlichen
Eingangs-/Schreibdaten. Andere Rätselarchive, alte Original-ZIPs und
unbeteiligte historische Bild-/Produktionsquellen sind keine Abhängigkeiten.
Kein vorgeschalteter Vollscan, Cacheaufbau oder versteckter Hintergrundreplay.

Eine lesende Planung verändert keine Dateien. Die autorisierte Übernahme
prüft ihre tatsächlich konsumierten aktuellen Eingänge und Ziele erneut;
ein früheres Planergebnis ist keine fremde Schreibfreigabe. Mehrfach
verwendete unveränderte Daten dürfen innerhalb des gebundenen Aufrufs
geteilt werden. Es entsteht kein dauerhafter Vertrauenscache.

Aktuelle ID-/Key-/Slot-/Pfadkollisionen, Sperre gegen konkurrierende
kooperative Writer, atomare Veröffentlichung, Journal vor Mutation,
Readback und kontrollierte Rückführung bleiben. Runtime wird zuletzt
veröffentlicht. Die bisherigen getrennten endlichen Publikations- und
Recoverybudgets bleiben, soweit keine konkret begründete Änderung im Paket
geschlossen wird. Keine historische Generationswahl und kein Rückfall in
einen allgemeinen Altwriter.

Ein Journal enthält nur den für diese aktuelle Transaktion erforderlichen
Vorher-/Nachherzustand und ihr eigenes Schreibinventar. Es ist temporäres
Recoverymaterial, kein dauerhaftes Integrationsprotokoll. Nach vollständigem
Abschluss wird es entfernt. Recovery behandelt ausschließlich künftig mit
diesem Kern erzeugte Transaktionen; ältere offene Journale werden vor der
Umschaltung mit dem bisherigen Werkzeugstand beendet. Unklare/fremde Daten
werden nicht aufgrund einer angeblich alten Version gelöscht.

Idempotenz vergleicht das **aktuelle fachliche Ergebnis**. Identische
Nutzdaten derselben ID sind schreibfreier No-op, unabhängig von damaligem
Producer oder Integrationsweg. Abweichende aktuelle Daten einer belegten ID
sind ein Konflikt und benötigen den eigenen Revisionsauftrag. Nach einer
späteren echten Revision muss ein alter Integrationsinput nicht erneut
erfolgreich sein oder den alten Ursprung erkennen.

## 5. Completion und Produktionsabschluss

Completion bestätigt die tatsächliche Registrierung der aktuellen gewählten
Lieferung. Der Abschluss vergleicht ihren aktuellen Inhalt mit dem bestätigten
Mainstand und entfernt ausschließlich die ausdrücklich zugehörigen entbehrlichen
Arbeitsdaten. Im laufenden Job/PR darf der tatsächlich geprüfte Maincommit
genannt werden; das erzeugt keine dauerhafte Pflichtbindung im Spielkatalog.

Es wird kein neuer historischer Integrationsreceipt mit Originalexport,
Quellcommit, Integrationscommit oder Paketbaum erzeugt. Für spätere Leser
genügen die aktuellen Nutzdaten aus §2. Nicht mehr vorhandene alte
Arbeitsdateien sind kein Inhaltsdefekt. Neue/offene Arbeit derselben ID,
fremde Daten und benötigte Rechteinformationen bleiben erhalten.

Die PW-Liste bestimmt den Abschluss aus der aktuellen Lieferung und dem
tatsächlichen Mainzustand. Ihr direkter Leser wird gemeinsam mit Completion
umgestellt; bloßes Entfernen des alten Receiptwriters genügt nicht.
Spätere Bild-/Rasterarbeit bleibt als eigene offene Arbeit erkennbar.

## 6. Einmalige Bestandsüberführung

Vor Umsetzung den dann aktuellen integrierten Bestand erfassen. Die bei der
Spezifikation vorhandenen 56 Einträge sind keine feste Zielzahl: die sechs
laufenden Produktionen können den Bestand vorher erweitern.

Ein einmaliger, gezielter Übergang übernimmt ausschließlich die aktuell
wirksamen Werte aus Inhaltsindex, Definitionen, aktiven Bildquellen, Metadaten,
Ratings, Datumsdaten und benötigten Notices/Rechten. Weder alte Produktions-
schritte noch historische Toolversionen müssen dafür funktionieren.
Aktive Editorpakete werden nur insoweit gelesen, wie sie noch benötigte
aktuelle Nutzdaten enthalten. Das ist ein Übergang, kein dauerhafter Importweg.

Werte und Livebytes vor/nach vergleichen; Runtime, Saveidentitäten und
Rätselrevisionen erhalten. Fehlende aktuelle Nutzdaten konkret klären,
keine früheren Freigaben oder Rechte erfinden. Erst nach vollständiger
Übernahme und gezieltem Readback werden ausschließlich entbehrliche
Produktionspaket-/Receipt-/Historienreste integrierter Inhalte entfernt.
Unbekannte oder nicht integrierte WIP bleiben unangetastet.

Der Produktdiff liefert den umgestellten Bestand und seine direkt konsumierenden
Reader gemeinsam. Ein temporäres Übergangswerkzeug darf im einmaligen
Umsetzungsnachweis vorgehalten werden und endet nach Wiederholungs-/Reviewnachweis;
kein dauerhaft installierter Legacyimporter, keine automatische Migration
beim Editorstart und keine dauerhafte Parallelstruktur. Git-Historie wird nicht
umgeschrieben. Die separate Obst-Kompaktierung aus #653 wird nicht vorausgesetzt
oder hier vorzeitig ausgeführt; der reale Zustand beim Start entscheidet.

## 7. Betroffene Verbraucher und Normablösung

Mindestens folgende Kopplungen im tatsächlichen Diff schließen:

| Bereich | Erforderliche Nachführung |
| --- | --- |
| `target_adapter`, `background_export`, Finalizer/Builder | Ein aktueller Endinput und Export; kein alter/neuer Integrator hinter einem Flag |
| `content_registry`, `catalog_integration` | Aktuelle Inhaltsautorität, keine Paket-/Receiptgeneration als Bestandspflicht |
| `catalog_transaction`, `catalog_publication`, `registration_*` | Genau aktuelle Erstregistrierung/Recovery; gemeinsame Writer anderer Operationen weiter funktionsfähig |
| `editor_change`, Bild-/Raster-/Rating-/Datumreader | Aktuelle Zustandsbindung ohne ursprüngliche Produktionspakete |
| `integrated_content`, Receipt-/Retirementreader | Ergebnisbezogener Abschluss ohne historischen Dauerreceipt |
| PW-Projektor, Präsentation, Lieferungs-/Listenleser, Batch | Derselbe Eingang/Kern und aktueller Abschluss; keine versteckte Ersatzroute |

Bei Umsetzung die betroffenen Abschnitte in RI, ZA-1, SD-Catalog, PW/PW-B,
Authoring Schritt 5, Hintergrund-/Reveal-/Editorvertrag, Batchvertrag und
Werkzeuganleitung konsistent auf den einen ausführbaren Weg bringen.
Aktuelle Phasensnapshots und ihre Verbraucher werden erst in diesem
Implementierungsdiff gemeinsam umgestellt. Alte operative Integrations-
beschreibungen und dafür allein bestehende Tests werden entfernt; historische
Lieferberichte dürfen Geschichte bleiben und sind keine Pflichtquellen.

Normativ entfallen im RI-ONE-Scope insbesondere: Unterstützung alter
Produktions-/Export-/Registrierungs-/Recoverygenerationen, Replay zur
Hersteller-/Versionszulassung, Reproduktion einer Integrationsherkunft sowie
dauerhafte Originalexport-/Source-/Maincommit-Receipts.
Unverändert relevant sind fachliche Inhaltsqualität, echte Entscheidungen,
aktuelle Nutzungsrechte, funktionale Datenintegrität und die allgemeinen
Befugnisse aus WORKFLOW. Der Benutzerauftrag bleibt maßgeblich.

## 8. Start, Akzeptanz und Nachweise

Die endliche Produktionskohorte, ihr tatsächlicher Stand, RI-ONE-S01,
K01–K08, T01–T03, das unabhängige Produktreview RI-ONE-A01 und die konkrete
Modulauswahl stehen im [Issue #660](https://github.com/venomenon328/picross/issues/660).
Vorbereitung ist abgeschlossen, der Implementierungsstart bleibt bis S01
gesperrt. Eine spätere Startprüfung verlangt keine erneute Freigabe dieser
bereits beschlossenen fachlichen Lösung.

Ein aussagekräftiger Minimalnachweis enthält neue Mono-/Farbinputs mit
Hintergrundvarianten, identische Wiederholung, relevante Inhalts-/IDkonflikte,
einen unterbrochenen aktuellen Schreibvorgang und den aktuellen
Bestands-/Verbraucherabgleich. Testkorpora früherer Generationen entfallen.
Der einmalige Aufwandvergleich verwendet gleiche aktuelle Eingänge und
Umgebung; weniger Zweige oder Testfälle sind allein keine gemessene
Zeitverbesserung. Keine neue allgemeine Benchmark-/Auditplattform.

Für diese reine Spezifikationslieferung gelten nur Quellen-/Paketplanprüfung
und Dokumentintegrität. Produktprüfungen und tatsächliche Datenüberführung
sind nicht ausgeführt und werden durch Dokument-CI nicht ersetzt.
