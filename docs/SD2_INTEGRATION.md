# SD2-C · Kompatible Integration und expliziter Produktionsstandard

Vertragsstand: 25.10.2026 · SD2-C-V01 · vor Implementierung festgelegt.
Status 26.10.2026: C nach separatem R01 über PR #410 auf
`4e23e644f3457362e02b75f78fdb575a99265494` integriert.
[D-V01](SD2_D_VERIFICATION.md) führt den gesonderten Bestandsvergleich;
[D-F01/T01](SD2_D_ADOPTION.md) übernimmt nach Eigentümerabnahme alle 45 Ratings
und aktiviert 0.4 auf dem Arbeitsbranch. Die folgende Ausgangsbindung und
der [C-T01-Bericht](SD2_C_VERIFICATION.md) bleiben historisch.
[Issue #405](https://github.com/venomenon328/picross/issues/405), einschließlich
Umsetzungsvorbereitung V1, beauftragt dieses Paket auf
`main@0ae6535073fb808af44dcf3e12130a33ba49cdbc`.
SD2-A/PR #408 und SD2-B/PR #409 sind nach jeweils separatem R01 integriert.
Die [A-Nachweise](SD2_A_VERIFICATION.md) und [B-Nachweise](SD2_B_VERIFICATION.md)
bleiben an ihre damaligen Lieferheads gebunden.

Dieser Vertrag ergänzt [SD-C1](SD_CATALOG.md), [Kategorien](CATEGORIES.md),
[ZA-1](ZA1_ADAPTER.md), [Authoring](ai-workflows/PUZZLE_AUTHORING.md) und die
[CLI-Anleitung](../tools/puzzle_production/README.md). Er ersetzt nur deren
nachfolgend ausdrücklich benannten Versions-/Dispatchregeln. Inhalt-v2,
Definitionen, Save-Schema 1, IDs, Slots, Kategorien, Freigaben, Added und AT
behalten ihre Verträge. Keine neuen UI-Funktionen oder persönlichen Spielgates.

## C-V01-01 · Unveränderte Methoden und geschlossene Altformate

| Methode | Unveränderlicher Freezehash |
| --- | --- |
| `picross-difficulty-0.3` | `8f7efa0d5ac76a1bd73fbae3618fec18dba28cf704887188eba2fcf020b9df79` |
| `picross-difficulty-0.4` | `5508f0742aa858a6adc31aa621433e68298b915fb0fd6b8d9e74e576ba87caaf` |

Alle gebundenen Pythonquellen und JSON-Artefakte bleiben bytegleich, einschließlich
`__init__.py`, alter Analyse-CLI und neuer A-/B-CLI. Neue Integrationsmodule
liegen außerhalb beider Freezes. Keine neue Formel, Referenz, Quantile oder
Umbenennung eines alten Ergebnisses. Methodenprüfung kontrolliert die tatsächlichen
gebundenen Dateien, nicht nur eine übergebene Hashzeichenfolge.

Aktive/Checked-Hüllen v1/v2, Kontext v1 und Auswahlberichte v1/v2/v3 bleiben
ausschließlich 0.3. A-v1 und B-v1 bleiben ihre geschlossenen eigenständigen
Verzeichnisse und Formate. Fremdfelder, doppelte Schlüssel, nichtendliche Zahlen,
Boolwerte an Integerstellen und fremde Methoden werden abgewiesen. Vorhandene
defekte aktive Quellen stoppen; nur fehlende Sidecars erlauben den bestehenden
historischen 0.1-/0.2-/null-Fallback. Ein gültiger historischer Wert wird durch
einen neuen Produktionsstandard nicht ungültig.

## C-V01-02 · Neue gebundene 0.4-Hüllen

`picross-checked-difficulty-v3` und `picross-catalog-difficulty-v3` behalten
exakt die äußeren Feldmengen ihrer jeweiligen v2-Hülle aus SD-C1, einschließlich
`production_mode`, Quell-/Logikbindung, Adoption, Werkzeugidentität und Hash.
Sie erlauben ausschließlich 0.4. Größenlimit bleibt **96 KiB**, eingebettete
Bewertung **64 KiB**; keine Vergrößerung der alten Readerlimits.

`logic_binding` bleibt `{analysis_hash,matrix_hash}`. Für v3 bindet
`analysis_hash` das normalisierte `picross-sd2-input-v1`, für v1/v2 weiterhin
den alten Eingang. `matrix_hash` bindet die unveränderte Lösungsmatrix.
`current_source` bleibt `{id,runtime_revision,definition_sha256}`.

Die eingebettete Bewertung verwendet `picross-catalog-sd2-rating-v1` mit exakt
`format,method,method_hash,analysis_result_hash,source,result,rating_hash`.
`method` ist die Zeichenfolge `picross-difficulty-0.4`; `source` ist die exakte
ursprüngliche Runtime-Quellbindung aus dem A-Bericht (dieselben sieben Felder wie
im alten Bewertungsimport). `result` ist das unveränderte vollständige
`picross-sd2-rating-v1`-Ergebnis aus B. `rating_hash` bindet alle anderen Felder.
Die ursprüngliche Quelle wird bei Rebind niemals umgeschrieben.

`compact_analysis` hat exakt:
`result_hash,analysis_hash,trace_hash,profiles_hash,status,reason,
line_analysis_complete,line_fixpoint_confirmed,deduction_complete,r4,structure,
wave_count,new_singletons`.
Die ersten vier Werte sind SHA-256; `profiles_hash` bindet die vollständigen
geprüften drei Rohprofile, die im externen A-Bündel bleiben. `structure` ist
exakt das strukturbezogene Workloadobjekt aus SD2-A (Dimensionen, Farben,
Hinweissummen/-histogramm, kurze Blöcke, Farbwechsel, Abstände, geometrischer
Spielraum); es wird ohne Deduktionssuche aus der gebundenen Definition geprüft.
`wave_count` ist 0..80000, `new_singletons` 0..Zellzahl; solved verlangt alle
Zellen. Status, Abbruchgründe, Vollständigkeit und getrennte R4-Belege behalten
die A-Semantik. Notwendiges R4 verlangt stalled, bestätigten Linienfixpunkt und
frisch unabhängig geprüfte solved-Paar-/stalled-Basisbelege beim Import.

Die B-Bewertung wird strukturell und arithmetisch gegen ihren eingefrorenen
Vertrag geprüft: exakte Ergebnis-/Assessment-/Signalobjekte, reduzierte rationale
Zahlen, Beiträge, Score, Grenzen/Abstände, Stufe ohne Umfang und Umfangsbremse.
Neue rationale Zähler liegen in 0..10^100, Nenner in 1..10^100; Boolwerte
sind ausgeschlossen. Diese begrenzte Ganzzahlarithmetik verändert keine Note.
Vollständige Linienfälle nutzen die gespeicherten B-Signale, R4 den festen Anker.
Diese Datenprüfung ist ausdrücklich kein erneuter Beweis der Deduktion.
Nur der explizite Import prüft das komplette externe A-/B-Bündel frisch.
Unvollständige, widersprüchliche oder abgebrochene Ergebnisse dürfen Checked-
Arbeitsdaten sein, aber niemals aktive Ratings; ihre Übernahme erhält Altwerte.

Die neue Werkzeugidentität ist `picross-catalog-difficulty`, Version 2, mit
exakt den Hashes von `catalog_rating.py`, `catalog_analysis.py`,
`catalog_transaction.py`, `catalog_integration.py`, `sd2_catalog_rating.py` und
`catalog_method.py`. Historische Werkzeugversion 1 bleibt unverändert zulässig
in ihren alten Hüllen; kein Vergleich mit späteren lokalen Integrationsbytes.

Die neue äußere Arbeitsmappe enthält exakt `catalog-context.json` und `rating/`.
`rating/` ist das unveränderte geschlossene B-Bündel. Kontextformat
`picross-difficulty-context-v2` hat exakt
`format,production_mode,source,method,method_hash,context_hash`; Quelle und
Mode binden den tatsächlichen Runtime-Eingang, Methode/Hash ausschließlich 0.4.
Keine Zusatzdatei innerhalb von A oder B. Import vergleicht alle Eingangsbytes
vor/nach unabhängiger Prüfung und fordert Kontext, Quelle und Methode konsistent.
Mono verlangt eine Vordergrundfarbe; Farbe mit einer Farbe bleibt eigener Modus.

Metadaten-Rebind benötigt gleiche ID, normalisierte Logik, Matrix und Modus.
Nur `current_source` und der äußere Hash ändern sich; Bewertungsoriginal,
Analysehashes und Provenienz bleiben erhalten. Neue/geänderte Logik oder ein
Moduswechsel brauchen frische Analyse der aktiven Produktionsmethode. Ein
historischer Register-No-op kontrolliert weiterhin sämtliche Quellen und erhält
alle Bytes/Revisionen/mtime, ohne nachträglich ein Rating zu verlangen.

## C-V01-03 · Auswahlbericht und Runtime

Neue Auswahlberichte verwenden `picross-catalog-difficulty-report-v4`.
Äußere Felder entsprechen exakt v3. Jede Zeile ergänzt genau `assessment`:
bei vollständig bewerteter 0.4 das unveränderte B-Assessment mit drei Beiträgen,
Score, Stufe, Grenzen und Signalen; sonst null. Der Report prüft dessen geschlossene
Felder und eingefrorene Arithmetik; Übernahme bindet es zusätzlich exakt an das
Checked-Ergebnis. Markdown nennt Alt-/Neumethode und enthält die Teilwerte.
`result` ergänzt genau `method`
zu `selection,source_commit,method_hash,snapshot,sources,entries,distribution`.
Pro Bericht genau eine Zielmethode 0.3 oder 0.4 samt geprüftem Freeze; `old` darf
alle vier unterstützten Methoden/null enthalten, `proposed` nur die Zielmethode.
Ein rated-Eintrag hat `reason=null`; der vollständige B-Grund bleibt im Rating.
Quell-/Rating-/Checked-/Vorgängerhashes und Vorgängerrevision bleiben Pflicht.
16 MiB, 10000 eindeutige sortierte IDs, höchstens 80004 Quellen, Grund maximal
2048 Zeichen. Verteilung ist beobachtend, nie Kalibrierung. `operation` bleibt
außerhalb der Ergebnisidentität. Quellen umfassen den vollständigen AT-Snapshot
und den optionalen Produktionsstandard aus C-V01-04, auch dessen Abwesenheit.

`picross-runtime-registry-v5` hat dieselben exakten Felder wie v4: Top-Level
`format,categories,entries`, neun Felder je Eintrag. Es erlaubt zusätzlich 0.4
im exakt sechs Felder großen `difficulty`: `method,level,assessment_type,
confidence,plausible_range,r4_required`. 0.4 verlangt instrumented, medium,
`[level,level]`, L1..L5 und bei notwendigem R4 L5. Null bleibt neutral.
Alte Runtime-v2/v3/v4 bleiben exakt geschlossen und akzeptieren 0.4 nicht.
Neue normale Projektionen schreiben v5. Lesen gültiger Altprojektionen schreibt
nichts; v2/v3 bleiben nur ohne Added-Daten zulässig. Python und Godot prüfen
dieselbe Versions-/Methodenmatrix. Fünf Namen, Farben, Sortierung, Nullbehandlung
und Spoilergrenze bleiben unverändert; keine Scores, Profile oder Freitexte im
Runtimekatalog. Der reale Runtimekatalog wird in C nicht neu geschrieben.

## C-V01-04 · Explizite Aktivierung

Fehlendes `content/difficulty-method.json` bedeutet ausschließlich den gebundenen
Default 0.3. Vorhandene Datei ist autoritativ und darf nicht still ignoriert
werden. `picross-difficulty-default-v1` hat exakt
`format,revision,method,method_hash,previous_record_hash,activation_hash,record_hash`.
Revision 1..1000000; erster Vorgänger null, weitere ein SHA-256; Methode 0.3/0.4
mit gültigem Freeze. Der Default ist Werkzeug-/Produktionskontext, keine
Runtime-/Saveinformation und keine automatische Bestandsneubewertung.

`catalog_method plan` benötigt Checkout, erwartete bisherige Methode, Zielmethode,
exakten Zielmethodenhash und neuen externen Ausgabepfad. Es erzeugt
`picross-difficulty-activation-plan-v1` mit exakt
`format,expected,target,sources,result_hash`.
`expected` enthält `method,method_hash,record_hash,revision` (null und Revision 0
bei fehlender Quelle, sonst die vorhandene Revision 1..1000000),
`target` enthält `method,method_hash`, `sources` alle T/K-Dateihashes oder null.
`result_hash` bindet alle übrigen Felder. Limit 16 MiB/80004 Quellen.
Gleiche Ausgangs-/Zielmethode ist kein neuer Aktivierungsplan.
`catalog_method adopt --plan ...` prüft beide Freezes, vollständige Quellen,
Erwartung und Planhash vor Mutation; ausschließlich der Standardrecord ändert
sich. Wiederholung desselben Plans akzeptiert genau seine eigene Recordrevision,
Vorgängerbindung, exakt `expected.revision + 1` und sonst identische Quellen,
ohne Rewrite/Lock/mtime-Änderung. Damit genügt ein neu versiegelter Record mit
beliebiger höherer Revision auch bei gleichem Planhash nicht als Wiederholung.
Fremde Änderung oder zwischenzeitliche andere Aktivierung macht den Plan stale.

Neue Registrierung und echte Logik-/Modusänderung benötigen die aktive Methode.
Reine Metadatenänderung darf die gültige bisherige Methode rebindend erhalten.
Explizite Katalogbewertung darf unabhängig vom Produktionsdefault beide Methoden
vorbereiten/übernehmen. Bloßes Lesen, Sync, Cleanup, Recovery, Build, Start oder
CI aktiviert nichts. C prüft Aktivierung ausschließlich in synthetischen
Checkouts; C selbst beließ den realen Default durch Abwesenheit der Datei bei
**0.3**. Die anschließende reale Aktivierung gehört ausschließlich D-F01/T01.

## C-V01-05 · Gemeinsame Transaktion und Altjournalmatrix

Neue Generationen: registration-v6, content-update-v5, catalog-metadata-v3,
reveal-adoption-v2 und difficulty-activation-journal-v1. Die acht äußeren Felder
bleiben `format,operation,old,new,retained,additions,report_run,replacements`.
Metadata umfasst adoption/sync/added-adoption; Aktivierung ausschließlich
method-activation. Neue T-Menge ergänzt `content/difficulty-method.json` zu
allen bisherigen AT-Textquellen. K, Reportziele und exakte Deltamengen bleiben.
Aktivierung darf nur diese eine Textquelle ändern, ohne Runtime-Neuprojektion.
Reine Bildadoption erhält weiterhin die genaue gültige Runtimefassung.
Sonstige neue Schreiboperationen projizieren v5. Ratings, Added, Bilder,
Originalbelege und Saves außerhalb ihres ausdrücklich erlaubten Deltas bleiben.

| Journal | Zulassung und Recovery |
| --- | --- |
| registration-v1 | Weiter gesperrt; keine automatische Reparatur. |
| registration-v2/update-v1 | Alter geschlossener Vertrag; keine ungebundenen Ratings/Added/AT/Default. |
| registration-v3/update-v2/difficulty-adoption-v1 | Alte sieben Felder, keine Added/AT/Default; alte Runtime-v3. |
| registration-v4/update-v3/metadata-v1 | Alte sieben Felder mit Added, ohne AT/Default; alte Runtime-v4 samt dokumentierten v2/v3-Ausgängen. |
| registration-v5/update-v4/metadata-v2/reveal-v1 | Alte acht AT-Felder und Mengen, kein Default/0.4/Runtime-v5; bisheriger vollständiger AT-Prüfweg. |
| Neue C-Generationen | Acht Felder, vollständiges T einschließlich Default, gemischte gültige Ratings; normale Zielprojektion v5. |

Alte Journale werden nicht umetikettiert. Ihre Recovery endet nach bisherigem
Vertrag direkt in gültiger Runtime-v4; alte Reveal-Recovery behält die Runtime
bytegleich. Neue Recovery stellt die vollständig gültige alte Runtime bytegleich
wieder her; nur ein mit stale-Projektion gestarteter Sync erhält eine abgeleitete
gültige v5-Projektion. Erneutes Recovery akzeptiert ausschließlich gebundene eigene
Alt-/Neu-/Recoverybytes. Jede ungebundene neue Quelle stoppt vor Mutation und
vor scheinbarem No-op. Keine Analyse, Solver oder Zertifizierungswiederholung.

Vorprüfung, vollständiges dauerhaftes Journal, no-replace-Lock, Quellen-/Namensraum-
Guards vor jedem Schreibschritt, gesicherte Binäraltbytes, Runtime zuletzt,
Gesamtprüfung vor Lockentfernung und fremde Bytes erhaltender Rollback folgen
AT-P01-D05/D06. Normale Journale bleiben 24 MiB; Reveal-v1/v2 128 MiB, Bilder
32 MiB/Seite, zusammen maximal 96 MiB dekodiert. JSON-Tiefe maximal 32.
Keine neue unbegrenzte Lesestelle oder Ausweitung alter Limits.

Added-Plan-v3 und Reveal-Plan-v2 übernehmen ausschließlich die neue vollständige
Quellen-/Journalgeneration; ihre sonstigen Felder und Fachregeln bleiben gleich.
Alte Added-v1/v2, Reveal-v1 und SD-Berichte v1/v2/v3 sind nur auf einem passenden
Altstand ohne ungebundene Default-/0.4-/v5-Quellen übernehmbar. Historische
dauerhafte Berichte bleiben lesbar. Wiederholung verlangt sämtliche ursprünglichen
Quellen oder das exakt rekonstruierbare eigene Delta; keine stillen Upgrades.

## C-V01-06 · CLI, Produktion und Prüfung

`catalog_analysis analyze/preview/preview-checked --method` wählt explizit 0.3
oder 0.4; ohne Option bleibt 0.3. Import dispatcht allein nach der geschlossenen
Kontexthülle; alte Bundles bleiben alt. Ressourcenflags und getrennte Analyse-/
Prüfbudgets bleiben; 0.4 verwendet den unveränderten SD2-Budgettyp.
`candidate → analyze/import → rebind → target_adapter plan/register/update`
ist der Produktionsweg: vorläufige Definition aus freigegebener Matrix,
explizite Methode/Mode, frische Prüfung, dann Rebind auf den fertigen Export.
`--difficulty` und `--rebind-difficulty` bleiben an den Integrationsbefehlen.
Plan/Adopt analysieren niemals. Keine verborgenen Analyseläufe in Registrierung,
Sync, Cleanup, Recovery, Export/Build oder Spielstart. Bestehende explizite
ZA-1-Produktionszertifizierung bleibt getrennt erhalten.

Exit 0: Erfolg/Plan/No-op; 2: Daten-/Vertrags-/Stalefehler; 4: Abbruch/Ressource.
Fehlgeschlagene Einzelanalyse bleibt offen mit Grund; keine scheinbare Nullnote.
Arbeitsdateien liegen außerhalb von Runtime und dauerhaften Ratingquellen.
Keine echten Katalogfälle oder daraus abgeleiteten Testkopien.

SD2-C-T01 bindet feste synthetische Positiv-/Negativfälle an C-A01..C-A06:
beide Methoden/mixed/null, Mono und Einfarb-Color, Quelle/Mode/Rebind/Logikwechsel,
R4/offene Versuche, alle Writer samt Cleanup, Stale/Fremdquellen/No-op-mtime,
Journalgenerationen/Unterbrechung/wiederholtes Recovery, explizite Aktivierung,
Python-/Godot-Zulassung und isolierte bestehende Saves. Beide Freezes werden
zusätzlich gegen die Basis bytegeprüft. Neue Fälle sind unabhängig synthetisch.
Der Gesamtdiff wählt docs, production, alle sieben nativen Gruppen, alle fünf
Chromiumgruppen, delivery und ci-required; Preflight nur nach tatsächlicher
Auswahl. Kein Firefox, keine Verkürzung der Selektoren. Lokale Adaptertests
verwenden isoliert Python 3.11+ und exakt Pillow 12.3.0. T01 dokumentiert Head,
Basis, CI-Test-Merge, Run/Jobs und einen getrennten Selbstreview. Das separate
qualifizierte SD2-C-R01 war ein eigenes Gate vor Merge und ist über PR #410
abgeschlossen. Die dortige Eigentümerausnahme zum fehlenden Gesamt-CI-/Chromium-Gate
gilt nur für #410. C beauftragte weder Deployment noch #406.
