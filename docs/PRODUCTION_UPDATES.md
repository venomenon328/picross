# PW: Automatisierte App-Releases und Selbstupdate

**Stand APP-B1 · 13.11.2026 · [Issue #612](https://github.com/venomenon328/picross/issues/612).**
Maßgeblich: [Paketentscheidung APP-B1](https://github.com/venomenon328/picross/issues/612#issuecomment-6848332974).
**APP-A ist über PR #613 unabhängig abgenommen und in main integriert.**
Erste Veröffentlichung und Windows-11-Upgradeprobe sind weiterhin offen.
**APP-B1 liefert signierte Updateautorität und gemeinsamen Verifier; APP-B2
(Startprüfung und Installation) ist noch nicht implementiert.** Produktionsvertrauen
ist ausdrücklich unprovisioniert. Veröffentlichung bleibt ohne eigenen Betriebsauftrag,
provisionierte Roots und beide Aktivierungsschalter gesperrt. Kein aktiver Selbstupdateclient.
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
- **APP-B1:** signierte Updatekanalinformation und gemeinsamer Offlineverifier.
- **APP-B2 (danach):** Prüfung beim Start,
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

## 3. APP-B2 · Noch ausstehender verifizierter Updateclient

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
ungeprüften HTTP-Endpoint allein genügt nicht. Der in APP-B1 geschlossene Schlüsselbereitstellungs-/Rotations-/Widerrufsweg
steht in Abschnitt 6; APP-B2 verwendet diese feste Vertrauensgrenze.
Keine Secrets committen oder eine Signierungsbefugnis aus der Clientumsetzung ableiten.
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
Veröffentlichte Vorgänger bleiben erhalten. Die v1-Form von Manifest und Delivery bleibt Bauprovenienz; die zusätzliche
v2-Signatur wird ausschließlich im Publisher erzeugt (Abschnitt 6).

Ein manueller Dispatch baut den fixierten Workflow-Branchcommit ausschließlich
diagnostisch und veröffentlicht nie. Vor Merge kann damit der neue Code im
Draft-PR geprüft werden; die Herkunft wird als PR-Branch, nicht als bereits
integrierte Mainfassung ausgewiesen. Der reguläre Folgetrigger verwendet nur
erfolgreiche Main-Pushquellen. Eine Erstaktivierung braucht nach Review/Integration
einen eigenen Betriebsauftrag einschließlich Root-/Environmentbereitstellung,
beider Repositoryvariablen und eines gezielten erfolgreichen Main-CI-Re-Runs.
Weder dieser PR noch ein Diagnosebau aktiviert diese Voraussetzungen.
Original-Serverlogs und sechs gebundene v1-Diagnosekandidatdateien stehen dem unabhängigen
Reviewer im jeweiligen Actionslauf zur Verfügung (Plan sieben, Produkt vierzehn
Tage); `.ci/package.json` bleibt `evidence.mode=none`. Abgelaufene Belege müssen
gezielt erneuert werden. Die erste Liveveröffentlichung und echte Windows-11-
Upgradeprobe bleiben getrennte nachgelagerte Releasegates.


## 6. APP-B1 · Signierte Autorität und feste Roots

[`release_manifest.py`](../tools/production_workspace/release_manifest.py) prüft
beide geschlossenen Manifestformen und alle tatsächlichen Nutzassetbytes.
[`update_verifier.py`](../tools/production_workspace/update_verifier.py) authentifiziert
v2 mit Ed25519 aus der stabilen `cryptography`-Bibliothek. Keine selbst geschriebene
Kryptografie, kein Netzwerk-/Datenwriter und kein Aufruf von MSI oder Shell.

### Wireform und Schnittstelle

`picross-pw-release-v2` enthält exakt die v1-Felder
`format,repository,status,version,tag,source_commit,payload_fingerprint,product_code,
upgrade_code,assets,inspection` und zusätzlich `platform="windows-x64"`,
`channel="stable"`, `signing_key_id`. Repository ist `venomenon328/picross`, Status
`production`; Source ist eine volle SHA, Fingerprint SHA-256, Version höher als
0.1.0 in der MSI-Linie 0.1.x. ProductCode ist versionsspezifisch, UpgradeCode fest.
`assets` bindet genau MSI, `.sha256`, `START.txt`, `delivery.json`, `inputs.json`
mit jeweils exakt `bytes` (positive Ganzzahl, kein Boolean) und `sha256`.
Die bestehenden geschlossenen Inspektionsfelder und Delivery-/Inputbindungen bleiben.

`manifest.sig.json` enthält exakt `format="picross-pw-signature-v1"`,
`algorithm="Ed25519"`, `key_id`, `signature`. Schlüssel-ID ist der kleingeschriebene
SHA-256 der 32 rohen Public-Key-Bytes, identisch zu `signing_key_id`.
Signatur: striktes kanonisches Base64, genau 64 dekodierte Bytes. Signierte Nachricht:
ASCII `picross-pw-release-v2`, genau ein NUL, dann die unveränderten kanonischen
UTF-8-Manifestbytes. Kanonisch: `payload.canonical`, sortierte Schlüssel, keine
Trennleerzeichen, `ensure_ascii=False`, genau ein LF. Auch die Signaturdatei ist
kanonisch. Manifest höchstens 64 KiB, Signatur höchstens 4 KiB. Ungültiges UTF-8,
Duplikate, Zusatzfelder, Typabweichungen, NaN/Infinity, andere Formen oder
nichtkanonische Bytes scheitern. Die Signaturdatei ist kein gehashtes Nutzasset;
v2 hat genau sieben Releaseassets, historisches v1 weiterhin sechs.

`verify_candidate(manifest_bytes, signature_bytes, files)` verwendet immer den
festen Programmtrust und liefert erst nach Signatur- und vollständiger Assetprüfung
einen unveränderlichen `VerifiedCandidate`. Er bindet Originalmanifest/-signatur,
Version, Source, Fingerprint, Schlüssel und MSI-Hash/-Bytes. `binding` ist SHA-256
der kanonischen Manifestbytes. `assess_update(candidate, local_version,
local_binding=None)` liefert nur für höhere Version `update`, bei gleicher Version
und identischer zuvor authentifizierter Manifestbindung `noop`. Ohne belastbare
Same-Version-Bindung, bei abweichendem Inhalt oder älterer Version: Fehler.
Lokaler Zustand wird weder gelesen noch gespeichert. Ein gültiges Ergebnis führt
keinen Download oder Programmstart aus. v1 ist ausschließlich historische
Versions-/Fingerprintautorität, niemals automatische Installationsautorität.

### Bootstrap, Geheimnisse und Wechsel

[`update-trust.json`](../tools/production_workspace/update-trust.json) ist eine
explizit eingefrorene öffentliche Programmressource mit exakt
`format="picross-pw-trust-v1"`, `accepted` (ID → striktes Base64 des 32-Byte-Public-Keys),
`blocked` (eindeutige gesperrte IDs), `active_signer` (genau eine akzeptierte ID).
Sperren haben Vorrang. Unprovisioniert sind `accepted={}` und `active_signer=null`;
das ist der gelieferte Stand und autorisiert keine Produktionssignierung.
Kein Root aus Environment, Nutzereinstellungen, Gitdatencheckout, Browser,
Produktionsrecord oder beliebigem Download; kein TOFU und kein Testkey-Schalter.

Erst ein eigener Betriebsauftrag an den Eigentümer erzeugt einen echten Schlüssel
mit sicherer Zufallsquelle. Nur Public Key/ID werden über geprüften PR in das
Payload aufgenommen. Der private 32-Byte-Seed wird kanonisch Base64-kodiert als
`PW_UPDATE_SIGNING_KEY` im vorab eingerichteten Environment `pw-app-release`
bereitgestellt. Dessen benutzerdefinierte Branchpolicy erlaubt exakt den Branch
`main`, keine Tags/Wildcards. Privater Schlüssel nie in Git, Chat, Logs, App oder
Artefakten; kein privater Clienttoken. APP-B1 richtet nichts davon ein.

Beide Repositoryvariablen `PW_RELEASE_ENABLED=true` und
`PW_UPDATE_SIGNING_ENABLED=true` sind nötig. Eine secretfreie `publication-gate`
prüft Main-/Push-/CI-/Versuchs-/Quellbindung, Kandidat, Autorität und provisionierten
Trust sowie das bereits vorhandene Environment samt Main-only-Policy, bevor der
Publisher es referenziert. Ohne Freigabe kann ein Lauf kein Environment implizit
anlegen. Nur `publish` hat Release-Schreibrecht; nur dessen finaler Schritt erhält
das Secret als Laufzeitwert. Dort werden sämtliche Prüfungen erneut ausgeführt.
Fehlender/falsch kodierter/fremder/gesperrter Schlüssel stoppt ohne Secret-Echo.
Diagnose, PR, Fork, Plan und Installer erhalten kein Produktionssecret.

Der Publisher bindet den Trusthash in den Plan, erzeugt aus geprüfter v1-Provenienz
die v2-Form und signiert deterministisch. Draft-first und serielle Ausführung
bleiben erhalten. Vor Sichtbarkeit lädt er alle sieben Dateien binär zurück,
prüft Signatur und Nutzassets erneut und wiederholt den Quellen-/Autoritätscheck.
Teiluploads sind nur bei identischen bereits vorhandenen Bytes wiederaufnehmbar.
Geänderte Roots/Signierkonfiguration, fremde Signaturassets oder Autoritätsänderungen
stoppen ohne Überschreiben. Bestehende Releases/Tags werden nicht nachsigniert.
Ein blockierter v2-Autoritätsstand erfordert einen eigenen Recoveryauftrag;
kein stilles Überspringen und kein Reset auf den Startanker.

Geplante Rotation: neuen Public Key zunächst in einer noch vom alten Schlüssel
signierten App ausliefern. Ein Altclient, der diese Übergangsversion verpasst,
benötigt nach Stilllegung des alten Keys eine vertrauenswürdig bezogene manuelle
Installation. Bei Verlust/Kompromittierung Signierung/Veröffentlichung stoppen,
alte ID sperren, neue Wurzel separat prüfen und betroffene Installationen manuell
erneuern. Keine dynamische Rootübernahme oder automatische Brückeninstallation,
keine nahtlose Rotation aller Offlineclients und keine sofortige Fernsperre
eines offline installierten Roots. Reguläre Updates unter gültigem Root bleiben
automatisierbar, sobald APP-B2 geliefert ist.

### Bau, Belege und offene Gates

`requirements-update.txt` pinnt die gemeinsame Kryptografiebasis für ausgewählte
tools-Tests und den separaten Appkanal. Dokumentkern und Main-Modulauswahl erhalten
keine zusätzliche Kryptografielast. Der Frozenbau sammelt Verifier und benötigte
Kryptografiemodule ausdrücklich ein, prüft tatsächlichen PYZ-/Native-Erweiterungs-
bestand und inventarisiert ausschließlich öffentliche Trust-/Produktressourcen.
Wheel-Lizenzen für cryptography, cffi und pycparser sowie die tatsächlich eingebundene
OpenSSL-4.0.3-Lizenz werden mitgeliefert. MSI/EXE bleiben ohne Authenticode.

APP-B1-T01 läuft ausschließlich im gewählten tools-Modul mit RFC-8032-Vektor,
temporären Testidentitäten und positiven/negativen Wire-/Root-/Asset-/Versions-/
Publisherfällen. [`update_diagnostic.py`](../tools/production_workspace/update_diagnostic.py)
ist ein ausdrücklich vom Frozen-Payload ausgeschlossener synthetischer Adapter.
T02 verwendet ihn in der gepinnten Windowsbauumgebung am echten fixierten Kandidaten:
gültige Signatur prüfen, manipulierte MSI ablehnen und Testroot im Produktionspfad
ablehnen. Private Testkeys existieren nur im Prozess, keine privaten Schlüsseldateien.
Die Diagnose ersetzt keine Installation und keinen Windows-11-Lebenszyklus.

Unabhängiger Reviewer erhält Serverlogs, unveränderte sechs v1-Kandidatdateien
(maximal 14 Tage) sowie v2-Testmanifest/-signatur, öffentlichen Testtrust,
Ergebnis, Inputaudit und MSI-Inspektion (maximal 7 Tage). Der Lieferkommentar bindet
Run/Attempt/Head und tatsächlich zurückgeladene Bytes/Hashes. Kein Binärbeleg im
Produktdiff; nach Ablauf gezielt erneuern. `.ci/package.json`: genau tools,
`evidence.mode=none`; keine Browser-/Produktions-/Native-Vollmatrix.
APP-B1-A01 bleibt unabhängiges Review vor Merge. APP-B1-R01 (reale Provisionierung
und Signaturaktivierung), APP-A-R01 (erste Veröffentlichung) und APP-A-R02
(Windows-11-Upgrade) bleiben gesonderte offene Betriebsgates. APP-B2 wird erst an
dieser gelieferten Schnittstelle separat vorbereitet.

Primärquellen geprüft 13.11.2026: [Ed25519-API](https://cryptography.io/en/50.0.2/hazmat/primitives/asymmetric/ed25519/),
[stabile Version/Wheel-OpenSSL](https://cryptography.io/en/50.0.2/changelog/),
[Windows-Wheels](https://cryptography.io/en/50.0.2/installation/),
[RFC 8032](https://datatracker.ietf.org/doc/html/rfc8032),
[Environmentfreigaben](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments).
