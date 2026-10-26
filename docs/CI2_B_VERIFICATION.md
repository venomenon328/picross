# CI2-B · Fachgruppen, Fixtures und technische Nachweise

26.10.2026 · [#414](https://github.com/venomenon328/picross/issues/414), einschließlich
Umsetzungsvorbereitung V1 · [Draft-PR #420](https://github.com/venomenon328/picross/pull/420).
Basis: `main@94e3ea7d9674babbdcd6bde6251e233191fd096f`, integriertes CI2-A / PR #419.
Finaler Head, Test-Merge, Run, tatsächliche Prüfergebnisse, Vorher-/Nachherwerte
und das getrennte vollständige Selbstreview stehen im PR. Diese Zuordnung ersetzt
weder fehlende Ergebnisse noch das separate qualifizierte CI2-B-R01 vor Merge.
Kein Browserauftrag, Merge, Deployment oder Release.

## Auswahl, Ausführung und Ergebnis

[production_contract.py](../tools/production_contract.py) ist die gemeinsame
Zuordnung für Selektor, Scheduler, Runner und Gate. Jedes aktive Fachtestmodul
hat genau eine Gruppe: Solver/Analyse (`solver`), Import/Bilder (`images`),
Adapter (`adapter`) oder Katalog/Transaktionen (`catalog`). Die vollständige
aktuelle Modulliste steht dort ausführbar, ohne zweite gepflegte Testliste.
362 Fachtests ersetzen die 368 der Basis: sechs historische RP4/RP5-Tests
entfallen, die eigenständige Aufrufzählungsproduktion wird in eine bereits
erforderliche echte Integration aufgenommen; eine Fixtureisolationsprobe kommt hinzu.
Die 13 entfernten BP-Tests gehörten zum Werkzeugpfad, nicht zu diesen 368.

Die geprüfte Quellenzuordnung berücksichtigt transitive tatsächliche Konsumenten,
auch Funktionsimporte, CLI-Module und importierte Testfixtures. Rechenkerne können
deshalb mehrere Gruppen wählen. Ein kleiner CLI-/Testmoduldiff wählt nur seine
Konsumenten; gemeinsame oder unbekannte Wirkung wählt die notwendige Vereinigung.
Neue Testmodule und abweichende Importabhängigkeiten lassen den schnellen
Werkzeugcheck scheitern, bis ihre Zuordnung ausdrücklich nachgeführt ist.
Native Gruppen, Preflight und Zustellung aus A bleiben unabhängig erhalten.

Die sechs festen unabhängigen Solver-/Verifier-Referenzen gehören zu `solver`,
der feste synthetische Vierer-ZA-1-Durchstich zu `adapter`. Gruppen ohne diesen
Bezug führen keine dieser Integrationen aus. Kein Test liest den realen Fundus.
Die kurze automatische Mainroute wiederholt keine Fachgruppe.

[production_ci.py](../tools/production_ci.py) startet die ausgewählten Tests
und Integrationen im bestehenden Fachjob. `production_groups` wird kanonisch
als JSON-Array transportiert, einschließlich `[]`; `production_expected` bindet
die Modul-/Integrationsmenge. Leere, doppelte und unbekannte Runnergruppen sind
Fehler. Die tatsächliche Unittest-Discovery muss exakt zu den aktuellen
Quelldeklarationen passen. Das Gate importiert keine Fachtests: Es liest deren
Deklarationen aus demselben Checkout und prüft jede erwartete Test-ID genau einmal.

[production_results.py](../tools/production_results.py) verlangt erfolgreiche
Test-/Integrationsresultate und sämtliche nichtleeren gebundenen Dateien.
Fehlende/zusätzliche/doppelte Tests, übersprungene Fälle, fehlgeschlagene Fixtures,
Abbruch, falsche Gruppen oder manipulierte Dateien werden abgewiesen.
Head, Basis, Checkout und Run müssen passen; Auswahlversuch ≤ Fachversuch ≤
Gateversuch. Fremde oder spätere Resultate sind kein Erfolg. Auswahl-/Resultformat
ist v6. Der vorhandene Artefaktweg erhält die Versuchsnummer; Aufbewahrung sieben
Tage. Mutable synthetische ZA-1-Checkouts werden nicht hochgeladen.

## Günstigste passende Prüfebenen

| Änderung | Erhaltene Aussage und Ebene |
| --- | --- |
| `test_content_update` | Einmal drei echte Exporte und zwei Registrierungen pro Klasse; danach getrennte vollständige Kopien aller Eingänge/Exporte/Checkouts. Raster weiterhin 5→8 Farben, eigener unveränderter Nachbar und synthetische Fremdbytes; 9×2 statt 10×4 genügt für alle acht Farben. Plan, echter Update, unabhängiges Staging, historisches Paket, Revisionen, No-op, eigene/fremde Recovery bleiben. |
| Lokale Updateablehnungen | Stale-Hash, gleiche Revision, Slot/Kategorie/Reveal und belegte Paketrevision am Planer hinter der bereits unabhängig geprüften Exportgrenze. Kleine geänderte Manifestwerte ersetzen fünf Exportneuproduktionen und die wiederholte vollständige Quellenprüfung für sechs lokale Varianten. Quellen-/Proof-/Freigabevalidierung bleibt unverändert in den Adaptertests. |
| Interne Exportprüfungen | Die bereits notwendige echte Happy-Path-Integration kontrolliert Eingangs- und unabhängigen Stagingcheck. Keine zusätzliche Vollproduktion allein für Aufrufzahlen. |
| Technische Fehlerphasen | Sämtliche Veröffentlichungs-/Recoveryphasen einschließlich Binärersatz, Lock, Temps, Fremdbytes und wiederholter Unterbrechung einmal am gemeinsamen Kern in `test_reveal_recovery`. Pro Rastereinstieg bleibt ein echter gewöhnlicher Rollback und ein echter Abbruch nach Runtimepublikation; Paketneuanlagen-/Fremdquellenschutz bleiben separat. |
| `test_sd2_catalog` | `UpdateTests` übernimmt ausdrücklich den neuen isolierten Klassenaufbau; derselbe echte gemischte 0.3-/0.4-Update-/Aktivierungs-/Recoveryfall bleibt mit kleineren Quellen erhalten. `CatalogTests` kopiert für Metadatenfälle einen gültigen kompakten Grundstand; der echte Cleanupfall erhält weiterhin eine eigene Kopie der vollständigen Export-/Registrierungsbasis. |
| `test_catalog_review` | Vier unveränderliche Exporte für zwei Modi/Revisionen und zwei echte Registrierungsgrundstände einmal pro Klasse. Jede Testinstanz bekommt eigene Quellen-/Export-/Checkoutwurzeln; alle Mode-/Rebind-/Stale-/Namespace-/No-op-/Altformatgegenproben bleiben. |
| Journal-/Limit-/Dispatchdaten | Drei lokale Binär-/Dispatchprüfungen in eigener `JournalTests`-Klasse ohne Export-/Registrierungsvoraussetzung. Kleine feste Registryeinträge genügen; echte 32-MiB-Bildseiten und sämtliche Readerlimits bleiben. |
| Technischer Recoverygrundstand | Geprüfte synthetische kompakte Receipts reduzieren die mitgebundene Produktionsdateimenge auch im Mehr-ID-Fall und beim unabhängigen Updatenachbarn. Echte Export-/Register-/Bildintegration bleibt bei den fachlichen Einstiegen. Altjournale behalten ihre geschlossenen Generationen und synthetischen Eingänge. |

Kopiert werden Eingabebytes, keine bestandenen Tests. Die neue Isolationsgegenprobe
mutiert Checkout, Export und fremde Speicherbytes in zwei getrennten Instanzen in
beiden Richtungen und kontrolliert die unveränderte Grundfixture. Vorhandene
Stale-/Fremdbyte-/No-op-/mtime-/Recoverytests bleiben wirksam. Der bestehende
prozesslokale Bewertungseingangscache von `difficulty_for_export()` wurde nicht
neu eingeführt und wird nicht als neue Beschleunigungsursache ausgegeben.
Methodenfreezes, Produktdaten, Saveformate und produktiver Code bleiben bytegleich.

## Messung und T01

Der bestehende Fachbericht enthält jetzt `tests.json`, `tests.log` und
`production-result.json`. Gemessen werden je Test `setUp`, Testkörper, `tearDown`
und Cleanups; Modulimport, Modul-/Klassenaufbau und deren Abbau separat und in
der Gruppensumme. Die langsamsten zehn Tests, Gruppenzeiten, tatsächlich
ausgeführten Integrationen sowie Elternprozessaufrufe von Import, Export,
Exportprüfung, Registrierung und Checkoutprüfung stehen im Bericht und der
Actions-Zusammenfassung. Unterprozesse haben eigene Integrationslogs und Zeiten;
sie sind keine zusätzlichen Elternprozessaufrufe. Neue teure Fälle müssen ihren
Zweck und die günstigste passende Ebene erklären; hier kommt nur eine kurze
Kopier-/Isolationsprobe hinzu. Testmengen wurden nicht nach Methodenzahl halbiert.

Die historische Ubuntu-Baseline aus #414 bindet Python 3.12.3/Pillow 12.3.0,
368 erfolgreiche Tests in 1.466,505 Sekunden an den A-Head und dessen tatsächlichen
Test-Merge. Die zusätzliche lokale Ausgangsmessung auf unveränderten B-Fachquellen
der Basis umfasst sechs gezielte Fälle: 605,577 Sekunden einschließlich Aufbau,
15 Exporte, neun Registrierungen, 69 Export- und 93 Checkoutprüfungen. Umgebung:
Windows 11, Python 3.13.14, Pillow 12.3.0, frischer Prozess, bestehender Ratingcache.
Dies sind Ausgangswerte; Nachherwerte und ihre Vergleichsgrenzen stehen im PR.
Ein konsolidierter Fall hat dort ausdrücklich eine andere Test-ID; Parallelität,
Runner, Cache, Suitezeit, Jobdauer und kritischer CI-Pfad werden unterschieden.
Keine ungemessene Erreichung des Fünf-/Zehnminutenziels.

Lokaler schneller Werkzeuglauf: 219 Tests in 42,742 Sekunden erfolgreich;
drei plattformbedingte Proben übersprungen. Der echte Linux-PR-Lauf liefert ihre
maßgebliche Ausführung und die finalen Pflichtresultate. Die sechs neuen
Werkzeugtests prüfen Auswahl/Importzuordnung, kanonischen Transport,
unvollständige/gefälschte Ergebnis-/Quellen-/Versuchsbindung, Dateiintegrität und
die tatsächliche Unittest-Zeitgrenze mit Aufbau/Cleanup. Dokumentvalidator,
vollständiger Diffcheck, zusätzliche gezielte Reihenfolge-/Isolationsproben und
finale CI-Ergebnisse werden im PR zugeordnet. Kein zweiter ritualisierter Vollauf.

CI2-B-T01 ist erst mit den dort dokumentierten tatsächlichen Resultaten erfüllt.
`docs`, `ci-required` und alle ausgewählten Nichtbrowserjobs müssen am finalen
Head/Test-Merge erfolgreich sein. Überschreitungen bleiben Optimierungsbefunde.
Das getrennte Selbstreview ist keine unabhängige Zweitprüfung; CI2-B-R01 bleibt
vor Merge ein eigenes qualifiziertes Gate. C/D/E werden dadurch nicht abgenommen.

## Historische Stilllegung nach aktuellem Leserabgleich

Am Umsetzungsstand wurden sämtliche Repositoryleser mit `rg` erneut geprüft.
Die BP-Hersteller lesen nur einander und ihre folgenden Tests; kein aktiver
Spiel-/Ressourcenpfad importiert sie. RP4 `inspect_trial` und RP5 `unpack_archive`
werden ausschließlich von den benannten Tests gelesen; ihre alten CLIs waren
bereits entfernt. Die vollständigen Quellen und damaligen Ergebnisse bleiben
im [unveränderlichen Vorgänger](https://github.com/venomenon328/picross/tree/94e3ea7d9674babbdcd6bde6251e233191fd096f).
Keine neue Galerie, Archivkopie oder Historienumschreibung.

| Entfallender Test an der Basis | Exklusiver Helfer |
| --- | --- |
| `tools/book_inventory/test_artwork.py::ArtworkHelpers.test_source_over_keeps_transparent_and_opaque_ui` | `tools/book_inventory/artwork.py` |
| `tools/book_inventory/test_artwork.py::ArtworkHelpers.test_proportional_half_size_uses_pixel_centres` | `tools/book_inventory/artwork.py` |
| `tools/book_inventory/test_artwork.py::ArtworkHelpers.test_rejects_stretch_and_ui_resize` | `tools/book_inventory/artwork.py` |
| `tools/book_inventory/test_composition.py::CompositionHelpers.test_reject_changed_clue` | `tools/book_inventory/composition.py` |
| `tools/book_inventory/test_composition.py::CompositionHelpers.test_reject_solution_instead_of_own_miniature` | `tools/book_inventory/composition.py` |
| `tools/book_inventory/test_composition.py::CompositionHelpers.test_reject_shifted_hit_and_wrong_navigation` | `tools/book_inventory/composition.py` |
| `tools/book_inventory/test_composition.py::CompositionHelpers.test_reject_wrong_layer_pixels_and_alpha` | `tools/book_inventory/composition.py` |
| `tools/book_inventory/test_composition.py::CompositionHelpers.test_actual_substrate_minimum_not_average` | `tools/book_inventory/composition.py` |
| `tools/book_inventory/test_production.py::ProductionHelpers.test_fold_cannot_enter_working_page` | `tools/book_inventory/production.py` |
| `tools/book_inventory/test_production.py::ProductionHelpers.test_720_status_must_stay_inside_page` | `tools/book_inventory/production.py` |
| `tools/book_inventory/test_production.py::ProductionHelpers.test_navigation_cannot_overlay_clues` | `tools/book_inventory/production.py` |
| `tools/book_inventory/test_production.py::ProductionHelpers.test_actual_svg_must_name_correct_target` | `tools/book_inventory/production.py` |
| `tools/book_inventory/test_production.py::ProductionHelpers.test_mask_must_not_protect_wrong_crop` | `tools/book_inventory/production.py` |
| `tests/puzzle_production/test_rp4.py::ResultTests.test_actual_solved_proof_and_matrix_are_accepted` | `rp4.inspect_trial` |
| `tests/puzzle_production/test_rp4.py::ResultTests.test_stalled_does_not_become_a_certified_puzzle` | `rp4.inspect_trial` |
| `tests/puzzle_production/test_rp4.py::ResultTests.test_forged_certification_rejected_even_after_all_file_rebindings` | `rp4.inspect_trial` |
| `tests/puzzle_production/test_rp4.py::ResultTests.test_successful_replay_does_not_overwrite_original_verification_abort` | `rp4.inspect_trial` |
| `tests/puzzle_production/test_rp4.py::ResultTests.test_wrong_source_and_unequal_budget_rejected` | `rp4.inspect_trial` |
| `tests/puzzle_production/test_rp5.py::RP5Tests.test_archive_bytes_member_hashes_and_path_limits` | `rp5.unpack_archive` |

Aktive Buch-/Font-/Lizenzdaten bleiben über `tools/z2_resources.py` erhalten.
RP6 und `p1_export.export_p1` samt aktuellen Größen-/Codec-/Formatgrenzen bleiben;
Archiveingangsvalidierung erfolgt weiter durch `authoring_package.open_package()`
und Adaptertests. Der bereits in A entfernte PR411-Sondertest zählt nicht zu B.
BP-ARCHIVE und lokale Herstellerlinks wurden nachgeführt; historische
Prüfergebnisse wurden nicht umgeschrieben. Großer Bestandsabbau gehört weiterhin E.
