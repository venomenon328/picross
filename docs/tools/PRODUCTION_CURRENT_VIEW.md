# Motivbezogene Ansichtsübergabe

## Geltung und Quellen

- **Status:** aktiver Vertrag für `current-view.json`, Quellenauswahl und ansichtsbezogenen Abschluss.
- **Oberfläche und Remoteauswahl:** [PW](PRODUCTION_WORKSPACE.md) und [PW3-A](https://github.com/venomenon328/picross/issues/646#issuecomment-6882941268).
- **Authoringformen:** [PW-B](PW_B_CONTRACT.md); aktuelle Inhaltsformen und Completion nach [RI](../production/PUZZLE_INTEGRATION.md).
- **Historie:** die frühere lokale/entfernte Gleichstellung aus [#596/B](https://github.com/venomenon328/picross/issues/596#issuecomment-6821266401) ist durch PW3-A ersetzt.

Der Verweis bezeichnet die aktuell zu öffnende Ansicht, keine Bild-/Rasterwahl
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

Builder, Finalizer, Projektor und `projector.complete()` führen denselben
[Übergabepublisher](../../tools/production_workspace/current_view.py) unter dem
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

Im konfigurierten Remotebetrieb gilt [PW3-A](https://github.com/venomenon328/picross/issues/646#issuecomment-6882941268):
Nur ausgewählte Remotequellen bilden die aktive Auswahl. Die gültige aktuelle
Ansicht am tatsächlichen Tip von `content/pw/<puzzle_id>` führt vor main, auch
bei unabhängigen Historien, einer früheren Korrekturphase oder nichtnumerischen
Revisionen. Ohne offenen Produktionsbranch bleibt offene Mainarbeit sichtbar.
Ein fehlender/defekter Pointer des offenen Produktionsbranches verlangt gezielte
Remoteversionswahl; main oder lokale Dateien sind kein geratener Ersatz.
Versions-/Quelldetails bleiben untergeordnet. Lokale Refs werden für P2 oder
gezielte Diagnose gelesen; lokale Fortschritte erzeugen keine Alternativen und
keinen Auswahlkonflikt. Es braucht keine Abstammungssuche für diesen Remoteeinstieg.

Bewusst eingerichteter lokaler Diagnosebetrieb bleibt lokal und unverändert
konfiguriert. Seine Gitrelation verwendet echte Commit-Eltern aus lokalen
Objekten mit höchstens 256 Headern je Richtung; fehlende Historie bleibt ungeklärt.
Keine allgemeine Historien-/Blobsuche oder Fetchmutation im Benutzercheckout.
Offline-/Authentifizierungsfehler behalten ausschließlich den letzten gebundenen
Remotecache lesbar und zeigen `Remote nicht aktuell bestätigt` samt letzter
Cachezeit/Fehler. Cachezeit ist keine frische Remoteprüfung. Unbestätigte lokale
oder veraltete Quellen ergeben keinen Cloudfolgeauftrag.

Passive Suche bietet einen Listenwechsel an; aktive Ansicht, Bilder und Absichten
bleiben gebunden. Erst ausdrückliches Laden, Motiv-/Versions-/Quellwechsel verwirft
alte Absichten. Alte Antworten werden generationgebunden ignoriert. Eine automatisch
geöffnete Remoteansicht erlaubt noch keine P2-Entfernung: erst konkrete Remotequelle
ausdrücklich wählen, dann die unveränderten frischen P2-Schutzprüfungen/Bestätigung.

## Abschluss und Prüfgrenzen

Die aktive Auswahl folgt zusätzlich dem
[PW2-C-Liefervergleich](PRODUCTION_WORKSPACE.md#pw2-c--aktive-lieferungen-und-bestätigter-abschluss).
Vor der Motivgruppierung werden ausschließlich konkrete, an einem frisch
bestätigten konfigurierten Remote-`main` vollständig belegte Lieferungen und ihre
eindeutig zugeordneten alten Quellen ausgeblendet. Dies gilt vor und nach
Retirement, auch bei Squash oder unveränderter Sammelübernahme. Gleichheit der ID
oder des ursprünglichen Exportbezugs allein verdeckt keine neue Revision oder
spätere Raster-/Reveal-/Hintergrundarbeit. Ein widersprüchlicher Ansichtsverweis,
abweichende Bytes oder fehlende Lieferbelege halten die betroffene Quelle sichtbar.
Ohne frischen Mainbezug entsteht keine neue Abschlussannahme. Die Entscheidung
wird auch bei unverändertem Produktionscommit nach Mainwechsel neu ausgewertet.

Passive Suche übernimmt diesen Listenwechsel noch nicht. Erst das ausdrückliche
Laden meldet den belegten Entfall und öffnet verbleibende Arbeit derselben ID,
eine andere offene Produktion oder eine verständlich leere aktive Liste. Gespeicherte
Motivtexte bleiben sekundär ausdrücklich erreichbar und öffnen bei leerer Liste
oder Appstart niemals automatisch. Neue ungesendete Eingaben überleben passive
Suche; Kopieren erklärt weder Absenden noch Freigabe. Der Leser verändert weder
Pointer noch Quellen. Er vergleicht die aktuelle Lieferung aus Registry v5,
Reveal v5, Hintergrund v7, Runtime v8 und den tatsächlichen Livebytes gemäß
[RI](../production/PUZZLE_INTEGRATION.md). Historische Export-/Receipt-/O/R-Anker sind keine
Abschlussvoraussetzung. Frühere Phasen werden nur durch ihre konkreten
bytegleichen Record-/Projektionsbindungen zu einer bestätigten abgeschlossenen
Lieferung zugeordnet. Eine ausdrücklich aktuell ausgewählte frühere Phase gilt
als wiederaufgenommene offene Arbeit. Die Auswertung verarbeitet die vollständige
ausgewählte Liste ohne 32er-Gesamtgrenze; `completion.unresolved` benennt fehlende
oder widersprüchliche Belege als Ansichtsdaten.

Registrierte Ansichten werden über aktuelle Definition, Registry, Runtime und
Livebytes bestätigt. `projector.complete()` erhält den finalen aktuellen Input
explizit per `--input`; historische Produktionsarchive sind keine
Abschlussvoraussetzung. Die Main- und Wiederaufnahmegrenzen folgen
[PW2-C](PRODUCTION_WORKSPACE.md#pw2-c--aktive-lieferungen-und-bestätigter-abschluss).

Nach bestätigter Endabnahme und Mainintegration prüft `retire-production` die
aktuelle Lieferung und die ausdrücklich ausgewählten abgeschlossenen Arbeitsdaten.
Es entfernt den Ansichtsverweis nur, wenn seine unveränderten gebundenen Bytes
exakt auf eine ausgewählte abgeschlossene Revision zeigen. Ein Verweis auf
neuere/offene Arbeit bleibt erhalten. Unbekannte Dateien und fremde Änderungen
blockieren die Bereinigung; keine vorgezogene Entfernung und kein neuer Writer.
Der vollständige Abschlussweg steht in [Authoring Schritt 5 §9](../production/authoring/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung).

## Prüf- und Lieferhistorie

Kleine synthetische Regressionen liegen in `tools` und `production.adapter`;
die konkrete Prüfauswahl folgt dem aktuellen CI-Vertrag. Die einmaligen
Gitintegrations-, Desktop-, Schmalfenster-, Offline- und Refreshproben sowie
unabhängige Reviews sind am jeweiligen Produkt-Head in
[Issue #596](https://github.com/venomenon328/picross/issues/596) beziehungsweise
[PW3-A / #646](https://github.com/venomenon328/picross/issues/646) gebunden.
HTTP-/Node-Controllerprüfungen ersetzen keine Browserdarstellung. Diese
Lieferhistorie begründet keine zusätzliche allgemeine Bild- oder Produktionsfreigabe.
