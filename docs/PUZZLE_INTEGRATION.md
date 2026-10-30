# RI: Zuverlässige und messbare Rätselintegration

Spezifikationsstand: 29.10.2026 · RI-V01 · vom Eigentümer im Chat freigegeben.
Gesamtvorhaben: [RI / #477](https://github.com/venomenon328/picross/issues/477).
Geprüfte Ausgangsbasis: `main@ddacc8dbf328923626cbd0235578fda2bfb99c37`.

**Stand 30.10.2026:** RI-A ist über PR #484 auf `864c4e6` integriert;
[RI-A-T01](RI_A_VERIFICATION.md) bleibt historisch gebunden. RI-B ist auf dem
beauftragten Branch zu #479 implementiert; [RI-B-T01](RI_B_VERIFICATION.md)
führt aktuelle Nachweise und offene Gates. RI-C ist nicht implementiert.
RI-B-V01 und der gemeinsame B/C-Schnittstellenabgleich wurden vor Code in
#479/#480 gespeichert. Kein Mergeauftrag und keine echte Rätselintegration.

## 1. Problem, Belege und Ziel

Standardauftrag 4 nach [Authoring §8](ai-workflows/PUZZLE_AUTHORING.md) soll ein
abgenommenes Paket kontrolliert ins Spiel übernehmen. Der äußere Ablauf ist
bereits schlank; interne Prüfungen verursachen dennoch wiederholte Arbeit:
`export → plan → register` inspiziert den neuen Kandidaten auf dem vollständigen
normalen Neuregistrierungspfad achtmal. Dies sind Rekonstruktionen und Prüfungen
vorhandener Nachweise, keine acht neuen Suchsolverläufe. Umfassende
Publikationsguards lesen und hashen den gebundenen Bestand vor einzelnen
Dateischritten mehrfach. Sich überlagernde sichere Read-Wrapper traversieren
absolute Pfade wiederholt. Diese Aufrufstruktur ist belegt; ihre aktuellen
Laufzeitanteile sind noch nicht gemessen.

| Beleg | Beobachtung und Aussagegrenze |
| --- | --- |
| [Balut #462](https://github.com/venomenon328/picross/pull/462) | Zwei vorherige Budgetabbrüche; erfolgreicher Registrierungsaufruf nach ausdrücklich begrenzter Ausnahme in 453,593 s. Das ist die Gesamtdauer des Aufrufs, keine isolierte Publikationsmessung. |
| [Chocolate Hills #447](https://github.com/venomenon328/picross/pull/447) | Windows-Budgetabbruch; unveränderte Werkzeuge/Eingänge auf nativem Linux-Dateisystem mit Plan 7,587 s und Register 63,391 s erfolgreich. Kein kontrollierter Vergleich einzelner OS-/Datenträgerfaktoren. |
| [Huhn #453](https://github.com/venomenon328/picross/pull/453) | Nach vollständigem Rollback mit unveränderten Budgets im kürzeren Windows-Pfad erfolgreich. Kurze Pfade sind eine mögliche Zwischenhilfe, keine Erfolgsgarantie. |
| [Klauenhammer #476](https://github.com/venomenon328/picross/pull/476) | Export und Plan erfolgreich, Registrierung mit `resource_limit: catalog time budget exhausted` vollständig zurückgerollt. INT-01 bleibt offen; der Ablagemerge ist keine Spielintegration. |

Die vorhandenen Optimierungen aus [#286](https://github.com/venomenon328/picross/pull/286)
und [CI2-F/#425](https://github.com/venomenon328/picross/pull/425) sind Ausgangsbasis.
Sie werden nicht erneut als neue Lieferung versprochen. [CI2/#412](https://github.com/venomenon328/picross/issues/412)
bleibt ein separates Vorhaben mit seinen eigenen offenen Zeitbefunden.

Ziel ist eine zuverlässig abschließbare, messbare neue Rätselintegration mit
weniger wiederholter Prüf- und Dateisystemarbeit. Korrektheit, menschliche
Freigaben und ein sicherer vollständiger Zustand bestimmen den Erfolg.
Laufzeitüberschreitungen werden als Leistungsbefund sichtbar; eine echte
Abbruchgrenze bleibt eine getrennte technische Schutzmaßnahme.

## 2. Dauerhafte Entscheidungen

### RI-D01 · Geltung und unveränderte Grenzen

RI betrifft die Neuregistrierung in Standardauftrag 4 samt ihrer Wiederaufnahme.
Im ersten Paket gilt die neue Budgetpolitik ausschließlich für neue
Registrierungen und die Recovery unterstützter Registrierungsjournale oder
eindeutig zugehöriger zulässiger Stagingreste. Der gemeinsame Recoveryeinstieg
muss die Operation zuerst sicher klassifizieren. Gesperrte Altformate, insbesondere
registration-v1, werden dadurch nicht zugelassen. Journalbytes und -schemata
werden nicht um operative Budgets ergänzt.

Update, Sync, Bewertungs-/Hinzugefügt-Übernahme, Bildupdate und Methodenaktivierung
behalten ihre bisherigen operativen Defaults und äußeren Budgets. Eine gemeinsam
verwendete Hilfsfunktion darf deren Verhalten nicht versehentlich erweitern.
Verhaltenserhaltende sichere I/O-Verbesserungen dürfen gemeinsamen Code betreffen;
die betroffenen Aufrufer sind dann angemessen mitzuprüfen.

Die gesonderten 300 s für ZA-1-Eingangsprüfung/Extraktion sowie Import-, Reparatur-,
Proof-, Datei-, Byte-, Pixel- und Speichergrenzen bleiben erhalten. Ebenso bleiben
IDs, Runtime-Revisionen, Slots, Saves, Freigaben, Quellenbindungen, aktive Bilder,
Kategorien, Added-Daten und beide Difficulty-Freezes unverändert. Kein versteckter
Solver- oder Schwierigkeitsanalyselauf in Registrierung, Sync oder Recovery.

### RI-D02 · Warnung und Schutzrahmen trennen

Für die Registrierungspublikation wird der heutige harte 300-s-Rahmen durch
folgende getrennte Einstellungen der RI-A-Implementierung abgelöst:

| Aspekt | Freigegebener Sollstand |
| --- | --- |
| Warnschwelle | Nach 300 s sichtbare Laufzeitwarnung mit Phase und tatsächlichem Fortschritt; allein deshalb weder Abbruch noch Rollback. |
| Publikationsschutz | Vor dem Lauf konfigurierbarer positiver endlicher Zeitrahmen; vorläufiger Standard 1800 s (30 min). |
| Recovery | Eigenständig konfigurierbarer positiver endlicher Rahmen, vorläufig ebenfalls 1800 s; nicht aus dem verbrauchten Publikationsrest ableiten. |
| Gesamtauftrag | Export, Plan, Publikation, Recovery, GitHub-/CI-Wartezeit getrennt messen; kein pauschales 300-s-Gesamtgate für Schritt 4. |

Die 1800 s sind eine Übergangseinstellung mit Reserve, kein gemessenes Leistungsziel.
Eine spätere Änderung des Standards benötigt dokumentierte Messwerte und eine
ausdrückliche Fortschreibung dieser Entscheidung. Kein automatisches endloses
Verlängern oder Wiederholen; kein unendlicher Default. Ungültige Werte müssen
vor Mutation scheitern. Verschachtelte Aufrufe dürfen den wirksamen Rahmen nicht
heimlich verlängern; eine eigenständige Recovery beginnt mit ihrem eigenen Rahmen.

RI-A-V01 in #478 wurde vor Code freigegeben. Die konkrete
[CLI-/API-Bindung](ZA1_ADAPTER.md#ri--zeitbudget-und-diagnose-neuer-registrierungen)
dokumentiert Wertevalidierung, Ausgabe und kooperative Prüfgrenzen.

### RI-D03 · Messung und tatsächlicher Fortschritt

Ein kompakter operativer Bericht erfasst mindestens Eingangs-/Exportprüfung,
Snapshot/Planung, Staging, Publikation, Guards, Abschlussprüfung und gegebenenfalls
Recovery. Gesamtdauer und enthaltene/verschachtelte Phasen dürfen nicht additiv
als unabhängige Laufzeiten ausgegeben werden. Umgebung, Werkzeugcommit, Parameter,
Paketdateizahl und synthetische Bestandsgröße machen Vergleiche nachvollziehbar.

Erfassen: Anzahl vollständiger Kandidaten-/Proofprüfungen, Guards, sicherer Reads
und Pfadprüfungen sowie tatsächlich gelesene/gehashte Bytes. Zusatzmessung der
Methodenprüfung und Schreibsynchronisation erfolgt, soweit sie für die
Ursachenaufteilung nötig ist. Berichte benennen fehlende Messwerte ausdrücklich.

Regelmäßige Statusmeldungen nennen Phase, verstrichene Zeit und erledigte
Dateien/Arbeitsschritte. Eine bloße Lebensmeldung ist kein Arbeitsfortschritt und
setzt keine Deadline zurück. Zeitabbruch benennt die auslösende Phase, verbrauchte
Ressourcen und den belegten Publikations-/Journalzustand. Zeiten und Telemetrie
bleiben außerhalb kanonischer Inhalts-, Proof-, Rating- und Freigabeidentitäten.

### RI-D04 · Zuerst überlappende sichere Reads reduzieren

RI-A bündelt die nachweislich überlappenden `tx.read`-/`io.read`-/Pfadprüfungen
bei gleicher Aussage. Frische Bytes, Pfad-/Alias-/Link-/Dateityp-/Größenprüfungen
und Identitätsvergleich vor/nach Öffnen und Lesen bleiben erhalten.
Kein Dateiname-/mtime-Cache als Ersatz; keine geringere Fremdänderungserkennung.
Die vollständigen bisherigen Guards und Produktionsprüfungen bleiben in A aktiv.
Die bereits vorhandene unveränderliche Journalansicht und POSIX-Optimierungen
werden erhalten. Weitere Optimierungen brauchen einen belegten Kostenanteil.

### RI-D05 · Geprüftes Paket innerhalb eines definierten Kontexts wiederverwenden

RI-B reduziert wiederholte vollständige Kandidaten-/Proofprüfung in einer
zusammenhängenden Integration. Einmal tatsächlich geprüfte Eingänge, Freigaben,
Parameter und benötigte Werkzeug-/Methodenstände werden zusammen mit dem
unveränderlichen Staging gebunden. Beim Übernehmen und nach dem Schreiben muss
feststehen, dass genau diese Bytes vorliegen. Änderungen invalidieren den Kontext.

Ein Dateihash allein oder ein externes `pass`-Flag ist kein neuer Prüfbeweis.
Bevorzugt ist ein intern erzeugter Prüfkontext innerhalb einer zusammenhängenden
Ausführung; getrennt gestartete bestehende CLI-Befehle bleiben eigenständig sicher
prüfend. Prozess-/Lebensdauergrenze, API/CLI, Stagingeigentum, Invalidierung und
Ausgabekontrolle sind vor Code in RI-B-V01 zu schließen. Ein dauerhafter
prozessübergreifender Vertrauenscache ist durch RI nicht freigegeben.
Die bestehende Planprüfung und tatsächliche Übernahmeautorisierung bleiben erhalten.

RI-B-V01 konkretisiert den engen gelieferten Weg: Nur eine mutierende neue
Registrierung erzeugt nach erfolgreichem unabhängigem Staging-Replay einen
internen prozess-/threadgebundenen Kontext. Eingangsprüfung und Staging-Replay
bleiben vollständig. P3 und ausschließlich der neue Eintrag im P5-Replay verwenden
frische vollständige Inventar-/Byte-Nachprüfungen statt desselben Proof-Replays.
Der Kontext bindet Original-/Stagingidentitäten, tatsächliche Freigabe-/Parameter-
bytes, Checked-Input, Ausgangssnapshot, konkretes Journal samt Added-Zeitpunkt,
Addition-Quellpfade sowie tatsächliche Werkzeug-/Methodenbytes und Laufzeitstände.
Austausch, Zusatz/Fehlen oder Änderung invalidieren ihn; Scopeende bei Erfolg,
Fehler oder Abbruch ebenfalls. Keine Serialisierung und kein persistenter Cache.
Ohne privaten Kontext bleibt der bisherige vollständige Prüfweg aktiv.

`export`, `plan`, `verify-export`, No-op und Updates prüfen unabhängig nach ihren
bisherigen Verträgen. `plan` bleibt lesend, `register` ausdrücklich autorisiert.
Recovery erhält niemals den Kontext. B-Paketbeweis und der vollständige
Quell-/Namespacebeweis bleiben unabhängige Autoritäten: B-Erfolg belegt keinen
unveränderten Katalog, ein späterer C-Snapshot keine Kandidatenprüfung.
**B ändert weder globale Guard-Aufrufstellen/-frequenz noch P0–P6/R0–R2,
Erkennungszeitpunkte oder Recoverysemantik.** Keine neue Journalgeneration.

### RI-D06 · Globale Kontrolle an definierte Transaktionsgrenzen binden

RI-C soll die Multiplikation vollständiger Bestandskontrollen mit jeder neuen
Paketdatei auflösen. Vollständige Quell-/Bestandsprüfung an klaren Phasengrenzen
wird mit gezielten Prüfungen der unmittelbar betroffenen Ziele und des Journals
zwischen atomaren Dateischritten verbunden. Das ist eine Änderung des heutigen
Vertrags, keine bloße Umbenennung von Caching.

Vor Code sind P0–P6/R0–R2, Konflikt-/Fremdänderungsmodell, Erkennungszeitpunkte,
Quellensnapshot, Sperre, Commitgrenze und Recovery in RI-C-V01 festzulegen.
Eine spätere Erkennung an einer globalen Grenze darf nicht als unveränderte
Erkennung vor jedem Dateischritt ausgegeben werden. Fremde Bytes bleiben erhalten;
Journal vor aktiver Mutation, sichere no-replace-Veröffentlichung, erforderliche
Dauerhaftigkeit, Runtime zuletzt und wiederholbare Recovery bleiben Pflicht.
Neue Journalversion nur bei nachgewiesenem Bedarf; Altverträge bleiben geschlossen.
Bis zur qualifizierten Lieferung gilt der vollständige bisherige Guardvertrag.

### RI-D07 · Timeout und tatsächlicher Abschlusszustand

Ein Abbruch bedeutet unvollständige Prüfung/Übernahme, keine fachliche Widerlegung
des Rätsels. Vor Mutation, vollständig zurückgerollt, Recovery erforderlich und
dauerhaft abgeschlossen sind getrennt zu melden. Ein nach dem belegten dauerhaften
Abschluss festgestellter Zeitablauf darf nicht pauschal als nicht integriert gelten.
Harter Prozessabbruch garantiert keine abschließende JSON-Ausgabe. Bei unklarer
oder fremder Belegung bleiben Journal/Dateien erhalten; kein scheinbarer Erfolg.
Recovery verwendet ihre eigene Grenze und kann bei erneutem Abbruch wiederholt
werden. Kein Budgetbypass und kein Entfernen eines Locks als Fehlerbehandlung.

## 3. Entwicklungspakete und Reihenfolge

| Paket | Ergebnis | Abhängigkeit / Status |
| --- | --- | --- |
| [RI-A / #478](https://github.com/venomenon328/picross/issues/478) | Budgetkonfiguration, Warnung/Fortschritt, Phasen-/I/O-Messung und gleichwertig gebündelte sichere Reads. | Über PR #484 auf `864c4e6` integriert; Abschlussentscheidung im Issue. |
| [RI-B / #479](https://github.com/venomenon328/picross/issues/479) | Bytegebundene Wiederverwendung tatsächlich geprüfter Pakete in zusammenhängender Integration. | A-Messauswertung und B-V01/B/C-Abgleich vor Code dokumentiert; beauftragte Branchlieferung, T01/CI/Review standgebunden. |
| [RI-C / #480](https://github.com/venomenon328/picross/issues/480) | Skalierende Katalogpublikation mit explizitem Kontroll- und Recoveryvertrag. | Nach A-Messauswertung/C-V01; geplante Umsetzung auf dem abgestimmten B-Kontext. |

Geplante Folge: A → Messauswertung und gemeinsamer B/C-Vertragsabgleich → B → C.
Die Auswertung entscheidet über den konkret wirksamen Optimierungsumfang.
Zeigt sie eine andere sinnvolle Reihenfolge, diese zuerst in Issues und diesem
Vertrag begründet fortschreiben; keine neue Produktanforderung daraus ableiten.
Tests, notwendige Dokumentation und getrenntes Selbstreview gehören jeweils
zur Lieferung, nicht zu einem späteren optionalen Paket. Die Paket-Issues führen
Akzeptanz, T01-/Reviewstand und konkrete Ausführungsaufträge.

## 4. Nachweise und Abnahme

Kleine feste synthetische Eingänge verwenden. Keine echten Rätsel, kopierten
Bestandskataloge, neuen rätselspezifischen Tests oder dauerhaften Replaykorpora.
Kontrollierte Uhren prüfen Warnung, Deadline und Recovery ohne minutenlange
Testwartezeiten. Die wirkliche Plattformprüfung ersetzt eine Uhrsimulation nicht.

Ein begrenzter synthetischer Messbestand wird vor/nach der jeweiligen Änderung
auf Windows und Linux verglichen; Windows umfasst einen kurzen und einen normal
verschachtelten Pfad. Gleiche Eingänge/Parameter und Umgebungsangaben sind Pflicht.
Für C getrennt Bestand bei festem Neupaket und Paketdateizahl bei festem Bestand
variieren. Messpunkte und Aufbaukosten vor Ausführung festlegen; Zähler sollen
die vermiedenen Wiederholungen neben der Wallclockverbesserung belegen.
Keine ungeprüfte Prozent-/Sekundengarantie und keine bloße Behauptung schnellerer
Integration nach höherem Timeout. Ein überschrittenes Laufzeitziel bleibt offen.

Relevante Negativ-/Unterbrechungsfälle sichern manipulierte Inputs und Staging,
fremde Quellen/Dateien, Pfadalias/Links, dauerhafte Veröffentlichung, No-op und
wiederholbare Recovery. Bestehende kleine Fälle erweitern statt eine breite neue
CI-Matrix aufzubauen. C benötigt wegen der geänderten Transaktionssemantik ein
gesondertes qualifiziertes Review vor Merge.

Die tatsächliche CI-Auswahl folgt weiter [CI2](CI_SLIMMING.md) und
[CI-Policy](CI_POLICY.md). Werkzeugänderungen erben keine `content_only`-Ausnahme;
alle tatsächlich ausgewählten Pflichtjobs müssen erfolgreich sein. Chromium nur
auf ausdrücklichen Auftrag. Performancebelege erzeugen keinen automatischen
Spiel-/Browser-/Buildauftrag und keinen zusätzlichen dauerhaften CI-Job.
Kompakte Messberichte bleiben als T01/PR-Belege gebunden, Rohprofile temporär.

## 5. Zuständige Dokumente und Übergang

[ZA-1](ZA1_ADAPTER.md) führt Paket-/Export- und Aufrufgrenzen,
[SD-Catalog](SD_CATALOG.md) den Publikations-/Recoveryvertrag,
[Kategorien](CATEGORIES.md) die Quellen-/Projektionsregeln und
[SD2-Integration](SD2_INTEGRATION.md) die Methoden-/Journalergänzungen.
Die [CLI-Anleitung](../tools/puzzle_production/README.md) dokumentiert ausschließlich
tatsächlich gelieferte Befehle. Dieser RI-Sollvertrag ersetzt nur die bei Lieferung
ausdrücklich benannten Abläufe; versiegelte Pakete und historische Belege bleiben
unverändert.

Bei den jeweiligen Implementierungslieferungen die betroffenen Verträge,
[Authoring §8](ai-workflows/PUZZLE_AUTHORING.md) und nötigenfalls dessen Offline-
Cheat-Sheet samt Regelwerksnapshot/Revision gemeinsam auf den ausführbaren Stand
fortschreiben. Diese Spezifikationslieferung verändert deren operative Aufträge
und eingebetteten Snapshot noch nicht. Es werden keine neuen Freigabeschritte für
gewöhnliche Rätselproduktion eingeführt.

INT-01 und andere konkrete Produktionsblocker werden erst durch nachgewiesene
erfolgreiche Wiederaufnahme im jeweiligen Produktionsauftrag erledigt. RI-T01
prüft das Werkzeug an synthetischen Daten und nimmt keine echten Rätsel ab.
