# PW · Git-gestützter Produktionsassistent

## PW2-A · Operativer Quellenweg

Für normale Rätselproduktion aller fünf Schritte einschließlich Korrektur und
Wiederaufnahme gilt [Authoring 0.8.0, Dokumentrevision 6, §1.1](ai-workflows/PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase):
AGENTS-Produktionseinstieg, gemeinsamer Authoringkern, vollständiger
[Bildstil](PUZZLE_IMAGE_STYLE.md), dann nur die fällige Phase und die konkret
benötigte technische Operation. Dieser PW-Gesamtvertrag, WORKFLOW, Projektprofil
und die vollständigen technischen Handbücher sind dabei keine zusätzliche
pauschale Pflichtlektüre. Quellenlinks sind keine rekursive Vollleseanweisung.
Die folgenden Abschnitte beschreiben den Assistenten und seine technischen
Verträge; Entwicklungsaufträge lesen sie weiterhin gemäß AGENTS/Fachrouting.
Historische Paketgrenzen und Lieferstände sind keine neuen Produktionsaufträge.

Die gemeinsame Stilnorm präzisiert farbige Reveals in Richtung Filzstift/farbiger
Tusche und leichte neutralgraue Graphitkontexte. Auch komplexe Szenen und Gruppen
bleiben zulässig. Hintergrundkomposition meint die vollständige 2304×576-Leinwand
mit transparentem Freiraum, nicht die Alpha-Bounds des sichtbaren Motivs.
Gemeinsamer Fit/Anker und alle geschlossenen Dateiformen bleiben unverändert.
PW2-A führte allein den Normschnitt ein. PW2-B ergänzt den unten beschriebenen
Schlussauftrag und die Oberfläche; Listenausblendung bleibt PW2-C.

## #596/C · Reguläre motivtreue Rasterkorrektur

Der [geschlossene C-Vertrag](FIXED_RASTER.md) wurde für Authoring 0.8.0,
Dokumentrevision 4 eingeführt und gilt unter Dokumentrevision 6 weiter.
Er ergänzt den Produktionsweg um freigegebene feste Mono-/Farbzellenkorrekturen
und leeren Außenbeschnitt, auch bei bereits gelösten Rastern.
Korridor, Schutzmaske, frische Endnachweise und echte Motivfreigabe sind Pflicht.
Die reguläre Übergabe endet bei raster_ready ohne Auswahl/Hintergrund/Endabnahme;
historische manuelle Sonderwege bleiben getrennt. Bildsichtung folgt der direkten
Originalprüfung nach Authoring §2.3/Q-B03, ohne verlagerte Montagen-/Fadepflicht.

**PW-B · 0.8.0, 11.11.2026:** Für neue Produktionen gilt der
[fünfstufige Authoringweg](ai-workflows/PUZZLE_AUTHORING.md) mit dem geschlossenen
[PW-B-Datenvertrag](PW_B_CONTRACT.md). Hintergrundbriefing, drei Kandidaten und
Auswahl beginnen erst nach der ausdrücklichen qualifizierten Rasterwahl in Schritt 4.
Frühe Hintergrundpflichten sowie 0.6-Default/0.7-Opt-in-/Offline-Sheetbeschreibungen
weiter unten bezeichnen ihre alten Generationen und gelten nicht für neue 0.8-Jobs.
Bestehende Inhalts-, Proof-, Paletten-, Bild-, Freigabe- und Integrationsgarantien
bleiben erhalten. Anzeige und Produktion bleiben lesend; allein die ausdrücklich bestätigte
Branchentfernung nach §4.4 ist eine enge Schreibausnahme. Veröffentlichung und
Gitabschluss führt der beauftragte Akteur aus. Historische Originale werden nicht migriert.

**APP-Updatevertrag · 13.11.2026 · [Issue #612](https://github.com/venomenon328/picross/issues/612):**
[Automatische App-Releases und Selbstupdate](PRODUCTION_UPDATES.md): APP-A ist
über #613 unabhängig abgenommen und integriert. APP-B1 ergänzt signierte
Updateautorität und den gemeinsamen Verifier; APP-ROOT1 bindet den
[freigegebenen öffentlichen Root](https://github.com/venomenon328/picross/issues/612#issuecomment-6852316923)
im festen Programmtrust, ohne private Signierbereitstellung oder Aktivierung;
APP-B2 ergänzt den standardmäßig ausgeschalteten Start-/Downloadclient und unabhängigen MSI-Helfer. Die veröffentlichende Pipeline
bleibt bis zum eigenen Betriebsauftrag, Schlüsselbereitstellung und beiden
Aktivierungsschaltern gesperrt. Der Selbstupdatekanal bleibt inaktiv. Die Freigabe hebt
die historischen P4-Verbote ausschließlich für diesen Sollweg auf;
Spiel-/Rätsel-/Produktionsdaten bleiben unabhängig.

**Spezifikation 1.0 · 11.11.2026 · [Issue #578](https://github.com/venomenon328/picross/issues/578)**

PW-B liefert diesen Produktionsweg auf Basis des integrierten PW-A2-Starts
(`main@f9764a91fc0e0c717d9d4ffeb0a769ec8ec0aab9`). Der neue Default ist 0.8.0.
Dieser Vertrag erteilt keinen Mergeauftrag.
Paketentscheidungen, Prüfungen und tatsächliche Lieferung stehen in #578.

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

Die hier festgelegte Reihenfolge gilt für neue Produktion nach
[Authoring](ai-workflows/PUZZLE_AUTHORING.md) und dem
[Hintergrundvertrag](PUZZLE_BACKGROUNDS.md). Die geschlossenen neuen Formen
und ihre tatsächlich umgestellten Verbraucher stehen im [PW-B-Vertrag](PW_B_CONTRACT.md).
Der fünfstufige Authoringstand ist **0.8.0**; die Dokumentrevision 5 ordnet seine
operativen Quellen, nicht seine technischen Datenformen neu. 0.7.0 bezeichnet
weiterhin seinen bisherigen vierstufigen Stand, nicht denselben Ablauf unter
neuem Etikett. Unveränderte technische Dateiformen brauchen keine neue Version
allein wegen eines neuen UI-Labels; geänderte geschlossene Semantik wird vor Code
im zugehörigen Fachvertrag eindeutig dem neuen Regelstand zugeordnet.

#490 und #491 bleiben abgeschlossene Lieferungen. #563 führt die neue
Priorisierung vor dem Serienpilot #492. #560 behält die tatsächliche
HW-Kriterienbilanz, insbesondere reale Bild-/Auswahlbelege. Der getrennte
Bestandseditor #576 bearbeitet vorhandene Spielinhalte; PW erstellt keine
konkurrierenden Inhaltswriter und wartet nicht pauschal auf diesen Editor.

## 2. Fünf Schritte, nicht fünf neue Freigaberituale

| Schritt | Arbeit und Entscheidung | Ende des Schritts |
| --- | --- | --- |
| 1 · Abschlussbilder erstellen | Motivtext und optional eigene Referenz; drei tatsächliche farbige detaillierte transparente Abschlussbilder nach gemeinsamem Bildstil erzeugen und im Repository sichern | Bildangebote zur Auswahl; noch keine Abstraktion |
| 2 · Motivvorlage erstellen | Tatsächliche Abschlussbildfreigabe binden; passende Konfiguration empfehlen und standardmäßig eine begründete Abstraktion aus genau diesem Bild erzeugen | Vergleich Abschlussbild/Motivvorlage und klarer Parameterkorridor |
| 3 · Rätsel produzieren | Tatsächliche Motiv-/Parameterfreigabe binden; aussichtsreichsten Kandidaten zuerst, weitere nacheinander nur nach konkretem Bedarf; notwendige Reparaturen und vollständige technische/visuelle Qualifikation samt Schwierigkeit | Ein geeignetes geprüftes Raster genügt; sinnvolle vorhandene qualifizierte Alternativen oder getrennte Sichtungsentwürfe; tatsächliche Rasterwahl |
| 4 · Hintergrund gestalten | Zum gewählten Motiv und Raster drei unterschiedliche Kontextzeichnungen erzeugen, speichern, isoliert zeigen; Wahl/Korrektur oder ausdrückliches `none` | Konkrete Hintergrundentscheidung oder offene Korrektur; kein Spieleinbau |
| 5 · Abnehmen und integrieren | Tatsächliche Endabnahme des gewählten Rasterpakets, gültige Hintergrundentscheidung und Integrationsauftrag prüfen; Ableitung finalisieren, nur gewählte Lieferung gemeinsam integrieren | Draft-PR oder bei passendem Auftrag tatsächlicher Merge; danach regulärer Produktionsabschluss |

Die bedarfsweise Rasterarbeit setzt weder kumulative Kandidaten-/Such-/Reparatur-
budgets noch Korridor oder Qualitätsgates zurück. Ein Angebot ist vollständig
qualifiziert; günstige Vorprüfung ersetzt keinen Endnachweis. Die Dreierauswahl
bei Reveal und Hintergrund bleibt von der aufgehobenen Rasterquote getrennt.

Die Gestaltung des Hintergrunds gehört weder in Abschlussbild- noch in
Abstraktions- oder Rasterproduktionsprompts. In Schritten 1–3 keine Aufforderung
zum Hintergrundbriefing, zu drei Hintergrundmotiven oder zur Hintergrundwahl.
Ein intern erforderlicher Status `pending` ist keine Benutzeraufgabe und darf
keinen sichtbaren Blocker vor dem fälligen Schritt erzeugen.

Die bisherige 0.7-Pflicht, schon bei `motif_review` drei Hintergründe zu besitzen,
entfällt für 0.8.0. `raster_ready` bleibt die sinnvolle Trennung zwischen
vollständiger Rasterprüfung und noch offener Hintergrundbereitschaft.
`content_ready` setzt die gültige gewählte Hintergrunddisposition und die
fälligen technischen/visuellen Belege voraus; Endabnahme und Integration sind
davon weiterhin getrennt. Eine bloß angeklickte Bildkarte setzt keinen Gatewert.

Vor Schritt 4 muss ein tatsächlich qualifiziertes Rasterangebot gewählt sein.
Das ist noch keine Endabnahme oder Integrationsfreigabe. Die bereits gültige
Bild-/Motivfreigabe wird nicht erneut abgefragt. Eine noch offene Hintergrundwahl
kann mit dem abschließenden Auftrag erklärt werden; keine zusätzliche Nachricht
nur zum Wiederholen derselben unveränderten Bildentscheidung verlangen.

Die [Qualitätsregeln](PUZZLE_QUALITY.md), der [gemeinsame Bildstil](PUZZLE_IMAGE_STYLE.md)
und der [Abschlussbildstandard](REVEAL_TRANSPARENCY.md) bleiben maßgeblich.
Hintergrundbilder zeigen Kontext, nicht Rätselsubjekt, Lösung oder Motivname.
Drei unterschiedliche Bildinhalte sind der Standard, nicht drei Dateiformate
desselben Motivs. `none` ist eine ausdrückliche Entscheidung, kein Ersatz für
fehlende Dateien. Keine Buchvorschau, Kandidaten-Testintegration oder zusätzliche
Buchabnahme. Hintergrundkorrekturen erneuern nur die betroffenen Bildbindungen;
unveränderte Raster erhalten ihre gültigen Nachweise. Ein nachträglicher eigener
Hintergrundwechsel bleibt unter weiteren Aktionen getrennt vom neuen Regelweg.

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
  [Authoring §2.1](ai-workflows/PUZZLE_AUTHORING.md).
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
Bytegleiche Veröffentlichungen zeigen „Lokal und Remote“; echte Gitrelation und
Konflikte bleiben davon unabhängig sichtbar. Titelgleiche IDs sind unterscheidbar.
Lokale Entwürfe und deren
Verwerfen bleiben getrennte Browserentwürfe. Job-/Revisions-/Quellwechsel und das ausdrückliche
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
und [Bau-/Lieferbindung](../tools/production_workspace/WINDOWS_BUILD.md) sind maßgeblich. Der
Zustandsordner liegt nicht in `content/`, `game/` oder einem fremden Arbeitsbaum.
[WORKSPACE](dev-rules/WORKSPACE.md) gilt; persönliche Pfade werden nicht committed.

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
Ein lokaler Commit ist lokal lesbar; daraus folgt keine Remote-Erreichbarkeit.

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
Erst verifizierter Erfolg aktualisiert die Remoteansichten. Lokale und Mainquellen
werden weiter gelesen; ihre aktive Auswahl folgt dem lieferbezogenen PW2-C-Abgleich.
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
[release.json](../tools/production_workspace/release.json) bleibt 0.1.0-Startanker
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

Der aktuelle [Builder](../tools/puzzle_production/authoring_builder.py) erzeugt
`record`, Handoff und Paket; seine `sheet_from_record`-Projektion setzt die
Rasteroptionsliste zunächst auf `[]`. Die gemeinsame Angebotsliste wird nach
[Authoring §7](ai-workflows/PUZZLE_AUTHORING.md) bislang in der Chatübergabe
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

Die aktuellen [Authoring-Paketgrenzen](../tools/puzzle_production/authoring_package.py)
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

Maßgeblich ist die [Paketentscheidung PW2-C](https://github.com/venomenon328/picross/issues/626#issuecomment-6862546388).
Die aktive Liste blendet eine konkrete Lieferung erst aus, wenn ihre ID,
Lieferrevision und Original-/Integrationsbindungen mit einem frisch bestätigten
Commit des konfigurierten Remote-Refs `main` übereinstimmen. `registered`, gleiche
ID, PR-Status oder Commitabstammung allein genügen nicht. Ein normaler Merge,
Squash oder unveränderte Sammelübernahme wird anhand derselben Lieferbelege
erkannt. Spätere unabhängige Ergänzungen der Gesamtregistries ändern die
Zuordnung einer weiterhin identischen Lieferzeile nicht.

Der begrenzte Leser verwendet Metadaten des vollständigen Exports oder der
vorhandenen kompakten `picross-integrated-content-v1/v2/v3`-Belege. Nach Retirement
bindet die aktive Produktion den Receipthash; der darin erhaltene ursprüngliche
Exporthash bleibt davon verschieden. Raster-, Reveal- und Hintergrundbezüge
gehören zur Zuordnung. ZIPs, Bilddaten und Solver-/Proofläufe werden für diese
Listenentscheidung nicht geöffnet oder ausgeführt.

Die Zuordnung erfolgt pro konkreter Quelle vor der Motivgruppierung. Identische
lokale/Remote-Kopien sowie nachweislich zugehörige ältere Record-/Projektionsstände
verschwinden gemeinsam. Für ältere Schritte zählt ihre tatsächliche Bindung am
expliziten historischen Lieferstand, keine Revisionssortierung oder Branchfolge.
Neue Revisionen, abweichende Bytes, spätere Reveal-/Hintergrundarbeit und fehlende
oder widersprüchliche Belege bleiben sichtbar, auch unter derselben Rätsel-ID.
Der Abgleich löscht keine Daten oder Refs und erzeugt keinen Completionbeleg.

Die Bestätigung umfasst den tatsächlichen Mainref im gebundenen Quellenstand.
Ein lokaler `main`, ein alter Cache oder ein erfolgreiches Refresh nur anderer
Refs genügt nicht. Eine bewusst ohne `main` konfigurierte Refwahl wird nicht
erweitert. Bei fehlendem, offline gebliebenem oder unlesbarem Mainbezug bleiben
betroffene Quellen sichtbar; die Liste erklärt die fehlende Bestätigung.
Ein Mainwechsel wird auch bei unverändertem Produktionscommit neu ausgewertet.
Die Statusabfrage startet weiterhin keinen Gitlauf.

Passive Suche erhält die geöffnete Quelle, ihre Bilder und ungesendete Eingaben.
Erst „Neueren Stand laden“ übernimmt den gefilterten Listenstand und erklärt den
bestätigten Entfall. Verbleibende offene Arbeit derselben ID bleibt anwählbar;
andernfalls folgt eine andere offene Produktion oder der leere aktive Zustand.
Eigene Browserentwürfe bleiben getrennt gespeichert und erreichbar. Die internen
Listenfelder unter `completion` geben Mainbestätigung, Quellenbindung und
Ausblendungsumfang an; sie sind Ansichtsdaten, keine neuen Originalschemas.

Kleine synthetische Regressionen liegen im ausgewählten `tools`-Modul. PW2-C-T01
liefert einmalig den lesenden Praxisabgleich der drei #622-Lieferungen sowie die
echte Browserprobe mit unveränderten Original-PNGs. Quellen, Produkt-Head,
Liefer-/Prüfstand und das unabhängige Vor-Merge-Gate PW2-C-A01 stehen im Liefer-PR.
Es entsteht keine dauerhafte Browsermatrix oder Sammlung realer Produktionsdaten.

## 9. Paketgrenze PW-A

Dieser Abschnitt beschreibt die historische PW-A-Paketgrenze, nicht den heutigen
Funktionsumfang nach PW-B. Er ist keine zusätzliche operative Pflichtquelle.

PW-A liefert Projektor/Schema, lokale Git-/Paketauflösung, sicheren Dienst,
Windowsstarter und eine tatsächlich benutzbare **lesende Job-/Bildansicht**.
Diese bietet Job-/Revisionauswahl, Bildkarten/Großansicht, Vergleich der vorhandenen
Bildrollen, Quellen-/Aktualisierungsstatus, Hell/Dunkel und verständliche Fehler.
Es ist kein reiner HTTP-Skeleton und keine nur in Logs sichtbare Bildlieferung.

Noch nicht enthalten sind neue fünfstufige Prompts, produktive Auswahl- und
Freigabeaufträge, Defaultumstellung, WIP-Import/Migration, eigener Bestandseditor,
Runtimeänderungen, neue Bilder, Solveränderungen oder automatische Gitpublikation.
Die kurze Projektor-/Launcher-Anleitung gehört zur Lieferung. Die bestehende
Offline-HTML-Datei bleibt bis zum vollständigen PW-B-Ersatz als Iststand erhalten;
kein neuer Kompatibilitätsmodus innerhalb des Assistenten.

Technische Trennung: Der Projektor ist ein ausdrücklich beauftragtes lokales
Produktionswerkzeug für die neue Ansichtsdatei. Der langlebige HTTP-Dienst ist
projektseitig Leser mit der späteren engen P2-Ausnahme nach §4.4. Kein Projektor-/Dateischreibaufruf durch
einen beliebigen Browserrequest.

Das Issue definiert PW-A-K01 bis K12, T01/T02 sowie die separaten Vor-Merge-Gates.
PW-B ist erst nach dem tatsächlich gelieferten PW-A-Vertrag fein zu schneiden;
die produktseitigen Anforderungen dieses Dokuments sind bereits freigegeben.

Die ausführbare PW-A-Schnittstelle, Einrichtung und Schutzgrenzen stehen in der
[Werkzeuganleitung](../tools/production_workspace/README.md); der konkrete
Liefer-/Prüfstand einschließlich offener Plattformgates steht in PR #579.

## 10. Nachführung beim späteren PW-B

Historischer Einführungsplan für PW-B; keine Wiederholungsaufträge durch PW2-A.
In einem konsistenten Implementierungsdiff mindestens diese Quellen abgleichen:

- Authoring und den eingebetteten/ersetzenden Regelstand: fünf Aufträge, neue
  0.8.0-Phasenbedingungen, Ausgabe und verpflichtende Repositoryprojektion.
- Hintergrundvertrag und Qualität: Bilderzeugung erst Schritt 4, endgültige
  Nutzung Schritt 5; keine neue Buchsichtpflicht.
- Paketbuilder, Phasenreader, Finalizer/Export, Projektor und Auftragstransport:
  neue gültige Zwischenstände und korrekte Bereitschaft, kein alter Schritt-4-
  Integrationsprompt unter neuem sichtbaren Titel.
- Werkzeuganleitung, Projektprofil und Produktionsablage: Launcher, Quelle,
  Veröffentlichung, Wiederaufnahme und Nichtunterstützung alter WIP.
- #560/#563/#492: tatsächlichen Liefer-/Aktivierungsstand und den neu
  vorbereiteten Pilotweg führen. Frühere SP-P1-Reihenfolge nicht still ausführen.

Der reale Pilot ist kein Ersatz für technische Prüfung. Eine persönliche Probe
des vollständigen Assistenten beurteilt Bedienbarkeit am konkreten gelieferten
Head; sie erteilt keine pauschale Freigabe später erzeugter Bilder oder Rätsel.

## Quellen

Für normale Produktion gilt ausschließlich das operative Routing am Anfang
und in Authoring §1.1. Die folgende Liste ordnet Entwicklungs-/Herkunftsquellen
zu und erteilt keine zusätzliche pauschale Volllektüreplicht:

[Workflow](dev-rules/WORKFLOW.md), [Projektprofil](PROJECT_PROFILE.md),
[Authoring](ai-workflows/PUZZLE_AUTHORING.md), [Bildstil](PUZZLE_IMAGE_STYLE.md),
[0.7-Iststand](ai-workflows/PUZZLE_AUTHORING_0_7_0_PREVIEW.md),
[Hintergrundvertrag](PUZZLE_BACKGROUNDS.md), [Qualität](PUZZLE_QUALITY.md),
[Produktionswerkzeuge](../tools/puzzle_production/README.md),
[CI v2](CI_WORKFLOW_V2.md), [CI-Vertrag](dev-rules/CI_CONTRACT.md).

Technische Referenzen zur Umsetzung: [Git-Objektzugriff](https://git-scm.com/docs/git-cat-file),
[Python-HTTP-Sicherheitsgrenzen](https://docs.python.org/3/library/http.server.html#security-considerations),
[CSP und lokale Verbindungen](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/connect-src).
Ein bloßer Aufruf von `python -m http.server` erfüllt die hier definierten
Zugriffs- und Autoritätsgrenzen nicht.
