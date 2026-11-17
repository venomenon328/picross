# Lokaler Rätselbestand-Editor (PE)

Dokument-ID: `puzzle-editor`
Status: `active`
Zuständigkeit: Editorumfang, Importgrenzen, lokale API, gezielte Änderungen,
Save-Neustart sowie die feste Windows-Produktbindung.

## Quellen und Geltung

| Gegenstand | Maßgebliche Quelle |
| --- | --- |
| Aktuelle Inhalts- und Bildquellen, Integration | [RI](../production/PUZZLE_INTEGRATION.md) und [RI-ONE](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md) |
| Editorrequest, Plan, Journal und Prüfgrenze | §13 dieses Dokuments |
| Lokaler Dienst und HTTP-Formen | §11 dieses Dokuments |
| Hintergrundprofile und Geometrie | [Hintergrundvertrag](../production/PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile) |
| Gestalterische Bildanforderungen | [Bildnormen](../production/images/README.md) |
| Gemeinsames App-Updateprotokoll | [Updatevertrag](PRODUCTION_UPDATES.md); PE-spezifische Werte in §14–15 |
| Bedienung und Bau | [Werkzeuganleitung](../../tools/puzzle_editor/README.md) |

Der aktuelle Editor verwendet den gezielten PE-EDIT2-Weg und die aktuellen
RI-ONE-Quellen. Frühere v4/v7-Migrationen und alte Bild-/Rasterjournalformen sind
keine alternativen aktuellen Schnittstellen. Die getrennte aktuelle
Metadaten-Fach-API aus §7.1 bleibt ausdrücklich erhalten. Die früheren Abschnittsnummern
bleiben für die Navigation erhalten; historische Formen stehen im festen
[Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_EDITOR.md).
Aufträge, technische Lieferung, unabhängige Reviews und persönliche Abnahmen
werden im jeweiligen Issue/PR geführt, insbesondere [#576](https://github.com/venomenon328/picross/issues/576),
[#640](https://github.com/venomenon328/picross/issues/640) und
[#691](https://github.com/venomenon328/picross/issues/691).

## 1. Ziel und freigegebener Umfang

Eine lokale Weboberfläche öffnet einen vorhandenen Projektcheckout und pflegt
bereits registrierte Rätsel. Name, Kategorie, Abschlussbild und tatsächlich
wirksamer Hintergrund sind unmittelbar sichtbar und änderbar. Die Autorenansicht
darf alle Motivnamen und Bilder zeigen; die Spoilergrenze des Spiels bleibt erhalten.
Speichern übernimmt gültige Änderungen direkt in den lokalen Inhaltsbestand und
seine Laufzeitprojektion. Git, Build und Veröffentlichung erfolgen außerhalb des
Editors. Für Bearbeiten, Prüfen und Speichern ist kein KI-Zwischenschritt nötig.

| Bereich | Verbindliches Verhalten |
| --- | --- |
| Einstieg | Bequemer Start unter Windows; lokaler Backendprozess und Browseroberfläche. Der gewählte Checkout ist eindeutig sichtbar. Kein gehosteter Dienst oder GitHub-Zugang erforderlich. |
| Auswahl | Durchsuchbare, virtualisierte Liste mit Name und Kategorie, eigener Scrollfläche und rein visueller Sortierung. Keine technischen Keys oder vorab geladenen Bilder in den Zeilen. |
| Metadaten | Motivname und genau eine Kategorie direkt bearbeiten. Stabile IDs dienen der Zuordnung und sind keine gewöhnlichen Eingabefelder. |
| Kategorien | Anlegen, Anzeigenamen ändern, zuweisen. Löschen nur leer oder zusammen mit ausdrücklicher Neuzuordnung sämtlicher betroffener Rätsel. Keine Sortierungsverwaltung. |
| Bilder | Abschlussbild und Hintergrund ansehen, vorbereitete Datei auswählen oder hineinziehen, prüfen und unverändert importieren. |
| Hintergrund | Standard, eigenes Bild oder ausdrücklich kein Hintergrund. Auch erstmals bei einem bestehenden Legacyrätsel zuweisen und später zu Standard zurückkehren. |
| Raster | Grafische Vorschau mit echter Palette, Leerzellen, Gitter und Zoom/Fit; nachgeordnete Textbearbeitung. Lokale Vorschau ohne Solver. Kein Zeichenwerkzeug. |
| Speichern | Explizites Speichern und Verwerfen, erkennbare ungespeicherte Änderungen, konkrete Fehler. Zusammengehörige Änderungen werden konsistent übernommen. |

Keine Neuanlage oder Duplikation von Rätseln, keine Rätsellöschung, Bildgenerierung,
Bildbearbeitung, Git-Automatik, Veröffentlichung, Onlinekonten oder Mehrbenutzerlösung.
Die Inhaltsverwaltung bekommt keine zweite dauerhaft unabhängig bearbeitbare
Datenkopie in Browserstorage oder einer Datenbank. Eine schlichte Arbeitsoberfläche
genügt; der Editor übernimmt keine verpflichtende Buchinszenierung des Spiels.

## 2. Datenautorität und Änderungsgrenzen

Lesbare JSON-Quellen mit stabilen IDs bleiben maßgeblich. Die relationale Zuordnung
von Kategorien und Rätseln wird durch den gemeinsamen Datenzugriff geprüft.
SQLite und ein eigener Datenbankserver sind für diesen Umfang nicht vorgesehen.
Bilder bleiben Dateien. Der Spieler liest vorbereitete Laufzeitdaten und benötigt
weder Produktionspakete noch Python, Editor oder KI.

| Gegenstand | Zuständigkeit |
| --- | --- |
| Identität | Bestehende Rätsel-ID, Schlüssel und Save-Slot bleiben bei normaler Pflege erhalten. Technische Dateinamen werden beim Umbenennen nicht neu abgeleitet. |
| Aktuelle Metadaten | Genau eine aktuelle Namens-/Kategoriezuordnung je registrierter ID, getrennt von historischen Produktionsangaben. |
| Rasterlogik | Maße, Lösungsmatrix und Bedeutung der logischen Farbkennungen. Hinweise sind abgeleitete Daten. |
| Darstellung | Abschlussbild und Hintergrund haben eigene Inhaltsbindungen. Ein Bildwechsel ist keine Rasterrevision. |
| Produktionshistorie | Bestehende Exporte, Receipts, Freigaben und Rechte behalten ihren damaligen Inhalt. Neue Editorquellen folgen §13 und behaupten keine frühere Produktionsfreigabe. |

Ein Bytehash darf sich ändern, ohne Rätselidentität oder Spielstandkompatibilität
zu ändern. Name, Kategorie, Bildbytes und JSON-Formatierung gehören nicht zur
logischen Identität. Prüfungen binden die tatsächlich relevanten Eingaben.
Unveränderte Logik erfordert keinen neuen Solver-/Schwierigkeitslauf. Neue
Bilddateien und Kategoriebezüge werden dennoch fachlich geprüft.

Editor, CLI, Standardproduktion und Laufzeitprojektion verwenden dieselbe
Auflösung der aktuellen Daten. Eine Pflege im Editor darf nicht durch einen
späteren Produktionsschritt aus historischen Angaben überschrieben werden.

## 3. Namen und Kategorien

Der bestehende Anzeigenamenbereich von 1 bis 128 Zeichen und nicht ausschließlich
Whitespace bleibt erhalten. Kategorien behalten den exakten Wertebereich aus
[CATEGORIES](../game/CATEGORIES.md), insbesondere ihre stabilen IDs. Neue Kategorie-IDs
werden einmalig kollisionsfrei erzeugt; ein späterer Anzeigenamenwechsel ändert
die ID nicht. Bestehende technische `order`-Werte bleiben, neue Kategorien werden
automatisch angehängt. Erschöpfte Vertragsgrenzen werden als Fehler gemeldet.

Jedes registrierte Rätsel gehört genau einer aktuell vorhandenen Kategorie an,
auch wenn es nicht sichtbar ist. Beim Löschen einer belegten Kategorie muss der
Benutzer eine andere vorhandene Kategorie wählen. Neuzuordnung und Löschung
bilden einen gemeinsamen Speichervorgang. Historische Kategorien in alten
Produktionsbelegen werden dadurch weder umgeschrieben noch zu einer Pflicht,
die gelöschte Kategorie im aktuellen Katalog weiterzuführen.

## 4. Bilder und Hintergrundauswahl

### 4.1 Fertige Dateien unverändert importieren

Import übernimmt genau die ausgewählten Dateibytes in den verwalteten Assetbereich.
Die weitere Nutzung hängt nicht vom ursprünglichen externen Speicherort ab.
Keine Skalierung, Drehung, Beschneidung, Leinwanderweiterung, Freistellung,
Farbkonvertierung oder Neukodierung im Editor. Prüfung und Vorschau verändern
die Quelle nicht. Ein unzulässiger Eingang wird mit erwarteten und tatsächlichen
Eigenschaften zurückgewiesen; es gibt keine automatische Reparatur.

| Bildtyp | Importgrenzen |
| --- | --- |
| Hintergrund | Fertiges Einzel-PNG nach einem ausdrücklich unterstützten [Hintergrundprofil](../production/PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile), höchstens 32 MiB. Profil, Geometrie, sRGB-/Alphaeigenschaften und Mindestbelegung werden gemeinsam geprüft. |
| Abschlussbild | Bestehende PNG-/begrenzte lokale SVG-Zulassung und Bildprüfung. Höchstens 32 MiB, 8192 Pixel je Achse und 8.000.000 Pixel insgesamt; mindestens zwei Bildpixel je Rasterzelle in jeder Achse. PNG bereits korrekt orientiert. |
| Abschlussbildgröße | Keine neue Einheitsgröße, keine Gleichheit mit den bisherigen Bildmaßen und kein erzwungenes Seitenverhältnis zum Raster. |

Der [Transparenzstandard](../production/REVEAL_TRANSPARENCY.md) bleibt inhaltlich maßgeblich.
Ein technischer Alphacheck ersetzt keine menschliche Motivbeurteilung. Auswahl
und Speichern durch den Eigentümer erfassen die manuelle Inhaltsentscheidung;
es wird weder ein KI-Auftrag noch eine erfundene frühere Produktionsfreigabe erzeugt.
Gültige historische Assets verhindern eine reine Namens-/Kategoriepflege nicht.

Der vorhandene [Hintergrundweg](../production/PUZZLE_BACKGROUNDS.md) leitet Originale deterministisch
ab und kodiert sie dabei neu. PE benötigt einen gesondert versionierten Eingang
für bereits fertige Assets; er darf nicht behaupten, eine solche Ableitung sei
ausgeführt worden. Die reguläre Produktionsableitung bleibt für ihre Eingänge
bestehen. Der spätere isolierte Godot-Texturimport ist ein davon getrenntes
Laufzeitnebenprodukt; Quellbilder bleiben bytegleich.

Ein Formatwechsel eines Abschlussbilds darf nicht in einen Writer eingeschleust
werden, der einen unveränderten Dateipfad beziehungsweise dieselbe Endung verlangt.
Der aktuelle Writer führt zulässige PNG-/SVG-Wechsel samt verwaltetem Zielpfad
und aktueller Referenz gemäß §13 aus.

### 4.2 Drei verständliche Hintergrundzustände

| Auswahl | Wirkung |
| --- | --- |
| Standard | Vorhandene Standardzeichnung der aktuell zugewiesenen Kategorie; ohne solche Zeichnung kein Hintergrund. |
| Eigenes Bild | Individuelles importiertes Bild ersetzt die Kategoriezeichnung. |
| Kein Hintergrund | Kategoriezeichnung ausdrücklich unterdrücken. |

Alle Wechsel zwischen diesen Zuständen sind Teil des Gesamtumfangs. Der Bestand
ohne individuelle Bindung startet ohne optische Änderung mit Standard. Ein
Kategoriewechsel aktualisiert die Standardvorschau; eigenes Bild und ausdrückliches
Kein Hintergrund behalten ihre Bedeutung. Eine defekte individuelle Quelle ist
ein Fehler und kein stiller Wechsel zu einem anderen Zustand.

Die geschlossenen aktuellen Bildquellen stehen in [RI](../production/PUZZLE_INTEGRATION.md),
die Runtimeprojektion in [RI-ONE §2.1](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md#21-geschlossene-aktuelle-runtimeprojektion).
Historische `legacy`-Werte werden nicht als neue manuelle Entscheidung ausgegeben.

## 5. Rastertext und Spielstandrevision

Das Textfeld bearbeitet die numerische `solution`-Matrix: Zeilen von oben nach
unten, Zellen von links nach rechts, `0` leer, positive Werte als vorhandene
Palette-IDs. Fehler nennen Zeile/Zelle und Ursache. Dimensionen und Palette
werden geprüft, `rows/columns` reproduzierbar erzeugt. Ungültige oder noch nicht
erfolgreich geprüfte Änderungen werden nicht in den spielbaren Bestand übernommen.
Ein eigener dauerhafter Entwurfsbestand ist für den ersten Editor nicht erforderlich.

Eine echte Änderung der kanonischen Rasterlogik erhöht die spielstandrelevante
Revision genau einmal pro erfolgreicher Übernahme. Identische Wiederholung,
andere Textformatierung oder identisch abgeleitete Hinweise erhöhen sie nicht.
Name, Kategorie und Bildwechsel erhöhen sie ebenfalls nicht. Der Editor führt
die erforderlichen bestehenden Logik-/Qualitätsprüfungen selbst aus; kein KI-Gate.
Eine veränderte Logik darf keine unverändert behauptete alte Bewertung übernehmen.

Beim nächsten Laden im Spiel beginnt ein eindeutig zuordenbarer Spielstand einer
älteren Rasterrevision desselben Rätsels automatisch neu. Zellen, History/Redo,
Undo-Merkmal, Abschluss, rätselbezogene Ansicht und alter Fortsetzen-Merker
werden zusammen behandelt. Andere Rätsel und allgemeine Einstellungen bleiben.
Ein kurzer Hinweis erklärt die Rätselüberarbeitung. Neue Fortschritte der aktuellen
Revision bleiben bei weiteren Starts erhalten.

Ein gültiger aktueller Primärstand beziehungsweise ein gültiges aktuelles Backup
hat Vorrang. Alte Backups dürfen weder alte Fortschritte zurückbringen noch nach
erfolgreichem Wechsel das Speichern blockieren. Unlesbare Daten, unbekannte
Saveformate, falsche IDs und höhere gespeicherte Revisionen bleiben Fehler-/
Recoveryfälle; ein Git-Downgrade löscht keinen neueren Spielstand automatisch.
Die Erkennung einer älteren Revision verwendet einen lesbaren, konsistenten
Speicherumschlag mit unterstütztem Schema, gleicher ID und positiver kleinerer
Revision. Sie verlangt keine Prüfung gegen eine nicht mehr verfügbare alte Lösung
und übernimmt keine alten Zellen in das neue Raster.

Der Revisionswechsel ist wiederholbar und abbruchsicher. Die bestehenden vollständigen
Prüfungen aktueller Saves bleiben. Editor und Inhaltswriter greifen auf kein
Spielerprofil zu; die Laufzeit behandelt den Wechsel. Die allgemeinen Save-/Recoveryregeln stehen in [P1](../game/PROTOTYPE_P1.md);
der automatische revisionsbedingte Neustart wird in §9.3 festgelegt.

## 6. Gemeinsamer Zugriff, Speichern und Effizienz

Ein lokaler Python-Dienst verwendet die vorhandenen Fachfunktionen und gemeinsame
Writer. Die Browseroberfläche schreibt nicht an ihnen vorbei. Der Dienst bindet
nur lokal und begrenzt Dateizugriffe auf den bewusst geöffneten Checkout und
ausgewählte Importe; ein öffentliches Hosting wird nicht eingerichtet.

Ein Speichervorgang darf mehrere geänderte Felder zusammen übernehmen. Vor der
Mutation werden Eingaben, Ausgangsstand und betroffene Referenzen geprüft.
Zwischenzeitliche fremde Änderungen erzeugen einen Konflikt statt Überschreiben.
Zusammenhängende Dateien werden unter dem gemeinsamen Checkoutlock mit
vorhandener Transaktions-/Recoverysemantik übernommen; Runtime zuletzt. Offene
Journale werden nicht ignoriert. Ein No-op verändert keine Bytes oder mtimes.

Die aktuelle Namens-/Kategorieansicht wird aus einem kleinen Katalog einmal
geladen und nach ID aufgelöst. Dafür werden nicht sämtliche Rasterbilder oder
Produktionsbelege geöffnet. Die jeweils benötigten Prüfungen folgen der gezielten Grenze aus §13;
eine Texteingabe startet keine Bestandsprüfung. Dateihashes bleiben Integritäts- und
Konfliktschutz; sie sind keine fachlichen Rätsel-IDs.

PE verspricht keinen unbelegten Geschwindigkeitsgewinn. Der heutige Spielstart
lädt viele Definitionen/Saves bereits vorab. Ein allgemeiner Umbau dieses
Startverhaltens ist kein verdeckter Teil des Editors. Konkrete Engpässe werden anhand gemessener Zugriffe und Laufzeiten behandelt.

## 7. Metadatenpflege

Die Editoroberfläche verwendet für Namen, Kategoriezuordnung und Kategorienaktionen
den aktuellen Request und gezielten Änderungsplan aus §13. Technische Kategoriegrenzen
stehen in [CATEGORIES](../game/CATEGORIES.md), aktuelle Registryformen in [RI](../production/PUZZLE_INTEGRATION.md).
Die früheren PE-A1-v4/v7-Migrations- und Journalformen sind im
[historischen §7](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_EDITOR.md#7-pe-a1-geschlossener-metadatenvertrag)
erhalten. Sie sind keine aktuellen Writer- oder Recoveryeingänge.

### 7.1 Getrennte aktuelle Metadaten-Fach-API

`catalog_metadata.view/plan/apply` bleibt als separate Fach-API am aktuellen
Katalog verfügbar. Die normale Editoroberfläche und `metadata_cli plan`
verwenden den gezielten Änderungsplan aus §13. `metadata_cli apply` liest
zusätzlich die folgende aktuelle Metadatenplanform; daraus entsteht keine
v4/v7-Migrations- oder Altjournalunterstützung.

| Form/Feld | Exakter Inhalt |
| --- | --- |
| `picross-editor-metadata-plan-v2` | `format,operation,operations,changes,files,journal`; `operation=metadata`. |
| `operations` | Geprüfte Metadatenoperationen nach §13.2; bei `category_create` ist die erzeugte stabile `id` im Plan ergänzt. |
| `changes` | Fachliche Vorschau als Liste mit `kind,id,before,after`; `kind=puzzle` oder `category`. |
| `files` | Sortierte tatsächlich geänderte Pfade; keine zusätzliche Schreibautorität. |
| `journal` | Aktuelles `picross-current-catalog-journal-v1` nach [SD-Catalog](../difficulty/SD_CATALOG.md#aktuelle-katalogjournale); dessen geschlossene Felder, Größe und Recovery gelten unverändert. |
| Journaloperation | `operation=metadata`, `report_run=null`, `additions={}`, `replacements={}`. |
| `old,new` | Gleiche geschlossene Menge benötigter aktueller Quellen; Pfad → UTF-8-Text oder null für gebundene Abwesenheit. |
| `retained` | Pfad → SHA-256 der unveränderten aktuellen Bildbytes. Keine Produktionsarchive oder alten Paketnamespaces. |
| Plangröße | Höchstens 32 MiB. |

Diese Fach-API bindet die aktuellen gemeinsamen Katalogquellen und prüft ihre
Projektion vollständig. Ihre Schreibmenge ist ausschließlich Registrymetadaten,
Kategorien und daraus abgeleitete Runtime; Definitionen, Bildquellen, Bewertungen
und Datumswerte bleiben erhalten. Die gezielte Lesegrenze der Editoroberfläche
aus §13 wird dadurch nicht erweitert. Gemeinsamer Lock, frische Quellprüfung,
Runtime zuletzt und aktuelle Katalogrecovery bleiben maßgeblich.

## 8. Bildpflege

Importgrenzen und drei Hintergrundzustände stehen in §4; Request, Bytebindung,
Schreibmenge und Recovery in §13. Die technischen Bildprofile definiert der
Hintergrundvertrag. Vorhandene historische Rechte-/Lizenzinformationen bleiben
erhalten; neue Editoraktionen erzeugen keine Provenienznotices.
Die früheren PE-A2-Quellen-, Notice-, Namespace- und Migrationsformen stehen im
[historischen §8](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_EDITOR.md#8-pe-a2-geschlossener-bild--und-präferenzvertrag).

## 9. Raster und Spielstandrevision

### 9.1 Rastereingang

`text` ist ein UTF-8-String bis 64 KiB mit einer nichtleeren Zeile je Matrixzeile.
Whitespace trennt vorzeichenlose Dezimaltokens. Ein abschließender Zeilenumbruch
ist erlaubt; CRLF und LF sind semantisch gleich. Jede Achse umfasst 1…50 Zellen.
`0` bezeichnet leer; positive IDs müssen aus der unveränderten vorhandenen Palette
stammen. Fehlerpositionen sind 1-basiert. Die Profile `line` und `paired` verwenden
die bestehende Mono-/Farbverifikation; Paarwahl allein behauptet keine R4-Notwendigkeit.

Kanonisch gleiche Maße, Farb-ID-Semantik und Matrix lösen keinen Solverlauf,
keine neue Raster- oder Ratingrevision aus. Ohne weiteres Delta bleiben Bytes
und mtimes unverändert. Eine echte Logikänderung folgt §5 und §13.

### 9.2 Transaktion

Raster, ausdrücklich gewählte Metadaten und Bilder werden im gemeinsamen
gezielten Änderungsplan aus §13 verarbeitet. Neue dauerhafte Editor-Rasterpakete
oder historische Quellenketten werden dabei nicht erzeugt.
Die abgelösten PE-A3-Paket-, Plan- und Journalformen sind im
[historischen §9](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_EDITOR.md#9-pe-a3-geschlossener-raster--und-revisionsvertrag)
dokumentiert; sie ändern den aktuellen Vertrag nicht.

### 9.3 Sicherer automatischer Save-Neustart

Alte mittlere Hinweislesefenster müssen innerhalb der alten Linienlänge liegen:
`0 < start < end < width` für Zeilen, entsprechend `< height` für Spalten.
Die alte Lösung wird dafür nicht benötigt; ein darüber hinausreichender Index
ist schon anhand des gespeicherten Umschlags unplausibel und bleibt Fehler.

Schema 1, Slotnamen und vollständige `SaveStore.validate`-Prüfung aktueller
Revisionen bleiben. Ältere Erkennung verlangt den exakten Schema-1-Umschlag,
gleiche ID, Integerrevision `0 < saved < current`, plausible positive Maße,
typisierte Zellen, History/Redo mit konsistentem Replay und Viewgrundformen.
Keine Prüfung gegen eine nicht mehr vorhandene Alt-Lösung. Unlesbare, fremde,
höhere oder unbekannte Fassungen werden nicht automatisch entfernt.
Gültiges aktuelles Primary hat Vorrang, sonst aktuelles Backup mit bestehender
bewusster Restoresemantik. Ein eindeutig altes Backup sperrt aktuelle Saves nicht.

Vor automatischem Entfernen entsteht im selben Slotverzeichnis ein atomar
publizierter Marker `<save_slot>.revision-reset.json`, Format
`picross-save-revision-reset-v1`, exakt `format,id,revision,files,recent`.
`files` ist exakt `.json,.bak,.tmp` → SHA-256 oder null für geprüfte Abwesenheit.
`recent` ist SHA-256 der eigenen alten Merkerdatei oder null; die Merkerdatei
wird nur bei derselben ID entfernt. Zielrevision 1…1.000.000, gleiche ID/Slot.
Marker-Temp ist ausschließlich `<save_slot>.revision-reset.tmp` und wird vor
Publikation vollständig geschrieben, geflusht und zurückgelesen. Fremde
Temp-/Markerbytes blockieren. Vor jedem Schritt werden Marker und alle noch
vorhandenen Zielbytes erneut geprüft; nur gebundene eigene Hashes oder bereits
entfernte Dateien sind zulässige Recoveryzustände. Neue aktuelle Fortschritte,
fremde Slots und allgemeine Präferenzen bleiben erhalten; Konflikt stoppt.
Alle Schreib-/Reparatur-/Resetwege beachten offene Marker. Erst nach vollständigem
eigenen Reset werden Marker und eigener Temp entfernt. Webpersistenz erhält
den Abschluss über die bestehende Bridge. Der sachliche deutsche Hinweis wird
nur nach abgeschlossenem automatischem Reset gezeigt, nie aufgrund alter Bytes.

## 10. Lieferung und Abnahme

Technischer Lieferstand, unabhängiges Review, persönliche Bedienprobe und Merge
sind getrennte Aussagen und werden am tatsächlichen Issue-/PR-Stand geprüft.
Die frühere Aufteilung in PE-A1/A2/A3/B steht im
[historischen §10](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_EDITOR.md#10-lieferung-abnahme-und-paketgrenzen).
Aktuelle Änderungen wählen ihren Prüfplan nach [CI-Workflow](../ci/CI_WORKFLOW_V2.md);
eine frühere Paketliste ist kein Dauerauftrag.

## 11. PE-B: lokaler Dienstvertrag v1

Lokaler HTTP-Vertrag auf Grundlage der
[PE-B-Entscheidung](https://github.com/venomenon328/picross/issues/576#issuecomment-6855913029),
mit den aktuellen gezielten Operationen aus §13.
Programmcode und UI kommen ausschließlich aus `tools/puzzle_editor/` und dem
gebundenen Programmpaket. Das lokal im Starter gewählte bestehende Checkout
liefert nur Daten. Keine Codeimporte, Gitbefehle oder externen URLs aus diesem
Checkout. Windowsausgaben gemäß §14; keine PW-Zustandsübernahme.

### 11.1 Transport, Sitzung und Lebenszyklus

Nur HTTP auf `127.0.0.1:<tatsächlich gebundener Port>`.
Der Windows-Listener setzt vor Bindung `SO_EXCLUSIVEADDRUSE` und deaktiviert
`SO_REUSEADDR`; auch ein späterer zweiter Prozess darf denselben Port nicht teilen.
Feste statische GETs
`/`, `/app.js`, `/style.css`; alle Daten unter `/api/pe/v1/`. Exakter Host,
kein Query/Fragment/Prozentpfad, kein CORS, Fetch-Site nur fehlend/none/same-origin.
Jeder API-Aufruf benötigt `X-PE-Session` mit 256-Bit-Sitzungsgeheimnis;
POST zusätzlich exakt den eigenen Origin. Fehlender Origin ist nur lesend erlaubt.
Der Starter öffnet die UI mit Token im Fragment; JS entfernt das Fragment sofort
und hält die Sitzung in tabgebundenem sessionStorage, niemals Inhaltsentwürfe.
Alle Antworten: no-store, nosniff, keine Referrer; CSP beschränkt Skript/Stil/API
auf eigene Ressourcen und Bilder auf Blob-URLs. SVG nur nach bestehender Prüfung
als Bild-Blob, nie als Dokument, HTML, object oder Inline-SVG.

Keine Transfer-Encoding-/Chunked-Anfragen, doppelte Längen-/Typ-/Sicherheitsheader
oder Bodies an GET. POST genau eine dezimale Content-Length und passenden Typ.
JSON streng UTF-8, ohne doppelte Schlüssel/NaN; höchstens 256 KiB. Upload roh,
1…32 MiB, Content-Type image/png oder image/svg+xml. Socket-Lesegrenze 15 s;
höchstens acht gleichzeitige Requests, davon nur eine fachliche Operation.
Fehler sind `{format:"picross-pe-error-v1",error:<Text>}` mit 400 (Eingabe),
403 (Sitzung/Ursprung), 404 (Route), 409 (belegt/stale beziehungsweise
Fach-/Zustandskonflikt einer Operation) oder 413 (Länge).
JSON-Erfolgsantworten haben `format:"picross-pe-api-v1"` und die unten benannten
Felder; die Einstellungen antworten ausschließlich mit `{theme}`. Bild-/statische
GETs liefern ihre jeweiligen Originalressourcen. Ein asynchrones Fachergebnis
steht im `result` des Jobstatus und hat die jeweilige unten genannte Form.

Ein OS-Lock pro kanonischem Checkout verhindert zweite Editorinstanzen auch
bei unterschiedlichem Port/Zustandsordner. Ein Zweitstart meldet die laufende
Zuordnung; fremde Prozesse werden nie beendet. Belegter Port führt im Starter
zur bewussten Wahl eines freien Ports. Tabende beendet keinen Prozess.
Stop sperrt neue Arbeit und wartet auf bereits gestartete Reader/Writer,
bevor Server, eigene Tempdaten und Lock geschlossen werden. Kein Kill einer
Mutation. Offenes gemeinsames Journal verlangt ausdrücklich Recovery.

### 11.2 Geschlossene Routen und Formen

Alle Objekte geschlossen. Kennungen sind serververgebene 32-stellige Hexwerte,
Puzzle-IDs müssen im aktuellen validierten Katalog vorkommen. Ein Plan bleibt
höchstens zehn Minuten gültig, Uploads höchstens 15 Minuten, höchstens zwei
Uploads und ein Plan gleichzeitig. Jeder neue Upload/Plan entwertet alte Pläne.
Kein frei übergebener Datei-/Checkoutpfad und keine Kommando-API.

| Methode/Route | Exakter Eingang / Ergebnisfelder zusätzlich zu format |
| --- | --- |
| GET `status` | Kein Body; `checkout,origin,stopping,recovery_required,job`. job null oder `{id,operation,state,stage,elapsed_seconds,result,error}`, state running/done/error. Status führt keine Vollprüfung aus. |
| GET `settings` | Kein Body; exakt `{theme}` ohne `format`; `theme=light` oder `dark`. Kein Fachworker oder Katalogzugriff. |
| POST `settings` | Exakt `{theme}` mit `light` oder `dark`; Ergebnis exakt `{theme}` ohne `format`. Aktualisiert nur die Programmeinstellung gemäß §13.4. |
| GET `catalog` | Kein Body; `snapshot,categories,entries,runtime_format,migration_required`. Die Katalogansicht liest aktuelle Indizes; snapshot bindet deren Bytes und Runtime. Keine Bild-/Paketprüfung in Suche/Filter. Ein inkompatibler Stand erlaubt keine Mutation; der Editor bietet keine Migration. |
| POST `detail` | `{id,snapshot}`; startet Job. Ergebnis exakt `detail,raster,snapshot,definition_sha256,source_migration_required,pictures`; gezielte Ansichten gemäß §13. `pictures={reveal:[asset-id],background:[asset-id],paper:asset-id}` mit null bis zwei Hintergrundbildern. Keine Vollbestandsprüfung. |
| GET `image/<asset-id>` | Tokenheader, kein Body. Nur im Detail/Upload freigegebene aktuelle Datei; Ref-Hash/Bytes und Pfadsicherheit beim Abruf erneut prüfen. Originalbytes, kein Encoding. |
| GET `standard/<category-id>` | Nur aktuelle validierte Kategorie; `assets` mit null bis zwei opaken Bildkennungen für die vorhandene Kategoriezeichnung. Keine Definition-/Paketprüfung, kein freier Bildpfad. |
| POST `upload/<reveal|background>/<png|svg>` | Rohbytes, Hintergrund nur png. Startet Prüfjob; Ergebnis exakt `upload,asset,sha256,bytes` mit opaker Import- und Vorschaukennung; keine Clientdateinamen/Pfade. Vor Vorschau vorhandene Bildprüfer aufrufen; keine unvalidierten SVG ausliefern. |
| POST `plan` | `{snapshot,id,metadata,text,profile,reveal,background}`. Bei `id=null` genau eine `category_create`-, `category_rename`- oder `category_delete`-Operation in metadata; alle übrigen Fachfelder null. Sonst metadata null oder die aktuelle ID-Änderung, text null oder Rasterstring, profile line/paired, reveal null oder `{upload}`, background null oder `{status,upload}`. Kein authority-/provenance-Feld. |
| POST `apply` | `{plan,id}`; gebundener vorbereiteter Plan, ID null ausschließlich bei Kategorienaktion. Frische relevante Altbyte-/Planhashprüfung gemäß §13; Ergebnis tatsächliche Writerquittung. |
| POST `recover` | `{confirmed:true}`; gezielte Pending-Prüfung und bei vorhandenem Journal gemeinsames `content_registry.recover`. Ohne Journal/Staging bestätigter No-op ohne Vollbestandsprüfung. Keine freien Restore-/Löschpfade. |
| POST `discard` | `{confirmed:true}`; eigene Pläne/Uploads verwerfen, `discarded:true`; keine Inhaltsdatei ändern. |
| POST `stop` | `{confirmed:true}`; `stopping:true`, anschließend geordnetes Drain. |

Detail/Upload/Plan/Apply/Recovery liefern zunächst 202 mit `job`-Kennung.
Polling über status liefert den echten Abschluss. Nur ein Workerprozess aus dem
vertrauenswürdigen Programmpaket arbeitet seriell; Kontrollstatus bleibt erreichbar.
Stage zeigt gestartete Fachoperation/Originaldiagnose und verstrichene Zeit,
keine simulierten Prozentwerte. Fachbudgets bleiben je 300 s; Abbruch eines
Requests beendet keine Mutation. Fertige Ergebnisse bleiben bis zur nächsten
Operation/Stop. Ein Planresultat enthält exakt
`plan,id,plan_hash,kind,files,before,after,quality,logic_changed,expires_seconds`;
kind metadata/images/raster. Vorher/nachher stammen aus dem echten Plan.
Apply vergleicht Planbundle, Eingangsbytes, Snapshot, ID, Sitzung und Frist frisch.
Alle Änderungen verwenden denselben gezielten Writer aus §13;
Kategorien bleiben eine eigene Aktion.

### 11.3 Ablage, Benutzerführung und Lieferung

Uploads, Requests, Planbundle, Workerprofile und Protokolle liegen in einem
eigenen temporären Verzeichnis außerhalb des Inhaltscheckouts. Sichere I/O-Guards
gelten für Wurzel, Vorfahren und einzelne Dateien einschließlich Junctions,
Hardlinks, Aliase und Austausch während des Lesens. Die bei Import geprüften
unveränderlichen Bildbytes bleiben über den vorbereiteten Plan gebunden;
Apply prüft dessen Planhash und relevante Altbytes nach §13, ohne die
Bildvorbereitung erneut auszuführen. Bei Ablauf/Verwerfen/Stop eigene Daten beseitigen;
gemeinsame Recoverydaten im Checkout niemals automatisch löschen.
Lokale Einstellungen und GET/POST `settings` folgen §13.4.

Ungespeicherte Felder werden markiert; Auswahl-/Kategorie-/Checkoutwechsel sowie
Refresh verlangen Übernehmen oder bewusstes Verwerfen. Prüfen schreibt keine
Inhalte. Vorschau nennt Dateien, Änderungen und bei echter Rasterrevision den
Neustart genau dieser ID beim nächsten Laden. Palette unveränderbar; Dimensionen
und Hinweise deterministisch aus numerischem Text, Zellfehler 1-basiert.
Nach Apply tatsächlichen Katalog und Detail neu laden. Git/Build/Veröffentlichung
bleiben extern. Der aktuelle Editor bietet keine Migrationsaktion.

Portable Windowsausgabe bindet CPython 3.13.14 x64, Pillow 12.3.0, Tcl/Tk und
alle Fachmodule, UI, Schemata und Lizenzen. Build prüft Versionen, vollständiges
Bundleinventar und saubere Quellbindung, kein Laufzeitdownload. Entwicklerstart
`python -m tools.puzzle_editor` verwendet denselben Starter/Dienst.
Bedienung/Bau und technische Einschränkungen stehen in der
[Werkzeuganleitung](../../tools/puzzle_editor/README.md). Die jeweils erforderlichen
Reviews und persönlichen Proben ergeben sich aus dem aktuellen Auftrag.

## 12. Betriebsdiagnose und Effizienz

Detail, Planung und Übernahme sind getrennte Vorgänge mit jeweils endlichen
300-s-Rahmen. Ein allgemeiner Cache ersetzt keine frische relevante Quellbindung.
Die genaue Lese-, Prüf- und Schreibgrenze sowie zulässige Vorbereitung stehen in
§13. Frühere T8/K8/C8-Vollbestandsbindungen sind keine zusätzliche Editorpflicht.

Der Jobstatus zeigt die tatsächlich betretene Prüf-/Publikationsphase und monoton
verstrichene Zeit. Es gibt keine geschätzten Prozentwerte. Phasen und I/O-Zähler
sind Betriebsdiagnose außerhalb fachlicher Plan-/Journalidentitäten.
Kontrollstatus und geordnetes Beenden bleiben erreichbar; Stop wartet Reader und
Writer sicher ab. Diagnosefehler erweitern keine Schreibbefugnis. Fehler nennen
Phase, lesbaren Runtimezustand oder unbekannt sowie den wirklichen Journal-/
Recoverybedarf, ohne Sitzungstoken oder private Pfade offenzulegen.

Ein verlorenes Browserergebnis ist kein Rollbackauftrag: frischer Readback
entscheidet zwischen erledigt und offen. Die früheren einmaligen Performanceproben
und der abgelöste Vollbestandsvertrag stehen im
[historischen §12](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_EDITOR.md#12-pe-perf1-gebundene-effizienz-und-betriebsdiagnose).

## 13. PE-EDIT2: gezielte Pflege statt Vollbestandsprüfung

Aktueller gezielter Schreibvertrag gemäß
[#640](https://github.com/venomenon328/picross/issues/640) und RI-ONE.
Neue Pläne verwenden ausschließlich diesen Weg; alte Journale werden nicht als
aktuelle Recoveryeingänge zugelassen. Die einmalige Bestandsüberführung gehört
zur Einführungshistorie, nicht zum normalen Editorbetrieb.

### 13.1 Lese- und Prüfgrenze

Start/Liste lesen nur Inhaltsregistry, Runtime und Kategorien. Detail liest
zusätzlich die ausgewählte Definition und ihre kleinen aktuellen Bildreferenzen;
sichtbare Bilder werden bedarfsweise geladen. Keine rekursive Inventur, keine
Pakete, historischen Freigaben oder unbeteiligten Einzeldateien, auch nicht im
Hintergrund. Name/Kategorie/Kategorienpflege benötigen ausschließlich die drei
Indizes. Lesen und Schreiben verlangen den aktuellen Katalog mit Runtime v8.
Es gibt keine Migration in UI, Dienst, Worker oder portablem Paket. Die einmalige Bestandsüberführung gehört zum RI-ONE-Produktdiff; kein
dauerhafter Legacyimporter wird installiert.
Die unveränderten Runtimezeilen werden übernommen, nicht aus allen Definitionen
rekonstruiert. Suche und Sortierung laufen ausschließlich im Browserspeicher.

Ein Bildimport prüft nur seine neuen Bytes auf bestehende Format-, Größen-,
Alpha- und SVG-Grenzen. Rastertext wird kanonisch verglichen; nur geänderte Logik
startet den bestehenden Solver-/Ratingweg samt unabhängiger Proofprüfung für
diese ID. Apply verwendet dessen vorbereitete Bytes ohne erneute Analyse.
Beschädigte, nicht benötigte historische Belege blockieren die Pflege nicht.
Normale Editorrequests benötigen keine Herkunfts- oder Akteursfelder und
erzeugen keine Platzhalter oder erfundenen Herkunftsnotices. Eine aktuelle
Produktionsübergabe darf tatsächlich angegebene Rechte für ihren ausgewählten
neuen Hintergrund kompakt mitgeben; der gemeinsame Writer erhält diese
Angaben als aktive Notice. Bibliothekslizenzen bleiben erhalten.
Derselbe Grundsatz gilt für den späteren Mainvergleich und den
[Abschluss nach Authoring Schritt 5 §9](../production/authoring/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung):
Ein unter PE-EDIT2 ausgewählter Hintergrund ohne Live-`.txt` ist vollständig;
der Abschlussreader darf keinen Ersatztext fordern oder erzeugen. Eine
tatsächlich vorhandene ältere TXT-Datei bleibt hingegen schutzwürdig und
wird unverändert gegen den bestätigten Mainstand verglichen; auch ihr Fehlen
wird als aktuelle Abwesenheit geprüft. Reveal-Notices und vorhandene echte
Rechte-/Lizenzinformationen bleiben unberührt.

### 13.2 Geschlossener Änderungsplan und kleines Journal

Der allgemeine CLI-Einstieg ist `python -m tools.puzzle_production.editor_cli`.
`list`, `detail --id`, `plan --request --output`, `apply --plan` und `recover`
verwenden jeweils `--target-root`. Die versionierte Requestform heißt
`picross-editor-request-v2`, mit exakt `format,id,metadata,text,profile,reveal,
background,imports`. `metadata` ist bei einer ID die optionale Name/Kategorie-
Änderung mit `name` und/oder `category_id`, sonst eine Liste der unten definierten
Kategorien-/Metadatenoperationen. Alle Requestfelder sind vorhanden; nicht
verwendete Einzeländerungen sind null. `text` ist optionaler Rastertext,
`profile` bei Rasteränderung `line` oder `paired`, sonst auch null; Reveal ist
null oder `{upload}`, Hintergrund null oder `{status,upload}`. Für eine
ausgewählte neue Hintergrunddatei erlaubt die aktuelle Produktionsübergabe
zusätzlich exakt `rights={author,usage_basis,source,changes}` mit den tatsächlichen
Angaben nach PW-B; keine leeren/erfundenen Texte und kein `rights` ohne Upload.
Der gemeinsame Editorwriter schreibt dafür ausschließlich
`game/art/backgrounds/<id>.txt` im selben geprüften Plan/Journal. Ohne dieses
explizite Feld bleiben vorhandene Notices unverändert; ein fehlender TXT bleibt
zulässig. `imports` ordnet
nur benutzte Uploadschlüssel relativen neuen PNG-/SVG-Pfaden neben dem Request
zu. Eingaben und Plan liegen außerhalb des Inhaltscheckouts. Kein Akteur,
keine Herkunft, Bestätigung oder implizite Migrationsaktion. Die HTTP-Route
`/api/pe/v1/plan` überträgt diese fachlichen Werte mit dem aktuellen Index-
Token und sitzungseigenen bereits geprüften Uploadschlüsseln.

| Metadatenoperation | Exakte zulässige Requestfelder und Wirkung |
| --- | --- |
| `set_metadata` | `op,id` und mindestens eines von `name,category_id`; verändert die genannten Metadaten einer vorhandenen Rätsel-ID. |
| `category_create` | `op,name`; erzeugt eine stabile ID `cat-` plus UUID-Hex und hängt die Kategorie nach der höchsten vorhandenen `order` an. Die separate Metadaten-Fach-API ergänzt diese erzeugte `id` in ihrem gespeicherten Plan. |
| `category_rename` | `op,id,name`; ändert nur den Anzeigenamen einer vorhandenen Kategorie. |
| `category_delete` | `op,id` und optional `reassign_to`; eine belegte Kategorie verlangt die vollständige Neuzuordnung auf eine andere vorhandene Kategorie. Ohne Belegung darf `reassign_to` fehlen oder null sein. |

Namen, IDs, Zuordnungen und Reihenfolge werden nach jeder einzelnen Operation
gegen den [Kategorienvertrag](../game/CATEGORIES.md) und den aktuellen Inhaltsindex
geprüft. Die CLI akzeptiert bei `id=null` eine Liste mit höchstens 10.000
Operationen; die Metadaten-Fach-API nimmt dieselbe Operationsliste direkt an.
Eine leere Liste ist ein No-op. Die HTTP-Route
beschränkt denselben Fall auf genau eine `category_*`-Operation. Bei `id=null`
sind `text,profile,reveal,background` stets null. Eine ausgewählte Rätsel-ID
verwendet stattdessen `metadata=null` oder das Name-/Kategorieänderungsobjekt.

Die logischen Formen sind geschlossene UTF-8-JSON-Objekte ohne Doppelschlüssel,
kanonisch mit abschließendem LF. Hashes sind SHA-256, Ganzzahlen keine bools.
Plan und entpacktes Journal sind auf 128 MiB begrenzt; einzelne Seiten auf
64 MiB, importierte Bilder weiterhin auf 32 MiB. Physisch speichert allein das
neue Journal die ASCII-Kennung `PICROSS-EDITOR-CHANGE-JOURNAL-V1` plus LF und
einen RFC-1950/zlib-Strom (Level 6) seines kanonischen JSON mit kanonischer Schlüsselsortierung.
Der Reader begrenzt bereits die Dekompression, verlangt genau einen vollständigen
Strom ohne Nachlauf und prüft die kanonische Rekodierung. Das vermeidet erneutes
Lesen der Base64-Vergrößerung der betroffenen Bildbytes; alte Journale werden nicht mehr als aktuelle Recoveryeingänge zugelassen.

| Form | Exakte Felder |
| --- | --- |
| `picross-editor-change-plan-v1` | `format,action,id,entry,reads,changes,before,after,quality,plan_hash` |
| `action` | `metadata`, `images` oder `raster`; Kategorienpflege ist metadata mit id/entry null. |
| `entry` | Der ausgewählte unveränderte Inhaltsregistryeintrag, bei Kategorienpflege null. Er begrenzt technische Zielpfade, keine erneute Produktionsabnahme. |
| `reads` | Pfad → SHA-256 oder null für tatsächlich benötigte aktuelle Quellen/Abwesenheiten. Keine Namespace- oder Vollbestandsbindung. |
| `changes` | Pfad → exakt `{old,new}`; jede Seite Base64 der tatsächlichen Bytes oder null. Nur unterschiedliche Seiten, ausschließlich tatsächliche Schreibmenge. |
| `before,after` | Lesbare fachliche Vorschau der betroffenen Werte; keine zusätzliche Schreibautorität. |
| `quality` | null ohne Logikänderung; sonst der tatsächlich erzeugte Rating-/Proofbefund mit `method,checked,proof,baseline,proof_data,baseline_data`. `proof` und gegebenenfalls `baseline` sind Byte-Refs `file,bytes,sha256`; die zugehörigen `*_data` enthalten die tatsächlich geprüften JSON-Belege. Ohne Paired-Profil sind beide Baselinefelder null. |
| `plan_hash` | Kanonischer Hash aller anderen Planfelder. |
| `picross-editor-change-journal-v1` | `format,action,id,entry,reads,changes,quality`; dieselben bereits vorbereiteten Quellen, Schreibseiten und gegebenenfalls Prüfbelege. |

Ein Zielpfad muss aus den drei Indexpfaden oder der ausgewählten Entry-ID und
ihren festen Definitions-/Bildstämmen herleitbar sein. Kategorienpflege
dürfen keine Einzeldateien schreiben. Keine freien Restorepfade, Spielstände,
Programmdateien oder fremden IDs. Quellen und vorbereitete Schreibseiten bleiben bytegebunden;
der Dienst bindet zusätzlich Sitzung, Plan-ID und zehnminütige Gültigkeit.
Ein sitzungseigener Worker hält höchstens die zwei ausdrücklich importierten,
einmal technisch geprüften Bytefolgen (15 Minuten) und einen vorbereiteten Plan
(zehn Minuten). Es gibt keinen Index-/Bestandscache und keine Leerlaufarbeit.
Jede neue Detail-/Planaktion liest ihre aktuellen kleinen Eingänge erneut;
Apply prüft den vorbereiteten Planhash und frisch die relevanten Altbytes.
Workerende verwirft die Vorbereitung, niemals ein offenes Recoveryjournal.
Der Browser hält nur bereits sichtbare Bilder der aktuellen Auswahl; reine
Kompositions- und Themeänderungen brauchen keinen erneuten Inhaltsread.
Ein alter sichtbarer Detailstand autorisiert kein Überschreiben neuer relevanter
Index-/Definitionsbytes. Metadatenänderungen hängen nicht an Raster-/Bildbytes.

Der gemeinsame exklusive Writerlock bleibt `content/.registration-pending.json`.
Die feste neue Journalstagingdatei heißt `content/.editor-change-journal.tmp`.
Beide werden gezielt geprüft. Keine Repositorysuche nach Journalen. Ein belegter
Lock oder fremdes/unklares Staging wird erhalten und blockiert neue Mutationen.
Vor der ersten Inhaltsänderung wird das vollständige Journal dauerhaft und
atomar ohne Ersetzen eines vorhandenen Locks veröffentlicht. Unter diesem Lock
werden alle relevanten Eingangs-/Zielaltbytes frisch verglichen. Vor jedem
Dateiersatz folgt ausschließlich dessen lokale Pfad-/Altbyteprüfung; Runtime
zuletzt. Kein erneutes Lesen sämtlicher Abhängigkeiten je Schreibziel.
Ergebnisse werden gezielt zurückgelesen. Flush und atomare Veröffentlichung
bleiben Pflicht. Ein No-op erzeugt weder Journal noch neue Dateien oder mtimes.

Recovery validiert Form, Pfade und alle betroffenen Zustände vor Mutation und
stellt nur exakt eigene Alt-/Neu-/belegbare temporäre Bytes wieder her. Fremde
Bytes stoppen mit erhaltenem Journal. Wiederholung bleibt möglich, Runtime
wird zuletzt zurückgestellt. Ein verlorener Browserabschluss allein löst keine
Recovery aus; frischer Readback entscheidet zwischen erledigt und offen.
Die gemeinsamen Recoverydispatches erkennen diese Generation ausdrücklich.

### 13.3 Aktive Quellen

Registry v5, Reveal v5 und Hintergrund v7 folgen exakt [RI](../production/PUZZLE_INTEGRATION.md).
Die geschlossene Runtime v8 steht in [RI-ONE §2.1](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md#21-geschlossene-aktuelle-runtimeprojektion).
`binding` enthält nur `identity` mit Key, Slot, aktuellem Definitionsref und
Runtime-Revision. Keine eingebettete Entry-Produktion, kein `origin`, kein
Paket-/Receiptanker. Namen, Kategorien und expliziter Mono-/Color-Modus kommen
aus der aktuellen Autorität. PNG/SVG und selected/none/standard bleiben erhalten;
Bildrevisionen erhöhen nur die tatsächliche aktuelle Bildrevision.

Der Editor führt keine automatische Migration aus. Runtime-/Rätselrevision,
Slots, Bewertung und Datum bleiben bei Bild-/Metadatenpflege gleich. Rasteränderung
verwendet das vorhandene Analyzer-/Proofverfahren für die betroffene neue Logik;
aktuelle Bildquellen werden an die neue Definition gebunden. Proof und gegebenenfalls
Baseline liegen im privaten Plan/Journaleingang, kein neues dauerhaftes Rasterpaket.
Unabhängige Verifikation bleibt vor Apply Pflicht; Recovery analysiert nicht neu.

### 13.4 Oberfläche, Einstellungen und Nachweise

Die Liste rendert nur sichtbare Zeilen plus kleinen Puffer, besitzt eine eigene
Scrollfläche und feste Suche/Kategorie/Sortierung (Name A–Z, Z–A, Kategorie/Name).
Tastaturfokus, ID-Auswahl, Filter und Scrollposition bleiben bei Speichern und
Verwerfen erhalten. Die Sortierung schreibt keine Inhaltsdatei.

Rastervorschau verwendet echte Matrix/Palette, Leerzellen, Gitter und Zoom/Fit.
Ungültiger Text nennt Zeile/Spalte und wird nicht als gültiges Raster angezeigt.
Die Bildkomposition verwendet statische aktuelle Spielressourcen: Papier,
Kategoriezeichnung/eigenes Bild/keine Zeichnung und proportionales Reveal.
Uploads erscheinen vor dem Speichern; Originalbytes bleiben unverändert.
Dark Mode verändert den Papierkontext und die Motivfarben nicht.

`config.json` außerhalb des Inhaltscheckouts enthält `checkout,port,theme`;
theme ist `light` oder `dark`, Altformen ohne theme lesen als light. Gemeinsames
serialisiertes, atomares Aktualisieren erhält die jeweils anderen Werte.
GET/POST `settings` lesen beziehungsweise ändern ausschließlich theme, ohne
Fachworker, Inhaltsdirty-Flag oder Katalogzugriff. Portwechsel und Neustart
verwenden dieselbe Programmeinstellung.

Die begrenzten Zugriffs-, Konflikt-, Recovery-, Metadaten- und Einstellungstests
prüfen diesen Vertrag mit synthetischen Daten. Historische Messbudgets und
Einführungsproben stehen in [#640](https://github.com/venomenon328/picross/issues/640);
sie sind keine erneute Abnahme eines bloßen Dokumentationsumbaus.


## RI-ONE · Abschluss aktueller Quellen

Für ausgewählte abgeschlossene Arbeit gilt [Authoring Schritt 5 §9](../production/authoring/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung).
Aktuelle Definitionen, Bilder, Notices, Ratings und Datumsdaten bleiben erhalten.
Kein neuer Receipt und kein Nachproduzieren entfernter Originale. Fachlich eigenständige
Bild-/Rasteränderungen bleiben eigene ausdrückliche Änderungsaufträge.

## 14. PE-APP-A · feste Windows-Produkt- und Releasebindung

Vertrag vor konsumierendem Code gemäß [#691 / PE-APP-A](https://github.com/venomenon328/picross/issues/691#umsetzungsvorbereitung-pe-app-a).
Der bestehende gezielte Editor aus §13 bleibt unverändert. MSI und portable
Diagnoseausgabe enthalten dieselben privaten Programmbytes; der Entwicklerstart
bleibt nutzbar. Der clientseitige Updateweg steht in §15.

Die feste PE-UpgradeGUID lautet `6A6CBDE3-60BA-4A72-A44E-D1F3AF186985`.
ProductCode ist UUIDv5 dieser GUID und der Version. Programmziel ist ausschließlich
`%LOCALAPPDATA%/Programs/PicrossPuzzleEditor`, Zustand bleibt
`%LOCALAPPDATA%/PicrossPuzzleEditor`. Registry und produktweites Running-Ereignis
verwenden `PicrossPuzzleEditor`; PW-Identitäten bleiben unverändert.
Installation, Upgrade und Uninstall verändern ausschließlich eigene Programmdateien
und Links. Alle laufenden PE-Instanzen veröffentlichen das Lebenszeichen vor
Einrichtung bis nach vollständigem Writer-Drain, unabhängig von Checkout/--state.
MSI prüft es und reale Dateibelegungen ohne Kill oder erzwungenen Neustart.

PE verwendet exakt die geschlossenen Feld-/Byte-/Asset-/Prüfformen des
[PW-Updatevertrags §6](PRODUCTION_UPDATES.md#6-app-b1--signierte-autorität-und-feste-roots),
mit folgenden ausschließlich festen Ersetzungen: `picross-pe-release-v1`
als unsignierte Bauprovenienz, `picross-pe-release-v2` als ausschließlich vom
Publisher erzeugte Updateautorität, `picross-pe-signature-v1`,
`picross-pe-trust-v1`, Signaturdomäne ASCII `picross-pe-release-v2` plus NUL.
Tags heißen `pe-vX.Y.Z`, MSI `Picross-Bestandseditor-X.Y.Z-windows-x64.msi`.
0.2.0 ist ausschließlich Portable-Startanker, erster MSI-Kandidat 0.2.1;
anschließend genau Patch +1 bei verändertem veröffentlichtem Fingerprint.
PW-Kandidaten sind in PE und PE-Kandidaten in PW unzulässig. Feste Produktadapter
kommen aus dem Programmpaket, niemals aus Inhaltscheckout oder Updateauftrag.

Der feste PE-Trust enthält denselben bereits freigegebenen öffentlichen
Ed25519-Root wie PW, mit eigener Format-/Signaturdomäne. Keine Schlüsselerzeugung,
keine dynamische Rootübernahme. `PE_RELEASE_ENABLED` und
`PE_UPDATE_SIGNING_ENABLED` sowie das vorbestehende exakt Main-only-Environment
`pe-app-release` sperren Veröffentlichung bis zum gesonderten Betriebsauftrag.
Nur dessen Publisher erhält `PE_UPDATE_SIGNING_KEY`; es muss zur festen Wurzel
passen. Die Implementierung allein autorisiert keine Änderung dieser Betriebsfreigaben.
Der tatsächliche Aktivierungs- und Abnahmestand steht in #691.

Der getrennte PE-Workflow prüft erfolgreiche Main-Push-Package-CI, aktuellen Head,
Payload und veröffentlichte PE-Autorität vor Bau und Veröffentlichung. Gleicher
Payload ist No-op; Diagnose-Dispatch kann nie veröffentlichen. Draft-first,
Rückdownload sämtlicher Bytes, monotone Versionierung, Teilupload-Recovery und
Rennschutz verwenden denselben Code wie PW. Kein PE-Pflichtmodul in Package CI.
Der Fingerprint bindet alle wirksamen Code-/Daten-/Collector-/Analysisinputs,
Papier-/Randressourcen, Anleitung, Pins und Lizenzen; unbekannte mögliche Inputs
stoppen. Testfixtures werden weder eingefroren noch als Methodenquellen kopiert.

Die technischen und persönlichen Einführungsnachweise werden in
[#691](https://github.com/venomenon328/picross/issues/691) geführt. Eine MSI-Inspektion
ersetzt keine persönliche Installations-/Bedienprobe und keine Betriebsfreigabe.


## 15. PE-APP-B · Startgate und sicherer Wiederanlauf

Vertrag vor konsumierendem Code gemäß [Paketentscheidung #691](https://github.com/venomenon328/picross/issues/691#umsetzungsvorbereitung-pe-app-b--startgate-selbstupdate-und-sicherer-wiederanlauf).
Der gemeinsame PW-Client, Verifier, private Stage und C#-Helfer verwenden nur
fest eingebaute PW-/PE-Adapter. PE bleibt auf pe-v0.2.x, eigener MSI-Identität,
Programmpfad und PE-Trust gebunden; Datencheckout und --state liefern keine
Programmautorität. PW-Wireformen und sein aktiver Releasebetrieb bleiben erhalten.

Das native Auswahlfenster erscheint zuerst. Eine eigene ausdrückliche Zustimmung
liegt unter --state/.updates/app-updates.json, mit der geschlossenen Form
picross-app-update-preference-v1 und ausschließlich format,enabled (Boolean).
Fehlende oder ungültige Zustimmung erlaubt keinen Netzabruf. Portable, Entwickler,
Worker und Service führen kein Installationsupdate aus. Nach Zustimmung höchstens
eine nebenläufige Prüfung vor der ersten Editor-/Browseraufnahme. Pfad und Port
bleiben bedienbar. Ohne Update fortfahren verwirft diesen Versuch, erhält aber
das Opt-in. Erst die atomare GUI-Übernahme des READY-Helfers sperrt Skip/Opt-out.
Ohne Update oder bei Fehlern wird der manuelle Editorstart freigegeben; kein
Gitrefresh, automatischer Editorstart oder weiterer Versuch in dieser Instanz.

Anonyme HTTPS-, Katalog-, Signatur-, Versions-, Asset-, Byte- und Zeitgrenzen
entsprechen [PW §7](PRODUCTION_UPDATES.md#7-app-b2--client-übergabe-und-abschluss).
Signiert bestätigte Gleichversion verlangt erneut dieselbe lokale MSI-/Source-/
Fingerprintidentität und meldet ausschließlich: Keine neuere Appversion
veröffentlicht. Keine lokale Manifestautorität aus Kandidatenbytes erfinden.
Eigene flache Stages, Pending und Ergebnisse liegen ausschließlich in .updates;
PW-Zustand bleibt getrennt. Fremde Dateien verhindern Bereinigung. Unbestätigte
Aufträge werden niemals wieder ausgeführt, Fehler nennen den manuellen Weg.

Der gemeinsame Helfer wird mit fester PE-Identität separat kompiliert. Sein
picross-pe-update-handoff-v1 verwendet die geschlossene PW-Feldmenge plus selection; no_browser
ist für PE immer true. state_hashes bindet config.json (Hash oder sichere
Abwesenheit) und .updates/app-updates.json. Die echte Elternprozesshandlebindung,
Benutzerprüfung, verifizierten Programm-/MSIbytes und noncegebundenes READY/GO
bleiben Pflicht. PE-Konfiguration samt Checkout, Port und Theme bleibt bytegleich.
selection ist ein kanonischer ASCII-JSON-String mit genau checkout und port als
Anzeigestrings (höchstens 8192 bzw. 16 Zeichen). Er erhält auch ungespeicherte
Auswahl und CLI-Vorgaben, ohne config.json zu schreiben. Änderungen zwischen
Snapshot und GUI-Übernahme verwerfen den Versuch. GUI-Eingaben beeinflussen
keine Installationsautorität. Nach READY: Service-/Writer-/HTTP-
Drain, vollständiger Abschluss eigener Threads und Desktopfinally; erst danach
GO. Der Helfer wartet zusätzlich auf das echte Ende des alten Prozesses samt
InstallInterlock. Andere PE-Instanzen und fremde Dateibelegungen sperren MSI.
Kein Kill, Elevation, erzwungener Reboot oder Update während einer Transaktion.

Erfolg verlangt MSI-Exit 0, neue registrierte Version, neue EXE-Bytes und einen
neuen authentisierten nativen PE-Start. Eine private zufällige Windows-Pipe
bindet den vom Helfer selbst gestarteten Prozess mittels echter Client-PID,
frischer Challenge und HMAC-SHA256 mit ausschließlich vererbtem Einmalgeheimnis.
Die Antwort bindet pid,commit,state,selection,challenge und den Hash beziehungsweise die
Abwesenheit von config.json. Antwort erst aus dem laufenden nativen Fenster;
kein HTTP-Editorstart, PID-/Fensterexistenzorakel oder Browserstart. Pipe und
Geheimnis sind flüchtig, nicht in Konfiguration, Logs oder Updateaufträgen.
state ist der SHA256 des UTF-8-Zustandspfads, selection der SHA256 des ASCII-
Auswahlstrings. Der neue Prozess verwendet denselben --state und erhält selection
nur über seine private Startumgebung; Theme bleibt aus unveränderter Konfiguration. Fehlende Bestätigung bleibt unconfirmed.

Technische Kandidatenprüfung, unabhängiges Review, persönliche Windows-/
Bedienprobe und Betriebsfreigabe werden in #691 getrennt nachgewiesen.
Dieser Vertrag allein autorisiert keine Erstpublikation oder Updateinstallation.
