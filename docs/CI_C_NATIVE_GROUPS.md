# CI-C: Native Prüfgruppen und Belegvertrag

Inventar vor Umstellung: `main@019b4dba98ef56c549ef5e7da10402dba0c9e93a`,
[Issue #249](https://github.com/venomenon328/picross/issues/249), CI-C/V1.
[CI-Policy](CI_POLICY.md) bestimmt Auswahl und Abnahme. Keine Produktänderung.

## Vollständige Zuordnung

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
