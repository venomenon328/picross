# PE-PERF1 · aktuelle Revieworiginale zu #636

Produkt-Head: `120ed61824d2184cc59425deeac7def9e7aa3cd0`; Basis:
`67df294e164d5732586a4e93b5b31628fffe5998`; geprüfter Test-Merge:
`85e28b43c61f89e0afa71d0795012cc30ea85b04`.
Maßgeblich sind [Issue #636](https://github.com/venomenon328/picross/issues/636)
und die [Erweiterung K08/K09/T04](https://github.com/venomenon328/picross/issues/636#issuecomment-6861975778).
Dieser Belegref gehört zu Draft-PR #637 und hat keinen Merge-PR nach main.

Umsetzung und technische Beleglieferung sind von der Abnahme getrennt.
PE-PERF1-A01 bleibt vor Merge offen, PE-B-U01 in #576 vor Release.
Insbesondere muss A01 die unten ausdrücklich genannten Zielabweichungen und
den kombinierten nativen/headless Windows-Nachweis beurteilen. Kein Merge und
keine Aussage einer persönlichen Eigentümerabnahme.

Die Datenkopien stammen ausschließlich aus `git archive` von
`4e5bfe489851fe4a4b771fcdf125fd89ce440a98`: 56 reale versionierte Rätsel,
v4/Runtime-v7, separat vom Programmcheckout. Sie enthalten keine Nutzersaves.
Testgeometrie, Eingangsdateien, Pläne, Katalogkopien und private Sitzungstoken
werden hier nicht als Datenarchive veröffentlicht. Die Skripte verwenden nur
eigene benannte Arbeitsordner; die gewählte Datenwurzel ist niemals Importpfad.

| Direkte Fachoperation, gleicher Windows-Rechner/Datenträger | Altstand | Korrigierter Stand |
| --- | ---: | ---: |
| Kleines Mono-Detail, Erstaufruf / Wiederholung | 228,143 / 216,934 s | 41,426 / 5,379 s |
| Großes Farbdetail, Erstaufruf / Wiederholung | UI: 201,983 / 209,617 s | direkt: 5,214 / 4,904 s |
| Migration-Plan, Erstaufruf / Wiederholung | 233,564 / 227,227 s | 31,962 / 33,484 s |
| Migration-Apply | Fehler nach 300,010 s | Erfolg nach 65,750 s |
| Migration-Apply No-op | nicht vorgetäuscht | 14,346 s |
| A1 Metadaten-Plan, Erstaufruf / Wiederholung | 226,814 / 236,666 s | 37,723 / 40,802 s |
| A1 Metadaten-Apply | 278,513 s | 58,337 s |
| A2 Plan, Erstaufruf / Wiederholung | zusätzlicher Vergleich in save-comparison.json | 41,564 / 40,346 s |
| A2 Apply / No-op | zusätzlicher Vergleich in save-comparison.json | 113,367 / 38,557 s |
| A3 Plan, Erstaufruf / Wiederholung | zusätzlicher Vergleich in save-comparison.json | 71,277 / 72,051 s |
| A3 Apply / No-op | zusätzlicher Vergleich in save-comparison.json | 188,994 / 96,668 s |
| Gewähltes Detail nach echter Rasterrevision | — | 6,422 s |
| Kategorien-Anlage Plan / Apply, 56 Einträge | — | 29,897 / 43,573 s |
| Kategoriezuordnung Plan / Apply, 56 Einträge | — | 29,374 / 42,305 s |
| Belegte Kategorie löschen + Reassign, Plan / Apply | — | 29,597 / 44,283 s |

Die große Alt-Detailzahl ist ein tatsächlicher Browserlauf, kein direkter API-Lauf.
`legacy-detail-ui.json` führt genau dessen zwei abgeschlossene Detailaktionen,
keinen anschließend behaupteten vollständigen Ablauf.
Die Tabelle mischt diese Schichten ausdrücklich nicht zu einem exakten Quotienten.
`performance.json` enthält CPU, inklusive Phasen, Zähler, vollständige Ziel-
Hash-/Byte-/mtimeänderungen sowie einen weiteren Erstzugriff von 63,528 s bei
6,844 s CPU. Wiederholungen werden nicht als universelles Kaltstartversprechen
ausgegeben. OS-Caches wurden nicht gespült; die unabhängigen Vorinventare lesen
die Inhaltsbytes bereits. Hintergrundlast/PC-Nutzung war nicht kontrolliert.
Beim 41,426-s-Erstzugriff entfielen 6,031 s auf Prozess-CPU; der große übrige
Zeitanteil liegt in der Quellen-/Namespaceaufnahme. Sein konkreter Anteil aus
I/O, Scheduling oder sonstiger Systemwartezeit wurde nicht isoliert.

Das Ziel einstelliger normaler Detailzeiten wird in den Wiederholungen erreicht;
ein frischer Kopie-Erstzugriff und insbesondere A2/A3-Apply bleiben darüber.
Auch 58–113 s für normale Metadaten-/Bildübernahme liegen über dem Ziel weniger
Zehnersekunden. A3 verwendet hier eine kleine eigene 3×2-Testgeometrie; seine
188,994 s dürfen daher nicht pauschal mit einem großen Motivproof erklärt werden.
Die Phasen zeigen die weiterhin frischen Gesamtquellen-, Staging-, Unter-Lock-
und Fremdbyteprüfungen für 56 Einträge und 18 tatsächlich geänderte Dateien.
Kein Budget wurde erhöht oder für die Messung abgeschaltet. Diese Zielabweichung
ist eine ausdrücklich offene Vor-Merge-Beurteilung für A01.

Der ursprüngliche Fehler hat zwei tatsächlich beobachtete Verläufe. Im mit
voller I/O-Diagnose instrumentierten direkten Alt-Aufruf erschöpft Apply nach
300 s sein Budget in der wiederholten Journal-/Guardprüfung noch vor erster
Mutation: Bytes und mtimes unverändert, v7, kein Journal. Der unveränderte
Alt-UI-Worker läuft weiter bis zu einer anderen Grenze: insgesamt 436,287 s,
Fehler `resource_limit: catalog time budget exhausted`, danach v7 und kein
Journal/Staging. Die Runtime-Bytes sind vollständig zurückgerollt, ihre mtime
hat sich geändert. Alle 1625 ursprünglichen Archivdateien wurden danach
unabhängig bytegleich gelesen. Die Quelle des Budgets ist derselbe bestehende
300-s-Rahmen; zusätzlich benötigt der gemeinsame Recoveryweg Zeit. Der
Diagnoseaufwand kann den erreichten Grenzpunkt verändern. Der zusätzliche
leicht beobachtete Lauf in `old-ui-light-observation.json` erfasst deshalb nur
Funktions-/Publikationsgrenzen, echte Worker-CPU und Prozess-I/O, keinen Observer
an jedem I/O-Tick. Konkrete Grenzen/Stack/Resultate stehen in dieser Datei.
Dieser leicht beobachtete Apply scheitert nach P5 in `check_checkout` innerhalb
der abschließenden Gesamtprüfung: Journal veröffentlicht bei 260,756 s,
Runtime geschrieben bei 268,738 s, Recoverybeginn bei 300,000 s, Recoveryende
bei 431,293 s. Tatsächliche Worker-CPU: 428,797 s; UI-Wallclock: 431,790 s.
Die Korrektur behält genau diese vollständige Abschlussprüfung bei.
Die Popen-Zähler des venv-Redirectors im ersten UI-Lauf sind ausdrücklich keine
Worker-CPU-/I/O-Messung. Exit 0 allein ist bei diesem Fehlerprotokoll kein Erfolg.

`current-ui.json` führt dieselbe v7-Kopie nach dem Altfehler mit einem frischen
Plan fort: 32,428 s Plan, 69,773 s Apply einschließlich tatsächlichem UI-Readback,
nur Runtime geändert, v8, erneuter Plan/No-op, unveränderte No-op-mtimes,
erhaltene Suche/Kategorie/ID und erneute Auswahl einer anderen ID. Zwei reale
IDs wurden gegen ihre tatsächlichen Namen, Kategorien, Palettenfarben und
vollständigen Rastertexte geprüft; Abschluss-/Hintergrundbilder wurden wirklich
geladen und dekodiert. Das ist kein Mock eines Writers oder einer Browserantwort.

`portable-ui.json` verwendet die wirklich gepackte Windows-EXE und deren frozen
Worker. Der native Start als Standardbenutzer, tatsächlicher Standardbrowser,
zwei ID-Klicks und Migrationsplan wurden mit Windows UI Automation beobachtet.
Der physische Apply-Klick des Harness startete keinen Worker; das ist keine
belegte Produktfehlfunktion. Nach Widerruf des exklusiven Zugriffs gab es keine
weitere Maus-/Fensterautomation. Die Fortsetzung erfolgte in headless Edge gegen
dieselbe echte EXE: vollständige Migration, v8-Readback, No-op, A1-Speicherung
und geordnetes natives Beenden während eines aktiven frozen Readers. Schichten
und Grenzen stehen in `native-ui.json`; kein vollständiger physischer
Migrations-/Speicherdurchlauf wird daraus erfunden. Zwischen dem ausführlich
gemessenen/nativ geprüften Stand und dem Lieferhead änderten sich nur der
CI-Plantext und ein plattformübergreifender Test, keine Laufzeitquellen.
`binary-binding.json` liefert den tatsächlichen Dateivergleich sowie einen neuen
Fenster-losen EXE-Durchstich auf dem finalen Head mit Detail, Plan, Apply und No-op.
Die neu gebaute EXE, `base_library.zip`, Komponenten- und Inventardatei unterscheiden
sich beim Buildvergleich; eine identische komplette Binärdatei wird nicht
behauptet. Die Laufzeitquellen blieben unverändert. Der finale tatsächliche
Windows-EXE-Durchstich endete viermal mit Exit 0 und geprüftem v8/No-op-Inventar.

`synthetic-http.json` und `synthetic-ui.json` prüfen echte eigene v4/v7-/v8-Fälle:
A1/Kategorien inklusive belegter Löschung mit Neuzuordnung, bytegleiche PNG/SVG,
selected/none/standard, A3-Kombination und vollständiger neuer Proof, No-op-mtimes,
Stale-/Fremdbytes, blockierte Eingaben, echte Verbindungsunterbrechung und Neustart.
Status und Stop wurden auch während eines realen P1-Writers angesprochen; Drain
wartet dessen vollständigen Commit ab. `controlled-failures.json` unterscheidet
P0 (v7, keine Mutation), vollständiges Journalstaging, P1 (v7 + Journal) und P5
(v8 + Journal); Recovery erfolgt ausschließlich über `content_registry.recover`,
wiederholt, anschließend frisch geplant und erfolgreich angewendet. Fremde/höhere
und defekte Quellen sowie Link-/Stale-/Frist-/Bundlebindungen bleiben zusätzlich
durch das vollständige ausgewählte Katalogmodul geschützt.

`independent-readback.json` vergleicht 1619 nicht betroffene ursprüngliche Dateien
bytegleich mit dem Archiv, alle übrigen 55 Registry-/Runtimerows, Zielrevision,
die sechs neuen Rasterzellen und die exakten SVG-Bytes. Der vollständige aktuelle
Quellenreader und der neue Rasterproof wurden unabhängig erneut ausgeführt.
Der zusätzliche Versuch, alle historischen Bildproduktionen neu abzuleiten,
scheitert an deren ursprünglicher Tool-/Codec-Bindung; er wird ausdrücklich
nicht als bestanden angegeben und nicht durch geänderte Pins/Guards umgangen.
Der separate Descriptorvergleich in `historical-replay-binding.json` grenzt das
ein: Codecversionen stimmen überein, die ursprüngliche Modulbindung unterscheidet
sich bereits im Altstand bei `operation_diagnostics.py`; aktuell zusätzlich bei
`catalog_io.py`. Die historischen Derivationen und ihre erwarteten Hashes bleiben
unverändert und werden nicht fälschlich als mit neuem Tool reproduziert ausgegeben.

`save-comparison.json` ergänzt A2/A3-Altzeiten und reale 56-Eintrag-Kategorienzeiten.
Für diesen Altvergleich ist v8 eine dokumentierte Testvorbedingung, hergestellt
durch den korrigierten expliziten gemeinsamen Migrationswriter auf einer weiteren
isolierten Kopie. Die A1-Ausgangsmetadaten entsprechen der aktuellen Messfolge.
Für einen getrennten Alt-Apply wird ein schemaidentischer Plan mit dem aktuellen
Konstruktor vorbereitet; der alte Apply prüft ihn vollständig neu. Das ist kein
Beleg, dass die alte UI zuvor ihre Migration oder diesen Plan erfolgreich
ausgeführt hätte, und keine Umgehung alter Budgets oder Prüfer.
Für A2 wurden zusätzlich sämtliche vier Dateien des erfolgreich vom Altstand
erzeugten Bundles mit der aktuellen Vorbereitung bytegleich verglichen
(`a2-constructor-equivalence.json`).
Der alte A2-Plan benötigt 226,840 s; Apply erschöpft nach 300,006 s sein Budget.
Der alte A3-Plan erschöpft ebenfalls nach 300,444 s sein Budget. Ein zusätzlich
versuchter alter Apply auf einem aktuell erstellten A3-Bundle wird nach 181,539 s
vor Mutation abgewiesen: `Raster rating differs from independently checked bundle`.
`a3-tool-binding-comparison.json` grenzt dies ab: Rating und kompakte Analyse sind
exakt gleich, Werkzeugmodulbindung und davon abhängiger checked_hash unterscheiden
sich. Das ist **kein** vergleichbarer alter A3-Commitzeitwert. Es wird kein
erfolgreicher alter vollständiger A3-Plan/Apply erfunden und keine Toolbindung
umgeschrieben, um einen alten Apply künstlich ausführbar zu machen.

[CI-Lauf 43503895313, Versuch 1](https://github.com/venomenon328/picross/actions/runs/43503895313)
ist am genannten finalen Head/Test-Merge erfolgreich: docs, regulärer Windows-
Spieler, tools, vollständiges production.catalog und ci-required. 332/332
Katalogtests erfolgreich, kein Skip. Der frühere Windows-only-Test wurde nach
dem zu Recht zurückgewiesenen Linux-Skip auf echte Plattformfälle umgestellt.
Das Katalogmodul benötigte 1875,619 s; die weiche Zehn-Minuten-Zielzeit ist kein
Erfolgsgate. Die 56-Rätsel-Proben und diese Originale sind keine neue CI-Dauerlast.

Die portable ZIP ist ein eigenständiger Nutzerdownload; `delivery.json` bindet
Commit, exakte Pins, Bytezahl und SHA-256. Der reproduzierbare Bau steht in
`tools/puzzle_editor/README.md` am Produkthead: CPython 3.13.14 Windows x64,
Tcl/Tk 8.6.15 und die exakten requirements-windows-Pins, sauberer Commit,
absolutes neues Ausgabeziel außerhalb des Programmcheckouts. Kein Release,
kein automatisches Update und keine Änderung der Browservoreinstellung.

Die einmaligen Skripte unter `probes/` sind lesbare Diagnosequellen, keine neue
unterstützte Produkt-CLI. Zum Wiederholen in eine neue eigene Sandbox kopieren,
deren Kinder `work` (Produkthead), `old-program` (4e5), `build-env` und
`baseline-source.zip` anlegen. Das ZIP entsteht mit `git archive` von 4e5; jedes
genannte Datenziel frisch separat daraus entpacken und nur dort einen leeren
`.git`-Marker für die kopierte Editor-Datenwurzel anlegen. Produktpins verwenden;
Playwright 1.58.0 ist eine zusätzliche einmalige Prüfab­hängigkeit, installiertes
Edge wird verwendet. TEMP/TMP/TMPDIR vor Start unter die Sandbox setzen.
`synthetic_http.py` erzeugt den eigenen Zwei-ID-Seed; `synthetic_ui.py` und
`failure_probe.py` benutzen ihn. `browser56_probe.py old` und danach `retry`
führen den realen Alt-/Neu-UI-Weg seriell aus, `old -traced` den leicht
beobachteten Altfall. Große Leistungsproben nicht parallel ausführen.
`final3_measure.py` benötigt eine frische `final3-data`-Kopie; seine Zieländerungen
sind ausschließlich Teständerungen darin. Die weiteren Skripte nennen ihre
Ausgangs-/Bundleverzeichnisse ausdrücklich. `browser_bridge.py` ist nur für ein
gesondert erlaubtes natives Zeitfenster: eigene Sitzungs-URL privat protokollieren,
danach unverändert per ShellExecute an den OS-Standardbrowser geben. Keine
Sitzungsdatei veröffentlichen, keine native Fenstersteuerung ungefragt starten.

`manifest.json` ordnet genau drei unveränderte Status-PNGs mit Bytezahl/Hash zu:
Altfehler, wirkliche neue Apply-Phase mit Zeit und bestätigter Readback. Sie stammen
aus 1600×1000-Edge-Viewports bei DPR 1; es sind gezielte Elementoriginale ohne
privaten Checkoutkopf, keine umkodierten oder verkleinerten Vorschauen.
Der konkrete Belegcommit und der geprüfte binäre Abrufweg stehen im PR. Zugriff auf die Originalbytes
wurde per öffentlichem Raw-HTTPS-Abruf ohne Anmeldung geprüft. Der textgebundene
API-Abruf kann PNG/ZIP nicht als UTF-8 liefern; ein binärer Raw-/Gitabruf ist nötig.
Der unabhängige Reviewer öffnet die Originalbytes selbst. Zustellung ist keine
unabhängige Sichtabnahme.

Zweck/Empfänger: einmaliges PE-PERF1-A01 und anschließende persönliche PE-B-U01.
Endpunkt: A01, spätestens am 20.11.2026 Bedarf/Zustellung erneut prüfen. Eigener
Belegref wird im beauftragten Rückbau entfernt, weder nach main noch in den
Produktbranch übernommen. Lokale Anschlussdaten bleiben nur für diesen konkreten
Reviewzweck; temporäre Jobdaten werden laufintern abgeräumt. Kein fremdes WIP
oder Benutzercheckout wird bereinigt.
