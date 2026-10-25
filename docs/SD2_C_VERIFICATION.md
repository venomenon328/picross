# SD2-C-T01 · Kompatible Integration

Stand: 25.10.2026. [Issue #405](https://github.com/venomenon328/picross/issues/405),
einschließlich Umsetzungsvorbereitung V1; Branch `feat/405-sd2-integration`.
Basis `0ae6535073fb808af44dcf3e12130a33ba49cdbc`, beim Start identisch mit aktuellem
`origin/main`; kein vorheriger C-Arbeitsbranch oder PR vorhanden.

## 1. Vertragsreihenfolge und Grenzen

[SD2-C-V01](SD2_INTEGRATION.md) wurde vor betroffenem Integrationscode mit
`23c0a90544d65437dad03d8f9457ce14893ef131` versioniert. Die ebenfalls vor ihrem
betroffenen Code gebundenen Ergänzungen `5a2d9f72cb8fb7a4823f9c45f92b5f7ea69e807d`
und `b28c856c90c24fbdea614b7bf9ac944c33a92d8b` präzisieren Vorgängerrevision,
rationale Grenzen und das explizite Vorschau-Assessment. Beide Methodenmanifeste
und ihre gebundenen Quellen/Artefakte bleiben unverändert:

| Methode | Freezehash |
| --- | --- |
| 0.3 | `8f7efa0d5ac76a1bd73fbae3618fec18dba28cf704887188eba2fcf020b9df79` |
| 0.4 | `5508f0742aa858a6adc31aa621433e68298b915fb0fd6b8d9e74e576ba87caaf` |

Der reale Katalog, aktive Bewertungen, Definitions-/Bildbytes und Produktions-
freigaben bleiben unverändert. `content/difficulty-method.json` wird im echten
Checkout nicht angelegt: Standard bleibt 0.3. Kein echter Kataloglauf, keine
Bestandsübernahme, keine Aktivierung, keine Save-Migration, kein Merge oder
Deployment. Historische A-/B-Nachweise werden weder ersetzt noch als C-Pass gezählt.

## 2. Prüfzuordnung C01–C06

Die neuen Fälle in
[test_sd2_catalog.py](../tests/puzzle_production/test_sd2_catalog.py)
verwenden feste unabhängige Testdefinitionen, kleine bereits synthetische
ZA-1-Pakete, isolierte Checkouts und eigens erzeugte Test-Git-Historien.
Es gibt keine aus echten Katalogrätseln abgeleiteten Fixtures. Analysatoren und
Importer werden nur in den ausdrücklich dafür vorgesehenen Schritten aufgerufen.

| Kriterium | Konkrete Gegenprobe / erhaltene Grenze |
| --- | --- |
| C01 | Analyse/Import von Kontext-v2 mit geschlossenem B-Bundle; CLI `candidate → analyze → import → rebind`, Registrierung nach synthetischer Aktivierung, Auswahl/alle, Plan/Adopt. Neue Logik verlangt genau aktive Methode; falsche Altmethoden und fehlende Ergebnisse werden vor Mutation abgewiesen. |
| C02 | Python-/Godot-Matrix für Runtime-v2/v3/v4/v5, 0.3/0.4 und null, alle L1–L5, notwendiges R4, exakte Feldmengen, keine Scores in Runtime. Alte Versionen lehnen 0.4 ab. Gemischte synthetische Kataloge in nativer Darstellung und Chromium prüfen unveränderte Namen, Sortierung und fehlende Tooltips. |
| C03 | Falsche innere/äußere Hashes, Quell-/Modusbindung, Zusatzdateien, veraltete Vorschau, fremde Bytes, ungültiger/aliasierter Default, Abbruch und wiederholte Recovery. No-op prüft vollständige Quellen und erhält Bytes, Revisionen und mtimes. Vier Journalgenerationen bleiben geschlossen. |
| C04 | Neueinstufung zwischen zwei synthetischen AT-Bildrevisionen erhält Definitionen, Identität, Slots, Kategorien, Added, ursprüngliche Freigaben und aktive AT-Quelle. Cleanup erhält Rating/Added/AT/Default/Runtime; historische Pakete werden nur durch den vorhandenen kompakten Belegweg ersetzt. |
| C05 | Plan bindet erwartete Methode/Revision, beide Freezehashes und vollen Snapshot; Adopt ändert nur Defaultdatei. Wiederholung und Rollback sind geprüft. Rebind einer gültigen 0.3-Bewertung nach synthetischer 0.4-Aktivierung bleibt zulässig; geänderte Logik benötigt frisches 0.4-Ergebnis. |
| C06 | Daten-/Runtime-/Journalvertrag, CLI-Beispiele und Authoring-/Produktionsrouting sind aktualisiert. Beide Freezehashes sowie Quellenbytegleichheit gegen die Basis sind zusätzliche Kontrollen. CI-Selektion bleibt unverändert. |

Zusätzliche spezifische Belege:

- Der R4-Fall prüft vollständige Paarlösung mit bewiesener Notwendigkeit gegen
  denselben vollständigen Proof bei abgebrochener Baseline. Nur der erste Fall
  erhält L5; der zweite bleibt `r4_necessity_unproven`, ohne aktive Ersatzstufe.
  Ein unvollständiger Linienfixpunkt bleibt ebenfalls offen.
- [test_reveal_recovery.py](../tests/puzzle_production/test_reveal_recovery.py)
  konstruiert echte alte Feldmengen und Runtimegenerationen, einschließlich AT,
  statt neue Felder unter alten Versionsnamen zu akzeptieren. Neue C-Rollbacks
  erhalten gültige alte Runtimebytes; alte Recoverygenerationen behalten ihr
  vereinbartes v4-Ziel. Der bestehende Staging-/Phasen-/Fremdbyte-Testumfang bleibt.
- [sd2_c_cases.gd](../game/tests/sd2_c_cases.gd) lädt ausschließlich eingefrorene
  synthetische Teil-/Abschlusssaves in temporären Profilen. Zellzustand, Verlauf,
  Redo, erarbeitete Enthüllung, Savebytes und Slotauflösung bleiben bei Wechsel
  der Ratingmetadaten gleich. Die Browser-Persistenzgruppe prüft dieselben
  bestehenden Grenzen über echte getrennte Webexports und Profilneustart.
- Die gemeinsamen Cleanup-Prüfungen erfassen jetzt auch Rating-/AT-/Added-/
  Defaultquellen und deren Namespaces unmittelbar vor der vorhandenen Mutation.
  Register, Sync, Cleanup und Recovery benötigen keinen neuen Analyse-/Ratinglauf.

## 3. Ausführung und Integrationsbindung

Lokale Adaptertests: Python 3.13.14, isoliertes Pillow exakt 12.3.0 unter Windows.
Der isolierte Godot-4.7.2-Regressionslauf des Implementierungsstands mit festen Testressourcen bestand mit
**17310 Prüfungen, 0 Fehlern**, einschließlich neuer C-Fälle. Keine echten Saves.
Die vier gezielten Durchstiche für Logikupdate, CLI, AT/Cleanup und Altjournal-
Abgrenzung bestanden gemeinsam (771,456 s); die zusätzliche Added-Übernahme mit
0.4 und aktivierter synthetischer Vorgabe separat (124,028 s). R4-Prefixabgrenzung
bestand ebenfalls (11,965 s). Gezielte alte Metadata-/Legacy-Recoverytests und
die beiden Selbstreview-Gegenproben bestanden. Entwicklungsfehler in
Testaufbau beziehungsweise alten Projektionsannahmen wurden sichtbar behoben;
frühere fehlgeschlagene Zwischenläufe gelten nicht als Abschlussnachweis.

Der [Implementierungs-PR #410](https://github.com/venomenon328/picross/pull/410)
bindet den endgültigen vollständigen Head, Basis,
Checkout/Test-Merge, CI-Run/Attempt, tatsächliche Jobauswahl und Resultate.
Die erforderliche vollständige Auswahl ist docs, production, product mit
`core,history,catalog,completion,adapters,graphics,export`, web mit allen fünf
Chromiumgruppen, delivery und ci-required. Der tatsächliche Diffselektor wählt
zusätzlich Preflight wegen `tools/product_fixtures.py` und
`tools/test_catalog_difficulty.py` über seine unveränderte konservative Regel
für unklassifizierte Werkzeugpfade; kein Firefox und keine Selektorverkürzung. Aktuelle
Remote-CI ist der Abschlussnachweis, nicht ein historischer A-/B-Lauf.

Die lokale Dokumentprüfung verwendet einen sauberen Snapshot der gelieferten
Dateien: vorhandene ignorierte Artefaktverzeichnisse im gemeinsamen Checkout
enthalten historische Markdownkopien und gehören nicht zum Paket. Ihre dortigen
Linkfehler sind kein Grund, fremde Arbeitsdateien zu ändern. Remote-Docs prüft
den sauberen tatsächlichen Integrationscheckout.

## 4. Getrennter Selbstreview und Gates

Nach Implementierung wurde der gesamte tatsächliche Diff von der oben genannten
Basis zu `b7fff7357e9ed3b23b50c2ee79e6f3d7153f73f1` gegen C01–C06,
Altversionsmatrix, Methodenfreezes und vollständige Quellen-/Recoverybindung in
einem getrennten Prüfschritt gelesen; anschließend die folgenden Korrekturen
nachgeprüft. 35 geschützte Dateien (27 Pythonquellen, sieben gebundene JSON-
Artefakte und 0.4-Manifest) sind bytegleich zur Basis. Der PR bindet den Abschluss
zusätzlich an finalen Head und aktuelle CI. Dies ist ein Selbstreview des Implementierers.

| Befund | Korrektur und Gegenprobe |
| --- | --- |
| B-SD2-C-01, behoben | Die neuen eigenständigen Projektionsvalidatoren akzeptierten bei unbekanntem Versionsparameter weiterhin Altwerte/null, obwohl die Registryprüfung schon geschlossen war. Python und Godot prüfen nun zuerst die exakte Versionsmenge; negative Proben einschließlich null decken den Fall ab. |
| B-SD2-C-02, behoben | Der gemeinsame Analyse-/Rebind-Einstieg las die Definition vor seiner JSON-Grenzprüfung vollständig. Er verwendet nun auch dort den vorhandenen begrenzten 2-MiB-Reader; übergroße Definition stoppt vor Anlage eines Analyseverzeichnisses. |
| B-SD2-C-03, behoben | Der erste CI-Zwischenlauf zeigte zwei überholte Testaufbauten: Eine aktuelle Added-Recovery wurde noch mit automatischem v4-Upgrade erwartet, und der Legacy-Reporttest etikettierte neue Felder/Runtimebytes als v1 um. Der Added-Test prüft jetzt exakte Wiederherstellung und anschließende Stale-Ablehnung nach explizitem Sync; der Legacy-Test verwendet die echte alte Feldmenge und Runtime-v4. Beide gezielten Regressionen bestanden nach Korrektur (2/2, 81,898 s); kein Reader wurde aufgeweicht. |
| B-SD2-C-04, behoben | Ein altes Sync-Journal konnte die bekannte Runtime-v5 unter seiner Ausnahme für veraltete Projektionsbytes akzeptieren. Der Grenzfall wurde reproduziert und wird jetzt vor Mutation abgewiesen. Die Gegenprobe deckt AT-/Previous-/Legacy-Generationen ab und bestätigt zugleich deren weiterhin zulässige Recovery aus opaken veralteten Bytes (1/1, 0,421 s). |
| B-SD2-C-05, behoben | CI-Lauf 40231927358 am Head `b9cae3daffc8b368070ae5280fc497a66a728bfe` meldete bei 368 Produktionstests einen Fehler in der neuen Default-Negativprobe: Die bestehende Ressourcengrenze bricht korrekt mit `Aborted` ab, der Test erwartete auch dafür `ValueError`. Die Probe unterscheidet nun Größenabbruch und ungültige Inhalte ausdrücklich und prüft weiter für Check, Sync und Registrierung unveränderte Bytes/mtimes. Gezielte Wiederholung bestanden (1/1, 26,360 s), Produktcode unverändert. Die kleine Test-/Dokumentkorrektur wurde getrennt nachgeprüft; der abgelöste CI-Lauf ist kein finaler Pass. |

- **A-SD2-C-R01:** Qualifizierter separater Review am finalen Head durch einen
  gesonderten Reviewlauf bleibt vor Merge offen.
- **A-SD2-C-MERGE:** Ausdrückliche Eigentümer-Mergefreigabe nach erfüllten Gates
  bleibt offen; dieser Auftrag enthält keinen Merge.
- Tatsächliche Analyse, Übernahme und Aktivierung bleiben #406. Menschliche
  Vergleichslösungen sind freiwillig; kein neues persönliches Gameplaygate.

Nach der Nachprüfung bestehen keine offenen blockierenden Selbstreviewbefunde.
Urteil: **separate Abnahme offen**. Der aktuelle technische Abschlussnachweis
bleibt an die tatsächlich abgeschlossene finale CI im PR gebunden.
