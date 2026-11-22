# WEB-1: Browserbuild und manuelles SSH-Deployment

Dokument-ID: `web-hosting`
Status: `active`
Zuständigkeit: Browserpersistenz, Build, Zielvoraussetzungen, manueller
SSH-Deploy und Rollback. Die Toolchainversion steht im [Projektprofil](../PROJECT_PROFILE.md),
Browserprüfungen ausschließlich im [Chromiumvertrag](../ci/CI_B_BROWSER_GROUPS.md).

## K-B: Fortsetzen-Metadaten

[Paketentscheidung #485](https://github.com/venomenon328/picross/issues/485#issuecomment-6705799391).
Der Merker wird erst nach bestehender WebLock-/Hydrationsgrenze aus `user://p1`
geladen. Es gibt keinen neuen Backend-, Lock- oder Speicherpfad. Die vorhandene
serialisierte FS.syncfs-Schlange transportiert eigene recentGeneration/recentSaved-
Zähler, Pending, Error und Retry. Nur der tatsächliche zugehörige Callback bestätigt
seine Generation; ein älterer Callback, ein Slot-/Sortierungserfolg oder eine
Startausnahme bestätigt keinen neueren Merker. Das Browserlabel zeigt auch ausstehende
Merker; Savefehler behalten Vorrang. Blur/Visibility und Retry versuchen ausstehende
Metadaten erneut. Beenden wartet begrenzt auf deren Callback, ein reiner Merkerfehler
blockiert aber keinen erfolgreich gesicherten Spielstand. Das bestehende abrupte
Verlustfenster bleibt. Die Node-Mechanismusprobe ist kein echter IndexedDB-Nachweis:
Tatsächliche Browsernachweise und Abnahmen stehen im jeweiligen Auftrag.

**B-B / #498:** Der reguläre Webexport startet denselben [Buchroot](../game/BOOK_INTEGRATION.md)
wie Windows. Produkt-HTML, Appidentität, IndexedDB-/Lock-/Retrywege bleiben erhalten.
Die technische Beobachtung erweitert diesen Root; die persistenzlose Studienshell
ist kein Webspielernachweis. Die damaligen Einführungsnachweise stehen in [B-B-T01](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/B_B_VERIFICATION.md).

Zusätzliche statische Entwicklungsfassung aus [#162](https://github.com/venomenon328/picross/issues/162).
Gebundene Godot-Standard-Toolchain, Single-Thread, WebGL 2 und WebAssembly; Desktop mit
Maus in Chromium und Firefox. Windows, Regeln, Schema 1 und Savevalidierung
bleiben erhalten. Der gelieferte WEB-1-Weg ist statisch, ohne Backend, PWA oder
Cloudsave und ohne automatisches Deployment. Der zusätzliche optionale
[SYNC-Dienst](../game/SAVE_SYNC.md) ist als Soll freigegeben, noch nicht geliefert.
Seine spätere Kontoanbindung ergänzt diesen Webweg; kontolose Browserpersistenz
und statisches Deployment bleiben bestehen. Lieferstatus: [#821](https://github.com/venomenon328/picross/issues/821).
P1 enthält kein Audio; der Webstart verwendet deshalb Godots Dummy-Audiotreiber
und erzeugt keine unbenötigten Browser-Audiokontexte.
Technische Ergebnisse und Artefaktbindung stehen im jeweils tatsächlich geprüften PR.

## Aktuelle CI-Auswahl und kurzer Browserauftrag

[Workflow v2](../ci/CI_WORKFLOW_V2.md) bestimmt die automatische Package-CI.
[CI-B](../ci/CI_B_BROWSER_GROUPS.md) definiert vollständig Browserfälle, Exporte,
Quellenbindung und Nachweisgrenzen; diese werden hier nicht erneut festgelegt.
Ein ausdrücklich beauftragter kurzer Browserlauf startet auf dem gebundenen
Arbeitsbranch mit:

```sh
gh workflow run ci-chromium.yml --ref <arbeitsbranch> -f scope=auto -f browser_scope=short
```

Ein Branchdispatch prüft seinen Quellhead und ist kein PR-Test-Merge-Nachweis.
SSH-/HTTP-Integrität und persönliche Produktabnahme bleiben eigenständige Aussagen.

## Build unter Windows/PowerShell

Python 3.11+, Netzwerkzugriff auf die gebundenen offiziellen Godot-Archive und
ein sauberer Checkout sind erforderlich. Der Cache enthält ausschließlich erneut
hashgeprüfte Downloads. Engine, Projektkopie und Benutzerprofil sind temporär.

```powershell
python tools/build_web_player.py --cache-dir "$env:TEMP/picross-p1-preflight-cache" --output-dir artifacts/web-player
```

Das Ausgabeverzeichnis muss leer sein. `build-manifest.json` bindet den tatsächlich
ausgecheckten Commit, Engine, UTC-Bauzeit, Version und jede ausgelieferte Datei
per SHA-256/Größe. Package CI prüft bei PRs den zugehörigen Test-Merge;
ein manueller Browserdispatch prüft seinen Branchcommit. Head, Basis und Checkout
werden getrennt im jeweiligen Ergebnis geführt. HTML zeigt die Buildkennung. `--development`
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
konfigurierten Ziel, schreibt aber keine Dateien. Ein Test der isolierten Referenz ist kein Nachweis für ein tatsächliches Liveziel.
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

`user://p1/saves/` ist der bisherige kontolose Speicherroot. Die hier beschriebene
gelieferte Fassung speichert ausschließlich lokal. Zusätzliche Kontoprofile und
Serversynchronisierung folgen erst dem [SYNC-Vertrag](../game/SAVE_SYNC.md);
sie ersetzen weder diesen Gaststand noch die bestätigte lokale Persistenz.
Godots `/userfs`-IDBFS-Mount
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
Fortschritt entfernen. Savevalidierung und Recovery folgen [P1](../game/PROTOTYPE_P1.md); der automatische
Neustart eindeutig älterer Rasterrevisionen folgt [PE §9.3](../tools/PUZZLE_EDITOR.md#93-sicherer-automatischer-save-neustart).
Unlesbare, fremde oder höhere Revisionen werden nicht automatisch zurückgesetzt.

WEB-T01 ist der historische technische Einführungsnachweis aus
[#162](https://github.com/venomenon328/picross/issues/162); aktuelle technische
Prüfauswahl folgt dem CI-Workflow und CI-B. WEB-M01 bezeichnet die getrennte
persönliche Eigentümerprobe vor Freigabe als nutzbarer Testzugang: links/rechts/mittig,
lange Hinweise, Zoom/Fenstergröße, Teilstand, Reload und erneuter Browserstart.
WEB-D01 prüft vor erstem Live-Deployment tatsächliches Zielsystem, Benutzer,
Hostschlüssel, Pfad, URL/TLS und öffentliche oder geschützte Auslieferung.
Persönliche Probe, Mergefreigabe und Live-Deployment bleiben separate Aufträge.

