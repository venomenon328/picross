# Historische Quellen und benötigte Bestände

Dokument-ID: `history-index`
Status: `reference`
Zuständigkeit: Historische Nachweise auffindbar halten und von aktuellen Normen
abgrenzen. Aktuelle Regeln stehen im [Dokumentationsindex](../README.md).

## 1. Erhaltene Bestände

| Bestand | Erhaltungsgrund und zuständige Quelle |
| --- | --- |
| Spielressourcen, Schriftoriginale, SVGs/PNGs, Manifeste und Lizenztexte | Tatsächliche Runtime-/Herstellungsinputs und Nutzungsrechte; [Designquellen](../design/README.md). |
| Laufende Authoringarbeit | Noch benötigte Eingänge/Entscheidungen; Abschluss nach [Authoring Schritt 5](../production/authoring/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung). |
| Aktuelle Definitionen, Bilder, Ratings, Datums- und Kategorienquellen | Produktdaten nach [RI-ONE](../production/PUZZLE_INTEGRATION_SINGLE_PATH.md); keine CI-Arbeitsdaten. |
| Methodische Referenzen und synthetische Testinputs | Tatsächlich konsumierte Regression, Kompatibilität oder eingefrorene Bewertungsgrundlage. |
| Authoring 0.7 und ZS1-Diagnosequellen | Ausdrücklich begrenzte alte Eingänge; [Legacy-Abgrenzung](../legacy/README.md). |
| KK-Originale | Weiterhin konsumierte Diagnoseinputs; [KK-Wegweiser](../evidence/kk/README.md). |
| [AT_B_OWNER_APPROVAL](AT_B_OWNER_APPROVAL.md) | Kompakte tatsächliche bildgebundene Eigentümerfreigabe; keine pauschale Freigabe heutiger Bildänderungen. |

Ein alter Dateiname macht einen technischen Input nicht entbehrlich. Eine frühere
CI-Pflicht macht einen Lieferbericht ebenso wenig zu einer dauerhaften Norm.
Historische Originale, Hashes und Freigaben werden nicht umgeschrieben oder auf
neue Quellen übertragen. Aktuelle Aufbewahrung und eigene Arbeitsbereinigung
folgen [CI-Vertrag](../dev-rules/CI_CONTRACT.md) und [WORKSPACE](../dev-rules/WORKSPACE.md).

## 2. Entfernte Berichte und abgelöste Sammelquellen

Der vollständige [Dokumentbestand vor der Konsolidierung](https://github.com/venomenon328/picross/tree/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs)
enthält alle entfernten Texte mit ihren damaligen Pfaden. Aktuelle Querverweise
auf solche Nachweise führen direkt auf diesen festen Git-Stand.

| Frühere Quelle | Aktuelle Zuständigkeit |
| --- | --- |
| `PUZZLE_IMAGE_STYLE.md` | [Bildindex](../production/images/README.md) und je eine Norm für Abschlussbild, Motivvorlage, Raster, Hintergrund und UI-Titelgrafik. |
| `CI_POLICY.md` | [CI_WORKFLOW_V2](../ci/CI_WORKFLOW_V2.md); kein zweiter CI-Regeltext. |
| `CI_SLIMMING.md` | Herkunft in §3 dieser Seite; tatsächliche Module in [CI-A](../ci/CI_A_SELECTION.md), [CI-B](../ci/CI_B_BROWSER_GROUPS.md), [CI-C](../ci/CI_C_NATIVE_GROUPS.md). |
| `BOOK_STUDY.md` | Alle weiterhin geltenden Einzelregeln in [BOOK_INTEGRATION](../game/BOOK_INTEGRATION.md); frühere Vollstudie ausschließlich historisch. |
| BP-1R-/BP-2-/BP-3-Pakettexte und Archivplatzhalter | Aktive Ressourcen und unveränderte Originalpakete über den [Designindex](../design/README.md#buchoriginale-und-historische-pakete); frühere Briefings, Empfehlungen und Prüfberichte bleiben historische Quellen. |
| Alte Produktions-HTML-Bedienhilfe | [Produktionsworkspace](../tools/PRODUCTION_WORKSPACE.md) und tatsächliche [Bedienanleitung](../../tools/production_workspace/README.md). |
| Abgeschlossene `*_VERIFICATION`, `*_IMPLEMENTATION`, `*_OWNER_TRIAL`, Selbstreviews und textuelle Evidenceberichte | Gebundene damalige Ergebnisse im Git-Verlauf und zugehörigen PR; aktuelle Fachnormen und Module übernehmen keine alten Lieferaufträge. |

Ein gelöschter Bericht wird nicht unter neuem Namen als Archivkopie in Repository,
Build oder CI-Artefakten abgelegt. Falls er eine noch gültige Einzelregel enthielt,
ist diese vor dem Löschen in die zuständige aktuelle Fachquelle übernommen worden.
Historische rote oder fehlende Nachweise werden durch neue Regeln nicht erfolgreich;
frühere Abnahmen werden durch die Bereinigung weder widerrufen noch erweitert.

## 3. Herkunft der CI- und Bestandsbereinigung

CI2 (#412–#424) führte frühere Auswahl-/Fach-/Browser-/Native-Kürzungen ein.
Workflow v2 ersetzt deren automatische Vollauswahl, pauschale Uploads und harte
Gesamtzeit-/Mengenpflichten. Die tatsächlichen aktuellen Prüfmodule und bewusst
akzeptierten Lücken stehen ausschließlich in den CI-Fachverträgen.

| Historischer Schritt | Gebundener Nachweis |
| --- | --- |
| CI2-A, Auswahl | [PR #419](https://github.com/venomenon328/picross/pull/419) |
| CI2-B, Fachgruppen | [PR #420](https://github.com/venomenon328/picross/pull/420), [B-T01](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CI2_B_VERIFICATION.md) |
| CI2-C, Browserumfang | [PR #421](https://github.com/venomenon328/picross/pull/421), [C-T01](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CI2_C_VERIFICATION.md) |
| CI2-D, native Prüfungen | [PR #422](https://github.com/venomenon328/picross/pull/422), [D-T01](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CI2_D_VERIFICATION.md) |
| CI2-E, Datenabbau | [PR #423](https://github.com/venomenon328/picross/pull/423), [E-T01](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CI2_E_VERIFICATION.md) |
| CI2-F, Kataloglaufzeit | [Issue #424](https://github.com/venomenon328/picross/issues/424), [F-T01](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/CI2_F_VERIFICATION.md) |
| Frühere native Bildmatrizen | [P2-C-V03-Audit](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/P2_C_V03_AUDIT.md); aktuelle Auswahl in CI-C. |
| Buchvollstudie und Entwurfsarchive | [BP-Ressourcen und Originalpakete](../design/README.md#buchoriginale-und-historische-pakete), [historische Studienquellen](https://github.com/venomenon328/picross/tree/fc86d2a2eff543f5b0c4ff328a71e815e4bc43a7/game/study/book). |
| Frühere Produktions-/Proofstudien | [Stand vor #116](https://github.com/venomenon328/picross/tree/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f); aktive Import-/Reparaturformen bleiben in den Produktionsverträgen. |

Frühere lokale Arbeitsordner, Fristen, Messzahlen und Bereinigungsblockaden sind
im [vorherigen Bestandsbericht](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/DEVELOPMENT_ARCHIVE.md)
dokumentiert. Dieser Wegweiser behauptet weder ihre heutige Existenz noch eine
erfolgte Löschung. Konkrete offene Arbeit und Abnahmen am tatsächlichen Issue-/PR-
Stand prüfen; alte Texte erteilen keinen neuen Implementierungs- oder Löschauftrag.
