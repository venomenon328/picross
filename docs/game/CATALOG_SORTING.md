# Katalogsortierung und Hinzugefügt-Metadaten · KU-B

## Geltung und Zuständigkeit

Dieser Vertrag besitzt Sortiersemantik, die unabhängige Sortierpräferenz sowie
Bedeutung, Herkunft und Sidecar-/Planformate von „Hinzugefügt“. Er bewertet keine
Rätsel neu und verändert keine Definitionen oder bestehenden Rätselsaves.
Die Regeln im aktuellen Git-Stand sind vom Liefer- und Abnahmestand im Issue/PR
zu unterscheiden.

| Bereich | Maßgebliche Quelle |
| --- | --- |
| Karten, Filter, Seitenteilung und Vorschauen | [Katalogdarstellung](CATALOG_PRESENTATION.md) |
| Buchnavigation und Besuchsrückkehr | [Buchdarstellung](BOOK_INTEGRATION.md) |
| Schrift, Menüs und Piktogramme | [Handgezeichnete UI](HAND_DRAWN_UI.md) |
| Registry-/Runtimeprojektion und Spieler-Lesekompatibilität | [RI-ONE](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md) |
| Kategorien | [CATEGORIES](CATEGORIES.md) |
| Vorhandene Schwierigkeit | [SD-Catalog](../difficulty/SD_CATALOG.md) |
| Rätselspeicherung | [P1](PROTOTYPE_P1.md) |

## KU-B-D01 · Bedienung und Anfangszustände

Direkt neben der Kategorienauswahl stehen ein Dropdown **„Sortieren nach“**
und ein kompakter Richtungsumschalter. Beide verwenden die bestehende Buch-UI,
lesbare Beschriftungen und ihre üblichen Hover-/Fokus-/Trefferflächen.
Schrift, gezeichnete Dropdowns, Richtungs-/Seitenpfeile, optische Ausrichtung,
Trefferflächen und Popupbudgets folgen [HAND_DRAWN_UI](HAND_DRAWN_UI.md).
Kategorie, Sortierung und Kopfaktionen bleiben in den unterstützten Fenster-/
UI-Konfigurationen erreichbar.

| Auswahl | Primärer Sortierwert | Anfangsrichtung bei neu gewähltem Kriterium |
| --- | --- | --- |
| Kategorie | Redaktionelles `category.order` aus der validierten Kategorienquelle | Kategorienfolge aufsteigend |
| Größe | Zellzahl `Breite × Höhe` | Kleinste zuerst |
| Schwierigkeit | Vorhandene Stufe L1 bis L5 | Sehr leicht zuerst |
| Hinzugefügt | UTC-Zeitpunkt nach KU-B-D04/D05 | Neueste zuerst |

Der Richtungsumschalter kehrt ausschließlich den Primärvergleich um. Seine
zugängliche Beschriftung benennt die aktuelle Bedeutung: Kategorienfolge oder
umgekehrte Kategorienfolge, kleinste/größte, sehr leichte/sehr schwere oder
neueste/älteste zuerst. „Kategorie“ behauptet keine alphabetische Reihenfolge.
Das Entfernen des Schwierigkeitstooltips aus KU-A verbietet keine kurze
Bedienerklärung dieses eigenständigen Umschalters.

Ohne gültige gespeicherte Präferenz beginnt das Spiel bei **Kategorie aufsteigend**.
Ein tatsächlicher Wechsel des Sortierkriteriums setzt dessen obige Anfangsrichtung;
eine erneute Auswahl desselben Kriteriums ist für die Ansicht ein No-op:
Reihenfolge, Richtung und Seitenposition bleiben unverändert. Eine ausstehende
oder fehlgeschlagene Präferenzsicherung darf dabei nach D03 erneut versucht werden.
Der Richtungsumschalter ändert das aktuelle Kriterium nicht. Eine andere
Kategorienfilterung erhält das zuletzt gewählte Paar aus Kriterium und Richtung.

## KU-B-D02 · Reihenfolge, Seiten und Identität

Zuerst den gesamten gültigen sichtbaren Bestand nach allen gemeinsam aktiven
[K-A-Filtern](CATALOG_PRESENTATION.md#k-a--kombinierbare-sitzungsfilter-485) filtern, dann alle
Treffer sortieren und erst danach Seiten mit höchstens 24 Karten bilden. Nur die
aktuelle Seite zu sortieren erfüllt den Vertrag nicht. Leerbestand, leere Kategorie
und ungültiger Katalog bleiben unterscheidbar; K-A ändert keine Sortierwerte.

Bei gleichen Primärwerten entscheidet immer die unveränderte kanonische Blattfolge
aufsteigend. Dieser Gleichstandsvergleich wird durch den Richtungsumschalter nicht
umgekehrt. `20 × 30` und `30 × 20` haben dieselbe Größe; zusätzliche verdeckte
Sortierung nach Breite, Motivnamen, Dateistämmen oder Bildern entfällt.
Fehlende Schwierigkeit und unbekanntes Hinzugefügt-Datum stehen **in beiden
Richtungen am Ende**, untereinander ebenfalls in kanonischer Blattfolge.
Ungültige vorhandene Metadaten sind ein Validierungsfehler, kein fehlender Wert.

Ein tatsächlicher Filter-, Kriteriums- oder Richtungswechsel setzt Seite und
Scrollposition auf Seite 1/oben. Öffnen und Rückkehr eines Rätsels erhalten
Filter, Kriterium, Richtung, Seite, Scrollposition und ausgewählte ID innerhalb
der Sitzung. UI-Skalierung und Resize ändern die gewählte Ordnung nicht.
Bestehende begrenzte Karten-/Reveal-Lebenszyklen bleiben erhalten.

„Blatt NN“ stammt weiterhin aus der kanonischen Registryzuordnung, niemals aus
dem sortierten Anzeigeplatz. Sortierung ändert keine Registryreihenfolge, ID,
Key, Save-Slot oder Definition. Öffnen, Reset und Recovery einschließlich schon
geöffneter Bestätigungsdialoge bleiben an ihre ursprüngliche Registry-ID gebunden.
Diese Stabilität betrifft Ansichtswechsel im selben Inhaltsstand; eine neue
dauerhaft vergebene Blattnummer über spätere Bestandserweiterungen hinweg ist
nicht Teil von KU-B. Die vorhandene Spoilergrenze gilt auch für Vergleichsschlüssel.

## KU-B-D03 · Genau eine gespeicherte UI-Präferenz

Das zuletzt gewählte **Paar aus Kriterium und Richtung** bleibt nach regulärem
Neustart im selben lokalen Speicherprofil erhalten. Beide Werte werden gemeinsam
validiert und gespeichert. Es entsteht weder ein separates Gedächtnis pro
Kriterium noch eine Präferenz pro Rätsel. Kategorie, Seite, Scrollposition und
Rätselauswahl bleiben sitzungsgebunden: Ein neuer Prozess beginnt bei „Alle Rätsel“,
Seite 1/oben, mit dem gültigen zuletzt gespeicherten Sortierpaar.

Die versionierte Präferenz liegt getrennt von `user://p1/saves/` im
vorhandenen App-Datenbereich. Pfad, Felder, Werte und Größenlimit stehen
unter KU-B-P01. Save-Schema 1, Slots, Primary/Backup/Temp,
History, Abschluss und Rätsel-Recovery werden dafür weder erweitert noch migriert.
Ein reiner Sortier-/Filterwechsel erzeugt oder verändert keine Rätselsavedatei.

Fehlende Präferenz verwendet den Default. Unbekannte Version, falsche Typen,
unzulässige Werte oder ein beschädigtes Dokument werden als ganzes Paar verworfen;
keine teilweise Übernahme und kein automatisches Umschreiben beim Start.
Eine neue ausdrückliche Auswahl darf ausschließlich diese eigene Präferenz neu
speichern. Ein bereits erfolgreich gespeicherter identischer Zustand erzeugt keine
neue Schreiboperation. Bei ausstehender oder fehlgeschlagener Präferenzsicherung
darf dieselbe ausdrückliche Auswahl deren Speicherung erneut versuchen; die
Sortierung, ihre Richtung und die Seitenposition bleiben dabei unverändert.
Native Veröffentlichung ist atomar; bei Schreibfehler bleibt die vorige gültige
Fassung erhalten. Die aktuelle Auswahl wirkt sofort in der laufenden Sitzung.
Ein tatsächlicher Präferenzfehler wird knapp und nicht modal angezeigt, ohne
das Spielen oder Navigieren zu sperren; erneute Auswahl erlaubt einen neuen Versuch.

Im Browser verwendet die Präferenz denselben origin-/profilgebundenen
`/userfs`-Speicher und die bestehende serialisierte IDBFS-Synchronisation nach
[WEB-1](../operations/WEB_HOSTING.md). Lesen erst nach initialisiertem Dateisystem, Schreiben
erst nach erworbener Einzeltabsperre; keine zweite Datenbank oder eigene Sperre.
Eine neue Auswahl während laufender Synchronisation muss am Ende das jüngste
Paar sichern. Erst der echte Callback bestätigt dauerhafte Speicherung.
Reguläres Beenden führt den vorhandenen Synchronisationsweg aus. Ein isolierter
Präferenzfehler ist kein Rätselsavefehler; bereits ausstehende oder fehlgeschlagene
Rätselsicherungen behalten ihre unveränderten Flush-/Sperr-/Retryregeln und dürfen
durch diese Trennung nicht als gesichert ausgegeben werden.

Andere Origins/Profile und Windows teilen keine Präferenz. Versions-/Assetpfade
begründen keinen neuen Speicherraum auf demselben Origin. Abruptes Schließen vor
bestätigtem Sync, Privatmodus, gelöschte Websitedaten und Browserspeicherräumung
behalten die dokumentierten Grenzen; keine Cloud- oder verlustfreie Abruptschlusszusage.

## KU-B-D04 · Bedeutung und Lebenszyklus von „Hinzugefügt“

„Hinzugefügt“ bezeichnet die erstmalige erfolgreiche Registrierung als spielbares
Rätsel im Zielkatalog. Es bezeichnet weder die kreative Motiverstellung noch
Bildfreigabe, Schwierigkeitsbewertung, letzten Export, letzte Bearbeitung oder
späteres Hosting. Der Zeitpunkt ist eine Eigenschaft der Rätsel-ID.

Bei einer neuen Erstregistrierung wird eine tatsächliche UTC-Zeit einmalig im
mutierenden Registrierungsvorgang fixiert und zusammen mit dessen neuen Daten
in der Transaktion gebunden. Ein lesender Plan setzt keinen Zeitpunkt. Das
Datum darf vor erfolgreicher Veröffentlichung nicht als abgeschlossene Aufnahme
ausgegeben werden; ein zurückgerollter Versuch hinterlässt keinen neuen Wert.
Ein künftiger PR-Merge oder Deploymentzeitpunkt wird nicht vorweggenommen.

Identische Wiederholung, Update eines bereits registrierten Rasters, Neubewertung,
Sync, Export, Produktionscleanup und Sichtbarkeitswechsel erhalten einen bestehenden
Zeitpunkt. Recovery verwendet ausschließlich die gebundenen alten/neuen Werte
des Journals, niemals die aktuelle Uhrzeit. Wiederholen alter registrierter Daten
ohne Datumsbeleg setzt nicht nachträglich „jetzt“; deren unbekannter Wert bleibt
bis zu einer ausdrücklich belegten Übernahme unbekannt.

Die Quelle führt einen kanonischen UTC-Zeitpunkt oder ausdrücklich unbekannt.
Vollständiges Datum und Uhrzeit mit UTC-Bezug sind typisiert und auf tatsächliche
Kalendergültigkeit zu prüfen; lokale Anzeigezeichenketten sind kein Sortierwert.
Die Runtime benötigt nur diesen Wert beziehungsweise null. Der Herkunftsbeleg
gehört in den Inhalts-/Nachweisbereich und wird nicht mit dem Spieler ausgeliefert.

## KU-B-D05 · Einmaliger belegbarer Bestandsnachtrag

Ein ausdrücklich beauftragter Bestandsnachtrag ermittelt und übernimmt Werte
für den vollständigen zum Plan gehörenden Registrybestand. Jede ID erscheint im Bericht, unabhängig von
ihrer aktuellen Sichtbarkeit. Ein damals unsichtbarer Registryeintrag allein
belegt noch keine Aufnahme als spielbares Rätsel.
Die Rekonstruktion verwendet die **erste belegte Katalogaufnahme** nach folgender
Quellenpriorität:

1. Ein eindeutiger vorhandener Beleg der erfolgreichen Erstregistrierung liefert
   seine tatsächliche UTC-Ereigniszeit.
2. Sonst darf der früheste nachweisbare versionierte, damals gültige und sichtbare
   Registryeintrag mit der zugehörigen Commitzeit übernommen werden. Der Snapshot
   muss zur nachvollziehbar integrierten Historie gehören; eindeutig an die
   Integration gebundene PR-Vorgeschichte darf einen früheren Eintrag belegen.
3. Bei fehlender oder uneindeutiger Provenienz bleibt der Wert null. Die Lücke wird
   mit den geprüften Quellen und dem konkreten Grund dokumentiert.

Der zweite Weg ist eine historische Rekonstruktionskonvention. Sein Zeitpunkt wird
im dauerhaften Beleg ausdrücklich als Referenzzeitpunkt aus Integrationshistorie
gekennzeichnet, nicht als sekundengenau nachgewiesene damalige Toolausführung.
Ein späterer Main-Merge ist kein Ersatz für einen früheren belegbaren gültigen
Integrationssnapshot. Dateisystemzeiten, jüngste Datei-Commits, Ratingberichte und
bloße Erzeugungsdaten von Bildern/Paketen dürfen keinen Hinzugefügt-Wert ersetzen.

Vor Übernahme entsteht ein lesender Plan mit genau einer Zeile je aktueller Registry-ID:
bisheriger und vorgeschlagener Wert, Herkunftstyp, Ereignis-/Referenzzeit, konkreter
Quellcommit beziehungsweise unveränderlicher Beleg samt Dateipfad/Hash und
Begründung oder offene Lücke. Der Bericht bindet den geprüften Ausgangsbestand
und trennt direkte Registrierungsbelege, Historienrekonstruktionen und unbekannte
Fälle. Keine nachträgliche Änderung historischer Freigaben, Pakete oder Manifeste.

Die ausdrückliche Übernahme kontrolliert erneut ihre Quellen und Ausgangsbytes,
ändert nur die freigegebenen Katalogmetadaten und ihre Projektion und erhält den
vollständigen Bericht dauerhaft. Identische Wiederholung ist ein echter No-op.
Neu hinzugekommene IDs, abweichende Quellen oder fremde Änderungen verlangen einen
aktualisierten Plan; kein stilles Überschreiben. Vollständigkeit bedeutet: jede
aktuelle Registry-ID ist begründet übernommen oder als konkrete Quellenlücke ausgewiesen,
nicht eine erfundene lückenlose Datumsreihe.

## KU-B-D06 · Gemeinsame Versionierung und Transaktionen

Hinzugefügt-Daten erhalten eine eigene autoritative, ID-gebundene Katalogquelle
außerhalb der historischen Produktions-/Integrationsbindungen. Aktuelle Werte
werden direkt gelesen; ihre historischen Herkunftsangaben verpflichten nicht
zum erneuten Öffnen früherer Produktionspakete oder Nachtragsberichte.
Die Runtime erhält nur die minimale spoilerfreie Datumsprojektion neben den
bestehenden Katalogangaben. Schwierigkeiten und deren Quellenpriorität bleiben
inhaltlich unverändert; keine neuen Bewertungsfelder oder Methoden.

Konkrete Sidecar-/Plan-/Präferenzformate stehen unter KU-B-P01.
Aktuelle Runtimeprojektion und reine Spieler-Lesekompatibilität stehen in
[RI-ONE](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md), aktuelle Metadatenjournale in
[SD-Catalog](../difficulty/SD_CATALOG.md#aktuelle-katalogjournale).
Erstregistrierung folgt ausschließlich [RI](../production/PUZZLE_INTEGRATION.md).
Neue Felder werden nicht unter einem bestehenden geschlossenen Formatnamen
stillschweigend zugelassen. Frühere Inhalts-/Journalgenerationen sind keine
aktuellen Schreib- oder Recoverywege.

Writer, Loader und Validator verwenden dieselbe strikte Interpretation.
Registrieren, Rasterupdate, Ratingübernahme, explizites Sync, Bestandsnachtrag und
Recovery prüfen dieselbe Datumsquelle und publizieren dieselbe kanonische
Runtimeprojektion. Unbekannte Formate, ungültige Werte, doppelte oder unregistrierte
IDs, widersprüchliche Belege und fremde Zwischenstände werden nicht still akzeptiert.
Die Abwesenheit eines erlaubten Altwerts und eine vorhandene ungültige Datei sind
verschiedene Fälle. Bestehende Pfad-/Dateigrenzen und Spoilerprüfung bleiben wirksam.

Datumsquelle, Bericht und Runtime werden über den gemeinsamen Transaktionsweg
mit alter/neuer Bindung und unverändertem Schutz fremder Änderungen übernommen.
Abbruch/Recovery und No-op folgen dessen aktuellem geschlossenen Journalvertrag.
Keine zweite unkoordinierte Schreibstrecke, keine offenen gemischten Projektionen
und kein nachträgliches Pflicht-Sync nach angeblich erfolgreicher Recovery.
Produktionscleanup entfernt keine noch maßgeblichen Datumsbelege.

## KU-B-P01 · Verbindliche Implementierungsverträge

Die folgenden exakten Formate konkretisieren D03–D06. Sie sind die
Fachautorität für Hinzugefügt-Sidecars, Nachtragspläne und Sortierpräferenz.

### Autoritative Hinzugefügt-Daten und Herkunft

Je registrierter ID führt der Einzelrecord `content/puzzles/<id>.json` das Objekt `added` mit exakt `added_at,provenance`. Der Zeitpunkt wird bei der ersten erfolgreichen Registrierung gesetzt. Die Runtime v9 enthält ausschließlich den UTC-Zeitpunkt oder null. Die Herkunft enthält genau `kind,reference_time,commit,evidence,reason`. Die Fälle registration, direct, git-snapshot und unknown behalten ihren wirksamen Bezug. Bestehende Verweise auf Nachtragsberichte binden Pfad und SHA-256 der damaligen Originalbytes.

### Historischer Plan und explizite Übernahme

Die einmalige Bestandsrekonstruktion nach D05 ist abgeschlossen. Ein aktueller Datumsplan bindet Basiscommit, Kategorien, Runtime und die gewählten Record- und Definitionsbytes. Bereits bekannte Erstaufnahmen bleiben auch bei späteren Integrationen und bei identischer Wiederholung erhalten. Eine Uhrzeit aus einem Folgelauf ist keine Erstaufnahme.

### Lokale UI-Präferenz

Datei `user://p1/catalog-preference.json`, außerhalb `p1/saves`; höchstens 1024
UTF-8-Bytes. Exakt `format,criterion,direction`, Format
`picross-catalog-preference-v1`; Kriterien `category,size,difficulty,added`,
Richtungen `asc,desc`. Fehlende/ungültige Datei einschließlich doppelter Schlüssel
setzt das gesamte Paar auf Kategorie/aufsteigend, ohne Schreiben beim Lesen.
Ein neuer gültiger Wert wird nativ über eine temporäre Schwesterdatei mit
Flush und atomarem Rename publiziert; Fehler bewahrt die vorherige gültige Datei.
Dieselbe erfolgreich gespeicherte Auswahl ist ein echter Schreib-No-op.

Sitzungswirkung, No-op/Retry, Browserhydration, Einzeltabsperre und gemeinsame
IDBFS-Warteschlange folgen D03; Sortier-/Seiten-/Identitätssemantik folgt D02.

### Übernahme eines direkten Erstaufnahmebelegs

Ein expliziter Nachtrag für ein bisher unbekanntes Datum enthält ID, Ereignis `first-playable-registration`, Erfolg und UTC-Zeitpunkt. Der Plan bindet Belegbytes und Hash sowie die gewählten Records. Widersprüchliche Ereigniszeiten lassen den Wert unbekannt. Bereits bekannte Erstaufnahmen bleiben erhalten. Die Übernahme schreibt den gebundenen Plan als Nachtragsbericht, die betroffenen Records und die Runtime in einer Transaktion. Eine identische Wiederholung prüft Bericht und wirksame Datumswerte.

## KU-B · Anforderungsschlüssel

Diese Kennungen bleiben für Issue-, Code- und Nachweisverweise erhalten. Die
zugeordneten Fachabschnitte enthalten die Regeln; die Tabelle ist kein zweiter
abgeschriebener Anforderungskatalog.

| Kennung | Zuständiger Vertrag |
| --- | --- |
| KU-B-A01 | D01 · Bedienleiste und HZ-Gestaltung |
| KU-B-A02 | D01/D02 · Schlüssel |
| KU-B-A03 | D01/D02 · Anfangsrichtung, Umkehr und Gleichstände |
| KU-B-A04 | D03/P01 · Gemerkte Auswahl, No-op und Retry |
| KU-B-A05 | D02 · Filter, Seiten, Rückkehr und ID-Bindung |
| KU-B-A06 | D04 · Bedeutung und Lebenszyklus des Zeitpunkts |
| KU-B-A07 | D06/P01 · Versionierung und Transaktionen |
| KU-B-A08 | D05/P01 · Vollständiger belegbarer Bestandsnachtrag |
| KU-B-A09 | D05/D06 · Erhalt historischer Bindungen und Spielstände |
| KU-B-A10 | D01–D06/P01 · Vollständige Funktion und prüfbare Lieferung |

Automatisierte Prüfungen verwenden synthetische Historien-, Rating-, Integrations-
und Runtimeeingänge. Ein echter Bestandsbericht ist ein redaktioneller Beleg;
er ist kein allgemeiner CI-Testbestand. Aktueller Prüfbedarf folgt dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md), native Darstellung dem
[Modulvertrag](../ci/CI_C_NATIVE_GROUPS.md), Browserpersistenz dem
[Webvertrag](../operations/WEB_HOSTING.md). Historische KU-B-T01/R01/M01-Ergebnisse und spätere
Entscheidungen stehen in [#244 / PR #255](https://github.com/venomenon328/picross/pull/255).

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#244](https://github.com/venomenon328/picross/issues/244) und [PR #255](https://github.com/venomenon328/picross/pull/255).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CATALOG_SORTING.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
