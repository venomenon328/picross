# PW: Automatisierte App-Releases und Selbstupdate

## Geltung und Quellen

- **Status:** aktiver technischer Vertrag für PW-Publisher, Signaturprüfung und installierten Updateclient.
- **Betriebsautorität:** [Issue #612](https://github.com/venomenon328/picross/issues/612); die [Abschlussentscheidung](https://github.com/venomenon328/picross/issues/612#issuecomment-6878665809) aktiviert den PW-Betrieb. Ein Implementierungsmerge allein erteilt keine neue Betriebsbefugnis.
- **Vertrauenswurzel:** [APP-ROOT1](https://github.com/venomenon328/picross/issues/612#issuecomment-6851636493) und [öffentlicher Root mit Eigentümerfreigabe](https://github.com/venomenon328/picross/issues/612#issuecomment-6852316923); feste technische Bindung in Abschnitt 6.
- **PE-Mitnutzung:** derselbe technische Kern mit festen getrennten Produktidentitäten; [PE-Vertrag](PUZZLE_EDITOR.md#15-pe-app-b--startgate-und-sicherer-wiederanlauf). PW-Betrieb aktiviert keinen PE-Betrieb.
- **PG:** feste dritte Produzenten-, Client- und Helferidentität mit eigenem [Windows-Spielvertrag](../operations/WINDOWS_GAME_APP.md), Runtime-Fingerprint und zustimmungsgebundenem Startgate. PG verwendet die gemeinsamen Netz-, Byte- und Zeitgrenzen aus diesem Vertrag. [GAME-APP-D](https://github.com/venomenon328/picross/issues/731) legt für PG die integrierte Startansicht, den expliziten Spielstartwunsch und die passive MSI-Anzeige fest.
- **Lieferhistorie und Abnahmen:** zuständige Issues, Pull Requests und Releases. Dieser Vertrag ersetzt keine historischen [P4-Liefernachweise](https://github.com/venomenon328/picross/issues/588).

## 1. Autorität und Grenzen

Der Windows-Produktionsassistent ist eine installierte lokale Anwendung mit
fester vertrauenswürdiger Python-/Reader-/UI-Laufzeit und eigenen Zustandsdaten.
Ein `main`-Commit oder eine Gitdatenaktualisierung ist kein installierbares
Update. Nur eine erfolgreich verifizierte, veröffentlichte höhere Appversion
kann zur Aktualisierung dienen. Der PW-Fingerprint schließt Game-Export,
Inhalts-/Bildproduktion, Godot, Entwicklungs-HTML und Produktionsbranches aus.
PG verwendet seine eigene Auswahl für den regulären Windows-Spielinhalt.

Die Installations-, Zustands- und Erstumstiegsregeln stehen ausschließlich in
Abschnitt 7. Insbesondere autorisiert ein Produktionscheckout keine Programmbytes.

## 2. APP-A · Buildauswahl, Version, Veröffentlichung

Abschnitt 5 besitzt den vollständigen Publishervertrag: Main-Push-Auslöser,
Payload-Fingerprint, monotone Versionsautorität, MSI-Prüfung, Veröffentlichung
und Recovery. Abschnitt 6 ergänzt die signierte Installationsautorität.
Bauprovenienz und veröffentlichte Updateautorität sind getrennte Formen.

## 3. APP-B2 · Verifizierter Updateclient

Abschnitt 6 besitzt Wireformen, feste Vertrauenswurzel und Verifierschnittstelle.
Abschnitt 7 besitzt Zustimmung, Startgate, Netzwerkzugriff, Download, sichere
MSI-Übergabe, Wiederanlauf und Bereinigung. Der Client ist kein dauerhafter Dienst.

## 4. Prüf- und Abnahmegrenzen

Appbau und Appveröffentlichung bleiben außerhalb des regulären Spiel-
Windowspakets und der normalen Zusatzmodule. Auswahl und Freigaben folgen dem
[CI-Vertrag](../ci/CI_WORKFLOW_V2.md) und der jeweiligen Paketentscheidung in
[Issue #612](https://github.com/venomenon328/picross/issues/612), einschließlich
der ursprünglichen [APP-A-Kriterien K01–K10](https://github.com/venomenon328/picross/issues/612#issuecomment-6834815644).

Reguläre technische Prüfungen verwenden synthetische Identitäten und Negativfälle.
Diagnose-Dispatches bauen fixierte echte Windowskandidaten ohne Veröffentlichung;
private Testschlüssel existieren nur im Prozess. Vor Veröffentlichung werden die
gebundenen Originalassets zurückgeladen und erneut geprüft. Unabhängige Reviews,
Betriebsfreigaben und persönliche Windows-11-Abnahmen bleiben an konkrete
Produkt-Heads und Artefakte gebunden; ihr tatsächlicher Status steht im Issue/PR.

Eine erfolgreiche Linuxprüfung oder Hosted-Windows-Server-MSI-Inspektion ersetzt
keinen echten Windowsstart, keine nicht erhöhte Installation und keinen
Windows-11-Upgrade-/Selbstupdate-Lebenszyklus. Hosted Windows Server ist wegen
Policy 1625 für die erforderliche unprivilegierte MSI-Installation ungeeignet.
Erhaltene Benutzerzustände, Browserorigin, Offline-/Abbruch-/Fehlerverhalten und
geordneter Prozessstop sind am tatsächlich gelieferten Kandidaten nachzuweisen.
Die [Windows-Start-/Buildanleitung](../../tools/production_workspace/WINDOWS_BUILD.md)
beschreibt Bedienung und Bau.

## 5. APP-A-Ausführung und Recovery

Die eigene Release-Pipeline darf ausschließlich durch eine tatsächlich erfolgreiche
Package-CI für einen Main-Push dieses Repositorys veröffentlichen. Der isolierte
`workflow_run`-Folgetrigger ist dafür zugelassen; PR, Fork, Dispatch und fremdes
Repository sind keine Veröffentlichungsquellen. Nur der dedizierte Publisher
erhält `contents:write`; Prüf-/PR-Code erhält kein Release-Schreibrecht.

[`payload.py`](../../tools/production_workspace/payload.py) bildet die sortierten
committeten Gitdateien samt Pfad, Gitmodus, Bytezahl und SHA-256 auf einen kanonischen
Fingerprint ab. Sämtliche eingesammelten Produktions-Pythonmodule, App-Reader,
UI, MSI-/Build-/Prüfcode, Pins, Guard, Lizenztexte, Icon und START sind Eingaben.
Explizite Ausnahmen sind nicht eingebaute Markdown-/Schema-/Kalibrierungsdateien,
CMD-Fallbackbau und manuelle Smokes. Neue Pythonmodule werden einbezogen;
unbekannte Ressourcen und nichtreguläre Modi stoppen die Vorprüfung. Änderungen
außerhalb dieser Eingaben (insbesondere Inhalt, Spiel und allgemeiner CI-Kern)
ändern den Fingerprint nicht. Der echte Bau gleicht die repositorybezogenen
Dateien aus `Analysis-00.toc` gegen `inputs.json` ab; ein nicht inventarisierter
eingefrorener Input oder abweichende Arbeitsbytes brechen den Bau ab.

Vor Draftanlage und vor Sichtbarschaltung prüfen PW, PE und PG unter derselben
Remote-Lease wie der Arbeitsasset-Publisher die Grenzen bereits installierter
Clients. Kapazitätsreserve, Wartezeit und Rückbau stehen im
[PW-B-Vertrag](PW_B_CONTRACT.md). Ein gesperrter Versuch lässt die signierte
Versionsautorität bestehen.

[`release_channel.py`](../../tools/production_workspace/release_channel.py) liest
den letzten gültigen veröffentlichten `pw-v0.1.x`-Release samt kanonischem
`manifest.json` und lädt dessen gebundene Assets binär zurück. Unvollständige
oder fremde veröffentlichte PW-Einträge sind Fehler, keine neue Startlinie.
Gleicher Fingerprint erzeugt keinen Bau, keine neue Version und keinen Release;
andernfalls folgt genau Patch +1 ab 0.1.0.
`--version` injiziert die geplante Version in den vorhandenen Builder und Inspector,
ohne `release.json` oder den Sourcecheckout zu verändern. ProductCode bleibt
deterministisch je Version, UpgradeCode bleibt gleich. Der Inspector prüft auch
die tatsächlichen EXE-Versionsressourcen und den Hash des portablen Bauarchivs.
MSI, EXE, Manifest, Dateiname und `delivery.json` müssen dieselbe Versions- und
Produktidentität verwenden. Same-Version-Installation und Downgrade bleiben
gesperrt. Der 0.1.0-Startanker bezeichnet eine Actions-Auslieferung, keinen
historischen GitHub Release. Vor Sichtbarkeit prüft
[`verify_installer.py`](../../tools/production_workspace/verify_installer.py)
den fixierten Kandidaten gegen reale MSI-/Payload-/Lizenz-/Versions-/Hashbytes.

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
Ein Implementierungsmerge oder Diagnosebau aktiviert diese Voraussetzungen nicht.
Für den freigegebenen PW-Betrieb gelten weiterhin alle Quellen-, Signatur- und
Veröffentlichungsguards; der Betriebsentscheid steht unter „Geltung und Quellen“.


### Historische Quellbindung bei REPO-SLIM-A

Für die 23 veröffentlichten PW-Versionen bis 0.1.23 und die drei PE-Versionen
bis 0.2.3 enthält der Publisher eine geschlossene Zuordnung je Release-ID
und SHA-256 des ursprünglichen signierten Manifests. Bei diesen Releases darf
der Lightweight-Tag auch auf den geprüften Commit mit identischem vollständigem
Quellbaum und bereinigter Elternhistorie zeigen. Manifest, Signatur, Nutzassets
und die ursprüngliche Source in Delivery, Inspektion und Releaseziel bleiben
bytegebunden. Die höchste veröffentlichte Version bestimmt weiterhin die
Autorität. Entwürfe und neue Publikationen erfordern den exakten ursprünglichen
Tagvertrag. Bestehende Installationen lesen denselben signierten Release.

Die Zuordnung wird erst mit der separat geprüften und freigegebenen Refumstellung
wirksam. Vor dem Merge des Publisher-PRs beide Publisher für das Wartungsfenster
koordinieren. Jede zusätzliche Publikation oder geänderte Quelle verlangt einen
frischen Abgleich vor der Umschaltung. Refplan, Prüfbasis und Rückweg stehen in
[REPO-SLIM-A](https://github.com/venomenon328/picross/issues/717#repo-slim-a).

## 6. APP-B1 · Signierte Autorität und feste Roots

[`release_manifest.py`](../../tools/production_workspace/release_manifest.py) prüft
beide geschlossenen Manifestformen und alle tatsächlichen Nutzassetbytes.
[`update_verifier.py`](../../tools/production_workspace/update_verifier.py) authentifiziert
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

[`update-trust.json`](../../tools/production_workspace/update-trust.json) ist eine
explizit eingefrorene öffentliche Programmressource mit exakt
`format="picross-pw-trust-v1"`, `accepted` (ID → striktes Base64 des 32-Byte-Public-Keys),
`blocked` (eindeutige gesperrte IDs), `active_signer` (genau eine akzeptierte ID).
Sperren haben Vorrang. Die unprovisionierte Form `accepted={}` und `active_signer=null`
bleibt gültig und sperrt Signierung. APP-ROOT1 enthält genau den freigegebenen
öffentlichen Schlüssel `a+FfCpsBYUS/pDwRIDeV8X/VGTk5h0gv61fBP4Nlku4=` unter
seiner SHA-256-ID `7434f1625066c40b5b1ee43e5202745cccd2986d542bec6af5071688c9b9a134`,
dieselbe ID als `active_signer` und `blocked=[]`. Der Eigentümer bestätigt die
sichere private Sicherung; die öffentliche Hashbindung beweist keine private
Paarzugehörigkeit. Der separat beauftragte Signierbetrieb muss diese zusätzlich prüfen.
Kein Root aus Environment, Nutzereinstellungen, Gitdatencheckout, Browser,
Produktionsrecord oder beliebigem Download; kein TOFU und kein Testkey-Schalter.

Nur Public Key/ID werden über den geprüften PR in das Payload aufgenommen.
Die Bereitstellung des privaten 32-Byte-Seeds verlangt einen gesonderten Betriebsauftrag.
Er wird kanonisch Base64-kodiert als
`PW_UPDATE_SIGNING_KEY` im vorab eingerichteten Environment `pw-app-release`
bereitgestellt. Dessen benutzerdefinierte Branchpolicy erlaubt exakt den Branch
`main`, keine Tags/Wildcards. Privater Schlüssel nie in Git, Chat, Logs, App oder
Artefakten; kein privater Clienttoken. Eine Implementierungsänderung erteilt
keine Befugnis zur Bereitstellung oder Änderung des Secrets.

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

### Bau und technische Prüfung

`requirements-update.txt` pinnt die gemeinsame Kryptografiebasis für ausgewählte
tools-Tests und den separaten Appkanal. Dokumentkern und Main-Modulauswahl erhalten
keine zusätzliche Kryptografielast. Der Frozenbau sammelt Verifier und benötigte
Kryptografiemodule ausdrücklich ein, prüft tatsächlichen PYZ-/Native-Erweiterungs-
bestand und inventarisiert ausschließlich öffentliche Trust-/Produktressourcen.
Wheel-Lizenzen für cryptography, cffi und pycparser sowie die tatsächlich eingebundene
OpenSSL-4.0.3-Lizenz werden mitgeliefert. MSI/EXE bleiben ohne Authenticode.
Eine Metadatensignatur ersetzt keine Windows-Codesignatur; SmartScreen und
bestehende Plattformrichtlinien bleiben wirksam.

Die technischen Verifierprüfungen verwenden RFC-8032-Vektor, temporäre
Testidentitäten und positive/negative Wire-/Root-/Asset-/Versions-/Publisherfälle.
[`update_diagnostic.py`](../../tools/production_workspace/update_diagnostic.py)
ist ein ausdrücklich vom Frozen-Payload ausgeschlossener synthetischer Adapter.
Er prüft am fixierten echten Kandidaten gültige Signaturen und die Ablehnung
manipulierter MSI sowie eines Testroots im Produktionspfad. Private Testkeys
existieren nur im Prozess, keine privaten Schlüsseldateien. Prüfauswahl,
Artefaktbindung und Abnahmegrenzen folgen Abschnitt 4.

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
registrierter MSI-Version. Sie bindet Version, Product-/UpgradeCode, Quellcommit
und gültigen Payload-Fingerprint. Setup, Entwickler-/portable Fassung, Headless- und
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

[`update_client.py`](../../tools/production_workspace/update_client.py) verwendet
ausschließlich anonyme HTTPS-Releases des festen Repositorys. Keine Tokens,
Proxy-/Credentialübernahme oder Produktionsremotes. Höchstens vier Seiten à 100
Releases und 4 MiB, zehn Sekunden je Socketoperation, 60 Sekunden Metadatenbudget;
unvollständiger Katalog ist ein Fehler. Höchste veröffentlichte 0.1.x-Version
entscheidet, ohne älteren Fallback. API-Redirects sind verboten; Assetredirects
gehen höchstens zweimal an den expliziten GitHub-Releaseasset-Host mit festem
Pfadmuster. v2-Metadaten werden vor Nutzdownloads mit `verify_metadata` geprüft.
`VerifiedMetadata` ist keine Installationsfreigabe.

Gemäß [APP-B2-N](https://github.com/venomenon328/picross/issues/612#issuecomment-6863885687)
endet die Prüfung bei gleicher höchster veröffentlichter Version mit dem nativen
Status „Keine neuere Appversion veröffentlicht.“, wenn die signiert authentifizierten
v2-Metadaten einschließlich Release-/Assetmetadatenbindung zu sämtlichen genannten
lokalen Identitätsmerkmalen passen. Die Installation wird vor dieser Meldung erneut
geprüft. Kein Nutzassetdownload, Staging, Helfer oder MSI; Browser und initiales Git
starten anschließend genau einmal. Zustimmung und übriger Zustand bleiben erhalten.
Diese Aussage betrifft das Fehlen einer höheren veröffentlichten Version; sie
behauptet keine bitidentischen lokalen MSI-/EXE-Bytes und keine authentifizierte
lokale Manifestbindung. Der unveränderte `assess_update`-Guard verlangt für sein
kryptografisches `noop` weiterhin die zuvor authentifizierte identische Bindung;
der Kandidatenhash darf dafür nicht als lokale Autorität eingesetzt werden.

Abweichende Source-/Fingerprint-/Produktidentität ergibt einen unterscheidbaren
Warnstatus und den nutzbaren bisherigen Arbeitsweg, keine Same-Version-Installation.
Fehlende oder ungültige Installationsidentität, ältere Version, unvollständiger
Katalog, Signatur-/Root-/Metadatenfehler sowie Offline/404/429/TLS/Timeout bestätigen
keine Kanalfrische. Die vorhandenen Fehler-/Fallbackwege bleiben bestehen. Höhere
Versionen durchlaufen unverändert den vollständigen folgenden Updateweg; kein
weiterer Versuch in derselben Instanz.

Die fünf gebundenen Nutzassets werden streamend in eine neue private flache
Stagingablage unter `.launcher/update-staging/<zufällige Kennung>` geladen.
Maximal 512 MiB zusammen, Sidecars jeweils 8 MiB, 300 Sekunden Downloadbudget;
das sind lokale Ressourcenschutzgrenzen, keine CI-Erfolgsgates. Keine Extraktion.
Links/Reparsepfade, unvollständige Längen und Hashabweichungen werden abgewiesen.
Alle tatsächlichen Bytes durchlaufen danach den unveränderten vollständigen
B1-Vertrag `verify_candidate`, erneut unmittelbar vor Übergabe. PG zeigt den
Downloadfortschritt nur für die fünf signiert gebundenen Nutzassets an. Der
Metadatenabruf und die anschließende Verifikation sind eigene Statusphasen.

[`UpdateHelper.cs`](../../tools/production_workspace/packaging/UpdateHelper.cs)
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
weiter über parallele Starts, Locks und Fremdbelegung. PG verwendet hier
`/passive` für die native Windows-Installer-Fortschrittsanzeige. PW und PE
verwenden weiterhin `/qn`. Eine installierte Desktop-
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
Konfiguration, Repository-/Remote-/Refwahl, Gitcache, Browserprofil, lokaler
Zustand, gespeicherter Port und Produktionsdaten bleiben beim Upgrade erhalten.

Die getrennte Windowsdiagnose verwendet den echten Client mit synthetischen
Signaturen und den gebauten Helfer: MSI-Identität/Negativfälle und echtes
Prozesshandle-Warten mit isoliertem Kindprozess. Diagnoseadapter und C#-Treiber
werden nicht mitgeliefert. Die echte nicht erhöhte Windows-11-Probe und ihre
Abnahme folgen Abschnitt 4. Die erste root-provisionierte updaterfähige Version
wird einmalig manuell installiert, insbesondere nach 0.1.0 oder leerem Trust.

Technische Grundlagen: [Prozess-Wait](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject),
[per-user MSI-Abfrage](https://learn.microsoft.com/en-us/windows/win32/api/msi/nf-msi-msigetproductinfoexw),
[explizite Handlevererbung](https://docs.python.org/3.13/library/subprocess.html#subprocess.STARTUPINFO).


## PE-APP-B · feste zweite Clientidentität

[#691 / PE-APP-B](https://github.com/venomenon328/picross/issues/691#umsetzungsvorbereitung-pe-app-b--startgate-selbstupdate-und-sicherer-wiederanlauf)
verwendet denselben Client, Stage, Verifier und externen C#-Helfer über feste
PW-/PE-Adapter. Ohne Adapter bleibt der PW-Einstieg unverändert. PE hat eigene
0.2.x-Tags, Programm-/MSI-/Trustidentität, .updates-Zustand und einen separat
kompilierten Helfer; keine freien Produktparameter aus dem Checkout oder Netz.
PE bestätigt sein natives Fenster über private IPC statt PW-HTTP-Bereitschaft.
Der geschlossene Vertrag steht in [PE §15](PUZZLE_EDITOR.md#15-pe-app-b--startgate-und-sicherer-wiederanlauf).

Gemeinsame Payloadänderungen können nach Mainmerge und erfolgreicher Main-CI
regulär eine neue PW-Version auslösen. Eine Änderung des gemeinsamen Kerns
aktiviert weder PE-Publikation noch PE-Secrets/Environments. Die jeweiligen
Betriebsentscheidungen bleiben produktbezogen.
