# ZA-1: Prüfzuordnung und Referenzeingang

Scope: [#74](https://github.com/venomenon328/picross/issues/74),
[Adaptervertrag](ZA1_ADAPTER.md), Arbeitsbasis
`039f59d9a94ad6c2fea32a900d03d1d3b8a7df4c` (aktueller main beim Start).
Commit/Head, Basis, tatsächlicher CI-Test-Merge und Run werden im Draft-PR gebunden.
Diese Zuordnung ist keine unabhängige Zweitprüfung oder Inhaltsabnahme.

## Original und reproduzierbares Derivat

Vor Verwendung wurde das bereitgestellte Original-ZIP gehasht:

| Bindung | SHA-256 |
| --- | --- |
| Original-ZIP | `7013d5b29a0dda5ad9a5047730a1e71b4d06596aa284ee8a3cbdad9184dc23f1` |
| Originalhandoff | `8411cb079ac321b975cc51c01aa47f935fe492aee569060046aee917d594c06c` |
| Originalinventar | `57af3c9c896edfbccfeef50aff235d467aef7fc3acb345a7c626d8282ee52d07` |
| Ausgewählte Matrix | `2691fe2f52cf330e9500779160dd90a8446c1c7d90f174b75fdbc1df5aa81f09` |
| Ausgewählte Logik | `62a584d7b1179a30f914ec5b8decb56a5fef532b8a85422e2147ad49dbd9963e` |

Das Original enthält 182 Dateien, 36.827.537 entpackte Bytes, ZIP 33.631.879 Bytes.
Der [gebundene Originalbericht](evidence/za1/original-input.json) führt die Prüfung
am Implementierungscommit und den tatsächlich blockierten Exportversuch.
Die frische Eingangsprüfung las das vollständige Inventar, rekonstruierte den
Import und prüfte den vollständigen Reparaturverlauf mit drei Kandidaten.
Auswahl `candidate-002`, Referenz `area-128`, Endproof solved/certified,
297 Schritte. Technische Prüfung erfolgreich; einzig offene Endfreigabe bleibt
`final_editorial: missing bound human final approval`. Export bleibt blockiert,
kein neuer echter Katalogeintrag und keine Änderung der Eingangsbytes.

Für CI liegt [garlic-r03-reference.zip](../tests/puzzle_production/fixtures/garlic-r03-reference.zip)
als etwa 5,1-MB-Prüfderivat vor. Es enthält 69 benötigte Originaldateien plus
Ableitungsmanifest (6.614.689 entpackte Bytes), einschließlich unverändertem
Originalhandoff und Inventar, aller Importvarianten, vollständiger Reparatur,
beider Bilder/Freigaben/Provenienzen und referenzierter Belege. Code-, Galerie-
und Altpaketkopien werden ausgelassen. Das eigene Derivat bindet Original-ZIP,
Inventar/Handoff und jede enthaltene Originaldatei, deutet das Inventar nicht um.
CI benötigt keinen privaten Dateidienst. Original-ZIP-Prüfung und Derivatreplay
sind getrennte Belege; das Derivat ersetzt keinen vollständigen ZIP-Hashnachweis.

## Automatische Abdeckung

| Kriterium | Ausführbare Prüfung |
| --- | --- |
| ZA-A01 | `TargetTests.test_garlic_compact_original_handoff_and_missing_final_approval`; gebundene lokale Originalprüfung |
| ZA-A02 | vier versionierte künstliche Authoring-Pakete, `za1_fixtures.replay`, Exportprüfung und isolierte Registrierung; zwei unterschiedliche IDs im Produktlauf |
| ZA-A03 | `test_target_adapter.py`: neu gehashte Quelle/Normalisierung/Matrix/Hinweise/Proofs, ursprüngliche Abbrüche, alle Reparaturbindungen, Bild-/Endfreigabe, Parameter, Gates, Schwierigkeit, Größen/Farben/Randregel, ZIP/JSON/Pfade/Budgets |
| ZA-A04 | Registrytests: ID/Slot/Zielpfad/Windows-Kollision, No-op, Rollback/Prozesskill/Recovery; Runtimeprobe unbekannte IDs und Dateisuffixe; fremde Saves bytegleich über Spiel/Reset hinweg |
| ZA-A05 | `game/tests/za1_probe.gd` über `tools/za1_product.py`: reguläre Hauptszene, Album-Mauswahl, falsche eigene Eingabe, Undo/Redo, Teilstand, Neustart/Fortsetzung, Abschluss, erneuter Neustart/Albumbild; Mono 6×4 und Farbe 4×6 |
| ZA-A06 | native Pixelassertions für ungelöst/Teilstand/Abschluss, quadratische Zellen/proportionales Reveal, echte Windows-Ausgabe und externes `content_pack_probe.gd` gegen eingebetteten PCK |
| ZA-A07 | vollständige Produktionstests, bestehende v1/v2-Replays, Kern-/Save-/Recoverytests, 500-Aktionen-Integration, vier Piloten, aktuelle Render-/PERF-B-Prüfung gemäß CI-Auswahl |
| ZA-A08 | [Adaptervertrag](ZA1_ADAPTER.md), Werkzeuganleitung, Authoring 0.4.1, P1-/Produktionsvertrag und Projektprofil |

Die vier künstlichen Pakete sind ausdrücklich `test_only`; Endfreigaben werden
nur temporär erzeugt, nie als Eigentümererklärung verwendet. Reparaturfixtures
enthalten tatsächlich einen geänderten Endkandidaten; Farbfixtures verwenden
zwei tatsächliche Vordergrundfarben. Die reguläre Registry bleibt unverändert
bei den sechs sichtbaren historischen Inhalten plus drei Reservierungen.

Das Produktprogramm kopiert das Projekt, registriert vier Testpakete und startet
zehn separate native Spielprozesse sowie die bestehende vollständige Save-/Recovery-
Suite gegen den erweiterten Katalog. F01/F02/F06 werden über echte Eingaben mit
Teilständen belegt. Ihre Dateien und alle fremden neuen Slots bleiben über
jedes Partial-/Finish-/Read-/Resetstadium bytegleich. Ein zusätzlicher F01-Reset
erhält beide neuen Slots bytegleich und prüft damit auch die Gegenrichtung.
Der Reset nutzt das reale
Bestätigungssignal des Dialogs; die positiven Spielaktionen verwenden echte
Viewport-Mausevents. Kein direkter Save-Write ersetzt einen positiven Spielpfad.

Pixelprüfungen laufen auf 1920×1080-Originalframes. Technische CI-Artefakte
enthalten kompakte unveränderte Ausschnitte der tatsächlich geprüften Miniatur,
des gelösten Rasters und des Reveals; keine Skalierung. Vollbilder stehen lokal
für Kontext/Sichtprüfung. Reports führen native Maße, Cropkoordinaten und
getrennte Abschlusszustände. Die lokale gezielte Sichtprüfung kontrolliert
Mono/Farbe, beide Rechteckorientierungen, falsche Miniaturzelle, verdeckten
Motivnamen, Abschlussdarstellung und verdientes Albumbild.

PCK-Prüfung erfolgt für das reguläre Spielerpaket und den isolierten Export mit
zehn sichtbaren Einträgen. Alle ausgewählten Definitionen/Assets/Nutzungshinweise
müssen im tatsächlichen Pack laden; technische Verzeichnisse/Proofs und reservierte
F03/F05/F07-Definitionen müssen fehlen. Der Windows-Harness startet die tatsächlich
exportierte Fassung; Linux-CI behauptet keinen Windows-Prozessstart.

## Befehle und Reviewgate

```sh
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/check_docs.py
python -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python -m tools.puzzle_production.za1_fixtures --output-dir <neuer-replaypfad>
python tools/p1_product.py --cache-dir <cache> --output-dir <neuer-produktpfad>
python tools/p1_preflight.py --cache-dir <cache> --output-dir <neuer-preflightpfad>
```

Produkt-/Harness-/CI-Änderungen wählen alle Jobs: `docs`, `production`, `product`
mit Integration/Piloten/Visual/PERF-B, `preflight`, anschließend `ci-required`.
Der Produktionsjob liefert nur den kompakten Replaybericht, keine redundanten
Export-/Quellkopien. Bestehende Zeit-/Bytebudgets bleiben unverändert.

Vor Merge: alle ausgewählten aktuellen Checks erfolgreich, vollständiger Diff
und getrennter Selbstreview, danach unabhängiges technisches Review einschließlich
Sichtbelegen. Dieses unabhängige Review bleibt ein eigenes offenes Gate. Kein
verpflichtendes menschliches Probespielen; keine Merge-/Releasefreigabe.

## Nacharbeit N1 zu R1/B-01

[R1](https://github.com/venomenon328/picross/pull/75#pullrequestreview-5485612196)
und [N1](https://github.com/venomenon328/picross/pull/75#issuecomment-6115466029)
binden die gezielte Slotkorrektur. Export-Revalidierung und Validierung neuer
Registry-Einträge wenden zusätzlich zum unveränderten STEM-Muster dieselbe
Windows-Pfadprüfung wie der Erstexport auf `save_slot + ".json"` an.
Historische Reservierungen bleiben unverändert.

Vier ergänzende Tests in `test_target_adapter.py` prüfen:

- ausschließlich im Exportmanifest manipulierte Slots `con`, `nul`, `prn`,
  `aux`, `com1`, `lpt9`: API-Revalidierung, Plan und Registrierung lehnen ab;
  alle drei echten CLI-Aufrufe für `con` liefern `blocked` und Exit 2;
- bytegleiche Eingangs-/Checkoutdateien und identische Verzeichnismengen nach
  jeder Ablehnung, einschließlich fehlendem Paket-/Assetpfad und Journal;
- legale ähnliche Slots `con_test` und `com10`: Export, Revalidierung, Plan,
  Registrierung, vollständiger Checkout-Replay und wiederholter No-op bestehen;
- manipulierte bereits registrierte künstliche Einträge: In-Memory-Validierung,
  materialisierter Checkout mit konsistenter Runtime-Projektion sowie ein
  manipuliertes Recoveryjournal lehnen vor Dateiänderungen ab.

Lokaler Prüfweg: isolierte `.venv/za1` mit Python 3.13.14 / Pillow 12.3.0,
16 Adaptertests erfolgreich; 122 Tooltests erfolgreich mit einem bestehenden
Windows-Symlink-Skip. Der Dokumentvalidator prüft den isolierten versionierten
Snapshot, ohne fremde unversionierte Ablagen einzubeziehen. Vollständige aktuelle
CI, Commit-/Basis-/Test-Merge-Bindung und der aktualisierte getrennte Selbstreview
werden im PR nachgewiesen. Unabhängige Nachprüfung R2 bleibt vor Merge offen.
