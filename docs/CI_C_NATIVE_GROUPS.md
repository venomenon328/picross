# CI-C: Native Prüfgruppen und Belegvertrag

## Neue Prüfungen und Featureabschluss · #502 / P3-A

Der [Lebenszyklusvertrag](CI_POLICY.md#testlebenszyklus-und-featureabschluss--502--p3-a)
gilt vor neuer nativer Prüf-/Bildlast: dauerhafte aktuelle Spiel-/Save-/Pixel-/
Exportregression oder befristeter Einführungs-/Abnahmenachweis, jeweils mit
Zweck, minimaler Ebene, Leser, Auswahl, CPU-/Wandzeit-/Datei-/Byte-/PNGkosten,
Verantwortung und konkreter Ablauf-/Reviewentscheidung. Neue Maschinen,
Frame-/Filmmatrizen, Generatoren und Artefaktklassen benötigen diese Erklärung
auch bei anderem Namen, Ausgabeordner oder optionalem Einstieg. Schwere neue
Dauerpflichten benötigen die separat gebundene Eigentümerentscheidung.
Der schnelle Docs-Guard prüft Quell-/Leser-/Auswahlbindung und Ablauf; T01 und
unabhängiges R01 prüfen Abdeckung und tatsächliche Kosten. Vor Featureabschluss
temporäre Last zurückbauen und verbleibende Dauerregressionen begründen.

Das heutige logische Pflichtinventar, seine physischen Aliase, alle Assertions,
Quellen-, Head-/Basis-/Run-/Versuchsbindungen und Pixel-/Exportgates bleiben
erhalten. Laufzeit, erzeugte/gelieferte PNGs und physische/logische Dateien/Bytes
werden weiter gemessen. P3-A setzt keine globale 75-MiB-/10-Minuten-Grenze,
ändert keine funktionalen Zeitfenster und erteilt keinen Browserauftrag. P2-C/P3-B bleiben
separat; bestehende Produktprüfungen werden nicht rückwirkend nach Namen verboten.

## Phasenschutz · #502 / P3-A-F02

Die [Eigentümerentscheidung vom 04.11.2026](https://github.com/venomenon328/picross/pull/506#issuecomment-6631521834)
ersetzt ausschließlich für `kat2-kk` den bisherigen 300-s-Abbruch: Während der
laufenden Phase wird bei 300 s einmal eine nicht-fatale Warnung in Konsole und
geflushtes Phasenlog geschrieben; der harte Schutz endet bei 600 s. Warnung und
Protokollierung verbrauchen denselben Rahmen. Erfolg zwischen den Grenzen bleibt
zulässig, sofern normale Exit-/Enginefehler-, Marker-, Fach- und Ergebnisprüfungen
bestehen. Alle 3.440 KK-Checks und Pflichtbilder bleiben erhalten.

Die bestehenden Phasenergebnisse in `product-report.json` enthalten tatsächliche
`seconds`, wirksame `timeout_seconds`, `warning_seconds`, `warning_emitted` und
`timed_out`; das gebundene Originalphasenlog hält Warnung bzw. Timeouttext fest.
Bei Timeout bleiben Fehlerstatus und die Bereinigung der eigenen Linux-
Prozessgruppe samt Nachkommen erhalten. Andere Phasen, auch `kat2-kk-import`,
übernehmen unverändert das jeweilige Aufruferbudget. Der Workflow bleibt bei
`--process-timeout-seconds 300`; Scheduler, Renderer und Threadpolicy bleiben
unverändert. Der gesonderte Buchproducer behält seine bestehenden Grenzen.

Kontrollierte Uhr-/Waitfälle und ein kurzer echter Linux-Kind-/Enkelprozessfall
prüfen diese Grenze im bestehenden Toolpfad ohne minutenlange Wartezeiten.
600 s sind ein Hangschutz, kein Leistungsziel. Tatsächliche CI-Zeiten und
verbleibende CI2-Zielverfehlungen werden in T01 am geprüften Head/Run ausgewiesen.

## Laufzeit und Originalpixel · #502 / P2-B

Die aktuelle Auswahl, sämtliche Produktassertions, KAT-2-Modi, nativen Prozesse,
funktionalen Zeitgrenzen und isolierten Projekte/Profile bleiben erhalten;
den selektiven KK-Hangschutz ersetzt F02 wie oben beschrieben. Nur Linux-
Softwarerenderprozesse erhalten `LP_NUM_THREADS=1`, ausgenommen die aktuellen
kurzen Save-/Schraffur-/Atlasbewegungs- und echten Buch-Lifecyclezeitfenster
(`kat2-information`, `current-drawing-capture`, `perf-b-native`, `book-integration`).
Die Gegenmessung mit einem Worker auch in diesen Zeitfenstern war fehlgeschlagen;
dort bleibt der ursprüngliche Mesa-Pool erhalten. Windows behält seine serielle
Fokusgrenze. Bereits vorhandene Editor-/Vorlagenarchive dürfen die Parallelität
nach erneuter vollständiger SHA-Prüfung sofort freigeben. Bei fehlendem/falschem
Cache bleibt zuerst ein echter serieller Gruppenlauf erforderlich. Jeder Producer
prüft weiterhin seine Archive und extrahiert eigene Werkzeuge. Kein importiertes
Projekt, Save oder Prüfergebnis wird gruppenübergreifend geteilt. Der Python-
Downloadpfad nutzt das vorhandene kurzlebige Jobtoken mit den unveränderten
Leserechten gegen anonyme GitHub-API-Limits; Godot erhält dieses Token nicht.
Export wartet
weiter auf beide Rendergruppen. Start-/Endoffsets, Cachevorbereitung, CPU-/
Kontextwechselkosten und Ergebnisprüfung werden separat gemessen; RSS ist der
bisherige Höchststand aller beendeten Kindprozesse, keine isolierte Phasenmessung.

KAT-2 behält alle 53 Layoutaufnahmen und unveränderten Ausschnittkoordinaten.
Der native Producer speichert sofort das bisher in Python ausgeschnittene
Rechteck. Originalframe-Maße/RGBA-Hash, Ausschnitt/RGBA-Hash und native PNG-Bytes
bleiben gebunden. Python prüft dekodierte RGBA-Pixel einschließlich Alpha und
liefert dieses native PNG nach Umbenennung einmal aus. Vollbildencoding,
erneutes Zuschneiden/Encoding und doppelte Kontextdateien entfallen. Die
unveränderten direkten KE-/HZ-/AT-Bilder bleiben im Pflichtinventar. Der bestehende
ausdrückliche PNG-Vergleich prüft zusätzlich den unabhängigen Pythonzuschnitt
eines identischen nativen Vollframes; Vergleichskopien entfallen nach Gleichheit.

HN behält alle 15 Fälle und sämtliche bisherigen Pixel-/Eingabe-/Cacheassertions.
Statt 15 Vollbildern liefert jeder Fall die exakt verglichenen 2.500 Originalpixel
und ihre 2.500 Basispixel in einem 50×100-PNG: oben Ist, unten Basis, ohne
Interpolation. Quellframe-/Basis-/Sample-RGBA-Hashes, Client, Board, Rasterursprung,
Zellgröße, Overlay und Kontext bleiben im Originalbericht. `hn_evidence.py`
wiederholt unabhängig alle Band-/Phantomvergleiche einschließlich Alpha und
natürlicher Overlayausschlüsse. Fehlende Fälle, falsche Maße/Bindungen oder
auch konsistent neu gehashte falsche Pixel scheitern. Dies sind Pixelsamples,
keine verkleinerten Kontextbilder; die übrigen Vollhinweis-/Schriftoriginale
behalten ihre eigenen unabhängigen Leser.

Byteidentische PNGs werden nach erfolgreicher Erzeugung nur einmal physisch
geliefert. `image_aliases` bindet jeden logischen Originalpfad mit Bytezahl/SHA
an ein tatsächlich geliefertes, identisches PNG; Ketten, Fremdpfade, doppelte
Ziele, Nicht-PNGs oder Überschreiben sind verboten. Producer und unabhängiges
Gate rekonstruieren die exakten Originalbytes nur für die bestehenden Leser und
entfernen diese temporären Kopien auch nach Fehlern. Das feste logische Inventar,
Originalberichte und Einzelbindungen bleiben unverändert verpflichtend. Fehler-
artefakte werden nicht dedupliziert. Physische und logische Dateien/PNGs/Bytes,
erzeugte Arbeitsdateien sowie direkt im Technikbereich erzeugte HIL-PNGs werden
getrennt ausgewiesen. Globale Budgetguards bleiben P3-B; neue Lebenszyklusregeln
stehen oben unter P3-A. CI2-Ziele gelten
erst nach tatsächlicher Messung als erreicht. Messwerte und Restbefunde im P2-B-T01.

## Studienrückbau · #502 / P2-A

`tools/book_lifecycle.py` enthält ausschließlich den unveränderten kurzen
Hilfe-/Produktlebenszyklus. `p1_product.py` ruft ihn als
`regular-book-integration` auf; `validate_book_lifecycle` bleibt das unabhängige
Ergebnisgate. `book_contract.SOURCES`, alle Pflichtassertions, sieben HIL-Originale,
Phasen-, Hash-, Head-/Basis-/Checkout-/Run-/Versuchsbindung bleiben erhalten.
Die manuelle CLI desselben Producers verlangt `--cache-dir` und `--output-dir`.
Es gibt keinen Vollstudien-, Fixturegenerator- oder Studienexportmodus mehr.

Entfernt sind `tools/book_study.py`, dessen exklusive Tests und
`validate_book_study` samt N04–N06-/F01-/Projektions-/Pixelmatrixguards sowie
`game/study/book/`: 27 Definitionen, 27 Reveal-SVGs, Registry/RAM-Adapter,
Szenen-/Shaderdiagnosen, Tooltip-Vollmatrix, Packprüfer und Webshell. Die
[historische Quelle](https://github.com/venomenon328/picross/tree/fc86d2a2eff543f5b0c4ff328a71e815e4bc43a7/game/study/book)
und [B-A-/B-B-Liefernachweise](BOOK_STUDY.md) ersetzen deren aktive Reproduktion.
P1 hat die Filmproduktion bereits vollständig entfernt; sie wird nicht ersetzt.

Aktuelle `core`-/`history`-/`catalog`-/`completion`-/`adapters`-/`graphics`-/`export`-
Regressionen bleiben ausgewählt wie bisher. Insbesondere KAT-2 `kb` prüft echte
Hover nach Zellaktionen, lesbaren Text, Clientgrenzen und Abbau beim Seitenwechsel;
`kk`/`ke` prüfen Reset-/Modustooltips. Der vorhandene `kb`-Pfad ergänzt ohne neue
Bilder einen verzögerten Whitespacehover, verzögerten Popupabbau und erneuten
beschrifteten Hover. Das ist eine kleine aktuelle Prüfaussage, keine Behauptung,
den wechselnden Windowsbefund P1-R01-O01 reproduziert oder behoben zu haben.

Der weiterhin ausdrücklich manuelle `book_windows_probe.py` baut ausschließlich
den regulären synthetischen Windowsplayer und behält beide echten negativen
PCK-Überlagerungen, Hashbindung, Tooltip-/Release-/Fokus-/Save-/Retrydiagnosen.
Sein externer rein lesender Beobachter liegt in
`game/tests/book_windows_observer.gd`; beide verwenden den echten SaveStore,
keinen historischen RAM-Adapter. `product_fixtures.copy_regression_game` versorgt
beide aktiven Producer. `tests/*` und `study/*` bleiben im Runtimeexport gesperrt;
der PCK-Audit prüft weiterhin die tatsächlichen Verzeichnisse und den Entrypoint.
B-B-M01/HIL-M01 und P1-R01-O01 bleiben offen; kein automatischer Desktoplauf oder
Chromiumauftrag. Die persönliche Prüfung erfolgt am regulären Spieler.

Die Vollstudie lief bereits seit #501 nicht mehr in CI. Ihr Quellenrückbau
belegt keine CI-Beschleunigung; aktuelle Kosten stehen im P2-A-T01 des PRs.
Laufzeitoptimierung und neue Größen-/Lebenszyklusguards bleiben P2-B/P3.

## Aktuelle gezielte Buchintegration · HIL-1 / #500

Eigentümeranweisung vom 03.11.2026: In CI keine komplette Buchprüfung und keine
Filmproduktion. `regular-book-integration` führt deshalb ausschließlich
`book-version`, `book-import` und `book-integration` aus. Die letzte Phase nutzt
den regulären Produktroot mit festen synthetischen Inputs für Hilfe, Navigation
und unveränderten Spiel-/Savezustand; keine vollständige Studien-/Materialroute.
`book_lifecycle` und `book-lifecycle/report.json` binden denselben begrenzten
Umfang an Head, Basis, Checkout, Producer-Versuch und aktuelle Quellbytes.
Das Ergebnisgate verlangt sämtliche Lifecycle-/HIL-Einzelassertions, genau die
sieben unten genannten 1920×1080-Originale, den Assertionbericht und drei Logs.
Zusätzlicher Film oder eine Galerie werden abgewiesen; Spielprofile werden nicht
ausgeliefert. Die vollständige Studienroute ist aus dem aktiven Tree entfernt.
Historische B-B-Nachweise behalten ihren damaligen Umfang und werden dadurch
weder erneut verlangt noch nachträglich als verkürzte Prüfung ausgegeben.

## Historischer B-B-Vollumfang / #493, #498

Die folgenden Absätze beschreiben den damaligen Liefernachweis. Für aktuelle
automatische Läufe gilt ausschließlich der gezielte Umfang oben.

Die Exportgruppe verlangt einmalig `regular-book-integration` und dessen
[B-B-T01-Belege](B_B_VERIFICATION.md). Das Gate prüft originale Einzelassertions,
die feste Szenariomenge, Doppelseitengeometrie, beide Blätterrichtungen,
24 Unterbrechungsfälle, gültige ID-/Revealinstanzen, gerenderte Glyphen-/Konturabstände,
Rückkehr mit aktuellem Fortschritt, Quellbindung, Materialvergleich und Papierstabilität,
vollständige Phasen, Film mit stabilem Katalogende und neun Übergabepaare samt
Dateihashes. Der reale Produktlebenszyklus ergänzt eingefrorene Schema-1-Bytes,
Redo-/View-Wiederherstellung, Schreibfehler/Retry, ID-gebundene Recovery,
Abbruch-/Generationskontrollen sowie leere und fehlerhafte Kataloge.
Der unabhängige Guard bindet die gemeinsamen Runtimequellen an den aktuellen
Checkout und verlangt sämtliche Lifecycle-Assertions. Die regulären Export-
und Paketprüfungen bleiben zuständig für Windows/Web; die zusätzliche B-A-
Exportmatrix entfällt. Prüfskripte und Studieninputs bleiben im Technikartefakt.
N03 bindet zusätzlich die eigene Ledertextur samt Importkosten, 15 unskalierte
Randdetails, echte verzögerte Tooltipfälle in den drei bestehenden Konfigurationen,
deren Inhalt/Geometrie/Lebensdauer und Gegenbeispiele für leeren Rahmen und alten
Hoverstrich. Producer, Originalbericht, unabhängiger Guard und Mutationstests
folgen gemeinsam diesem Umfang. Keine neue Gruppe und kein Browserauftrag.
N04 erhält diese Nachweise, ergänzt genau eine gezielte 1920×1200/UI100-Fläche
mit fünfter Übergabe sowie günstige Nachbar-/UI125-Geometrieprüfungen. 24
unskalierte Randdetails binden beide inneren Enden und tatsächliche Quellmaße.
Das Gate kontrolliert links beginnende Belegung, unabhängige Offsets einschließlich
Abbruch/Resize, Originalglyphenhüllen und explizite Breite/Höhe statt 16:9-Ableitung.
Tischquelle/Importkosten und beidseitige Paketisolation bleiben gebunden. Ein
tatsächlicher Windows-Exportlauf ergänzt Standard/Maximieren/Wiederherstellen;
Linux behauptet diese Probe nicht. Für B-B erhält ausschließlich `book-native`
nach Eigentümerklarstellung vom 02.11.2026 einen 600-s-Hangschutz statt 300 s;
Laufzeitziele werden berichtet, sind aber keine zusätzlichen Abnahmeblocker.
N05 erweitert denselben Lauf um zehn echte Informationsrouten, zwei nahe
Seitenlayouts in vier gezielten Flächen, sechs native Unterbrechungen und eine
günstige vollständige Entscheidungstabelle. Fünf bisherige plus vier neue
Handoffs behalten die Grenzen 4/0,1 samt Versatz-/Alphagegenprobe. Der unabhängige
Guard prüft Ursprung, ungleiche Offsets, tatsächliche Kamera-/Blattspuren, native
Hüllen, Optionsänderung und Film. N05 führte keine neue CI-Gruppe, Budgeterhöhung
oder Browserpflicht ein; die spätere B-B-Ausnahme steht oben.
N06 ergänzt vier 640×128-Tiefenbilder des echten Mesh-/Vertexpfads:
Ruhe, gegenüberliegende Landung, verbreiterter Spalt und flache Geometrie.
Die beiden Gegenbeispiele müssen scheitern; tatsächliche Leder-/Blockarrays
prüfen Gelenktiefe und positiven Abstand unter den bestehenden Mengenbudgets.
Ein echter Tree-Exit prüft den unter Windows gefundenen reentranten Fokusabbruch
und die Bindung an dieselbe Bewegung. Der Guard verlangt Fälle, PNG-Maße und
Messwerte mit acht Mutationen.
Die obigen N03–N06-Prüfungen bleiben unverändert auf die gemeinsame Darstellung
angewendet. B-A-R08/M01 sind auf PR #497 abgeschlossen. B-B bindet neue reguläre
Windowsoriginale und echte OS-Eingaben für sein getrenntes Selbstreview sowie
das spätere unabhängige B-B-R01; die persönliche B-B-M01 bleibt gesondert.

HIL-1 / #500 erweitert dieselbe Integration um passive Lehrbeispiele und die
vier Hilfekapitel. `help_cases.gd` enumeriert die tatsächlich dargestellten
kleinen Belegungen unabhängig; `help_native.gd` prüft echte GUI-Ereignisse,
verschachtelte Schriftrollen, Platz-/Scrollgrenzen, Besuchs-/Rückkehrkontext und
unveränderte Spiel-/Savewerte. Keine neue Gruppe und keine zusätzliche
Spielprozessmatrix. Sieben Originale (`integration/hil-{work,principle,
combination,colors,overlap,legend,pan}.png`) sind über `book_contract.py` gebunden;
der Guard verlangt Quellen, Assertions und Dateien. Ein gezielter Pan mit dem
neuen Seiteninhalt gehört zur Hilferoute; die vollständige Übergabematrix und
Filmproduktion werden in CI nicht ausgeführt. Die
PCK-Prüfung verlangt die drei aktiven Hilfemodule; Tests bleiben ausgeschlossen.
Es entsteht kein Chromiumauftrag und kein exklusiver Desktop-Eingabelauf.

## Aktuelle Umsetzung: CI2-D / #416

Der freigegebene [CI2-Vertrag vom 26.10.2026](CI_SLIMMING.md),
[Gesamtissue #412](https://github.com/venomenon328/picross/issues/412), ersetzt
die nachfolgenden ungekürzten History-/Bild-/Prozesspflichten.
[CI2-D / #416](https://github.com/venomenon328/picross/issues/416) ist auf
`chore/416-ci2-d-native` von `main@8e5e99647596bc3ef9d7bd22bd746b73fbb424d5`
implementiert. [T01, Messungen und Selbstreview](CI2_D_VERIFICATION.md) binden
die tatsächlichen Prüfungen. Separates D-R01 bleibt vor Merge offen.

Die neue Historyroute umfasst insgesamt höchstens 20 semantische Benutzerkommandos,
höchstens sechs neue wirksame History-Transaktionen und genau zwei tatsächliche
Spielprozesse zum Schreiben und frischen Laden/Redo im selben isolierten
synthetischen Profil. Werkzeug-/Farbwahl, Blattwahl, Navigation, Undo/Redo und
reguläres Beenden zählen mit; ein zusammenhängender Down/Move/Up-Strich zählt
als ein Kommando. Passive Assertions und Prozessstarts zählen nicht. Versteckte
Setup-Bearbeitungen, Mengenauffüllung oder Wiederholungen je Region/Fenstergröße
sind ausgeschlossen. Die 500er-Route entfällt aus Standard, `history`, `runtime`,
`all`, `--integration` und gewöhnlichen manuellen Vollläufen; sie wird nicht
automatisch als Stressroute weitergeführt.

Atomarer Strich, exakte Vor-/Nachwerte, Undo/Redo und Redo-Verzweigung, History
ohne Navigationsmutation, Zustand/Ansicht/Undo-Merkmal nach echtem Neustart,
tatsächlicher Redo und fremde Slotbytes bleiben geschützt. Das unabhängige
Python-Orakel importiert keine produktive Historylogik; zwei billige Gegenproben
weisen manipulierte Zelländerung und unvollständige Spur ohne weitere
Spielprozesse ab. Producer, Trace, Zusammenfassung und Gate binden die kurze
Folge; 500 Aktionen, mehr als 500 geänderte Zellen, fünf 100er-Segmente und das
künstliche 560px-Board sind keine aktive Pflicht.

Abgeschlossene HZ-C-14/15-Vergleiche und 36 HC92-before-Bilder entfallen;
aktuelle Schrift-/Layoutzusagen bleiben geprüft. Animationen erhalten relevante
Anfangs-/Zwischen-/Endzustände und einen echten Bewegungsnachweis. Katalogmodi
und wiederholte Importe werden konsolidiert; eine verifizierte unveränderliche
Importbasis darf geteilt/kopiert werden, veränderliche Daten bleiben isoliert.
Lastmatrizen mit 256 Kategorien, 128 Zeichen oder 300 Einträgen werden nur gezielt
gewählt. Untersuchungsziel sind mindestens 50 % weniger routinemäßige Bildbelege
gegenüber 858 festen PNGs; erzeugte und gelieferte Mengen werden getrennt gemessen.
CI2 §6 ersetzt den pauschalen Verzicht auf Laufzeitziele: übliche Standard-CI
möglichst unter fünf Minuten, aufwendigere relevante Integration unter zehn.

Auswahl, Producer und Gate werden zusammen auf das begrenzte Inventar umgestellt.
Tatsächlich gewählte native Gruppen behalten vollständige Ergebnisse, echte
Originalbelege und Quell-/Run-/Versuchs-/Dateibindungen; fehlende oder übersprungene
Pflichtresultate scheitern weiterhin. Native Scopes begründen nach CI2-A keinen
impliziten Browserauftrag. Alte Logs sind die Baseline; die 500er- oder volle
Vergleichsmatrix wird dafür nicht erneut ausgeführt.

Die feste aktuelle Lieferung umfasst 423 PNGs: 152 catalog, 240 graphics,
22 completion, neun adapters (zuvor 858). Die Dateien werden tatsächlich nicht
mehr erzeugt, wenn ihr Fall entfällt; Layoutbelege bündeln zuvor überlappende
Ausschnitte. ZS2 liefert 42 statt 201 kontrollierter/Echtzeitframes; drei echte
Bewegungsframes je Variante behalten die zeit-/pixelbezogenen Gegenorakel.
HC92 liefert 36 aktuelle Bilder, HZ-C die gewählten 15/19-Grundlinien ohne
14/15-Galerie; KE liefert 27 aktuelle Bilder ohne Legacy-Zeichner.

Der feste Historyplan enthält 17 Kommandos und vier neue Transaktionen. Das
Gate liest alle sechs Originaldateien (Plan, Trace, beide Saves, Fremdslot-Hashes,
Summary) und rekonstruiert Zellen, vollständige History, Cursor und Ansicht.
Katalogkopien sind vor jeder Mutation bytegleich zur verifizierten Importbasis;
elf Projekte bleiben getrennt, nur regular/restart teilen ihr Testprofil.
Unter Linux überlappen catalog und graphics mit den übrigen seriellen Gruppen
auf eigenen Xvfb-Displays, nach Cachevorbereitung durch die erste serielle Gruppe.
Unter Windows bleiben native Fenster wegen Fokus vollständig seriell.

## Gebundener CI-C-Ausgangsstand

Alle folgenden Mengen, Prozessfolgen, Pflichtdateien und Abnahmeformulierungen
dokumentieren den bisherigen Lieferstand und seine Erweiterungen. Ihre
Quellenbindungen bleiben erhalten; sie erzwingen keine Fortführung der alten
Mengen unter CI2. Für aktuelle Producer, Inventar und Gate gelten die oben
beschriebenen D-Umfänge; tatsächlich ausgewählte fehlende Resultate scheitern.

Inventar vor Umstellung: `main@019b4dba98ef56c549ef5e7da10402dba0c9e93a`,
[Issue #249](https://github.com/venomenon328/picross/issues/249), CI-C/V1.
[CI-Policy](CI_POLICY.md) bestimmt Auswahl und Abnahme. Keine Produktänderung.

## Bisherige vollständige Zuordnung

| Gruppe | Erhaltene ausführbare Aussagen und Pflichtbelege |
| --- | --- |
| core | `run_tests.gd` einschließlich Save/Recovery, KAT-2-Status, goldener Atlas-/Geometriefälle; ZS2-Logik; echter Exit-23-Fehlerpfad; p13 write/read in zwei Prozessen; kontrollierter Start. Vollständige gebundene Phasenlogs. |
| history | Fünf Prozesse mit je 100 echten Aktionen, unabhängiges Python-Zell-/History-/Redo-Orakel, sechster Neustartprozess, Navigation und negative Kontrollen; `integration/summary.json`. |
| catalog | Zehn KAT-2-Modi regular/restart/large/empty/invalid/adapter/information/kb/kk/ke einschließlich aller inneren Pointer-, Slot-, Reset-, Fehler-, Last-, KE-Pixelassertions. Temporäre synthetische Adapterregistrierung gehört hierzu, nicht pauschal alle Piloten. Zehn Originalberichte, Zusammenfassung, 244 unverkleinerte Python-Crops plus 72 unveränderte, bereits nativ erzeugte KE-Bilder. |
| completion | Eigener EA-Import; native und restart mit gemeinsamem Profil, sofortiger Commit/Save, Bewegung/Abbruch, Geometrie und ursprungsgebundener Reset. Beide Berichte, alle End-/Rechteckbilder, fünf anhand echter Zeitstempel ausgewählte Phasenbilder und unveränderte native APNG-Zeitfolge. |
| adapters | Vier RP6-Fälle partial/finish/read, fremde Slotbytes und T04-Negativkontrolle nach echter T01-Schreibaktion; anschließend alle vier Pilotcaptures aus genau diesen Saves. ZA-1: vier synthetische Pakete, echte Registrierung, Save-/Recoveryguards, zehn Prozesse einschließlich seed/oldreset, Pixel-/Slotisolation, eigener Windows-Export und tatsächlicher PCK-Audit; Windows zusätzlich EXE-Start. Alle bisherigen Pilot-/ZA-1-Berichte und Pflichtbilder. |
| graphics | VS2 write/read, GF1, HF149 write/read/native, vollständige 96er-Matrix, V1-Fokus, V2 write/read, V3/Sidebar, HC92-, HS186-, HN192-Pixel-/Eingabenachweise; fünf kompakte Capturestufen, 17 Buchzustände, aktuelle ZS2-/ZS1-Bewegungsorakel. PERF-B echte Ressourcen/Cache/Alpha/Mutation/Invalidierung. Alle bisherigen ausgewählten Originalbilder und vollständigen komprimierten Geometrieberichte. |
| export | Regulären Inhaltsbestand ausschließlich für Export übernehmen/importieren; echter Windows-Debugexport, separate EXE/Konsolenhilfe/PCK, externer nativer PCK-Audit, vollständiges Spieler-ZIP und Verpackungsprüfung. Windows zusätzlich headless und GUI-EXE-Start. |

AT-A ergänzt den elften Katalogmodus `at`: drei Fenster-/UI-Kombinationen mit
kleinem transparentem Bild und echtem Hover, zwölf unveränderte native Bild-/
Papierausschnitte und `at.json`/`at-fixture.json`. Die Completion-Gruppe ergänzt
drei Kombinationen für Endbild, Wiederöffnung und Überblendung, dazu 18 native
Bild-/Papierausschnitte und die feste Fixturebindung. Das unabhängige Gate liest
die Originalpixel und vergleicht sie mit importiertem RGBA und tatsächlichem
Papierhintergrund. Bisherige Fälle und ihre Originalbelege bleiben Pflicht.
Der gesonderte echte Windows-Export-/Savewechsel und die Abschlussbindung
stehen in [AT-A-T01](AT_A_VERIFICATION.md).

Jede Gruppe behält die hashgeprüfte Toolchain, aktive Buch-/Atlasressourcenprüfung
und ihren eigenen isolierten Editorimport. Die genaue Pflichtdateimenge steht in
[native_artifacts.json](../tools/native_artifacts.json), ausschließlich Dateinamen
aus der aktiven technischen Matrix. Keine historischen Daten oder Korpusreplays.
EA-Phasenbilder werden weiterhin aus den tatsächlichen nativen Zeitstempeln abgeleitet.
Die vollständige Vereinigung erhält jede bisherige aktive Prüfaussage; Pilotcapture
ist jetzt auch bei allein gewählter Adaptergruppe Pflicht.

## Auswahl und Ausführung

`native_contract.py` ist die gemeinsame Quelle für Auswahl und Gate.
`picross-ci-selection-v4` ergänzt `native_groups` und `native_expected` mit exakter
Teilprüfungsmenge. Die sechs CI-A-Jobergebnisse und CI-B-Browserbelege bleiben Pflicht.
Der vollständige Base-/Head-Treevergleich, beide Rename-/Delete-Seiten, Inhalts-
Dateimodusschutz, Main-Abkürzung und konservative unbekannte Wirkung bleiben.

**CI-258 / #258:** Zwischen Docs-Producer und Scheduler/Gate ist `native_groups`
ein kanonischer kompakter JSON-Array-String (`[]` bei keiner Auswahl),
nicht mehr CSV beziehungsweise ein leerer Outputwert. Für den bestehenden
Product-Workflow wird die Liste bei Übergabe zu CSV dekodiert/verbunden;
die Entscheidung zum Spieler-/PCK-Download beruht auf Listenmitgliedschaft.
Format der Selection-/Result-Artefakte bleibt v4 mit echtem JSON-Array.
Fehlende beziehungsweise nichtkanonische Outputs werden auch bei
leerem Array abgewiesen; die Quell-/Run-/Retryprüfung bleibt unverändert.

| Geprüfte exakte Abhängigkeit | Native Gruppen |
| --- | --- |
| `tools/kat2_product.py`, `tools/native_images.py`, `game/tests/kat2_probe.gd` | catalog |
| `tools/ea_product.py`, `game/tests/ea_probe.gd` | completion |
| `tools/p14_integration.py`, `game/tests/p14_integration.gd` | history |
| `catalog_ink.gd`, `catalog_tip.gd` unter `game/ui/` | core, catalog, adapters, graphics, export; RP6-/ZA-1-Kartencaptures und kompakter Album-Capture verwenden die Darstellung |
| `catalog.gd`, `catalog_card.gd` unter `game/ui/` | core, catalog, completion, adapters, graphics, export; Karten öffnen, Reset, Pilot-/Adapter-Slotisolation und Album-Capture |
| `game/model/catalog_difficulty.gd` | alle sieben Gruppen; Anzeige über `catalog_card.gd` und gemeinsame Registryvalidierung über `content_registry.gd` |
| `game/ui/completion.gd` | core, catalog, completion, adapters, graphics, export; KAT-2/KE rendert die Abschlussansicht, RP6/ZA-1 prüfen echte Abschlüsse/Reveals |
| `tools/za1_product.py` | adapters, export; gemeinsamer PCK-Auditor |
| RP6-/ZA-1-Probes | adapters; `content_pack_probe.gd` zusätzlich export |
| Exakt benannte native Render-/Atlasprüfer und aktive Renderer im Vertrag | core, graphics, export |
| Gemeinsame UI (`main.gd`), Save/Session, Fixtures, unbekannte Namen, gemeinsame Harness-/Toolchainwirkung | alle sieben Gruppen |

Keine Präfixausnahme für neue Dateien. Mischdiffs vereinigen alle betroffenen
Gruppen. CI-A entscheidet weiterhin unabhängig über Browser, Fachtests, Preflight
und Zustellung; deren eigene Abhängigkeiten bleiben erhalten. Ein reiner nativer
Katalogharness benötigt keinen Browser-/SSH-Lauf. Runtime-Katalogänderungen behalten
ihre CI-B-Browsergruppen. Kern-/Exportpflichten folgen der tatsächlichen Wirkung.

Die UI-Zuordnung folgt den aktiven Aufrufern: `rp6_probe.gd` und `za1_probe.gd`
öffnen Karten über die Hauptszene, prüfen Slotisolation und verdiente Reveals;
`rp6_capture.gd` liefert auch Albumzustände. `capture.gd` rendert mit
`capture_compact_layout()` den Katalog und mit `capture_h1()` verdiente Albumzustände.
`ke_graphics.gd` wird vom KAT-2-Modus `ke` ausgeführt und prüft `Completion` direkt.
History bleibt bei den fünf UI-Modulen ungewählt: die 500er-Route wählt ihre Session
direkt und prüft Zell-/History-/Ansichtszustand, keine Karten-/Abschlussdarstellung.
Ink/Tip wählen auch nicht allein die EA-Gruppe. Das Difficulty-Modul ist dagegen
kein reiner Anzeigeleaf: `content_registry.gd.validate()` verwendet `Difficulty.valid()`
für jeden v3-Eintrag. Registryladung, Definitionen/Slots und der native PCK-Audit
betreffen deshalb auch History, Adapter, Grafik und Export. Die explizite Zuordnung
aller sieben Gruppen ist hier begründet; der unbekannte Fallback ist kein Pfadnachweis.
`test_ci_c.py` prüft die sechs realen Einzelpfade, den Difficulty-Import beider
direkten Verbraucher, Mischdiffs, sichere Nichtauswahlen und manuelle Erweiterung
über `ci_scope.classify()` einschließlich Schedulerflags und unveränderter Browserwahl.

`native-core`, `native-history`, `native-catalog`, `native-completion`,
`native-adapters`, `native-graphics`, `native-export` erweitern manuell um die
benannte Gruppe. `runtime` erhält core/history/catalog/completion/export plus
vollständige Browserprüfung. `visual`/`perf-b` verlangen core/graphics/export plus
Browser. `production`, `all` und `toolchain` erweitern auf alle nativen Gruppen;
Browser-/Zustellungs-/Preflightpflichten folgen weiterhin ihrer bisherigen Zuordnung.
Kein Scope kann automatisch erforderliche Gruppen entfernen.

Lokaler Standard ist die vollständige Vereinigung. `p1_product.py --groups catalog`
startet ausschließlich Katalog; analog für alle anderen Gruppen. Die alten lokalen
Flags bleiben kompatibel erweiternd: `--integration` bedeutet history/catalog/
completion, `--pilots` adapters, `--visual` oder `--perf-b` jeweils graphics;
core/export bleiben bei Verwendung dieser alten Flagfamilie erhalten.
CI verwendet ausschließlich die neue explizite Gruppenliste.

Jede Gruppe startet einen eigenen Pythonprozess mit neuem temporären Projekt,
eigenen APPDATA/LOCALAPPDATA- beziehungsweise XDG-Wurzeln und eigenem Ausgabe-
und Technikverzeichnis. Die absoluten temporären Grenzen werden im Bericht
festgehalten und im Gate auf getrennte Wurzeln geprüft. Nur hashgeprüfte
Downloadarchive werden geteilt; jeder Prozess prüft sie erneut und extrahiert
seine eigene Engine/Exportvorlage. Keine gemeinsamen importierten Projekte/Saves.
Der erste echte Gruppenlauf füllt gegebenenfalls den Downloadcache vor Parallelität.

Unter Linux überlappt graphics mit den übrigen seriellen Gruppen, jeweils mit
`xvfb-run -a` und eigenen Displays. Unter Windows laufen sämtliche Gruppen
seriell: keine konkurrierenden interaktiven Fenster während Katalog-/EA-Dialogen.
Der vorhandene innere Grafikworker bleibt ebenfalls projekt-/profilisoliert.
Fehler einer Gruppe verhindern nicht die Diagnose der übrigen Gruppen, verhindern
aber den Gesamterfolg. Laufende Phasenlogs liegen direkt im späteren Technikartefakt.

Die inneren Prozessfolgen bleiben: KAT-2 regular → restart mit gemeinsamem Save;
EA native → restart; fünf History-Schreibprozesse → unabhängiges Orakel → read;
RP6 partial → finish → read → Capture aus echten Saves. T04-Negativkontrolle
verändert nur eine Profilkopie über echte Zellaktion. ZA-1 seed/partial/finish/read/
oldreset/reset erhält seine gegenseitigen Slotbyteprüfungen. Der isolierte
serielle Editorimport mit Wiederherstellung der Projektbytes bleibt erhalten.

## Bilder, Messung und Gate

Katalogaufbereitung liest jeden der 56 tatsächlichen Kontextframes einmal, schneidet die
unveränderten nativen Rechtecke und schreibt PNGs mit `optimize=False`,
`compress_level=1`. Kein Resize, keine Palettenreduktion, keine neue Grafik.
`--compare-native-png` beziehungsweise der gleichnamige Dispatchschalter schreibt
zuerst den bisherigen `optimize=True`-Weg und danach den neuen Codec auf denselben
Crops. Jede Ausgabe wird wieder zu RGBA dekodiert und bytegenau verglichen,
einschließlich Alpha und Maßen. Vergleichskopien werden erst nach Gleichheit
entfernt. Kontextmaße/-SHA, Regionen und beide RGBA-Identitäten bleiben im Bericht.
Der Vergleich ist eine ausdrückliche Abnahmemessung, keine dauerhafte Altpfadpflicht.

`kat2/image-costs.json` wird ab Beginn und nach jedem Eingangsframe fortgeschrieben;
Fehler bleiben sichtbar. Er trennt Frame-I/O/Dekodierung, Zuschneiden, PNG-Encoding/
Schreiben, Quellbindung und Vergleich samt Eingangsframes, Crops und Dateibytes.
Wandzeit und CPU-Prozesszeit der Bildaufbereitung werden getrennt angegeben.
Native Rendering-/Interaktionsphasen stehen mit Start/Ende und Dauer in den
Prozessberichten; sie enthalten auch Assertions und funktionale Wartezeiten und
sind keine reine GPU-Zeit. EA misst Frame-I/O und APNG-Schreiben getrennt, behält
alle echten Zeitabstände und die bisherige RGB/APNG-Ausgabe unverändert.

Dateiselektion und Spieler-ZIP-Verpackung besitzen eigene Dauern. Der Runner
bindet tatsächliche gelieferte Technikdateizahl/-bytes; Upload-/Kompressionsdauer
und tatsächlich gespeicherte Actions-Artefaktbytes werden aus den betreffenden
Actions-Schritten und API-Metadaten ermittelt. Upload ist nicht Teil der nativen
Renderzeit. Referenz, Nachhermessung, Runner/Cache/Toolchain, Queue, Jobdauer,
summierte Runnerbelegung und überlappende Spanne werden im PR getrennt ausgewiesen.
Keine Zeit-/Bytegrenze, kein verkürzter funktionaler Timeout.

`native-result.json` bindet jede erwartete und tatsächliche Gruppe, Prozessausgänge,
Originalberichte, vollständige Teilprüfungsmenge, Quellen und Dateien. Das Inventar
verlangt die bisherigen Pflichtbilder auch dann, wenn ein Producer sie aus seiner
Selbstauskunft entfernt. Die fünf variablen EA-Phasenbilder werden aus den echten
Sequenzzeitstempeln unabhängig neu bestimmt. Originale Fehler-/Checkfelder und
KAT-/EA-Unterberichte müssen mit dem aggregierten Bericht übereinstimmen.
Die originale History-Zusammenfassung muss 500 Aktionen, Kategoriengesamtzahl,
verbleibenden Redo-Zweig, Zellhash, beide Negativkontrollen und Neustart ausweisen
und mit dem Gruppenbericht übereinstimmen.

`ci-required` lädt Technik und gegebenenfalls Spieler vom konkreten Product-
Producer-Versuch herunter und prüft tatsächliche Datei-/SHA-/Größenbindungen,
eindeutige Vollständigkeit, Gruppen-/Phasenstatus und EXE/PCK-Bytes im Spieler-ZIP.
Ein grüner Productjob allein reicht nicht. Fehlend, leer, doppelt, falsch,
fehlgeschlagen, abgebrochen, nicht gestartet oder ausgewählt+skipped scheitert.
Nicht ausgewählte Gruppen erscheinen ausdrücklich als nicht ausgeführt.

Head, Base, tatsächlicher Test-Merge, Event und Run müssen übereinstimmen;
Auswahlversuch ≤ Productversuch ≤ Gateversuch. Erfolgreiche Jobs dürfen nur
innerhalb desselben unveränderten Runs wiederverwendet werden. Artefaktnamen sind
`picross-p1-technical-<head>-<attempt>` (sieben Tage) und
`picross-p1-player-<head>-<attempt>` (vierzehn Tage). Kein Wildcarddownload alter
Resultate, keine Ergebnis-Caches. Technische Originalframes bleiben lokal, soweit
sie nicht zu den bisherigen Pflicht- oder konkreten Fehlerbildern gehören.

## Abnahme

HZ-A ergänzt den bestehenden `kk`-Modus um lokale Tidy-Hand-Zeichen-/Ellipsen-
und Layoutprüfungen, vollständige Größenangaben, 128 Zeichen lange Kategorien,
256 auswählbare Kategorien, Hilfe und native Dialoge. Die drei HZ-Fenster-/UI-
Kombinationen liefern zusätzlich 18 unveränderte native `hz-*.png`-Ausschnitte
beziehungsweise Kontextbilder; sie stehen im verpflichtenden Direktbildinventar.
Bestehende KAT-/KE-/AT-Prüfungen und ihre Bilder bleiben erhalten.

HZ-C erweitert denselben `kk`-Modus um stabile rollenbezogene Grundlinien,
unveränderte Anfangsglyphenpixel bei Wort-/Fallbackwechsel, feste Kategorie-
und Fußbereiche sowie den korrigierten Größenvergleich 14/15. Die 21 zusätzlichen
Originalausschnitte `hz-c-*.png` und die Messwerte in `hzc_measurements` gehören
zum selben verpflichtenden Direktbild-/Berichtsweg; Auswahl und bestehende
Pflichten bleiben unverändert. [HZ-C-Prüfzuordnung](HZ_C_VERIFICATION.md).

CI-C-T01 bindet technische Ergebnisse, Messungen, finalen Head/Base/Test-Merge/Run
und getrennten vollständigen Selbstreview im Draft-PR. CI-C-R01 bleibt ein separater
qualifizierter Review vor Merge. Bestehende Windows-/Eigentümergates bleiben separat.
