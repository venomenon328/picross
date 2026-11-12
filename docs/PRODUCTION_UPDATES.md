# PW: Automatisierte App-Releases und Selbstupdate

**Beschlossener Sollvertrag · 12.11.2026 · [Issue #612](https://github.com/venomenon328/picross/issues/612).**
Verbindliche erste [Paketentscheidung APP-A](https://github.com/venomenon328/picross/issues/612#issuecomment-6834815644).
Die folgenden Fähigkeiten sind **noch nicht implementiert oder veröffentlicht**.
Es gelten bis zur jeweiligen abgenommenen Integration die vorhandenen
P4-Programm-/Installerregeln und der ausschließlich manuelle
[`pw-installer.yml`](../.github/workflows/pw-installer.yml).
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
