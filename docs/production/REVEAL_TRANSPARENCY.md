# Technischer Vertrag für Abschlussbilder

Dokument-ID: `reveal-technical`
Status: `active`
Stand: 17.11.2026 · DOCS-696 / [#696](https://github.com/venomenon328/picross/issues/696)

## 1. Zuständigkeit und aktueller Weg

- Gestaltung, Motivschutz und Transparenzbildstandard: ausschließlich [REVEAL](images/REVEAL.md).
- Bildsichtung und Einzelurteile: [Qualität §3.1](PUZZLE_QUALITY.md#31-abschlussbildphase).
- Produktion, Auswahl, Revision und Abschluss: [Authoring](authoring/PUZZLE_AUTHORING.md).
- Aktuelle Integration/Quellen/Recovery: [RI](PUZZLE_INTEGRATION.md) und [ZA-1](ZA1_ADAPTER.md).
- Gezielter Bildwechsel und aktuelle Editorformen: [PE §13](../tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).

Dieser Vertrag ergänzt die Bildnorm um Alpha-Erhalt, Bildquellen und
Änderungsinvarianten. Er definiert weder einen zweiten Integrationsweg noch
neue Bildabnahmen. Historische Einführungspakete sind keine aktuellen Aufträge.

## 2. Verbindlicher Bildstandard

Die gestalterischen Anforderungen stehen vollständig in
[REVEAL RV-01–RV-05](images/REVEAL.md). Die technische Kette MUSS
Alpha vom tatsächlich freigegebenen PNG beziehungsweise zulässigen bestehenden
SVG über Export, Integration, Import und Darstellung erhalten. Keine JPEG- oder
deckende Zwischenstufe, keine Runtimefreistellung und kein globaler Weiß-/Farbfilter.

Katalog und Abschluss verwenden dieselbe aktuelle Bilddatei, lediglich in
unterschiedlichen Anzeigegrößen. Bestehende proportionale Darstellung und
lokale Lanczos-/Linear-Glättung bleiben abgeleitete Anzeige; sie verändern die
Originalbytes nicht. Ressourcenlimits und erlaubte PNG-/SVG-Formen stehen im
zuständigen aktuellen Import-/Editorvertrag.

Neue/begonnene Rätsel zeigen nur zulässige eigene Spielerdaten. Keine vorzeitige
Revealvorschau und kein neues Preload. Fragezeichen, eigene Füllminiatur,
Spoiler-/Recoverygrenzen und der bestehende Abschlussübergang bleiben erhalten.
Der Papieruntergrund wird nicht durch eine neue Ersatzfläche überdeckt.

## 3. Reine Bildrevision: Identität und historische Bindungen

Eine reine Bildrevision ersetzt das freigegebene Abschlussbild und die dafür
benötigte aktuelle Bildbindung. Sie ist kein Rasterupdate.

| Bereich | Invariante |
| --- | --- |
| Rätsel | Definitions-/Rasteridentität, Matrix, Hinweise, Palette und Runtime-Rasterrevision bleiben erhalten. Kein neuer Solver-, Proof- oder Difficultylauf allein wegen der Bildänderung. |
| Auffindbarkeit | ID, Schlüssel, Save-Slot, Kategorie, Sichtbarkeit und Katalogslot bleiben erhalten. Den aktiven Ressourcenpfad über den aktuellen Writer auflösen; erlaubter PNG↔SVG-Wechsel folgt PE. |
| Fortschritt | Saves, Redo, Abschlusszustand und Recent-Marker bleiben gültig; kein Reset, keine Migration und keine Rückstufung. |
| Metadaten | Schwierigkeit, Rating-/Added-Daten und ihre Bindungen bleiben erhalten; ein neues Bild ist keine neue Katalogaufnahme. |
| Tatsächliche Entscheidungen | Aktuelle Bildwahl und benötigte Nutzungsgrundlagen bleiben konkret an die gewählten Bytes gebunden. Tatsächlich vorhandene alte Belege nicht auf einen neuen Bildhash umschreiben; ihre Aufbewahrung oder Rekonstruktion ist keine Voraussetzung der aktuellen Produktion. |
| Neue Bildfassung | Neue Bild-/Recordrevision mit tatsächlicher Entscheidung und aktueller Identitäts-/Bytebindung. Herkunft, Rechte und tatsächlich nötige Notices erhalten. |

Der aktuelle Editor prüft die ausgewählten neuen Bildbytes und die relevanten
aktuellen Bindungen gemäß PE §13. Die ausdrückliche Eigentümerauswahl erzeugt
keine neue Herkunftsnotice und keine fingierte Produktionsfreigabe; vorhandene
echte Rechte-/Lizenzinformationen bleiben erhalten. Technische Validierung
ersetzt keine Motivbeurteilung.

Eine gemeinsame Freigabe mehrerer Bilder ist zulässig, wenn jede ID, Datei,
Bildrevision und jeder Hash eindeutig bezeichnet ist. Eine Spezifikation,
Vorschau ohne Dateibindung oder frühere Auswahl ist keine Freigabe neuer Bytes.
Änderungen erneuern nur die tatsächlich abhängigen Belege nach Authoring.

## 4. Gemeinsamer technischer Vertrag

Erstregistrierung verwendet den aktuellen `picross-integration-input-v1` nach
RI/ZA-1. Aktuelle Quellen binden Identität und Livebytes; Produktionsarchive,
Producer- oder Regelbuch-Allowlisten sind keine neue Integrationsvoraussetzung.
Raster-, Reveal-, Hintergrund- und Metadatenpflege bleiben getrennte Operationen.

Zulässige vorbereitete PNGs und begrenzte lokale SVGs werden bytegleich importiert;
variable Maße und Seitenverhältnisse sind erlaubt. PNG↔SVG wechselt den
verwalteten technischen Pfad samt Source/Notice/Runtime und entfernt nur die
eigene verdrängte Live-Datei im gemeinsamen Journal. Bestehende ursprüngliche
Produktions-/Definitionsbelege dürfen keine neue Aufbewahrungspflicht begründen;
der aktuelle Stand folgt [PW-B](../tools/PW_B_CONTRACT.md).

Recovery prüft die tatsächlich zuständige Journalgeneration und alle gebundenen
Zielbytes, bevor eigene Daten entfernt werden. Ein aktueller Bildplan hängt nicht
von einem früheren Produktionspaket ab. Fehlende bereinigte Arbeitsdateien
rechtfertigen keine Rekonstruktion abgeschlossener Produktion.

## 5. Weiterhin gebundene Altformen

Historische Bedeutung tatsächlich vorliegender älterer Belege. Diese Formen
sind keine zusätzlichen aktuellen Reader-/Writer-/Recoveryeingänge und werden
nicht in neue Generationen umetikettiert.

- Reveal v3: exakt `format,id,record_revision,origin,binding,current,record_hash`. Unterformen, Zähler, Grenzen und manuelles Notice-Layout: [PE §8.1–8.2](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_EDITOR.md#81-gemeinsame-typen-und-aktive-quellen).
- `origin`: unveränderlicher nichtrekursiver alter Reveal-v1/v2-Record oder gültiger sourcefreier Produktionsanker. Aktuelle äußere `binding` und Darstellungsentscheidung bleiben getrennt.
- Reguläre historische AT-Adoption: Revealrequest v2, Revealplan v5, Revealjournal v6 nach [SD_CATALOG](https://github.com/venomenon328/picross/blob/62401382f58adc2e3d303b19c1ecb1f1dc8a5040/docs/SD_CATALOG.md#pe-a2--geschlossene-v8-quellen-pläne-und-journale), mit tatsächlicher `picross-reveal-approval-v1`.
- `authority={kind,approval,binding}` mit `kind=production` erhält den tatsächlichen Adoptionstand. Ein späterer Raster-Rebind verändert die äußere Bindung, keine Bildrevision oder ursprünglichen Entscheidungsbytes.
- Vollständige historische Prüfung validiert die dort gebundene Definition und Originale nach ihrem eigenen Format. Das ist keine Pflichtrekonstruktion für die aktuelle gezielte Bildpflege.

## 6. Einführungshistorie

AT-A/AT-B, die damaligen synthetischen Nachweisinventare und späteren
HP-I1c-/PW-PERF-Ergänzungen sind am
[Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/REVEAL_TRANSPARENCY.md)
abrufbar. Die mehrfach identischen RI-ONE-Fortschreibungen sind in §1/§4
zusammengeführt. Laufende Aufträge und tatsächliche Abnahmen stehen im jeweiligen
Issue/PR; historische Gates werden durch diesen Verweis nicht erneut eröffnet.
