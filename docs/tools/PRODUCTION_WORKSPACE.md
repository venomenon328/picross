# PW: Produktionsassistent

In der Auswahl zeigt der Assistent die gebundenen Angebote. Bei Hintergrundangeboten zeigt das Bild die vorbereitete PNG-Datei. Fehlende Voraussetzungen und konkrete Befunde stehen am Kandidaten. Die kombinierte Schlussentscheidung verwendet die angezeigte Revision.

## Geltung und Quellen

- **Status:** aktiver Vertrag für Oberfläche, lokalen Git-/Bildzugriff und Ansichtsprojektion.
- **Normale Produktion:** ausschließlich [Authoring-Quellenroute](../production/authoring/PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase); dieser Gesamtvertrag ist keine pauschale Produktionspflichtlektüre.
- **Geschlossene Authoring-/Projektionsformen:** [PW-B](PW_B_CONTRACT.md).
- Für den schreibenden Akteur richtet [PW-LOCAL](PRODUCTION_GIT_WORKSPACE.md) die gemeinsame Gitbasis ein. Der [Remote-Einstieg](PW_REMOTE.md) orchestriert denselben Fachkern für den schreibenden Akteur. Die App verwendet ihren eigenen lesenden Cache.
- **Aktuelle Ansicht und Lieferung:** [PRODUCTION_CURRENT_VIEW](PRODUCTION_CURRENT_VIEW.md).
- **Installer und Updatekanal:** [PRODUCTION_UPDATES](PRODUCTION_UPDATES.md); tatsächlicher Betriebsstatus im zuständigen Issue/Release.
- **Bildgestaltung und Profile:** [Bildnormen](../production/images/README.md) beziehungsweise [Hintergrundtechnik](../production/PUZZLE_BACKGROUNDS.md).

Unter „Einstellungen für Google Drive“ speichert der Benutzer Stammordner-ID und
synchronisierten Windows-Pfad. Der normale [Empfangsauftrag](PW_IMPORT.md)
verwendet die ausgewählte Produktion, den v3-Builder, einen eigenen PW-LOCAL-Store
und die lokale gh-Anmeldung. Die veröffentlichte Ansicht bleibt lesend. Der
[Schritt-5-Writer PW-FINAL](https://github.com/venomenon328/picross/issues/907)
bleibt ein eigener anschließender Umfang.

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

Die aktuellen Datenformen und der Bestandsschutz für bereits gebundene
Mono-Vorschauen stehen im [PW-B-Vertrag](PW_B_CONTRACT.md#rastervorschau-und-bindung).
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
  Genauigkeit der ausgefüllten Achsen, Modus und die Vordergrundfarbzahl mit
  eigener Genauigkeit. Die Farbzahl lässt sich auch bei offenem Modus vorgeben.
  Wünsche werden im Motivbriefing des Produktionsauftrags
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
Rasterwünsche und den als freigegeben überlieferten Korridor getrennt. Quelle ist ausschließlich der aktuelle Record nach PW-B. Ein Statuswort beweist keine menschliche Freigabe. Eindeutig
abbildbare Einzelwünsche belegen die Rasterfelder vor, andere Formen und mehrere
Optionen bleiben vollständig lesbar. Fehlende strukturierte Einzelwerte sagen
nichts über freie Wünsche im Motivbriefing aus. Vollständige Parameteroriginale und veröffentlichtes
Motivbriefing sind beim Öffnen, Wiederladen und Motiv-/Revisionswechsel geschlossen;
Zusammenfassung, Quellenstatus und Fehler bleiben davor sichtbar. Das aktuelle Briefing steht direkt im geprüften Record.
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
nur Indexeinträge der im Branchnamen gebundenen Rätsel-ID. Der gültige Katalog am gebundenen
`main` bestimmt die dauerhafte Ausblendung bereits registrierter IDs vor dem
Scannen der Arbeitsbranches und dem Lesen der Main-Records (PW2-C). Für die
Katalogbindung wird main auch bei einer engeren Arbeitsrefauswahl gelesen.
Der Produktionsakteur veröffentlicht neue PW-Übergaben auf dem zugehörigen
Branch und schließt ihn nach bestätigter Integration nach Authoring Schritt 5 §9 ab.

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
keine fremden Gitrefs löschen. Bei Offline-, Authentifizierungs- oder Katalogfehlern zeigt PW den letzten
erfolgreich gebundenen Listenstand als veraltet an. Beim Neustart gelten dessen
gesicherte Commits. Ohne gebundenen Stand zeigt PW den Ladefehler.

### 4.3 Konsistenz

Vor einer Anzeige jeden Ref in eine volle Commit-SHA auflösen. Index, aktueller Record, abgeleitete Ansicht und Bilder werden innerhalb dieser Ansicht ausschließlich aus
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

Bei bisherigen Git-Records erhält Git ohne Shell genau eine Lösch-Refspec und eine explizite
`--force-with-lease=<voller Ref>:<erwartete SHA>`. Hooks werden abgeschaltet;
nur vorhandene nichtinteraktive Anmeldung wird benutzt. Keine neuen Credentials
im Browser, Zustand oder Log. Erfolg verlangt danach das tatsächlich geprüfte
Fehlen des exakten Remote-Refs. Push-/Timeout-/Berechtigungsfehler, unbekannter
Ausgang und fehlgeschlagene Cachesynchronisierung bleiben getrennte Resultate.
Erst verifizierter Erfolg aktualisiert die Remoteansichten.
Mainquellen bleiben mit dem ID-Filter nach PW2-C lesbar. Lokale Refreste
bleiben für P2 prüfbar. Fehler offener Produktionen bleiben sichtbar. Bei
Cachefehlern wird der letzte gebundene Listenstand als veraltet markiert.

Bei v2-Records legt PW mit der eingerichteten HTTPS- oder SSH-Git-Anmeldung
einen bedingten Auftragsref unter `work-prod-control/remove/` am bestätigten
Maincommit an. Job, Arbeits-SHA und die bei Bestätigung sichtbaren PR-Befunde
binden den Auftrag. Der erfolgreiche Arbeitsref-Check löst auf main den
[Actions-Auftrag](../../.github/workflows/work-removal.yml) aus. Dessen
Ausführungsjob verwendet das eingebaute Repositorytoken mit `contents: write`
und `pull-requests: read`. Er führt ausschließlich Code des bestätigten
Mainstands aus und authentifiziert seine PR-Prüfungen mit diesem Token.
Unter der gemeinsamen Katalogsperre prüft er erneut Main, Arbeitsref, offene
und geschlossene PRs, Record, Indexdelta, Release-ID, Tag und zugehörige
Asset-IDs. Nach dem gezielten Releaseabbau quittiert er am Auftragsref.
PW verwendet für Git die vorhandene Git-/SSH-Anmeldung und für öffentliche
Repository- und PR-Abfragen den unten beschriebenen optionalen REST-Zugang.
Die Worker-Authentifizierung wird mit dem Workflow auf main wirksam
und erfordert für PW-Installationen mit v2-Entfernung kein neues MSI.

PW wartet bis zu vier Minuten, wiederholt seine Vorprüfung und prüft anonym
die öffentliche Release-ID und den Tagnamen auf Abwesenheit. So kann ein vom
Tokenzugriff abhängiges HTTP 404 keine Entfernung bestätigen. Nach bestätigtem
Fehlen entfernt der Client Arbeitsref, vorhandenen gebundenen Tag und Quittung gemeinsam per
atomarem Lease-Push und prüft das Ergebnis. Bei Ablehnung, abgelaufenem Auftrag
oder unbekanntem Ausgang die Quellen aktualisieren und denselben Job neu
vorprüfen und bestätigen. Bis zum letzten Push bleibt der Arbeitsref erhalten.
Ein bereits abgebauter Release und eine zum selben Stand gehörige Quittung
sind wiederaufnehmbar. Der Client räumt seinen temporären Auftrag auch bei
kontrolliertem Abbruch bedingt auf. Die spätere lokale Refentfernung bleibt
separat bestätigt.

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

### Optionaler REST-Zugang unter Windows

Die Windows-EXE übernimmt beim Start das vorhandene `GH_TOKEN`, ersatzweise
`GITHUB_TOKEN`. Sind beide Werte in ihrer Prozessumgebung leer, liest sie diese
Benutzervariablen aus dem aktuellen Windows-Benutzerprofil. Das gilt auch beim
Wiederanlauf durch den getrennten Updatehelfer. Ohne Token bleiben öffentliche
Abfragen anonym. Ein geänderter Wert gilt nach vollständigem Beenden und
erneutem Start.

Der Wert bleibt flüchtig im Prozess. Der Assistent entfernt beide Variablen
vor dem Start von Browser, Git oder Updatehelfer aus seiner Prozessumgebung.
Gesendet wird der Token als Bearer-Header ausschließlich bei den festen
HTTPS-REST-GETs an `api.github.com` für Originalmetadaten, Repository-/PR-Daten
und den [Updatekatalog](PRODUCTION_UPDATES.md). API-Redirects werden abgewiesen.
Browser- und Assetdownloads laufen ohne Token. Browser, Prompts, Logs und
gespeicherter Arbeitszustand enthalten den Wert nicht.

Rate-Limits, Anmelde-/Zugriffsfehler und technische Abrufstörungen werden als
solche angezeigt. Ein authentifiziertes 404 kann auch fehlenden Zugriff
bedeuten. Nachgewiesene fehlende Quellen oder abweichende Originalbindungen
bleiben Quellenfehler. Bei einem nicht bestätigten PR- oder Releasebefund bleibt
die Entfernung gesperrt.

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
liefern niemals ausführbaren Code. Vor Bereitschaft prüft PW die benötigten
Reader, UI/Tcl/Tk, echte Pillowdekodierung sowie die vollständigen unveränderten
Ressourcen beider unterstützten Bewertungsmethoden. Fehlende oder beschädigte
interne Methodenressourcen werden als Programmpaketfehler auf Deutsch gemeldet.
Die Ressourcen- und Pfadbindung folgt
[WINDOWS_BUILD](../../tools/production_workspace/WINDOWS_BUILD.md). Der
Datencheckout liefert dafür weder ausführbaren Code noch Methodenoriginale.
Diese Startprüfung validiert Methodenidentitäten. Sie analysiert oder bewertet
kein Rätsel neu.

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

## 5. Direkt abgeleitete aktuelle Ansicht

Neue Jobs besitzen genau einen aktuellen Record nach [PW-B](PW_B_CONTRACT.md).
Der gemeinsame Index verweist darauf; kein persistiertes workspace.json oder
current-view.json ist erforderlich. Liste, Bilder, Angebots-IDs, tatsächliche
Auswahl, Briefing, Parameter und Folgeauftrag werden am selben fixierten Gitstand
daraus abgeleitet. Die Bedienung bleibt unverändert. Ein aktuelles Rasterpreview
bei reiner Hintergrundpflege wird aus der aktiven Definition nur für den Abruf
gerendert; keine neue Produktionsdatei oder Bildkopie.

## 6. Geschlossener Sichtvertrag

Aktuelle Rasterkachel und Großansicht verwenden dieselbe PNG-Ableitung aus
Definition und geprüftem Modus nach [PW-B](PW_B_CONTRACT.md#rastervorschau-und-bindung).
Die Angebotsüberschrift in beiden Ansichten stammt aus dem gebundenen Label.

Der Reader vergleicht die ganze abgeleitete Ansicht mit dem kanonischen aktuellen
Record und den tatsächlichen aktiven Datei-/Inhaltsbindungen. Fremde Angebote,
vertauschte Bilder und stale Auswahl scheitern. Technische Detailprüfung ist
keine neue kreative Entscheidung und führt im HTTP-Lesepfad keinen Solver aus.
Der geschlossene persistente Vertrag und die Limits stehen ausschließlich in
[PW-B](PW_B_CONTRACT.md); die vorhandene transiente Präsentationshülle bleibt
für die UI erhalten. Historische workspace-/Pointerformen werden ausdrücklich
als alte Formen erkannt und niemals still als aktuelle Daten etikettiert.

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
Nachgewiesene fehlende Originale bleiben als Quellenfehler sichtbar.
Interne Ladefehler bei Detail- oder Bildabruf erhalten eine feste Meldung zum
Programmstand ohne interne Pfade, Zugangsdaten oder Tracebacks.
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
die phasenbezogene Quellenroute einschließlich der zugeordneten Bildtypnormen, nicht
die Volllektüre aller Fachhandbücher. Nur neue Absicht, Freigabe, Änderung oder
Aufhebung sowie persönliche Befugnisse ergänzen.
Das gilt für alle Phasen, Korrekturen, Wiederaufnahme und spätere Bildaufträge.
Bei einer Korrektur bestimmt die Rolle der konkreten Arbeitsgrundlage die Phase:
Reveal 1, Motiv 2, Raster einschließlich Sichtungsentwurf 3, Hintergrund 4.
Dieselbe Zuordnung steuert Auftragskopf, Ausführungspräferenz, Vorschau und
Bildempfang; der globale Jobzustand ersetzt sie bei einem Rücksprung nicht.
Wiederaufnahme bleibt in der offenen Phase; nur Fortsetzen beziehungsweise
eine neue Auswahl darf den Folgeschritt beauftragen.
Neue Eingaben der jeweiligen Auftragsart bleiben im gekürzten Prompt erhalten. Allgemeine
Mono-/Farbregeln, Bildvorgaben, Publikationsbefehle, Prüf- und Abschlussverfahren
gehören ausschließlich in die Pflichtquellen. Auch passende Regeln werden nicht
als vorsorgliche Hinweise angehängt.
Ein neuer Erstauftrag enthält dagegen Motiv, Hinweise, Referenz und frühe Wünsche.
Der Empfänger löst die vollständigen Definitionen und Bilder aus diesen Quellen
auf. Ein relativer Paketpfad allein beweist keinen Zugang. Cloudschritte dürfen
keine localhost-Adresse oder bloß lokale Windowsdatei als erreichbare Quelle
bekommen; ungesicherte neue Bilder erst passend veröffentlichen.

Direkt bei Kopieraktion und Vorschau steht „Auftrag ausführen mit“ für alle fünf
Schritte und Auftragsarten. Maßgeblich ist die Phase im Auftragskopf. Eine
Rasterdiagnose mit anschließender Fortsetzung führt den Auftrag für Schritt 3
und behält die Folgeabsicht für Schritt 4. `pw-options` merkt sich die
Ausführungswahl pro Auftragsphase und Browserorigin. Ohne gültige Einstellung
gilt Codex in 1, 2 und 4 sowie ChatGPT in 3 und 5. Ein Wechsel aktualisiert
Vorschau und Kopieraktion und erhält ungesendete Absichten und den Mergeumfang.

Codex-Aufträge verweisen auf [PW-LOCAL](PRODUCTION_GIT_WORKSPACE.md). Nur dabei
ist die optionale Codex-Arbeitswurzel sichtbar und wird bei nichtleerem Wert
mitgegeben. Auch die Aufbereitung/Bewertung veröffentlichter Hintergründe wird
lokal beauftragt. ChatGPT-Bildangebote und -korrekturen verwenden den gebundenen
[Bildempfang](PW_IMPORT.md); Rasterarbeit, Hintergrundaufbereitung nach bestätigtem
Import und Erstintegration/Git-Abschluss verwenden [PW-REMOTE](PW_REMOTE.md).
Spätere Hintergrundrevisionen verwenden den eigenen Bestandsweg nach
Authoring Schritt 5 §9. Die aktuellen Regeln stammen aus main, der bestehende
Produktionsstand aus dem festen Recordlink. Private Empfangsbindungen stehen
zusätzlich im aktivierten Bildauftrag.

„Bild neu bewerten“ richtet sich ausschließlich an ein noch offenes Reveal-
oder Motivangebot der aktuellen Phase. Die Auswahl bietet nur diese Ziele an;
bereits gewählte frühere Bilder sind keine neuen Bewertungsziele. Codex sichtet
die vorhandenen unveränderten Bytes lokal und sichert die Bewertung, ChatGPT
verwendet das bestehende Empfangs-Assessment. Beide Aufträge binden das
gewählte Bild und die zulässigen neuen Befundentscheidungen an diesem Bild.
Vorgemerkte kreative Wünsche bleiben mit sichtbarem Hinweis in der Ansicht
erhalten. Bei offenen Eingaben erfolgt der Wechsel auf den veröffentlichten
Nachfolger ausdrücklich. Die Neubewertung erzeugt weder neue Bildbytes noch
eine Auswahl, Endabnahme oder Integrationsbefugnis.

Reguläre Frühphasenaufträge enden bei der veröffentlichten Auswahlvorlage nach
Authoring; sie verlangen keinen Produkt-PR. Diagnoseaufträge transportieren die
konkrete Crop-/Frame-Erklärung mit ihren Bindungen und dem gewünschten Ende.
Ihre allgemeinen Prüfverfahren stehen ausschließlich in Schritt 3.

ChatGPT-Aufträge sind für einen frischen Chat mit dem festen Record oder dem
neuen Motivbriefing und der beigefügten Referenz bestimmt. Bei Unterbrechung
am zuletzt bestätigt veröffentlichten Stand fortsetzen und fehlende Originale
oder Fähigkeiten benennen. „Auftrag starten und kopieren“ bindet die angezeigten
Entscheidungen und aktiviert den begrenzten Empfang im Rätselunterordner.
Er erscheint sofort unter „Offene Produktionen“. Der Hauptbereich zeigt je
Produktions-ID das gebundene Briefing oder den gewählten Gitstand und genau
einen aktuellen Auftragsbereich. Dort kopiert „Auftrag kopieren“ den bereits
gebundenen Text auch nach einem Neustart. Ein gespeicherter Motivtext allein
bleibt ein Entwurf. Übernahmestatus und fachliche Gitphase sind getrennt sichtbar.
Nach abgeschlossener Bereinigung lädt PW auch einen nachgewiesenen Nachfolger des Imports auf demselben Produktionsbranch. Bei ungeklärter Abstammung bleibt die Quittung sichtbar. Der Hauptbereich verlinkt den bestätigten Import oder den Vergleich mit dem aktuellen Arbeitsstand auf GitHub.
Passives Ansehen und erneutes Kopieren erteilen keine zusätzliche Befugnis.
Neue Vorlagen ändern keinen bereits gespeicherten Auftrag. Vor der Aktivierung
eines Bildempfangs gibt es noch keinen ausführbaren Producertext; anschließend
zeigen Vorschau und Kopie denselben gebundenen Text. Eine Vorschau vor dem Start
ist keine zusätzliche Pflicht.

Vorgefüllte Quellwerte sind keine neue Absicht oder Freigabe. Der Folgeauftrag
trennt den veröffentlichten Kontext von Änderungen, ausdrücklich aufgehobenen
Rasterwünschen und neuen/zusätzlichen Wünschen zur Motivvorlage. Bloßes Leeren
oder „Offen“ hebt einen vorhandenen Wunsch nicht auf; dafür gibt es eine eigene
beschriftete Aufhebungswahl je Achse beziehungsweise Modus/Farbzahl. Sie hat Vorrang
vor den betroffenen Eingabefeldern; die andere Achse bleibt unverändert wirksam.
Ein geänderter freigegebener Korridor geht über den bestehenden Korrekturweg zur
erneuten Entscheidung. Die bewusst angeforderte reguläre Freigabe in Schritt 3
bleibt erhalten.

Die Auswahl im Assistenten ist zunächst Bedienabsicht. Beim gebundenen Bildempfang
bestätigt „Auftrag starten und kopieren“ unter „Fortsetzen / Entscheidung senden“
die angezeigte Auswahl. „Arbeit wieder aufnehmen“ bindet bei ChatGPT den offenen
Empfang oder das aktuelle Reveal- oder Motivangebot nach [PW-IMPORT](PW_IMPORT.md).
Auf dem übrigen Auftragsweg erklärt das Absenden die Freigabe oder beauftragt die Integration.
Ein neuer Quellstand oder geänderte relevante Bildbytes entwerten
stale Auswahlabsichten gezielt. Kein automatischer Modellaufruf, keine Modell-API,
kein Freigabewriter im Hilfsdienst und keine automatische Serienfreigabe.

Mit der tatsächlich abgesendeten und an aktuelle Originalbytes gebundenen
Kandidatenwahl ist die eng begrenzte Publisherbereinigung der ausgeschiedenen
eigenen Alternativen bereits autorisiert. Dafür keine weitere Bestätigungsrunde
im Assistenten, im Folgeauftrag oder im Produktionschat anfordern; die Prüfung
und sichere Veröffentlichung folgen [PW-B](PW_B_CONTRACT.md). Scheitert nur
der automatische Assetabbau, bleibt die gültige Bild-/Motiv-/Raster-/Hintergrundwahl
bestehen; den technischen Rest gesondert ausweisen. Die eigenständig ausdrücklich
bestätigte Entfernung einer vollständigen Produktion nach §4.4 ist davon
nicht betroffen.

Bei der Motivfreigabe genügt die ausdrückliche Motivwahl, wenn der aktuelle
Record genau einen vollständigen Parametervorschlag enthält. Bei mehreren
vollständigen Vorschlägen ist eine eigene Auswahl erforderlich. Die Ansicht
ordnet Ziel, Genauigkeit, Grenzen, erlaubte Beschnittseiten und geschützte
Merkmale der jeweiligen Option zu. Der kopierte Auftrag bindet die Motiv-ID
und den jeweiligen Eintrag in `parameters.proposed` im fixierten Record.
Der Produktionsakteur liest und prüft dort das vollständige Original.

Die lesende Oberfläche darf aktuelle Repositorydaten automatisch übernehmen;
unabgesendete menschliche Eingaben nicht unbemerkt überschreiben. Persönliche
Arbeitswurzel und Merge bleiben eigene ausdrücklich angezeigte
Auftragsparameter, keine aus einem Produktionsrecord abgeleiteten Rechte.
Der Assistent fordert keine zusätzliche Bereinigung lokaler Arbeitsdaten an;
eine frühere gespeicherte Bereinigungsoption hat keine Wirkung. Der fachliche Produktionsabschluss folgt Authoring Schritt 5 §9. Bei neuem Job muss dessen Motivbriefing im kopierten Erstauftrag stehen;
noch nicht vorhandene Repositorydaten werden nicht als existent behauptet.

Die normalen beauftragten Produktionsakteure verwenden tools.work_publish nach PW-B für Originalassets und Git-Metadaten an den fälligen Übergängen. Die Befugnis zum Merge folgt dem tatsächlichen Auftrag. Nach bestätigter
Mainintegration führt der Akteur den gebundenen Produktionsabschluss in
Authoring Schritt 5 §9 direkt aus. Der nächste übernommene Listenstand blendet
die integrierte ID aus.

Der kurze Schritt-5-Auftrag gilt auch im frischen Chat. Die technische
Originalzustellung, PR-/CI-Fortsetzung und Wiederaufnahme folgen dem
[Remote-Vertrag](PW_REMOTE.md#draft-pr-und-package-ci-über-den-connector).

## PW-FIND · Befunde am Kandidaten

Bei v3-Produktionen zeigt die Werkstatt die Wählbarkeit direkt am Bild.
„Korrigieren“ an einer Karte übernimmt diese Variante und fokussiert das Änderungsfeld.
Die fachliche Annahmesemantik besitzt
[Qualität §6.1](../production/PUZZLE_QUALITY.md#61-pw-find--befundentscheidungen-in-allen-phasen),
Daten-/Prüfbindung [PW-B](PW_B_CONTRACT.md#pw-find--freigegebene-erweiterung-der-entscheidungsdaten).

In allen Phasen stehen konkrete Befunde direkt an der jeweiligen Reveal-,
Motiv-, Raster- oder Hintergrundkarte. Die Schlussübersicht verwendet die
gewählten Bestandteile; sie braucht keinen künstlichen fünften Kandidatentyp.
Zusätzliche Befunde am Zusammenspiel stehen direkt an der konkret gebundenen
Schlusskombination; ein betroffener Bestandteilwechsel verlangt ihre Neubewertung,
ohne unveränderte Einzelannahmen aufzuheben.
Ein Befund zeigt Kürzel, kurze Beschreibung und Zustand. Nähere Erklärung per
Tooltip oder Aufklappen auch mit Tastatur erreichbar machen. Annahmefähige
Befunde erhalten eine beschriftete Checkbox und „Umgang mit diesem Befund“.
Bei einer nicht annehmbaren Voraussetzung ohne zugelassenen Ausnahmeweg
stattdessen die konkrete fehlende Prüfung oder nötige Korrektur nennen.
Unterstützte technische Ausnahmen dürfen diese Befundbedienung nutzen und müssen
ihren vorgeschriebenen aktuellen Ausnahme- und Bindungsweg vollständig erfüllen.
Auftragsweite Quellen-/Transportfehler bleiben
getrennt sichtbar und werden nicht als redaktionell akzeptierbar angeboten.

Gleiche Kriterien an mehreren Kandidaten und mehrere konkrete Befunde desselben
Kriteriums behalten eigene Eingaben. Gültige Übernahmen zeigen Checkbox und
bisherigen Text vorgefüllt mit kurzer Herkunftskennzeichnung. Bei erstmaliger
Annahme ohne Text vor Absenden sichtbar „Unverändert beibehalten“ einsetzen;
ein Placeholder allein ist kein übertragener Text. Individuelle übernommene
Eingaben erhalten. Die wirksame Wählbarkeit wird bei Annahme oder Rücknahme
unmittelbar neu angezeigt; andere Kandidaten bleiben unverändert.

„Nächste Aktion“ bleibt erhalten:

| Aktion | Bedeutung der Kandidatenwahl |
| --- | --- |
| Fortsetzen / Entscheidung senden | Den vorhandenen Kandidaten einschließlich der im selben Auftrag erklärten zulässigen Annahmen für die fällige Folge verwenden. Keine zusätzliche Annahme-/Auswahlrunde. |
| Korrigieren | Den Kandidaten, auch mit offenen Blockern, als Grundlage der beschriebenen Änderung verwenden. Behandlungsvorgaben mitnehmen; keine kreative Wahl künftiger Bytes. |

Checkbox, Texte und Auswahl bleiben bis zur Start-und-Kopieraktion beim Bildempfang bzw. zum Absenden des übrigen Auftrags lokale
Bedienabsichten. Das UI unterscheidet vorgemerkte und veröffentlichte Entscheidungen.
Der Auftrag trägt neue Annahmen/Widerrufe mit Kandidaten-/Befundzuordnung,
Behandlung, konkrete Wahl oder Korrekturgrundlage und nächste Aktion. Bereits
veröffentlichte gültige Entscheidungen werden aus derselben festen Quelle gelesen;
keine komplette Historie oder allgemeinen Regeln erneut in Prompts kopieren.

Passives Suchen erhält die aktuelle gebundene Ansicht und Eingaben. Ausdrücklicher
Job-/Quellenwechsel überträgt ungesendete Absichten nicht still auf neue Inhalte.
Ein abgesendeter Widerruf folgt dem fachlichen Kandidatenscope. Die Oberfläche
schreibt keine Produktionsdaten und behauptet nach Kopieren keinen neuen Stand.
Nach Veröffentlichung müssen dieselben Annahmen und Behandlungstexte aus dem
Record wieder sichtbar sein. Endabnahme, Integrations- und Mergebefugnis werden
durch ein Häkchen nicht ergänzt. Die tatsächliche Bedienprobe für Karten,
Erklärung/Fokus, Texte und Aktionseffekt steht im Paket; DOM-Nachbildung allein
belegt keine Browserbedienung.

## PW2-B · Schlussübersicht und gebundener Auftrag

Die normale Hintergrundentscheidung zeigt zuerst das tatsächlich gewählte Raster,
dessen Reveal und die vorgemerkte Hintergrunddatei beziehungsweise `none`. Der
primäre Schlussauftrag erklärt diese konkrete Wahl, Endabnahme und Integration
zusammen. Er nennt den gewählten Umfang: Commit, Push und Draft-PR ohne Merge
oder PR samt bedingtem Squash-Merge und anschließendem Produktionsabschluss.
Für Bedingungen und Verfahren verweist er auf Authoring Schritt 5 §§8–9.
Der reguläre Auftragsweg verwendet die Rätsel-ID im Produktionsplan.
`content_ready`, echte äußere Endfreigabe, Finalizer, Export/Plan/Register und
bestätigtes main bleiben getrennte technische Tatsachen; kein UI-Writer entsteht.

Ohne gültigen gespeicherten Mergewert ist der bedingte Merge eingeschaltet. Ein
explizites gespeichertes `false` bleibt erhalten. Die Option und die Wirkung des
konkreten Schlussauftrags sind sichtbar; Kopieren ist noch kein Absenden.
Korrektur, Neubewertung und Wiederaufnahme erzeugen weder eine neue Endabnahme
noch eine neue Mergefreigabe. Wiederaufnahme übernimmt keine vorgemerkte Auswahl
oder neue Befunderklärung. Vorhandene passende Endabnahmen werden nicht erneut
erklärt; ein registrierter Stand erhält nur seinen noch offenen Git-/PR-Abschluss.
Unabhängigen Rätsel-Proof, vollständiges PR-Diff-Selbstreview, das Verbot
routinemäßiger Zweitreview-/Copilot-Anfragen und die tatsächlichen Mergegates regelt
[Authoring Schritt 5 §8](../production/authoring/PUZZLE_AUTHORING_STEP_5.md#8-abgenommenes-ergebnis-ins-spiel-integrieren).
Diese dauerhaften Regeln werden über die Pflichtquellen gelesen. Die Oberfläche
beschreibt denselben gewählten Umfang, ohne ein zusätzliches Reviewgate einzuführen.
Unveränderte Quellenwerte und allgemeine Regeln werden aus den Pflichtquellen
gelesen. Der Auftrag enthält feste Recordquelle, neue Absichten und die
Ausführungsreferenz mit optionaler Arbeitswurzel bei Codex.

Die interne Detailantwort leitet Metadaten, aktuelle Recorddaten und die
Komposition aus genau den ausgewählten aktuellen Dateien ab. Keine Kopien alter
Angebotsrecords oder Inventare. Fehlende Rollen oder Entscheidungen bleiben
sichtbar offen. `facts.originals.record` enthält den kanonischen Record;
es gibt keinen zweiten Handoff als eigene Autorität.

Bilder und relevante Parameter stehen vor dem Auftrag; handlungsrelevante Probleme
bleiben sichtbar. Die Rasteransicht zeigt qualifizierte Angebote und
Sichtungsentwürfe nebeneinander. Ein negativer H-01-Randbefund benennt die
betroffenen Kanten und zeigt eine gültige technische frame-Ausnahme mit eigenem
Nachweis. Bei einem gebundenen Außenbeschnitt lassen sich beide Originale
vergrößern; die Ansicht nennt Maße, Zellzahlen und die vorgeschlagene Änderung
der ungefähren Untergrenze. Der kopierte Auftrag kann diese konkrete Änderung
und die beabsichtigte Rasterwahl zusammen erklären. Die aktuelle Auswahl bleibt
bis zur erneuten Prüfung durch den Produktionsakteur offen. Technische
Diagnoseaufträge sind an die aktuelle Quelle und Endrevision gebunden.
Der standardmäßig geschlossene, kopierbare Detailbereich unten
enthält Original-JSON, Hashes, Revisionen, Commit-/Import- und Diagnosebindungen.
Briefing und vollständige Parameter sind weiterhin erreichbar. Die vorhandene
Snapshot-, Bildlade-, Quellwechsel-, P2- und Origin-Sicherheit bleibt erhalten.
Der CMD-Fallback wird aus denselben Quellen regeneriert. Neue Originale der
Browserprobe dienen nur PW2-B-T01/A01 im Liefer-PR, nicht einer Dauergalerie.

## PW2-C · aktive Produktionen und fachlicher Abschluss

[PW-DONE / #721](https://github.com/venomenon328/picross/issues/721) bindet den
Listenfilter an die registrierten IDs aus dem gültigen aktuellen
Runtime v9 und flachem Inventar von `content/puzzles/` am Listen-Maincommit. Im Remotebetrieb entscheidet
der gewählte Remote-main. PW ermittelt die IDs einmal pro gebundenem Stand.
Bereits registrierte `content/pw/<id>`-Branches werden vor dem Scan übersprungen.
In main überspringt PW entsprechende Indexeinträge vor dem Lesen ihrer Records.
Das gilt für jede Produktionsphase, Revision und Hintergrundarbeit derselben
ID. Spätere Katalog-, Bild- und Rasterpflege läuft über den Bestandseditor.

Offene IDs und deren Fehler bleiben sichtbar. Ein fehlender oder ungültiger
Mainkatalog lässt die Aktualisierung fehlschlagen. Die passive Suche erhält die
aktive Ansicht und ihre Eingaben. Nach einer erfolgreichen Aktualisierung
übernimmt der Benutzer den neuen Listenstand ausdrücklich.

Completion prüft weiterhin die tatsächliche Integration der gewählten
Lieferung. Der Akteur führt nach bestätigter autorisierter Mainintegration
den vorhandenen eng gebundenen Retirementweg nach
[Authoring Schritt 5 §9](../production/authoring/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung)
aus. Erst der verifizierte Abbau von eigenem Arbeitsref, Release und Tag
schließt die Arbeitsgeneration ab. Bei einem Rest wird derselbe erwartete
Arbeitscommit zur Wiederaufnahme verwendet.

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

## Katalogprofile für Abschlussbilder

Die registrierte Lieferung bindet Original, Revealquelle und beide Katalogprofile. Die private Windowslaufzeit liefert den SVG-Renderer mit. Der prüfende Programmstart mit `--catalog-svg-self-test` rasterisiert ein kleines teiltransparentes SVG ohne Benutzercheckout.
