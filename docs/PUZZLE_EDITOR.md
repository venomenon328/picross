# Lokaler Rätselbestand-Editor (PE)

Stand: 13.11.2026. **PE-A1 und PE-A2 sind nach unabhängigem Review über
[PR #577](https://github.com/venomenon328/picross/pull/577) und
[PR #623](https://github.com/venomenon328/picross/pull/623) integriert.**
[PE-A3](https://github.com/venomenon328/picross/issues/576#issuecomment-6848707827)
liefert den Rasterwriter und gezielten Save-Neustart gemäß §9;
unabhängige Abnahme und Merge bleiben eigene Schritte. PE-B bleibt Sollstand.
Auftrag, Kriterien und gebundene technische Nachweise
stehen im [PE-Issue #576](https://github.com/venomenon328/picross/issues/576)
und im jeweiligen Liefer-PR. PE-A2 beginnt auf
`main@907d40c8e08f6c7777cd579c8f214921c67efd9b`; der ursprüngliche
Spezifikationsstand wurde gegen `main@9cc07b411155adeab0aa6516ab5b4c4341f48184` geprüft.

Dieser Vertrag beschreibt ein persönliches Werkzeug außerhalb des Spiels.
Abschnitt 7 beschreibt das Metadatenfundament, §8 die gemeinsame
Bildpflege und §9 die geprüfte Rasterpflege. Die Weboberfläche folgt in PE-B.
Neue Rätsel folgen weiterhin [PUZZLE_AUTHORING](ai-workflows/PUZZLE_AUTHORING.md).

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
| Auswahl | Durchsuchbare Liste mit Name, Kategorie und Bildvorschauen; Kategorienfilter. Auswahl öffnet ein vorhandenes Rätsel. |
| Metadaten | Motivname und genau eine Kategorie direkt bearbeiten. Stabile IDs dienen der Zuordnung und sind keine gewöhnlichen Eingabefelder. |
| Kategorien | Anlegen, Anzeigenamen ändern, zuweisen. Löschen nur leer oder zusammen mit ausdrücklicher Neuzuordnung sämtlicher betroffener Rätsel. Keine Sortierungsverwaltung. |
| Bilder | Abschlussbild und Hintergrund ansehen, vorbereitete Datei auswählen oder hineinziehen, prüfen und unverändert importieren. |
| Hintergrund | Standard, eigenes Bild oder ausdrücklich kein Hintergrund. Auch erstmals bei einem bestehenden Legacyrätsel zuweisen und später zu Standard zurückkehren. |
| Raster | Nachgeordnete Textbearbeitung der Lösungsmatrix mit vorhandener Palette. Maße und Hinweise daraus ableiten beziehungsweise prüfen. Kein Zeichenwerkzeug und keine verpflichtende grafische Rastervorschau. |
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
| Produktionshistorie | Bestehende Exporte, Receipts, Freigaben und Rechte behalten ihren damaligen Inhalt. Eine manuelle Änderung wird ehrlich als solche geführt. |

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
[CATEGORIES](CATEGORIES.md), insbesondere ihre stabilen IDs. Neue Kategorie-IDs
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
| Hintergrund | Ein einzelnes, nicht animiertes, vollständig dekodierbares PNG, genau 2304 × 576 Pixel, höchstens 32 MiB; geeignete sRGB-/Alphaeigenschaften gemäß Hintergrundvertrag. Mindestens ein vollständig transparenter und ein sichtbarer Pixel. |
| Abschlussbild | Bestehende PNG-/begrenzte lokale SVG-Zulassung und Bildprüfung. Höchstens 32 MiB, 8192 Pixel je Achse und 8.000.000 Pixel insgesamt; mindestens zwei Bildpixel je Rasterzelle in jeder Achse. PNG bereits korrekt orientiert. |
| Abschlussbildgröße | Keine neue Einheitsgröße, keine Gleichheit mit den bisherigen Bildmaßen und kein erzwungenes Seitenverhältnis zum Raster. |

Der [Transparenzstandard](REVEAL_TRANSPARENCY.md) bleibt inhaltlich maßgeblich.
Ein technischer Alphacheck ersetzt keine menschliche Motivbeurteilung. Auswahl
und Speichern durch den Eigentümer erfassen die manuelle Inhaltsentscheidung;
es wird weder ein KI-Auftrag noch eine erfundene frühere Produktionsfreigabe erzeugt.
Gültige historische Assets verhindern eine reine Namens-/Kategoriepflege nicht.

Der vorhandene [Hintergrundweg](PUZZLE_BACKGROUNDS.md) leitet Originale deterministisch
ab und kodiert sie dabei neu. PE benötigt einen gesondert versionierten Eingang
für bereits fertige Assets; er darf nicht behaupten, eine solche Ableitung sei
ausgeführt worden. Die reguläre Produktionsableitung bleibt für ihre Eingänge
bestehen. Der spätere isolierte Godot-Texturimport ist ein davon getrenntes
Laufzeitnebenprodukt; Quellbilder bleiben bytegleich.

Ein Formatwechsel eines Abschlussbilds darf nicht in einen Writer eingeschleust
werden, der einen unveränderten Dateipfad beziehungsweise dieselbe Endung verlangt.
PE-A2 schließt zulässige PNG-/SVG-Wechsel einschließlich verwaltetem Zielpfad,
aktueller Referenz und historischer Herkunft in §8.

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

Runtime v6/v7 kennt `legacy/selected/none`; `legacy` bleibt eine historische
Ableitung. PE-A2 führt `standard` und die Legacy-Erstzuordnung ausdrücklich in
Quellen v3/v5 und Runtime v8 ein (§8). Die bisherige
Sperre der Legacy-Nachrüstung beschreibt den alten Werkzeugweg, nicht das PE-Ziel.

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
Spielerprofil zu; die Laufzeit behandelt den Wechsel. Die heutige manuelle
Resetpflicht aus [P1](PROTOTYPE_P1.md) bleibt bis PE-A3 implementierter Stand.

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
Produktionsbelege geöffnet. Umfangreiche Prüfungen gehören an den Schreib-/
Integrationsweg, nicht an jede Texteingabe. Dateihashes bleiben Integritäts- und
Konfliktschutz; sie sind keine fachlichen Rätsel-IDs.

PE verspricht keinen unbelegten Geschwindigkeitsgewinn. Der heutige Spielstart
lädt viele Definitionen/Saves bereits vorab. Ein allgemeiner Umbau dieses
Startverhaltens ist kein verdeckter Teil des Editors. Der erste Datenwechsel
bekommt einen begrenzten Vergleich von Aufwand, Dateizugriffen und Laufzeit;
spätere konkrete Engpässe werden anhand der Messung behandelt.

## 7. PE-A1: geschlossener Metadatenvertrag

PE-A1 ist das erste eigenständig lieferbare Fundament. Es liefert Namen,
Kategorien, Migration und gemeinsame API/CLI; noch keine Weboberfläche,
Bildübernahme, Rasteränderung oder automatische Savebehandlung.

### 7.1 Inhaltsregistry v4

Neue Wurzel `picross-content-registry-v4`, exakt
`format,entries,metadata,backgrounds`. `backgrounds` verwendet den bestehenden
Indexvertrag und darf leer sein. `entries` behalten ihren bestehenden exakten
Eintragsvertrag und die Produktionsbindungen. `metadata` ist eine nach ID
sortierte Liste mit exakt einer Zeile `{id,name,category_id}` je registrierter ID.
Keine fehlenden, zusätzlichen oder doppelten IDs. Name gemäß §3; `category_id`
verweist auf den aktuellen Kategorienkatalog. Bestehende Größen-/Anzahlgrenzen
der Inhaltsregistry und Kategorien bleiben.

| Daten | Autorität in v4 |
| --- | --- |
| Aktueller Motivname | `metadata[id].name` |
| Aktuelle Kategorie | `metadata[id].category_id` |
| Identität, Definitionspfad und Produktion | Bestehender `entries`-Eintrag und seine gebundenen Fachquellen; aktuelle Bildpfade ab PE-A2 nach §8 |
| Aktuelles Raster | Bestehende Definitionsdatei mit ID, Revision, Matrix, Palette und Hinweisen |
| Name in `definition.reveal.name` / Kategorie in Produktionseintrag | Zum jeweiligen Produktionsstand gehörende Angabe; kein zweiter aktueller redaktioneller Wert |

Bestehende v2/v3 bleiben unter ihren exakten Altregeln lesbar. Nur dort darf die
aktuelle Ansicht aus Definition/Entry abgeleitet werden. Bei v4 sind fehlende oder
ungültige Metadaten ein Fehler, kein Rückfall auf alte Angaben. Der reine
Entry-Struktur-/Receiptvergleich wird von der Prüfung aktueller Kategoriebezüge
getrennt. Historische Entrykategorien bleiben gegen ihren damaligen Export-/
Receiptstand geprüft; sie müssen in v4 nicht mehr im aktuellen Kategorienkatalog
existieren. Keine Ersatzkategorien und kein Umschreiben alter Belege.

### 7.2 Laufzeitregistry v7

`picross-runtime-registry-v7` hat exakt `format,categories,entries`. Jeder Eintrag
enthält die zehn bisherigen v6-Felder
`id,key,save_slot,definition,reveal,visible,category_id,difficulty,added_at,background`
und zusätzlich `name`. Name und Kategorie stammen aus der aktuellen Metadatentabelle.
Es gibt genau eine v7-Form; Legacy erhält `background={status:legacy,
image_revision:null,asset:null}`. Sonstige Hintergrundformen entsprechen exakt v6.

V7 konsumiert ausdrücklich denselben Hintergrundteilvertrag wie v6. Die geschlossene
Capability-v1 und ihr v6-Fähigkeitsnachweis bleiben unverändert gültig; `selected/none`
verlangen weiterhin eine aktivierte kompatible Fähigkeit. Ein Legacy-only-v7-Katalog
erzwingt keine Hintergrundaktivierung. Unbekannte/defekte Fähigkeiten werden nicht
stillschweigend akzeptiert. V2–v6 behalten ihre geschlossenen Altleser.

Der gemeinsame Definitionsloader übernimmt bei v7 den aktuellen Namen ausschließlich
in das im Speicher verwendete Definitionsobjekt. ID, Revision, Lösung und übrige
Felder bleiben gleich; die Definitionsdatei wird dafür nicht geschrieben. Alle
normalen Spielanzeigen verwenden diese gemeinsame Auflösung. Neue/begonnene Rätsel
zeigen weiterhin keine unverdienten Motivnamen oder Bilder. Der Spieler lädt keine
Inhaltsregistry oder Produktionsbelege.

### 7.3 Migration und laufende Produktion

Die explizite einmalige Migration prüft den gültigen Ausgangscheckout und übernimmt
für jede ID den aktuellen Namen aus der Definition und die Kategorie aus dem Entry.
Bei v2 entsteht ein leerer Hintergrundindex, bei v3 bleibt der Index erhalten.
Nur Inhaltsregistry und Runtimeprojektion ändern sich; Kategorien, Definitionen,
Bilder, aktive Quellen, Ratings, Added und Herkunftsbelege bleiben bytegleich.
Keine sichtbare Umbenennung, neue Rätselrevision, erneute Zertifizierung oder
Spielstandmigration. Wiederholung eines bereits gültigen v4/v7-Stands ist No-op.

PE-A1-Mutationen verlangen einen gültigen v4/v7-Zielstand; PE-A2 ergänzt nach
expliziter Projektionseinführung v4/v8 (§8). Fortgeführte Writer erhalten die
gewählte aktuelle Generation. Außer bei der ausdrücklich aufgerufenen Migration
stoppen sie auf v2/v3 vor Mutation mit einem konkreten Migrationshinweis.
Historische Prüfung, vollständig geprüfte No-ops und bereits gebundene Alt-Recovery
bleiben unter ihrem jeweiligen Vertrag möglich. Gewöhnliche Pflege- oder
Produktionsoperationen führen keine implizite Migration aus.

| Operation nach PE-A1 | Behandlung aktueller Metadaten |
| --- | --- |
| Erstregistrierung einer neuen ID | Aktuell vorhandene Kategorie verlangen; Zeile aus geprüfter Exportkategorie und Definitionsname initialisieren. |
| Historisch identische Registerwiederholung | Vollständige ursprüngliche Bindung prüfen, aktive Zeile erhalten. Eine inzwischen gelöschte Ursprungskategorie ist kein Grund, aktuelle Metadaten zurückzusetzen. |
| Rasterupdate einer vorhandenen ID | Aktive Zeile vollständig erhalten. Exportkategorie gegen den eigenen unveränderten Exportsnapshot prüfen; sie darf von der aktuellen Zuordnung abweichen und wird nur Herkunft des neuen Produktionseintrags. |
| Reveal-/Hintergrund-/Rating-/Added-Operation, Sync, Batch | Aktive Zeilen erhalten und bei Planung/Prüfung mitbinden. Keine Rekonstruktion aus historischen Angaben. |
| Name/Kategorie/Kategorienkatalog pflegen | Nur betroffene Metadaten beziehungsweise Kategorienquelle und erforderliche Runtimeprojektion ändern. Keine Definition-/Rating-/Bildneubindung allein dafür. |

Ein gemeinsamer Resolver liefert aktuelle und historische Angaben bewusst getrennt.
Alle Full-/Quick-/Snapshot-/Recovery-/Namespacewege müssen die neue Generation
konsistent akzeptieren oder eine unpassende alte Operation vor Mutation ablehnen.
Ein Metadatenwechsel nach Planung macht alte schreibende Pläne stale, auch wenn
deren eigenes Zielfeld unverändert ist. Offene alte Journale werden vor Migration
mit ihrem passenden bisherigen Vertrag aufgelöst; keine blinde Journalumschreibung.

### 7.4 API/CLI und Änderungsumfang

Eine kleine gemeinsame Python-API und CLI bieten lesende Auflösung, lesenden
Änderungsplan, explizite Übernahme sowie Migration und Wiederherstellung. Sie
unterstützen Name, Kategoriezuordnung, Kategorieanlage/-umbenennung sowie
Kategorieentfernung mit optionaler vollständiger Neuzuordnung. Keine API zum
freien Ersetzen der gesamten Registry und keine zweite alternative Schreiblogik.
Konkrete Befehlsnamen gehören zur mitzuliefernden Werkzeuganleitung.

Ein Plan zeigt ausgewählte IDs, Werte vorher/nachher und die tatsächlich betroffenen
Dateien. Er bindet Ausgangsbytes, relevante Abwesenheiten und gemeinsame Quellen.
Eine neue geschlossene Plangeneration und nötige Journalgeneration verwenden die
bestehenden Locks, Staging-, Konflikt- und Recoverymechanismen. Alte Generationen
werden nicht durch ignorierte Fremdfelder erweitert. Normale Name-/Kategoriepflege
erzeugt keine eigene endlose Metadatenhistorie oder zusätzliche Freigaberunde.

PE-A1 umfasst die verlustfreie Übernahme des dann aktuellen echten Bestands und
die nötigen gemeinsamen Leser-/Writeranpassungen. Der echte Bestand dient nur
der einmaligen Migration und Integritätskontrolle, nicht als wachsender Dauertest.

### 7.5 Geschlossene Implementierungsformen

Vor der Codeänderung am 12.11.2026 festgelegt: Der gemeinsame lesende Plan
`picross-editor-metadata-plan-v1` enthält exakt
`format,operation,operations,changes,files,journal`. `operation` ist `metadata`
oder `metadata-migration`. Der eingebettete gemeinsame Transaktionsplan bindet
vollständige alte/neue Quellen, Abwesenheiten und behaltene Dateihashes.
`changes` zeigt die betroffenen Rätsel-/Kategoriezeilen vorher/nachher;
`files` nennt nur tatsächlich unterschiedliche Zieldateien. Die Übernahme
prüft Operationen, Vorschau und Journal erneut gegeneinander. Eine Kategorie-ID
wird beim Planen einmalig erzeugt und bleibt in diesem Plan fest gebunden.

Die gemeinsame API unterstützt `set_metadata` mit ID und mindestens einem der
Felder `name,category_id`, `category_create` mit Name, `category_rename` mit ID/Name
und `category_delete` mit ID sowie optionalem `reassign_to`. Fehlende Neuzuordnung
bei belegter Kategorie ist ein Fehler. Migration ist eine eigene Operation.
Der lesende `picross-metadata-view-v1` enthält exakt `format,categories,entries`;
die Einträge sind die aktuellen `{id,name,category_id}`-Zeilen. Eine geladene
Ansicht löst IDs im Speicher auf, ohne Definitionen oder Bilder erneut zu lesen.

Die neuen Journale verwenden dieselbe geschlossene äußere Form und denselben
Publikations-/Recoveryweg wie die bisherige Hintergrundgeneration:

| Operation | Neue Formatkennung |
| --- | --- |
| Registrierung | `picross-registration-journal-v8` |
| Rasterupdate | `picross-content-update-journal-v8` |
| Rating-/Added-Übernahme, Sync | `picross-catalog-metadata-journal-v5` |
| Revealübernahme | `picross-reveal-adoption-journal-v5` |
| Hintergrundübernahme | `picross-background-adoption-journal-v3` |
| Methodenaktivierung | `picross-difficulty-activation-journal-v3` |
| Aktuelle Metadaten/Kategorien | `picross-editor-metadata-journal-v1` |
| Explizite v4/v7-Migration | `picross-editor-migration-journal-v1` |

Für einen regulären Rasterupdate-Export mit geänderter historischer Kategorie
benötigt der Hintergrund-Verlauf `picross-catalog-background-v4`. Er behält exakt
die v3-Felder `format,base,entry,events` und deren geschlossene Unterformen.
Ausschließlich bei einem Rasterupdate darf die Kategorie zwischen historischen
Bindings wechseln; Struktur, vollständige Export-/Receiptbindung und jeweiliger
Kategoriesnapshot bleiben geprüft. Der aktuelle Fremdschlüssel steht in
`metadata`. Alle übrigen Identitäts-, Rasterrevisions-, Bild-, Rechte- und
Quellenbindungen bleiben erhalten. Ein v3-Verlauf bleibt v3 bis zum ersten
solchen Kategoriewechsel; danach bleibt er v4. Bei der Prüfung früherer
`previous_source`-Hashes wird deren tatsächliche v3-/v4-Generation rekonstruiert.
Migration und reine Metadatenpflege ändern niemals diese Quellenbytes.

## 8. PE-A2: geschlossener Bild- und Präferenzvertrag

Vertrag vor konsumierendem Code, 12.11.2026, gemäß
[Paketentscheidung PE-A2](https://github.com/venomenon328/picross/issues/576#issuecomment-6839202555).
Die folgenden Tabellen definieren neue Generationen; bestehende geschlossene
Quellen, Pläne und Journale behalten ihre Altregeln. Der gemeinsame Writer und
Resolver gelten für Editor, CLI, Standardproduktion, Sync und Recovery.

### 8.1 Gemeinsame Typen und aktive Quellen

Alle Objekte sind geschlossen, ohne Zusatz- oder Doppelschlüssel. Kanonisches
UTF-8-JSON verwendet die bestehenden Hashregeln und genau ein abschließendes LF.
Ein SHA-256 ist eine kleingeschriebene hexadezimale Zeichenfolge mit 64 Stellen;
Ganzzahlen schließen boolesche Werte aus. Revisionszähler liegen in 1…1.000.000.
`Ref` ist exakt `{file,sha256,bytes}` mit sicherem relativem POSIX-Pfad, positivem
Byteumfang und echtem Dateihash. Pfade bleiben unter ihrer gebundenen Wurzel;
Links/Reparsepunkte, Casefold-/Datei-/Verzeichnisaliase und Kollisionen sind Fehler.
Eine Quelle darf einschließlich LF höchstens 1 MiB groß sein. Überläufe stoppen
vor Mutation; historische Belege werden dafür weder gekürzt noch neu versiegelt.

| Objekt | Exakte Felder und Bindung |
| --- | --- |
| Revealquelle | `format,id,record_revision,origin,binding,current,record_hash`; `format=picross-catalog-reveal-v3`, Pfad `content/reveals/<id>.json`. |
| Hintergrundquelle | Dieselben sieben Felder; `format=picross-catalog-background-v5`, Pfad `content/backgrounds/<id>.json`. |
| `origin` | `entry,identity,notice,source`; einmaliger unveränderlicher Ausgangsanker. |
| `binding` | `entry,identity`; aktueller vollständig geprüfter Produktions-/Definitionsstand. |
| `identity` | `key,save_slot,definition,runtime_revision`; `definition` ist der Ref der tatsächlichen Definitionsdatei unter `game/`, übrige Werte müssen zum gebundenen Entry und zur Definition passen. |
| Reveal-`current` | `image_revision,asset,notice,provenance,authority`. `asset` ist ein Ref auf den bisherigen technischen Revealstamm mit tatsächlicher `.png`-/`.svg`-Endung. `notice` ist die Text/Hash-Unterform, Datei am selben Stamm mit `.txt`. |
| Hintergrund-`current` | `image_revision,status,asset,notice,authority`; `status` genau `standard`, `selected` oder `none`. Bei selected Asset-/Notice-Refs genau `game/art/backgrounds/<id>.png` beziehungsweise `.txt`; sonst beide null. |
| `provenance` | `author,usage_basis,source,changes`; bestehende vierfeldrige Provenienz, jede Angabe 1…4096 Zeichen, getrimmt, einzeilig, ohne Steuerzeichen. |
| Textnotice | `text,sha256`; bestehende Noticeform, 1…65.536 UTF-8-Bytes, abschließendes LF, kein BOM/CR/NUL, Hash über die tatsächlichen Textbytes. |
| `decision` | `actor,timestamp_utc,statement`; Akteur 1…128, Aussage 1…4096 getrimmte einzeilige Zeichen ohne Steuerzeichen, echter UTC-Zeitpunkt exakt `YYYY-MM-DDTHH:MM:SSZ`. |
| `record_hash` | Kanonischer SHA-256 des vollständigen Quellenobjekts ohne dieses Feld. |

`origin.entry` ist der vollständige normalisierte historische Produktionseintrag,
nicht nur seine ID. Export/Receipt und seine ursprünglichen Hash-/Rechte-/
Freigabebindungen werden nach dem bestehenden gemeinsamen Resolver geprüft.
`origin.source` ist entweder die vollständige unveränderte vorhandene Reveal-v1/v2-
beziehungsweise Background-v1–v4-Quelle oder null ausschließlich bei gültiger
bisher sourcefreier Produktion. Es enthält niemals eine neue v3-/v5-Hülle.
`origin.notice` bindet die damals wirksame Textnotice, bei bildlosem Hintergrund
null. Die erste tatsächliche Pflege erstellt diesen Anker; spätere Pflege erhält
ihn byteinhaltlich. Git führt die Änderungshistorie, keine rekursiven Wrapper.

Die äußere `binding` prüft den aktuellen vollständig normalisierten Entry und
die aktuellen Definitionsbytes. Ein physischer Export→Receiptwechsel ändert
keine Rätsel-/Bildidentität und rechtfertigt keine neue Inhaltsentscheidung.
Bestehende physische Paket-, Receipt- und Exportanker werden vollständig gelesen
und verglichen; ID-Gleichheit oder der neue Wrapperhash allein genügen nicht.

| `authority` | Exakte Unterform und Prüfung |
| --- | --- |
| Manuell | `kind,decision,provenance` mit `kind=manual`. Provenienz nur bei standard/none null; bei einer Datei vollständig. Reveal-`current.provenance` und `authority.provenance` sind identisch. Auswahl und Speichern dokumentieren die wirkliche Eigentümerentscheidung, kein technisches Programm erzeugt ein menschliches Sichturteil. |
| Produktives Reveal | `kind,approval,binding` mit `kind=production`. `approval` ist die unveränderte gültige `picross-reveal-approval-v1`. Das innere `{entry,identity}` bindet ihren damaligen Adoptionstand. Approval-ID, Bildrevision, Vorgänger-/Bild-/Noticehash und Definitionshash werden gegen diesen Stand geprüft. Ein späterer Raster-Rebind ändert nur die äußere aktuelle Bindung. |
| Produktiver Hintergrund | `kind,candidate_revision,decision,derivation,provenance,review,adoption` mit `kind=production`; die bestehenden geschlossenen HP-W2-/HP-I1b2-Unterformen bleiben vollständig erhalten und mit Bild/Notice/ID/Revision sowie ihren wirklichen Quellständen gekreuzt geprüft. In Source v5 hat `adoption` exakt `request,revision,target,background,authorization,context`; `context` bindet den tatsächlichen Request-v2-Kontext gemäß §8.5. Alte Sourcegenerationen behalten ihre fünfgliedrige Adoptionsform. |

Standard ist eine manuelle Präferenz, keine fingierte Produktionsableitung.
Manuelle Aktionen benötigen weder Approval- noch Derivationobjekt. Eine reguläre
spätere Adoption führt die aktuelle Quelle mit ihren echten Produktionsbelegen
fort; sie setzt sie nicht auf eine historische Baseline zurück.

Die [Implementierungspräzisierung](https://github.com/venomenon328/picross/issues/576#issuecomment-6839354651)
erlaubt zusätzlich die notwendige rein produktive v5-Überführung einer bestehenden
Background-v1–v4-Quelle beim Rebind auf einen manuellen Reveal-v3-Stand.
`origin.source` erhält die vollständige alte Quelle samt damaliger Bindung/Notice;
`current` übernimmt exakt deren validierte tatsächliche Bild-/HP-Felder.
Die Autorität ist production, keine neue Hintergrundentscheidung: image_revision
bleibt, record_revision erhöht sich einmal und binding wird aktuell. Eine vorhandene
alte fünffeldrige Adoption bleibt in genau diesem nachgewiesenen Herkunftsfall
unverändert. Adoption darf ausschließlich beim ursprünglichen Bild ohne Adoption
null sein, wenn sämtliche aktuellen Bild-/HP-Felder der vollständig validierten
origin.source entsprechen. Neue Request-v2-Adoptionen verlangen weiterhin ihren
sechsfeldrigen Kontext. Keine fiktive Adoption oder allgemeine optionale Beleglücke;
Erstregistrierung bleibt bei ihrem bisherigen produktiven Quellweg.

Eine echte reguläre Request-v2-Hintergrundadoption darf eine noch vorhandene
alte BG-v1–v4-Quelle direkt produktiv nach v5 übernehmen. Der Erst-Adoptionsanker
enthält die vollständige alte Quelle, während `adoption.target` unverändert die
tatsächlich adressierte alte Source samt ihrem damaligen Originhash/Bildzähler
bindet. Dieser besondere Targetfall ist ausschließlich durch vollständige
Gleichheit mit `origin.source` erlaubt; es gibt keine virtuell vorgeschaltete
v5-Zielquelle. `current` trägt die echte neue sechsfeldrige Adoption mit context,
image_revision und record_revision steigen je einmal. Spätere v5-Adoptionen
binden regulär den v5-Originhash. Alte Request-/Sourceformen werden nicht umgedeutet.

`image_revision` zählt wirkliche Änderungen der aktiven Bild-/Präferenzentscheidung:
erster manueller Wert = bisherige wirksame Bildrevision + 1, bei sourcefreiem
Legacy 0 + 1. Ein Rebind erhält diesen Wert. Der erste Wrapper erhält
`record_revision = max(bisherige record_revision, bisherige image_revision, 0) + 1`,
wobei ein nicht vorhandener Zähler 0 ist; jede spätere wirkliche Quellenfortschreibung
erhöht ihn genau einmal. Ein No-op erhält beide Zähler und die ursprüngliche
Entscheidung/Zeit. Nur ein neuer Zeitstempel/Akteur bei identischem gewünschtem
Datei-/Provenienz-/Präferenzstand erzeugt keine neue Entscheidung. Eine erstmals
ausdrücklich gespeicherte Standardpräferenz ist von sourcefreiem Legacy getrennt.

### 8.2 Unveränderter Eingang und festes Notice-Layout

`picross-prepared-background-png2304-v1` bezeichnet ausschließlich die Prüfung
des vorbereiteten direkten Hintergrunds: genau 2304×576, einzelnes nicht
animiertes vollständig dekodierbares PNG, höchstens 32 MiB, bereits korrekt
orientiert und sRGB-kompatibel, mindestens ein transparenter und ein sichtbarer
Pixel. Die bisherigen sicheren höchstens 8-Bit-Farbtypen, zulässiges tRNS und
Interlacing bleiben zulässig. Dies ist kein HP-W2-Ableitungsprofil; Originalbytes
werden nicht gedreht, konvertiert oder neu kodiert. Der isolierte Godotimport
beweist die erweiterten Eingangsformen durch echte Dekodierung im PCK (§9).

Revealgrenzen aus §4.1 bleiben; PNG↔SVG verwendet denselben technischen Stamm
und die wirkliche neue Endung. Die alte eigene Live-Datei wird im selben
abgesicherten Vorgang entfernt. Produktionsentry und Definitionsbytes behalten
ihren historischen Pfad; nur die aktive Quelle und Runtimeauflösung wechseln.
Keine beliebigen Asset-/Löschpfade und keine dauerhafte Live-Fassungssammlung.

Bei wirklicher manueller Dateiübernahme besteht die Notice aus dem unveränderten
vorhandenen Live-Noticetext, andernfalls dem vorhandenen `origin.notice.text`,
andernfalls leerem Präfix. Auf einen nichtleeren Präfix folgt genau ein zusätzliches
LF. Anschließend folgt exakt dieser Block mit den unveränderten validierten Werten:

```text
Manuelle Bildpflege (PE-A2)
author: {author}
usage_basis: {usage_basis}
source: {source}
changes: {changes}
actor: {actor}
timestamp_utc: {timestamp_utc}
statement: {statement}
```

Auch die letzte Zeile endet mit LF. Keine zusätzliche Datumserzeugung, Umformulierung
oder fingierte Produktionsfreigabe. Die Gesamtgrenze bleibt 65.536 Bytes; eine
Überschreitung ist ein konkreter Fehler. No-op erzeugt keinen Block. Standard/none
entfernt ausschließlich die eigene Live-Notice zusammen mit dem eigenen Livebild;
die unveränderliche Ausgangsattribution im `origin` bleibt erhalten.

### 8.3 Request, Plan und isoliertes Planbundle

| Form | Exakte Felder |
| --- | --- |
| `picross-editor-images-request-v1` | `format,id,metadata,reveal,background,decision`. |
| `metadata` | null oder nichtleeres Objekt aus ausschließlich `name,category_id`; Werte und Fremdschlüssel gemäß §3/§7. |
| `reveal` | null oder exakt `asset,provenance`; Asset-Ref unter der ausdrücklich gewählten Inputwurzel. |
| `background` | null oder exakt `status,asset,provenance`; status standard/selected/none, Asset-Ref und Provenienz nur bei selected, andernfalls beide null. |
| `decision` | Die geschlossene dreifeldrige Unterform aus §8.1. |
| `picross-editor-images-plan-v1` | `format,request,snapshot,old,new,files,plan_hash`. |
| `snapshot` | `sources,namespaces`; vollständige Pfad-/Hash-/Abwesenheits- und Namespacebindung nach §8.4. |
| Plan-`old` / `new` | Je exakt `entry,metadata,reveal,background,runtime`: vollständiger Produktionseintrag, aktuelle ID-Metadatenzeile, vollständige jeweilige Quelle oder null und vollständige einzelne v8-Runtimezeile. Alle fünf gehören zu derselben ausgewählten ID. |
| `files` | Sortierte duplikatfreie Liste genau der tatsächlich unterschiedlichen verwalteten Zielpfade; keine frei ausgewählten Schreibziele. |
| `plan_hash` | Kanonischer SHA-256 des Plans ohne dieses Feld. |

Mindestens eines von metadata/reveal/background ist nicht null. Der Request
enthält die wirklichen manuellen Eingaben, keine frei editierbare komplette
Registry. Reine Metadaten-/No-op-Anfragen erzeugen keine Bildentscheidung.
Gemeinsam gewünschte Bild-/Hintergrund-/ID-Metadatenänderungen bilden genau
eine Transaktion. Kategorienweite CRUD/Neuzuordnung bleibt eine eigene Operation.

Planung ist im geöffneten Inhaltscheckout vollständig lesend. Sie schreibt
ausschließlich in das ausdrücklich gewählte eigene Ausgabeziel außerhalb der
aktiven Inhalte. Das geschlossene Bundle enthält `plan.json`, die unveränderten
Requestbytes als `request.json`, tatsächlich benötigte Eingangsbilder unter
`input/<Request-Ref.file>` und erforderliche alte Binärseiten unter
`previous/<sha256>.bin`. `plan.request` ist der Ref auf `request.json`.
Keine Binärbytes/Base64 im Plan; das Inventar wird exakt aus Requestrefs und den
gebundenen alten Binärseiten hergeleitet. Fehlende/fremde Dateien, Aliase oder
Hash-/Abwesenheitsabweichungen blockieren. Der ursprüngliche externe Eingang
wird nach vollständiger Bundlebindung nicht mehr gebraucht.

Apply validiert Bundle und aktuellen vollständigen Checkout frisch und
rekonstruiert Requestwirkung, Vorschau, Importbytes, Quellen, Runtime, `files`
und gemeinsames Journal unabhängig. Hash/`pass` ersetzen keine Fachprüfung.
Ein bereits vollständig erreichter identischer Zustand bleibt No-op; ein
teilweiser oder fremd geänderter Zustand ist kein Erfolg.

### 8.4 Exakte Quellen-, Namespace- und Deltamengen

Für jeden gültigen Gesamtstand R bezeichnet `T8(R)` die bisherige vollständige
Textmenge des v4/v7-Writers: Inhalts-/Runtime-/Kategorienregistry,
Difficultydefault und Capability einschließlich sicherer Abwesenheit; je ID
Definition, gemeinsame Revealnotice, aktive Revealquelle, Rating, Addedquelle,
Hintergrundquelle und Hintergrundnotice. Fehlende optionale Quellen stehen
explizit auf null. Bildlose Hintergrundzustände dürfen keine Live-Notice besitzen.
Quelle, aktueller Index und tatsächliche Status-/Pfadbindung müssen übereinstimmen.

`K8(R)` enthält sämtliche bisherigen Paket-/Receipt-/Export-/Rating-/Added-
Berichtsquellen und deren vollständig geprüfte historische Bindungen sowie die
tatsächlich ausgewählten Livebilder. Neue Wrapper ersetzen keine dieser
Prüfungen. `C8(R)` enthält für jede registrierte ID beide aus ihrem unveränderten
technischen Revealstamm hergeleiteten `.png`-/`.svg`-Pfade und den festen
Hintergrund-PNG-Pfad. Genau die wirksamen Dateien existieren; jede inaktive
Alternative hat eine explizite negative Erwartung. `snapshot.sources` ist exakt
die Vereinigung `T8(R) ∪ K8(R) ∪ C8(R)`, jeweils SHA-256 oder null nur für erlaubte
Abwesenheit. Binärbytes werden niemals als Text interpretiert.

`snapshot.namespaces` hat exakt sieben Felder mit sortierten duplikatfreien Listen:

| Feld | Exakte tatsächliche Dateimenge |
| --- | --- |
| `reveals` | Aktive kanonische `content/reveals/<id>.json`. |
| `difficulty` | Bestehende kanonische Rating- und Difficultyberichtspfade. |
| `added` | Bestehende kanonische Addedquellen und ihre Berichte. |
| `packages` | Vollständige Dateien in allen registrierten Paket-/Receiptbäumen. |
| `backgrounds` | Genau die im Registryindex gebundenen `content/backgrounds/<id>.json`. |
| `background_assets` | Tatsächlich vorhandene selected-PNGs und ihre Notices; keine Dateien für standard/none/legacy. |
| `reveal_assets` | Tatsächlich vorhandene wirksame `.png`-/`.svg`-Datei und gemeinsame `.txt`-Notice je technischem Revealstamm. |

Die bisherigen Namespacegrenzen bleiben. Fremde Dateien, nichtkanonische Namen,
Links und unerwartete alternative Endungen blockieren; sichere leere kanonische
Verzeichnisse dürfen nach Rollback verbleiben. Eine vorhandene ungültige
Capability ist stets Fehler, auch wenn der Katalog nur legacy/standard enthält.

Das Journal hat exakt `format,operation,old,new,retained,additions,report_run,replacements`.
Für `editor-images` gilt `format=picross-editor-images-journal-v1`,
`old/new` besitzen exakt `T8(Ralt) ∪ T8(Rneu)` mit Text oder null;
`additions={}` und `report_run=null`. `replacements` enthält genau die wirklich
geänderten binären Pfade aus `C8(Ralt) ∪ C8(Rneu)`, beschränkt auf die ausgewählte
ID. Jede Seite ist null für sicher belegte Abwesenheit oder die bestehende
geschlossene Binärform `{sha256,bytes,base64}`. Null/null und identische Seiten
sind keine Ersetzung. `retained` bindet exakt alle übrigen vorhandenen K8-/C8-Pfade
mit SHA-256; negative C8-Erwartungen werden zusätzlich streng aus beiden
vollständigen Quellansichten hergeleitet und geprüft, nicht als neue null-Werte
in der bisherigen Retainedform gespeichert. Kein freier zusätzlicher Löschpfad.
Alte/neue Gesamtansicht und Kandidatenmengen werden bei Planung, unter Lock und
Recovery aus den vollständigen Quellen erneut hergeleitet, nicht aus `files` geglaubt.

| Operation | Ausschließlich zulässige Unterschiede |
| --- | --- |
| `editor-images` | Gewünschte Reveal-/Hintergrundquelle, zugehörige Livebilder/Notices, betroffener Hintergrundindexref, ausdrücklich gewählte ID-Metadaten und daraus abgeleitete Runtime. Alle Produktionseinträge/Definitionen, Kategorienquelle, Ratings/Added und unbeteiligten IDs bytegleich. |
| `editor-image-migration` | Ausschließlich gültige Runtimeprojektion v7→v8; keine Quellen-/Bild-/Metadaten-/Indexänderung. |
| `metadata` | Wie §7 ausschließlich gewählte aktuelle Metadaten/Kategorien und Runtime; aktive Bildquellen/Präferenzen erhalten. |
| `registration` | Bestehender vollständig geprüfter neue-ID-Paketumfang mit eigenem regulärem Bildweg; keine manuellen Wrapper ohne manuelle Entscheidung. Bestehende IDs unverändert. |
| `update` | Bestehender geprüfter Rasterupdateumfang einer ID; manuelle aktuelle Bilder/Präferenzen und Metadaten erhalten, äußere Quellenbindung an neue Definition fortschreiben. Keine neue Bildrevision allein wegen Rebind. |
| `reveal-adoption` / `background-adoption` | Bestehender jeweils ausdrücklich autorisierter Produktionsbildwechsel; neue aktuelle Quelle fortführen, echte Belege erhalten, nötige Gegenquellenbindung/Index/Runtime ableiten. Keine Rückkehr zur alten Ausgangsautorität. |
| `adoption` / `added-adoption` / `sync` / `method-activation` | Bisheriges jeweiliges Rating-/Added-/Runtime-/Defaultdelta; aktuelle Bild-, Herkunfts-, Rechte- und Metadatenautorität unverändert. |

Die Journalgrößen bleiben 24 MiB für nichtbinäre und 128 MiB einschließlich
JSON/Base64 für Bildjournale, höchstens 32 MiB je Binärseite und 96 MiB dekodierte
Seiten insgesamt. Vor Mutation konkret ablehnen; keine automatische Teilmenge.
Planung, Übernahme und Recovery haben jeweils eigenständig den bisherigen
endlichen 300-s-Rahmen. RI-B/RI-C-Registrierungsabkürzungen und der 1800-s-
Registrierungsdefault werden nicht auf die neue Bildpflege übertragen.

Der Writer verwendet `content/.registration-pending.json`, vollständige isolierte
Alt-/Zielansichten, dauerhafte Journalanlage vor Mutation, frische Unter-Lock-
Prüfung, sichere atomare Binär-/Textpublikation und Runtime zuletzt. Recovery
rollt ausschließlich auf den vollständig gültigen eigenen Altstand zurück,
auch nach erneutem Abbruch oder bereits erreichter neuer Belegung. Eigene neue
Endung und entfernte alte Bildseite sind dabei symmetrisch gebunden. Fremde
Bytes bleiben mit Journal und konkreter Recoverymeldung erhalten.

### 8.5 Runtime v8, Projektionseinführung und Folgegenerationen

`picross-runtime-registry-v8` hat exakt die v7-Wurzel `format,categories,entries`
und je Eintrag exakt `id,key,save_slot,definition,reveal,visible,category_id,difficulty,added_at,background,name`.
`reveal` ist der wirksame aktuelle Ressourcenpfad; die übrigen Identitäts-/
Logikbindungen bleiben erhalten. `background` ist exakt
`status,image_revision,asset`: legacy mit null/null, standard mit positiver
Präferenzrevision und asset null; selected/none behalten den bisherigen Teilvertrag.
Standard folgt der aktuellen Metadatenkategorie, ohne passende Zeichnung ist
kein Hintergrund wirksam. Fehlende/defekte deklarierte Quellen sind Fehler.

Die unveränderte Capability v1 wird auch für v8 als Nachweis desselben
selected/none-Renderprofils akzeptiert. selected/none erfordert gültig enabled;
legacy/standard allein nicht. V2–v7 behalten ihre exakten Altleser.
Der gemeinsame Godotloader übernimmt aktuellen Namen und Revealpfad nur in
seine Speicheransicht. Definitionsdatei, Raster-/Save-Revision, Lösung, Hinweise,
Palette und Ratingbindung bleiben unverändert. Katalog und Abschluss verwenden
dieselbe aktive Datei; neue/begonnene Rätsel laden sie nicht zur Vorschau.

| Explizite Migration | Geschlossene Form |
| --- | --- |
| Plan | `picross-editor-image-migration-plan-v1` mit `format,snapshot,old,new,files,plan_hash`; vollständiger Snapshot aus §8.4, old/new die vollständigen gültigen v7-/v8-Runtimeobjekte. |
| Wiederholung | Bei bereits gültigem v8 old=new=v8 und files=[]; keine Bytes/mtime-Änderung. |
| Journal | `picross-editor-image-migration-journal-v1`, operation `editor-image-migration`, gleiche Achtfelderform und vollständige Text-/Quellenmengen; additions/replacements leer, report_run null. Nur Runtime darf sich unterscheiden. |

Bildpflege verlangt v4/v8; gewöhnliches Speichern migriert nicht. Die vorherige
v2/v3→v4/v7-Migration behält ihren Vertrag; danach ist der ausdrücklich gewählte
zweite Schritt möglich. V4/v7-Pflege bleibt zulässig, fortgeführte Writer stufen
einen gültigen v8-Stand niemals zurück.

| Operation auf v8 | Neue Journalkennung |
| --- | --- |
| Neue Registrierung | `picross-registration-journal-v9` |
| Reguläres Rasterupdate | `picross-content-update-journal-v9` |
| Rating-/Addedübernahme und Sync | `picross-catalog-metadata-journal-v6` |
| Reguläre AT-Bildadoption | `picross-reveal-adoption-journal-v6` |
| Reguläre Hintergrundadoption | `picross-background-adoption-journal-v4` |
| Methodenaktivierung | `picross-difficulty-activation-journal-v4` |
| PE-Namen-/Kategoriepflege | `picross-editor-metadata-journal-v2` |
| Gemeinsame Bild-/ID-Metadatenpflege | `picross-editor-images-journal-v1` |
| Explizite v7→v8-Projektion | `picross-editor-image-migration-journal-v1` |

Die gespeicherten v8-Generationen heißen Revealrequest v2 / Revealplan v5,
Background-Adoption-Request v2 / Backgroundplan v3, Metadatenplan v2,
Difficultyreport v6, Addedplan v5 und Aktivierungsplan v3. Ihre exakten bisherigen
äußeren Felder bleiben, außer der ausdrücklich neuen aktuellen Reveal-/
Kontextbindung im Background-Adoption-Request v2. Deren Feldtabellen stehen in
[SD_CATALOG](SD_CATALOG.md) und [PUZZLE_BACKGROUNDS](PUZZLE_BACKGROUNDS.md).
Alte Pläne/Journale werden weder umetikettiert noch still um Quellen ergänzt.

Der Background-Adoption-Request v2 ergänzt genau `context` zu seinen bisherigen
acht Wurzelfeldern. Kontext ist exakt `{source,production,reveal}`: `source` ist
ein Ref auf die aktuelle Revealquelle, andernfalls null; `production` ist nur
im sourcefreien Fall der vollständig geprüfte Anker `{entry,identity}`, sonst
null. Genau eine dieser Autoritäten ist vorhanden. `reveal` ist der Ref auf
die tatsächliche aktuelle Datei einschließlich wirksamer Endung, Hash und Bytes.
Die Produktionsauswahl bindet diesen aktuellen Kontext; eine alte
`origin.approval.selection.reveal` ersetzt ihn nicht. Derselbe Kontext bleibt
in der sechsfeldrigen produktiven v5-Adoption dauerhaft gebunden.

Die [begründete Receipt-Präzisierung](https://github.com/venomenon328/picross/issues/576#issuecomment-6839354651)
führt `picross-integrated-content-v3` mit exakt
`format,entry,integrated_commit,notice_sha256,background` ein. `background` ist
exakt `{origin_sha256,export_source}`: Hash des kanonischen unveränderlichen
v5-`origin` und die vollständige echte gültige Source v1 des aktuellen
v6-Exports, beziehungsweise null bei sourcefreier Produktion. Vor Retirement
werden Exportquellen, Mainbindung und aktive manuelle Quelle vollständig geprüft.
Damit bleibt Legacy→manueller Hintergrund→regulärer Rasterexport nach Retirement
prüfbar, ohne `origin.source=null` umzuschreiben oder neue Wrapperhistorie.
Bestehende Receipt-v1/v2-Formen bleiben unverändert geschlossen.

Historisch identische Registrierung prüft ursprünglichen Export/Receipt vollständig
und bleibt nach manueller Pflege No-op. Ein gültiger regulärer Folgeexport wird
als eigener Produktionsstand geprüft; seine historischen Bildpfade werden von
den wirksamen manuellen Pfaden getrennt. Er muss eine manuelle Entscheidung nicht
als HP-W2-Ableitung reproduzieren. Exportbilder setzen keine aktuelle manuelle
Präferenz zurück. Sync, Batch und Produktionsabschluss erhalten dieselbe Autorität
und deren aktive Rechte. Die einmalige #620-Ausnahme begründet keine allgemeine
HP-W2-Toolhashkompatibilität oder Neuversiegelung alter Belege.

## 9. PE-A3: geschlossener Raster- und Revisionsvertrag

Vertrag vor konsumierendem Code, 13.11.2026, gemäß
[PE-A3](https://github.com/venomenon328/picross/issues/576#issuecomment-6848707827).
Die gemeinsamen Typen, sichere Pfade, Kanonisierung und Grenzen aus §8 gelten.
Eingang ist ausschließlich ein gültiger v4/v8-Checkout. Die echte v7-Projektion
wird nicht implizit migriert. Alle Prüfungen verwenden synthetische Ziele.

### 9.1 Rasterrequest, Paket und Bundle

| Form | Exakte Felder |
| --- | --- |
| `picross-editor-raster-request-v1` | `format,id,text,metadata,reveal,background,decision,provenance,profile` |
| `text` | UTF-8-String bis 64 KiB; eine nichtleere Zeile je Matrixzeile, Whitespace zwischen unsigned Dezimaltokens. Ein abschließender Zeilenumbruch erlaubt, CRLF semantisch gleich. Je Achse 1…50, positive IDs ausschließlich aus unveränderter bestehender Palette. Fehlerpositionen 1-basiert. |
| `metadata,reveal,background,decision` | Unverändert die jeweiligen Unterformen aus §8.3/8.1. Bei Raster-only sind die ersten drei null. |
| `provenance` | Vierfeldrige Herkunft nach §8.1 für die tatsächliche manuelle Rasterentscheidung; keine KI-/Authoringbehauptung. |
| `profile` | `line` oder `paired`; Profile verwenden bestehende volle Mono-/Farbverifikation. Paarwahl allein behauptet keine R4-Notwendigkeit. |
| `picross-editor-raster-plan-v1` | `format,request,snapshot,old,new,quality,files,plan_hash` |
| Plan `old,new` | Je `entry,metadata,reveal,background,runtime,definition`; erste fünf wie §8.3, definition vollständiges Schema-2-Objekt. |
| `quality` | null bei kanonisch gleicher Logik, sonst `method,checked,proof,baseline`; checked ist vollständige geprüfte SD-Hülle, proof/baseline echte Bundle-Refs, baseline nur bei paired nicht null. |
| `picross-editor-raster-package-v1` | `format,id,revision,previous,origin,definition,reveal_sha256,notice_sha256,quality,decision,provenance,files,package_hash` |
| Paket `previous` | `entry,identity`; vollständiger physischer Vorgängereintrag und dessen Identity nach §8.1. Seine Paketdateien bleiben unverändert erhalten. |
| Paket `origin` | `entry,identity`; ursprünglicher echter Produktionsanker, bei wiederholtem Edit unverändert, niemals komplette Vorgängerhülle. |
| Paket `definition` | Ref auf `definition.json` im eigenen Paket. Definition hat stabile ID/Palette/Revealangaben und bei geänderter Logik genau Vorgängerrevision + 1. |
| `reveal_sha256` | Historischer Revealhash der neuen Rasterbindung: bisherige Produktionsbindung, bei alter AT-v1/v2-Quelle deren bereits tatsächlich aktiver Bildhash. Keine neue Bildentscheidung. |
| Paket `quality` | Dieselbe geschlossene Form wie im Plan; vollständige unabhängig geprüfte neue Rating-/Proofbindung. |
| Paket `files` | Pfad→SHA-256 exakt aller Paketdateien außer `manifest.json`. Zulässig: `definition.json`, `previous-definition.json`, `request.json`, `proof.json`, optional `baseline.json` und vollständiges geschlossenes Analysebundle unter `analysis/`. `previous-definition.json` sind die unveränderten alten Definitionsbytes; Hash und vollständige Identity müssen `previous` entsprechen. Damit bleiben tatsächliche Altlogik, Palette und Revision auch nach früherem Retirement prüfbar. Keine ausführbaren Dateien oder Originalbildkopien. |
| `package_hash` | Kanonischer Hash des Manifests ohne dieses Feld. Registry bindet zusätzlich den tatsächlichen Manifestdateihash. |

Neue Paketkennung ist `editor-<Runtime-Revision>` unter
`content/packages/<id>/`; belegte oder aliasierende Ziele sind Konflikte.
Eine vorhandene ausschließlich leere Verzeichnisstruktur darf nur verwendet
werden, wenn jedes Unterverzeichnis ein aus dem geprüften neuen Paketinventar
hergeleitetes Elternverzeichnis ist. So bleiben nach gemeinsamem Rollback
zurückgelassene leere Container wiederverwendbar; vorhandene Dateien und fremde
Unterverzeichnisse werden weder übernommen noch gelöscht.
Der historische Produktionsmodus und die historische Difficultyangabe werden
nicht als neue Bewertung ausgegeben; aktuelle Bewertung kommt ausschließlich
aus der neuen SD-Quelle. Aus vorheriger Produktion bleiben Bildhash/-pfad,
Added, Rechte, ID/Key/Slot und alle unbeteiligten IDs erhalten.

Das externe Bundle enthält `plan.json`, `request.json`, bei neuer Logik
`package/` mit exakt obigem Paket sowie nur die benötigten unveränderten
A2-Imports unter `input/`, binären Altseiten unter `previous/` (§8.3) und
exakten geänderten Alttexten unter `before/<SHA-256>.txt`. Letztere sind durch
den Snapshot gebunden und erlauben die vollständig geprüfte No-op-Wiederholung;
keine freien Restorepfade. Ihre Gesamtbytes bleiben innerhalb 24 MiB.
Planung löst und prüft den vollständigen neuen Proof, vergleicht jede Endzelle
mit der Matrix und analysiert/bewertet mit der aus dem Ziel gelesenen aktiven
Methode. Apply prüft diese geschriebenen Originale unabhängig erneut und
rekonstruiert die geplanten Bytes aus Request, Paket und frischen Quellen.
Keine fremden Pfade aus Plansummaries als Schreibziele öffnen.

Kanonisch gleiche Dimensionen, Farb-ID-Semantik und Matrix erzeugen weder
neue Entscheidung noch Paket, Solverlauf oder Ratingrevision. Ohne A1/A2-Delta
bleiben sämtliche Bytes und mtimes gleich. Zusammen gewählte A1/A2-Änderungen
werden als Teil desselben Rasterjournals mit ihren eigenen Grenzen geprüft.

### 9.2 Gemeinsame Transaktion und Folgequellen

`picross-editor-raster-journal-v1`, Operation `editor-raster`, besitzt exakt
`format,operation,old,new,retained,additions,report_run,replacements`.
T8/K8/C8 und die sieben Namespaces aus §8.4 gelten; K8 und packages schließen
alle tatsächlich referenzierten unveränderten Vorgängerpakete ein.
`additions` ist exakt das neue Rasterpaket, bei gleicher Logik leer;
`report_run=null`. Binäre A2-Deltas folgen unverändert §8.4.
Delta ausschließlich eine bestehende ID: neue Definition/Produktion/Rating,
erforderliche Reveal-/Hintergrundneubindung, ausdrücklich gewählte A1/A2-Felder
und abgeleitete Runtime. Kategorienquelle, Added und andere IDs bytegleich.
Historische Quellenanker und Bildzähler bleiben ohne Bildentscheidung erhalten.

Journalgrenzen: 128 MiB einschließlich Base64, 32 MiB je Binärseite,
96 MiB dekodiert; ohne Binärdelta 24 MiB. Planung, Apply und Recovery jeweils
endlich 300 s. Keine RI-Registrierungsabkürzung. Gemeinsamer Lock, vollständige
isolierte Alt-/Neuprüfung, frische Guards und Runtime zuletzt gelten unverändert.
Recovery ist wiederholbarer Rollback auf den validierten Altstand; fremde Bytes
werden mit Journal erhalten. Kein Solverlauf während Recovery.

Gemeinsame Resolver unterscheiden neue Editorpakete ausdrücklich von regulären
Exporten/Receipts. Historische Registerwiederholung prüft den gebundenen echten
Produktionsanker und bleibt No-op. Spätere reguläre Updates verwenden weiterhin
ihren vollständigen Exportprüfweg und erhalten aktuelle Metadaten und Bilder.
Sync/Rating/Added/Adoption/Abschluss dürfen die Rasterautorität nicht zurückstufen.
Retirement kompaktiert diese weiterhin benötigten manuellen Proof-/Entscheidungs-
pakete nicht in Authoringreceipts. Bei vollständig auf main gebundener aktueller
Quellansicht bleibt die Auswahl eines solchen Pakets ein geprüfter No-op;
historische Vorgänger bleiben erhalten. Ein späterer echter Standardexport
folgt wieder seinem normalen Retirementvertrag.

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

## 10. Lieferung, Abnahme und Paketgrenzen

Die beiden Hauptbereiche bleiben Datenpflege und Weboberfläche. Das Fundament
wird wegen seiner unterschiedlichen Datenrisiken in eigenständige Pakete geteilt:

| Paket | Eigenständig prüfbarer Endzustand |
| --- | --- |
| PE-A1 | Aktuelle Namen/Kategorien, v4/v7-Migration, gemeinsame CLI/API und weiter funktionierende Standardproduktion. Nach unabhängigem Review über PR #577 integriert. |
| PE-A2 | Unveränderter Fertigbildimport, Abschlussbildwechsel, Legacy-Erstzuordnung, alle drei Hintergrundzustände und kombinierte ID-Metadatenpflege. Nach unabhängigem Review über PR #623 integriert. |
| PE-A3 | Textuelle Rasterübernahme mit vorhandenen Prüfungen und gezielter automatischer Savebehandlung bei älterer Rasterrevision. Vertrag §9, eigener Prüfplan in #576; technische Lieferung und unabhängiges Review getrennt. |
| PE-B | Lokale Weboberfläche und komfortabler Windowsstart für sämtliche freigegebenen Bearbeitungen. Konsumiert die gemeinsamen Writer. |

PE-A1 und PE-A2 besitzen eigene vollständige Umsetzungsschnitte und Prüfpläne im
Issue. PE-A3 besitzt ebenfalls eine geschlossene Paketentscheidung; PE-B bleibt
fachlich beschlossen und benötigt seinen eigenen Umsetzungsschnitt. Ein
fertiges Fundament schließt das Gesamtissue nicht.

PE-A1 wurde nach ausdrücklichem Umsetzungsauftrag auf demselben Branch/PR
fortgeführt. Der anfängliche buildfreie Dokumentplan ist durch den
[PE-A1-Prüfplan](../.ci/package.json) mit `tools`, `production.adapter`,
`production.catalog`, `native.core` und `native.catalog` ersetzt. Die
[CLI/API-Anleitung](../tools/puzzle_production/README.md#pe-a1-aktuelle-namen-und-kategorien)
beschreibt Plan, Übernahme und Recovery. Der echte Bestand wurde ausschließlich
durch die explizite Migration nach v4/v7 übernommen; Definitionen, Kategorien,
Bilder und Herkunftsquellen bleiben unverändert. Die einmaligen T01-/T02-Belege
stehen kompakt im Liefer-PR, nicht als neue Dauerbenchmark- oder Bildfamilie.
Technische Lieferung, unabhängiges Review, persönliche Editorprobe und Merge
bleiben getrennt; PE-A1 liefert keine Weboberfläche.
