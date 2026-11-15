# PW-PERF-A · Produktionsaufwand und nächste Pakete

Stand 15.11.2026, Analyse zu [#653](https://github.com/venomenon328/picross/issues/653).
Basis: `6b0057100d5bdacd68878d80d5bd29e5ca4ee9a5` (main nach #654/#652).
Dies ist ein gebundener Analysebericht und eine Paketvorbereitung, keine neue
Produktionsnorm oder Freigabe zur Implementierung, Kompaktierung oder zum Merge.

## 1. Ergebnis und Beleggrenzen

Der akute v9-Dispatchfehler ist durch #652 behoben. Die normale Integration
replayt keine fremde historische Produktion mehr. Sie prüft deren Dateien aber
weiterhin vielfach: Register liest im erfolgreichen Wiederholungslauf insgesamt
6,668 GB, davon 2,075 GB aus alten Paketpfaden, und schreibt drei vollständige
Katalogprüfkopien mit zusammen 507.635.319 Bytes. Der nächste große Hebel ist
eine ausdrücklich kleinere Transaktionsabhängigkeit, nicht ein weiterer Cache.

Die Quellenroute ist bereits phasengenau. Physische Phasendateien verbessern
Abrufbarkeit und vermeiden versehentliche Volllektüre; allein durch Aufteilen
sinken die benötigten Textbytes nicht. Inhaltlich lohnt besonders die Trennung
aktueller Regeln von historischen Farb-/Lieferchronologien. Die Migration des
Bestands ist abgeschlossen. Drei absichtlich übernommene Vollpakete benötigen
einen eigenen, quellenerhaltenden Abschlussweg und zuvor korrigierte Reader.

### Gebundene Originale

| Quelle | Verwendung und Grenze |
| --- | --- |
| [Fehllauf #603](https://github.com/venomenon328/picross/pull/603#issuecomment-6886252211), [unabhängiges Review](https://github.com/venomenon328/picross/pull/603#issuecomment-6886028000) | Bestehende Fehlerursache und Messung wiederverwendet; kein neuer Negativlauf. Basis `628f88101d5bdc01cd44299eaaa2065e26bbcc03`, Produktion `e3b177673011c5477dd605c24420fef589e8f878`. |
| [RI-V9-Originale](https://github.com/venomenon328/picross/tree/ea8961cb8cd267cb2227fee647a7f835551efe8d/review/ri-v9), [Review #654](https://github.com/venomenon328/picross/pull/654#pullrequestreview-5908383815) | Erster erfolgreicher Realfall; Toolhead `4b7286461d3b074eaf6f044d45d69237d0b8b42b`. Reviewref bis 22.11.2026 00:00 UTC, gegebenenfalls früheres Reviewende. Der alte PR-Body mit offenem Review wird nicht als aktueller Status übernommen. |
| [PW3-B-T00/T01](https://github.com/venomenon328/picross/pull/649#issuecomment-6884655610) | Zwei vorhandene synthetische Fälle; kein erneuter Bild-/Solverlauf. Basis `254e7f2f82d9839933ce7f1dca0504fc362a4e1a` → `33d4f16effb475dbcedb63a9c18c8f6acb4b4190`. |
| [PW-PERF-A-Messoriginale](https://github.com/venomenon328/picross/tree/1b2a3e195846b4ab5dace9931f8a1db61283cebb/review/pw-perf-a) | Eine begrenzte positive Wiederholung, lesendes Inventar und Quellenprobe; Reviewref `review/653-pw-perf-a-until-20261122`, Ablauf 22.11.2026 00:00 UTC. Kein dauerhaftes Benchmarkkorpus. |

Die Wiederholung verwendet das vorhandene #652-Skript mit zusätzlichen rein
beobachtenden Zählern, unveränderte Werkzeuge von main und dieselbe Fliegenpilz-r07-
Quelle. Original-ZIP: 24.734.843 Bytes, SHA-256
`0ca64ae2eee8c317d7ed1d34978180f26029cb91e3276bf7201a682b444057bd`;
Approval SHA-256 `b360b8c5f3c686d8fc717887ca62a0ffbf69a89851a23698c70cab4033af426f`.
Windows 11 `10.0.26200`, Python 3.13.14, Pillow 12.3.0; E: als lokales NTFS
über `Win32_LogicalDisk` bestätigt. Ein eigener Wegwerfcheckout enthält das
Ziel und die kopierten Authoringquellen; der Benutzercheckout bleibt erhalten.
Der bestehende Checked-Beleg wird an die Definition gebunden, kein Vollsolver
über den Katalog gestartet. Registrierung, echte Completion und aktuelle
Projektionsbindung gelingen; 56 alte Einträge und deren Metadaten bleiben gleich,
923 von 925 alten Dateien unverändert, ausgenommen beide Registries.
Kein realer Inhalts-PR, kein Retirement und kein Merge wurden ausgeführt.

Frischer Prozess/Checkout bedeutet **keinen kalten Dateicache**. Quellenrestore,
Export und Plan wärmen spätere Zugriffe; der OS-Cache wurde nicht geleert.
Auch #652 liefert keinen kontrollierten Kaltcachewert. Die zusätzlichen Observer
haben ungemessenen Eigenaufwand, ersetzen aber keine Validierung. Identische
Read-/Hashzähler beider Erfolgsfälle stützen die Arbeitsmengenvergleichbarkeit.

## 2. Zeit- und Arbeitsbilanz

### 2.1 Serieller Ausschnitt von Schritt 5

Sekunden, gerundet; jede Spalte ist ein eigener Lauf. Native Operationen sind
nacheinander ausgeführt. Completion ist die Skriptklammer einschließlich ihrer
Prüfungen; sie ist kein isoliertes CPU-Profil des Projektors.

| Arbeit | Bestehender Fehllauf | Erster Erfolg #652 | Eine Wiederholung PW-PERF-A |
| --- | ---: | ---: | ---: |
| Export | 12,587 | 10,691 | 11,680 |
| Plan | 50,066 | 48,200 | 53,337 |
| Register einschließlich gegebenenfalls Recovery | 584,065, zurückgerollt | 286,655, erfolgreich | 158,366, erfolgreich |
| Completion | nicht erreicht | 8,043 | 8,487 |
| Summe dieser seriellen Klammern | 646,718 | 353,589 | 231,870 |

Die Nutzerbeobachtung von etwa 21 Minuten entspricht etwa 1.260 Sekunden.
Zum belegten Fehllaufausschnitt fehlen rechnerisch etwa 613 Sekunden. Das ist
eine **unzugeordnete Messlücke**, keine behauptete Reasoning-, CI- oder Lesezeit.
Zum zweiten berichteten Fehlschlag gibt es hier keine gleichwertige vollständige
Zeitreihe. Keine Mittelwerte über erfundene oder nicht vergleichbare Läufe.

Der neue komplette Runnerprozess dauert 259,506 s; darin liegen die 231,870 s
oben. Die restlichen 27,636 s umfassen Imports, Inventare vor/nach dem Lauf,
zusätzlichen Checkoutcheck, Rebind, Observer-/Dateiausgaben und den isolierten
Git-Testcommit, ohne feinere Zuordnung. Diese **Nachweisarbeit** gehört nicht
automatisch als Dauerpflicht in spätere Produktion. Worktreeanlage samt
Quellenrestore: separat 4,417 s; venv/Pillow-Setup separat, nicht vollständig
gestoppt. API-/Git-Netzwartezeit, Quellenlektüre, Review, Modellarbeit und
Unterbrechungen dieser Analyse wurden nicht durchgehend vermessen.

CI läuft außerhalb dieser nativen Klammern. #652 nutzt erfolgreich
[Run 43659533003](https://github.com/venomenon328/picross/actions/runs/43659533003):
189 Adaptertests plus ZA-1 und 351 Katalogtests; allein der Kataloglauf meldet
1.465,972 s. Das ist Entwicklungsabsicherung, keine Laufzeit eines neuen Rätsels.
Parallel laufende Jobs dürfen nicht zur Wartezeit addiert werden. Die vorhandene
#649-CI brauchte 196 s. Für diesen reinen Berichts-PR gilt nur der aktuelle Kern,
`modules=[]`, ohne Spielerbau; konkrete Ergebnisse stehen am Liefer-PR.

### 2.2 Registerprofil: gleiche Arbeit, unterschiedliche Laufzeit

| Größe | Fehllauf | #652-Erfolg | Wiederholung |
| --- | ---: | ---: | ---: |
| sichere Reads / Hashaufrufe | 77.031 / 49.317 | 20.377 / 14.461 | 20.377 / 14.461 |
| kumulierte Readbytes / Hashbytes | 23.061.433.143 / 22.664.674.469 | 6.667.817.833 / 5.699.031.343 | identisch zu #652 |
| Pfadprüfungen | 235.275 | 59.098 | 59.098 |
| Guards | 92 | 7 vollständig, 50 lokal | 7 vollständig, 50 lokal |
| Fremde / neue vollständige Exportreplays | alter Weg fehlerhaft | 0 / 2 | 0 / 2 |
| Publizierte Dateien / Bytes | 27 / 29.743.566, danach Rollback | 25 / 29.567.273 | identisch zu #652 |

Read- und Hashbytes sind kumulierte, teilweise überlappende Zähler. Nicht
addieren und nicht als eindeutige Datenmenge oder physische Datenträgerbytes
interpretieren. `catalog_io` deckt nicht jedes Dateisystem-I/O ab. Die längeren
Prüfpfade der Wiederholung erhöhen Pfadkomponenten/Windows-Attributchecks von
520.526 auf 561.477, ohne Änderung der Zahl logischer Pfadprüfungen.

Für die Wiederholung zerlegen **disjunkte Zeitklammern** den nativen Registerwert:
Snapshot 23,074 + Export/Proof 7,972 + Plan/Projection 41,086 + Publication 74,633
+ übrige Arbeit 11,601 = 158,366 s. Unterhalb von Publication: P0 31,484,
P1 0,046, P2 4,990, P3 6,316, P4 0,597, P5 25,700, P6 5,481 s;
Rest rund 0,019 s. Kinderzeiten nicht zusätzlich zu Eltern zählen.

Drei `_stage_check`-Klammern liegen in Plan/Projection und P0: 14,524 + 15,965
+ 14,975 = 45,464 s, **einschließlich** Validierung. Geschriebene Prüfkopien:
506/529/506 Dateien, 159.414.757/188.805.805/159.414.757 Bytes. Der separate
Planbefehl hat zusätzlich eine Stagingklammer von 15,351 s und einen Snapshot
von 23,598 s, zusammen innerhalb seiner 53,337 s. Register nutzt dessen Ergebnis
nicht als dauerhafte Autorität, sondern plant erneut.

P5 im ersten Erfolg: 171,631 s, darin Checkout 107,311 und G5b 58,863 s.
In der Wiederholung: P5 25,700, Checkout 14,865, G5b 5,418 s. Derselbe
logische Arbeitsumfang erklärt diese Differenz nicht. OS-/I/O-/Lastursache
ist nicht isoliert; keine behauptete dauerhafte Beschleunigung um 45 % durch
eine unveränderte Implementierung. Die Mengen belegen dagegen den Restaufwand.

Die zusätzlichen Registerobserver partitionieren zurückgegebene Readbytes:

| Pfadgruppe | Reads | Bytes |
| --- | ---: | ---: |
| alte Paketpfade, einschließlich Receipts | 4.618 | 2.074.932.197 |
| `game/`-Liveinhalte | 6.242 | 2.834.969.795 |
| übrige `content/`-Quellen | 6.675 | 433.583.030 |
| neues Fliegenpilzpaket | 494 | 480.963.422 |
| Werkzeug/Runtime | 1.916 | 97.292.712 |
| Eingänge/sonstige temporäre Pfade | 432 | 746.076.677 |

Diese Gruppen summieren sich exakt zu 6.667.817.833 Bytes. Die Pfadklassifikation
gilt auch für temporäre vollständige Prüfkopien; sie ist keine Messung einmalig
benötigter Nutzdaten. Zusätzlich: 10 `registry.projection`, 829 `reveal.resolve`,
1.262 `reveal.package`, 31 `verification.inventory`, 6 `verification._methods`.
Native Methodenzähler: 617 Prüfungen, davon 565 Ansichtsreuses, 12 vollständige
Validierungen und 10 Byte-Nachprüfungen. Kategorien sind nicht disjunkt.

### 2.3 Fünf Phasen und Wiederaufnahme

| Phase | Notwendige Arbeit | Technischer/organisatorischer Aufwand und Messgrenze |
| --- | --- | --- |
| 1 Abschlussbild | Kreative Bildarbeit, Stil/Transparenz und tatsächliche Wahl | Builder, Paket/Record/Projektion, Git/API-Sicherung. Keine generative Echtzeitmessung vorhanden. |
| 2 Motiv | Gewählte Vorlage, visuelle Eignung, Parameterentscheidung | Gebundene Quellen lesen, Builder/Projektor; keine neue Bildserie für diese Analyse. |
| 3 Raster | Passendes Raster, unabhängiger Proof, aktuelle Schwierigkeit; Suche nur bei Bedarf | ZIP-/Recordinspektion, Import/Analyse/Rebind. Zwei vorhandene kleine Fixtures messen technische Hüllen, keinen großen Solver oder kreative Gesamtzeit. |
| 4 Hintergrund | Kontextbilder, echte Wahl/none, nur gewählte Ableitung | Manifest, Rechte, HP-W2-Verifikation, Finalizer; historische Identitätskopplung verursacht Wiederaufnahmestopps. |
| 5 Abschluss | Gültige Endfreigabe, neue Inhalte/Zieländerungen prüfen | Export/Plan/Register, begrenzte Recovery bei Fehler, Git/CI/Review, Completion und später §9. Obige Laufzeitklammern messen nur einen Teil. |
| Wiederaufnahme | Aktuelle Phase, Zielmain, gültige Entscheidungen und verbrauchte Budgets feststellen | Unveränderte kreative/solverbezogene Arbeit wiederverwenden. Zielprüfung frisch; ältere Revisionen nur bei tatsächlich betroffener Bindung oder expliziter Diagnose öffnen. |

#649 reduziert nachweislich technische Arbeit, aber nicht alle Zeiten:

| Operation | Mono/none vorher → nachher (s) | Farbe/selected vorher → nachher (s) | Belegter Arbeitsrückgang |
| --- | ---: | ---: | --- |
| Builder | 9,189 → 9,302 | 8,823 → 8,359 | ZIP-Öffnungen 28 → 9, Recordreads 7 → 6 |
| Automatic | 0,381 → 0,177 | 0,314 → 0,182 | ZIP 8 → 1, Recordreads 2 → 1 |
| Finalizer | 7,919 → 6,998 | 9,602 → 8,892 | ZIP 26 → 6, Recordreads 5 → 3; Projektorinspektionen bleiben 2 |
| Export | 6,647 → 6,149 | 9,524 → 8,818 | I/O unverändert; 3 Inspektionen/ZIP-Öffnungen |
| Offline verify | 2,013 → 1,957 | 2,976 → 2,692 | I/O unverändert; 1 Inspektion/ZIP-Öffnung |

Fixtures: 3×3, einmal kopierte gleiche Eingänge, warmer OS-Zustand nach Kopie,
Setup außerhalb der Timer, `tracemalloc` statt RSS. Nachher-Export: 287 Reads /
622.374 Bytes mono, 334 / 1.465.852 farbig; Dekodierungen 12/18. Offline: 102 /
232.790 beziehungsweise 120 / 570.180; Dekodierungen 4/6. Plan/Register waren
nicht Gegenstand von #649. Die vom Eigentümer noch nicht praktisch geprüften
anderen Phasen gelten deshalb weder pauschal als schnell noch als gescheitert.

## 3. Quellen- und Dateikarte

### 3.1 Gemessene Route statt pauschaler Handbuchlektüre

Die temporäre `source_map.py`-Probe liest je Phase jede benötigte Datei einmal,
vereinigt exakte Überschriftenbereiche und zählt UTF-8-Bytes mit Original-LF.
Alle Zeilenbereiche/Hashes stehen im Messoriginal `source-map.json`.
Gemeinsam: AGENTS-Produktionsabschnitt (1.270 Bytes), vollständiger Bildstil
(7.041 Bytes) und Authoring §1. A = Authoring, Q = Qualität, AT = Transparenz,
HG = Hintergrundvertrag. Die Zahlen enthalten Veröffentlichung §§6.1–6.2/7.

| Phase | Zusätzliche ausgewählte Abschnitte | Dateien/Abrufe | Ausgewählte Textbytes | Tatsächlich lokal gelesene ganze Dateibytes |
| --- | --- | ---: | ---: | ---: |
| 1 | A §2, §§6.1–6.2/7; Q §2/3.1; AT §2 | 5 | 35.494 | 165.594 |
| 2 | A §2, §§6.1–6.2/7; Q §2/3.2, H-03/H-04 | 4 | 33.552 | 129.530 |
| 3 mono | A §4/5.2, §§6.1–6.2/7; Q §§2–4 | 4 | 56.378 | 129.530 |
| 4 vor Ableitung | A §§6.1–6.3/7; Q §2/9.1; HG §3 | 5 | 46.592 | 313.417 |
| 5 Basiseinstieg | A §§6–9 | 3 | 35.761 | 73.969 |

Bedingte Zusatzlektüre: Farbe Q §8 +22.035 Bytes (Phase 3 somit 78.413), fehlender
Kandidat Q §5 +2.600, redaktionelle Ausnahme Q §6 +2.407. **Die Tabelle ist keine
vollständige Operationslektüre:** Paketbau benötigt PW-B und Tool-README PW-B/PB-A;
Rasterimport RP-3 und Produktion §§4–5; Paarprofil PAIRED_LINES nur bei Verwendung;
Korrektur FIXED_RASTER/RP-5 nur bei Verwendung; Difficulty/Rebind SD2_INTEGRATION
und passende CLI-Abschnitte; Ableitung HG §4/HP-W2; Export/Plan/Register/Recovery
RI, generationsbezogenes ZA-1 und CLI; Retirement §9 und seinen Zielvertrag.
Die §8-Zielprüfung umfasst auch die dort gerouteten PE-A2-Regeln. Kategorien,
Arbeitsindex, Runtime und konkret gebundene Eingangsrecords kommen als Daten hinzu.
Diese bedarfsabhängigen Quellen dürfen weder pauschal weggelassen noch für jede
frühe Phase vollständig geladen werden. Der Entwicklungsauftrag hier hat
zusätzlich seine eigenen vollständigen Pflichtquellen.

Die Probe hat innerhalb einer Phase 0 Wiederholungsreads und 0 abgeschnittene
lokale Reads. Zwischen fünf unabhängigen Phasen wird der gemeinsame Kern fünfmal
gelesen; es wird kein dauerhaft vorhandener Modellkontext angenommen. Ganze
Dateibytes sind Dateisystemarbeit des Helpers, ausgewählte Bytes dessen berechnete
Abschnittsausgabe, **keine gemessenen Modelltokens**. Historische Tool-/Tokenlogs
der 21-Minuten-Aufträge sind nicht zugänglich. Auch die Analyse selbst hatte
abgeschnittene lange Toolantworten und gezielte Nachlektüre; dafür liegt kein
lückenloser Zähler vor. Diese Grenze wird nicht durch angebliche Nullkosten der
lokalen Probe verdeckt. #649 misst nur Promptbytes 386/521/528/536/617 für Schritt
1–5; das ist nicht der geladene Quellenkontext.

### 3.2 Entscheidung über die physische Struktur

Aktuell: Authoring 60.305 Bytes in einer Datei, historischer
`PUZZLE_AUTHORING_0_7_0_PREVIEW.md` 157.957 Bytes, HTML-Verweissheet 904 Bytes.
Der Root-README hat nur 3.488 Bytes und ist kein wesentlicher Kostentreiber.
Große Referenzen: PW 56.306, Qualität 55.561, Hintergrund 183.887, Tool-README
171.186 Bytes. Größe bedeutet keine pauschale Pflichtlektüre. ZA-1 ist ein
technischer Generationenvertrag; PW/README mischen aktuelle Schnittstellen mit
historischen Erweiterungen. Entwicklung braucht andere Teile als Produktion.

**Empfehlung:** ein kurzer gemeinsamer Authoringkern plus fünf aktuelle
Phasendateien mit jeweils kanonischem Phaseninhalt. Gemeinsame Befugnisse,
Sicherung/Freigaben nur einmal definieren; keine konkurrierende Kurzregelkopie.
Technische Quellen bleiben separat und werden durch konkrete Operationen geroutet.
Physischer Split allein: 0 eingesparte ausgewählte Regelbytes. Ein belegter
inhaltlicher Kandidat sind Q §8.2–8.3 mit 10.820 Bytes historischer Farbchronologie:
aus routinemäßiger Farblektüre herauslösen, operative Regeln §8.4–8.5 erhalten.
Das entspricht zunächst 78.413 → höchstens 67.593 Bytes für den obigen Farbpfad,
bevor neue Routerbytes gegengerechnet werden. Keine Token-/Zeitersparnis zusagen.

Gemeinsam zu ändern: AGENTS, Authoringrouter, tatsächliche Promptrouter,
PW-B-Builder-/Snapshotbindungen und lokale Links. Statische Fundstellen für
Dateinamenbindungen: `batch_operations.py`, `batch_runner.py` und
`integration_batch_operations.py`; aktive Builder-/Requestgeneration zusätzlich
am tatsächlichen Paket prüfen, nicht nur diese drei historischen Consumer ändern.
Alte ZIP-/Freigabe-/Snapshotbytes und darin gebundene Pfade bleiben unverändert.
Historische Reader behalten ihre genaue Quellenversion; neue Snapshots binden
die neue kanonische Dateimenge ausdrücklich.

Aktuelle Normtexte bleiben Autorität; Lieferberichte werden über
DEVELOPMENT_ARCHIVE bei konkreter Herkunftsfrage gesucht. Native Mess-JSONs und
Runner liegen befristet im Reviewref, der Bericht enthält nur entscheidende
Aggregate. Keine Kopie derselben ZIPs, Screenshots oder vollständigen JSONs in
Bericht, Issue und PR. Bei langen Diskussionen zuerst aktuelle Entscheidung und
konkretes Revieworiginal lesen; ältere widersprochene Paketpläne bleiben Historie.

## 4. Prüfungsnutzen und bewusste Vertragsänderung

Aufrufstellen beziehen sich auf die oben gebundene main-Basis, überwiegend
`tools/puzzle_production/`. Kosten sind inklusive, soweit nicht ausdrücklich
als disjunkte Zähler markiert; Tabelle nicht als additive Zeitrechnung benutzen.

| Prüfung/Aufrufstelle | Risiko und tatsächliche Eingänge/Ziele | Häufigkeit/Kosten im Register | Entscheidung für Folgepaket |
| --- | --- | --- | --- |
| `catalog_transaction.capture` | Konsistenter Registry-/Runtime-/Quellenstand, Fremdänderungen; bisher alle T/K und Namespaces | 1 Capture, 23,074 s; liest/hashprüft Quellen vor und nach Checkoutcheck | **zielbezogen machen**: gemeinsame Indizes und deklarierte neue Abhängigkeiten; keine unbeteiligten Archive/Livebilder. |
| `_stage_check` aus Prepare/Journalprüfung | Alt-/Zielansicht semantisch gültig | 3 Kopien, 507,6 MB geschrieben, 45,464 s; Plan extra 1 | **entfernen** als vollständige Dateikopie; neue Zielprojektion aus validierten Indizes plus einzigem Paket prüfen. Kein gleich großer RAM-/Hintergrundscan. |
| `content_registry.check_checkout/projection/_check_entry`, `reveal.resolve/package`, `integrated_content.check` | Aktuelle Entry-/Source-/Assetbindungen; heute mehrfach je altem Eintrag | 5 Checkoutchecks, 10 Projektionen, 829 Resolve/1.262 Package | **zusammenlegen und zielbezogen machen**; reine globale ID/Slot/Pfad-Kollisionen behalten, einzelne alte Dateien nur auf tatsächlicher Abhängigkeit. |
| `registration_publication.Guards.full`, Journalvalidierung | Fremdänderungen, Lock-/Ziel-/Namespacekonsistenz | 5 Grenzen G0/G2/G5a/G5b/G6 + 2 Journalvalidierungen; 50 lokale Zielguards | **Grenzen behalten, Quellenmenge ändern**; per-Datei-Vollguards sind durch #652 bereits weg. Lokale frische Ziel-/Eltern-/Lock-/Tempprüfung bleibt. |
| Recovery GR0/GR2 und R1 | Ausschließlich eigene Änderungen rollbacken; wiederholbarer Abbruch, fremde Bytes schützen | Im Erfolg nicht ausgeführt; bestehende #652-Recoverytests wiederverwendet | **behalten, für neue Generation zielbezogen machen**; alte Journalbytes/Reader unverändert. Kein neuer echter Fehllauf. |
| `registration_verification.inventory/_sources/_methods` | Neue Eingänge, unabhängiges Staging und echte Methodenbytes gegen Austausch schützen | 31 Inventare, 6 gesamte Methodeninventare; P3/P5 zwei Byte-Readbacks | **zusammenlegen/zielbezogen**: aktuelle Eingangs-/Staging-/Zielbeweise behalten; pro Addition nur betroffene Datei/Eltern frisch, gesamte Inventare an expliziten Grenzen. |
| `catalog_io.safe`, Method freeze/binding | Link-/Alias-/Pfadwechsel, falsche Implementierung | 59.098 Pfadprüfungen, 561.477 Komponenten; 617 Methodenprüfungen mit Reuses | **behalten für konsumierte/geschriebene Pfade**, durch kleineres Abhängigkeitsset reduzieren; kein mtime-Vertrauen, keine lockübergreifende Cacheautorität. |
| Adapter Original/Staging/Export/Offline | Neue Produktion, unabhängiger Proof, Transport und freigegebene Bytes | Register 2 volle Replays + 2 Byte-Readbacks; Export 3 volle Inspektionen | **Registergrenzen behalten**, redundante Exportinspektion **zusammenlegen**; explizite Offlineprüfung bleibt frisch. |
| Builder/Finalizer, ZIP/Bilddekodierung | Gebundene Angebote, tatsächliche Bild-/Raster-/Freigabequalität | #649 reduziert ZIPs; Finalizer weiter 2 Projektorinspektionen, Export 3 | **zusammenlegen** innerhalb eines Aufrufs; neue/materiell geänderte Inhalte weiterhin vollständig prüfen, keine persistenten Erfolgsstempel. |
| HP-W2-Toolidentität (`background_assets`) | Ableitung unter behauptetem Bildalgorithmus/Codec | Neun Module einschließlich Diagnose/I/O; Änderung an `operation_diagnostics.py` stoppte #620 | **zielbezogen versionieren** für neue Belege; pixelwirksame Implementierung/Profil/Codecs streng binden. Keine globale Alt-Hashfreigabe. |
| Abschlussreview älterer Revisionen | Herkunft/Manipulation nur soweit konkrete Bindung betroffen | #603 prüfte zusätzlich 7 ZIPs/803 Inventarhashes; kein separater Zeitwert | **nur explizite Diagnose** für unveränderte ältere Produktion; aktuelle Endfreigabe, neues Paket, tatsächlicher Diff und abhängige Quellen bleiben Reviewumfang. |

Der heutige Vertrag in SD_CATALOG RI-B/RI-C/HP-I1b1/RI-V9 bindet sämtliche alten
T/K-Bytes und die vollständigen Namespaces. Das lässt sich nicht durch einen
`skip_checks`-Parameter ehrlich abschaffen. Der vorgeschlagene neue Vertrag
garantiert bei einer Neuregistrierung die gültige gemeinsame Indexprojektion,
vollständig gültige neue Inhalte, unveränderte tatsächlich gelesene Quellen und
geschützte Schreibziele. Er **garantiert nicht mehr**, währenddessen jede
unbeteiligte alte Datei auf Existenz, Byteintegrität und semantische Gültigkeit
geprüft zu haben. Beschädigung dort kann erst beim gezielten Reader oder
ausdrücklich beauftragten Gesamtaudit auffallen. Fremde Daten werden trotzdem
nicht überschrieben oder gelöscht. Die fehlende ABA-/OS-Transaktionsgarantie
gegen nicht kooperierende Schreiber bleibt ausdrücklich bestehen.

Für diese Garantieänderung eine neue geschlossene Registrierungsgeneration
vorsehen; alte Journale einschließlich Recovery nicht umdeuten. Zuständige Normen:
RI, SD_CATALOG, ZA1, betroffene Hintergrund-/Reveal-/PW-B-Abschnitte und CLI.
PE §13 dient als Vergleich für aktuelle Quellenbindungen, nicht als ungeprüfte
Übernahme des Editorverfahrens. Kein Startscan, Leerlaufscanner, Pflichtcache,
Merklebaum, Auditdienst oder neue Datenbank als Ersatz für entfallene Arbeit.

## 5. Bestandsabschluss und Readerreste

Lesende Inventur aus `git ls-tree -rlz`, Registry, Manifesten und Source-JSONs;
keine ZIP-Dekodierung oder Solver-/Bildprüfung. Der Gitvergleich von M2
`e1e8caf91d9ad1e6661807e09020c338ad6b6d29` bis zur Analysebasis enthält keine
Änderung unter `content/` oder `game/`.
[Abschluss #641](https://github.com/venomenon328/picross/issues/641#issuecomment-6882405744):
M1 Runtime v8 und M2 mit 56 Reveal-v4-/56 Hintergrund-v6-Quellen sind erledigt.
Die persönliche Editorabnahme #576 und alte lokale Bereinigungsreste sind keine
fehlende Repositorymigration.

| Rest | Zustand, Herkunft und aktive Abhängigkeit | Disposition |
| --- | --- | --- |
| 56 aktive Entries | Registry v4 / Runtime v8, Reveal v4 / Hintergrund v6; 53 aktive kompakte Receipts + 3 Vollpakete | **bewusst erhalten**, keine erneute allgemeine Migration |
| `pz-birne/r05` | 15 Dateien, 16.107.114 Bytes, davon ZIP 13.420.146; Ursprung #595 `2916e94c2d2eeaf8d5ce6ebd15346fe22a20a8d8` | **Readerkorrektur nötig**, danach separat kompaktieren |
| `pz-erdbeere/r06` | 15 Dateien, 21.714.958 Bytes, davon ZIP 18.871.091; #587 `f96583bdddcdc8df2c630fe480857a6e4da1a9f7` | **Readerkorrektur nötig**, danach separat kompaktieren |
| `pz-zitrone/r05` | 15 Dateien, 17.355.973 Bytes, davon ZIP 14.739.356; #593 `b8d797dbb7d4b30c10476e3b8b68ab60780b3d22` | **Readerkorrektur nötig**, danach separat kompaktieren |
| Zwei inaktive kleine Receipts | `pz-8ecddf77e80c4543bf4ec714fe3d/r05` 2.174 Bytes, aktiv r09; `pz-d829eb9b83e94f9c9357ee5ab9c9e359/r05` 2.807 Bytes, aktiv r06 | **bewusst erhalten**; keine großen Archive, kein pauschaler Löschauftrag |
| Main-Authoring Senf | `pz-4ec5ac61e2c447bd98c8508a993cbd32`, r01–r03; r03 `content_ready`, Endfreigabe/Integration null; ZIPs zusammen 19.536.201 Bytes | **bewusst erhalten**; offene Arbeit, nicht abgeschlossene Produktion |
| Main-Authoring Level 1-1 | `pz-cc522b3f66bc4d6eafe1f8a387d18d1f/r01`, `blocked`, Integration null, ZIP 26.578 Bytes | **bewusst erhalten**; kein Retirementbeleg |

Insgesamt 58 Paketmanifeste: 55 kompakte und 3 volle. Die drei v6-Vollpakete
umfassen 55.178.045 Bytes, davon 47.030.593 ZIPbytes. Das ist ein Bruttobestand,
keine zugesagte Nettoersparnis: notwendige Nutzungsbelege/Receipts bleiben.
Ihre Liveassets, Definitionen, Kategorie/Difficulty, Registrypaketanker und
aktuelle Reveal-/Hintergrundbindungen sind aktiv und dürfen nicht verschwinden.

[PR #622](https://github.com/venomenon328/picross/pull/622) folgt der
[ausdrücklichen Dreifachübernahme](https://github.com/venomenon328/picross/issues/620#issuecomment-6838085340):
historische registrierte Bytes übernommen, keine neue Approval/Completion
erfunden. Die ursprünglichen Arbeitsrevisionen bleiben an den Quellcommits;
sie wurden nicht als aktive Mainarbeit dupliziert. Frische `ls-remote`-Prüfung
der drei `content/pw/pz-*`-Branches ergibt weiterhin genau die oben genannten
Heads; die dortigen Indizes enden bei r05/r06/r05. Keine neuere offene Revision
derselben IDs in den geprüften Remotequellen. Unveröffentlichte Nutzerdaten sind
nicht untersucht; vor späterem Abschluss aktuellen Stand erneut prüfen.

Statische Readerlücke: `integrated_content.retire` erkennt Editorhintergrund nur
bei `picross-catalog-background-v5`. Für aktuelles v6 fällt es in
`receipt_binding → origin_hash → initial(source)["origin"]`; v6 hat kein initial.
Ein blindes Retirement ist damit nicht begründet. **Kein Retirement ausgeführt,
kein beobachteter Laufzeitfehler behauptet.** Weitere Generationenstellen im
gleichen Consumer: Editorreveal nur v3 statt auch v4, Editorraster nur v1 statt
auch v2. Sie müssen im kleinen Readerpaket zusammen geprüft werden.

Zulässiger späterer Weg: geschlossener technischer Kompaktbeleg, der aktuelle
Registry-/`binding/current`-/Assetbindungen und tatsächliche historische
Nutzungs-/Herkunftsbelege erhält; bei den drei Sonderimporten #622 als wirklichen
Integrationsbeleg nennen. Keine erfundene Completion, kein rekonstruierter Origin,
keine Rückstufung v6 und keine globale Freigabe alter Toolhashes. Wenn ein konkret
benötigter Rechtebeleg nicht aus dem erhaltenen Ursprung zugeordnet werden kann,
bleibt genau dieses Paket stehen. Erst nach Readerabnahme separater Datenauftrag.

## 6. Vier vorbereitete Umsetzungspakete

Die folgenden Schnitte sind **Vorschläge zur gesonderten Beauftragung**. Budgets
vor Implementierung in die jeweilige Paketentscheidung übernehmen oder begründet
ändern. Keine pauschale Unter-zwei-Minuten-Zusage. Zeitziele dienen einer
vergleichbaren lokalen Vorher/Nachherprobe, nicht einem harten CI-Timeout.
Ein erster und ein begrenzter warmer Vergleich genügen; keine Messserie bis zum
gewünschten Ergebnis. Änderungen an Inputs/Umgebung separat ausweisen.

### PW-PERF-B · Registrierung auf ihre Abhängigkeiten begrenzen (Priorität 1)

- **Scope:** neue geschlossene Registrierungsgeneration mit expliziter
  Abhängigkeitsmenge; Capture/Projection/Stagecheck/Journal/Guards/Recovery
  konsistent ändern. Günstige gemeinsame Indizes auf IDs, Slots, Metadaten,
  Referenzen und Pfadkollisionen prüfen; alte Entrybytes unverändert übernehmen.
  Neue Produktion zweimal vollständig (Eingang/unabhängiges Staging), P3/P5
  bytegebunden nachprüfen. Keine Änderung anderer Writer oder alter Recovery.
- **Vertragsentscheidung:** die in §4 beschriebene Vollbestandszusage aufgeben,
  neue Garantie und Erkennungszeitpunkte vor Code in RI/SD_CATALOG/ZA1 festlegen.
  Komplettaudit bleibt ausdrücklich aufrufbar, kein versteckter Ersatzscan.
- **Arbeitsbudget gleicher Fliegenpilz-/56er-Bestand:** 0 Reads/Hashes/Decodes
  unbeteiligter alter Paket-/Liveassetdateien, 0 vollständige Katalogprüfkopien;
  Register höchstens 4.592.885.636 catalog_io-Readbytes und 15.759 Reads
  (heutiger Wert minus allein die gemessene alte Paketgruppe). Das ist eine
  konservative Obergrenze, kein Ziel, den verbleibenden Spielraum auszuschöpfen.
  Weiterhin 2 neue Vollreplays, 2 Zielreadbacks und 5 benannte Publikationsgrenzen;
  lokale Guards proportional zu tatsächlichen Schreibzielen.
- **Zeitbudget:** Register höchstens 136 s, Plan höchstens 46 s im vergleichbaren
  warmen Referenzlauf. Herleitung: 158,366 minus halbe bisherige Stagingklammer
  45,464; 53,337 minus halbe Planstagingklammer 15,351, aufgerundet. Die andere
  Hälfte reserviert neue gezielte Prüfkosten. Kein Versprechen aus dem langsamen
  P5-Ausreißer; bei Verfehlung Restaufwand erklären und Paketentscheidung prüfen.
- **Abnahme/CI:** kleine synthetische Zähltests mit zusätzlichem unbeteiligtem
  Archiv/Asset müssen 0 Zusatz-Dateireads ergeben; Kollision, neue Paketmanipulation,
  Ziel-/Lock-/Tempänderung, Abbruch und wiederholte Recovery bleiben wirksam.
  Betroffene Module `production.catalog`, `production.adapter`, aktueller Kern
  samt Windowsbau. Realfall nur temporärer Vergleich, kein Dauertest. Unabhängig
  von Obstkompaktierung umsetzbar; gerade voller Bestand muss funktionieren.

### PW-PERF-C · Neue Eingänge einmal je Vertrauensgrenze prüfen (Priorität 2)

- **Scope:** Export-/Finalizerinspektionen innerhalb eines Aufrufs zusammenführen;
  Inspektionsergebnis nur für exakt unveränderte Inputs und denselben Aufruf.
  Ausgabe frisch an die geprüften Eingangsdaten binden, Offlineverify separat
  vollständig lassen. Neue HP-W2-Beleggeneration bindet bildwirksame Module,
  Profil/Codecs/Parameter; Diagnoseänderungen erhalten keine Bildautorität.
  Historische Belege bleiben strikt lesbar oder ehrlich inkompatibel, unverändert.
- **Budgets zwei vorhandener 3×3-Szenarien:** Export höchstens 2 statt 3 volle
  Inspektionen/ZIP-Öffnungen, höchstens 8/12 statt 12/18 Dekodierungen (mono/farbig).
  Finalizer höchstens 1 statt 2 Projektorinspektionen, höchstens heutige 6 ZIPs
  und 3 Recordreads. Exportreads/Bytes höchstens 287/622.374 mono bzw.
  334/1.465.852 farbig, Offline weiterhin 1 frische Inspektion. Zeit höchstens
  identischer frisch gemessener Vorherwert mit derselben Instrumentierung;
  historische 6,149/8,818 s Export und 6,998/8,892 s Finalizer sind Orientierung,
  kein hardwareunabhängiger Grenzwert. Weniger Arbeit ist zusätzlich zwingend.
- **Abnahme/Verträge:** PW-B, ZA1, HP-W2 und Toolidentitätsvertrag vorher präzisieren.
  Manipulierte Original-/Ausgangsbytes und echte Pixel-/Codec-/Profiländerung
  müssen sperren; reine Diagnoseänderung darf bei neuen Belegen keine erneute
  Bilderzeugung erzwingen. Alte Hashes nicht global erlauben. Synthetische
  Tests, `tools`, `production.adapter`, `production.images`, Kern/Windowsbau;
  Katalogmodul nur bei tatsächlichem Eingriff in dessen Consumer. Keine neue
  historische Wiederholungsserie und kein allgemeiner Freigabestempel.

### PW-PERF-D · Kanonischer Kern und fünf Phasendateien (parallel unabhängig)

- **Scope:** §3.2 umsetzen; aktuelle Regeln verschieben, gemeinsame Norm einmal,
  Historie getrennt; AGENTS, Router, Links und neue Snapshotgeneration konsistent.
  Bestehende versiegelte Paket-/Freigabebytes nicht anfassen.
- **Budgets:** Kern plus jeweilige Phasendatei ersetzen den langen Authoringabruf.
  Bei demselben Abschnittsscope ausgewählte Gesamttextbytes für Phasen 1/2/3-mono/
  4/5 höchstens 35.494/33.552/56.378/46.592/35.761 einschließlich neuer Routertexte;
  Farbpfad höchstens 67.593. Bedingte technische Verträge separat zählen und
  weiterhin vollständig dort laden, wo nötig. 0 historische Snapshot-/Liefertexte
  in Routinephasen, 0 abgeschnittene Antworten/ungeplante Wiederholungsabrufe bei
  der fünfphasigen Abrufprobe. Physischer Split darf einen zusätzlichen Abruf
  brauchen; das ist kein Scheitern, wenn Kontext vollständig und kleiner ist.
- **Zeit/Abnahme:** kein Produktionslaufzeitversprechen; fünf Quellenabrufe im
  selben Zugriffskanal dürfen zusammen nicht länger als der gebundene Vorherlauf
  brauchen, API-Wartezeit getrennt ausweisen. Regelabdeckung Satz für Satz,
  Arbeits-/Sicherungs-/Freigabe- und Operationsrouting erhalten. Reine Dokumente:
  Kern, `modules=[]`, kein Spielerbau. Falls neue Builder-/Snapshotconsumer nötig
  sind, tatsächlichen Codeumfang mit `tools`/`production.adapter` und Kernbau
  auswählen; keine versteckte Normänderung allein durch defekte Snapshotpfade.

### PW-PERF-E · Schlanke Retirementreader, danach separater Datenauftrag

- **Werkzeugteil:** `integrated_content` mit aktuellen Hintergrund-v6-/Reveal-v4-/
  Editorraster-v2-Formen und technischen Kompaktbelegen schließen; aktuelle
  Bindungen statt erfundenem initial erhalten. Unterstützte alte Formen behalten.
  Sonderimport #622 als eigene belegte Abschlussherkunft unterstützen. §9,
  Hintergrund-/Reveal-/PE-/Receiptvertrag konsistent; neue Form zuerst festlegen.
- **Budget:** nur ausgewählte ID und ihre aktiven Abhängigkeiten; 0 Reads/Hashes
  unbeteiligter Paket-/Bilddateien, 0 Solver-/Produktionsreplays, 0 neue kreative
  Freigaben. Ist ein Kopiernachweis für ein zu entfernendes Original erforderlich,
  höchstens ein vollständiger Read je Quelldatei, keine ZIP-Dekodierung ohne
  konkret daraus benötigten Rechtebeleg. Kleine synthetische Referenzfälle
  dürfen gegenüber der gültigen alten Retirementform keinen größeren
  Eingangsbyteumfang lesen; Zeit höchstens deren frischer Vorherwert bei gleichem
  Byteumfang. Für aktuell scheiternde v6-Form keine erfundene Erfolgsbaseline.
- **Abnahme/CI:** v6 selected/none/standard, Reveal v4, Raster v2, historische
  Form, fehlender Rechtebeleg, neuere offene Revision und identische Wiederholung.
  Aktive Registry-/Livebytes bleiben gleich; höchstens gewählte Paket-/Receipt-/
  Arbeitsindexdeltas. `production.catalog`, bei Exportconsumeränderung zusätzlich
  `production.adapter`, Kern/Windowsbau. Keine reale Bereinigung im Werkzeug-PR.
- **Späterer Datenteil nur nach gesondertem Auftrag:** genau drei Obstpakete,
  frische Quellen-/offene-Arbeit-Prüfung, benötigte Nutzungsbelege behalten,
  Brutto-/Nettobytes aus konkretem Diff berichten. Kein Ziel, alle 55.178.045 Bytes
  blind zu löschen. Reiner Daten-PR mit Kern und `modules=[]`, ohne Spielerbau;
  main-Authoringreste und persönliche Editorabnahme bleiben getrennt.

## 7. Abschluss dieses Pakets

PW-PERF-A liefert Analyse und vier überprüfbare Folgeschnitte. #652 und #649
werden als vorhandene Nachweise wiederverwendet; neu hinzu kommen genau eine
isolierte positive Wiederholung und kleine lesende Quellen-/Bestandsproben.
Produktcode, echte Katalogdaten, Produktionsfreigaben und zentrale Entwicklungsregeln
werden nicht geändert. Revieworiginale bleiben befristet erreichbar; nach Ende
des Reviewzwecks kann der eigene Reviewref entfernt werden, dieser Bericht bleibt.
Das Gesamtissue #653 bleibt offen. Nächster Schritt ist Review dieser Analyse und
Auswahl eines Folgeschnitts, vorzugsweise PW-PERF-B; erst danach gesonderte Umsetzung.
