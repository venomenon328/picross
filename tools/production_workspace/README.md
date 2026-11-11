# Lokale Produktionsansicht (PW-A)

Die lesende Job-/Bildansicht für neu veröffentlichte Handoff-v3-/Record-v2-
Arbeitsstände. [Fachvertrag](../../docs/PRODUCTION_WORKSPACE.md),
[Paketentscheidung PW-A](https://github.com/venomenon328/picross/issues/578#issuecomment-6793791025).
[Startkorrektur PW-A2](https://github.com/venomenon328/picross/issues/578#issuecomment-6798166149)
engt das Branchschema ein und lädt Git im Hintergrund.
Der neue Produktionsdefault und die fünfstufige Auftragssteuerung gehören zu PW-B.
Das bestehende Offline-Sheet und vorhandene WIP bleiben unverändert.

## Start und einmalige Einrichtung

Voraussetzungen: Python **3.11+**, aktuelles Git mit `--no-lazy-fetch` und
Pillow **12.3.0**. Der Git-Schalter verhindert implizites Nachladen im
Benutzercheckout; ein Git ohne diese Fähigkeit wird abgewiesen. Keine globale
Installation durch den Starter. Im vertrauenswürdigen Programmcheckout einmal
in einer eigenen Pythonumgebung installieren, beispielsweise unter Windows:

```powershell
python -m venv .venv-pw
.\.venv-pw\Scripts\Activate.ps1
python -m pip install --only-binary=:all: -r tools/puzzle_production/requirements-image.txt
.\tools\production_workspace\start-production-workspace.cmd
```

Der Starter fragt beim ersten Start nach dem vorhandenen Projektcheckout und
bietet lokale Gitstände oder die ausdrücklich gewählte Remote-URL an.
Standardeinstellung: nur lokal. Standardbranches: `main` und `content/pw/*`.
Neue Produktionen verwenden verbindlich `content/pw/<puzzle_id>`, zum Beispiel
`content/pw/pz-eule`, mit einem stabilen Branch pro Rätsel. Alte `content/*`-
Branches werden weder abgerufen noch durchsucht.
Der Browser öffnet vor der Git-Suche; diese läuft einzeln im Hintergrund und
meldet Laufzeit/Abschluss/Fehler in der Oberfläche; Strg+C im Starter beendet den Dienst.
Nach erneutem Start sind keine Bild-, ZIP- oder JSON-Importe nötig.
Die unveränderte frühere Standardauswahl `main` + `content/*` wird automatisch
im eigenen Zustand eingeengt. Abweichende alte Auswahlen benötigen einen neuen
Zustandsordner; neue CLI-Optionen überschreiben keine bestehende Einrichtung.

Explizite Einrichtung aus dem Programmcheckout, mit absoluten lokalen Pfaden:

```powershell
python -m tools.production_workspace --setup --repository C:\Projekte\picross --state C:\Picross-PW
python -m tools.production_workspace --state C:\Picross-PW
```

Für bewusst bestätigte Synchronisierung bei der Einrichtung ergänzen:
`--remote https://github.com/venomenon328/picross.git` oder eine SSH-URL.
Eine kleinere Auswahl über wiederholtes `--ref` angeben, zum Beispiel
`--ref main --ref content/pw/pz-eule`. Andere Branchfamilien sind nicht zulässig.
Die URL darf keinen Token und kein eingebettetes Passwort enthalten.
Die vorhandene Git-Anmeldung bleibt zuständig; keine Anmeldedaten in der UI.

Ohne `--state` liegt der eigene Zustandsordner unter
`%LOCALAPPDATA%\PicrossProductionWorkspace` (Linux: im persönlichen lokalen
Datenordner). Er muss außerhalb des Projektcheckouts und fremder Git-Arbeitsbäume
liegen. Der Programmcheckout liefert immer die vertrauenswürdige UI; betrachtete
Produktionsbranches liefern ausschließlich Daten. Neue Einrichtung benötigt einen
neuen leeren eigenen Zustandsordner; kein Übernehmen beliebiger fremder Cachebäume.

Ein belegter `--port` wird gemeldet; ohne Angabe wählt der Starter einen freien
Loopbackport. Fehlendes Git, Python oder Pillow wird gemeldet. Keine ungefragte
Installation. `--no-browser` dient einem beaufsichtigten Diensttest, nicht als
zweiter manueller Einrichtungspfad.

## Einzelne ausführbare Startdatei

[Picross-Start.cmd](Picross-Start.cmd) enthält den zugehörigen lesenden Programmstand
samt Oberfläche. Sie kann auch mit einem unveränderten PW-A-Checkout verwendet
werden. Doppelklick genügt; bei Bedarf einmal den Projektordner angeben.
Die vorhandene Einrichtung und isolierte Pythonumgebung werden wiederverwendet;
Pillow 12.3.0 wird nur bei Bedarf dort installiert. Python/Git bleiben
Voraussetzung. Store-Python- und Junctionpfade werden innerhalb von Python
aufgelöst. Das Skript führt keine Git-Aktualisierung des Programmcheckouts aus.

Die eingebetteten vertrauenswürdigen Dateien werden mit SHA-256 geprüft, in einen
eigenen temporären Programmordner geschrieben und von dort geladen. Die
unveränderten Produktionsbibliotheken stammen aus dem angegebenen vertrauenswürdigen
Checkout. Es wird kein Programmcode von Produktionsbranches übernommen.
Der Programmordner wird bei regulärem Ende entfernt. Den laufenden Starter mit
Strg+C beenden, bevor eine neue Version gestartet wird.

Nach Änderungen an den eingebetteten Quelldateien regenerieren:

```sh
python -m tools.production_workspace.build_launcher
```

Der kleine Regressionstest gleicht die eingebetteten Bytes mit den Quelldateien ab.
Die Windows-`.cmd`-Ausführung und echte Browserbedienung benötigen weiterhin die
separat benannte Windowsprobe; eine Linuxmessung belegt diese nicht.

## Bedienung und Quellenstatus

Job/Revision wählen; Bildkarten nach Rollen und der Reveal-/Motivvergleich
laden ihre Originale. Großansicht bietet Einpassen, 100/200/400 Prozent und
neutralen Transparenzprüfgrund. Alle Texte werden als Klartext gerendert.
Es gibt keine Freigabeschaltfläche, automatische Rasterwahl oder neue Zertifizierung.
Die Anzeige benennt vorhandene Prüfungen ausdrücklich als überlieferte Befunde.

„Neuere Ergebnisse suchen“ aktualisiert lokale Refs und bei gewählter
Synchronisierung ausschließlich den eigenen Gitcache. Die aktive Ansicht bleibt
an ihrer SHA gebunden. „Neueren Stand laden“ übernimmt die neue komplette Liste.
Bis zu acht Listenstände bleiben pro Sitzung erreichbar; danach neu laden.
Unterschiedliche Quellen derselben ID/Revision mit abweichenden Bytes sind
Konflikte. Es wird keine höchste Revisionszeichenfolge gewählt.

Nur lokale Nachweise, im konfigurierten Remote gefundene Commits, Zeitpunkt der
letzten Synchronisierung und Remote-/Offlinefehler sind getrennt sichtbar.
Ein lokaler Commit ist keine bestätigte Remote-Sicherung. Offline bleibt ein
vorhandener Cache lesbar; noch nicht geladene Gitobjekte können dann fehlen.
Ein Dirty-Checkout ist zulässig, seine Arbeitsdateien werden nicht angezeigt.
Eine defekte Projektion wird ihrem Indexeintrag zugeordnet; andere gültige
Revisionen bleiben sichtbar. Erfolgreiche Synchronisierung entfernt weggefallene
Remote-Branches ausschließlich aus den konfigurierten eigenen Cache-Refs.
Bereits geöffnete Snapshots bleiben gebunden; bei Offlinefehlern bleiben die
zuletzt gespeicherten Refs erhalten.

Der Dienst schreibt nur eigene Einrichtung/Cachedateien: `config.json`,
`git-cache-pw-v1` und `sync-pw-v1.json`. Der frühere `git-cache` und dessen
Synchronisierungsdatei bleiben unangetastet und werden nicht durchsucht.
Kein Pull/Checkout/Reset/Stash/Add/Commit/Push oder Merge im Benutzercheckout.
Fetch verwendet eine flache Historie (`depth=1`) und `blob:none`, soweit das
Remote Filter unterstützt. Ausdrücklich gebundene historische Commits und
einzelne baumgebundene Blobs werden bei Bedarf geholt. Unveränderte Listenbefunde
liegen commitgebunden in einem begrenzten 8-MiB-Prozesscache. HTTP-Statusabrufe
lesen den fertigen Snapshot und starten keine Git-Suche.
Es wird nichts entpackt, kein allgemeiner Archivbrowser aufgebaut.
Der Cache beendet weitere Fetches ab 384 MiB bereits gespeicherter Objekte,
mit Reserve für ein höchstens 128-MiB-Paket. Danach einen neuen eigenen Zustand
anlegen; dies ist eine lokale Schutzgrenze, keine CI-Artefaktgrenze.

Blob-/Bildcaches sind nur im Prozess (je höchstens 64 MiB/512 Einträge),
Baummetadaten höchstens 4 MiB. Große ZIPs werden einzeln geöffnet und wieder
freigegeben. Höchstens vier Datenoperationen laufen gleichzeitig; weitere erhalten
„beschäftigt“. Davon dürfen auch nach einem Transportabbruch höchstens zwei
laufende Bildoperationen sein; deren Serverplätze bleiben bis zum tatsächlichen
Arbeitsende belegt. So bleibt Kapazität für Job-/Metadatenzugriffe frei.
Die Oberfläche lädt Bilder mit einer Zweierwarteschlange. Bei „beschäftigt“
warten aktuelle Bildkarten automatisch weiter, mit Abständen von 250 ms bis
höchstens zwei Sekunden, bis Kapazität frei wird oder der Job verlassen wird.
Metadatenaufrufe wiederholen höchstens viermal; fehlgeschlagene Bildkarten bieten
„Bild erneut laden“. Jobwechsel verwirft alte Warteschlangeneinträge und Antworten.
Die Jobliste liest keine ZIPs. Ein Job wird vor Bildausgabe gegen
Originale geprüft, anschließend werden nur gebundene Bildkennungen ausgeliefert.
Kein Browserbildarchiv: nur die Darstellungseinstellung bleibt im Local Storage;
der zufällige Sitzungsschlüssel liegt bis zum Schließen im Session Storage,
damit Neuladen funktioniert. Er erscheint weder in Logs noch technischen Details.

## Projektor für den Produktionsakteur

Vor der beauftragten Phasensicherung erzeugt der Produktionsakteur automatisch
die neue Ansichtsdatei. Dies ist kein zusätzlicher manueller Schritt für den
Benutzer. PW-A liefert die API/CLI; erst PW-B bindet sie obligatorisch in den
neuen Produktionsablauf ein.

```sh
python -m tools.production_workspace.projector --repository /absoluter/projektcheckout --request /absoluter/request.json
```

API: `projector.project(request, repository)`.
Der Auftrag folgt [request.schema.json](request.schema.json): nur Identitäten,
Beschriftungen und vorhandene Quellreferenzen, keine Hash-/Erfolgs-/Freigabeoverrides.
Beispiel für eine einzelne Assetquelle im Auftrag:

```json
{"id":"reveal-A","role":"reveal","caption":"Abschlussbild A","location":{"commit":null,"storage":"package","container":"content/authoring/pz-beispiel/r01/package.zip","file":"images/reveal-A.png"}}
```

Das Beispiel ist nur ein Feldbeispiel; der komplette Auftrag enthält exakt
`format,puzzle_id,revision,record,title,assets,offers`. Format:
`picross-production-presentation-request-v1`. `record` ist `{commit:null,file:...}`
an der kanonischen Indexposition. `offers[]` enthält `id,kind,label,record,asset_ids`;
jeder Angebotsrecord liegt im Index seines ausdrücklich gebundenen Snapshots.
Angebotsmitgliedschaft und Beschriftungen stammen aus der tatsächlichen
Auswahlvorlage. Es gibt keinen PNG-Verzeichnisscan. Historische Quellen benötigen
volle Commit-SHAs; `null` bezeichnet die gemeinsam zu sichernden Arbeitsbytes.
Verworfene Hintergrundoriginale dürfen über die ausdrückliche Historybindung
aus einem bytegleichen früheren Manifest gelesen werden; aktive Originale
müssen regulär vorliegen. Verlorene historische Gitobjekte sind ein Fehler.

Bei direkter Repositoryquelle ist `container=null`; der Pfad bezeichnet die zum
Record gehörende Originaldatei unter dessen Produktionsrevision. ZIP-Mitgliedspfade
sind relativ zur Paketwurzel, auch bei ZIPs mit einer einzelnen äußeren Wurzel.
Voraussetzung sind heutige v3-/v2-Pakete; kein WIP-Import und keine automatische
Konvertierung. Reveal-/Motivbezüge, Revealangebote, vorhandene Import-/Reparatur-
Rasteransichten und Hintergrundmanifestkandidaten werden an ihren Originalen
geprüft. Unvollständige Raster bleiben `raster_draft`; sie sind kein Rasterangebot.

Der Projektor berechnet sämtliche Hashes und Bytezahlen selbst und prüft die
Projektion nach [presentation.schema.json](presentation.schema.json) plus den
fachlichen Kreuzbindungen aus dem Fachvertrag. Die geschlossenen JSON-Schemas
beschreiben die Formen; Pfadsicherheit, Eindeutigkeit, Rollen, Inventare,
Originalbezüge, tatsächlich dekodierte PNG/JPEG und fachliche Angebotsfähigkeit
werden zusätzlich im Reader/Projektor geprüft. Keine Solver-/Difficultyausführung.

Geschrieben wird genau `workspace.json` neben `record.json`. Alle anderen Quellen
bleiben bytegleich. Identische Wiederholung ist No-op samt mtimes. Abweichende
bestehende Ausgabe oder zwischenzeitlich geänderte Quellen stoppen. Ein temporärer
Nachbar wird nach erneuter Quellenprüfung atomar ohne Ersetzen veröffentlicht und
entfernt. Ergebnis auf stdout: `published` oder `reused`, Pfad/Hash/Bytezahl;
Exit 0 bei Erfolg, 2 bei ungültigen oder kollidierenden Quellen. Git-Sicherung
von Index, Record, Projektion und Originalen bleibt ausdrücklich Aufgabe des
beauftragten Produktionsakteurs. Die HTTP-API kann den Projektor nicht aufrufen.

## Sicherheits- und Prüfgrenzen

Loopback, exakter Host/Origin, Sitzungsschlüssel und keine CORS-Freigabe.
Die API akzeptiert nur serververgebene Job-/Assetkennungen, keine Pfade/Refs/URLs.
CSP erlaubt eigene UI und lokal erzeugte Bild-Blob-URLs; HTML/SVG aus Paketen
werden nicht ausgeführt. Gitlinks/Submodule, ZIP-Aliase, Spezialdateien,
CRC-/Hash-/Größenfehler und beschädigte Bilder werden zurückgewiesen.
Die vorhandenen 128/64/512-MiB-/2048-Datei-Paketgrenzen und 32-MiB-/8-Megapixel-
Bildgrenzen gelten weiter. Der Reader bestätigt keine neue Inhaltsfreigabe.

Kleine Regressionen: `python -m unittest tools.test_production_workspace -v`
in der isolierten Imageumgebung, mit Node.js 22+ für die browserfreie Ausführung
des tatsächlichen UI-Ladecodes gegen einen langsamen lokalen HTTP-Dienst.
Die DOM-Testnachbildung prüft keine Darstellung oder echte Browserbedienung.
Sie prüft getrennt echte Fetch-Abbrüche bei fünf Sekunden weiterlaufender
Serverarbeit und verspätet eintreffende Bildantworten.
Der einmalige PW-A-T01-Durchstich und die
wirkliche Windows-/Browserprobe T02 werden am konkreten Lieferhead im PR geführt.
Linux-/HTTP-Tests ersetzen die Windowsprobe nicht. Die getrennten Vor-Merge-Gates
PW-A-A01 und PW-A-A02 stehen in der Paketentscheidung.
