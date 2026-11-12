# Motivbezogene Ansichtsübergabe · #596/B

Maßgeblich ist die [Paketentscheidung B](https://github.com/venomenon328/picross/issues/596#issuecomment-6821266401).
Der Verweis bezeichnet die aktuell zu öffnende **Ansicht**, keine Bild-/Rasterwahl
und keine Freigabe. Mehrere Rasterangebote bleiben gleichberechtigt.

## Geschlossene Form und Veröffentlichung

`content/authoring/<puzzle_id>/current-view.json` enthält exakt
`format,puzzle_id,revision,record,projection`, Format
`picross-production-current-view-v1`. Beide Dateireferenzen enthalten exakt
`file,sha256,bytes`: kanonischer Record-/workspace-Pfad derselben ID/Revision,
64 kleine Hexzeichen, positive tatsächliche Bytezahl. ID und Revision folgen
den vorhandenen Authoringregeln, auch nichtnumerische Revisionen. Kanonisches
JSON mit UTF-8/LF, maximal 4096 Bytes. Keine Commit-Selbstbindung, Zeitstempel,
Angebote oder Autoritätsfelder; Index v1 und die versiegelten Formen bleiben gleich.

Builder v3, Finalizer v2, Projektor v2 und `projector.complete()` führen denselben
[Übergabepublisher](../tools/production_workspace/current_view.py) unter dem
gemeinsamen Authoringwriter aus. Erst vollständige indexierte Originale und
fachlich geprüfte Projektion, dann erneute Quellenprüfung und atomare Publikation
des Pointers. Identische Wiederholung erhält Bytes und mtime. Eine konkurrierende
Pointer-/Quellenänderung stoppt; unbekannte alte Bytes werden nicht repariert.
Finalizer und Completion dürfen ausschließlich ihre nachgewiesenen Vorherbytes
zur Wiederaufnahme einer unterbrochenen In-place-Fortschreibung verwenden.
Ein Fehler nach Record-/Projektionswechsel ist kein erfolgreiches Handoff.
Identischen Aufruf vollständig wiederholen, Zwischenstände nicht committen.

Bereits vollständige 0.8-Arbeit kann der beauftragte Akteur gezielt veröffentlichen:

```text
python -m tools.production_workspace.projector --repository <checkout> --current-view <pz-ID> <revision>
```

Vorhandener Pointer, Indexmitgliedschaft, Record, Projektion und Originale werden
frisch geprüft. Keine freie Pfad-/Ref-API und kein HTTP-Writer. Sämtliche nötigen
Originale, Index, Record, Projektion **und Pointer** gemeinsam committen/pushen;
Remotezugriff am festen Commit prüfen. Auch eine Korrektur in früherer Phase darf
so ausdrücklich zur aktuellen Ansicht werden. Ein Builder-No-op ist nur dann
eine neue Übergabe, wenn der Akteur genau diese Revision erneut übergeben will.

## Lesen und Quellenrelation

Die Hauptauswahl gruppiert nach ID. Die Versionsansicht trennt Phase/Revision,
Herkunft und Aktualität. Bytegleiche Record-/Projektionsbindungen erscheinen einmal
mit allen konkreten Quellen. Titelgleiche IDs bleiben unterscheidbar. Die konkrete
geöffnete Quelle bindet alle Details, Bilder und Folgeaufträge.

Die Liste prüft Pointerform, Index, Record-/Projektionsbytes und deren gegenseitige
Bindung aus festen Gitcommits. Pakete/Bilder werden erst beim Öffnen mit den
bestehenden fachlichen Kreuzprüfungen gelesen; kein Vorabentpacken aller ZIPs.
Fehlende/defekte Pointer bleiben sichtbar, gültige Revisionen einzeln aufrufbar.
Diese Implementierung nutzt **keinen geratenen Altfallback**: ohne eindeutig
geprüften Ansichtsbezug bewusste Versionswahl oder gezielte nächste Übergabe.
Keine Alt-WIP-Konvertierung.

Gitrelation verwendet echte Commit-Eltern aus lokalen Objekten und privatem Cache.
Bei fehlenden flachen Metadaten höchstens zwei gezielte Fetches ausgewählter
Remotespitzen mit `depth=64,blob:none` je Listenlauf; höchstens 256 Commitheader
je Abstammungsrichtung. Fehlende Historie bleibt ungeklärt. Keine allgemeine
Historien-/Blobsuche, keine Fetchmutation im Benutzercheckout.
Der Lokal-/Remote-Status vergleicht jeweils denselben Ref; verschiedene Main-/
Produktionsstände sind für sich kein Synchronisationskonflikt. `Synchron` verlangt
gleiche frisch bestätigte Quellenstände aller vertretenen Refs; fehlt ein Gegenstück,
bleibt der Gesamtvergleich unbestätigt. `Lokal neuer` und `Remote neuer` verlangen
bewiesene Abstammung desselben Refs. Divergenz und unterschiedliche Bytes derselben
ID/Revision erfinden keinen Sieger. Offline-/Authentifizierungsfehler behalten
Cacheansichten lesbar und zeigen `Remote nicht aktuell bestätigt` samt letzter
Cachezeit/Fehler. Cachezeit ist keine frische Remoteprüfung. Unbestätigte lokale
oder veraltete Quellen ergeben keinen Cloudfolgeauftrag.

Passive Suche bietet einen Listenwechsel an; aktive Ansicht, Bilder und Absichten
bleiben gebunden. Erst ausdrückliches Laden, Motiv-/Versions-/Quellwechsel verwirft
alte Absichten. Alte Antworten werden generationgebunden ignoriert. Eine automatisch
geöffnete Remoteansicht erlaubt noch keine P2-Entfernung: erst konkrete Remotequelle
ausdrücklich wählen, dann die unveränderten frischen P2-Schutzprüfungen/Bestätigung.

## Abschluss und Prüfgrenzen

Nach bestätigter Endabnahme und Mainintegration entfernt der Produktionsakteur den
abgeschlossenen Ansichtsverweis **vor** dem vorhandenen `retire-production`-Aufruf:
Pointer und Mainbeleg frisch prüfen, nur den zur abgeschlossenen Revision gehörenden
Pointer entfernen. Ein Verweis auf neuere/offene Arbeit bleibt erhalten und verlangt
zuerst Klärung. Der bestehende Retirementguard weist unbekannte Dateien weiterhin
ab. Kein neuer Katalogwriter oder Transaktionspfad; keine vorgezogene Bereinigung.

Kleine synthetische Regressionen liegen in `tools` und `production.adapter`.
Die Paketentscheidung verlangt zusätzlich reale synthetische Gitintegration und
eine getrennte interaktive Desktop-/Schmalfenster-/Offline-/Refreshprobe. Deren
tatsächlicher Stand und unabhängiges Review stehen am konkreten B-PR-Head.
HTTP-/Node-Controllerprüfungen ersetzen keine Browserdarstellung. Keine automatische
Chromium-CI, keine zusätzlichen allgemeinen Bild- oder Produktionsfreigaben.
