# HG-BESTAND-01 · Qualle

Phase: **background_review**, eigene Hintergrundarbeit für die bestehende Rätsel-ID `pz-20ecf7747bbf40828238ec26d1207172`. Keine neue Rätselproduktion oder Authoring-Recordrevision; kein Eintrag im regulären fünfstufigen Authoringindex.

- Branch: `content/hg-bestand-01`
- Feste Produktions-/Regelquelle: `5f620228958e58c7f98fc6c9823ea970f3cb1764`
- Bestehende Kategorie: `wasserwelt`
- Aktuelles Reveal: `game/art/content/qualle_001.png`, SHA-256 `91a20121593a44b0f7c41c2db6a1025a62f3c89f9c40927f2cb52ceb8513e29d`, Bildrevision 1
- Aktuelles Angebotsmanifest: [work/bg-offer-r03.json](work/bg-offer-r03.json) (`picross-background-work-v1`, Manifestrevision bg03)
- Quellen, Zuordnung und geschützte Werte: [evidence/source-bindings.json](evidence/source-bindings.json)
- Einzelurteile: im Angebotsmanifest an Kandidat/Dateirevision und Normhash gebunden
- PNG-/Formatprüfungen: [evidence/png-inspection.json](evidence/png-inspection.json)
- Originalabruf: [evidence/remote-readback.json](evidence/remote-readback.json)
- Korrekturen/Budget: [evidence/revision-history.txt](evidence/revision-history.txt)

## Zur Auswahl

| Kennung | Bildrevision | Kontext | Einzelbild |
| --- | --- | --- | --- |
| Q1 | r04 | Sandgrund mit Muscheln | [PNG groß öffnen](https://raw.githubusercontent.com/venomenon328/picross/19cb1a7687305671af260252b68ae7c66e3b6dcd/content/authoring/pz-20ecf7747bbf40828238ec26d1207172/hg-bestand-01/candidates/Q1-r04.png) |
| Q2 | r02 | Kelpwald mit kleinen Fischen | [PNG groß öffnen](https://raw.githubusercontent.com/venomenon328/picross/19cb1a7687305671af260252b68ae7c66e3b6dcd/content/authoring/pz-20ecf7747bbf40828238ec26d1207172/hg-bestand-01/candidates/Q2-r02.png) |
| Q3 | r02 | Felsküste mit Gezeitenbecken | [PNG groß öffnen](https://raw.githubusercontent.com/venomenon328/picross/19cb1a7687305671af260252b68ae7c66e3b6dcd/content/authoring/pz-20ecf7747bbf40828238ec26d1207172/hg-bestand-01/candidates/Q3-r02.png) |

Alle angebotenen Bilder sind 2896×724 RGBA-PNGs mit echter Außen-/Zwischenraumtransparenz. Die initialen 2172×724-Rohbilder wurden vollständig und pixelgleich auf einer 4:1-Leinwand unten mittig mit 362 transparenten Pixeln je Seite platziert. Keine Zeichnung, bewusst leerer Bereich oder Alphakante wurde beschnitten, skaliert oder individuell verschoben. Q-HG01–04 sind an den Auswahlfassungen erfüllt.

Q1-r01/r02 zeigen einen dokumentierten Transparenzmangel und sind **keine Auswahlfassungen**. Eine gezielte native ImageGen-Korrektur lieferte Q1-r03; Q1-r04 ist deren pixelgleich gepaddete Auswahlfassung. Die übrigen beiden Angebote sind Q2-r02 und Q3-r02.

`work/bg-raw-r01.json` und `work/bg-format-r02.json` erhalten Vorstufen/negative Urteile; sie bleiben pending und werden nicht als gültige Auswahl angeboten. Alle Rohoriginale sind unverändert vorhanden.

## Offene Entscheidung und Fortsetzung

Der Eigentümer wählt genau eine angebotene Kennung/Dateirevision oder erklärt gezielte Korrektur beziehungsweise ausdrücklich none. Es liegt noch keine Hintergrundentscheidung vor. Kein HP-W2 describe/derive/verify, Editorplan/import, Spieleinbau oder Merge wurde ausgeführt.

Nach echter Wahl nur das gewählte Bild in einer getrennten externen Arbeitskopie mit unveränderten relativen Pfaden über den bestehenden HP-W2-v2-Weg ableiten. Die spätere Integration benötigt ihren tatsächlichen Auftrag. Die ursprüngliche Bestandseinbindung wird nicht erneut abgenommen und keine historische Bildwahl rekonstruiert.

Dieser Ordner ist die ausdrücklich gesicherte eigenständige Zusatzarbeit `hg-bestand-01` im Sinn von `--completed-work`. Abschluss/Retirement erst nach bestätigter Mainintegration. Bis dahin Originale, Alternativen und Belege erhalten; keine dauerhafte Galerie.

Kein neuer PR im Kandidatenschritt: der gemeinsame Integrations-PR folgt erst im beauftragten späteren Integrationsschritt. Daher noch kein neuer CI-Paketplan oder Playerbau; die einmaligen Bild-/Dateiprüfungen stehen oben. Benutzercheckout nicht umgeschaltet oder bereinigt; eigene lokale Arbeitsablage bleibt für die Auswahl/Wiederaufnahme erhalten.
