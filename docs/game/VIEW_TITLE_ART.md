# BTI · Bildhaupttitel der Buchansichten

## Geltung und Zuständigkeit

Dieser Vertrag besitzt UI-Rollen, Original-/Manifestbindung, Import, optischen
Fit und geschützte Anordnung der Titelbilder. Der Produktionsstil steht allein
im [Titelstilbrief](../production/images/TITLES.md). Regeln im aktuellen Git-Stand
sind der Fachvertrag; tatsächliche Integration, Review und persönliche Sicht
stehen im zuständigen Issue/PR.

## BTI-D01 · Rolle und exakte Texte

| Buchansicht | Einziger betroffener großer Seitentitel | Platz |
| --- | --- | --- |
| Katalog | **Rätselkatalog** | Kopf der linken aufgeschlagenen Buchhälfte |
| Hilfe | **Hilfe** | Kopf der rechten Informationsbuchseite; ersetzt nur den bisher sichtbaren Haupttitel „Spielerhilfe“ |
| Einstellungen | **Einstellungen** | Kopf der linken Informationsbuchseite |

Alle drei werden **als lokal gebündelte, generativ hergestellte transparente Schriftzugbilder** dargestellt, nicht als zur Laufzeit mit einem Font gesetzter Schriftzug. Keine KI-Anfrage im Spieler und keine Abhängigkeit von einem externen Dienst. Der exakte Text wird als semantischer UI-/Accessibilityname und bei fehlender Bildressource als gut lesbarer Textfallback vorgehalten; keine doppelte sichtbare Beschriftung im Normalfall. Für die Hilfe darf der interne funktionale Begriff „Spielerhilfe“ bleiben; ausschließlich die große sichtbare Überschrift lautet „Hilfe“.

Diese drei Bildrollen ersetzen ausschließlich die jeweiligen sichtbaren
Haupttitel. Die bisherigen Textlabels bleiben Ressourcenfallbacks. Alle anderen
Schriftrollen stehen in [HAND_DRAWN_UI](HAND_DRAWN_UI.md); keine zusätzliche
allgemeine Schriftoption.

## BTI-D02 · Die freigegebene Zeichenhand

Die aktive Familie ist BTI-B-V2-rev1. Lettering, Graphitfarbe, Schraffur,
buchstabengebundene f-/g-Züge, natürliche Wortproportionen und Transparenz sind
im [Titelstilbrief](../production/images/TITLES.md) festgelegt. Die drei gebundenen
Originale werden für ihre Runtimeintegration unverändert verwendet.

## BTI-D03 · Originalbindung und Import

Genau drei verlustfreie RGBA-PNGs unter `game/art/drawing/view_titles/`:
`catalog.png`, `help.png`, `settings.png`. Das
[Manifest](../../game/art/drawing/view_titles/manifest.json) ist die exakte Quelle
für Dateinamen, Maße, Bytezahlen, SHA-256, Quellcommit und Alpha-/optische Hüllen.
[Provenienz](../../game/art/drawing/view_titles/provenance.json) und
[NOTICE](../../game/art/drawing/view_titles/NOTICE.txt) bleiben unveränderte
Herstellungs-/Herkunftsbelege. Keine nachträgliche Freistellung, Beschneidung,
Neufärbung, Alphaersetzung oder Neucodierung der freigegebenen finalen Bytes.

Optische Hüllen bei Alpha ≥16 bestimmen die Zentrierung; Endkoordinaten sind
exklusiv. Die vollständige PNG-Fläche einschließlich schwacher Alpha-1-Reste
wird proportional um diesen Mittelpunkt mit vier Pixeln Reserve eingepasst.
Keine abgeschnittenen ä-/i-Punkte oder f-/g-Enden; Hilfe wird nicht auf
Langwortbreite gestreckt. Verlustfreier Godot-Import mit Mipmaps, Alpha und
lokalem linearem Sampling. Windows/Web liefern aktive Titel und Herkunft offline.
Statische 42-/96-px-Studienkörper sind keine Runtime-Endmaße.

## BTI-D04 · Geschützte Buch-/UI-Anordnung

**Katalog:** Der Titel ist im aus Papierhöhe bestimmten Kopfbereich der sicheren
projizierten linken Papierhälfte horizontal zentriert. Weder fensterweite
Zentrierung noch Lage über dem Falz. Rechte Zusammenfassung, Filter-, Scroll-
und Kartenflächen bleiben frei. Die gemeinsame `title`-Textrolle für Arbeitsblätter
wird nicht entfernt oder versehentlich zum Bildtitel gemacht.

**Hilfe/Einstellungen:** Zentrierter Bildtitel und NAV-A-Kopfgruppe liegen an
derselben oberen Papierkante außerhalb der unabhängigen Inhalts-Scrollfläche.
Die Gruppe erzeugt keine zusätzliche Höhenzeile. Das vollständige Titelbild
bleibt seitlich von Trefferflächen getrennt. Navigation, Besuchsursprung,
Kapitelregister und Scrollkontexte folgen BOOK_INTEGRATION; Einstellungsgruppen
folgen DISPLAY_SETTINGS. Interne Hilfe-Bezeichnungen dürfen „Spielerhilfe“ heißen,
aber nur der Haupttitel zeigt „Hilfe“; übrige Überschriften bleiben Textlabels.

**Priorität bei engem Platz:** echte Papiergrenze, erreichbare Navigation und
Status-/Fehlermeldungen vor dekorativer Größe. Titel proportional verkleinern
und Scrollraum begrenzen; keine abgeschnittenen Konturen, versteckten Controls
oder Inhalte über dem Falz. Resize, UI100→125→100, Kamera-/Blattcapture, Fokus
und Ladefehler erhalten diese Anordnung. Unterstützte Flächen und Komfortgrenzen
stehen in DISPLAY_SETTINGS/VS1_DECISION. Zusätzliche Fläche bläht Titel nicht
willkürlich auf.

## BTI-D05 · Lieferung und Abnahmegrenzen

BTI-C-A01–A08, T01/R01/M01 und konkrete Original-/Windowsbelege stehen in
[Issue #533](https://github.com/venomenon328/picross/issues/533). Aktueller
Prüfbedarf folgt [CI_WORKFLOW_V2](../ci/CI_WORKFLOW_V2.md) und dem
[nativen Modulvertrag](../ci/CI_C_NATIVE_GROUPS.md). Quellen-/Importprüfung,
tatsächliche Buchbedienung und persönliche Wirkung der Originale sind getrennte
Nachweise. Frühere Stilfreigabe ist keine Abnahme eines späteren Produkt-Heads.

## Herkunft und Nachweise

Fachentscheidungen und tatsächliche Review-/Abnahmeergebnisse: [#533](https://github.com/venomenon328/picross/issues/533) und [PR #534](https://github.com/venomenon328/picross/pull/534).
Der [historische Dokumentstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/VIEW_TITLE_ART.md)
erhält frühere Lieferchronologie und ersetzte Regeln. Er ist keine zusätzliche
Normquelle oder dauerhafte Prüfpflicht. Aktuelle Prüfungen folgen dem
[Paketvertrag](../ci/CI_WORKFLOW_V2.md) und dem jeweils betroffenen Modul.
