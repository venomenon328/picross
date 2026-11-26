# PW-IMPORT: gebundener Eingang für Produktionsdateien

Dokument-ID: `pw-import`
Status: `approved-specification`
Zuständigkeit: Transport und lokale Übernahme neuer kreativer Produktionsdateien.
Umsetzung und Prüfplan: [PW-IMPORT / #910](https://github.com/venomenon328/picross/issues/910), Paket `PW-IMPORT-A`.

Der lokale Empfänger verwendet für jeden aktivierten Auftrag den v3-Builder
und den PW-LOCAL-Publisher. Der Browser zeigt den veröffentlichten Record. Die tatsächliche Lieferung
und die Erfüllung der Startvoraussetzungen stehen im Issue/PR. Der schrittweise
Produktionsabschluss bleibt bei [PW-FINAL / #907](https://github.com/venomenon328/picross/issues/907).

## IMPORT-01 · Zweck und Zuständigkeiten

ChatGPT erzeugt und korrigiert native Bildoriginale, sichtet sie tatsächlich und
liefert die fachlichen Angaben. Der verbundene Google-Drive-Connector transportiert
Originalbytes und eine kleine maschinenlesbare Lieferung in einen privaten Ordner.
Native Dateireferenzen werden programmatisch an den Connector übergeben. Keine
Base64-Bildnutzlast im Modellkontext, Rekonstruktion oder Neucodierung als Transport.
Drive für Desktop stellt diesen Ordner unter Windows bereit. Die installierte
PW-App empfängt die Dateien automatisch, prüft die gebundene Lieferung und
veröffentlicht sie mit dem gemeinsamen [Builder/Publisher](PW_B_CONTRACT.md#bau-auswahl-und-sichere-fortschreibung).

Der Datenweg endet erst am unabhängig zurückgelesenen Arbeitscommit mit den
zugehörigen Releaseassets. Eine Drive-Uploadbestätigung heißt lediglich
„bereitgestellt“. Der kanonische aktuelle Produktionsrecord bleibt die einzige
fachliche Autorität. Eine lokale Eingangsdatei, ein Manifest oder eine
Transportquittung ist keine zweite bearbeitbare Produktion.

Keine reguläre manuelle Datei-, ZIP- oder JSON-Übergabe. Kein Modell-API-Aufruf
aus PW, eigener Uploaddienst, öffentlicher Drive-Link oder neue Drive-API-Anmeldung.
Die App verwendet den eingerichteten lokalen Ordner; sie bindet keinen
Drive-Connector ein. Der vorhandene Git-/REST-Zugang des Publishers wird genutzt.
Fehlende Fähigkeiten oder Berechtigungen bleiben konkrete Voraussetzungen;
die Transportstudien erteilen keine zusätzlichen Rechte.

## IMPORT-02 · Unterstützte Phasen

Der erste vertikale Schnitt deckt alle drei kreativen Bildrollen neuer,
nach dem CAT-CONS-Cutover begonnener und aktuell unterstützter Produktionen ab.

| Produktionsphase | Lieferinhalt und Wirkung |
| --- | --- |
| Schritt 1 · Abschlussbilder | Neue Einzeloriginale, Briefing, Herkunft/Rechte und tatsächliche Sichtbefunde; Neuanlage oder gebundene Korrektur des Revealangebots. Noch keine Auswahl künftiger Bilder. |
| Schritt 2 · Motivvorlage | Gewähltes Reveal bleibt gebunden; neue Motivoriginale, geschützte Merkmale und vollständige Parametervorschläge. Eine ausdrücklich erklärte Revealwahl darf übernommen werden; Motiv-/Parameterfreigabe wird nicht aus Dateieingang abgeleitet. |
| Schritt 3 · Rasterangebote | Der vorhandene [Remote-/Fachkern](PW_REMOTE.md) bleibt zuständig für Berechnung, Proof, Schwierigkeit und Originalzustellung. Korrigierte kreative Eingangsdateien verwenden die gebundene Schritt-2-Lieferung. PW-IMPORT führt kein zweites Rasterverfahren und keinen beliebigen Import fremder Raster-/Proofdateien ein. |
| Schritt 4 · Hintergrund | Native Kontextoriginale und Korrekturen, erforderliche Profilangaben sowie tatsächlich ausgeführte Sichturteile. Vorhandene Aufbereitung und Prüfung werden weiterverwendet; eine vorhandene Rasterwahl bleibt gebunden. Nach Veröffentlichung erfolgen Aufbereitung und Bewertung über den bestehenden Remote-Weg. |
| Schritt 5 · Abschluss | PW-FINAL übernimmt veröffentlichte, qualifizierte Eingänge und die tatsächliche Schlussentscheidung. Stellt die Sichtung einen kreativen Korrekturbedarf fest, läuft die neue Lieferung in ihrer betroffenen Phase; danach werden nur betroffene Entscheidungen/Nachweise erneuert. |

Für Schritt 4 sind Eingang des Originals, HP-W2-Aufbereitung und Sichtung der
tatsächlichen Ausgabe verschiedene Tatsachen. Nach Veröffentlichung kann der
ChatGPT-Akteur die bestehenden `step4 prepare`-/Originalzustellungsoperationen
verwenden und anschließend seine Bewertung an genau diese Bytes binden. Ein
bloß importiertes Original wird dadurch nicht als fertig vorbereitet oder
wählbar ausgegeben. Die anschließende Bewertung verwendet das vorhandene
Remote-Assessment am tatsächlich vorbereiteten Stand. Sie sendet keine zweite
Lieferung gegen die inzwischen verbrauchte Eingangsbindung.

Der Auftrag darf die technische Fortsetzung nach bestätigtem Import bereits
enthalten. Dann setzt derselbe Akteur bei erreichbarem Ergebnis ohne erneute
Routinebestätigung fort. Ist die lokale App aus oder bleibt die Synchronisierung
offen, lautet das Ergebnis „Übernahme ausstehend“ mit dem tatsächlichen
Wiederaufnahmepunkt. Keine erfundene automatische Chatfortsetzung.

Spätere Pflege bereits registrierter IDs bleibt beim Bestandseditor und dessen
Revisionsvertrag. Der Transport ist wiederverwendbar, aber `PW-IMPORT-A` führt
keinen zusätzlichen Writer für registrierte Reveals, Hintergründe oder Katalogdaten
ein. Keine Migration alter WIP-Stände.

## IMPORT-03 · Einrichtung und tatsächlicher Auftrag

In den Einstellungen speichert der Benutzer den privaten Drive-Stammordner und dessen lokales
Eingangsverzeichnis. Die Cloud-Ordner-ID ist eine nicht geheime Auftragsbindung;
der Windows-Pfad bleibt lokale Einrichtung und wird nicht als Cloudquelle
ausgegeben. Der App-Gitcache und die eigene vollständige Gitbasis liegen
außerhalb des synchronisierten Eingangs. Keine Speicherung persönlicher Pfade
oder Zugangsdaten im Repository.

„Auftrag starten und kopieren“ im Produktionsbereich aktiviert genau einen Empfang.
PW weist dem Entwurf beim ersten Start eine freie Produktions-ID zu. Jeder neue
Auftrag bindet einen direkten Kindordner mit dieser ID. Nur ChatGPT löst dessen
Namen, Typ und Elternbindung vollständig paginiert über den Drive-Connector auf.
Bei Abwesenheit erstellt der Akteur den Ordner einmal. Nach Antwortverlust und
vor dem Upload prüft er die eindeutige Zuordnung erneut und verwendet die
tatsächliche Ordner-ID. Ein gleichnamiger Nichtordner oder mehrere Treffer
sperren die Lieferung. PW wartet auf das synchronisierte Kindverzeichnis.
Eine geänderte Einstellung gilt für neu gestartete Aufträge. Vor dem Update
begonnene flache Lieferungen werden im ursprünglich gebundenen Eingang beendet.
Die Aktion nennt verständlich, dass passende Ergebnisse automatisch geprüft
und als Arbeitsstand veröffentlicht werden. Sie bindet serverseitig
Repository, Job, Phase, konkrete Absicht, erwarteten Arbeitsstand, zulässige
Inhaltsänderung und tatsächlich erklärte Auswahl-/Befundentscheidungen.
Einmalige Ordnereinrichtung, passive Vorschau und bloßes Kopieren bleiben
ohne fachliche Schreib- oder Freigabewirkung. Die App darf diese Unterscheidung
nicht hinter einem unverändert beschrifteten Kopierbutton verstecken.

Die tatsächliche Startaktion kann eine bereits gewählte und angezeigte
Kandidatenentscheidung zugleich erklären. Sie erteilt keine Auswahl künftig
gelieferter Bytes und keine Endabnahme, Integration, Merge- oder Retirementbefugnis.
Bestehende gültige Erklärungen werden übernommen. Der Lieferant darf keine
zusätzlichen Erklärungen oder Befugniserweiterungen behaupten.

Pro Job gibt es höchstens einen aktiven Empfangsauftrag; andere Jobs dürfen
unabhängig warten. Abbrechen oder Ersetzen eines Empfangs macht die alte
Auftragskennung unwirksam, erhält aber ungesicherte Dateien. Neustart erhält
den aktiven gebundenen Empfang. Änderungen an der zugehörigen Produktionsbasis
werden vor Veröffentlichung neu geprüft.

Ein Empfangsauftrag übernimmt höchstens eine wirksame Lieferung. Danach ist
seine Kennung verbraucht. Eine weitere Inbox-Korrektur oder reine
Bewertungsfortschreibung braucht einen neu aktivierten Auftrag am aktuellen
veröffentlichten Stand. Der Empfänger bindet einen alten Auftrag nicht
automatisch an einen nachträglichen Workhead. Die bereits beauftragte
Remote-Fortsetzung nach Schritt 4 verwendet ihren eigenen bestehenden
Erwartungs-/Wiederaufnahmevertrag.

Der kopierte ChatGPT-Auftrag enthält die feste Quellenreferenz beziehungsweise
das neue Motivbriefing, neue Absicht, zulässigen Umfang, Zielordner-ID und
Auftragskennung sowie einen kurzen Verweis auf diesen Vertrag und Authoring.

Der Empfänger bindet neue Motivhinweise, Rasterwünsche je Achse, ausdrücklich
aufgehobene Vorgaben, Motivvorlagenwünsche, Korrekturtext und Kontextwunsch an
die gewählte Bildrolle und Handlung. Bei der Neuanlage wird das gebundene
Briefing übernommen. Bei bestehenden Jobs bleibt das bisherige Briefing erhalten;
neue Absichten werden als exakt gebundener Zusatz fortgeschrieben. Der normale
Auftragsweg bindet den Namen, die Bytezahl und SHA-256 der gewählten PNG-/JPEG-
Referenz. Der Benutzer hängt die Datei beim Absenden nativ in ChatGPT an.
Vor der Generierung öffnet der Akteur die tatsächliche Anlage, prüft alle drei
Werte und dokumentiert die erforderliche Herkunft. Eine fehlende oder mehrdeutige
Anlage sperrt die abhängige Generierung. Bei der ersten Reveal-Lieferung ist
genau diese Referenz als zusätzliches `input`-Asset zulässig und erforderlich.
Folgeaufträge verwenden die aktiven veröffentlichten Quellen.

## IMPORT-04 · Geschlossene Lieferhülle

Eine Lieferung besteht aus genau einem Manifest und den darin referenzierten
neuen Nutzdateien. Der vorhandene Builderrequest wird eingebettet, nicht neu
erfunden. Das Manifest ist UTF-8-JSON ohne doppelte Schlüssel oder nicht endliche
Zahlen; unbekannte Felder und nicht unterstützte Versionen werden abgewiesen.

Format `picross-production-inbox-v1`, exakt folgende Felder:

| Feld | Typ und Bedeutung |
| --- | --- |
| `format` | Exakt `picross-production-inbox-v1`. |
| `delivery_id` | Kleine kanonische UUIDv4; unveränderliche Identität genau dieser Lieferung. |
| `request_id` | Kleine kanonische UUIDv4 des lokal aktiven Auftrags. Keine eigene Befugnis. |
| `repository` | Exakt das bestätigte Produktionsrepository `venomenon328/picross`; Diagnoseadapter bleiben außerhalb der Auslieferung. |
| `puzzle_id` | Geschlossene aktuelle PW-B-ID; bereits vom Auftrag gebunden, auch bei Neuanlage. |
| `phase` | Genau `reveal`, `motif` oder `background`. |
| `source` | Genau `main_commit,work_head,record_sha256`; volle kleine 40-stellige Commit-SHAs beziehungsweise 64-stelliger SHA-256. `work_head` und `record_sha256` sind gemeinsam null nur bei Neuanlage, sonst beide gesetzt. |
| `request` | Vollständiger `picross-authoring-current-request-v1`-Request nach PW-B mit `format,record,expected,files`; aktueller v3-Draft. `expected` entspricht `source.record_sha256`. |

`source.main_commit` bindet die gelesene Regel-/Katalogbasis; Workhead und
Recordhash binden den bearbeiteten Job. Alle Werte müssen zum gespeicherten
lokalen Auftrag passen. Eine passende UUID allein genügt nicht. Der Empfänger
prüft den tatsächlichen Recorddelta gegen Phase, Absicht, neue Eingaben und
erklärte Entscheidungen. Keine beliebigen Felder, Befugnisse oder fremden IDs
durch Ersetzen eines vollständigen Records einschleusen.

Manifest maximal 2 MiB, eingebetteter Record weiterhin maximal 1 MiB; übrige
Datei-, Mengen-, Tiefen- und Dekodierungsgrenzen bleiben in PW-B maßgeblich.
`files` nennt ausschließlich neue erforderliche Nutzbytes. Bereits veröffentlichte
Dateien werden mit ihrer vorhandenen Bindung referenziert und gezielt bezogen.
Neue PNG-Originale sind byteidentische Generatorausgaben; technische Ableitungen
bleiben ausdrücklich eigene, an die Eingabe gebundene Dateien.

Manifestname: `<delivery_id>.json`. Neue lokale Quelldateinamen:
`<delivery_id>--<laufnummer>.<typ>`, mit fortlaufender positiver Dezimalzahl ohne
führende Nullen. Der Typ ist `png`, `jpg`, `jpeg`, `svg`, `json` oder `txt` und
muss für die konkrete Rolle im aktuellen PW-B-Vertrag zulässig sein. `source`
im Dateieintrag ist genau dieser einfache Dateiname;
der Ziel-`path` bleibt die geprüfte eigene PW-B-Dateibindung. Namensauflösung
niemals anhand eines ähnlichen Dateinamens oder des neuesten Zeitstempels.
Doppelte Namen, Case-/Windowsaliase und widersprüchliche Liefer-IDs sind Fehler.
Unterverzeichnisse, Archive, Links und Spezialdateien werden nicht als
Nutzdateien dieser Lieferhülle verfolgt.

Der Erzeuger lädt die Nutzdateien zuerst und das abschließend erzeugte Manifest
zuletzt hoch; nach dieser Veröffentlichung wird die Lieferung nicht verändert.
Eine korrigierte Lieferung erhält eine neue `delivery_id` und muss noch zum
aktiven Auftrag passen. Der Empfänger darf sich auf die Reihenfolge des
Windows-Eingangs nicht verlassen.

Sind mehrere unterschiedliche Lieferungen für denselben Auftrag vorhanden,
bleibt die Übernahme als Konflikt stehen. Es wird nicht die erste, neueste oder
zuletzt vollständig synchronisierte Variante geraten. Eine ungültige Lieferung
wird nur durch einen ausdrücklich ersetzten, frisch gebundenen Empfangsauftrag
abgelöst; technisch identische Wiederholung behält ihre Lieferkennung.

Die Eingangskennung wird im begrenzten aktuellen Operationszustand geführt,
nicht durch Pflichtfelder oder dauerhafte Historien im Produktionsrecord.
Ein maschinenlesbarer Validator für diese Hülle und die Abbildung auf den
bestehenden Builder gehören zur Implementierung; die ausführbare Hüllenprüfung steht in
[inbox_contract.py](../../tools/production_workspace/inbox_contract.py).

## IMPORT-05 · Empfang, Integrität und Veröffentlichung

1. Beim Start und während aktivierter Aufträge nach passenden Manifesten suchen.
   Dateisystemereignisse sind ein Hinweis; ein begrenzter erneuter Scan muss
   auch verpasste Ereignisse und einen zuvor ausgeschalteten PW abdecken.
   Auch das Manifest selbst kann erst teilweise synchronisiert sein. Ein
   unvollständig oder wechselnd gelesener JSON-Stand verbraucht den Auftrag
   nicht; nach erneuter vollständiger Lesung wird er nochmals geprüft. Ein
   vollständig gelesener widersprüchlicher Inhalt bleibt ein konkreter Fehler.
2. Fehlende, gesperrte, offline nicht lesbare oder noch unvollständige Dateien
   zeigen „Wartet auf vollständige Dateien“. Tatsächliches Lesen darf normale
   Drive-Streamingdateien hydratisieren; vorheriges manuelles Öffnen oder
   Offline-Pinnen ist keine Voraussetzung.
3. Erst vollständig gelesene Bytes mit Größe und SHA-256 jedes Dateieintrags
   sowie tatsächlichem Dateiformat/Dekoder prüfen. Abweichende vollständige
   Inhalte bleiben gesperrt; kein Abgleich nur anhand von Metadaten oder Größe.
   Wartebudgets enden mit wiederaufnehmbarem Status, nicht mit Datenverlust.
4. Eine eigene stabile Arbeitskopie außerhalb der Synchronisierung erzeugen.
   Prüfen und veröffentlichen müssen genau dieselben Bytes. Quellenwechsel
   während Lesen, Kopieren oder Publikation darf weder gemischte Snapshots
   noch eine unbemerkte zweite Version ergeben.
   Das gilt ebenso für die Manifestbytes und ihren gespeicherten Lieferhash;
   kein späteres Nachlesen eines veränderten Manifests für dieselbe Mutation.
5. Vor jedem Schreiben gespeicherten Auftrag, frische Remote-/Katalogquelle,
   erwarteten Workhead, Recordhash, Releasegeneration und zulässige Änderungen
   prüfen. Fremder Fortschritt desselben Jobs stoppt mit konkretem Konflikt.
   Unabhängiger Mainfortschritt verlangt einen frischen fachlichen Abgleich;
   keine pauschale erneute Bildfreigabe bei identischem Inhalt und kein
   automatisches Umschreiben der erwarteten Jobbasis.
6. Bestehenden Builder, Qualifikationskern, [PW-LOCAL](PRODUCTION_GIT_WORKSPACE.md)
   und `tools.work_publish` verwenden. Nur eigene benötigte Originalassets
   und der aktuelle Record/Index werden veröffentlicht. Originalbytes bleiben
   außerhalb der Git-Historie. Vorabobjektprüfung, gemeinsame Locks, atomare
   erwartete Headbindung und separate Readbacks bleiben verbindlich.
7. Erfolg verlangt zurückgelesenen Arbeitscommit, aktuellen Record und
   byte-/identitätsgebundene Releaseassets. PW übernimmt die veröffentlichte
   Ansicht mit sichtbarem Aktualisierungshinweis; bestehende ungesendete
   Eingaben werden nicht still auf neue Quellen übertragen.

Der lokale Writer führt ausschließlich installierte vertrauenswürdige
Werkzeugmodule aus. Produktionsrecord, Liefermanifest und Datencheckout liefern
keinen Code, keine Shellparameter, keine freien Download-/Gitziele oder
Löschpfade. Session-, Origin-, Pfad- und Produktidentitätsgrenzen gelten weiter.
Git-/REST-Identität wird vor der Operation bewusst gewählt; keine neue
Tokenablage im Browser, Manifest, Record oder Log. Öffentliches Lesen allein
beweist keine Schreibfähigkeit.

## IMPORT-06 · Qualität und Entscheidungen

Transportprüfung, technische Qualifikation, tatsächliche Sichtung und
menschliche Entscheidung bleiben getrennt. Der gemeinsame Builder berechnet
die erforderlichen technischen Fakten an den Originalen; mitgesendete
Erfolgsbehauptungen sind keine Prüfquelle. Der Akteur liefert nur tatsächlich
ausgeführte Sichturteile mit konkreter Kandidaten-/Bytebindung. Unbekannte
Befunde bleiben unbekannt.

Die blockierenden Kernanforderungen und zulässigen Detailannahmen für Revealbilder
stehen in [Qualität §3.1](../production/PUZZLE_QUALITY.md#31-abschlussbildphase)
und den zugehörigen [Bildtypnormen](../production/images/README.md).
[Schritt 1 §2.4](../production/authoring/PUZZLE_AUTHORING_STEP_1.md#24-abschlussbildauswahl-und-abstraktionsfreigabe)
und die gemeinsame Bildkorrektur regeln die erforderliche weitere Korrektur:
Ein Dreierangebot wird nicht mit mangelhaften Kandidaten aufgefüllt.
Der Import setzt diese Regeln um, ohne eine zweite Qualitätstabelle einzuführen.
Rastervorschauen werden nicht an Revealstilregeln gemessen. Bestehende tatsächlich
verbrauchte Budgets und nötige Budgeterklärungen werden ehrlich fortgeschrieben;
kein heimliches Zurücksetzen und keine erfundene Erhöhung.

Unqualifizierte Zwischenstände dürfen nach dem aktuellen Phasenvertrag
gesichert und als solche sichtbar bleiben. Sie zählen nicht als fertige
Angebote und lösen keinen automatischen Phasenfortschritt aus. Übermittelte
Grafiken mit Prüftabellen sind Illustrationen, keine maschinellen Prüfergebnisse.
Alphakanalbereich, Randpixel oder Bytegleichheit allein ersetzen keine
visuelle Prüfung. Der Transport verändert keine Alpha- oder Farbdaten, um
einen Befund scheinbar zu beheben.

Die fachliche Qualitätsnorm bleibt [PUZZLE_QUALITY](../production/PUZZLE_QUALITY.md)
mit den [Bildtypnormen](../production/images/README.md). Der gemeinsame Qualifikationskern prüft freie und sichtbare PNG-Bereiche. Die
gezeichnete Ausarbeitung beurteilt der sichtig arbeitende Akteur am Original.

## IMPORT-07 · Wiederaufnahme und begrenzte Bereinigung

Vor Mutationen aktuellen Operationszustand sichern: Auftrag und Lieferhash,
gebundene Eingänge, Publikationsabsicht sowie erwartete/beobachtete Ref- und
Assetbindungen. Keine zweite Produktionshistorie. Nach Antwortverlust zunächst
gezielt nachlesen; bestätigte eigene Veröffentlichung übernehmen, niemals blind
erneut hochladen oder einen weiteren Job erzeugen.

Erkennt der Empfänger bei einem gespeicherten Build einen fremden Nachfolgecommit,
prüft er lokalen Worktree, Publikationsjournal und den Remote-Record. Bei bestätigtem
unveröffentlichtem Build lässt sich der Auftrag widerrufen und am frischen Stand
neu binden. Der frühere Arbeitsbaum und die gebundenen Eingangskopien bleiben
erhalten. Bei unklarem Publikationsausgang bleibt die Wiederaufnahme mit Readback
erforderlich.

Identische Wiederholung derselben Lieferung bewirkt höchstens die Fortsetzung
ihres offenen Schritts. Abweichende Bytes bei gleicher Lieferkennung sind ein
Konflikt. Verbrauchte oder widerrufene Aufträge dürfen auch nach Entfernung der
Quittung nicht erneut publizieren. Die kleine aktuelle Quittung darf nur so lange
erhalten bleiben, wie Anzeige, Rückbestätigung oder Wiederaufnahme sie benötigt.

Erst nach bestätigter GitHub-Publikation dürfen die exakt zu dieser Lieferung
gehörenden unveränderten Eingangsdateien und das Manifest automatisch entfernt
werden. Diese gebundene Bereinigung gehört zum bewusst gestarteten Auftrag;
keine zusätzliche Routinebestätigung. Vor Entfernen erneut Identität, Pfad und
Bytes prüfen. Nachträglich geänderte Dateien, fremde Dateien und ganze
Eingangsordner bleiben erhalten. Ein Fehler erhält die noch benötigten Quellen.

Veröffentlichungserfolg und Bereinigungsrest sind getrennt. Ein lokaler
Löschabschluss belegt keine sofortige Cloudlöschung oder Papierkorbleerung.
Die verzögerte Drive-Synchronisierung wird nicht durch eine zweite Cloud-API
oder vorsorgliche Wiederholungsuploads kompensiert. Nach Neustart sind offene
eigene Publikations-/Bereinigungsreste weiterhin erreichbar.

Bestehende berechtigte Entfernung ausgeschiedener Arbeitsrelease-Alternativen
bleibt beim Publisher. Die Entfernung einer ganzen Produktion, Release-/Tag-
Retirement und allgemeine Arbeitsplatzbereinigung werden nicht aus dem
Eingangsauftrag abgeleitet. Appstop und Update warten auf eine sichere Grenze
oder hinterlassen einen konkret wiederaufnehmbaren eigenen Zustand.

## IMPORT-08 · Liefergrenze und gemeinsame Weiterentwicklung

`PW-IMPORT-A` umfasst Auftragsbindung, Producervertrag, lokalen Empfang,
Builder-/Publisheranschluss, Anzeige/Fehler/Wiederaufnahme und tatsächliche
Windows-Paketierung. Ein Ordnerwächter oder isolierter JSON-Parser allein erfüllt
das Paket nicht. Benötigte Writer und Ressourcen gehören in das geprüfte
Frozen-/MSI-Payload; Code aus einem Benutzercheckout ersetzt sie nicht.

PW-IMPORT stellt nur die gemeinsam benötigten Writer-/Operationsbausteine bereit.
PW-FINAL verwendet sie weiter und ergänzt seinen begrenzten Abschlusscontroller.
Keine zwei Git-Stores, konkurrierenden Locks oder parallel gepflegten Publisher.
Die vorhandene lesende Ansicht bleibt an veröffentlichte Snapshots gebunden.

Pflichtquellen und aktive Beschreibungen werden mit der Implementierung an den
tatsächlich unterstützten Stand angepasst: PRODUCTION_WORKSPACE, PW_B_CONTRACT,
PRODUCTION_GIT_WORKSPACE, PW_REMOTE, betroffene Authoring-/Qualitätsabschnitte,
Windows-Payload-/Updatevertrag und Werkzeuganleitung. Prüfbedarf, konkrete
Einführungsnachweise und offene Gates stehen ausschließlich im Issue/Paket.

Der lokale Empfänger prüft pro Durchlauf höchstens 1024 Verzeichniseinträge und 32 mögliche Manifeste. Bei Überschreitung bleibt die Lieferung zur Klärung stehen.
