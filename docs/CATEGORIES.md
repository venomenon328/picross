# Kategorien- und Zuordnungsvertrag (KAT-1)

**SD2 · 25.10.2026:** [SD2-D05](PUZZLE_DIFFICULTY_V2.md) verlangt künftig die
gemeinsame kompatible Projektion der Methode 0.4. Die folgenden exakten
alten Schemas erlauben 0.4 nicht. [SD2-C-V01](SD2_INTEGRATION.md) spezifiziert
vor Code Runtime-v5, Quellenpriorität und Alt-/Neuübergänge; keine zusätzlichen Rohprofile,
Scores oder Freitexte im Spieler. Kategorien, Identitäten, Added und AT bleiben
bei einer reinen späteren Neueinstufung unverändert. [D-F01/T01](SD2_D_ADOPTION.md)
übernimmt nach Eigentümerabnahme 45 Ratings auf 0.4 und projiziert Runtime-v5;
dieser Zusatz ändert keine historischen Runtime-v2/v3/v4-Formate.

**AT · Umsetzungsvorbereitung V4 vom 19.10.2026; AT-A nach AT-A-R01 mit PR #263 integriert:**
[AT](REVEAL_TRANSPARENCY.md) ergänzt in AT-A die getrennte aktive Bildbindung und
deren gemeinsamen Prüf-/Transaktionsweg; AT-B übernimmt danach freigegebene neue
Bildfassungen des gebundenen Bestands. Historische Registry-/Paket-/Integrations-
bindungen bleiben unverändert. [AT-B-V01](AT_B_VERIFICATION.md) liefert die
vollständige gebundene Bild-/Endfreigabevorlage. Nach
[Eigentümerabnahme](AT_B_OWNER_APPROVAL.md) ist AT-B-F01 mit kontrollierter
Bildübernahme und AT-B-T01 beauftragt; finales separates Review und Merge bleiben offen.

**KU-B / #244, freigegebener Sollstand vom 18.10.2026; Umsetzung offen:**
[Katalogsortierung](CATALOG_SORTING.md) ergänzt eine eigene autoritative,
ID-gebundene Quelle für die erste Katalogaufnahme und deren minimale
UTC-Zeitpunkt-/null-Projektion. Herkunftsbelege bleiben im Inhaltsbereich;
historische Produktions-/Integrationsbindungen bleiben unverändert. Neue
Formatversionen und der gemeinsame Writer-/Loader-/Validierungs-/Recoveryvertrag
werden im KU-B-Paket vor der ersten betroffenen Codeänderung festgelegt.
Die unten genannten exakten Inhalts-v2-/Runtime-v2/v3-Schemas sind der aktuelle
Implementierungsstand und dürfen nicht still um zusätzliche Felder erweitert werden.
KU-A verändert diese Datenverträge nicht.

**SD-C1, technischer Vertrag vom 17.10.2026:**
[Bewertungsquelle und Recovery](SD_CATALOG.md) ergänzen die getrennte aktuelle
Katalogbewertung. Inhalts-v2, Runtime-v3 und der exakte Runtime-v2-Leser bleiben.
SD-C1 ist mit PR #242 integriert. SD-C2 hat nach bestandenem Vor-Übernahme-Review
gemäß SD-C2-F01 die 26 geprüften Bewertungen und ausschließlich deren Difficultyfelder
in der Runtime übernommen; [Belege und finales Reviewgate](SD_CATALOG.md).
Historische Produktionswerte, Kategorien und Identitäten bleiben unverändert.

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

Für KU-B gelten ergänzend die Quellen-, Zeit- und Übernahmeregeln in
[CATALOG_SORTING](CATALOG_SORTING.md): eine Erstregistrierung setzt ihren
Zeitpunkt genau einmal im mutierenden Transaktionsplan; Wiederholung, spätere
Änderung, Sync, Bewertungsübernahme, Cleanup und Recovery erhalten ihn.
Ein lesender Plan erzeugt keinen endgültigen Zeitpunkt. Bestehende unbekannte
Zeitpunkte bleiben null, bis eine ausdrücklich belegte Übernahme erfolgt.
Die einmalige historische Ergänzung verwendet einen prüfbaren Plan und einen
dauerhaften kompakten Herkunftsbeleg je ID; keine Datumsannahme aus Dateizeiten
oder späteren Änderungen. Die zulässige Rekonstruktion aus der ersten belegten
Katalogaufnahme ist ausdrücklich als solche gekennzeichnet.

Eine ungültige vorhandene Quelle ist kein fehlender Wert. Alle gemeinsamen
Projektions-/Transaktionswege prüfen dieselbe Quelle und erhalten gültige
Altformate und historische Bindungen. Die gespeicherte Sortierauswahl ist eine
separate lokale UI-Präferenz und kein Registry- oder Rätselsavefeld.

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
| `method` | `picross-difficulty-0.1`, `picross-difficulty-0.2`, `picross-difficulty-0.3` |
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

0.3 verlangt ausschließlich `instrumented`/`medium` und `[Lx,Lx]` für die
projizierte Stufe. Notwendiges R4 verlangt L5. Diese Punktprojektion ist kein
menschliches Unsicherheitsintervall. Die bisherige KE-Anzeige erläutert dies im
methodenspezifischen Tooltip; KU-A entfernt diesen Schwierigkeitstooltip gemäß
[Katalogdarstellung](CATALOG_PRESENTATION.md), ohne die Bewertungsdaten oder
deren Bedeutung zu ändern.

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

## SD · Aktuelle Bewertungsmetadaten

SD-C1 führt die akzeptierte aktuelle Katalogbewertung in einer eigenen autoritativen
Metadatenquelle mit gebundenen kompakten Berichten. Die bisherigen
`production.difficulty`-Werte bleiben historische Produktionsangaben; bestehende
Paket-/Export-/Integrationsmanifeste werden nicht für eine Neubewertung umgeschrieben.
Insbesondere bleibt der vollständige Eintragsvergleich kompakter Integrationsbelege
erhalten. Eine neue Ratingquelle darf diese Bindung nicht umgehen.

Die Zuordnung bindet Rätsel-ID, tatsächlichen Definitionshash, einen eigenen
kanonischen Analyseinputhash sowie Methode, Parameter-/Werkzeugstand und Bericht.
Der Analysehash wird aus der aktuellen Hinweissemantik gebildet; historische
Produktions-`logic_hash`-Werte werden wegen der damaligen Farbumabbildung nicht als
identisch behauptet. Ratingdaten und erforderliche kompakte Berichte bleiben nach
Produktionscleanup erhalten. Die vollständigen Pfad-/Feld-/Formatverträge stehen
in [SD-C1](SD_CATALOG.md): `content/difficulty/<pz-ID>/rating.json` und kompakte
Berichte unter `content/difficulty/reports/<run-id>/`. Fehlend erhält den Altwert;
vorhanden ungültig stoppt ohne Fallback. Aktive Gültigkeit hängt nicht an
Registrygesamt-, Git-HEAD- oder Produktionspakethashes.

Die Runtime erhält weiterhin nur minimale typisierte, spoilerfreie Angaben aus
einer ausdrücklich übernommenen Bewertung. SD-C1 führt Writer, Godot-Loader,
Methoden-/Versionsprüfung, kanonische Projektion und sämtliche Registrierungs-,
Update-/Recoverypfade gemeinsam fort. Bisher gültige v2-/v3-Daten und
exakte KE-Altjournale behalten ihren geprüften Übergang; unbekannte, gemischte,
veraltete oder fremd veränderte Bindungen werden nicht still akzeptiert.
Es gelten ausschließlich die oben benannten Methoden und exakten v2-/v3-Felder;
es gibt keine neue Runtimeversion.

Eine reine Neueinstufung ändert weder Definition, Hinweise, ID/Key, Save-Slot,
Runtime-Revision noch Assets oder Saves. Die erste Bestandsübernahme und spätere
Neueinstufungen werden ausdrücklich ausgeführt; aus Katalogstart, Build oder
Methodenänderung folgt kein Ratinglauf. Bewertungsmethode, Stufengrenzen und
Übergangsverhalten stehen im [SD-Vertrag](PUZZLE_DIFFICULTY.md).

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

KE-N1: Registrierungsjournal v2 und Updatejournal v1 dürfen einheitlich kanonische
Runtime-v2-Snapshots mit sieben Feldern oder aktuelle v3-Snapshots enthalten.
Gemischte, unbekannte und nichtkanonische Projektionen werden abgewiesen. Vor
der ersten Checkoutänderung wird die gesamte alte Zielansicht mit ihrer aus
Authoringdaten strikt abgeleiteten v3-Runtime geprüft. Erfolgreiche Recovery
endet direkt in einem gültigen aktuellen Checkout; kein nachgeschobenes Sync.
Bei Unterbrechung ist nur die exakt hergeleitete eigene v3-Zwischenprojektion
zusätzlich zu den gebundenen alten/neuen Bytes zulässig. Fremde Bytes bleiben
einschließlich Journal erhalten. Die Sperre für Registrierungsjournal v1 bleibt.

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

## KU-B · Runtimeprojektion v4

`picross-runtime-registry-v4` behält exakt die drei Top-Level-Felder
`format,categories,entries` und die kanonische Registryreihenfolge. Ein Eintrag
hat exakt die bisherigen acht v3-Felder plus `added_at` (striktes UTC/null gemäß
[Hinzugefügt-Vertrag](CATALOG_SORTING.md)). Content-Registry-v2 bleibt unverändert.
Runtime-v2 mit exakt sieben und v3 mit exakt acht Eintragsfeldern bleiben lesbar;
ihr fehlendes Datum wird nur im Speicher als unbekannt behandelt. Fremdfelder,
falsche Versionstypen und Datumstypen sind Fehler, keine implizite Migration.
Der gemeinsame Projektor validiert alle Added-Quellen und schreibt künftig v4;
Runtimeverbraucher analysieren keine Rätsel und lesen keine Herkunftsbelege.

## AT · Aktive Bildquelle und exakte Kompatibilität

Für den freigegebenen [AT-A-Sollstand](REVEAL_TRANSPARENCY.md) wird die aktuelle
Bildfassung außerhalb historischer Produktions-/Integrationsbelege geführt.
Unveränderte Originalbindungen und neue aktive Bildbindung bleiben separat
prüfbar; der vollständige Eintragsvergleich kompakter Altmanifeste wird nicht
gelockert. Die neue Quelle bindet tatsächliche Bildfreigabe, ID, Bildrevision und
Alt-/Neuhashes. Fehlt die neue optionale Bildquelle, gilt die bisherige
Originalbindung; eine vorhandene ungültige oder widersprüchliche Quelle stoppt
ohne Fallback.
Alle Quellen-/Registrierungs-/Update-/Sync-/Adopt-/Recoverywege prüfen denselben
aktuellen Bildstand und erhalten die übrigen Metadaten bytegleich.

Definition samt Runtime-Revision, Ressourcenpfade, ID/Key, Save-Slot, Kategorie,
Sichtbarkeit, Reihenfolge, Rating und Hinzugefügt-Daten ändern sich durch ein
reines Bildupdate nicht. Die Runtime erhält keine Produktionsfreitexte,
Bildfreigaben oder Herkunftsprotokolle. Die Spoilergrenze bleibt auch beim Laden
und Ableiten des aktuellen Reveals bestehen. Neu und Begonnen erhalten keine
Motivvorschau aus dem neuen Bild.

P01 schließt die Formate in [ZA-1](ZA1_ADAPTER.md),
[Transaktionen](SD_CATALOG.md) und der [Soll-CLI](../tools/puzzle_production/README.md).
Inhalts-v2, Runtime-v2/v3/v4 und abgegrenzte Altjournale behalten ihre exakten
Felder/Leseregeln. Keine zusätzliche Runtimeversion oder neue Runtimefelder.
Reine Bildadoption schreibt auch keine byteidentische Runtime neu.

### AT-P01-D02 · Namensraum und eine gemeinsame Auflösung

Der gesamte optionale Baum `content/reveals/` wird vor jeder Quellenprüfung
inventarisiert. Er darf fehlen oder leer sein. Sonst sind ausschließlich reguläre,
nicht ausführbare Dateien `<registrierte-kanonische-pz-ID>.json` erlaubt, maximal
10000, je 1 MiB. Keine Unterverzeichnisse, weiteren Endungen, Aliasnamen,
unregistrierten IDs, Großschreibungsvarianten, Punktsegmente, Symlinks, Junctions,
Reparsepunkte oder Hardlinks mit mehreren Namen. Alle Pfadkomponenten sind vor
Öffnen und erneut unmittelbar vor Mutation sicher zu prüfen; Pfad-/Dateiwechsel
während des Lesens blockieren. Windows-Gerätenamen, abschließende Punkte/Leerzeichen,
Laufwerke, UNC und casefold-Kollisionen sind verboten. Repositoryrelative Pfade
haben `/` und höchstens 240 Zeichen; Registryressourcen dürfen nicht kollidieren.
Aktive Transaktionstemporärdateien sind ausschließlich die streng abgeleitete
Ausnahme aus [Recovery](SD_CATALOG.md), keine generelle Punktdateiausnahme.

Die gemeinsame Auflösung liefert intern exakt
`id,definition_sha256,runtime_revision,export_manifest_sha256,physical_manifest_sha256,historical_reveal_sha256,effective_reveal_sha256,historical_notice_sha256,effective_notice_sha256,record_hash`.
`record_hash` ist null ausschließlich ohne Quelle; alle anderen Werte sind
geprüfte Hashes beziehungsweise die registrierte ID/numerische Runtime-Revision.
Das ist ein internes Prüfergebnis, kein zusätzliches persistiertes Runtimeformat.

| Quelle/Zustand | Verbindliche Prüfung |
| --- | --- |
| Kein AT-Record | Vollständiger bisheriger Export-/Receipt-/Eintragsvergleich; Live-Bild und Live-Notice müssen den historischen Bindungen entsprechen. Kein Transparenzzwang für legitime alte Bytes. |
| Gültiger Record | Gesamte Historie, Hashketten, Freigaben, Herkunft und Notice prüfen; letzte Bindung gegen aktuelle Definition, Identität und normalisierten Produktionseintrag vergleichen. Tatsächliches Live-Bild/Notice gegen effektive Bindung prüfen. Historischer Bildhash bleibt am Export/Receipt geprüft. |
| Ungültiger oder fehlender erwarteter Record, fremde Namespaceeinträge | Gesamte Operation vor Mutation/No-op stoppen. Kein Fallback; erwartete Abwesenheit nur bei tatsächlich gültiger historischer Live-Bindung. |

`content_registry.check_checkout` prüft weiterhin den tatsächlichen
Manifestdateihash gegen die aktuelle Inhaltsregistry, Definitionsbytes sowie alle
Identitäts-/Kategorie-/Produktionsfelder. `integrated_content.check` behält exakt
seinen vollständigen Receipt-Eintragsvergleich: Nur der **physische** Pakethash
wird beim Vergleich wie bisher durch den ursprünglichen Exporthash ersetzt.
Der historische Noticehash muss dem Receipt und `origin`/passender Bindung
entsprechen; bei vollem Export wird die darin enthaltene Notice geprüft.
Nur der zusätzliche Live-Bild-/Noticevergleich verwendet die aktive Auflösung.
Ein gültiger AT-Record legitimiert keine andere Abweichung im historischen Beleg.
`verify-export` selbst bleibt ein vollständiger Prüfer des jeweils übergebenen
unveränderten Exports; es ersetzt dessen Bild nicht heimlich aus dem Checkout.

Die aktuelle AT-Bindung enthält **keinen physisch wechselnden Receipthash** und
keinen Registry-/HEAD-Gesamthash. Cleanup darf deshalb den belegten Export durch
den zulässigen kompakten Receipt ersetzen, ohne den Record zu ändern. Ein Plan
bindet hingegen auch physische Quellen: Cleanup nach Planung macht ihn stale.

### AT-P01 · Folgeoperationen, Snapshot und zulässige Deltas

`T(R)`/`K(R)` bezeichnen die vollständigen Text-/Retainedmengen des
[Transaktionsvertrags](SD_CATALOG.md). Jeder neue Plan/Snapshot bindet ihre
Vereinigung plus sämtliche ausdrücklich erwarteten Zielabwesenheiten und das
vollständige sichere Namespaceinventar; keine bloße Auswahl der geänderten ID.
Definitionen, Bilddateien, Notice, physische Manifest-/Receiptbytes, Ratings,
Added und ihre behaltenen Berichte sind damit auch für unabhängige IDs geschützt.

| Operation | Alt-/Zielvertrag und ausdrücklich erlaubtes Delta |
| --- | --- |
| Neue Registrierung | Gültiger Altcheckout, genau eine neue Produktions-ID nach ZA-1 mit Bild aus freigegebenem Export, Rating und einmaligem Added; vorhandene AT-Records und Bilder unverändert. Neue ID hat zunächst keinen AT-Record, seine Abwesenheit ist gebunden. |
| Historisch identische Registrierung | Vollständiger ursprünglicher Eingangsvergleich und gültiger aktiver Checkout; kein Delta und kein Journal. Nach Rasterupdate kein Wiederbeleben alter Produktion. |
| Reine Bildadoption | Registry/Kategorien/Runtime/Definitionen/Ratings/Added/Produktionsbelege exakt gleich. Nur ausgewählte vorhandene Bilder, zugehörige AT-Records und gegebenenfalls angehängte Notices ändern sich. Vollständiger Zielcheckout vor Mutation geprüft. |
| Rasterupdate | Genau eine neue Produktion/höhere Definition nach ZA-1; Bild und aktive Notice gleich. Nur dessen Registryeintrag, Definition, eigener SD-Record nach SD-C1, neues Paket und AT-Quellen-Rebind dürfen ändern; Added unverändert. Export enthält genau das aktive Bild, seine historische Exportnotice darf separat bleiben. |
| Sync | Alle Quellen und AT unverändert; ausschließlich kanonische Runtime-v4 darf eine veraltete Projektion ersetzen. Ausgangsquellen einschließlich gültiger aktiver Bilder müssen vollständig geprüft sein. |
| SD-Adoption | Bisheriger SD-Delta-/Berichtsvertrag; Definitionen, Bilder, AT und Added bleiben bytegleich. Neuer Plan bindet AT einschließlich erwarteter Abwesenheiten. |
| Added-Adoption | Nur ausgewählte zulässige Added-Records, eigener Bericht und Runtime; Bilder, AT, Ratings und Definitionen bleiben bytegleich. Neuer Plan bindet AT. |
| Prüfen/Export | Gemeinsame Auflösung vor Checkoutprüfung/Spielerexport; kein Quellenschreiben. Regulärer neuer Produktionsexport prüft weiter seine eigenen freigegebenen Eingänge, Rasterexport nach AT zusätzlich effektive Bildgleichheit vor Integration. |
| Produktionscleanup | Bisheriges belegtes Paket-/Authoring-/Indexdelta; aktive Bildquelle, Bild, Notice, Runtime, Rating und Added unverändert, historischer Noticebezug separat erhalten. Kein AT-Rebind allein wegen physischem Receiptwechsel. |
| Recovery | Exakte Journalgeneration und alle Quellen prüfen; nur gebundene eigene Alt-/Neu-/abgeleitete Zwischenstände, Rückführung unmittelbar in gültigen aktuellen Altcheckout. Kein Analyse-/Exportreplay und kein Pflicht-Sync danach. |

Nach AT werden neue SD-Auswahlberichte als `picross-catalog-difficulty-report-v3`
geschrieben: exakt die v2-Felder/Unterfelder und Regeln, aber `result.sources`
um alle kanonischen AT-Pfade (Hash/null) erweitert; `snapshot` bleibt Registry,
Kategorien, Runtime. Die Quellenhöchstzahl steigt für v3 von 70003 auf 80003.
V1/v2 bleiben unverändert lesbar und wiederholbar ausschließlich ohne ungebundene
AT-Quellen. Kein nachträgliches Ergänzen historischer Reports. Neue Added-Pläne
verwenden `picross-added-plan-v2`: exakt v1-Felder und -Zeilen, `sources` erweitert
um dieselben AT-Bindungen, maximal 80003 Pfade. Ihr Dauerbericht sind dieselben
unveränderten Planbytes. Aktive Added-v1-Records und Rating-v1/v2-Hüllen ändern
ihr Schema nicht. Alte Pläne/Reports bei vorhandenen AT-Daten stoppen vor
Mutation/No-op; neue vollständige Planung ist erforderlich.
Auch eine zwischenzeitliche Bildrevision ohne sichtbare Runtimeänderung macht
einen neuen SD-/Added-/AT-Plan stale. Erfolgreiche Wiederholung darf nur ihre
exakt gebundenen eigenen Zielbytes im Speicher auf den Ausgangssnapshot
zurückführen; jede andere Quellenänderung blockiert.
