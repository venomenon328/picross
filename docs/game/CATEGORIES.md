# Kategorien und Zuordnung

Dokument-ID: `categories`
Status: `active`
Zuständigkeit: Kategorienquelle, Kategorie-ID, Anzeigename, Reihenfolge und
fachliche Zuordnung. Geschlossene Registry-, Transaktions- und Bildformen
stehen in [RI](../production/PUZZLE_INTEGRATION.md), Runtimeprojektion und ihre
Spieler-Lesekompatibilität in [RI-ONE §2.1–2.2](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md#21-geschlossene-aktuelle-runtimeprojektion), Editoraktionen in
[PE §13](../tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung).

## 1. Fachliche Bedeutung

Kategorien gruppieren Motive. Sie sind weder Kapitel noch Schwierigkeit oder
Freischaltbedingung. Alle sichtbaren registrierten Rätsel bleiben spielbar.
Ausgewogene Mengen sind ein Planungsziel ohne Quote.

Der prägende Hauptgegenstand bestimmt genau eine Kategorie; Nebenobjekte erzeugen
keine zusätzliche Zuordnung. Die Gruppen bilden keine biologische Taxonomie oder
Essbarkeitsaussage. Keine automatische Ableitung aus Dateiname, Motivname, ID,
Bild oder Schwierigkeit; keine Auffangkategorie, Tags oder Unterkategorien.

## 2. Geschlossene Kategorienquelle

Einzige autoritative Quelle ist [content/categories.json](../../content/categories.json).
Der Writer/Reader verwendet `picross-categories-v1`.

| Gegenstand | Vertrag |
| --- | --- |
| Wurzel | Exakt `format,categories`; format ist `picross-categories-v1`. |
| Kategorie | Exakt `id,name,order`. |
| `id` | ASCII `[a-z][a-z0-9-]{0,63}`, eindeutig und dauerhaft stabil. |
| `name` | 1…128 Zeichen, ohne Randwhitespace oder C0/C1-Steuerzeichen. |
| `order` | Eindeutige Ganzzahl 1…10000; Boolean ist keine Ganzzahl. Projektion sortiert danach. |
| Grenzen | Höchstens 256 Kategorien und 131072 UTF-8-Dateibytes. |
| Leere Liste | Nur zulässig, wenn keine Inhalte eine Kategorie referenzieren. |
| Fehler | Unbekannte Formate/Felder, doppelte JSON-Schlüssel, IDs oder Reihenfolgen sowie nichtendliche Zahlen werden zurückgewiesen. |

## 3. Aktuelle Zuordnung und Pflege

Jede registrierte Rätsel-ID verweist unabhängig von Sichtbarkeit auf genau eine
vorhandene Kategorie. Aktueller Motivname und Kategoriezuordnung werden aus der
aktuellen Inhaltsautorität aufgelöst. Historische Produktionsangaben werden bei
Pflege nicht rückwirkend geändert und überschreiben keine aktuelle Zuordnung.

Umbenennen erhält Kategorie-ID, Rätsel-ID, Key, Save-Slot und Rasterrevision.
Neue Kategorie-IDs werden einmalig kollisionsfrei angelegt. Bestehende `order`-
Werte bleiben erhalten; der Editor hängt neue Kategorien an. Erschöpfte Grenzen
sind Fehler. Die Oberfläche bietet keine Sortierungsverwaltung der Kategorien.

Löschen ist nur bei einer leeren Kategorie oder zusammen mit ausdrücklicher
Neuzuordnung aller betroffenen Rätsel zulässig. Neuzuordnung und Löschung bilden
einen gemeinsamen Speichervorgang. Die Ursprungskategorie eines historischen
Produktionsbelegs muss anschließend nicht mehr im aktuellen Katalog existieren.

Standardhintergründe folgen der aktuellen Kategorie. Ein eigenes Hintergrundbild
oder ausdrücklich kein Hintergrund behalten ihre Auswahl beim Kategoriewechsel;
die drei Zustände definiert [PE §4.2](../tools/PUZZLE_EDITOR.md#42-drei-verständliche-hintergrundzustände).
Eine vorhandene defekte Quelle ist ein Fehler, kein stiller Fallback.

## 4. Produktion und Projektion

Ein offenes Motivbriefing darf `category_id=null` führen; vor Integration ist die
explizite gültige Zuordnung Pflicht. Arbeitsindex und Authoring-Record sind keine
Katalogregistrierung. Fortsetzen und Abschluss folgen [Authoring](../production/authoring/PUZZLE_AUTHORING.md).

Die aktuelle Übergabe folgt [ZA-1](../production/ZA1_ADAPTER.md) und [RI](../production/PUZZLE_INTEGRATION.md).
Eine Kategorieänderung ist kein Rasterupdate und kein neuer Schwierigkeitslauf.
Manuelles Eintragen ersetzt nicht die Prüfung des zuständigen Writers.
Kategorienpflege und Registrierung im selben Checkout werden seriell ausgeführt;
keine parallelen manuellen Dateiänderungen während einer Transaktion.

Der Runtimeverbraucher prüft Format, Grenzen, Felder und Referenzen vor Übernahme
des gesamten Katalogs. Ein ungültiger Bestand muss von einem gültigen leeren
Bestand unterscheidbar bleiben; unbekannte Zuordnungen dürfen Rätsel nicht still
aus dem Angebot entfernen. Exakte Runtimefelder werden ausschließlich in RI-ONE
definiert. Spieleransichten erhalten keine Produktionsfreitexte oder Freigaben.

| Angrenzender Gegenstand | Maßgebliche Quelle |
| --- | --- |
| Katalogdarstellung und Spoilergrenze | [CATALOG_PRESENTATION](CATALOG_PRESENTATION.md) |
| Erstaufnahme und lokale Sortierauswahl | [CATALOG_SORTING](CATALOG_SORTING.md) |
| Aktuelle Bewertung | [SD_CATALOG](../difficulty/SD_CATALOG.md) und [SD2-Integration](../difficulty/SD2_INTEGRATION.md) |
| Kategoriezeichnungen im Buch | [UI_DRAWING_STYLE](UI_DRAWING_STYLE.md) und [Hintergrunddarstellung](../production/PUZZLE_BACKGROUNDS.md#13-hp-i2--runtime-darstellung-und-besuch) |

## 5. Historische Generationen

Frühere Inhalts-v2/v3/v4-, Runtime-v2…v7-, AT-, KU-B- und HP-Übergangsformen
sind im festen [Vorgängerstand](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CATEGORIES.md) nachschlagbar.
Sie sind keine aktuelle Kategorien- oder Recoveryschnittstelle. Die weiterhin
unterstützte reine Spieler-Lesekompatibilität für Runtime v2…v8 steht in
[RI-ONE §2.2](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md#22-spieler-lesekompatibilität).
Historische Originale behalten ihre Bytes und Bedeutung.
Es gibt keine implizite Formatumstellung durch Lesen oder Kategorienpflege.
