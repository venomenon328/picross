# PW: Automatisierte App-Releases und Selbstupdate

**Stand APP-ROOT1 · 13.11.2026 · [Issue #612](https://github.com/venomenon328/picross/issues/612).**
Maßgeblich: [APP-ROOT1](https://github.com/venomenon328/picross/issues/612#issuecomment-6851636493)
und [Eigentümerfreigabe / öffentlicher Root](https://github.com/venomenon328/picross/issues/612#issuecomment-6852316923).
**APP-A ist über PR #613 unabhängig abgenommen und in main integriert.**
Erste Veröffentlichung und Windows-11-Upgradeprobe sind weiterhin offen.
**APP-B1 liefert signierte Updateautorität und gemeinsamen Verifier; APP-B2
ergänzt den standardmäßig ausgeschalteten Client und unabhängigen MSI-Helfer.** APP-ROOT1
verankert ausschließlich den vom Eigentümer freigegebenen öffentlichen Root im Payload.
Veröffentlichung bleibt ohne eigenen Betriebsauftrag, private Signierbereitstellung
und beide Aktivierungsschalter gesperrt. Der Updatekanal bleibt inaktiv.
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
- **APP-B2:** Prüfung beim Start,
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

## 3. APP-B2 · Verifizierter Updateclient

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
Sperren haben Vorrang. Die unprovisionierte Form `accepted={}` und `active_signer=null`
bleibt gültig und sperrt Signierung. APP-ROOT1 enthält genau den freigegebenen
öffentlichen Schlüssel `a+FfCpsBYUS/pDwRIDeV8X/VGTk5h0gv61fBP4Nlku4=` unter
seiner SHA-256-ID `7434f1625066c40b5b1ee43e5202745cccd2986d542bec6af5071688c9b9a134`,
dieselbe ID als `active_signer` und `blocked=[]`. Der Eigentümer bestätigt die
sichere private Sicherung; die öffentliche Hashbindung beweist keine private
Paarzugehörigkeit. Diese wird erst im separat beauftragten Signierbetrieb geprüft.
Kein Root aus Environment, Nutzereinstellungen, Gitdatencheckout, Browser,
Produktionsrecord oder beliebigem Download; kein TOFU und kein Testkey-Schalter.

Die Eigentümerfreigabe erfüllt die Startvoraussetzung ROOT1-A02; ROOT1-A01 bleibt
unabhängiges Review vor Merge. ROOT1-T01 verwendet nur öffentliche Produktionsbytes
und synthetische Negativschlüssel. ROOT1-T02 ist der separate nicht veröffentlichende
Windowsdispatch am festen PR-Head mit frischem MSI-/Frozen-/Trust-/Lizenzvergleich.
MSI-Originale bleiben höchstens 14 Tage, gezielte technische Originale sieben Tage
für diesen Reviewer erreichbar; konkrete Bindungen stehen im Draft-PR. ROOT1-R01
und die bestehenden APP-A/B1/B2-Betriebs-/Windows-11-Gates bleiben getrennt offen.

Nur Public Key/ID werden über den geprüften PR in das Payload aufgenommen.
Erst auf gesonderten Betriebsauftrag wird der private 32-Byte-Seed kanonisch Base64-kodiert als
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
automatisierbar; Erstinstallation, produktive Provisionierung und Betriebsgates bleiben erforderlich.

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
(Windows-11-Upgrade) bleiben gesonderte offene Betriebsgates. APP-B2 verwendet
diese gelieferte Schnittstelle gemäß Abschnitt 7.

Primärquellen geprüft 13.11.2026: [Ed25519-API](https://cryptography.io/en/50.0.2/hazmat/primitives/asymmetric/ed25519/),
[stabile Version/Wheel-OpenSSL](https://cryptography.io/en/50.0.2/changelog/),
[Windows-Wheels](https://cryptography.io/en/50.0.2/installation/),
[RFC 8032](https://datatracker.ietf.org/doc/html/rfc8032),
[Environmentfreigaben](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments).

## 7. APP-B2 · Client, Übergabe und Abschluss

Gemäß [APP-B2-S](https://github.com/venomenon328/picross/issues/612#issuecomment-6859867142)
erscheinen natives Fenster und lokale Dienstbereitschaft sofort. Der normale
installierte Windows-GUI-Start mit bereits bestätigtem Opt-in prüft höchstens
einmal nebenläufig **vor** erster Browseröffnung und initialem Git-Refresh.
Bei signiert bestätigter höherer Version bleiben beide auch während Download,
Kandidatenprüfung und sicherer Helferübergabe zurückgestellt. Erst die bestätigte
neue App nimmt nach dem MSI-Neustart regulär die Arbeit auf. Ohne Opt-in oder
ohne bestätigten höheren Kandidaten, auch bei Offline-/Kanal-/Trust-/Versions-
oder Downloadfehlern, startet die vorhandene App Browser und initiales Git genau
einmal. Der Kanalstatus bleibt ehrlich; keine Zusicherung allgemeiner Aktualität.

Während Prüfung/Download ist „Ohne Update fortfahren“ bedienbar. Die Aktion
verwirft diesen Versuch, ohne die gespeicherte Zustimmung zu ändern. Abbruch
und Helferstart sind synchronisiert; ein verworfener Versuch erhält niemals GO.
Nach Übernahme der sicheren Helferübergabe durch die GUI sind Skip und Opt-out
gesperrt, der bestehende Stop-/MSI-Vertrag entscheidet. Reguläres Beenden bleibt
vorher möglich, ohne Browser/Git noch nachzustarten. Browseröffnungswünsche eines
Zweitstarts heben während des Gates nur das Steuerfenster hervor. Manuelles
„Im Browser öffnen“ wird erst nach Arbeitsaufnahme freigegeben; ein Browserfehler
erlaubt danach einen ausdrücklichen neuen Öffnungsversuch, keinen zweiten
initialen Refresh. Tk-Änderungen erfolgen ausschließlich im GUI-Thread.
Ein nach Arbeitsaufnahme begonnener Git-Refresh/P2-Vorgang läuft beim Stop
weiterhin geordnet aus; APP-B2-S führt keinen allgemeinen Gitabbruch ein.

Die Identität stammt aus übereinstimmenden gebauten
`build.json`/`components.json`, festem per-user-Programmziel und tatsächlich
registrierter MSI-Version. Setup, Entwickler-/portable Fassung, Headless- und
Zweitstart autorisieren keine Installation. Bei leerem festem Trust bleibt der
Kanal sichtbar inaktiv. Unbestätigte Kanalfrische heißt niemals „aktuell“.

Das native Steuerfenster bietet einmalig ausdrücklich Ablehnen/Aktivieren und
anschließend einen sichtbaren Schalter. `.launcher/app-updates.json` enthält nur
`format=picross-app-update-preference-v1` und den booleschen Wert `enabled`.
Fehlender/ungültiger Zustand ist keine Zustimmung. Die Datei wird im privaten
Launcherzustand atomar ersetzt; Browserstorage und `config.json` bleiben getrennt.
Ohne Opt-in findet auch kein automatischer Netzabruf statt. Ausschalten oder
reguläres Beenden verwirft einen laufenden Download. Nach abgeschlossener Übergabe
zeigt die Oberfläche den geordneten Stop; ein begonnener P2-Vorgang läuft aus.

[`update_client.py`](../tools/production_workspace/update_client.py) verwendet
ausschließlich anonyme HTTPS-Releases des festen Repositorys. Keine Tokens,
Proxy-/Credentialübernahme oder Produktionsremotes. Höchstens vier Seiten à 100
Releases und 4 MiB, zehn Sekunden je Socketoperation, 60 Sekunden Metadatenbudget;
unvollständiger Katalog ist ein Fehler. Höchste veröffentlichte 0.1.x-Version
entscheidet, ohne älteren Fallback. API-Redirects sind verboten; Assetredirects
gehen höchstens zweimal an den expliziten GitHub-Releaseasset-Host mit festem
Pfadmuster. v2-Metadaten werden vor Nutzdownloads mit `verify_metadata` geprüft.
`VerifiedMetadata` ist keine Installationsfreigabe. Gleiche Version ohne bekannte
identische Bindung und ältere Version sind Fehler, kein Update.

Die fünf gebundenen Nutzassets werden streamend in eine neue private flache
Stagingablage unter `.launcher/update-staging/<zufällige Kennung>` geladen.
Maximal 512 MiB zusammen, Sidecars jeweils 8 MiB, 300 Sekunden Downloadbudget;
das sind lokale Ressourcenschutzgrenzen, keine CI-Erfolgsgates. Keine Extraktion.
Links/Reparsepfade, unvollständige Längen und Hashabweichungen werden abgewiesen.
Alle tatsächlichen Bytes durchlaufen danach den unveränderten vollständigen
B1-Vertrag `verify_candidate`, erneut unmittelbar vor Übergabe.

[`UpdateHelper.cs`](../tools/production_workspace/packaging/UpdateHelper.cs)
wird als eigenständige x64-.NET-Framework-EXE gebaut und im Ressourceninventar
gebunden. Eine geprüfte Kopie läuft außerhalb des ersetzten Appimages. Die private
Pipe übergibt einen geschlossenen Auftrag, ein geerbtes echtes Prozesshandle,
Instanz-/Benutzer-/Installationsidentität, Manifest-/Asset-/EXEbindungen und Hashes
von Konfiguration, Port und Zustimmung. Der Helfer prüft seinen tatsächlichen
Elternprozess, Benutzer und dessen installierte EXE. Erst READY, anschließend
`Runtime.request_stop()` und vollständiger Request-/P2-Drain; nur dessen bestätigter
Erfolg sendet GO. Danach wartet der Helfer auf das echte Prozessende, einschließlich
Desktop-finally/InstallInterlock. EOF oder unbekannter Ausgang autorisieren nichts.

Alle Kandidaten bleiben mit Schreib-/Löschsperre geöffnet. Vor System-msiexec werden
Hashes und echte MSI-Datenbankidentität erneut geprüft. Feste per-user-Argumente,
keine Shell, Elevation, Kill- oder Rebootaktion. Der bestehende MSI-Guard entscheidet
weiter über parallele Starts, Locks und Fremdbelegung. Eine installierte Desktop-
Verknüpfung wird beim Upgrade erhalten. Erfolg verlangt MSI-Exit 0, nachgelesene
neue MSI-/EXE-Version und Bytebindung sowie einen tatsächlich authentisierten
Wiederanlauf auf dem unveränderten Port mit demselben `--state`/Browsermodus.
Der Wiederanlauf setzt `PYINSTALLER_RESET_ENVIRONMENT=1` für eine neue eigenständige
Frozen-Instanz, gemäß [PyInstaller-Neustartvertrag](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#using-sys-executable-to-spawn-subprocesses-that-outlive-the-application-process-implementing-application-restart).
Reboot-/Fehler-/unbestätigte Zustände erhalten einen sichtbaren manuellen Weg;
keine allgemeine Rollbackgarantie und kein automatischer Wiederholungsdienst.

Pending-/Ergebnisdateien enthalten ausschließlich den kleinen Übergabezustand.
Bestätigt beendete Downloads werden entfernt; eigene Helferreste erst nach seinem
Ende über die exakte gespeicherte Dateiliste. Fremde Dateien blockieren Bereinigung.
Unbestätigte Übergaben werden nie erneut ausgeführt. Temporär nicht entfernbare
Reste bleiben ehrlich als solche erhalten. Keine Checkout-/Cache-/Refwriter.

T01 liegt im bedarfsgewählten `tools`-Modul. T02 ergänzt den separaten diagnostischen
Windowsdispatch um den echten Client mit synthetischen Signaturen und den gebauten
Helfer: MSI-Identität/Negativfälle und echtes Prozesshandle-Warten mit isoliertem
Kindprozess. Der Diagnoseadapter und sein C#-Treiber werden nicht mitgeliefert.
Unveränderte MSI-Originale höchstens 14 Tage, kleine technische Originale sieben
Tage; keine privaten Testkeys. A01 bleibt unabhängiges Review vor Merge. T03/R01
bleibt die echte nicht erhöhte Windows-11-Probe vor produktiver Selbstupdate-
verteilung; Serverinspektion ersetzt sie nicht. Erste root-provisionierte Version
weiterhin einmalig manuell installieren, insbesondere nach 0.1.0 oder leerem Trust.

Technische Grundlagen: [Prozess-Wait](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject),
[per-user MSI-Abfrage](https://learn.microsoft.com/en-us/windows/win32/api/msi/nf-msi-msigetproductinfoexw),
[explizite Handlevererbung](https://docs.python.org/3.13/library/subprocess.html#subprocess.STARTUPINFO).
