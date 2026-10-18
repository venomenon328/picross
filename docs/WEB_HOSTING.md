# WEB-1: Browserbuild und manuelles SSH-Deployment

Zusätzliche statische Entwicklungsfassung aus [#162](https://github.com/venomenon328/picross/issues/162).
Godot Standard 4.7.2-stable, Single-Thread, WebGL 2 und WebAssembly; Desktop mit
Maus in Chromium und Firefox. Windows, Regeln, Schema 1 und Savevalidierung
bleiben erhalten. Kein Backend, PWA, Cloudsave oder automatisches Deployment.
P1 enthält kein Audio; der Webstart verwendet deshalb Godots Dummy-Audiotreiber
und erzeugt keine unbenötigten Browser-Audiokontexte.
Technische Ergebnisse und Artefaktbindung stehen im zugehörigen Draft-PR.

## Freigegebene CI-Auswahl und Browsergruppen

Die Eigentümerentscheidung vom 18.10.2026 in
[CI-Policy](CI_POLICY.md) / [#246](https://github.com/venomenon328/picross/issues/246)
ist ein gestufter Sollvertrag, **noch keine Implementierung oder Livefreigabe**.
Vor Integration des jeweiligen Pakets gelten die vorhandenen ausgewählten
Pflichtchecks weiter.

[CI-A (#247)](https://github.com/venomenon328/picross/issues/247) ersetzt die
pauschale Product→Browser→SSH-Kopplung durch Auswahl nach tatsächlichen
Abhängigkeiten. Reine Fachwerkzeuge und die einzelne PR-Vorlage können Web
vermeiden. Reine Deploy-/SSH-/HTTP-Arbeit erhält einen eigenständig ausführbaren
Referenzpfad ohne Browserinstallation/-start oder unnötige technische Exporte;
ein dafür benötigtes reguläres Bündel wird weiterhin tatsächlich gebaut.
Gemeinsame Export-/Hostingverträge wählen beide Bereiche. Bis CI-B bleibt
jede weiterhin ausgewählte Browserroute vollständig, einschließlich regulärem
Start und aller aktuellen positiven/negativen Szenarien beider Browser.

Erst nach [CI-B (#248)](https://github.com/venomenon328/picross/issues/248) gilt:

| Unabhängig startbare Gruppe | Prüfzweck |
| --- | --- |
| Regulärer Start | Uninstrumentierter Spielerexport und vorhandener Startvertrag in beiden Browsern. |
| Katalog/Darstellung | Aktuelle Katalog-/Metadatenzustände und geforderte Darstellungsbelege. |
| Eingabe/Geometrie | Echte Zeiger-/Gestenereignisse und relevante Zoom-/Fensterfälle. |
| Abschluss/Reset | Tatsächlicher Abschluss, Präsentation, Abbruch, Bestätigung und Reset. |
| Persistenz/Lifecycle | Echte Sicherung, Reload, Prozessneustart, Exportwechsel, Sperren, Fehler/Recovery, Offline und Beenden. |

Normale Runtime-/Darstellungsänderungen wählen regulären Start und die betroffenen
Gruppen in Chromium und Firefox; gemeinsame UI-/Save-/Export-/Harnessabhängigkeiten
wählen mehrere oder alle Gruppen. Insbesondere `game/ui/main.gd` ist keine
Katalogausnahme. Unbekannte Wirkung wird umfassend geprüft, manuelle Auswahl
erweitert ausschließlich. Vollständige Browserabdeckung ist die Vereinigung aller
Gruppen; die unabhängige SSH-Referenz folgt ihrem eigenen Änderungsbezug.

Vor der Trennung erhält jede aktive positive/negative Aussage einschließlich
technischem Start und Pflichtbelegen eine eindeutige Zuordnung. Jede Gruppe
richtet kontrollierte kleine synthetische Voraussetzungen selbst ein; sie hängt
nicht vom Durchlaufen einer anderen Gruppe ab. Reale Zeigereingabe, bestätigte
IndexedDB-Schreibstände, Reload und Neustart eines Browserprozesses bleiben dort
erforderlich, wo diese Übergänge geprüft werden. Der Versionswechsel verwendet
weiterhin zwei eigenständig erzeugte Exporte. Vorbefüllte Daten, ein anderer
Identifikator desselben Builds oder alleiniger Start ersetzen diese Belege nicht.

Chromium und Firefox laufen auf getrennten Runnern aus auf denselben geprüften
Quellstand gebundenen Builds. Eigene Profile, Ports, veränderliche Hosting- und
Releaseverzeichnisse, Reports und Artefaktnamen verhindern Überschneidungen:
Die Referenz verändert unter anderem Einstieg, Releasezuordnung und Unterpfad.
Beide Browser liefern ihre erforderlichen Szenarien; ausdrücklich browserspezifische
Fälle wie die Chromium-DPI-Prüfung bleiben erkennbar. Das Ergebnisgate kontrolliert
erwartete und tatsächlich gelieferte Gruppen, Szenarien und Belege je Browser;
fehlende, leere, doppelte oder falsche Pflichtresultate sind kein Erfolg.

Messungen trennen je Szenario Start/Navigation, Zustandsabfragen, Eingaben,
Save/Bestätigung, Wartephasen und Screenshots. Optimierungen beheben gemessenen
vermeidbaren Harnessaufwand; sie verkürzen weder Animationen noch Speicherzusagen.
Vergleichsbedingungen und tatsächliche Wirkung werden im Paket-PR dokumentiert,
ohne feste Laufzeit-/Bytebudgets. Windows-, Eigentümer- und Livegates bleiben
getrennt; die KU-Verhaltensnachweise aus #244 werden nicht durch Startproben ersetzt.

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
