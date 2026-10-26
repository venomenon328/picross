# CI2-D · Kurze native Prüfung und T01

Auftrag: [#416 einschließlich Umsetzungsvorbereitung V1](https://github.com/venomenon328/picross/issues/416).
Basis `main@8e5e99647596bc3ef9d7bd22bd746b73fbb424d5`, Arbeitsbranch
`chore/416-ci2-d-native`. [Aktueller Vertrag](CI_C_NATIVE_GROUPS.md).

## Startprüfung und Grenzen

Aktuelle AGENTS, Workflow, Projektprofil, fachliche Pflichtquellen, Issue und
Kommentare vollständig gelesen; #416 hatte beim Start keine Kommentare. Der
geprüfte aktuelle Main entspricht der zuletzt benannten Basis. C ist nach seinem
separaten R01 über PR #421 integriert; dessen historischer T01-Bericht bleibt
unverändert. D ändert Prüfer, Producer, Inventar und Ergebnisgate gemeinsam.
Produktcode, Runtime-/Savevertrag und Produktionsbestand bleiben unverändert.

Chromium ist weder beauftragt noch gestartet. Keine historische 500er-Route oder
Vergleichsgalerie wird erneut ausgeführt. Keine echten Spielstände, kein Merge,
Deployment, Release oder CI2-E-Datenabbau. Bereits vorhandene unversionierte
Produktionsdateien bleiben außerhalb des D-Commits. Lokale Diagnoseausgaben liegen
unter dem ignorierten `artifacts/ci2-d/`; keine neuen großen Repo-Belege.

## History: tatsächlicher kurzer Weg

Der feste Plan zählt **17 semantische Kommandos, vier neue wirksame Transaktionen,
genau zwei echte Godot-Spielprozesse**. Editorimport und Versionsabfrage sind
getrennte Toolchainprozesse, keine zusätzlichen Spielprozesse. Die native
SceneTree-Prüfung verwendet den regulären 1920×1080-Layoutweg, synthetisches T06
und ein isoliertes Profil; keine künstliche 560px-Fläche und keine Mengenschleifen.

| Prozess | Kommandos in Reihenfolge |
| --- | --- |
| Writer, 1–14 | Blattwahl; Farbe 2; Füllstrich (2,2)–(5,2); X-Strich (6,2)–(9,2); Radierer; Löschstrich (2,2)–(3,2); Füllwerkzeug; Undo; Redo; Undo; neuer Füllstrich (10,3)–(12,3); Zoom abwärts; Undo; reguläres Beenden |
| Reader, 15–17 | Blattwahl im frischen Prozess; echtes Redo; reguläres Beenden |

Ein Down/Move/Up-Strich ist ein Kommando. Farb-/Werkzeug-/Blattwahl, Navigation
und Beenden zählen mit; passive Frames/Assertions und Prozessstarts zählen nicht.
Die vier Striche erzeugen vier Transaktionen, der neue Strich verwirft den
zurückgenommenen Löschzweig. Beim ersten Beenden bleiben drei Transaktionen und
Cursor 2; nach Laden und Redo Cursor 3. `undo_used` bleibt wahr.

Der unabhängige Pythonprüfer importiert keine produktive Historylogik. Er
rekonstruiert nach jedem Kommando alle 2.500 Zellen, jede Transaktion einschließlich
Vor-/Nachwerten, Cursor, tatsächliche Änderungen und Undo-Merkmal. Navigation
ändert diese Felder nicht. Farb-/Werkzeugzustand, Zentrum, Zoom, Übersicht und
vollständige Hinweisansicht werden einschließlich Prozesswechsel verglichen.
Beide tatsächlich geschriebenen Save-JSONs müssen denselben vollständigen Zustand
enthalten; drei fremde synthetische Slotdateien bleiben byteidentisch.

Plan, vollständiger Trace, Writer-/Reader-Save, Fremdslot-Hashes und Summary sind
sechs feste Pflichtdateien. Das Ergebnisgate liest diese Originale erneut und
wiederholt den unabhängigen Abgleich; eine gefälschte positive Summary genügt
nicht. Zellmutation und abgeschnittener Trace werden ohne weitere Spielprozesse
abgewiesen. Werkzeuggegenproben mutieren außerdem Save/Ansicht und binden danach
alle Manifeste neu: auch dann muss das Gate scheitern. Quellen-, Run-, Versuch-,
Datei-/Hashbindung und Ablehnung fehlender/übersprungener Pflichtgruppen bleiben.

## Grafik, Katalog und Imports

| Feste PNG-Pflicht | Baseline | D |
| --- | ---: | ---: |
| catalog | 392 | 152 |
| graphics | 435 | 240 |
| completion | 22 | 22 |
| adapters | 9 | 9 |
| Summe | **858** | **423** |

435 feste Bilder weniger (**50,70 %**). Hinzu kommen weiterhin fünf anhand echter
EA-Zeitstempel ausgewählte variable Phasenbilder: 863 → 428 tatsächliche
Pflicht-PNGs bei vollständiger Vereinigung. Die Zahl ist eine Inventaraussage;
erzeugte Dateien und Laufzeiten werden zusätzlich aus echten Ausführungen gemessen.

- HZ-C entfernt die abgeschlossene 14/15-Galerie und doppelte Aufnahme desselben
  1920er-Layouts. Gewählte 15/19-Rollen, stabile Status-/Kategoriegrundlinien,
  Glyphen-/Fallbackpixel und native Menüs bleiben geprüft; pro Größe ein aktueller
  Statusbeleg statt dreier fast gleicher Bilder, alle drei Statusassertions bleiben.
- HC92 erzeugt 36 aktuelle Bilder ohne die 36 historischen before-Bilder. Native
  Schrift-/Pixelgrenzen, Zoomwachstum und die unabhängigen Gegenproben bleiben.
- ZS2 reduziert 201 kontrollierte/Echtzeitframes auf 42. X: 0/105/210 ms; Füllung:
  0/75/105/150/210 ms. Pro Zellgröße 12/24/36 bleiben drei echte gerenderte Frames
  in erster/zweiter Bewegungsphase und Endzustand. Unabhängige Pixelorakel weisen
  globales Fade, vertauschte X-Striche, Flächenwischen und sofortige Füllung ab.
  Günstige Logik-/Kurventests und andere aktuelle Bewegungsaussagen bleiben.
- Katalogbilder bündeln überlappende Einzelcrops zu einem nativen Layoutausschnitt
  je Zustand, ohne Skalierung oder Ersatzpixel. KE prüft 27 aktuelle PNG/SVG-
  Filter-/Geometrie-/Lebensdauerbilder ohne historische Vorherzeichnung.
- 54 synthetische Einträge ersetzen 300; echte Seitenwechsel, Sortierung vor
  Paginierung, 27 gelöste Einträge und Kategorien 48/6 bleiben. Repräsentative lange
  Namen und echte Menüs ersetzen 256 Kategorien/128-Zeichen-Last. Diese alten
  Lastmatrizen werden nicht als automatische Stressroute versteckt.
- Elf isolierte Katalogprojekte kopieren eine frisch importierte Basis. Vor jeder
  Mutation wird die gesamte Kopie dateiweise gegen dieselben Hashes geprüft;
  nach allen Modi bleibt die Basis unverändert. Neue Bilder in pages/adapter/at
  erhalten eigene Imports. Das senkt zwölf Editorimporte auf vier. Projekte und
  Savewurzeln bleiben getrennt; regular/restart teilen absichtlich ihr Testprofil.
- Linux kann catalog und graphics auf eigenen Xvfb-Displays mit den übrigen
  seriellen Gruppen überlappen, nachdem die erste serielle Gruppe den verifizierten
  Archivcache vorbereitet hat. Windows bleibt wegen Fensterfokus seriell. Ein
  gezielter Schedulergegenbeleg prüft Vorbereitung, gleichzeitigen Start und
  vollständiges Abwarten beider Gruppen. Keine Ergebnis- oder Profilcaches.

`native_metrics.py` ist als gemeinsame native Abhängigkeit allen Gruppen zugeordnet.
Alle gewöhnlichen CLI-/runtime-/all-/history-Wege verwenden den kurzen Ersatz.

## Historische Baseline, nur gelesen

[Run 40250428608, Versuch 1](https://github.com/venomenon328/picross/actions/runs/40250428608/attempts/1),
[Produktjob 121341083149](https://github.com/venomenon328/picross/actions/runs/40250428608/job/121341083149),
[Originalartefakt 12620432744](https://github.com/venomenon328/picross/actions/runs/40250428608/artifacts/12620432744).
Head `087db6b34c81ac8aae0e54c362250e597f1e5d3f`, Basis
`4e23e644f3457362e02b75f78fdb575a99265494`, Test-Merge
`9f93965de9ff4d5e55c6fe604d17667e25cb97bf`.
ZIP-SHA256 `fad0e41cda8d232d1cdb9b83ecda9e7234f1a810a57ae32c8423320feea19508`,
220.668.558 Bytes, 1.054 Dateien einschließlich 863 PNGs. Downloadhash und
Originalberichte wurden geprüft. Kein alter Producer wurde ausgeführt.

Ubuntu 24.04.5, Runner 2.338.0, Image `20261012.334.1`, Godot
4.7.2-stable/Software-OpenGL, verifizierter Downloadcache HIT. Gesamte native
Ausführung 847,739 s; Job 00:40:24,921–00:55:17,430 UTC, also 892,509 s
inklusive Setup/Upload/Cleanup. Die Summe paralleler Gruppen ist keine Walltime.

| Gruppe | Alte Gruppe s | Prozesse einschließlich Version/Import | Importe / s | Renderprozesse / kumulierte s | Gelieferte PNG |
| --- | ---: | ---: | ---: | ---: | ---: |
| core | 67,297 | 8 | 1 / 8,981 | 0 / 0 | 0 |
| history | 41,619 | 8 | 1 / 8,344 | 0 / 0 | 0 |
| catalog | 389,797 | 24 | 12 / 78,089 | 11 / 298,511 | 392 |
| completion | 60,065 | 5 | 2 / 13,202 | 2 / 43,490 | 27 |
| adapters | 242,148 | 34 | 2 / 12,753 | 14 / 106,789 | 9 |
| graphics | 407,842 | 24 | 1 / 7,337 | 17 / 364,871 | 435 |
| export | 28,224 | 5 | 2 / 23,322 | 0 / 0 | 0 |

Alte Katalogaufbereitung: 55 native Eingangsframes, 239 Pythoncrops,
99.957.791 Eingangsbytes, 54.708.255 Cropbytes; Decode 2,545 s, Crop 0,013 s,
PNG-Schreiben 3,309 s. Direkte native Bilder sind darin zusätzlich, nicht als
Pythoncrops mitgezählt. Aus 55 Kontexten und 392 gelieferten Bildern ergeben sich
447 unterschiedliche Katalog-PNGs vor Verpackung; wiederholtes Überschreiben
desselben Namens ist darin nicht gezählt. Vollständige erzeugte Mengen aller
Gruppen und separat instrumentierte Projektkopierzeiten sind nicht überliefert
und werden nicht erfunden. Prozesszahl wird aus gebundenen Phasenlogs, Rendering aus tatsächlichen
OpenGL-Prozesslogs ermittelt, einschließlich Grafikworker.

## D-Ausführung und Messgrenzen

Lokale native Vorläufe: Windows, NVIDIA RTX 3070/OpenGL 3.3, Godot
`4.7.2.stable.official.ed1daf0bf`, Python 3.13, Pillow 12.3.0. Archive erneut
hashgeprüft; keine globale Engineinstallation. Alle neuen Projekte/Profiles sind
temporär. Unterschiede zu Linux/Software-OpenGL verhindern eine direkte
Windows/Linux-Prozentbehauptung.

Entwicklungsfehler bleiben sichtbar: Die erste Historyfassung hatte bei 1280px
bereits den kleinsten passenden Zoom; der verlangte Navigationsschritt war
wirkungslos und das Orakel wies sie ab. Reguläres 1080p-Layout und Prüfung des
wirklichen Zellmaßes beheben das. Die erste verkleinerte Seitenfixture verwendete
mehrfach dieselbe Bildreferenz und scheiterte am unveränderten Registryvertrag;
eindeutige synthetische Bilder samt eigenem Import beheben das. Der erste gekürzte
Animationslauf erfasste den frühen 12px-X-Frame vor sichtbarer Atlasfarbe und
scheiterte am Pixelorakel. Aufnahme innerhalb der sichtbaren ersten Phase behebt
die Erfassung; Zeitfenster und Pixelanforderungen werden nicht gelockert.

Die finale Quellen-/CI-Bindung und Messung wird im Draft-PR nach den erfolgreichen
Pflichtjobs mit Head, Basis, Test-Merge, Run/Versuch und Originalartefakten ergänzt.
Dieser Bericht erklärt keine noch laufenden oder fehlgeschlagenen Jobs zum Erfolg.

Lokaler Historyvorlauf `native-dev2`: 22,153 s einschließlich frischer Vorbereitung,
beide Spielprozesse und Rohbeleggate erfolgreich. Katalogvorlauf `catalog-dev3`:
325,482 s Gruppenzeit / 328,515 s Gesamtharness, 16 Prozesse (Version, vier
Importe, elf Spiele); Import 29,094 s, Renderprozesse zusammen 235,244 s,
Setup 1,397 s. Elf vollständig geprüfte Kopien von 543 Dateien/33.377.307 Bytes
benötigten 27,905 s. 221 erzeugte Dateien/205 PNGs gegenüber 167 gelieferten
Dateien/152 PNGs; 53 Eingangsframes und 53 Crops. Diese Entwicklungsstände
waren noch nicht der finale saubere Lieferhead und ersetzen dessen CI nicht.

Dieser Katalogvorlauf zeigte trotz weniger Bildern eine Bytezunahme durch zu
großzügige Albumrechtecke (140.659.455 gelieferte Bytes). Der Lieferstand begrenzt
den gemeinsamen Ausschnitt deshalb auf Titel, Auswahl, Zähler, repräsentative
Karte und gegebenenfalls Seitenanzeige; keine ungenutzte Albumfläche. Die finale
CI misst die Wirkung. Kein Pixelresize oder Qualitätsverlust wird dafür eingeführt.

Werkzeugvorlauf: 225 Tests in 63,826 s erfolgreich, drei Linuxprüfungen lokal
übersprungen; nach zusätzlicher Schedulergegenprobe 19 gezielte Gate-/Isolations-
und Pixeltests in 3,288 s erfolgreich. Der Dokumentcheck des gesamten lokalen
Arbeitsverzeichnisses traf ignorierte Laufbelege und Windows-Zeilenenden und war
kein Erfolg. Am sauberen Git-Quellarchiv von `79e57f4` bestehen Dokumentcheck und
Diff-Whitespaceprüfung; die finale Linux-Docs-CI prüft den tatsächlichen Lieferstand.

Jeder neue Gruppenbericht enthält `work_measurements`: Prozessrollen und
kumulierte Prozesszeiten, Renderprozesse/-zeiten, Setup sowie erzeugte und
selektiert gelieferte Dateien/PNGs/Bytes. Erzeugt zählt vorhandene Dateien im
Gruppenausgang vor Verpackung ohne technische Kopien; geliefert zählt die festen
Originale/Ausschnitte. Interne temporäre Projektdateien und wiederholtes
Überschreiben desselben Namens werden nicht als neue Ausgabedateien gezählt.
Editorphase enthält Importsetup, Renderphase auch Assertions/Readback/Encoding.
Katalog-Decode/Crop/PNG-Zeiten bleiben zusätzlich separat. Diese kumulierten
Zeiten dürfen nicht als kritischer Pfad ausgegeben werden. Jobsetup, Queue,
Verpackung und Upload werden über Workflow-/Phasengrenzen gesondert bilanziert.

Relevante Integration soll unter zehn Minuten bleiben. Überschreitungen sind
sichtbare Optimierungsbefunde, keine stillen Ausnahmen. Der offene CI2-B-O01-
Produktionszeitbefund ist eigenständig und wird durch D nicht abgenommen.

## Getrennter vollständiger Selbstreview und Übergabe

Nach der Umsetzung wurde der vollständige Diff der 30 Dateien gegen die genannte
Mainbasis separat gelesen und gegen #416/V1 geprüft: Historyzustand/Ansicht/
Fremdslots, echte Prozessfolge, aktuelle Grafik-/Katalogaussagen, Producer-/Inventar-/
Gategleichheit, Isolation, Messgrenzen, Quell-/Run-/Versuchsbindung und Dokumente.
Der Review korrigierte eine versehentlich mitumbenannte Atlas-Auswahl (`large`
bleibt Ressourcenname), entfernte einen verbliebenen wirkungslosen KE-Vergleichszweig
und begrenzte die zu großen Katalogcrops. Zusätzliche neu gehashte Rohbelegmutationen
und der Linux-Parallelitätsgegenbeleg bestehen. Kein Produktcode, historischer
C-T01-Beleg, zentraler Workflow oder fremder Dateibestand ist geändert.

Keine offenen Codebefunde dieses Selbstreviews; native Korrekturläufe und finale
Pflicht-CI bleiben bis zu ihren tatsächlichen Ergebnissen offen. Der abschließende
PR bindet den erneuten Abgleich sämtlicher späterer Änderungen und Originalbelege
an seinen konkreten Lieferhead. Selbstreview ist keine unabhängige Zweitprüfung.

CI2-D-R01 bleibt vor Merge offen. Kein Merge, Deployment, Release oder Issueabschluss.
