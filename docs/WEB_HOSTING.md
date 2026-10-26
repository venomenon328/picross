# WEB-1: Browserbuild und manuelles SSH-Deployment

Zusätzliche statische Entwicklungsfassung aus [#162](https://github.com/venomenon328/picross/issues/162).
Godot Standard 4.7.2-stable, Single-Thread, WebGL 2 und WebAssembly; Desktop mit
Maus in Chromium und Firefox. Windows, Regeln, Schema 1 und Savevalidierung
bleiben erhalten. Kein Backend, PWA, Cloudsave oder automatisches Deployment.
P1 enthält kein Audio; der Webstart verwendet deshalb Godots Dummy-Audiotreiber
und erzeugt keine unbenötigten Browser-Audiokontexte.
Technische Ergebnisse und Artefaktbindung stehen im zugehörigen Draft-PR.

## Freigegebene CI-Auswahl und Browsergruppen

Der freigegebene [CI2-Sollvertrag vom 26.10.2026](CI_SLIMMING.md),
[Gesamtissue #412](https://github.com/venomenon328/picross/issues/412), ersetzt
die automatische Browserpflicht, impliziten Browserrechte manueller Scopes und
die ungekürzte bisherige Fall-/Bildmatrix. CI2-A ist auf dem #413-Arbeitsbranch
implementiert; Auswahl und explizite
Dispatchinputs stehen in [CI_A_SELECTION](CI_A_SELECTION.md). CI2-C bleibt
unbegonnen. Am historischen Ausgangsstand `main@967314538df376a281020fb4c34f93f370a491df`
besteht die bisherige Chromiumroute weiter. Dieser Abschnitt dokumentiert das
freigegebene Ziel, keinen bereits verfügbaren kurzen CLI-Weg oder Laufzeitnachweis.

[CI2-A / #413](https://github.com/venomenon328/picross/issues/413) entfernt
Browserinstallation und Browserstart aus automatischen PR-/Push-Ereignissen.
`all`, `toolchain`, `runtime`, `visual`, `perf-b`, `production`, gemeinsame
Komponenten und unbekannte Pfade sind kein impliziter Browserauftrag. Nur ein
ausdrücklicher manueller Auftrag mit Quellstand und Prüfumfang startet Chromium;
auch wiederverwendbare Unterworkflows verlangen ihn. Kein Zeitplan oder
automatischer Nachlauf ergänzt die Browserprüfung. Firefox bleibt aus CI
ausgeschlossen; die bestehende Webentwicklungsfassung und ihre Spiel-/
Speicherverträge werden dadurch nicht geändert.

[CI2-C / #415](https://github.com/venomenon328/picross/issues/415) ersetzt die
33 bisherigen Szenarien durch ungefähr 8–10 aktuelle Kernfälle:

| Prüfzweck im kurzen Umfang | Erhaltener Nachweis |
| --- | --- |
| Regulärer Start | Echter uninstrumentierter Spielerexport und Browserstart. |
| Katalog und Sortierung | Aktuelle Auswahl-/Sortierwege und repräsentative Bedien-/Darstellungszustände. |
| Eingabe und Geometrie | Echte Bearbeitung mit Undo/Redo sowie relevanter Resize-/DPI-Wechsel. |
| Abschluss und Reset | Kleiner echter Abschluss mit bestehender Präsentation, Bestätigung und Reset. |
| Persistenz und Wiederaufnahme | Bestätigte IndexedDB-Sicherung, Reload und echter Browserprozessneustart. |
| Sperre und Speicherfehler | Zweittab/Sperre sowie sichtbarer Schreibfehler und erfolgreicher Retry. |

KU-/AT-/HZ-Schichten werden zu aktueller Katalog-/Bedienprüfung zusammengeführt.
Ein normaler Viewport wird ausführlich geprüft; weitere Größen benötigen eine
konkrete Geometrieaussage. Seltene aktuelle Varianten werden möglichst günstig
unterhalb des Browsers abgesichert. Kleine synthetische Voraussetzungen dürfen
teure Vorbereitungsdurchspiele ersetzen; Zustandssetter ersetzen keine geprüften
Benutzer-/Speicherübergänge. Zusätzliche Browserprofile verlangen eine ausdrückliche
Auswahl mit konkretem Zweck und begrenztem Fall-/Zeitumfang. Kein Default ergänzt
die alte Vollmatrix.

Der kurze Chromiumlauf einschließlich benötigtem Build soll höchstens acht
Minuten dauern, typischerweise fünf bis acht. Ein zusätzlich angefordertes Profil
bleibt unter zehn Minuten. Nur benötigte Builds werden erzeugt; ein angeforderter
Exportwechsel verwendet weiterhin zwei eigenständig erzeugte Exporte. Eine neue
Kennung desselben Builds ersetzt diesen Nachweis nicht. Optimierungen verkürzen
weder Produktanimationen noch funktionale Speicherzusagen; Überschreitungen
bleiben sichtbare Optimierungsbefunde.

Auswahl, Producer und Gate werden gemeinsam auf den neuen Umfang umgestellt.
Das Gate unterscheidet nicht angefordert, Erfolg, fehlend, übersprungen,
fehlgeschlagen und abgebrochen. Nur angeforderte Browserprüfung verlangt passende
Resultate. Für tatsächlich gewählte Fälle bleiben vollständige Originalberichte,
Pflichtdateien samt Hashes und die Quell-/Run-/Versuchsbindung verbindlich.
Fehlende, leere, doppelte, falsche oder übersprungene Pflichtresultate sind kein
Erfolg. Isolierte Profile und veränderliche Hostingbäume verhindern gegenseitige
Beeinflussung. Ein noch ausgewählter Altjob wird durch Überspringen nicht
rückwirkend erfolgreich.

Native Prüfung, Fachtests, Toolchain und SSH/HTTP folgen unabhängig ihrem
tatsächlichen Änderungsbezug. Der Zustellungsweg erhält sein benötigtes reguläres
Bündel und die bestehende SSH/HTTP-Referenz ohne Browserauftrag. Messungen trennen
Aufbau, Szenarien/Phasen, Jobdauer, kritischen Pfad und summierte Rechenzeit.
Die [CI-A-Auswahl](CI_A_SELECTION.md) und der
[CI-B-Gruppenvertrag](CI_B_BROWSER_GROUPS.md) halten die ausführbare Ausgangsbasis
und ihre Quellenbindungen fest; alte Logs dienen als Baseline, ohne alte Voll-
oder Browserläufe neu zu reproduzieren. Historische Abnahmen bleiben gebunden.
Windows-, Eigentümer-, Merge- und Livefreigaben bleiben getrennt.

## Build unter Windows/PowerShell

Python 3.11+, Netzwerkzugriff auf die gebundenen offiziellen Godot-Archive und
ein sauberer Checkout sind erforderlich. Der Cache enthält ausschließlich erneut
hashgeprüfte Downloads. Engine, Projektkopie und Benutzerprofil sind temporär.

```powershell
python tools/build_web_player.py --cache-dir "$env:TEMP/picross-p1-preflight-cache" --output-dir artifacts/web-player
```

Das Ausgabeverzeichnis muss leer sein. `build-manifest.json` bindet den tatsächlich
ausgecheckten Commit, Engine, UTC-Bauzeit, Version und jede ausgelieferte Datei
per SHA-256/Größe. CI checkt den Test-Merge aus; Head und Basis werden getrennt
im CI-Auswahlbericht geführt. HTML zeigt die Buildkennung. `--development`
kennzeichnet veränderte Arbeitsbäume ausdrücklich als nicht deploybar; `--test`
erstellt einen separaten technischen Spieler mit festen Fixtures und Beobachtung.
Diese Prüfkopie gehört nicht auf den Spielserver. Import-/Exportfehler sind fatal.
Der reguläre exportierte PCK wird mit der bestehenden externen Paketprüfung auf
Runtime-Katalog und unerlaubte technische Beigaben geprüft.
Der Windows-main-Build bleibt separat unverändert benutzbar.

Für die getrennte persönliche lokale Probe, ohne SSH oder Veröffentlichung:

```powershell
python tools/web_tests/serve.py --build artifacts/web-player --port 8000
```

`http://127.0.0.1:8000/` im Browser öffnen; mit Strg+C den lokalen Server beenden.
Für Wiederaufnahme denselben Browser, dasselbe Profil und denselben Port verwenden.
`index.html` nicht direkt als lokale Datei öffnen.

## Einmaliges Zielsetup (separater Liveauftrag)

Die Referenz ist POSIX/OpenSSH mit SFTP, `sh` und GNU-Coreutils (`mv -T`, `cp`,
`sha256sum`, `mkdir`, `rmdir`, `cat`, `cut`, `rm`, `wc`), `find`, `grep`, `sed`, `cmp`.
Keine Python-/Godot-/Dockerinstallation auf dem Ziel nötig. Der SSH-Benutzer
braucht Schreib-/Suchrechte ausschließlich im eigenen dedizierten Verzeichnis.
Ein vorhandener statischer HTTPS-Webserver muss dieses Verzeichnis ausliefern.
Die tatsächlich vorhandene VPS-Plattform ist noch nicht geprüft.

Der Betreiber legt beispielsweise `/srv/www/example/picross-web` an. Kein
Symlink im Zielpfad; letzter Pfadteil genau `picross-web`. In diesem Verzeichnis
liegt die normale Datei `.picross-web` mit genau `picross-web-v1` als Inhalt.
Das Skript installiert weder Serverprogramme noch TLS, Benutzer oder Rechte.
Hostschlüssel vorab über einen vertrauenswürdigen Weg prüfen und in die lokale
OpenSSH-Konfiguration aufnehmen. Die Prüfung wird niemals abgeschaltet.

Lokale, durch Git ignorierte `web-deploy.local.json` im Checkout erstellen:

```json
{
  "host": "picross-host",
  "user": "deploy-user",
  "port": 22,
  "root": "/srv/www/example/picross-web",
  "url": "https://example.invalid/picross/"
}
```

`host` darf ein vorhandener SSH-Alias sein; SSH-Agent/SSH-Konfiguration liefert
den Zugang. Optional zeigt `ssh_config` auf eine lokale OpenSSH-Konfigurationsdatei.
Keine Schlüssel, Passwörter oder echten Hostadressen in Repository/Build/PR aufnehmen.
Batchbetrieb fragt keine Passwörter ab. URL immer mit abschließendem `/`.
Sitewurzel und Unterpfad verwenden dieselben relativen Ressourcenpfade.

## Update, Dry-Run und Rollback

```powershell
python tools/deploy_web.py --build artifacts/web-player --dry-run
python tools/deploy_web.py --build artifacts/web-player
python tools/deploy_web.py --rollback "vorherige-build_id-aus-dem-Deployprotokoll"
```

Ein Update prüft das lokale Bundle vollständig, prüft lesend die Zielfähigkeiten,
erwirbt `.deploy-lock`, überträgt über SFTP in einen eigenen Stagingbereich,
vergleicht alle Hashes und aktiviert erst dann. Dry-Run verbindet sich zum
konfigurierten Ziel, schreibt aber keine Dateien. In #162 wird ausschließlich
die isolierte Referenz verwendet; kein Kontakt zum Eigentümer-VPS.
Beim Rollback den Platzhalter durch die vollständige frühere Buildkennung ersetzen.

Alle Dateien eines Exports liegen unter `releases/<build_id>/`. `index.html`
wird durch eine Umbenennung im selben Verzeichnis atomar ersetzt und referenziert
ausschließlich diese unveränderliche Version. Bereits geladene HTML-Seiten und
offene Tabs können weiterhin ihre ursprünglichen Ressourcen laden. Kein `current`
Symlink und keine automatische Versionsbereinigung. `.previous` hält die vorherige
Kennung; Versionen bleiben für expliziten Rollback erhalten. Die Ausgabe meldet
den aktiven Stand, nicht nur einen erfolgreichen Upload.

Fehler ergeben Exitcode 1; Erfolg und Dry-Run Exitcode 0. Vor Aktivierung bleibt
die alte Fassung aktiv. Bei fehlgeschlagenem HTTP-Abschlusscheck wird eine vorhandene
vorherige Fassung wieder aktiviert; beim allerersten Deployment gibt es keine
vorherige Version. Bei Verbindungsabbruch kann der aktive Stand zunächst unbekannt
sein: Verbindung wiederherstellen, Kennung der ausgelieferten Seite kontrollieren
und bei Bedarf den expliziten Rollback ausführen. Keine Erfolgsmeldung bei fehlendem
Abschlusscheck. HTTP-Integrität ersetzt keine Browser-Spielprobe.

Abgebrochene Uploads bleiben in `.staging-*` zur Diagnose. Eine nach hartem
Prozessabbruch verbliebene `.deploy-lock` wird bewusst nicht automatisch gestohlen.
Der Betreiber darf sie erst nach Feststellung, dass kein Deployment mehr läuft,
entfernen. Aufräumen alter Versionen erfordert eine eigene Aufbewahrungsentscheidung;
alte Tabs können diese weiterhin benötigen. Rollback ist kein Savebackup.

## Webserververtrag

- HTTPS; auf Loopback darf die isolierte Referenz HTTP verwenden.
- Einstieg `index.html`: `Content-Type: text/html`, `Cache-Control: no-cache`.
- `releases/`: `Cache-Control: public, max-age=31536000, immutable`.
- `.js`: `text/javascript` oder `application/javascript`; `.wasm`:
  `application/wasm`; `.pck`: `application/octet-stream`.
- Keine SPA-Fallbackseite für fehlende Ressourcen. Fehlende Dateien müssen 404
  ergeben. Verzeichnislisting abschalten; Punktdateien und `.staging-*` nicht
  öffentlich ausliefern. Nur Einstieg und `releases/` sind öffentliche Pfade.
- Optionale HTTP-Kompression muss den Inhalt unverändert übertragen und korrekte
  `Content-Encoding`-/`Vary`-Header setzen. Keine Umbenennung einzelner Exportdateien.
- Keine COOP-/COEP-Pflicht durch Threading; es wird ohne Threads exportiert.

Der Abschlusscheck lädt Einstieg und sämtliche manifestgebundenen Ressourcen,
prüft Hashes sowie MIME-/Cacheheader. Die Serverkonfiguration bleibt Betreiberaufgabe.

## Browserspeicher und Abnahmen

`user://p1/saves/` bleibt die einzige Saveplattform. Godots `/userfs`-IDBFS-Mount
speichert tatsächlich in IndexedDB am Browserorigin; Version/Assetpfad ist kein
Teil dieser Identität. Verschiedene Installationen auf demselben Origin teilen
den Speicher; unterschiedliche Origins/Profile sowie Windows bleiben getrennt.
Ein Web Lock wird vor dem Laden des Dateisystems gehalten. Ein zweiter Tab
startet nicht schreibend; nach Schließen der ersten Instanz kann neu geladen werden.
Beim Start darf die exklusive Anfrage bis zu drei Sekunden auf die Freigabe des
vorherigen Dokuments warten. Das berücksichtigt die verzögerte Sperrfreigabe beim
Firefox-Reload. Ohne Erwerb wird die Anfrage abgebrochen und die Zweittabmeldung
gezeigt; sie startet auch nach späterer Freigabe nicht im Hintergrund. Bis zum
Erwerb erfolgt kein IndexedDB-/Enginezugriff. Eine gehaltene Sperre wird weder
gestohlen noch vor dem Ende des besitzenden Dokuments freigegeben.
Die Browserprobe prüft verzögerte Freigabe mit zwei echten Dokumenten, blockierte
Zweittabs ohne Speicherzugriff und dauerhafte Entfernung abgebrochener Anfragen.
Grundlage ist das [Abbruchsignal der Web Locks API](https://www.w3.org/TR/web-locks/#dom-lockoptions-signal).

Bestätigte Aktionen schreiben sofort in den vorhandenen validierenden SaveStore.
Eine serialisierte Synchronisation bestätigt erst nach dem echten IDBFS-Callback
„Im Browser gespeichert“. Währenddessen zeigt die Kopfzeile „Speichern läuft …“;
bei Fehler bleibt ein sichtbarer Retryweg. Ansichtsänderungen werden bis zu
350 ms gebündelt. Fokus-/Sichtbarkeitswechsel fordern einen Flush an und verwerfen
Gesten. Die eigene Beenden-Aktion wartet auf Persistenz; bei Fehler bleibt sie
offen. Erfolg zeigt einen beendeten Zustand mit Neuladehinweis.

Technischer Diagnosebefund der gebundenen Engine: Firefox kann beim Engineabschluss
die Konsolenmeldung `Pages in use exist at exit in PagedAllocator` für
`WorkerThreadPool::Group` ausgeben, auch im regulären Export. Dieser Cleanupbefund
ist nicht behoben; die Nachweise führen ihn separat. Die Beenden-Prüfung verlangt
weiterhin Exitcode 0, abgeschlossene Sicherung und erfolgreiche Wiederaufnahme
per Reload. Andere Spiel-/Navigationsfehler sowie neue Fehler nach dem Reload
bleiben Testfehler. Eine Wiederverwendung der beendeten Engine innerhalb derselben
Seite ist nicht vorgesehen.

Zwischen bestätigter Aktion und abgeschlossener IndexedDB-Transaktion bleibt ein
asynchrones Verlustfenster; bei Ansichten zusätzlich die Bündelzeit. Abruptes
Tab-/Prozessschließen kann den letzten noch nicht bestätigten Stand verlieren.
Eine mögliche Browserwarnung ist ergänzend, keine garantierte Schließsperre.
Privatmodus, gelöschte Websitedaten und Speicherräumung durch den Browser können
Fortschritt entfernen. Inkompatible Definitionen/Revisionen werden weiterhin
abgewiesen; Recovery und Reset verlangen die bestehende bewusste Bestätigung.

Technische Prüfung WEB-T01 gehört vor die Übergabe. WEB-M01 ist die persönliche
Eigentümerprobe vor Freigabe als nutzbarer Testzugang: links/rechts/mittig,
lange Hinweise, Zoom/Fenstergröße, Teilstand, Reload und erneuter Browserstart.
WEB-D01 prüft vor erstem Live-Deployment tatsächliches Zielsystem, Benutzer,
Hostschlüssel, Pfad, URL/TLS und öffentliche oder geschützte Auslieferung.
Persönliche Probe, Mergefreigabe und Live-Deployment bleiben separate Aufträge.
