# CI2-C · Kurzer Chromiumumfang und T01

Auftrag: [#415 einschließlich Umsetzungsvorbereitung V1](https://github.com/venomenon328/picross/issues/415).
Basis `main@dd56d310d942eee47448df4cdcca5e4af4a49b00`, Arbeitsbranch
`chore/415-ci2-c-chromium`. [Aktueller Vertrag](CI_B_BROWSER_GROUPS.md).

## Startprüfung und Umfang

Main/Issue/Kommentare am 26.10.2026 erneut geprüft: keine vorhandene C-Arbeit,
keine Kommentare. Separater sauberer Worktree; fremde unversionierte Arbeitsdateien
im ursprünglichen Checkout bleiben unberührt. `gh` ist als Eigentümer authentifiziert,
Repo-Push-/Workflowrechte vorhanden; registrierter Workflow `ci-chromium.yml`
(ID 389212566) ist aktiv. Implementierung und kurzer Chromiumlauf einschließlich
Build sind ausdrücklich beauftragt. Kein Merge, Deployment oder Release.

Neun Kernfälle und zwölf Erfolgsbilder ersetzen 33 Fälle/60 gelieferte Bilder.
Einzelgruppen bauen nur benötigte Exporte. Das separate optionale Exportprofil
hat zwei Fälle und wird nicht an kurze/all-/Toolchainscopes angehängt.
Native AT-Matrix und alle unabhängigen Nichtbrowserpflichten bleiben erhalten.

## Baseline und Messung

Original: [Run 40219765031, Versuch 1](https://github.com/venomenon328/picross/actions/runs/40219765031/attempts/1),
[Browserjob 121259857205](https://github.com/venomenon328/picross/actions/runs/40219765031/job/121259857205),
[Buildjob 121259856855](https://github.com/venomenon328/picross/actions/runs/40219765031/job/121259856855),
[Artefakt 12610550897](https://github.com/venomenon328/picross/actions/runs/40219765031/artifacts/12610550897).
Head `bc54a7122f2796949670e08925dd6eea9c4c1bf6`, Test-Merge
`01dd7f2c765fe206b4a5c1fd0f90b6713a09df3e`. Browser 40:46, Build 1:52.
Die Originalberichte wurden heruntergeladen; kein historischer Browserlauf gestartet.
Die beiden im Issue genannten Job-IDs sind in Versuch 2 erhaltene Erfolge mit
unveränderten Start-/Endzeiten aus Versuch 1. Die ursprünglichen Job-IDs sind
Build `121249048134` und Browser `121249512206`; das Originalartefakt bindet
`run_attempt=1`, nicht einen neu ausgeführten Browser im Retry.

Runner: Ubuntu 24.04, Playwright 1.58.0, Chromium 145.0.7632.6,
Godot 4.7.2-stable, Software-WebGL/SwiftShader. Der originale Joblog nennt
Image `20261012.334.1`, das originale Ergebnis-JSON dagegen
`20261023.334.3`. Diese Abweichung bleibt sichtbar; eine identische Imageversion
wird nicht behauptet. Der Downloadcache enthält erneut hashgeprüfte
Toolchainarchive, keine Browserergebnisse; Profile/Loopbackhosts starten pro
Gruppe leer. Browserprozesse zählen Starts persistenter Playwright-Kontexte,
nicht sämtliche Chromium-Unterprozesse.

Baseline: 33 Fälle, acht Browserstarts, 19 Navigationen, 62 Screenshotaufrufe
plus drei direkt geschriebene beobachtete Übergangsframes = **65 erzeugte PNGs**.
Das Artefakt enthält **60 gelieferte PNGs**. HZ-C schrieb beim Rückwechsel fünf
bereits vorhandene Namen erneut: 20 erzeugte gegenüber 15 gelieferten Bildern.
Die drei Frame-Schreibvorgänge sind aus den drei Original-AT-Zeilen und dem
damaligen Producer belegt; ihre separate Schreibzeit wurde damals nicht gemessen.

Zeitbasis: Job-API mit Sekundengenauigkeit; Phasen-/Fall-/Operationszeiten aus
monotoner Messung. Fallzeiten enthalten auch den eigenen Start und Vorbereitung;
keine rechnerische Gleichsetzung alter und neuer Fallgrenzen. Abfragen in den
folgenden Falltabellen fassen `query` und `state` zusammen, Warten fasst `wait`
und die bestätigte Sicherung zusammen. Verschachtelte Operationszeiten werden
exklusiv gezählt; Python-, Locator- und nicht instrumentierte Arbeit erklärt die
Differenz zur Fallzeit. Teardown wird außerhalb der Fachfälle bilanziert.

Baselinequeue: Run angelegt 18:07:47 UTC, docs gestartet 18:09:02 (75 s);
nach docs bis Build 2 s, nach Build bis Browser 3 s. Build 18:09:46–18:11:38
(112 s), Browser 18:11:41–18:52:27 (2446 s). Summe Build+Browser **42:38**,
kritischer Pfad vom Buildstart bis Browserende einschließlich Zwischenqueue
**42:41**. Diese Zahlen beschreiben den Browserpfad, nicht die parallel
laufenden nativen/Produktionsjobs oder das damalige fehlgeschlagene Gesamtgate.

### Alte Fälle aus den Originalbelegen

| Fall | s | Browserstarts | PNG erzeugt/geliefert | Navigation n / s | Abfragen n / s | Warten n / s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| regular-start | 14.412 | 1 | 1/1 | 1 / 0.061 | 3 / 0.516 | 2 / 11.030 |
| B02 | 8.996 | 1 | 0/0 | 1 / 0.086 | 4 / 0.638 | 7 / 7.741 |
| B03 | 101.945 | 0 | 5/5 | 0 / 0.000 | 83 / 13.213 | 79 / 23.880 |
| KU-B01 | 253.375 | 0 | 1/1 | 0 / 0.000 | 103 / 20.605 | 86 / 22.233 |
| AT-W01-C | 125.327 | 0 | 6/6 | 0 / 0.000 | 98 / 13.112 | 51 / 46.208 |
| HZ-A-W01 | 62.802 | 0 | 6/6 | 0 / 0.000 | 57 / 6.806 | 66 / 16.104 |
| HZ-B-W01 | 271.906 | 0 | 9/9 | 0 / 0.000 | 131 / 16.323 | 159 / 42.689 |
| HZ-C-W01 | 141.565 | 0 | 20/15 | 0 / 0.000 | 120 / 15.080 | 142 / 34.252 |
| B04 | 35.674 | 1 | 1/1 | 1 / 0.058 | 22 / 2.635 | 15 / 18.575 |
| B05 | 12.686 | 0 | 0/0 | 0 / 0.000 | 18 / 1.967 | 3 / 0.604 |
| B10 | 37.035 | 0 | 0/0 | 0 / 0.000 | 34 / 3.125 | 35 / 21.680 |
| B11 | 4.311 | 0 | 0/0 | 0 / 0.000 | 9 / 0.957 | 4 / 0.819 |
| B12 | 41.014 | 0 | 2/2 | 0 / 0.000 | 22 / 2.142 | 30 / 22.012 |
| B15 | 13.944 | 0 | 0/0 | 0 / 0.000 | 12 / 1.312 | 12 / 6.689 |
| B13 | 115.742 | 1 | 1/1 | 2 / 0.306 | 55 / 6.726 | 45 / 36.990 |
| B14 | 70.013 | 0 | 0/0 | 0 / 0.000 | 36 / 3.284 | 30 / 18.515 |
| AT-W01-E | 362.256 | 0 | 9/9 | 0 / 0.000 | 142 / 15.441 | 91 / 52.877 |
| B01 | 8.205 | 1 | 0/0 | 2 / 0.072 | 7 / 0.480 | 10 / 7.147 |
| B06 | 51.033 | 0 | 0/0 | 1 / 0.127 | 32 / 3.838 | 19 / 31.701 |
| B07 | 12.799 | 0 | 0/0 | 1 / 0.264 | 10 / 1.069 | 4 / 9.691 |
| B08 | 24.222 | 1 | 0/0 | 1 / 0.036 | 16 / 2.046 | 12 / 18.773 |
| AT-W01-P | 153.770 | 1 | 3/3 | 2 / 0.312 | 49 / 6.037 | 22 / 30.078 |
| KU-B02 | 70.509 | 0 | 1/1 | 1 / 0.346 | 37 / 5.440 | 34 / 49.278 |
| B09 | 3.059 | 0 | 0/0 | 0 / 0.000 | 7 / 0.811 | 2 / 0.334 |
| B16 | 134.113 | 0 | 0/0 | 0 / 0.000 | 52 / 5.151 | 46 / 71.247 |
| B17 | 27.282 | 0 | 0/0 | 1 / 0.029 | 12 / 1.564 | 13 / 20.786 |
| B18 | 27.365 | 0 | 0/0 | 1 / 0.294 | 8 / 0.907 | 8 / 22.277 |
| B19 | 23.564 | 0 | 0/0 | 0 / 0.000 | 6 / 0.800 | 5 / 19.526 |
| B20 | 19.683 | 0 | 0/0 | 1 / 0.327 | 4 / 0.606 | 3 / 18.750 |
| B21 | 12.550 | 0 | 0/0 | 0 / 0.000 | 7 / 1.143 | 5 / 8.174 |
| B22 | 33.696 | 0 | 0/0 | 1 / 0.296 | 10 / 1.375 | 8 / 27.394 |
| B23 | 24.596 | 0 | 0/0 | 1 / 0.040 | 7 / 0.648 | 7 / 21.245 |
| B24 | 0.218 | 1 | 0/0 | 1 / 0.046 | 1 / 0.002 | 1 / 0.023 |

### Neue Messung

[Run 40358707608, Versuch 2](https://github.com/venomenon328/picross/actions/runs/40358707608/attempts/2)
auf `310725d46b8f80359cb2e464bc01685f9eb54530`: **erfolgreich**, neun von neun
Fällen, zwölf erzeugte und zwölf gelieferte PNGs, sechs Browserstarts.
[Build](https://github.com/venomenon328/picross/actions/runs/40358707608/job/121700503102),
[Chromium](https://github.com/venomenon328/picross/actions/runs/40358707608/job/121701493551),
[ci-required](https://github.com/venomenon328/picross/actions/runs/40358707608/job/121704706005),
[Originalberichte/Bilder](https://github.com/venomenon328/picross/actions/runs/40358707608/artifacts/12667649573),
[angenommenes Gesamtergebnis](https://github.com/venomenon328/picross/actions/runs/40358707608/artifacts/12666964367).

Expliziter Originalinput: `scope=auto`, `browser_scope=short`. Source-Head,
Base und getesteter Checkout des Dispatchs sind identisch zum genannten Head;
dies ist kein PR-Test-Merge. Auswahl/docs aus Versuch 1 bleiben gebunden,
Build, Browser und Gate stammen frisch aus Versuch 2. Das Gate akzeptiert diese
zulässige Wiederholung desselben Runs und prüft die Producer-Versuche getrennt.
Die automatische PR-CI prüft daneben den vollständigen Diff gegen `dd56d310`.

| Vergleich | Original | CI2-C |
| --- | ---: | ---: |
| Buildjob | 1:52 | 1:42 |
| Chromiumjob einschließlich Setup/Upload | 40:46 | 5:43 |
| Summe Build + Chromium ohne Queue | **42:38** | **7:25** |
| Kritischer Pfad Buildstart → Browserende mit Zwischenqueue | 42:41 | 7:28 |
| Fälle | 33 | 9 |
| Exporte | 3 | 2 |
| Browserstarts | 8 | 6 |
| PNG erzeugt / geliefert | 65 / 60 | 12 / 12 |

Das Acht-Minuten-Ziel für Build plus Chromium ist erreicht (35:13 weniger,
82,6 % kürzer). Dies ist ein konkreter Lauf, keine Garantie gegen Runnervarianz.
Die beiden Messungen verwenden gleiche OS-Familie, Browser-/Playwright-/Godot-
Versionen, Software-WebGL, frische Gruppenprofile und denselben ausschließlich
hashgeprüften Downloadcache. Auch im neuen Joblog steht Image `20261012.334.1`,
im neuen JSON `20261023.334.3`; die oben erklärte Diskrepanz betrifft beide.
Keine Browserergebnisse oder Spielstände wurden aus einem Cache übernommen.

Die Retry-API nennt `run_started_at=16:28:07` und `created_at=16:28:09` UTC;
bis zum Buildstart 16:28:14 liegen damit 7 beziehungsweise 5 s. Eine eindeutig
abgetrennte reine Initialqueue liefert diese widersprüchliche Reihenfolge nicht.
Build 16:28:14–16:29:56: Checkout 15 s, Cache-Restore 9 s,
zwei tatsächliche Bauten 54 s, übrige Bindung/Installation/Transfers/Cleanup 24 s.
Browserstart nach 3 s Queue um 16:29:59, Ende 16:35:42:
63 s Setup einschließlich Checkout, Builddownload und Browserinstallation;
276 s Ausführung einschließlich Originalpixelgate; 4 s Upload/Cleanup.
Anschließend 3 s Gatequeue und 20 s `ci-required`; Buildstart bis Gateende
16:36:05 ergibt 7:51. Die 45 s docs-Prüfung aus Versuch 1 und dessen gescheiterter
Build sind getrennte Vorgänge, keine versteckte Verkürzung dieses Messpfads.
Die abschließende frische Ausführung am Berichtcommit wird in PR #421 gebunden.

### Gruppen und neue Fälle

| Gruppe | Original s | CI2-C s |
| --- | ---: | ---: |
| regular | 15.476 | 12.968 |
| catalog | 967.122 | 36.135 |
| input | 145.479 | 48.699 |
| completion | 548.695 | 79.715 |
| persistence | 627.700 | 89.880 |

| Fall | s | Browserstarts | PNG erzeugt/geliefert | Navigation n / s | Abfragen n / s | Warten n / s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| regular-start | 12.157 | 1 | 1/1 | 1 / 0.045 | 3 / 0.360 | 2 / 8.580 |
| C01 | 35.406 | 1 | 4/4 | 1 / 0.050 | 44 / 4.910 | 40 / 11.877 |
| C02 | 34.650 | 1 | 1/1 | 1 / 0.043 | 28 / 2.285 | 18 / 18.600 |
| C03 | 13.460 | 0 | 0/0 | 0 / 0.000 | 27 / 1.795 | 28 / 5.046 |
| C04 | 78.809 | 1 | 5/5 | 1 / 0.042 | 76 / 7.075 | 34 / 20.615 |
| C05 | 9.321 | 1 | 0/0 | 3 / 0.176 | 10 / 0.375 | 11 / 8.338 |
| C06 | 36.277 | 0 | 0/0 | 1 / 0.269 | 25 / 2.277 | 19 / 23.081 |
| C07 | 16.305 | 1 | 0/0 | 1 / 0.028 | 11 / 0.986 | 12 / 12.689 |
| C08 | 27.010 | 0 | 1/1 | 1 / 0.229 | 12 / 0.880 | 11 / 19.180 |

Die fünf abschließenden Teardowns brauchen zusammen 0,176 s. Die explizite
Schließung vor dem Prozessneustart ist in C07 enthalten. Elf Screenshots und ein
direkter PNG-Schreibvorgang des echten Übergangsframes ergeben zwölf Dateien;
kein Bildname wird im Erfolgsweg erneut geschrieben.

### Operationssummen

| Operation | Original n / s | CI2-C n / s |
| --- | ---: | ---: |
| `start` | 8 / 1.026 | 6 / 1.908 |
| `shutdown` | 10 / 0.297 | 6 / 0.216 |
| `navigation` | 19 / 2.700 | 10 / 0.882 |
| `query` | 115 / 14.228 | 43 / 3.467 |
| `state` | 1099 / 141.569 | 193 / 17.477 |
| `wait` | 937 / 388.454 | 147 / 73.603 |
| `save_confirmation` | 119 / 350.869 | 28 / 54.402 |
| `viewport` | 84 / 11.150 | 14 / 1.620 |
| `input` | 1045 / 914.376 | 162 / 46.840 |
| `screenshot` | 62 / 117.316 | 11 / 14.906 |
| `image_write` | 3 / unbekannt | 1 / 0.000343 |

Die `state`-Antworten sinken von 1.839.502 auf 370.958 übertragene JSON-Bytes.
Historische zehn `close`-Aufrufe enthielten redundante Schließungen; sie bedeuten
keine zehn Starts. Aktuell sind es sechs Starts und sechs Schließungen.

### Korrekturschleifen

- [Run 40354200914](https://github.com/venomenon328/picross/actions/runs/40354200914)
  stoppte vor jedem Browserstart in einem synthetischen Auswahltest. Dessen
  temporärer Git-Checkout erbte das echte Dispatch-Environment, obwohl sein
  CLI-Aufruf absichtlich keinen Browser anforderte. Nur dieser Testsubprozess
  erhält nun kein `GITHUB_*`-Environment; der Originaleventschutz bleibt unverändert.
- [Run 40354523189](https://github.com/venomenon328/picross/actions/runs/40354523189)
  auf `d23e0f18bf8b57bdbd570080c20ed60605ab5bb0` bestand Start, Katalog und Abschluss,
  scheiterte aber nach UI125/1280 am offscreen liegenden Katalogblatt und danach
  am Joblimit. Das Gate wies den unvollständigen Lauf zurück. Kein T01-Erfolg.
  C03 nutzt jetzt den direkten Menü-/Rückweg in der Arbeitsansicht. Der verdiente
  Katalog-/Hoverbeleg verwendet den echten C04-Abschluss, statt dass C01 dasselbe
  kleine Rätsel nochmals öffnet und löst. Originalpixelgate und zwölf Bilder bleiben.
- [Run 40356997281](https://github.com/venomenon328/picross/actions/runs/40356997281)
  auf `56ef8160e975f8d183816aa7b73331a41079837b` bestand acht Fälle, brach aber beim
  Aufheben der IndexedDB-Fehlerinjektion ab: Playwright rief den Funktionswert
  des Zuweisungsausdrucks ohne Receiver auf (`Illegal invocation`). Die
  Wiederherstellung verwendet nun eine explizite Funktion ohne Rückgabewert.
  Die gemessenen 7:35 einschließlich Build sind kein vollständiger T01-Erfolg.
- [Run 40358707608, Versuch 1](https://github.com/venomenon328/picross/actions/runs/40358707608/attempts/1)
  stoppte beim zweiten Build wegen HTTP 403 / GitHub-API-Ratelimit vor jedem
  Browserstart. Die vorhandene Release-Metadatenabfrage unterstützt bereits
  `GITHUB_TOKEN`; der Webbuild erhält nun den kurzlebigen Workflowtoken mit
  unveränderten `contents: read`-Rechten. Hash-/Releaseprüfung bleibt erhalten.
- [Run 40362312688](https://github.com/venomenon328/picross/actions/runs/40362312688)
  auf `e4c36ef7f8da4d590e3abc730f7347f7fecd745b` bestand alle neun Fälle,
  zwölf Originalbilder und das Gate, überschritt jedoch mit Build 2:28 plus
  Chromium 6:55 = **9:23** das Zeitziel. Damit war T01 nicht abgeschlossen.
  Kritischer Browserpfad mit 2 s Zwischenqueue: 9:25; Initialqueue 6 s,
  docs 47 s und anschließend 3 s Buildqueue sind getrennt. Cache-Restore 42 s
  statt 9 s; tatsächliche Bauten 60 s. Browser-Setup 43 s, Ausführung mit
  Pixelgate 369 s und Upload/Cleanup 3 s. Alle Gruppen waren langsamer:
  14,934 / 46,959 / 64,390 / 107,944 / 120,163 s. Die Operationsmengen waren
  identisch zur obigen Messung, die Laufzeiten jedoch höher.
  [Originale](https://github.com/venomenon328/picross/actions/runs/40362312688/artifacts/12669916372)
  bleiben als Gegenbeleg erhalten.
  Die Auswertung zeigte zusätzlich wiederholte Locator-/Probe-Abfragen derselben
  Canvas-Geometrie, allein fünf pro Bildstichprobe. Die Nacharbeit liest echte
  DOM-Grenzen und Godot-Koordinaten in einem gemeinsamen lesenden Aufruf;
  die fünf Bildpunkte verwenden jeweils denselben Geometriestand. Zellkoordinaten
  kommen ebenfalls aus einem aktuellen gemeinsamen Snapshot. Kein Zustand wird
  gesetzt, keine Eingabe zusammengezogen und kein Speicher-/Animationswarten
  verkürzt. Die abschließende frische Messung dieses Deltas wird im PR gebunden;
  bis zu ihrem Erfolg einschließlich Acht-Minuten-Ziel bleibt der Zeitbefund offen.

## T01

### Prüfzuordnung und Aussagegrenzen

| Pflicht | Ausführender Nachweis und Gegenprobe |
| --- | --- |
| Browserfreier Default, ausdrücklicher Auftrag | `test_ci2_a.py`/`test_ci_a.py`: Originalevent, Scheduler, vollständiger Diff und Scope-Abgleich; `test_ci2_c.py`: neun Fälle bei short/all, Export nie implizit. Automatischer PR-Lauf muss Web überspringen und alle ausgewählten Nichtbrowserjobs bestehen. |
| Nur benötigte Exporte | `test_ci2_c.py` führt die tatsächlichen Workflow-Shellzweige mit einem Befehlsrecorder aus: 1/2/3 Builds, Fehlerexit 23 bleibt Fehler. Gate verwirft fehlende/zusätzliche Exporte und identische IDs/Bauzeiten der beiden Exportwechselbauten. Das sind Auswahlgegenproben, keine ersetzten echten Builds. |
| Tatsächliche eindeutige Fallausführung | Producer akzeptiert jeden deklarierten Fall genau einmal; Gate gleicht IDs, PASS-Log, Timings und Originalbericht ab. Leere/fehlende/doppelte/falsche Logs scheitern selbst nach Neuberechnung des Dateihashes. Fehlgeschlagene Gruppen verhindern Erfolg. |
| Originalbelege und Bindung | `test_ci_b.py` und `test_at_evidence.py`: manipulierte Quellen, Runs, Versuche, Manifeste, Originaldateien und Pixel sowie fehlende Matrixzeilen scheitern. Ein fertiger Frame darf kein Zwischenframe sein; deckendes Weiß, Loch und weicher Alpha bleiben getrennte Stichproben. |
| Echte Browserübergänge | C02/C03 verwenden Maus/Tastatur und tatsächliche Resize-/DPI-Wechsel; C04 löst das feste 5×5-Rätsel durch einen Strich und beobachtet den natürlichen Übergang. C05–C08 verwenden echte Locks, IndexedDB, Reload, geschlossenen/neuen Browserprozess und Retry. Kein setterbasierter Ersatz dieser Übergänge. |
| Fremde Saves und seltene Varianten | C04 vergleicht die fremden Savebytes nach Reset; bestehende native Session-/Recovery-/Revisionsfälle und `kat2_probe.gd` bleiben erhalten. `ku_b_cases.gd` behält Sortierung/Gleichstände, HZ-/VS2-Fälle behalten Schrift-/Popup-/Geometriegrenzen. Keine Kürzung nativer Historien oder Bildmatrizen. |
| Günstiger Bridgevertrag | Fünf Node-Fälle führen die unveränderte `game/web/storage.js` mit synthetischen FS-Callbacks aus: fehlende Persistenz, Generation/Ansichtspending, Fehler/Retry, Slotfehlerisolation sowie Präferenz-/Savequeue. Diese Fälle behaupten ausdrücklich keine reale IndexedDB-Sicherung. |

Der normale Katalog wird einmal geprüft, die verdiente Karte nutzt den bereits
erspielten Abschluss von C04. HZ-C-Rückwechsel liefert Zustandsmessungen ohne
erneute Bilder. Das optionale Profil `export` ist auf regular-start/E01 begrenzt
(vier PNGs, drei echte Exporte, Ziel unter zehn Minuten einschließlich Build).
Es wurde im Auftrag dieses kurzen T01 nicht als zusätzlicher Browserlauf gestartet;
sein Laufzeitziel ist damit kein aktueller Messbeleg. Auswahl, unterschiedliche
Exportidentitäten und Originalbildgate sind durch gezielte Gegenproben abgesichert.

### Ausführung

Lokale Werkzeugprüfung: 225 Tests, 48,321 s, erfolgreich; drei Linux-exklusive
Prüfungen hier übersprungen, anschließend in der erfolgreichen Linux-docs-Prüfung
ausgeführt. Enthalten sind tatsächliche
Workflow-Shellgegenproben für 1/2/3 benötigte Builds, Originaleventschutz,
Ausführungs-/Bild-/Quell-/Versuchsgegenproben und fünf günstige Mechanismusfälle
an der unveränderten JavaScript-Speicherbridge. Nach den Korrekturen sind die
betroffenen CI-B- (15), AT- (3) und CI2-C-Tests (5) erneut erfolgreich.
Syntaxprüfung, Diffprüfung und Dokumentprüfung am sauberen Quellarchiv bestanden.
Die heruntergeladenen erfolgreichen Browseroriginale wurden mit dem aktuellen
Ergebnis-/Originalpixelgate lokal erneut erfolgreich geprüft: neun Fälle,
Producer/Gate-Versuch 2, gebundene Originaldateien und PNG-Pixel.

Der oben gebundene kurze Chromiumlauf einschließlich Gate besteht. Der finale
Berichtcommit erhält einen frischen ausdrücklichen kurzen Dispatch und die
vollständige automatische PR-Pflicht-CI. Deren konkrete Head-/Test-Merge-/Runbindung
steht im [Draft-PR #421](https://github.com/venomenon328/picross/pull/421), damit
der Bericht seinen eigenen Commit nicht zirkulär referenzieren muss. T01 darf
erst nach beiden erfolgreichen finalen Gates und einer finalen Messung innerhalb
des Acht-Minuten-Ziels als vollständig übergeben gelten.

## Getrennter Selbstreview und Abnahme

Nach dem erfolgreichen kurzen Lauf wurde der tatsächliche vollständige Diff
gegen `main@dd56d310` in einem getrennten Selbstreview geprüft: Inventar und
Ausführung, Einzel-/Gesamtprofile, benötigte Bauten, Originalevent und Quellen-/
Versuchsbindung, Gategegenproben, Fehler-/Retrypfad, Originalbilder und Messzahlen
sowie sämtliche geänderten Einstiegstexte. Codebasis ist `310725d4`; der
abschließende Delta ergänzt diesen Bericht, den lesenden Workflowtoken und
entfernt den nach Leserabgleich unbenutzten alten AT-Matrixhelfer. Nach der
9:23-Gegenmessung wurden die gebündelten lesenden Geometrieabfragen separat
gegen die bisherigen DOM-/Godot-Koordinatenformeln geprüft; tatsächliche
Resize-/DPI-Zelltreffer und Originalbildpixel bleiben die ausführenden Gegenproben.

Ergebnis: keine offenen fachlichen/codebezogenen Befunde in diesem Diff;
der Zeitbefund aus 9:23 benötigt die oben verlangte finale erfolgreiche Messung.
Die neun Fälle sind tatsächliche Übergänge; keine 33er-Vereinigung unter neuen
Namen. C04 verwendet seinen eigenen kleinen Abschluss zusätzlich für Karte/Hover.
Spielcode, Animationstempo, Save-/Hostingverträge, native Matrix und reale Inhalte
sind im Diff unverändert. Negative/abgebrochene Versuche bleiben oben sichtbar;
der optionale Exportlauf wird nicht als gemessen ausgegeben. API-Queue- und
Imageabweichungen werden nicht durch erfundene Genauigkeit verdeckt.

Die zwölf Bilder des Korrekturstands `56ef8160` wurden einzeln angesehen;
der erfolgreiche Stand besitzt denselben Bildumfang und wurde zusätzlich am
Originalpixelgate geprüft. Das ist eine technische Belegsichtung, keine neue
persönliche UI-/Spielabnahme. Abschließende CI-/Headbestätigung erfolgt im PR.
Dieser Selbstreview ist keine unabhängige Zweitprüfung.
**CI2-C-R01 bleibt als separates qualifiziertes Review des finalen Heads vor Merge offen.**
Keine neue persönliche Spielabnahme allein durch diesen CI-Umbau.
