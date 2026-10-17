# Kategorien- und Zuordnungsvertrag (KAT-1)

**KE / #233, Implementierungsvertrag vom 17.10.2026:**
[KE-D06](CATALOG_PRESENTATION.md) ergänzt minimale typisierte Schwierigkeit.
Kategorienquelle, Zuordnung, Definitionen, Saves und Freigabebindungen bleiben
unverändert. [Technische Nachweise](KE_VERIFICATION.md); KE-R01/KE-M01 separat.

Stand 12.10.2026, [Issue #78](https://github.com/venomenon328/picross/issues/78).
Die [Kategorienquelle](../content/categories.json) führt den initialen redaktionellen
Arbeitsbestand von 20 Motivgruppen. Kategorien sind weder Kapitel noch Schwierigkeit
oder Freischaltbedingungen. Alle sichtbaren registrierten Rätsel bleiben spielbar.
Ausgewogene Mengen sind ein Planungsziel ohne Quote. Die Katalogoberfläche aus [#79](https://github.com/venomenon328/picross/issues/79)
verwendet diese Projektion unverändert; [KAT-2-Prüfzuordnung](KAT2_VERIFICATION.md).

## Daten und Grenzen

`content/categories.json` ist die einzige autoritative Kategorienquelle:
`picross-categories-v1`, exakt `format` und `categories`. Ein Eintrag enthält exakt
`id`, `name`, `order`. ID: ASCII `[a-z][a-z0-9-]{0,63}`, eindeutig und stabil.
Anzeigename: 1…128 Zeichen, nicht leer, ohne Randwhitespace oder C0/C1-Steuerzeichen.
Reihenfolge: eindeutige Ganzzahl 1…10000, kein bool; die Projektion sortiert danach.
Höchstens 256 Kategorien und 131072 UTF-8-Dateibytes. Eine leere Kategorienliste ist
nur ohne referenzierende Inhalte gültig. Keine automatische Ableitung, Auffangkategorie,
Tags oder Unterkategorien. Unbekannte Formate/Felder, doppelte JSON-Schlüssel/IDs/
Reihenfolgen und nichtendliche Zahlen werden zurückgewiesen.

`content/registry.json` verwendet `picross-content-registry-v2`. Jeder Eintrag
besitzt genau ein `category_id`, das unabhängig von Sichtbarkeit eine vorhandene
Kategorie referenziert. Die Registry enthält ausschließlich Produktionsbindungen;
ein leerer Bestand ist gültig. Alle Einträge stehen lexikografisch nach ID.
Maximum: 10000 Einträge und 8 MiB Inhaltsregistry. Die aktive F01–F09-Reservierung
ist durch [#114](https://github.com/venomenon328/picross/issues/114) aufgehoben.
Workflow-Zuordnungen und Kategorienquelle einschließlich leerer Kategorien bleiben
unverändert.

Der prägende Hauptgegenstand entscheidet; Nebenobjekte erzeugen keine weitere
Zuordnung. Die Gruppen sind keine biologische Taxonomie oder Essbarkeitsaussage.

`game/data/registry.json` ist die kanonische UTF-8/LF-Projektion
`picross-runtime-registry-v3`: exakt `format`, geordnete `categories` und `entries`.
Einträge enthalten exakt `id`, `key`, `save_slot`, `definition`, `reveal`, `visible`,
`category_id` und `difficulty`. Produktionsbelege fehlen.

`difficulty` ist `null` für eine fehlende Einstufung (leeres historisch gültiges
Produktionsobjekt) oder ein Objekt mit exakt sechs Feldern:

| Feld | Zulässige Werte |
| --- | --- |
| `method` | `picross-difficulty-0.1`, `picross-difficulty-0.2` |
| `level` | `L1` bis `L5` |
| `assessment_type` | `editorial_estimate`, `instrumented` |
| `confidence` | `low`, `medium`, `high` |
| `plausible_range` | Zwei Stufen, untere ≤ Einstufung ≤ obere |
| `r4_required` | Boolean, aus vorhandener R4-Regelfamilie |

Notwendiges R4 verlangt den vorhandenen 0.2-Vertrag: instrumentiert, L5,
Spannweite L5–L5, Sicherheit medium. Der Writer prüft zusätzlich den vorhandenen
logischen Anspruch `linienübergreifend / besonders hoher logischer Anspruch`.
Produktionsregelfamilien, Engpässe und andere Freitexte werden nie exportiert.
Ungültige vorhandene Angaben sind Fehler; keine Ableitung oder Neueinstufung.

Der Loader liest weiterhin `picross-runtime-registry-v2` mit exakt den bisherigen
sieben Feldern, ohne `difficulty`; Anzeige „Nicht eingestuft“. Ein achtes Feld
ist unter v2 ungültig. Neue Writer erzeugen ausschließlich v3; unter v3 muss
`difficulty` ausdrücklich vorhanden sein. Unbekannte Methoden, Typen, Felder
und widersprüchliche Angaben verwerfen den gesamten Bestand.

Python prüft exakte Projektionsbytes; Godot prüft Format,
Grenzen, Felder, Kategorien und Referenzen vor Übernahme des gesamten Bestands.
`entries()`, `categories()`, `by_id()`, `by_key()` und `catalog_ids()` liefern die
Daten; `load_error` unterscheidet einen ungültigen Bestand von einem gültigen leeren.
Unbekannte Zuordnungen dürfen Inhalte nicht still aus dem Angebot entfernen.

Kategorie und Anzeigename gehören ausschließlich zum Katalog. Definitionen,
Raster/Hinweise, Logik-/Proofhashes, Assets, Runtime-Revision, Save-Schema 1,
Appidentität und `user://p1/saves/` bleiben unverändert. Umbenennen erzeugt keine
neue Rätselidentität; Entfernen einer referenzierten Kategorie ist ein Fehler.

## Export und technische Übernahme

Der [ZA-1-Adapter](ZA1_ADAPTER.md) verlangt bei neuen Exporten ausdrücklich
`--category-id <id> --categories content/categories.json`. API: `export(...,
category_id=..., categories_path=Path(...))`. Keine Ableitung aus Dateiname, Motiv,
ID, Bild oder Schwierigkeit. Die Kategorienquelle wird vollständig validiert und
als kanonischer `categories.json`-Snapshot mitgeliefert. Manifest
`picross-target-export-v2` bindet `category_id` und `categories={file,sha256}`;
Dateiinventar und `inspection.json` binden dieselbe Auswahl. Der autorisierte
manuelle ZA-1-v3-Export ergänzt dieselbe Kategoriebindung um seine externe
Autorisierung; der Paarprofil-Export v4 führt dieselben Kategoriebindungen und
zusätzlich seinen geprüften Deduktionsvertrag. Runtimeprojektion und
Kategorienvertrag bleiben gleich. `verify-export` prüft
Snapshot, Hash, Referenz und Bericht offline sowie den vollständigen ZA-1-Vertrag.

`plan`/`register` verlangen zusätzlich die ID im aktuellen Zielcheckout. Der Plan
zeigt ID, aktuellen Anzeigenamen und Registry vorher/nachher. Ein inzwischen
geänderter Anzeigename ist erlaubt. Eine abweichende Kategorie unter belegter
Inhalts-ID ist ein Konflikt; identische Wiederholung bleibt No-op. Registryprüfung
vergleicht die Zuordnung auch außerhalb des vollständigen Produktionsreplays mit
dem gebundenen Export. Manuelles Eintragen ersetzt keine gültigen Pakete/Freigaben.

Neue Kategorien und Anzeigenamen können ausdrücklich als Datenänderung gepflegt
werden. Danach die Projektion erzeugen und den gesamten Checkout prüfen:

```sh
python -m tools.puzzle_production.target_adapter sync-runtime --checkout .
python -m tools.puzzle_production.target_adapter check-registry --checkout .
```

`sync-runtime` validiert die Quellen und registrierten Bindungen vor
atomarem Ersetzen der Projektion. Fehlende Referenzen oder offene Journale stoppen
vor Änderungen. Kein Umklassifizierungseditor: Zuordnungsänderungen registrierter
v2-Exporte benötigen eine ausdrücklich geprüfte Metadaten-/Exportbindung.
Kategorien-/Registrypflege und Registrierung im selben Checkout seriell ausführen;
keine parallelen manuellen Dateiänderungen während einer Transaktion.

Registrierung verwendet `picross-registration-journal-v2` mit den unveränderten
Kategorienquellbytes zusätzlich zu alten/neuen Indizes und erwarteten Zielbytes.
Die Quelle wird vor Journalanlage, nach Staging und vor/während Veröffentlichung
erneut verglichen. Runtime wird zuletzt veröffentlicht. Fehler rollen eigene
Dateien/Indizes zurück; fremde Kategorienänderungen werden nicht überschrieben.
Ein Prozessabbruch blockiert weitere Arbeit bis zur expliziten Recovery.
Recovery prüft Kategorienbytes, Indizes, Ziele und Hashes vollständig vor Mutation;
fremde Änderungen erfordern Klärung, das Journal bleibt erhalten.

## Altformate und Umstellung

Authoring-v2 und alte `picross-target-export-v1`-Exporte bleiben technisch prüfbar.
Die gespeicherte v1-Inspektion behält ihre damalige Semantik. Der heutige
`verify-export`-Bericht weist `legacy_catalog_ready` getrennt aus;
`category_ready=false` und `catalog_ready=false` erlauben keine neue Registrierung.
Diagnose ohne Kategorien bleibt möglich, einschließlich fehlender Endfreigabe.
Neue Inspektionen verwenden `picross-target-inspection-v2`; erst der kategorisierte
Export verbindet technische, redaktionelle und Kategorienbereitschaft.

Ein neuer Export aus demselben unveränderten Eingangs-/Freigabepaket ergänzt die
Kategorie außen. Keine neue Bild-/Endfreigabe allein wegen Katalogmetadaten:
Original-ZIP, Handoff, Inventar, Auswahl und Freigabe bleiben byte-/hashgleich.
Bestehende historische Pilotexporte v1/v2 bleiben unverändert. Bereits vor KAT-1
registrierte ZA-1-v1-Pakete behalten ihre Exporthashes; ihre ausdrücklich geprüfte
Bestandskategorie steht in der neuen Registry, ohne einen rückwirkend kategorisierten
Originalexport zu behaupten. Eine neue Registrierung aus v1 bleibt gesperrt.

**Vor einer Formatumstellung jedes offene v1-Registrierungsjournal mit seinem
passenden alten Werkzeug und unverändertem alten Checkout vollständig auflösen.**
KAT-1 ignoriert oder löscht es nicht: `recover-registration` blockiert mit Hinweis
auf den alten Vertrag. Bei bereits gemischtem Stand alle Dateien/Journale erhalten
und die gebundenen alten/neuen Stände prüfen; kein automatisches Wegwerfen oder
blindes Umschreiben des Journals. Rollback von KAT-1 ist nur ohne neue v2-Inhalte
und ohne offene Transaktion als geprüfte Rücknahme der Metadatendateien möglich;
Spielstände benötigen keine Migration.

## Produktionsfundus und Wiederaufnahme

Neue äußere Authoring-Records führen `category_id`, sobald die Motivzuordnung
feststeht; ein offenes Briefing darf ausdrücklich `null` führen. Alte Records ohne
Feld bleiben lesbar. Vor kategorisiertem Export ist die Zuordnung Pflicht.
Arbeitsindex/Record sind keine Runtime-Registrierung; Freigaben bleiben separat.

Bei Wiederaufnahme den aktuellen Arbeitsindex und die Zielregistry verwenden.
Neuere Records, Freigaben und Integrationsbelege laufender Produktionen erhalten.
Final integrierte Produktionen werden gemäß PUZZLE_AUTHORING §9 entfernt; ihre
kompakten Integrationsbindungen benötigen keinen Paket-Replay. Historische Parallel-
oder Lieferstände erzeugen keine neuen Prüf-/Exportaufträge für Bestandsrätsel.

Prüfwege und gebundene Testinputs: [KAT1_VERIFICATION](KAT1_VERIFICATION.md).
