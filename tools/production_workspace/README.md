# Lokaler Produktionsassistent (PW-B)

Der fünfstufige Assistent für neue Authoring-0.8.0-Produktionen verwendet
genau einen aktuellen Record nach PROD-SLIM und daraus abgeleitete Ansichten.
Der operative Regelstand ist **Authoring 0.8.0** in der aktuellen
Phasenquelle; der aktuelle Datenvertrag steht in PW-B. Normale Produktion liest den
Produktionseinstieg in [AGENTS](../../AGENTS.md),
[Authoring §1.1](../../docs/production/authoring/PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase),
die [Bildnorm-Leseregeln](../../docs/production/images/README.md) und
die dort gerouteten Phasen- und Bildtypdateien. Diese Anleitung, der
[PW-B-Datenvertrag](../../docs/tools/PW_B_CONTRACT.md) und die technische
[Produktions-README](../puzzle_production/README.md) werden für die konkret
verwendete Operation abschnittsbezogen gelesen, nicht pauschal vollständig.
Die [ursprüngliche PW-B-Paketentscheidung](https://github.com/venomenon328/picross/issues/578#issuecomment-6799208194)
ist eine Entwicklungs-/Herkunftsquelle, keine zusätzliche Routinelektüre.

Unter „Einstellungen für Google Drive“ einmal die private Stammordner-ID und den
zugehörigen synchronisierten Windows-Ordner speichern. Im Produktionsbereich
das Motiv beschreiben oder die gewünschte Variante wählen. Bei ChatGPT-Bildarbeit
„Auftrag starten und kopieren“ wählen und den Auftrag im Chat senden. Eine
ausgewählte Referenzdatei dort anhängen. Die Werkstatt zeigt den Empfang bis
zur bestätigten Veröffentlichung. Dort den neuen Arbeitsstand öffnen oder einen
angezeigten Bereinigungsrest fortsetzen.

PW2-B stellt Bilder, fällige Entscheidungen und relevante Parameter vor die
technischen Originaldetails. Bei der Hintergrundwahl zeigt die Schlussübersicht
gewähltes Raster, Reveal und Hintergrund/none. „Endabnahme & Integration: Auftrag
kopieren“ erzeugt einen gemeinsamen Schlussauftrag; erst sein Absenden erklärt
die Freigabe. Bedingter Squash-Merge nach PR-Diff-Selbstprüfung und aktuellen Gates
ist ohne gespeicherte Einstellung der Standard; ein ausdrückliches Nein bleibt
als Draft-Auftrag erhalten. Korrektur, Neubewertung und Wiederaufnahme erklären keine neue Endabnahme
oder Mergefreigabe. Der geprüfte aktuelle Record bleibt unten
aufklappbar und kopierbar. Quellenwerte, Regeln und nicht beauftragte lokale
Bereinigung werden nicht routinemäßig im Prompt wiederholt. PW2-C nimmt konkret
nachgewiesene integrierte Lieferungen aus der aktiven Auswahl. Ein vollständig geeigneter qualifizierter
Rasterkandidat genügt; weitere entstehen nach Authoring bedarfsweise nacheinander,
ohne Budget-/Qualitätslockerung. Die drei Reveal- und drei Hintergrundoriginale
bleiben ihre eigenen Bildauswahlen. Hintergrund bedeutet die ganze Leinwand des
gebundenen [HG31-Profils](../../docs/production/PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile)
samt Freiraum; neue Produktion verwendet ausdrücklich das 3:1-Profil.

Die PW-A2-Start-/Git-/Sicherheitsarchitektur bleibt erhalten; P2 ergänzt allein
die ausdrücklich bestätigte Branchentfernung nach [PW §4.4](../../docs/tools/PRODUCTION_WORKSPACE.md#44-p2--ausdrücklich-bestätigte-produktionsentfernung).
Bestehende WIP werden nicht konvertiert. Das frühere Offline-Sheet ist entfallen;
der reguläre Einstieg ist die Windows-App.

„Neues Motiv“ beginnt mit einem Briefing und optional einer eigenen Datei, die
dem Chat tatsächlich beigegeben werden muss. Zusätzliche Motivhinweise wie Blickwinkel,
Stimmung und unverzichtbare Merkmale haben ein eigenes Feld. Unter „Rastervorgaben“
lassen sich Breite und Höhe unabhängig (je 1–50 Zellen, auch nur eine Achse), Modus und für
Farbrätsel 2–8 Vordergrundfarben angeben. Maße und Farbzahl haben getrennte
Genauigkeiten. Ohne Vorgabe bleibt die Wahl offen; das Abschlussbild ist immer
farbig. Die lokalen Motivbriefings merken sich diese Eingaben pro Entwurf.
Beim Übergang vom gewählten Abschlussbild zur Motivvorlage sind Rasterwünsche
direkt zugänglich. Änderungen an einem vorgelegten Korridor laufen über
„Gezielt korrigieren“. Eine ID entsteht erst im Auftrag.
Die fünf Schritte zeigen Abschlussbilder, Motivvorlage, geprüfte Rasterangebote,
danach Kontextzeichnungen und schließlich Endabnahme/Integration. Ein Klick
merkt eine Auswahl nur vor. Beim ChatGPT-Bildempfang bestätigt „Auftrag starten und
kopieren“ die angezeigte Wahl. Bei den übrigen Aufträgen bestätigt das Absenden
die Wahl. Den Fortschritt zeigt die Werkstatt am veröffentlichten Gitstand.
Fortsetzen und Korrektur verwenden dieselben Originalquellen. Eine vorhandene
gültige Endabnahme wird nicht nochmals angefordert. Arbeitswurzel und bedingte
Mergefreigabe sind persönliche Optionen, niemals Recordbefugnisse. Zusätzliche
lokale Arbeitsdatenbereinigung braucht einen gesonderten ausdrücklichen Auftrag.
Ein ungepushter Stand oder lokaler Testremote bleibt sichtbar, liefert aber
keinen als Cloudquelle ausgegebenen Folgeauftrag.

## Start und einmalige Einrichtung

Primärer Einstieg ist der per-user **Windows-x64-MSI** nach
[P4](https://github.com/venomenon328/picross/issues/588#issuecomment-6825638437).
Installieren und den Startmenüeintrag „Picross-Produktionsassistent“ öffnen;
Desktoplink optional. Das bestehende portable App-Image bleibt Fallback.
Private Python-/Pillow-/Tcl/Tk-Laufzeit, unveränderte benötigte
Produktionsreader und UI sind enthalten; kein globales Python/Node, pip oder
Laufzeitdownload. **Git für Windows mit `--no-lazy-fetch` bleibt Voraussetzung**,
damit die bisherige Git-/SSH-/Credential-Einrichtung weiterverwendet wird.
Keine Administratorrechte nötig. [Start-/Updateanleitung](START-WINDOWS.txt),
[versionierter Bau und Smoke](WINDOWS_BUILD.md).

Der [separate App-Releasekanal](../../docs/tools/PRODUCTION_UPDATES.md) verbindet
automatische Versionsplanung, MSI-Bau, signierte Updateautorität und Offlineverifier.
Sein produktbezogener Betriebsstand folgt ausschließlich dem Updatevertrag und
der dort gebundenen Abschlussentscheidung zu #612. Ein Actions-Dispatch ist
Diagnose. Der installierte Updateclient benötigt weiterhin eine einmalige
ausdrückliche Zustimmung im nativen Steuerfenster und bietet einen sichtbaren
Schalter. Leerer Trust erlaubt keinen Updatekanal; die erste vertrauenswürdig
root-provisionierte Version wird manuell installiert. Gitrefresh und installierte
Programmversion bleiben getrennt.
Nur der normale installierte GUI-Start prüft einmal nebenläufig. Bei bestehendem
Opt-in wartet Browser/Sheet samt erstem Git-Refresh bis zur Updateentscheidung,
bei höherem geprüftem Kandidaten auch bis zum vollständigen Download und Handoff.
Natives Fenster und lokaler Dienst sind sofort bereit. „Ohne Update fortfahren“
verwirft den Versuch sicher und startet Browser/Git genau einmal; die Zustimmung
bleibt gespeichert. Offline-/Signatur-/Downloadfehler geben denselben bisherigen
Arbeitsstart frei. Ohne Opt-in startet er direkt. Ausschalten bricht den Versuch
ab; nach sicher übernommener Helferübergabe sind Skip und Opt-out gesperrt.
Nach vollständiger Verifikation folgen P2-/Requestdrain,
echtes Prozessende, unabhängiger MSI-Helfer und geprüfter Neustart mit demselben
Zustand/Port. Fehler, Rebootbedarf und unklarer Ausgang erfordern manuelle Prüfung,
keinen blinden Retry. Echte Windows-11-Abnahme und Betrieb bleiben eigene Gates.

Das native Steuerfenster bietet bei neuer Einrichtung den vorhandenen lokalen
Projektcheckout und die bewusste Wahl „Nur lokale Gitstände“ (Standard) oder
„Mit Remote aktualisieren“. Standardrefs sind `main` und `content/pw/*`.
Eine kleinere explizite Refwahl über wiederholtes `--ref` ist weiterhin möglich.
Remote-URLs enthalten keine Tokens/Passwörter. Abbrechen startet keinen Dienst
und schreibt keine Konfiguration. Der Datencheckout benötigt **keine ausführbaren
tools-Quellen** und liefert niemals Anwendungscode; sämtliche Reader stammen aus
dem gebundenen App-Build. Fehlende Imports einschließlich `authoring_workflow`,
Bilddekodierung, UI-/Tcl/Tk-Ressourcen, Gitfähigkeit und Einrichtung werden vor
Bereitschaft geprüft. Defekte Installationen regulär deinstallieren und erneut installieren;
der getrennte Zustand bleibt erhalten.

Bestehende `config.json` im Format `picross-production-workspace-config-v1`,
gewählter Remote/Refs, `git-cache-pw-v1` und `sync-pw-v1.json` bleiben nutzbar.
Unbekannte Konfigurationsfelder werden abgewiesen und nicht überschrieben.
Die historische Einengung des unveränderten alten `content/*`-Defaults bleibt
bestehen. Kein Checkoutupdate oder Cacheverwerfen als normaler Startweg.

Ohne `--state` liegt der eigene Zustand unter
`%LOCALAPPDATA%\PicrossProductionWorkspace`. Ein bewusst gewählter anderer
Zustand bleibt über `Picross-Start.exe --state "D:\Eigener Zustand"` erreichbar.
Zustand und Datencheckout müssen getrennt liegen. Launcherdateien liegen separat
unter `.launcher/`: geschützter OS-Lock, kurzlebige authentisierte Instanzmetadaten
und versionierte persistente Portwahl. Sie ändern das geschlossene Configformat nicht.

Pro Windowsbenutzer und kanonischem Zustand läuft eine Instanz. Zweitstart prüft
Identität/Build/Protokoll tatsächlich und öffnet dieselbe Browserinstanz (während
des Update-Startgates nur das Steuerfenster), ohne
zweiten Server/Refresh. Weder PID noch Portdatei allein autorisieren eine Aktion.
Start läuft noch, fremder Dienst, andere Version und verwaiste Metadaten werden
unterschieden. Eine historische laufende CMD zuerst regulär mit Strg+C beenden;
keine automatische Übernahme oder Prozessbeendigung.

Die authentisiert geprüfte Oberfläche öffnet vor Git-Suche/Synchronisierung.
Ab P3 wird derselbe Loopbackport beim Neustart verwendet; Browseroptionen und
Entwürfe bleiben damit an ihrer Origin. Bei fremd belegtem Port Wiederholen oder
**ausdrücklich** einen neuen Port wählen. Dieser hat getrennten Browserzustand.
Keine automatische Migration unbekannter früherer Zufallsport-Origins.

„Im Browser öffnen“ öffnet den Windows-Standardbrowser. Minimieren lässt den
Dienst laufen, Tab schließen beendet ihn nicht. „Assistent beenden“ oder
Fensterschließen sperrt neue Arbeit und wartet sichtbar auf eigene Requests/
Worker. Eine begonnene P2-Transaktion einschließlich Ergebnisprüfung läuft aus;
kein harter Abbruch und keine automatische Wiederholung. Unbekannte Ergebnisse
bleiben als solche sichtbar. Danach sind Port und Lock freigegeben; Konfiguration,
Cache, Browser und Checkout bleiben erhalten. Absturzreste werden erst nach
Erwerb des OS-Locks ersetzt, niemals durch Töten eines gespeicherten PIDs.

Updates erfolgen nach vollständigem Stop per neuerem MSI. Die veröffentlichte Releaseautorität bestimmt neue Produktversionen; stabile Upgrade-
identität, Pins und 0.1.0-Startanker stammen aus [release.json](release.json); die frühere
Paketkennung 588-P3 ist keine Produktversion. Same-Version-Installation und Downgrade
sind gesperrt. Der Installer ersetzt alle eigenen Programmdateien gemeinsam und
fasst Zustand/Cache, Browserprofil, Checkout/Refs und portable Ordner nicht an.
Ein zustandsunabhängiges Windows-Lebenszeichen gilt bereits während Einrichtung
und bleibt bis zum Ende des P2-Drains erhalten. MSI prüft es vor Dateimanipulation,
zusätzlich den alten Standardlock und sämtliche belegten Payloaddateien über
Windows Restart Manager; unklar bedeutet Abbruch. Keine automatische Beendigung.
Während MSI-Ausführung beginnt kein neuer Launcherbetrieb. Deinstallation entfernt
nur eigene installierte Dateien/Links und den Windows-Anwendungseintrag.
„Neuere Ergebnisse suchen“ aktualisiert Gitdaten, keine Programmversion.
Der eigene [Installerbau](WINDOWS_BUILD.md) hat einen Main-CI-Folgetrigger und eine rein diagnostische manuelle Ausführung;
Package CI und regulärer Spiel-Windowsbau bleiben getrennt.

## Entwicklerfallback

[Picross-Start.cmd](Picross-Start.cmd) bleibt ein technischer Fallback mit
vertrauenswürdigem Programmcheckout, Python 3.11+ und isoliertem Pillow 12.3.0.
Die eingebetteten PW-Dateien samt Icon werden SHA-256-geprüft. Unveränderte weitere
Produktionsbibliotheken stammen beim Fallback aus dem vertrauenswürdigen
Programmcheckout. Der EXE-Weg benötigt diesen Codecheckout nicht. Beide verwenden
denselben Instanz-/Port-/Stopvertrag. Die CMD ist kein App-Image und kein Ersatz
für dessen Windowsnachweise.

```powershell
python -m venv .venv-pw
.\.venv-pw\Scripts\Activate.ps1
python -m pip install --only-binary=:all: -r tools/puzzle_production/requirements-image.txt
python -m tools.production_workspace --state "D:\Eigener Zustand"
```

Für explizite erstmalige Einrichtung `--setup --repository` und bei Bedarf
`--remote`/`--ref` verwenden. Bestehende Einrichtung nicht mit neuen CLI-Optionen
überschreiben. `--headless --no-browser` ist allein ein beaufsichtigter technischer
Prozess-/HTTP-Test. `--stop` beendet nur eine tatsächlich passende authentisierte
Instanz. `--port 0` ist ein ausdrücklich gewählter neuer freier Port.

Nach Änderungen an eingebetteten Quellen regenerieren:

```sh
python -m tools.production_workspace.build_launcher
```

Der Regressionstest vergleicht die eingebetteten Bytes mit den Quellen.

## Bedienung und Quellenstatus

Neben der Hauptaktion wählst du ChatGPT oder Codex. Die Werkstatt merkt
sich die Wahl pro beauftragtem Schritt im aktuellen Browser. Ohne eigene Wahl
beginnen Schritt 1, 2 und 4 mit Codex sowie Schritt 3 und 5 mit ChatGPT.
Eine Anschlussabsicht in Schritt 4 ändert die Ausführungswahl eines
Rasterdiagnoseauftrags in Schritt 3 nicht.
Bei „Gezielt korrigieren“ entscheidet das gewählte Bild über den beauftragten
Schritt: auch aus einer späteren Phase verwendet eine Reveal-Korrektur Schritt 1
und dessen Ausführungswahl, eine Motivkorrektur Schritt 2, Rasterkorrektur Schritt 3
und Hintergrundkorrektur Schritt 4.

„Bild neu bewerten“ bietet nur offene Abschlussbilder beziehungsweise
Motivvorlagen der aktuellen Phase an. Der Auftrag bewertet die vorhandenen
Bytes und sichert das Urteil. Codex arbeitet lokal, ChatGPT über den
Bildempfang. Bereits gewählte frühere Bilder lassen sich bei Bedarf als
Korrekturgrundlage verwenden, aber nicht hier neu bewerten.

Bei Codex kannst du hier eine Arbeitswurzel hinterlegen. Beim Wechsel zu
ChatGPT verschwindet das Feld und der Pfad bleibt für Codex gespeichert.
Sende den kopierten ChatGPT-Auftrag in einem neuen Chat. Setze nach einer
Unterbrechung am zuletzt gesichert veröffentlichten Stand an. Offene
Eingaben, Wahlen und der Umfang eines Schlussauftrags bleiben beim
Ausführungswechsel erhalten.
Die Wiederaufnahme veröffentlicht noch offene Arbeit derselben Phase. Eine
vorgemerkte Wahl oder Befundänderung wird dabei nicht abgesendet. Bereits
veröffentlichte Hintergründe werden mit Codex lokal und mit ChatGPT über
PW-REMOTE fertig aufbereitet und bewertet. Frühe Produktionsaufträge enden
bei der gesicherten Auswahlvorlage; der Produkt-PR gehört zum Schlussauftrag.

Vor dem Start eines ChatGPT-Bildempfangs bleibt die ausführbare Textvorschau
leer. Nach „Auftrag starten und kopieren“ sind Vorschau und Kopie an den
gespeicherten Auftrag gebunden. Erneutes Kopieren und Neustart verwenden
denselben Text, auch wenn er vor einem Programmupdate erzeugt wurde. Neue
Vorlagen und geänderte Einstellungen gelten erst für einen neu gestarteten Auftrag.

Reguläre Aufträge lesen aktuelle Regeln aus main und Produktionsdaten aus dem
festen Recordlink. Ein aktivierter ChatGPT-Bildauftrag bindet dagegen auch seine
Regelquellen an den beim Start gelesenen Maincommit. Er enthält die konkrete
Arbeit, neue Eingaben und die private Empfangsbindung; die Verfahren liest der
Akteur über den kurzen [PW-IMPORT-Verweis](../../docs/tools/PW_IMPORT.md).
Eine unveränderte Rekopie hebt die Quellenprüfung vor Veröffentlichung nicht auf.
Hält sie wegen geänderter Regeln an, muss ein nötiger neuer Auftrag bewusst am
aktuellen Stand gestartet werden.

Bei v3-Ständen steht die Bereitschaft auf der Bildkarte. Die Erklärung eines Befunds lässt sich mit Enter öffnen. Beim Bildempfang bindet die Start-und-Kopieraktion Annahme und Behandlung, beim übrigen Auftragsweg das Absenden. „Korrigieren“ an der Karte setzt die Arbeitsgrundlage und springt zum Änderungsfeld. Die Auswahl einer Motivvorlage umfasst auch die konkrete Parameteralternative.

Das Hauptdropdown enthält genau eine offene Produktion pro Rätsel-ID mit Titel
und aktueller Phase; titelgleiche IDs bleiben unterscheidbar. Im bewusst
konfigurierten Remotebetrieb führen nur Remotequellen. Die gültige Spitze von
`content/pw/<puzzle_id>` öffnet direkt, auch bei lokalen Vorsprüngen, Divergenzen
oder einer früheren veröffentlichten Korrekturphase. Tatsächlich offene Main-only-
Arbeit bleibt sichtbar. Die untergeordneten Versions-/Quelldetails dienen der
gezielten Wahl ungeklärter Quellen und der konkreten
Quellwahl für P2. Automatisches Öffnen aktiviert keine Entfernung.
[Ansichtsvertrag](../../docs/tools/PRODUCTION_CURRENT_VIEW.md).

„Neues Motiv“ bleibt der Einstieg vor Veröffentlichung. Unter „Gespeicherte
Motivtexte“ lassen sich lokale Eingaben ausdrücklich öffnen oder verwerfen;
sie erscheinen nicht als laufende Produktionen. Keine Titelzuordnung, automatische
Löschung oder alte Entwurfsöffnung bei Appstart/leerem Ergebnis. Der bewusst
lokale Diagnosebetrieb bleibt lokal eingerichtet. Im Remotebetrieb sind lokale
Refs weiter für P2/Diagnose lesbar, ohne Produktionsalternativen zu erzeugen.

Offline bleibt der alte Remotesnapshot lesbar, samt „Remote nicht aktuell
bestätigt“, Fehler und letzter Cachezeit. Unbestätigte Quellen erlauben keinen
Cloudauftrag. Den aktuellen Record kann der beauftragte Akteur gezielt
zurücklesen; für historische Revisionen bleibt die ausdrückliche alte
Pointerprüfung eine getrennte Diagnose:

```text
python -m tools.production_workspace.projector --repository <checkout> --current-view <pz-ID> <revision>
```

Die Detailansicht leitet freigegebene oder vorgeschlagene Parameter und das
aktuelle Motivbriefing aus dem einzigen Record ab. Beide Bereiche starten nach
Wiederladen und Motiv-/Quellwechsel eingeklappt; Zusammenfassung, Quellenstatus
und Fehler bleiben sichtbar. Eindeutige Einzelwünsche belegen Felder vor;
mehrere Optionen und freie Formen bleiben vollständig lesbar. Die Anzeige
erteilt keine neue menschliche Freigabe. Fehlende oder veränderte gebundene
Nutzdateien erscheinen als Fehler. Für aktuelle Records gilt die Briefgrenze
von 16.384 Zeichen nach PW-B, ohne separaten Handoff oder Pakettext.

Folgeaufträge nennen einen festen erreichbaren Commit mit dem kanonischen Record
als Einstieg und binden AGENTS/Authoring 0.8.0 kurz verbindlich ein. Dieser Einstieg
führt zur phasengerechten Pflichtlektüre einschließlich Bildstil, nicht zurück
zur Volllektüre aller Fachhandbücher. Vorhandene Parameter,
Briefings, Hashlisten und allgemeine Regeln werden dort nicht dupliziert.
Unveränderte Werte bleiben über diese Quelle gebunden. Änderungen sowie
„Neue/zusätzliche Wünsche zur Motivvorlage“ sind neue Absichten. Zum Aufheben
eines bisherigen Wunsches die entsprechende ausdrückliche Aufhebungswahl
verwenden; Breite und Höhe haben eigene Aufhebungswahlen. Die andere Achse bleibt
wirksam. Aufheben hat Vorrang vor dem jeweiligen Feld. Leeren oder „Offen“ allein
sperrt den Auftrag, solange dadurch eine bestehende Vorgabe entfallen würde.
Freigegebene Korridore werden über die Korrektur erneut zur Entscheidung vorgelegt.
Job-, Revisions-, Quellwechsel und „Neueren Stand laden“ verwerfen ungesendete
Absichten; ein bloßer Refresh erhält sie. Entwurfswerte überlagern keine Gitdaten.

System/Hell/Dunkel verwendet ausschließlich die bestehende Browserwahl `pw-theme`.
„System“ bleibt gespeichert und folgt der Systemdarstellung. Reload und ein
geordnetes P3-App-Neustart/Update bei erhaltenem Zustand verwenden denselben Origin.
Andere Browserprofile oder ausdrücklich geänderte Ports haben getrennte Einstellungen.

Bildkarten nach Rollen und der Reveal-/Motivvergleich
laden ihre Originale. Großansicht bietet Einpassen, 100/200/400 Prozent und
neutralen Transparenzprüfgrund. Alle Texte werden als Klartext gerendert.
Auswahlschaltflächen erzeugen nur Auftragsabsichten, keine Freigabe oder Zertifizierung.
Die Anzeige benennt vorhandene Prüfungen ausdrücklich als überlieferte Befunde.

„Neuere Ergebnisse suchen“ aktualisiert lokale Refs und bei gewählter
Synchronisierung ausschließlich den eigenen Gitcache. Die aktive Ansicht bleibt
an ihrer SHA gebunden. „Neueren Stand laden“ übernimmt die neue komplette Liste.
Bis zu acht Listenstände bleiben pro Sitzung erreichbar; danach neu laden.
Unterschiedliche Quellen derselben ID/Revision mit abweichenden Bytes sind
Konflikte. Es wird keine höchste Revisionszeichenfolge gewählt.

PW2-C gleicht konkrete aktuelle Lieferungen mit dem frisch bestätigten
konfigurierten Remote-`main` ab. Registry, Runtime und die betroffenen Livebytes
belegen den Abschluss nach [PW2-C](../../docs/tools/PRODUCTION_WORKSPACE.md#pw2-c--aktive-lieferungen-und-bestätigter-abschluss);
historische ZIPs, Receipts und Produktionsketten werden nicht geöffnet. Regulärer
Merge, Squash und unveränderte Sammelübernahme werden gleich behandelt. Bestätigte
Lieferungen, identische Kopien und eindeutig zugehörige alte Schritte verschwinden
aus der aktiven Liste. Eine offene neue Revision oder spätere Bildarbeit derselben
ID bleibt sichtbar. Unklare Zuordnung wird nicht als Abschluss geraten. Die
aktuellen kompakten Bildquellen binden Identität und Livebytes. Frühere Phasen
werden über unveränderte Record-/Projektionsbytes am bestätigten Integrationscommit
zugeordnet. Mehr als 32 Abschlüsse werden vollständig verarbeitet; identische
Lieferbindungen werden dedupliziert.
Fehlende Belege erscheinen konkret als Fehler und halten betroffene Arbeit offen.

Eine lokale Mainkopie, Cachezeit oder erfolgreiche Suche nur anderer Refs bestätigt
keine Mainintegration. Ohne frischen tatsächlichen Mainbezug bleibt betroffene
Arbeit sichtbar; ein bewusst abgewählter Mainref wird nicht zusätzlich geladen.
Die Liste erklärt diesen Zustand. Passive Suche lässt auch eine inzwischen
abgeschlossene geöffnete Quelle samt Bildern und ungesendeten Eingaben stehen.
Erst „Neueren Stand laden“ meldet deren belegten Entfall und übernimmt offene Arbeit
derselben ID, eine andere Produktion oder den leeren aktiven Zustand. Gespeicherte Motivtexte
bleiben eigenständig gespeichert und werden nicht automatisch geöffnet. Es werden dabei keine Dateien oder Refs gelöscht.

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

Außer der ausdrücklich bestätigten P2-Branchentfernung schreibt der Dienst nur
eigene Einrichtung/Cachedateien: `config.json`,
`git-cache-pw-v1` und `sync-pw-v1.json`. Der frühere `git-cache` und dessen
Synchronisierungsdatei bleiben unangetastet und werden nicht durchsucht.
Kein Pull/Checkout/Reset/Stash/Add/Commit oder Merge im Benutzercheckout.
Die optionale lokale P2-Nachbereinigung entfernt nur den bestätigten sicheren Ref.
Fetch verwendet eine flache Historie (`depth=1`) und `blob:none`, soweit das
Remote Filter unterstützt. Bei ausdrücklich historischen Eingängen gebundene Commits und
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
Kein Browserbildarchiv: Darstellung, persönliche Auftragsoptionen und höchstens
20 lokale Motivbriefings bleiben im Local Storage;
der zufällige Sitzungsschlüssel liegt bis zum Schließen im Session Storage,
damit Neuladen funktioniert. Er erscheint weder in Logs noch technischen Details.

## Produktion entfernen (P2)

Beim gewählten Remote-Produktionsstand öffnet „Produktion entfernen“ zunächst
nur eine Vorprüfung. Sie nennt den ganzen Branch einschließlich aller sichtbaren
Revisionen, die aktuelle SHA, Worktrees, lokale Refreste, PRs und Mainstände.
Die Aktion entfernt den Branch im konfigurierten Remote; integrierte Inhalte auf
main bleiben erhalten. Den genauen angezeigten Branchnamen selbst eingeben und
„Remote-Branch jetzt entfernen“ bestätigen. Pläne laufen nach drei Minuten ab
und sind nur einmal nutzbar. Nach einem Quellenwechsel neu vorprüfen.

Nur der konfigurierte öffentliche GitHub-Remote `venomenon328/picross` über
HTTPS/SSH ist produktiv freigegeben. Andere Quellen erklären ihre Sperre.
Offene PRs, unprüfbarer GitHub-Status, ausgecheckte Zielbranches, abweichende
lokale Commits und geänderte Remote-SHAs verhindern die Entfernung. Geschlossene
PRs und vorhandene Mainintegration werden ausdrücklich eingeordnet. Vorhandene
nichtinteraktive Git-Anmeldung verwenden; keine neue Anmeldung in der UI.

Ein Erfolg wird erst nach Prüfung des entfernten Remote-Refs gemeldet.
Cachefehler oder ein unbekannter Ausgang bleiben sichtbar und verlangen eine
neue Quellenprüfung. Lokale und Mainstände werden weiter gelesen; in der aktiven
Auswahl bleiben offene oder nicht eindeutig abgeschlossene Lieferungen. Ein sicherer
lokaler Branchref kann danach optional, zunächst abgewählt, in einem eigenen
Bestätigungsdialog bereinigt werden. Das löscht keine Arbeitsdatei oder Worktree.

P2-T01–T03 prüfen ausschließlich eigens erstellte synthetische Bare-Remotes und
Testrefs; der kontrollierte Testadapter ist keine Benutzer-/HTTP-Einstellung.
Die nicht gelieferten P2-Browser-/PNG-/A01-Gates wurden für P2 ausdrücklich
[aufgehoben](https://github.com/venomenon328/picross/pull/590#issuecomment-6809311950),
nicht als bestanden bestätigt. P3 hat eigene T01–T03-/A01-Nachweise.

## Aktuelle Veröffentlichung und abgeleitete Ansicht

Neue Produktion verwendet genau den aktuellen Record nach
[PW-B](../../docs/tools/PW_B_CONTRACT.md). Builder und Finalizer veröffentlichen
Record, benötigte Nutzdateien und den gemeinsamen Verweisindex unter denselben
Lock-/CAS-/Recoveryguards. Liste, Angebote, Bilder und Folgeauftrag werden daraus
am fixierten Gitstand abgeleitet. Kein obligatorisches workspace.json,
current-view.json, ZIP oder historischer Originalbezug für aktuelle Jobs.

Der Produktionsakteur sichert die aktuellen Arbeitsbytes samt Index per Git.
Noch angebotene Varianten bleiben bis zur echten inhaltsgebundenen Entscheidung
erreichbar. Eine allein gesetzte selected-Kennung autorisiert keine Bereinigung.
Rasteransichten werden aus der gebundenen Definition gerendert; die aktuelle
PNG-Vorschau wird zusätzlich semantisch gegen Matrix und Palette geprüft.

Optionaler gezielter Readback einer bestehenden aktuellen Veröffentlichung:

~~~sh
python -m tools.production_workspace.projector --repository /absoluter/arbeitscheckout --current-view pz-beispiel current
~~~

Dieser aktuelle Readback erzeugt keine separate Ansichts- oder Pointerdatei.
Die früheren Projektorrequests, workspace-/Pointerdateien und Paket-/Historyformen
sind ausschließlich historische Eingänge. Sie stehen am
[Stand vor PROD-SLIM](https://github.com/venomenon328/picross/blob/d389fbad01dd01860ed949a4e1e8e0b52c21362a/tools/production_workspace/README.md#projektor-für-den-produktionsakteur);
keine automatische Migration oder Wiederherstellung entfernter Archive.

## Tatsächlicher Registrierungsabschluss

Der endgültige aktuelle Record wird aus der Arbeitskopie als temporärer
RI-ONE-Eingang vorbereitet:

~~~sh
python -m tools.puzzle_production.authoring_builder prepare-integration --repository /absoluter/arbeitscheckout --record content/authoring/pz-beispiel/current/record.json --output-dir /absoluter/aktueller-eingang
python -m tools.puzzle_production.target_adapter plan --input /absoluter/aktueller-eingang --pw-worktree /absoluter/arbeitscheckout --checkout /absoluter/integrationscheckout
python -m tools.puzzle_production.target_adapter register --input /absoluter/aktueller-eingang --pw-worktree /absoluter/arbeitscheckout --checkout /absoluter/integrationscheckout
~~~

Der saubere Integrationsbranch entsteht vom aktuellen Main und übernimmt nur
gewählte Produktdaten über den gemeinsamen Integrationskern. Seine tatsächliche
Registrierung committen. Danach in der Arbeitskopie:

~~~sh
python -m tools.production_workspace.projector --repository /absoluter/arbeitscheckout --complete-record content/authoring/pz-beispiel/current/record.json --integration-commit <volle-SHA> --input /absoluter/aktueller-eingang
~~~

Completion registriert nichts. Es prüft die tatsächliche gewählte Lieferung samt
Rechten, Modus und Bewertung am genannten Commit und aktualisiert ausschließlich
den aktuellen Arbeitsrecord. Für reine Hintergrundpflege ist --input der aus
dem aktuellen Record vorbereitete Editor-Eingangsordner. Beide Wege verwenden
die gemeinsamen Writer; kein vorheriger Import des Arbeitsarchivs nach Main.
Den geänderten Record committen/pushen. Nach bestätigtem Mainergebnis erfolgt das
gezielte Retirement nach Authoring Schritt 5. Fehlende oder geänderte aktuelle
Arbeitsbytes bleiben vor diesem Abschluss sichtbar; die Liste prüft ihre Bindungen
frisch ohne erneuten Solverlauf. Ein separater späterer Hintergrundauftrag beginnt
an der tatsächlichen aktiven Runtime-/Bildsource.

## Sicherheits- und Prüfgrenzen

Loopback, exakter Host/Origin, Sitzungsschlüssel und keine CORS-Freigabe.
Die API akzeptiert nur serververgebene Job-/Assetkennungen, keine Pfade/Refs/URLs.
CSP erlaubt eigene UI und lokal erzeugte Bild-Blob-URLs; HTML/SVG aus Paketen
werden nicht ausgeführt. Gitlinks/Submodule, ZIP-Aliase, Spezialdateien,
CRC-/Hash-/Größenfehler und beschädigte Bilder werden zurückgewiesen.
Aktuelle Record-/Nutzdateigrenzen stehen in PW-B; die 32-MiB-/8-Megapixel-
Bildgrenzen bleiben erhalten. Historische Paketreader behalten ihre geschlossenen
Paketlimits. Der Reader bestätigt keine neue Inhaltsfreigabe.

Kleine Regressionen: `python -m unittest tools.test_production_workspace -v`
in der isolierten Imageumgebung, mit Node.js 22+ für die browserfreie Ausführung
des tatsächlichen UI-Ladecodes gegen einen langsamen lokalen HTTP-Dienst.
Die DOM-Testnachbildung prüft keine Darstellung oder echte Browserbedienung.
Sie prüft getrennt echte Fetch-Abbrüche bei fünf Sekunden weiterlaufender
Serverarbeit und verspätet eintreffende Bildantworten.
Der einmalige PW-B-T01-Durchstich und die
wirkliche Windows-/Browserprobe T02 werden am konkreten Lieferhead im PR geführt.
Linux-/HTTP-Tests ersetzen die Windowsprobe nicht. Die getrennten Vor-Merge-Gates
PW-B-A01 und PW-B-M01 stehen in der ursprünglichen Paketentscheidung; spätere
paketbezogene Entscheidungen und der tatsächliche Abschluss in #578 bleiben
maßgeblich. Daraus entstehen keine neuen PW2-A-Browser-/Bildprüfpflichten.


## PW-PERF-C · aufrufgebundene Prüfung und Hintergrund v2

Aktuelle Publikation, Ansichtsprüfung und Wiederholung verwenden die gebundenen
Nutzdaten nach PW-B sowie den gemeinsamen RI-ONE-Eingang. Prüfungen beginnen
bei jedem unabhängigen Aufruf frisch; keine Befunde über Ziele oder Locks hinweg
weiterverwenden. Der aktuelle Finalizer verwendet denselben Recordwriter,
keine separate Paket-/Sidecar-/Projektionskette.

Die früheren HP-W2-v1/v2-Requests, Ableitungsbefunde und der gemeinsame
Paket-/Projektionskontext sind historische Formen. Ihr damaliger Vertrag steht
am [Stand vor PROD-SLIM](https://github.com/venomenon328/picross/blob/d389fbad01dd01860ed949a4e1e8e0b52c21362a/tools/production_workspace/README.md#pw-perf-c--aufrufgebundene-prüfung-und-hintergrund-v2).
Sie sind keine Voraussetzung aktueller Bilder und werden nicht automatisch
rekonstruiert oder neu versiegelt.

## HG31: explizite Profilwahl

Neue Einzelkompositionen sind exakt 3:1. Der aktuelle Bildhelfer
`python -m tools.puzzle_production.current_tools background --input <datei> --output <neue-png>`
verwendet standardmäßig picross-background-png2304x768-v1 und erzeugt ausschließlich
das aktuelle 2304×768-RGBA8-PNG. Keine Ableitungs-/Codec-/Generatorhistorie.
Aktuelle Rechte und Bildurteile stehen kompakt im Record.

Fertigimport erkennt 2304×768 bzw. bestehende 2304×576 aus validierten PNG-Bytes
und übernimmt unverändert. V1-Capability erlaubt ausschließlich das alte Profil.
Der [geschlossene Bildprofilvertrag](../../docs/production/PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile)
bleibt verbindlich. Das alte Profil wird nicht automatisch konvertiert.
