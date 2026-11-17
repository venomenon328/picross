# PW: Produktionsassistent

## Geltung und Quellen

- **Status:** aktiver Vertrag für Oberfläche, lokalen Git-/Bildzugriff und Ansichtsprojektion.
- **Normale Produktion:** ausschließlich [Authoring-Quellenroute](../production/authoring/PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase); dieser Gesamtvertrag ist keine pauschale Produktionspflichtlektüre.
- **Geschlossene Authoring-/Projektionsformen:** [PW-B](PW_B_CONTRACT.md).
- **Aktuelle Ansicht und Lieferung:** [PRODUCTION_CURRENT_VIEW](PRODUCTION_CURRENT_VIEW.md).
- **Installer und Updatekanal:** [PRODUCTION_UPDATES](PRODUCTION_UPDATES.md); tatsächlicher Betriebsstatus im zuständigen Issue/Release.
- **Bildgestaltung und Profile:** [Bildnormen](../production/images/README.md) beziehungsweise [Hintergrundtechnik](../production/PUZZLE_BACKGROUNDS.md).

## 1. Auftrag, Vorrang und Grenzen

Der Eigentümer bestätigt einen lokalen, per Launcher/Skript gestarteten
Produktionsassistenten mit automatischem Git-/Dateizugriff, sichtbaren
Originalbildern, reduzierter Bedienoberfläche und fünf aufeinanderfolgenden
Produktionsschritten. Manuelle Bild-/ZIP- und Routine-JSON-Importe sind kein
regulärer Transportweg mehr. Einmalige Repositoryeinrichtung ist zulässig.

**Nachträgliche Präzisierung:** Bestehende WIP-Stände müssen nicht lesbar bleiben.
Es gibt keinen Migrationsauftrag, keinen Alt-Sitzungsimport und keinen parallel
zu pflegenden alten Produktionsmodus. Keine Kompatibilitätsmatrix und keine
neuen Altdatenregressionen als Voraussetzung der Lieferung. Die Wiederverwendung
bewährter aktueller Datenformen ist erlaubt; sie erzeugt keine Zusicherung für
alte Jobs. Vorhandene WIP-Dateien werden durch diesen Auftrag nicht gelöscht.
Bereits integrierte Inhalte, Spielstände, IDs, Rechte und kompakte historische
Belege sind keine WIP-Kompatibilitätslast und bleiben unverändert.

Die aktuellen Datenformen stehen im [PW-B-Vertrag](PW_B_CONTRACT.md).
Der getrennte [Bestandseditor](PUZZLE_EDITOR.md) bearbeitet vorhandene Spielinhalte;
der Assistent erstellt keine konkurrierenden Inhaltswriter.

## 2. Produktionsphasen in der Oberfläche

Die Phasenroute und Entscheidungen besitzt [Authoring §1.1](../production/authoring/PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase).
Die Oberfläche zeigt genau die fällige Phase und ihre tatsächliche Bereitschaft.
Technische Phasenbedingungen, Nullwerte und Zustandsübergänge definiert
[PW-B](PW_B_CONTRACT.md#phasen-und-autorität). Ein Klick oder kopierter Auftrag
ist keine Bild-/Raster-/Endfreigabe.

Die fünf Bereiche heißen Abschlussbilder, Motivvorlage, Rasterangebote,
Hintergrund und Abschluss/Integration. Hintergrundaufgaben erscheinen erst in
Schritt 4. Ein intern notwendiges `pending` ist vorher kein Benutzerblocker.
Eine bereits gültige Entscheidung wird nicht erneut verlangt; offene
Hintergrundwahl und Endauftrag dürfen nach PW2-B gemeinsam transportiert werden.

## 3. Bedienoberfläche und Datenautorität

Der normale Einstieg zeigt die laufenden Produktionen, ihren verständlichen
Stand und die nächste fällige Handlung. Ein gewählter Job hat eine kompakte
Fünf-Schritte-Anzeige, den aktuellen Arbeitsbereich und eine primäre Aktion.
Keine gleichrangige Sammlung sämtlicher Promptkarten, Suchfilter und
Schemafelder als Hauptoberfläche.

- Beginn: Motiv und optionales Referenzbild. Weitere Gestaltungswünsche auf
  Wunsch; Rastermaße/Modus/Farbzahl dürfen früh als Einschränkung mitgegeben
  werden, sind aber keine Pflichtfelder der Abschlussbilderzeugung.
  Das eigene optionale Feld für Motivhinweise gelangt unverändert in den ersten
  Auftrag. Die optionalen Rastervorgaben unterscheiden Breite/Höhe in Zellen,
  Genauigkeit der ausgefüllten Achsen, Modus und bei Farbrätseln die Anzahl der Vordergrundfarben
  mit eigener Genauigkeit. Wünsche werden im Motivbriefing des Produktionsauftrags
  festgehalten. Bei der Abschlussbildauswahl für den Motivauftrag lassen sie sich
  konkretisieren. Breite und Höhe sind unabhängig: keine, nur eine oder beide
  Achsen sind frühe Wünsche. Offene Achsen passend zum Motiv bestimmen, niemals
  durch 0, eine Quadratseite oder einen alten aufgehobenen Wert ersetzen.
  Jede Achse besitzt eine eigene ausdrückliche Aufhebungswahl. Frühe Teilmaße
  gehören in das veröffentlichte Motivbriefing; konkrete Raster haben zwei Maße.
  Nach Vorlage des Parameterkorridors laufen Änderungen über die
  Korrektur. Die Grenzen und die stets farbige Abschlussillustration folgen
  [Authoring §2.1](../production/authoring/PUZZLE_AUTHORING_STEP_2.md).
- Motiv-/Rasterphase: Konfiguration, geschützte Merkmale, echte Bildvergleiche
  und verständlich bezeichnete Rasteroptionen. Maße, Farben und Schwierigkeit
  sind Ergebnisdaten, keine zu kopierenden technischen Eingaben.
- Hintergrundphase: optionaler Kontextwunsch, drei isolierte Bildkarten,
  Original-Großansicht und klare Auswahl/Korrektur. Keine Engineansicht.
- Schluss: gewähltes Raster, Abschlussbild und Hintergrund sowie die tatsächlich
  noch fehlende Endabnahme/Integrationsbefugnis in einer kompakten Übersicht.

IDs, Revisionen, Prüfsummen, Paketpfade und Commits werden aus den Quellen
übernommen. Technische Details bleiben aufklappbar und kopierbar, aber nicht
als reguläre editierbare Pflichtfelder. Bei fehlenden Quellen lautet die Aktion
etwa „Veröffentlichung fehlt“ oder „Neuere Ergebnisse laden“, nicht „64-stelligen
Hash eingeben“. Ein Defekt bleibt sichtbar; die Oberfläche rät keine Werte.

System/Hell/Dunkel, Tastaturfokus, beschriftete Controls und sinnvolle
Fensteranpassung gehören zum Werkzeug. Es muss nicht die Godot-Buchoberfläche
nachbauen. Bildansichten erhalten das Seitenverhältnis, bieten Zoom/Großansicht
und für transparente Bilder einen neutralen Prüfgrund. Keine unmarkiert
umgerechneten Bilder als Freigabeoriginale verwenden.

Git enthält die fachlichen Produktionsdaten. Browser-/Anwendungseinstellungen
enthalten ausschließlich Einrichtung, Ansicht und noch nicht abgesendete
Bedienabsichten. Keine zweite unabhängig bearbeitbare Produktionsdatenbank.
Ein importierter Erfolgsstatus oder eine geprüfte Dateiprüfsumme ist keine
frische Logikprüfung, keine Rechteklärung und keine menschliche Abnahme.

Beim Wiederöffnen zeigt die Detailansicht die tatsächlich veröffentlichten
Rasterwünsche und den als freigegeben überlieferten Korridor getrennt. Quelle
ist der gebundene Handoff; der Record muss dessen bestehender Parameterprojektion
entsprechen. Ein Statuswort beweist keine menschliche Freigabe. Eindeutig
abbildbare Einzelwünsche belegen die Rasterfelder vor, andere Formen und mehrere
Optionen bleiben vollständig lesbar. Fehlende strukturierte Einzelwerte sagen
nichts über freie Wünsche im Motivbriefing aus. Vollständige Parameteroriginale und veröffentlichtes
Motivbriefing sind beim Öffnen, Wiederladen und Motiv-/Revisionswechsel geschlossen;
Zusammenfassung, Quellenstatus und Fehler bleiben davor sichtbar. Das inventarisierte `handoff.brief` wird aus demselben
geprüften Originalpaket als UTF-8-Klartext mit Absätzen gelesen (höchstens 1 MiB).
Fehlende oder widersprüchliche Originale sind Fehler.

Veröffentlichte Stände haben genau einen Haupteintrag je Rätsel-ID und eine
getrennte Versions-/Quellwahl nach [aktueller Ansichtsübergabe](PRODUCTION_CURRENT_VIEW.md).
Im konfigurierten Remotebetrieb führen ausschließlich die gewählten Remotequellen,
auch bei lokalen Vorsprüngen oder Divergenzen. Die gültige Spitze des zugeordneten
Produktionsbranches hat Vorrang vor main; tatsächlich offene Main-only-Arbeit
bleibt erreichbar. Die normale Fortsetzung benötigt keine Versions-/Quellwahl.
Titelgleiche IDs sind unterscheidbar. Gespeicherte Motivtexte und deren Verwerfen
bleiben sekundäre lokale Eingaben, keine laufenden Produktionen. Ohne aktive
Auswahl beginnt ein erklärter Leerzustand; alte Texte öffnen niemals automatisch.
Job-/Revisions-/Quellwechsel und das ausdrückliche
Laden eines neueren Standes verwerfen ungesendete Absichten. Ein bloßes Suchen
neuer Ergebnisse erhält die aktive gebundene Ansicht und ihre Eingaben.

## 4. Quelle, Synchronisierung und Snapshot

### 4.1 Einmalige Einrichtung

Der Launcher erhält genau einen vorhandenen lokalen Projektcheckout und einen
separaten eigenen Zustands-/Cacheordner. Primärer Einstieg ist der per-user
Windows-x64-MSI aus dem vorhandenen App-Image mit `Picross-Start.exe`, privater Python-/Pillow-/Tcl/Tk-
Laufzeit und sämtlichen benötigten unveränderten Readern aus einem Buildcommit.
Kein globales Python/Node oder Laufzeitdownload. Git mit `--no-lazy-fetch` bleibt
externe Voraussetzung; vorhandene Anmeldung wiederverwenden, Fehler früh auf Deutsch
melden. Native Einrichtung/Status, Browser öffnen und geordneter Stop gehören dazu.
Die CMD bleibt Entwicklerfallback mit vertrauenswürdigem Programmcheckout.
Die vollständige [P4-Entscheidung](https://github.com/venomenon328/picross/issues/588#issuecomment-6825638437)
und [Bau-/Lieferbindung](../../tools/production_workspace/WINDOWS_BUILD.md) sind maßgeblich. Der
Zustandsordner liegt nicht in `content/`, `game/` oder einem fremden Arbeitsbaum.
[WORKSPACE](../dev-rules/WORKSPACE.md) gilt; persönliche Pfade werden nicht committed.

Verbindliches Schema für neue PW-Produktionen: `content/pw/<puzzle_id>`, zum
Beispiel `content/pw/pz-eule`. Eine Produktion behält ihren Branch; ihre
Revisionen liegen weiterhin in der bestehenden Ablage. Die Rätsel-ID besteht
aus `pz-` und kleingeschriebenen Buchstaben/Ziffern mit optionalen Bindestrichen.
Standardauswahl: `main` und `content/pw/*`; ausdrücklich kleinere Auswahlen
daraus sind zulässig. Andere Produktionsbranches werden weder synchronisiert
noch inhaltlich durchsucht. Auf einem Produktionsbranch liest der Assistent
nur Indexeinträge der im Branchnamen gebundenen Rätsel-ID. Auf `main` werden
die dort veröffentlichten PW-Produktionen gelesen; die aktive Auswahl nimmt
anschließend nur eindeutig nachgewiesene abgeschlossene Lieferungen gemäß
PW2-C unten heraus. Der Produktionsakteur muss
neue PW-Übergaben auf dem zugehörigen Branch veröffentlichen; PW-B übernimmt
diese Vorgabe in seine Aufträge. Keine Umbenennung/Löschung alter Branches.

Die unveränderte bisherige Standardeinrichtung `main` + `content/*` wird einmalig
im eigenen Zustand auf den neuen Filter eingeengt. Abweichende alte Auswahlen
werden mit einer verständlichen Neueinrichtungsaufforderung zurückgewiesen,
nicht still erweitert. Der neue Leser verwendet `git-cache-pw-v1` und den
zugehörigen Synchronisierungsstatus. Ein vorhandener alter Cache bleibt
unangetastet und wird nicht durchsucht. Der Benutzer wählt nötigenfalls einen
Job-/Quellstand, aber keine einzelnen Bildpfade. Gitrevision und
Produktionsrevision sind verschiedene Kennungen.

### 4.2 Lesend gegenüber dem Projekt

Der Dienst liest **committete Objekte**, nicht ungeprüft gemischte Arbeitsbytes.
Auch ein verschmutzter Benutzercheckout darf verbunden werden: Seine Änderungen
bleiben unangetastet und werden nicht als veröffentlichter Stand dargestellt.
Ein lokaler Commit ist im ausdrücklich eingerichteten lokalen Diagnosebetrieb lesbar;
daraus folgt keine Remote-Erreichbarkeit. Ein bestehender lokaler Betrieb wird
nicht automatisch auf Remote umgestellt. Im Remotebetrieb bleiben lokale Refs
für P2 und gezielte Diagnose verfügbar, ohne die aktive Auswahl zu bestimmen.

Die einmalige Einrichtung bietet „Nur lokale Gitstände“ oder „Mit konfiguriertem
Remote aktualisieren“. Im zweiten Fall werden beim Start und über eine klar
bezeichnete Aktualisierungsaktion die gewählten Refs in einen eigenen Gitcache
geholt. Der Browser öffnet vor dieser Arbeit; eine einzelne Hintergrundoperation
liefert Fortschrittsstatus und meldet auch einen Fehlerabschluss. Status- und
vorhandene Bildansichten bleiben währenddessen erreichbar. Aktualisieren erzeugt
keinen zweiten parallelen Suchlauf. Das ist ausschließlich Cachepflege. Außer der separat bestätigten lokalen Refbereinigung nach §4.4 keine
Schreiboperation im Benutzercheckout; kein Pull, Checkout, Reset, Stash, Add,
Commit oder Merge. Der einzige Push ist die konditionale Remoteentfernung nach §4.4.
Keine automatische Authentifizierungsänderung. Bestehende Git-Anmeldung nutzen;
kein GitHub-Token in HTML, Browserstorage, Prompt oder Protokoll aufnehmen.

Remote und erlaubte Refs kommen aus der bewusst bestätigten Einrichtung, niemals
aus einem Produktionspaket. Keine frei parametrierbare Git-/Shell-API. Kommandos
als Argumentlisten, ohne Shellauswertung; Submodule, Hooks, externe Filter und
beliebige Remote-Helper nicht als Teil des Lesepfads ausführen. Cachepflege darf
keine fremden Gitrefs löschen. Bei Offline-/Authentifizierungsfehlern einen
vorhandenen gebundenen Stand weiter anzeigen, aber Alter und Fehler klar nennen.

### 4.3 Konsistenz

Vor einer Anzeige jeden Ref in eine volle Commit-SHA auflösen. Index, Records,
Paket, Projektion und Bilder werden innerhalb dieser Ansicht ausschließlich aus
diesem Snapshot oder aus ausdrücklich darin gebundenen historischen Commits
gelesen. Keine Mischung aus `main` von eben und einem Bild vom späteren Head.

Doppelte identische ID-/Revisionsbindungen verschiedener Refs dürfen zusammen-
gefasst werden. Abweichende Bytes unter derselben ID/Revision sind ein Konflikt,
kein Anlass, nach Dateiname, Zeitstempel oder größter Revisionszeichenfolge zu
raten. Unterschiedliche angebotene Rasterrevisionen bleiben Angebote; eine
neuere Revision wird nicht automatisch gewählt oder freigegeben.

Ein Refwechsel während der Betrachtung lässt die aktive Ansicht unverändert.
Die Oberfläche meldet einen neueren Stand und lädt ihn ausdrücklich vollständig.
Alte Bildantworten dürfen nach Job-/Revisionswechsel keine neue Karte überschreiben.
Historische Bildreferenzen werden bei Bedarf aus den erreichbaren Gitobjekten
aufgelöst; fehlende Objekte sind Fehler, keine Aufforderung zum Einzelbildupload.
Es entsteht kein allgemeiner Archivbrowser für alte WIP.

Der eigene Cache holt nur die gewählten Branchspitzen mit flacher Historie und
ohne Bildblobs. Ausdrücklich gebundene historische Commits und benötigte Blobs
werden gezielt nachgeladen. Unveränderte Index-/Projektionsbefunde werden
commitgebunden in einem begrenzten Prozesscache wiederverwendet. Statusabrufe
lesen ausschließlich den zuletzt fertiggestellten Listenstand und starten
keine erneute Git-Suche.

### 4.4 P2 · ausdrücklich bestätigte Produktionsentfernung

[P2/K07](https://github.com/venomenon328/picross/issues/588#issuecomment-6808562897)
erlaubt genau eine benutzerinitiierte Ausnahme: den vollständigen ausgewählten
Remote-Produktionsbranch `refs/heads/content/pw/<puzzle_id>` entfernen. Keine
Revision einzeln löschen, keine Inhaltsdateien, Worktrees oder Mainintegration
entfernen. Produktion, Veröffentlichung und Freigaben bleiben beim Akteur.

Die Vorprüfung löst Job und aktuellen Listensnapshot serverseitig auf. Nur eine
konfliktfreie Remotequelle mit exakter ID-/Branchbindung ist zulässig. Produktiv
ist allein der bewusst konfigurierte GitHub-Remote `venomenon328/picross` über
HTTPS oder gewöhnliche GitHub-SSH-URL freigegeben. Rein lokale Quellen und andere
Remotes bleiben lesbar, ihre Löschfunktion ist gesperrt. Lokale Bare-Remotes sind
nur über einen kontrollierten Testadapter in isolierten Prüfungen zulässig;
weder Einrichtung noch HTTP-API besitzen dafür einen Freigabeschalter.

Die Vorschau nennt Repository, Quelltyp, exakten Ref, frische Remote-SHA, alle
sichtbaren Revisionen des Branches, lokale SHA/Worktrees, PR-Befunde und auf main
vorhandene Stände. Effektive Fetch-/Pushziele werden geprüft; versteckte
Pushziele, Mehrfachziele, URL-Rewrites und Redirects werden nicht akzeptiert.
GitHub-Repositoryidentität und öffentliche Sichtbarkeit werden lesend verifiziert.
Die paginierte Pull-Request-Abfrage nutzt `head=owner:branch` und `state=all`.
Unprüfbare PRs oder offene PRs sperren; geschlossene ungemergte PRs warnen,
gemergte PRs und vorhandene Mainstände erklären die erhaltene Integration.

Alle verknüpften Worktrees und der exakte lokale Branchref werden geprüft.
Ausgecheckter Zielbranch oder abweichende lokale SHA sperren die ganze Aktion.
Dirty-Arbeitsbäume anderer Branches bleiben unberührt und blockieren nicht.
Vorprüfung verändert keine aktive Ansicht oder Quelldatei. Bestätigung verlangt
einen eigenhändig eingegebenen exakten Branchnamen und einen einmaligen,
kurzlebigen Sitzungsplan, gebunden an Job, Snapshot, Ziel und Vorprüfungsbefunde.
Vor dem Push werden diese Prüfungen frisch wiederholt. Refresh und Transaktionen
laufen seriell; die reine Statusabfrage bleibt erreichbar.

Git erhält ohne Shell genau eine Lösch-Refspec und eine explizite
`--force-with-lease=<voller Ref>:<erwartete SHA>`. Hooks werden abgeschaltet;
nur vorhandene nichtinteraktive Anmeldung wird benutzt. Keine neuen Credentials
im Browser, Zustand oder Log. Erfolg verlangt danach das tatsächlich geprüfte
Fehlen des exakten Remote-Refs. Push-/Timeout-/Berechtigungsfehler, unbekannter
Ausgang und fehlgeschlagene Cachesynchronisierung bleiben getrennte Resultate.
Erst verifizierter Erfolg aktualisiert die Remoteansichten.
Mainquellen werden weiter gelesen; ihre aktive Auswahl folgt dem lieferbezogenen
Abgleich und der Remoteautorität. Lokale Refreste bleiben für P2 prüfbar.
Offene oder unklar zugeordnete Arbeit bleibt sichtbar. Bei Cachefehler wird eine
stale Anzeige ausdrücklich benannt.

Ein noch vorhandener identischer lokaler Branchref kann erst danach separat
vorgeprüft und ausdrücklich bestätigt entfernt werden. Die Option ist anfangs
aus. Erneute Worktree-/SHA-/Remoteprüfung und ein bedingtes `update-ref -d`
verhindern die Entfernung eines inzwischen geänderten Refs. Nie Checkout,
Worktree, Bild, ZIP, Ordner oder andere Refs löschen. Unsichere Reste bleiben.

Die API ergänzt nur `/api/removal/preview` und `/api/removal/confirm` als POSTs
mit striktem kleinen UTF-8-JSON (maximal 2048 Bytes). Vorprüfung nimmt entweder
opake Job-/Snapshot-IDs oder die serververgebene Quittung für die lokale Folgeaktion;
Bestätigung ausschließlich opake Plan-/Job-/Snapshot-IDs und den Bestätigungstext.
Alle sonstigen API-Aufrufe behalten ihr Bodyverbot. Sitzung, Host, Origin und CSP
bleiben verbindlich. Kein allgemeiner Gitwriter, keine freie URL-/Ref-/Pfad-API.

Kleine Git-/Endpointregressionen laufen nur im gewählten `tools`-Modul. Echte
isolierte Remotetransaktionen und die Windows-/Browserbedienprobe sind einmalige
P2-T01–T03-Nachweise; ausschließlich synthetische Testrefs dürfen dafür entfallen.
Die nicht gelieferten P2-Browser-/PNG-/A01-Gates wurden durch die
[Eigentümerentscheidung](https://github.com/venomenon328/picross/pull/590#issuecomment-6809311950)
aufgehoben. P3-Paketierung und deren neue Nachweise bleiben separat.

### 4.5 P3 · Instanz, Origin und geordneter Stop

`config.json`, explizite Ref-/Remotewahl und vorhandene PW-Caches bleiben erhalten.
Neue Launcherdateien liegen getrennt in `.launcher/`. Ein OS-Dateilock sichert
atomar pro Benutzer und kanonischem Zustand; kurzlebige Instanzschlüssel erhalten
unter Windows eine geschützte DACL für den eigenen Benutzer und SYSTEM.
Datei-PID/-Portwerte allein erlauben weder Übernahme noch Prozessbeendigung.
Versionierter Kontrollweg `/control/v1`: ausschließlich challenge-authentisierte
Identifikation, Öffnen und Stop, mit signierter Antwort und eigener Instanz-/
Buildbindung. Keine freien Pfade, Ziel-URLs oder Programme. Die passend gebundene
Browseradresse wird ausschließlich nach Authentisierung zurückgegeben; Geheimnisse
erscheinen nicht in Logs, Prompts oder dauerhaften Optionen. Bestehender Browser-
Sitzungs-/Host-/Origin-/CSP- und P2-Bestätigungsschutz bleibt bestehen.

Die erste Bereitschaft und Browseröffnung gehen der Git-Suche voraus. Beim
installierten Windows-GUI-Start mit bestehendem Update-Opt-in wartet gemäß
[APP-B2-S / Updatevertrag §7](PRODUCTION_UPDATES.md#7-app-b2--client-übergabe-und-abschluss)
zuerst die Browseröffnung samt initialer Git-Suche auf die nebenläufige
Updateentscheidung. Das native Fenster bleibt bedienbar; „Ohne Update fortfahren“
verwirft den Versuch und gibt den einmaligen Arbeitsstart frei. Ein Zweitstart
übersteuert dieses Gate nicht. Ohne Updatefreigabe startet der bisherige Weg.
Die Loopbackadresse wird ab P3 pro Zustand gespeichert und wiederverwendet. Bei
Fremdbelegung kein stiller Portwechsel: Wiederholen oder ausdrücklich neuen Port
mit Hinweis auf getrennte Browseroptionen/Entwürfe wählen. Frühere Zufallsport-
Browserdaten bleiben unverändert; Migration wird nicht behauptet. Eine historische
CMD ohne Protokoll zuerst regulär beenden. Produktionsbranches und Datencheckout
liefern niemals ausführbaren Code. Fehlende Reader, UI/Tcl/Tk und echte
Pillowdekodierung werden vor Bereitschaft geprüft.

Fensterschließen und „Assistent beenden“ sperren neue Arbeit, warten auf eigene
Requests und Worker und geben Port/Lock erst nach deren Ende frei. Eine begonnene
P2-Transaktion samt Ergebnisprüfung läuft unverändert aus; unbekannter Ausgang
bleibt unbekannt, kein automatischer Retry. Keine pauschale Python-/Gitbeendigung.
Minimieren/Tab schließen stoppt nicht. Absturzreste werden nach tatsächlich
freigegebenem OS-Lock ersetzt, nicht anhand eines PIDs als sicher angenommen.
Updates ersetzen nach vollständigem Stop per neuerem MSI alle installierten
Programmdateien gemeinsam. Der [APP-A-Releasekanal](PRODUCTION_UPDATES.md) plant
Produktversionen aus der veröffentlichten Releaseautorität; bis zu dessen
Aktivierung gibt es keine neuen automatischen Veröffentlichungen.
[release.json](../../tools/production_workspace/release.json) bleibt 0.1.0-Startanker
und stabile Paketidentitäts-/Pinquelle, unabhängig von Authoring,
Spielversion und der alten Paketkennung 588-P3. Feste Upgradeidentität, neue
ProductCodes je Version, keine Same-Version-Installation und kein Downgrade.
Installation ohne Elevation unter dem eigenen per-user-Programmverzeichnis;
Startmenü und optional Desktoplink. Konfiguration/Refs/Remote, Cache, `.launcher`-
Dateien/Port, Browserprofil und externer Checkout bleiben beim Update, Uninstall
und Wiederinstallieren erhalten. Uninstall entfernt nur eigene Programmdateien,
Links und den Anwendungseintrag; alte portable Ordner bleiben unangetastet.
Gitrefresh ist kein Appupdate. Ein Windows-Lebenszeichen pro Benutzer/Produkt
gilt unabhängig vom `--state` schon während Einrichtung und bis nach dem Drain.
Vor Dateimanipulation prüft MSI dieses Zeichen, den älteren Standardzustandslock
und belegte Payloaddateien über Restart Manager. Laufend, fremd oder unklar:
verständlich abbrechen und nach regulärem Stop wiederholen; kein Kill, kein
automatischer Stop/Restart und keine erzwungene Rebootaktion. Neue Launcherstarts
während der Windows-MSI-Ausführung werden zurückgewiesen. Der getrennte Bau
hat einen isolierten erfolgreichen Main-CI-Folgetrigger und diagnostischen
`workflow_dispatch`; keinerlei Einbindung in Package CI. APP-B2 ergänzt den
Opt-in-Updater gemäß Updatevertrag; kein dauerhafter Dienst. Das App-Image und der Installer sind ohne Zertifikatauftrag unsigniert;
Lizenzen und mögliche SmartScreenhinweise gehören zur Lieferung.

## 5. Warum eine veröffentlichte Ansichtsprojektion nötig ist

Der aktuelle [Builder](../../tools/puzzle_production/authoring_builder.py) erzeugt
`record`, Handoff und Paket; seine `sheet_from_record`-Projektion setzt die
Rasteroptionsliste zunächst auf `[]`. Die gemeinsame Angebotsliste wird nach
[Authoring §7](../production/authoring/PUZZLE_AUTHORING.md) bislang in der Chatübergabe
geführt. Ein Repositoryreader darf diese nicht aus allen gefundenen PNGs oder
der lexikografisch letzten Paketrevision erraten.

Für neue, mit PW veröffentlichte Arbeitsstände kommt deshalb eine kompakte
**`workspace.json`-Ansichtsprojektion** neben den zuständigen `record.json`.
Sie enthält keine neuen Proofs oder Freigaben und ersetzt kein Originalpaket.
Sie macht die tatsächlich angebotenen Optionen und ihre Bildbezüge maschinen-
lesbar im Repository verfügbar. Fachliche Werte müssen zu den referenzierten
Originalrecords, Handoffs, Inventaren und Entscheidungen passen; bei Konflikten
wird die Projektion abgewiesen, nicht zur neuen Wahrheit erklärt.

Der Produktionsakteur lässt sie automatisch aus seinem vorhandenen Arbeitsstand
erzeugen und sichert sie mit den zugehörigen Quellen in demselben
Phasen-Sicherungscommit. Kein zusätzlicher manueller Benutzerschritt. Ein
veröffentlichtes Bild-/Rasterangebot ohne erreichbare Originale und gültige
Projektion ist für den neuen Assistenten nicht vollständig übergeben.

PW-A liefert dafür einen kleinen Projektor mit API/CLI neben dem bestehenden
Paketbau. Er schreibt ausschließlich eine neue, geprüfte `workspace.json` in die
zugehörige lokale Arbeitsrevision. Ein identischer Wiederholungsaufruf ist No-op;
abweichende bereits veröffentlichte Bytes werden nicht überschrieben. Record,
Handoff, ZIP, Entscheidungen, Index und Spielkatalog bleiben unverändert.
Die normale beauftragte Git-Sicherung bleibt Aufgabe des Produktionsakteurs.
Vor Publikation die gebundenen Quellbytes erneut vergleichen; bei zwischen-
zeitlicher Änderung keine scheinbar passende Projektion veröffentlichen.

PW3-B teilt ausschließlich innerhalb eines Projektor-/Detailprüfaufrufs bereits
gelesene Quell- und ZIP-Mitgliedbytes sowie geprüfte Recordmetadaten und
Bilddekodierbefunde. Der gemeinsame Bytevorrat ist auf 64 MiB/512 Einträge
begrenzt; Verdrängung führt zum gewöhnlichen vollständigen Lesen. ZIPs werden
weiter einzeln geöffnet und geschlossen, ihre Namespaces und CRCs vollständig
geprüft. Jede Referenz behält ihre eigene Hash-/Größen-, Index-, Rollen- und
Angebotsprüfung. Vor Rückgabe einer lokalen Detailprüfung und an den bisherigen
Projektor-Publikations-/No-op-Grenzen werden alle ursprünglichen Quellbytes
frisch gelesen und verglichen, einschließlich Dateiidentität und Pfadschutz.
Danach und bei Fehler/Abbruch endet der Vorrat. Ein unabhängiger Detail-/Bildabruf
beginnt ohne diesen Kontext. Keine gespeicherte Prüfautorität, keine Übernahme
von Adapter-/Proof-/HP-W2-Ergebnissen und keine Zusammenlegung verschiedener
Finalizerzustände oder Export-/Offlineprüfgrenzen.

PW-B integriert diesen Aufruf verbindlich in jede fällige Übergabe des neuen
Produktionswegs. Die bisherigen Chat-Sheet-Daten können als Diagnose entfallen;
der Nutzer muss sie nicht mehr in eine zweite Datenhaltung kopieren.

## 6. Geschlossener Sichtvertrag für PW-A

### 6.1 Datenform

`picross-production-presentation-v1` enthält genau:

| Feld | Bedeutung |
| --- | --- |
| `format` | Exakt `picross-production-presentation-v1` |
| `puzzle_id`, `revision` | Bestehende gültige Authoring-ID und Revision des äußeren Arbeitsrecords |
| `record` | Bytebindung des zugehörigen äußeren Records gemäß untenstehendem Referenztyp |
| `title` | Kurzer redaktioneller Anzeigename; keine neue Namensautorität für das Spiel |
| `assets` | Liste tatsächlich verfügbarer Betrachtungsdateien |
| `offers` | Liste der in dieser Lieferung tatsächlich angebotenen Auswahlmöglichkeiten |

Eine Dateireferenz enthält genau `commit,file,sha256,bytes`.
`commit=null` bedeutet den vom Reader bereits fixierten Publikationssnapshot;
eine volle SHA bezeichnet eine explizite historische Quelle im selben
Repository. `file` ist ein sicherer repositoryrelativer Pfad; SHA-256 und
Bytezahl werden aus den tatsächlichen Bytes bestimmt. Es wird kein zukünftiger
Sicherungscommit in die Datei hineingeschrieben: dadurch keine Commit-Selbstreferenz.
Der äußere `record` liegt an der kanonischen ID-/Revisionsposition des Index.

Jedes Asset enthält genau `id,role,caption,location`.
`role` ist `reveal`, `motif`, `raster`, `raster_draft` oder `background`.
`location` enthält genau `commit,storage,container,file,sha256,bytes`:

- `storage=repository`: `container=null`, `file` ist der gebundene relative
  Dateipfad im erlaubten Produktionsbaum.
- `storage=package`: `container` ist genau `{file,sha256,bytes}` für das
  Original-ZIP im Repository; `file` bezeichnet dessen sicheren Mitgliedspfad.
  Beide liegen im durch `location.commit` bestimmten Snapshot.

Jedes Angebot enthält genau `id,kind,label,record,asset_ids`.
`kind` ist `reveal`, `raster` oder `background`; `record` bindet die dafür
zuständige echte Revision derselben Rätsel-ID. `asset_ids` verweist auf die
passenden Assets dieser Projektion. IDs sind je Liste eindeutig und folgen
den vorhandenen Options-ID-Grenzen. Kein verstecktes `approved=true`, keine
Auswahl aus der Listenreihenfolge, keine freien URLs oder absoluten Pfade.

`title`, `caption` und `label` sind nichtleere Klartexte mit höchstens 512 Zeichen.
Höchstens 100 Assets und 20 Angebote je Projektion; der eigentliche Dreier-
Hintergrundauftrag wird dadurch nicht erweitert. Die Projektionsdatei bleibt
höchstens 1 MiB. Diese Grenzen schützen den lokalen Leser, sind keine Grenzen
für CI-Artefakte oder eine erzwungene Produktionsausbeute.

### 6.2 Ableitung und Prüfung

Projektor und Reader prüfen ID/Revision, geschlossene Formen, referenzierte
Dateien und tatsächliche Hashes. Das Paket muss dem Record entsprechen; äußere
Handoffkopie und Inventarbindung müssen stimmen. Assetrollen werden mit den
jeweiligen Originalbezügen abgeglichen: Revealangebote/-auswahl, Motivbezug,
konkreter Rasterkandidat und dessen inventarisierte Ansicht beziehungsweise
Hintergrundmanifest samt Kandidatenrevision. Eine fremde PNG mit passendem
Namen ist keine passende Option.

Rasterangebote binden jeweils ihre eigene Revision, den tatsächlichen
Handoffkandidaten und eine passende vollständige vorhandene Inhaltsprüfung;
`raster_ready` mit offener Hintergrundarbeit ist dabei zulässig. Ein
`raster_draft` kann betrachtet werden, gehört aber nicht in ein freigabefähiges
Rasterangebot. Die Anzeige benennt den fachlichen Zustand als überlieferten
Produktionsbefund. Der Reader führt keine neue Solver-/Proof-/Difficultyprüfung
und erteilt kein eigenes Inhaltszertifikat.

Die Angebotsmitgliedschaft und kurze Beschriftung liefert der Produktionsakteur
aus der tatsächlich erstellten Auswahlvorlage. Der Projektor übernimmt keine
ungeprüften Hashangaben und erfindet keine Angebote durch Verzeichnissuche.
Vor dem Implementieren die Requestschema-Datei für den Projektor aus exakt diesen
Eingaben ableiten; sie darf nur Identitäten/Beschriftungen und vorhandene
Quellreferenzen transportieren, keine Erfolgs- oder Freigabeoverrides.

Der Index bleibt der vorhandene `content/authoring/index.json`. Der Reader sucht
neben dessen kanonischen Records nach `workspace.json`; fehlende Projektionen
sind nicht für PW veröffentlicht und werden nicht automatisch konvertiert.
Es gibt keinen Scan aller Bilder im Repository. PW-A wird an neu erzeugten
synthetischen heutigen Handoff-v3-/Record-v2-Paketen geprüft. Das ist die
Wiederverwendung vorhandener Formen, kein Auftrag, den bestehenden WIP-Bestand
lesbar zu machen. PW-B bindet den neuen Authoringstand ausdrücklich an die
angepassten Fachleser.

## 7. Lokale Auslieferung und Schutzgrenzen

Eine kleine Pythonanwendung stellt vertrauenswürdige UI-Dateien und eine eng
begrenzte JSON-/Bildschnittstelle bereit. Keine Freigabe des gesamten Checkout-
Verzeichnisses durch einen generischen Dateiserver. Nur Loopback binden; Host
und Origin gegen die tatsächlich gestartete Adresse prüfen. Ein zufälliges
Sitzungsgeheimnis schützt sämtliche Daten-/Aktualisierungszugriffe. Keine
freigebende CORS-Konfiguration. Ein fremder Browserursprung darf weder Inhalte
lesen noch Aktualisierungen auslösen. Geheimnisse nicht in Logs oder kopierte
Aufträge aufnehmen.

Die Oberfläche und die API stammen aus demselben vertrauenswürdigen
Programmstand. Betrachtete Produktionsbranches liefern ausschließlich Daten,
niemals ausführbaren UI-/Python-/JavaScriptcode. HTML aus einem Paket wird
nicht ausgeführt, SVG nicht als aktive Webseite eingebettet. Text als Text
rendern. CSP gezielt auf eigene UI-/API-Ressourcen und lokal erzeugte
Bild-Blob-URLs begrenzen; keine pauschale Freigabe beliebiger Netzwerkziele.

HTTP-Endpunkte akzeptieren serverseitig vergebene Snapshot-/Job-/Assetkennungen
und die eng begrenzten Löschbestätigungen nach §4.4,
keine beliebigen Dateipfade, Shellkommandos, URLs oder Archivpfade. Der Server
löst ausschließlich die von validierten Projektionen freigegebenen Ressourcen
auf. Gitobjekte nach Typ und Größe prüfen; Symlinks, Submodule und Links aus dem
Produktionsbaum heraus nicht verfolgen. Pfade in ZIPs vollständig normalisieren;
Elternpfade, absolute Pfade, Laufwerke, Aliase, doppelte/Windows-kollidierende
Namen, Dateitypkonflikte und Spezialdateien ablehnen.

Die aktuellen [Authoring-Paketgrenzen](../../tools/puzzle_production/authoring_package.py)
bleiben maßgeblich: ZIP höchstens 128 MiB, einzelne Datei höchstens 64 MiB,
2048 Dateien und insgesamt höchstens 512 MiB entpackte Daten. CRC, tatsächlich
gelesene Bytezahl und SHA-256 prüfen. Nur benötigte Mitglieder lesen; keine
rekursive Entpackung weiterer Archive. Bewährte vorhandene Guards wiederverwenden,
ohne dadurch unbeabsichtigt Solver/Export/Writer aufzurufen. PNG/JPEG anhand
Bytes und tatsächlicher Dekodierung prüfen; Bildressourcengrenzen der bestehenden
Produktionswerkzeuge erhalten. Bilder unverändert ausliefern. Jede Darstellung
mit künstlichem Prüfgrund ist eine Ansicht, kein neues Original.

Index-/Jobliste zuerst günstig lesen; Pakete und Originalbilder bedarfsabhängig
laden. Metadaten dürfen vor vollständiger Bildprüfung angezeigt werden, jedoch
mit entsprechendem Status. Keine vorzeitige Meldung „vollständig geprüft“.
Cacheeinträge an Gitblob, Paket-/Dateihash und Readerstand binden, begrenzen und
bei Neustart/Änderung korrekt prüfen. Keine vollständige Bestandsentpackung,
kein permanentes Kandidatenarchiv und kein Speichern sämtlicher Bilder im
Browserstorage. Langsame/abgebrochene Ladevorgänge lassen andere Jobs bedienbar.

## 8. Auftragstransport und Befugnisse im vollständigen Assistenten

PW-B erzeugt pro Handlung einen kurzen, überprüfbaren Auftrag mit Repository,
fixiertem erreichbarem Quellencommit, einem kanonischen Recordpfad als Einstieg
und tatsächlichen Auswahl-IDs. Daraus erreichbare Parameter, Briefings, Hashes,
Paket-/Projektionspfade und allgemeine Regeln werden nicht in Folgeaufträge kopiert.
Ein kurzer verbindlicher Verweis auf AGENTS und Authoring 0.8.0 genügt; er aktiviert
die phasenbezogene Quellenroute einschließlich des gemeinsamen Bildstils, nicht
die Volllektüre aller Fachhandbücher. Nur neue Absicht, Freigabe, Änderung oder
Aufhebung sowie persönliche Befugnisse ergänzen.
Ein neuer Erstauftrag enthält dagegen Motiv, Hinweise, Referenz und frühe Wünsche.
Der Empfänger löst die vollständigen Definitionen und Bilder aus diesen Quellen
auf. Ein relativer Paketpfad allein beweist keinen Zugang. Cloudschritte dürfen
keine localhost-Adresse oder bloß lokale Windowsdatei als erreichbare Quelle
bekommen; ungesicherte neue Bilder erst passend veröffentlichen.

Vorgefüllte Quellwerte sind keine neue Absicht oder Freigabe. Der Folgeauftrag
trennt den veröffentlichten Kontext von Änderungen, ausdrücklich aufgehobenen
Rasterwünschen und neuen/zusätzlichen Wünschen zur Motivvorlage. Bloßes Leeren
oder „Offen“ hebt einen vorhandenen Wunsch nicht auf; dafür gibt es eine eigene
beschriftete Aufhebungswahl je Achse beziehungsweise Modus/Farbzahl. Sie hat Vorrang
vor den betroffenen Eingabefeldern; die andere Achse bleibt unverändert wirksam.
Ein geänderter freigegebener Korridor geht über den bestehenden Korrekturweg zur
erneuten Entscheidung. Die bewusst angeforderte reguläre Freigabe in Schritt 3
bleibt erhalten.

Die Auswahl im Assistenten ist zunächst Bedienabsicht. Erst der ausdrücklich
abgesendete Auftrag erklärt eine Bild-/Motiv-/Endfreigabe oder beauftragt eine
Integration. Ein neuer Quellstand oder geänderte relevante Bildbytes entwerten
stale Auswahlabsichten gezielt. Kein automatischer Modellaufruf, keine Modell-API,
kein Freigabewriter im Hilfsdienst und keine automatische Serienfreigabe.

Die lesende Oberfläche darf aktuelle Repositorydaten automatisch übernehmen;
unabgesendete menschliche Eingaben nicht unbemerkt überschreiben. Persönliche
Arbeitswurzel und Merge bleiben eigene ausdrücklich angezeigte
Auftragsparameter, keine aus einem Produktionsrecord abgeleiteten Rechte.
Der Assistent fordert keine zusätzliche Bereinigung lokaler Arbeitsdaten an;
eine frühere gespeicherte Bereinigungsoption hat keine Wirkung. Der separate
fachliche Produktionsabschluss nach Authoring §9 bleibt unverändert. Bei neuem Job muss dessen Motivbriefing im kopierten Erstauftrag stehen;
noch nicht vorhandene Repositorydaten werden nicht als existent behauptet.

Die normalen beauftragten Produktionsakteure committen/pushen Index, Record,
Projektion und Originale an den fälligen Übergängen. Merge bleibt entsprechend
dem tatsächlichen Auftrag getrennt. Nach vollständiger Mainintegration gilt
Authoring §9. Der Assistent zeigt danach den bestätigten Abschluss und gültige
Runtime-/Belegbezüge, keine defekten Links auf entfernte Zwischenbilder.

## PW2-B · Schlussübersicht und gebundener Auftrag

Die normale Hintergrundentscheidung zeigt zuerst das tatsächlich gewählte Raster,
dessen Reveal und die vorgemerkte Hintergrunddatei beziehungsweise `none`. Der
primäre Schlussauftrag erklärt diese konkrete Wahl, Endabnahme und Integration
zusammen. Er enthält Commit/PR, unabhängiges Review, Squash-Merge erst nach
aktuellen Vor-Merge-Gates und den bestehenden Produktionsabschluss nach Authoring
§9. `content_ready`, echte äußere Endfreigabe, Finalizer, Export/Plan/Register und
bestätigtes main bleiben getrennte technische Tatsachen; kein UI-Writer entsteht.

Ohne gültigen gespeicherten Mergewert ist der bedingte Merge eingeschaltet. Ein
explizites gespeichertes `false` bleibt erhalten. Die Option und die Wirkung des
konkreten Schlussauftrags sind sichtbar; Kopieren ist noch kein Absenden.
Korrektur und Wiederaufnahme erzeugen weder eine neue Endabnahme noch eine neue
Mergefreigabe. Vorhandene passende Endabnahmen werden nicht erneut erklärt.
Unveränderte Quellenwerte und allgemeine Regeln werden nicht im Prompt wiederholt;
Auftrag, feste Recordquelle, neue Absichten und persönliche Arbeitswurzel bleiben.

Die interne lesende Detailantwort ergänzt `facts.metadata` aus den vorhandenen
Recordfeldern `width,height,mode,used_colors,difficulty`, `facts.originals` mit
vollständigem geprüftem `record,handoff` und `facts.composition` mit den Asset-IDs
`raster,reveal,background`. Die Komposition ist vor tatsächlicher Rasterwahl null.
Spätere IDs stammen ausschließlich aus den Originalbezügen des äußeren Records;
die inventarisierte Rasterwahl samt unveränderten Quellkopien und Bild-/Kandidaten-
bindungen wird lesend abgeglichen. Fehlende/uneindeutige Auswahl wird nicht aus
Galerieordnung oder Dateinamen geraten. Äquivalente Referenzen desselben Originals
werden deterministisch nach ID zusammengefasst. Ein fehlender Rollenbezug bleibt
null und verhindert eine scheinbar vollständige Schlussfreigabe. Das sind
Ansichtsdaten, keine neuen Zertifikate oder Felder der geschlossenen Originalformen.

Bilder und relevante Parameter stehen vor dem Auftrag; handlungsrelevante Probleme
bleiben sichtbar. Der standardmäßig geschlossene, kopierbare Detailbereich unten
enthält Original-JSON, Hashes, Revisionen, Commit-/Import- und Diagnosebindungen.
Briefing und vollständige Parameter sind weiterhin erreichbar. Die vorhandene
Snapshot-, Bildlade-, Quellwechsel-, P2- und Origin-Sicherheit bleibt erhalten.
Der CMD-Fallback wird aus denselben Quellen regeneriert. Neue Originale der
Browserprobe dienen nur PW2-B-T01/A01 im Liefer-PR, nicht einer Dauergalerie.

## PW2-C · aktive Lieferungen und bestätigter Abschluss

Die Liste bestätigt abgeschlossene Lieferungen anhand der tatsächlichen aktuellen
Registry, Runtime und Livebytes am bestätigten `origin/main`. Ein unveränderter
abgeschlossener Stand bleibt auch in alten Branchkopien ausgeblendet; ein alter
Integrationshinweis allein genügt nicht. Dabei werden keine historischen ZIPs,
Receipts oder Provenienzen geöffnet. Noch benötigte frühere Phasen desselben
abgeschlossenen Vorgangs werden über unveränderte Record-/Projektionsbytes am
bestätigten Integrationscommit erkannt.

Ausdrücklich neu übergebene Frühphasen, neue Bild-/Rasterarbeit, abweichende
Livebytes, fehlende Mainbestätigung und defekte Ansichtsbindungen bleiben sichtbar.
Es gibt keine Rangfolge nach numerischen Revisionen. Der explizite aktuelle
Ansichtsverweis hat Vorrang vor der Vermutung, eine frühe Phase sei erledigt.

`projector.complete --input <current-input>` nutzt denselben erreichten aktuellen
Integrationszustand wie Plan/Write/No-op. Danach entfernt `retire` nur nachweislich
integrierte, ausdrücklich zugeordnete Arbeit: automatische registrierte Revisionen,
explizite frühere Revisionen und explizite gemeinsame Arbeitsverzeichnisse.
Die Prüfung verlangt einen bestätigten Mainstand und identische Gitbytes; fremde
oder wiederaufgenommene Daten blockieren. Der aktuelle Pointer wird mit entfernt,
wenn er genau auf die entfernte Arbeit verweist. Keine Abschlussreceipt,
Zählerfortschreibung oder neue Bild-/Rasterfreigabe. Einzelheiten und Befehle in
[Authoring Schritt 5](../production/authoring/PUZZLE_AUTHORING_STEP_5.md).

## 9. Herkunft der Schnittstellen

PW-A/PW-A2 führten Projektor, lesenden Dienst und Launcher ein; PW-B den heutigen
Produktionsweg. Ihre damaligen Paketgrenzen sind im
[gebundenen Vorgänger](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PRODUCTION_WORKSPACE.md)
erhalten. Sie definieren keine heute erneut offene Einführung oder persönliche
Abnahme. Die Anleitung steht unter [tools/production_workspace](../../tools/production_workspace/README.md).

## Quellen

Für normale Produktion gilt ausschließlich das operative Routing am Anfang
und in Authoring §1.1. Die folgende Liste ordnet Entwicklungs-/Herkunftsquellen
zu und erteilt keine zusätzliche pauschale Volllektüreplicht:

[Workflow](../dev-rules/WORKFLOW.md), [Projektprofil](../PROJECT_PROFILE.md),
[Authoring](../production/authoring/PUZZLE_AUTHORING.md), [Bildstil](../production/images/README.md),
[Hintergrundvertrag](../production/PUZZLE_BACKGROUNDS.md), [Qualität](../production/PUZZLE_QUALITY.md),
[Produktionswerkzeuge](../../tools/puzzle_production/README.md),
[CI v2](../ci/CI_WORKFLOW_V2.md), [CI-Vertrag](../dev-rules/CI_CONTRACT.md).

Technische Referenzen zur Umsetzung: [Git-Objektzugriff](https://git-scm.com/docs/git-cat-file),
[Python-HTTP-Sicherheitsgrenzen](https://docs.python.org/3/library/http.server.html#security-considerations),
[CSP und lokale Verbindungen](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/connect-src).
Ein bloßer Aufruf von `python -m http.server` erfüllt die hier definierten
Zugriffs- und Autoritätsgrenzen nicht.

## PW-PERF-B · Begrenzte Erstregistrierungsprüfung

Aktueller Integrationseingang und Quellen-/Recoverygrenzen stehen ausschließlich
in [RI-ONE](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md). Der Assistent zeigt gebundene
Lieferstände an; er erzeugt daraus keine Schreib- oder Mergefreigabe.

## PW-PERF-C · aufrufgebundene Prüfung und Hintergrund v2

Aufrufgebundene Finalisierung und Quellprüfung: [PW-B](PW_B_CONTRACT.md#pw-perf-c--aufrufgebundene-prüfung-und-hintergrund-v2).
Bildableitung und Profilformen: [Hintergrund §4](../production/PUZZLE_BACKGROUNDS.md#4-hp-w2-eigenständige-datei--und-ableitungsschnittstelle).
