# PW: Automatisierte App-Releases und Selbstupdate

**Beschlossener Sollvertrag · 12.11.2026 · [Issue #612](https://github.com/venomenon328/picross/issues/612).**
Verbindliche erste [Paketentscheidung APP-A](https://github.com/venomenon328/picross/issues/612#issuecomment-6834815644).
**APP-A ist im Arbeitsbranch implementiert; Integration, unabhängiges Review und
Liveaktivierung sind noch offen.** Der separate
[`pw-installer.yml`](../.github/workflows/pw-installer.yml) plant automatische
Versionen und prüft echte Installer. Veröffentlichung bleibt ohne die gesondert
freigegebene Repositoryvariable `PW_RELEASE_ENABLED=true` gesperrt.
**APP-B ist nicht implementiert.** Der Launcher prüft und installiert keine Updates.
Dieser Vertrag ersetzt **nicht rückwirkend** die P4-Liefernachweise aus
[#588](https://github.com/venomenon328/picross/issues/588).

## 1. Autorität und Grenzen

Der Windows-Produktionsassistent bleibt eine installierte lokale Anwendung mit
fester vertrauenswürdiger Python-/Reader-/UI-Laufzeit und eigenen Zustandsdaten.
Ein `main`-Commit oder eine Gitdatenaktualisierung ist **kein** installierbares
Update. Nur eine erfolgreich verifizierte, veröffentlichte höhere **Appversion**
kann zur Aktualisierung dienen. Game-Export, Inhalts-/Bildproduktion, Godot,
das eigenständige Entwicklungs-HTML und Produktionsbranches bleiben außerhalb.

- **APP-A (zuerst):** payloadgenaue Änderungserkennung, automatische
  Produktversionsvergabe, unabhängiger Windows-MSI-Bau und dauerhafter
  GitHub-Releasekanal. Noch **kein** Downloader/Updater im installierten Launcher.
- **APP-B (danach):** signierte Updatekanalinformation, Prüfung beim Start,
  einmalige Zustimmung zu automatischen Updates, sicherer externer MSI-Updatehelfer,
  geordneter Neustart und echte Windows-Lebenszyklusabnahme.
- Der vorhandene Launcher **0.1.0** besitzt keine Updatefähigkeit.
  Der erste updaterfähige Installer wird einmalig manuell installiert.
  Keine Migration oder stille Veränderung der alten 0.1.0-Installation durch APP-A.

## 2. APP-A · Buildauswahl, Version, Veröffentlichung

Eine **eigene** Release-Pipeline, nicht Teil von `Package CI`, darf nach einer
tatsächlich **erfolgreichen Package-CI für einen Main-Push** ausgelöst werden.
Ein isolierter `workflow_run`-Folgetrigger ist durch #612 ausdrücklich
zugelassen und ersetzt insoweit die alte P4-Beschränkung auf
`workflow_dispatch`. Erfolg einer PR, eines Forks, eines Dispatches oder
eines anderen Repositories ist kein Releaseauslöser. Der Publisher prüft
die Identität des Quellereignisses, erfolgreiche Pflichtchecks, den vollständigen
Main-Sourcecommit und den aktuellen Mainzustand erneut. Nur der dedizierte
Publisher erhält `contents:write`; Prüf-/PR-Code erhält kein Release-Schreibrecht.

Die günstige Vorprüfung berechnet einen **deterministischen Payload-Fingerprint**
aus den geprüften, sortierten Inputdateien samt Pfad, Dateiinhalt und relevanten
Modi. Er deckt die tatsächlichen PyInstaller-/MSI-Quellen ab, insbesondere
eingebundene Python-/Produktionsreader, UI, fremde verwendete Runtime-Ressourcen,
Installer-/Buildcode, C#-Guard, Pins, Lizenzen, Icon und mitgelieferte Anleitung.
Das Inputinventar wird gegen tatsächliche Packageinputs/Collector-Konfiguration
abgesichert. Nicht sicher klassifizierbare neue Inputs sind kein Freipass zum
Überspringen. Der Fingerprint ignoriert ausdrücklich **nicht** eine mitgepackte
Datei, nur weil sie technisch in einem anderen Verzeichnis liegt.

Unverändertes Payload bedeutet kein MSI-Neubau, keine neue Version und keinen
weiteren Release – selbst wenn `main` wegen Rätseln, Spiel, CI oder gewöhnlicher
nicht ausgelieferter Dokumente fortgeschritten ist. Gemischte Diffs mit
relevanten Dateien sind relevant.

Die **zuletzt gültig veröffentlichte PW-Releaseversion** und ihr
Fingerprint sind die automatische monotone Veröffentlichungsautorität;
`release.json` bleibt Paketierungs-/Upgradeidentitäts- und
**0.1.0-Startanker**, ist aber nach APP-A nicht mehr die bei jedem neuen Build
manuell hochzuzählende Produktversionsquelle. Bei neuem Fingerprint wird
standardmäßig exakt die nächste Patchversion veröffentlicht (z. B. 0.1.1).
Das veröffentlichte Versions- und Produktidentitätsmerkmal muss konsistent
in MSI, EXE, Manifest, Dateiname und `delivery.json` verwendet werden,
ohne den gepinnten sauberen `main`-Quellcheckout zu verändern oder automatisch
einen Versionscommit nach `main` zu schreiben. Fester UpgradeCode; neuer
passender ProductCode; Same-Version-Übernahme und Downgrade bleiben gesperrt.
Die 0.1.0-Auslieferung war ein tatsächlich geprüfter **Actions-Download**,
kein vorhandener GitHub Release. Einen historischen Release nicht erfinden.

Vor Sichtbarkeit eines neuen Releases wird ein vollständiger Build auf
fixiertem Commit mit dem vorhandenen
[`verify_installer.py`](../tools/production_workspace/verify_installer.py)
gegen reale MSI-/Payload-/Lizenz-/Versions-/Hashbytes geprüft. Der Hosted
Windows Server bleibt für unprivilegierte MSI-Installationen ungeeignet
(Policy 1625); erfolgreiche Paketinspektion ist keine echte Installation.

Ein veröffentlichter, dauerhaft abrufbarer GitHub Release `pw-vX.Y.Z`
enthält MSI, `.sha256`, knappe Anleitung, `delivery.json` und ein
kanonisches maschinenlesbares Manifest mindestens mit Version,
Repository, vollständiger Quell-SHA, Payload-Fingerprint, Paketname,
Byteumfang und SHA-256. Eine neue Version darf nicht sichtbar sein,
bevor der vollständige Kandidat erfolgreich geprüft ist. Fehlgeschlagene
Jobs, Teiluploads, Race Conditions und wiederholte gleiche Quellstände
erzeugen weder neue `latest`-Versionen noch überschreiben sie
Vorgänger-Assets. Bei zwischenzeitlich neuerem Main vor Veröffentlichung
frisch prüfen, ob die Lieferung noch zulässig ist; nie heimlich eine
ältere Version als aktuell positionieren.

Die **Veröffentlichung** selbst ist ein eigener Betriebs-/Aktivierungsschritt
nach Implementierungsreview und passend erteiltem Auftrag. Vorher nur isolierte
synthetische Release-API- und echte **nicht veröffentlichende** MSI-Bau-/Prüfproben.
Die Veröffentlichung darf nicht als bereits erfolgt gelten, weil der
Workflowcode gemergt wurde. APP-A stellt keinerlei automatische
Codeinstallation im Client bereit.

## 3. APP-B · Verifizierter Updateclient

Beim Programmstart wird für die *installierte Anwendung* ein veröffentlichter
Kanal geprüft, ohne die Verbindung zu Produktions-/Gitrefs als Codequelle zu
verwenden. Der Nutzer entscheidet einmalig über automatische Updates.
Danach sind bei neuerer geprüfter Version Download und kontrollierte
Aktualisierung möglich. Kein dauerhafter Dienst und keine spontane
Ausführung eines ungesicherten Branchstands.

Vor jeder automatischen MSI-Ausführung ist die Kanalbeschreibung
**kryptografisch signiert** und mit einer unabhängig in der Anwendung
verankerten Vertrauenswurzel geprüft; Asset-SHA-256, Bytezahl,
Version und Herkunft werden dagegen gebunden. Eine Hashliste aus demselben
ungeprüften HTTP-Endpoint allein genügt nicht. Den konkreten
Schlüsselbereitstellungs-/Rotations-/Widerrufsweg als Bestandteil der
APP-B-Paketentscheidung vor Implementation schließen, ohne Secrets zu
committen oder eine neue Signierungsbefugnis still anzunehmen.
Eine Metadatensignatur ist nicht automatisch eine Windows-Codesignatur
des MSI; SmartScreen und bestehende Plattformrichtlinien bleiben wirksam.

MSI-Ausführung nur durch einen kleinen externen Helfer nach kontrolliertem
Beenden aller zugehörigen Prozesse/Anfragen und laufenden
P2-Transaktionen; vorhandene Instanz-/Port-/Lock-/Restart-Manager-Guards
bleiben verbindlich. Kein harter Prozesskill, kein Downgrade, keine
Änderung am Datencheckout oder an Benutzerdateien. Nach Erfolg regulärer
Neustart; bei Download-/Kanalfehler normaler Start der bisherigen App,
bei Installationsfehler wahrheitsgemäßer Status und Erhalt des alten
Zustands. Keine funktionierende Rückabwicklung ohne echten Nachweis behaupten.

Konfiguration, Repository-/Remote-/Refwahl, Gitcache, Browserprofil,
lokaler Zustand, gespeicherter Port und Produktionsdaten bleiben wie
beim bisherigen Upgrade unter APP-B erhalten. Der erste Umstieg von
einem 0.1.0-Installer auf einen updaterfähigen Stand erfolgt einmalig
mit einem manuellen MSI.

## 4. Prüf- und Abnahmegrenzen

Für **APP-A** ist die [Paketentscheidung](https://github.com/venomenon328/picross/issues/612#issuecomment-6834815644) mit
K01–K10 und dortigem Prüfplan maßgeblich: schlanker `docs`-/`ci-required`-
Kern, begründet `tools`, einmalige echte Windows-MSI-Inspektion und
unabhängiges Review. Der neue Installerbau bleibt **außerhalb** des
regulären Spiel-Windowspakets und der normalen Zusatzmodule.
Ein tatsächlich publiziertes Release braucht eigene Rückdownload-/
Hash-/Quellprüfung nach dem freigegebenen Aktivierungsentscheid.

Für **APP-B** sind signierte Herkunft, echtes Windows-11-Upgrade,
Sicherheits-/Offline-/Abbruch-/Laufzeitfälle, geschützter Prozessstop,
erhaltener Zustand/Browserorigin und manuelle Erstinstallation gegen
den tatsächlichen Kandidaten nachzuweisen. Eine erfolgreiche Linuxprüfung
oder Hosted-Windows-Server-MSI-Inspektion ersetzt keinen echten Windowsstart
oder eine Installationsprobe. Unabhängige Reviews und tatsächliche
Nutzerabnahmen bleiben an einen konkreten Produkt-Head und Artefakte
gebunden; keine pauschal neue Kern-/Browserregression.

Bis zur jeweiligen Implementierung gilt die bestehende
[Windows-Start-/Buildanleitung](../tools/production_workspace/WINDOWS_BUILD.md).

## 5. APP-A-Ausführung und Recovery

[`payload.py`](../tools/production_workspace/payload.py) bildet die sortierten
committeten Gitdateien samt Gitmodus, Bytezahl und SHA-256 auf einen kanonischen
Fingerprint ab. Sämtliche eingesammelten Produktions-Pythonmodule, App-Reader,
UI, MSI-/Build-/Prüfcode, Pins, Guard, Lizenztexte, Icon und START sind Eingaben.
Explizite Ausnahmen sind nicht eingebaute Markdown-/Schema-/Kalibrierungsdateien,
CMD-Fallbackbau und manuelle Smokes. Neue Pythonmodule werden einbezogen;
unbekannte Ressourcen und nichtreguläre Modi stoppen die Vorprüfung. Änderungen
außerhalb dieser Eingaben (insbesondere Inhalt, Spiel und allgemeiner CI-Kern)
ändern den Fingerprint nicht. Der echte Bau gleicht die repositorybezogenen
Dateien aus `Analysis-00.toc` gegen `inputs.json` ab; ein nicht inventarisierter
eingefrorener Input oder abweichende Arbeitsbytes brechen den Bau ab.

[`release_channel.py`](../tools/production_workspace/release_channel.py) liest
den letzten gültigen veröffentlichten `pw-v0.1.x`-Release samt kanonischem
`manifest.json` und lädt dessen gebundene Assets binär zurück. Unvollständige
oder fremde veröffentlichte PW-Einträge sind Fehler, keine neue Startlinie.
Gleicher Fingerprint ist No-op; andernfalls folgt genau Patch +1 ab 0.1.0.
`--version` injiziert die geplante Version in den vorhandenen Builder und Inspector,
ohne `release.json` oder den Sourcecheckout zu verändern. ProductCode bleibt
deterministisch je Version, UpgradeCode bleibt gleich. Der Inspector prüft auch
die tatsächlichen EXE-Versionsressourcen und den Hash des portablen Bauarchivs.

Der Workflow ist global seriell (`pw-app-release`, kein Abbruch laufender Builds).
Nur der Publisher hat `contents:write`; er führt ausschließlich Maincode aus.
Vor Draftanlage und unmittelbar vor Sichtbarkeit prüft er Main-SHA, die echte
erfolgreiche Package-CI-Pushquelle einschließlich `docs`/`ci-required` und deren
Versuch sowie die veröffentlichte Autorität erneut. Überholte Kandidaten stoppen;
ein nachfolgender erfolgreicher Mainlauf plant neu. Die letzte Mainabfrage und
der GitHub-Publishaufruf sind keine gemeinsame atomare Transaktion: ein danach
eintreffender Push wird durch seinen eigenen Folgelauf verarbeitet. Die serielle
Pipeline verhindert, dass ein älterer Pipelinebuild einen neueren überholt.

Uploads erfolgen ausschließlich in einen gebundenen unsichtbaren Draft; erst
nach binärem Rückdownload aller Dateien und frischer Vorprüfung wird er
veröffentlicht. Fehler bleiben sichtbar im Lauf. Ein Re-Run übernimmt nur den
gleichen Draft mit gleicher Quell-/Fingerprintbindung und identischen vorhandenen
Bytes; fehlende Assets werden ergänzt. Abweichende Assets, fremde Tags/Drafts
und zwischenzeitlich geänderte Releaseautorität stoppen ohne Ersetzen oder Löschen.
Mutierende API-Aufrufe werden nach unbekanntem Ausgang nicht blind wiederholt.
Veröffentlichte Vorgänger bleiben erhalten. Manifest und Delivery sind Hash-/
Provenienzbindungen, keine APP-B-Vertrauenssignatur oder Installationsbefugnis.

Ein manueller Dispatch baut den fixierten Workflow-Branchcommit ausschließlich
diagnostisch und veröffentlicht nie. Vor Merge kann damit der neue Code im
Draft-PR geprüft werden; die Herkunft wird als PR-Branch, nicht als bereits
integrierte Mainfassung ausgewiesen. Der reguläre Folgetrigger verwendet nur
erfolgreiche Main-Pushquellen. Eine Erstaktivierung braucht nach Review/Integration
einen eigenen Auftrag zum Setzen der Repositoryvariable und einen gezielten
erfolgreichen Main-CI-Re-Run. Weder dieser PR noch ein Diagnosebau setzt die Variable.
Original-Serverlogs und sechs gebundene Kandidatdateien stehen dem unabhängigen
Reviewer im jeweiligen Actionslauf zur Verfügung (Plan sieben, Produkt vierzehn
Tage); `.ci/package.json` bleibt `evidence.mode=none`. Abgelaufene Belege müssen
gezielt erneuert werden. Die erste Liveveröffentlichung und echte Windows-11-
Upgradeprobe bleiben getrennte nachgelagerte Releasegates.
