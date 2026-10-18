# Katalogsortierung und Hinzugefügt-Metadaten · KU-B

Stand: 18.10.2026 · Spezifikation 1.0 · freigegebener Sollstand, nicht implementiert

Der Eigentümer hat die Katalogüberarbeitung als Spezifikation freigegeben.
[KU / #244](https://github.com/venomenon328/picross/issues/244) führt
KU-A für die [Kartengestaltung](CATALOG_PRESENTATION.md) und KU-B für die hier
beschriebene vollständige Sortierfunktion einschließlich Daten und Persistenz.
Empfohlene Reihenfolge ist KU-A, danach KU-B; beide liefern jeweils ein selbständig
abnehmbares Ergebnis in einem eigenen späteren Implementierungs-PR.
Diese Spezifikation ist keine Implementierungsfreigabe, Startprüfung oder Abnahme.

## Geltung und Ausgangsstand

Geprüfte Ausgangsbasis ist `main@72ba39391833f6fd834d0a6afaf881c86c7bdc3a`.
Der aktuelle Katalog übernimmt die kanonische Registryreihenfolge und bildet
anschließend Seiten mit höchstens 24 Karten. Kategorie, Seite, Scrollposition
und Auswahl sind nach [KAT-2](KAT2_VERIFICATION.md) sitzungsgebunden.
Inhaltsregistry und Runtime führen derzeit kein Hinzugefügt-Datum.

KU-B ergänzt gezielt diesen Ansichtsvertrag, eine eng begrenzte UI-Präferenz
und eine versionierte Katalogmetadatenquelle. [Kategorien](CATEGORIES.md),
[ZA-1](ZA1_ADAPTER.md), [SD-C1](SD_CATALOG.md), [P1](PROTOTYPE_P1.md),
[Webvertrag](WEB_HOSTING.md) und [CI-Policy](CI_POLICY.md) gelten im übrigen
Umfang weiter. Schwierigkeit wird ausschließlich aus der akzeptierten Projektion
gelesen. Es entstehen keine Neubewertung, Solverläufe, Inhaltsproduktion,
Fortschrittsregeln oder Änderungen an Rätseldefinitionen und bestehenden Saves.

## KU-B-D01 · Bedienung und Anfangszustände

Direkt neben der Kategorienauswahl stehen ein Dropdown **„Sortieren nach“**
und ein kompakter Richtungsumschalter. Beide verwenden die bestehende Buch-UI,
lesbare Beschriftungen und ihre üblichen Hover-/Fokus-/Trefferflächen.
Kategorie, Sortierung, Einstellungen/Info und Beenden bleiben in den gemeinsamen
Fenster-/UI-Konfigurationen erreichbar. Das Bedienpaar erscheint erst mit der
vollständigen KU-B-Funktion, ohne funktionslose Voraboption in KU-A.

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

Zuerst den gesamten gültigen sichtbaren Bestand nach Kategorie filtern, dann alle
Treffer sortieren und erst danach Seiten mit höchstens 24 Karten bilden. Nur die
aktuelle Seite zu sortieren erfüllt den Vertrag nicht. Leerbestand, leere Kategorie
und ungültiger Katalog bleiben unterscheidbar; es entsteht kein neuer Filter.

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

Die kleine versionierte Präferenz liegt getrennt von `user://p1/saves/` im
vorhandenen App-Datenbereich. Pfad, exakte Felder, Werte und Größenlimit werden
vor der ersten Codeänderung festgelegt. Save-Schema 1, Slots, Primary/Backup/Temp,
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
[WEB-1](WEB_HOSTING.md). Lesen erst nach initialisiertem Dateisystem, Schreiben
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

KU-B umfasst die kontrollierte Ermittlung und Übernahme für den vollständigen
dann aktuellen Registrybestand. Jede ID erscheint im Bericht, unabhängig von
ihrer aktuellen Sichtbarkeit. Ein damals unsichtbarer Registryeintrag allein
belegt noch keine Aufnahme als spielbares Rätsel. Dieser Spezifikationsauftrag
führt den Bestandsnachtrag noch nicht aus.
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
außerhalb der historischen Produktions-/Integrationsbindungen. Der vollständige
Eintragsvergleich alter kompakter Integrationsmanifeste bleibt erhalten.
Die Runtime erhält nur die minimale spoilerfreie Datumsprojektion neben den
bestehenden Katalogangaben. Schwierigkeiten und deren Quellenpriorität bleiben
inhaltlich unverändert; keine neuen Bewertungsfelder oder Methoden.

Konkrete Pfade, Formate/Felder, Grenzen, Projektionsversion und Journalübergänge
werden vor der ersten KU-B-Codeänderung in dieser Datei, [CATEGORIES](CATEGORIES.md)
und [ZA-1](ZA1_ADAPTER.md) gemeinsam festgelegt. Neue Felder werden nicht unter
einem bisherigen exakt definierten Formatnamen stillschweigend zugelassen.
Die aktuell gültigen Runtime-v2-/v3- und Inhalts-/Journalaltformate behalten ihre
exakten Leseregeln; fehlender Zeitpunkt alter Daten bedeutet unbekannt.

Writer, Loader und Validator verwenden dieselbe strikte Interpretation.
Registrieren, Rasterupdate, Ratingübernahme, explizites Sync, Bestandsnachtrag und
Recovery prüfen dieselbe Datumsquelle und publizieren dieselbe kanonische
Runtimeprojektion. Unbekannte Formate, ungültige Werte, doppelte oder unregistrierte
IDs, widersprüchliche Belege und fremde Zwischenstände werden nicht still akzeptiert.
Die Abwesenheit eines erlaubten Altwerts und eine vorhandene ungültige Datei sind
verschiedene Fälle. Bestehende Pfad-/Dateigrenzen und Spoilerprüfung bleiben wirksam.

Datumsquelle, Bericht und Runtime werden über den gemeinsamen Transaktionsweg
mit alter/neuer Bindung und unverändertem Schutz fremder Änderungen übernommen.
Abbruch/Recovery, No-op und exakte Altjournal-Kompatibilität gehören zum Paket.
Keine zweite unkoordinierte Schreibstrecke, keine offenen gemischten Projektionen
und kein nachträgliches Pflicht-Sync nach angeblich erfolgreicher Recovery.
Produktionscleanup entfernt keine noch maßgeblichen Datumsbelege.

## KU-B · Akzeptanz und getrennte Gates

Die Kennungen entsprechen dem übergeordneten KU-Issue; D01–D06 konkretisieren
dieselben Anforderungen.

| Kennung | Überprüfbares Ergebnis |
| --- | --- |
| KU-B-A01 | **Bedienleiste:** „Sortieren nach“ mit den vier Optionen Kategorie, Größe, Schwierigkeit und Hinzugefügt sowie Richtungsumschalter steht direkt neben der kompakteren Kategorienauswahl im Buchstil. Alle Kopfaktionen bleiben bei UI100/125 einschließlich des engen gemeinsamen Fensters erreichbar. Kategorie bezeichnet die redaktionelle Reihenfolge. |
| KU-B-A02 | **Schlüssel:** Kategorie folgt `category.order`, Größe allen Rasterzellen `Breite × Höhe`, Schwierigkeit vorhandenen L1–L5-Stufen und Hinzugefügt dem gespeicherten UTC-Zeitpunkt. `20 × 30` und `30 × 20` sind bei Größe gleich. Keine Schwierigkeit aus Größe/Farbe/Spielstand ableiten; keine Motivnamen als Sortierschlüssel. |
| KU-B-A03 | **Richtung und Gleichstände:** Erststart Kategorie aufsteigend; ein anderes Kriterium erhält seine Anfangsrichtung nach D01. Umkehr betrifft nur den Primärvergleich, Gleichstände bleiben in kanonischer Blattfolge, fehlende Schwierigkeit und unbekannte Zeitpunkte stehen in beiden Richtungen am Ende. Dieselbe Auswahl bleibt für die Ansicht ein No-op. |
| KU-B-A04 | **Gemerkte Auswahl:** Das vollständige Paar aus Kriterium/Richtung übersteht echten nativen Prozessneustart, Browserreload und Browserneustart im gleichen Profil. Fehlende/ungültige Präferenz fällt auf den Default zurück. Schreibfehler, Retry, rasche Auswahlwechsel und asynchroner Sync folgen D03; identische erneute Auswahl darf ungesicherte Präferenz speichern, ohne die Ansicht zu verändern. Rätselsaves und die bestehenden getrennten Speichergrenzen bleiben erhalten. |
| KU-B-A05 | **Filter, Seiten und Identität:** Erst filtern, den gesamten Trefferbestand sortieren, dann 24 Karten je Seite. Tatsächlicher Filter-/Sortierwechsel beginnt auf Seite 1/oben; Rückkehr erhält den Sitzungskontext. Blattnummer, Öffnen, Reset, Recovery, Fokus, Auswahl und bestehende Dialoge bleiben an die richtige ID gebunden. Resize, Leer-/Fehlerzustände und Karten-/Revealgrenzen bleiben korrekt; keine dauerhafte Blattnummernreform. |
| KU-B-A06 | **Bedeutung von Hinzugefügt:** Erste erfolgreiche Registrierung als spielbares Rätsel gemäß D04; kein Motiv-, Rating-, Änderungs- oder späteres Merge-Datum. Neue Registrierung fixiert tatsächliche UTC einmal im mutierenden Transaktionskontext, lesende Vorschau setzt keinen endgültigen Zeitpunkt. Wiederholung, Update, Kategorie-/Revealänderung, Ratingübernahme, Sync, Cleanup und Recovery erhalten Zeitwert oder erlaubtes unbekannt. |
| KU-B-A07 | **Kompatibler Datenweg:** Eigene ID-gebundene Quelle außerhalb historischer Bindungen und minimale Runtimeprojektion UTC/null sind in Writer, Loader, Validator und allen Register-/Update-/Sync-/Adopt-/Recoverypfaden gemeinsam versioniert. Exakt gültige Altformate bleiben lesbar; ungültige vorhandene Daten und fremde Änderungen werden nicht als fehlend kaschiert. Alte/neue Zustände vor Schreiben prüfen; Transaktion, Abbruch, Recovery und echte No-ops erfüllen D06. |
| KU-B-A08 | **Historischer Bestand:** Für jede ID des vollständigen aktuellen Registrybestands liegen prüfbarer Plan, tatsächliche Übernahme und dauerhafter Beleg oder begründete Lücke nach D05 vor. Eindeutiger Erstregistrierungsbeleg hat Vorrang, sonst gilt der früheste nachweisbare gültige sichtbare Integrationssnapshot mit seiner Commitzeit. Herkunftstyp, UTC-Ereignis-/Referenzzeit, Quelle und Rekonstruktionscharakter bleiben nachvollziehbar; keine erfundenen Daten oder ausgelassenen IDs. |
| KU-B-A09 | **Umfang und Sicherheit der Übernahme:** Definitionen, Hinweise, Raster, Bewertungen, Methodenfreeze, IDs/Keys/Slots, Runtime-Revisionen, Assets, historische Produktionspakete/Manifeste und Spielstände bleiben unverändert. Keine Solver-/Produktions-/Bewertungsreplays oder erneute historische Bild-/Rasterproduktion. Git-Historie wird nur für den ausdrücklichen redaktionellen Nachtrag ausgewertet, nicht im Spiel oder in allgemeinen Tests. |
| KU-B-A10 | **Lieferung:** Alle vier Sortierarten, gemerkte Auswahl und tatsächliche neue/alte Metadaten sind vollständig nutzbar. Eigenständige synthetische Tests sichern Richtungen, Gleichstände, unbekannte Werte, mehrseitige Filter, Rückkehr/Neustarts, ID-gebundene Aktionen und Daten-/Recoverygrenzen einschließlich Backfillpriorität und Wiederholbarkeit. Der echte Bestandsbericht bleibt gesonderter redaktioneller Nachweis; Verträge, Bedienanleitung und tatsächlicher Exportinhalt entsprechen der Lieferung. |

Alle automatisierten Prüfungen verwenden eigenständige synthetische Eingänge,
einschließlich der Historien-, Rating-, Integrations- und Runtimefälle. Der echte
Bestandsbericht ist ein redaktioneller Übernahmenachweis, kein neuer CI-Testbestand.
Keine Solverläufe oder Produktionsreplays für den Datumsnachtrag. Native
Darstellung/Bedienung und Browserpersistenz folgen der aktuellen CI-Policy mit
den gemeinsamen Konfigurationen 1280×720/UI125, 1920×1080/UI100 und
2560×1440/UI125; keine historische Prüfmatrix neu eröffnen.

- **KU-B-T01:** Implementierer liefert A01–A10 samt aktueller ausgewählter
  Pflicht-CI, nativen Windows- und Chromium-/Firefoxnachweisen, tatsächlichem
  Bestandsbericht und getrenntem Selbstreview vor Übergabe/Implementierungsmerge.
  Pflichtnachweise sind an Head, Basis, tatsächlichen Checkout und Run gebunden.
- **KU-B-R01:** Qualifizierter unabhängiger Reviewer prüft den konkreten Head
  technisch und visuell sowie Datumsprovenienz, Quellenlücken und Erhalt der
  historischen Bindungen vor Merge. Selbstreview ersetzt diese Prüfung nicht.
- **KU-B-M01:** Eigentümer prüft vor Implementierungsmerge am gebundenen Build
  Auswahl/Richtung, Lesbarkeit, größere Trefferlisten, Rückkehr und Wiederaufnahme;
  Reset-/Recoveryproben ausschließlich mit isolierten Testständen. Tatsächliche
  Fenster-/UI-/Windows-Skalierung und Einzelergebnisse dokumentieren.

Alle KU-B-Gates sind offen. KU-A kann vorher eigenständig abgenommen werden;
seine technische oder persönliche Abnahme nimmt KU-B nicht vorweg. Der aktuelle
Auftrag erzeugt ausschließlich Spezifikation und Issue-Pakete, keine Datenübernahme,
Implementierung, Code-PR, neue Produktprüfung, Merge oder Produktveröffentlichung.
