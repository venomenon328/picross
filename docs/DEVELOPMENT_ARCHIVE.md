# Aktiver Bestand und historische Quellen

## Aktuelle Ablageentscheidung

Aktive Produktdateien, Nutzungsrechte, technische Vertragsinputs und kompakte
Freigabe-/Integrationsdaten bleiben nach ihrem tatsächlichen Zweck erhalten.
Ein historischer Name macht eine Datei nicht entbehrlich; eine frühere CI-Pflicht
macht sie ebenso wenig dauerhaft notwendig. Für Tests/Artefakte gilt
[CI_CONTRACT](dev-rules/CI_CONTRACT.md), für Picross [CI_WORKFLOW_V2](CI_WORKFLOW_V2.md).

| Bestand | Zuständiger Zweck/Vertrag |
| --- | --- |
| `game/` einschließlich Buch-, Font-, Atlas- und Inhaltsressourcen | Runtime und Nutzungsrechte; technische Tests/Fixtures sind vom Spielerexport ausgeschlossen |
| `content/authoring/` | Laufende Produktion und noch benötigte Freigabevorlagen; Abschluss nach [Authoring §9](ai-workflows/PUZZLE_AUTHORING.md#9-produktionsabschluss-und-bereinigung) |
| `content/packages/` | Bis Abschluss gebundene Produktionskopie; danach kompakte [ZA-1-Integrationsbindung](ZA1_ADAPTER.md) |
| Aktive Bild-, Rating-, Hinzugefügt- und Kategorienmetadaten | Produkt-/Freigabedaten gemäß Fachvertrag; keine CI-Laufgalerie |
| Feste synthetische Testinputs, Freezes und tatsächlich verwendete Referenzen | Konkrete Regression, Kompatibilität oder methodischer Vertrag; keine echten Katalogkopien |
| Laufbezogene Logs, Screenshots, Videos, Exporte und Vergleichsbäume | Temporäre Prüfdaten; befristeter Download nur für konkret benannten Review-/Diagnosezweck |
| Frühere `*_VERIFICATION`, `*_IMPLEMENTATION`, `*_OWNER_TRIAL`, Selbstreviews und `docs/evidence/`-Berichte | Nachweise/Anleitungen ihres gebundenen Pakets; damalige „offen“-Angaben im aktuellen Issue/PR nachprüfen, keine neue Dauerpflicht |

Der Metadatencheck in `docs` verhindert neue unzulässige generierte Archivklassen.
Er lädt keine historischen Binärdaten nur zur Messung. Keine feste maximale
Byte-/Datei-/PNG-Menge, kein laufend wachsendes Belegarchiv. Dauerhafte visuelle
Regressionen behalten höchstens ihren letzten abgenommenen Referenzstand.
Produktillustrationen und ihre Rechte-/Quellbindung sind davon zu unterscheiden.

## Historische Bereinigungen

| Bereich | Gebundener Nachweis/Fundort |
| --- | --- |
| BP-Entwurfs-/Reviewpakete | [BP-Archiv](design/book_inventory/ARCHIVE.md), historische Pakete/Hashes statt neuer Kopien |
| Abgeschlossene frühe Rätselproduktionen, Proof-/Korpus-/RP4–RP6-Studien | [Stand vor #116](https://github.com/venomenon328/picross/tree/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f); aktive Import-/Reparaturformate bleiben in den Fachanleitungen |
| AT-B-Arbeitsdaten und AT-/HZ-Galerien, sechs Klassen mit damals 1.156 Dateien / 837.043.724 Bytes | [CI2-E-T01](CI2_E_VERIFICATION.md), [PR #423](https://github.com/venomenon328/picross/pull/423); keine aktuelle Bestandsmessung |
| Historische Buchvollstudie, 27 Definitions-/Revealpaare, Film-/Exportmatrix | [Studienquellen](https://github.com/venomenon328/picross/tree/fc86d2a2eff543f5b0c4ff328a71e815e4bc43a7/game/study/book), [BOOK_STUDY](BOOK_STUDY.md); heutiger [Buchvertrag](BOOK_INTEGRATION.md) |
| Frühere 435 PNG-Pflichten und Einführungsproducer | [P2-C-V03-Audit](P2_C_V03_AUDIT.md), heutiger [nativer Modulvertrag](CI_C_NATIVE_GROUPS.md) |
| CI2-A–F und spätere #502-Stichproben | [CI2-Wegweiser](CI_SLIMMING.md), aktuelle Native-/Fachverträge und zugehörige Issues/PRs |

Die vollständige [Bestandschronologie vor dieser Konsolidierung](https://github.com/venomenon328/picross/blob/f3626f28899a48fa4d783716925f7425a3eb1784/docs/DEVELOPMENT_ARCHIVE.md)
bleibt erreichbar. Historische Größen, Prüfergebnisse, Hashes und Abnahmen werden
nicht umgeschrieben. Git-Historie bleibt erhalten; gelöschte Arbeitsbäume werden
nicht unter neuem Namen in Repository, Build oder CI-Artefakten archiviert.

## Frühere lokale Restdaten

Folgende Pfade/Fristen wurden im Vorgänger dokumentiert. Dies ist **keine Prüfung
ihrer heutigen Existenz, ihres Eigentümers oder eines erfolgten Löschens**:

| damaliges Paket | berichtete eigene Ablage | damaliger Review-/Ablaufpunkt |
| --- | --- | --- |
| P2-C-V03 | `artifacts/502-p2cv03-local/` | V03-R01 beziehungsweise 18.11.2026 |
| P2-E-A-V02 | `artifacts/502-p2e-v02-local/` | V02-R01 beziehungsweise 19.11.2026 |
| P2-E-B-V01 | `artifacts/502-p2eb-local/` | P2-E-B-V01-R01 beziehungsweise 19.11.2026 |
| P2-F-A-V01 | `artifacts/502-p2f-local/` | P2-F-A-V01-R01 beziehungsweise 19.11.2026 |
| P2-F-B-V01 | `artifacts/502-p2fb-local/`, Container `picross-502-zs2` | P2-F-B-V01-R01 beziehungsweise 19.11.2026 |

Frühere HIL/V01/V02/P2-B-Blockaden sind in den jeweiligen PRs gebunden. Sie werden
weder umgangen noch als erledigt gemeldet. Vor Bereinigung tatsächlichen Pfad,
Eigentum, laufende Prozesse/Locks, ungesicherte Änderungen und noch erforderliche
Belege prüfen. Für einen beauftragten eigenen Bereinigungsumfang gilt
[WORKSPACE](dev-rules/WORKSPACE.md); die alten pauschalen Aussagen „keine automatische
Löschung“ schränken eine neue passende ausdrückliche Freigabe nicht ein.
Dieser Dokumentaudit selbst löscht keine solchen früheren Arbeitsdaten.

Offene Inhalts-/Designarbeit und persönliche Abnahmen bleiben im zuständigen
Issue/PR geführt. Sie werden durch Datenabbau oder diesen Wegweiser weder bestätigt
noch neu beauftragt. Bei konkretem historischen Untersuchungsbedarf einen getrennten
eigenen Checkout im beauftragten Arbeitsbereich verwenden und nach Übergabe bereinigen.
