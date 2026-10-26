# SD2-D-F01/T01 · Vollständige Übernahme und Aktivierung von 0.4

Stand: 26.10.2026, [#406](https://github.com/venomenon328/picross/issues/406),
[Draft-PR #411](https://github.com/venomenon328/picross/pull/411), Branch
`chore/406-sd2-bestandsumstellung`, Ziel `main`. Finales separates R01 und
Merge bleiben offen.

## Auftrag und gebundene Eingänge

Der Eigentümer hat nach [OM01](SD2_D_OM_FOLLOWUP.md) ausdrücklich erklärt:
**„Damit sind nun alle Vorschläge akzeptiert, fahre bitte fort.“** Damit sind
alle 45 Vorschläge einschließlich Om fachlich abgenommen. Der frühere
ausdrückliche Verzicht auf separates SD2-D-VR01 bleibt wirksam; dieses Review
wurde nicht durchgeführt und wird nicht als bestanden behauptet.

Der Folgeauftrag umfasst die vollständige Übernahme, ausdrückliche Aktivierung
und beide echten unmittelbaren Wiederholungs-No-ops. Er erlaubt keine Änderung
der Methodik, Definitionen, Identitäten, Revisionen der Rätsel, Bilder, Saves,
historischen Produktions- oder Freigabebelege. Kein neuer Analyse-/Paarlauf,
keine Teilumstellung, kein Merge, Deployment oder Issue-Schließen.

| Bindung | Wert |
| --- | --- |
| Start-/Abnahmehead | `44a70dc491dc37d78f98382f957ee88205f26743` |
| Vor Start erneut bestätigte Basis und Werkzeugstand | `4e23e644f3457362e02b75f78fdb575a99265494` |
| Übernommene Run-ID | `sd2-d-20261026-om01` |
| Abgenommener Ergebnishash | `a0d1908573a253978273736e86d66d32fa027068480654f1837d5cd570a46c2a` |
| 0.3-Freeze, unverändert | `8f7efa0d5ac76a1bd73fbae3618fec18dba28cf704887188eba2fcf020b9df79` |
| 0.4-Freeze, unverändert | `5508f0742aa858a6adc31aa621433e68298b915fb0fd6b8d9e74e576ba87caaf` |
| Externe Vorschau | `E:/Zeuch/Coding/picross-sd2d-evidence/sd2-d-20261026-om01/preview` |
| Neuer F01-Arbeitsroot | `E:/Zeuch/Coding/picross-sd2d-evidence/sd2-d-20261026-f01` |

Vor Mutation wurden alle 322 T/K-Quellenbindungen, die Bytes/Hashes/mtimes der
302 vorhandenen Dateien und die Namensräume gegen die ursprüngliche Bindung
geprüft. Beide Freezes stimmen. OM01- und V01-Arbeitsmanifeste und das
vollständige OM01-Archiv sind unverändert. Die 45 geprüften Eingänge und die
Vorschau bleiben im ursprünglichen geschlossenen Arbeitsverzeichnis.

## Kontrollierte Reihenfolge und tatsächliches Delta

Die vorhandenen Werkzeuge führen den [Integrationsvertrag](SD2_INTEGRATION.md)
und den [gemeinsamen Transaktionsweg](SD_CATALOG.md) unverändert aus:

1. `catalog_analysis adopt` auf der abgenommenen vollständigen OM01-Vorschau.
   45 aktive Ratingdateien wechseln von 0.3 auf 0.4, jeweils Revision 1→2 mit
   korrekter Vorgängerbindung. Die beiden Dauerberichte erhalten dieselbe
   Ergebnisidentität und lediglich `operation.phase=adopted`. Die Runtime
   wechselt von v4 auf v5 und erhält ausschließlich die neue Difficultyprojektion.
2. Derselbe Adopt unmittelbar erneut, vor jeder Defaultänderung: `no-op`,
   keine Änderung von Bytes, Hashes, Dateigrößen, mtimes, Revisionen oder
   Namensräumen. Keine nachträglich fremde Defaultquelle im Rating-No-op.
3. Erst danach ein frischer `catalog_method plan`, erwartete Methode 0.3,
   erwartete Revision 0/fehlender Record, Ziel 0.4 mit exaktem Freeze. Vor
   Mutation werden seine vollständigen Quellen und die reine Aktivierungswirkung
   über den bestehenden lesenden Planweg kontrolliert.
4. `catalog_method adopt` schreibt ausschließlich
   `content/difficulty-method.json`, Revision 1. Ratings und Runtime werden
   durch die Aktivierung nicht erneut geschrieben.
5. Derselbe Aktivierungsplan unmittelbar erneut: `no-op`, vollständige
   Byte-/Hash-/mtime-/Namensrauminvarianz. Der alte Ratingplan wird nach der
   Aktivierung nicht erneut angewendet; seine Defaultbindung wäre dann stale.

Das Datendelta umfasst **49 Pfade**: 45 vorhandene Ratings, vorhandene Runtime,
zwei neue Dauerberichte und den neuen Defaultrecord. 46 vorhandene Dateien
ändern sich, drei werden neu angelegt. Alle anderen 256 vorhandenen gebundenen
Quellen bleiben einschließlich ihrer mtimes erhalten. Die neue Quellenbindung
enthält 324 Pfade, davon 305 vorhanden. Die vorher bereits gebundene Abwesenheit
des Defaults wird durch seinen Record ersetzt; nur die zwei Berichtpfade kommen
zur Pfadmenge hinzu.

Aktive Verteilung L1/L2/L3/L4/L5: **4/9/6/23/3**, alle 45 gültig. Neue
Produktion und echte Logik-/Modusänderungen benötigen nun Methode 0.4.
Historische gültige Werte bleiben lesbar; reine Metadaten-Rebinds folgen
weiterhin dem ursprünglichen Methodenvertrag. Die explizite Analyse-CLI ohne
`--method` behält ihren technischen Default 0.3; das ist vom autoritativen
Produktionsdefault zu unterscheiden.

Die Dauerberichte liegen als [JSON](../content/difficulty/reports/sd2-d-20261026-om01/report.json)
und [lesbare Ableitung](../content/difficulty/reports/sd2-d-20261026-om01/report.md)
vor. Der [Delta-/Belegindex](evidence/sd2-d-f01/WORK_EVIDENCE.md) bindet die
konkreten Aufrufe, Ergebnisse, Aktivierungsidentität und jeden Vor-/Nachstand.
Die ursprünglichen V01-/OM01-Berichte und Beweisdateien bleiben historische
Originale, keine rückwirkend umgeschriebenen Übernahmeberichte.

Kein Journal oder Temprest bleibt zurück. Es gab keine Fehlerinjektion und
keinen Recoverylauf am echten Bestand. Die Transaktion prüft vor Mutation beide
vollständigen Zustände, erhält Fremdbytes, publiziert Runtime zuletzt und entfernt
den Lock erst nach erfolgreicher Abschlussprüfung. Bei einer Unterbrechung gilt
der bestehende Recoveryvertrag; eine abgeschlossene Übernahme wird nicht durch
Missbrauch eines alten Journals rückgängig gemacht.

## Technische Prüfung und getrenntes Selbstreview

Ausführung und Selbstreview sind getrennte Schritte. Das Audit liest alle
Vor-/Nachinventare und den tatsächlichen Endstand, kontrolliert beide No-ops,
die exakten 49 Datenpfade, alle 45 Vorgänger-/Ergebnis-/Quellbindungen,
Ratingrevisionen 2, Defaultrevision 1, beide Freezes, unveränderte Altbelege und
die dauerhafte Berichtsableitung. Die Runtime wird feldweise geprüft: nur
Format v4→v5 und `difficulty` dürfen sich ändern; Kategorien, Reihenfolge,
IDs, Slots und alle übrigen Eintragsfelder bleiben gleich. Keine neue
Deduktionssuche oder Wiederholung des Bestandslaufs im Audit.

Ergebnis und Hashbindung des Audits stehen im Belegindex. Das ist ein
Selbstreview, kein unabhängiges SD2-D-R01. Die synthetischen C-Regressionen
bleiben der allgemeine Integrations-/Recoveryprüfweg; reale Katalogdaten werden
nicht in neue Tests kopiert oder als CI-Solvereingänge verwendet.

## CI-Ausführung unter der ausdrücklichen Web-Grenze

`content/difficulty-method.json` wählt nach dem unveränderten Selektor breite
Prüfungen aus. Die Nutzeranweisung **„Der Web-Job in der CI wird nicht
ausgeführt“** bleibt wirksam. Deshalb ergänzt
`.github/workflows/ci-chromium.yml` ausschließlich am Web-Job die Bedingung
`github.event.pull_request.number != 411`. Andere PRs und die Bedingungen aller
anderen Jobs bleiben erhalten. Es gibt keine globale Actions-Sperre, keine
Änderung des Selektors, der Browsergruppen oder des Ergebnisgates.

Der Workflowdiff wählt zusätzlich Preflight; der vollständige Diff verlangt
`docs`, `production`, `product`, `preflight`, `web`, `delivery`, alle sieben
nativen Gruppen und alle fünf Chromiumgruppen. Nur Web wird für diesen PR
bewusst nicht ausgeführt. Das unveränderte `ci-required` muss den ausgewählten,
aber übersprungenen Web-Nachweis als fehlend ablehnen; **kein vollständiger
grüner CI-Pass und keine stillschweigende Gesamtgate-Ausnahme**.

Die bestehende synthetische Schedulerprüfung wurde auf die exakte eng begrenzte
Bedingung angepasst. Eine zusätzliche Gate-Gegenprobe bestätigt: Die
Aktivierungsdatei wählt Web; bei sonst erfolgreichen ausgewählten Jobs darf
`web=skipped` keinen vollständigen Pass ergeben. Der lokale gezielte CI-A-Lauf
liefert 11 Fälle, `OK (skipped=1)`; die Linux-Shellprobe ist unter Windows
regulär nicht ausführbar und wird in Remote-CI geprüft.

Der tatsächlich geprüfte Head, Basis, Test-Merge, Run/Jobs, Ergebnisse und
verbleibende Lücken werden in PR #411 und #406 festgehalten. Ältere grüne
V01-/OM01-Läufe gelten ausschließlich für ihre damaligen Heads. Die
eigenständige CI-Zustellungsreferenz arbeitet isoliert über Loopback; sie ist
kein Live-Deployment und kein Browsernachweis.

## Akzeptanz und verbleibende Schritte

| Kriterium / Gate | Stand |
| --- | --- |
| D01 | Alle 45 gebundenen IDs geprüft und gültig übernommen. |
| D02 | Vollständige Vergleichs-/Plausibilitätsberichte, alle Vorschläge vom Eigentümer akzeptiert; VR01 ausdrücklich erlassen. Modellschätzung und menschliche Beobachtung bleiben unterschieden. |
| D03 | Vollständige Ratingübernahme und explizite Aktivierung auf dem Arbeitsbranch umgesetzt. Noch keine Main-Integration. |
| D04 | Genau 49 erlaubte Datenpfade; sonst unveränderte Definitionen, Bild-/Added-/Kategorie-/Freigabequellen und beide Freezes. CI-Sperre und Statusdokumentation sind separat ausgewiesen. |
| D05 | Beide unmittelbaren Wiederholungen als echte Datei-/mtime-No-ops nachgewiesen. |
| D06 | Technische Quellen-/Runzuordnung und Selbstreview geliefert; vollständiges CI-Gate und separates finales SD2-D-R01 bleiben offen. |
| Merge / Deployment | Kein Auftrag, nicht ausgeführt; Issue bleibt offen und PR bleibt Draft. |

F01/T01 ist eine technische Datenlieferung. Der VR01-Verzicht umfasst weder
das finale Daten-/Integrationsreview noch eine eigene Mergefreigabe oder die
Abnahme fehlender CI-Nachweise.
