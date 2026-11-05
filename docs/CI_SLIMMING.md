# CI2: Herkunft der heutigen Prüfmodule

CI2 (#412–#424) war die frühere Verschlankung von Auswahl, Fachtests, Browser-,
nativen Prüfungen und aktivem Bestand. Ihr vollständiger
[Soll-/Liefervertrag vor Workflow v2](https://github.com/venomenon328/picross/blob/f3626f28899a48fa4d783716925f7425a3eb1784/docs/CI_SLIMMING.md)
bleibt commitgebunden erhalten. Diese Seite ist ein historischer Wegweiser,
kein zusätzlicher aktueller Prüfplan und keine offene Implementierungsanweisung.

## Heute maßgeblich

- [CI_WORKFLOW_V2](CI_WORKFLOW_V2.md): Paketwahl, kleiner Kern, Windows-Download,
  zehn Minuten als weiches Ziel und zweckgebundene Aufbewahrung.
- [Fachmodule](CI_A_SELECTION.md), [native Gruppen](CI_C_NATIVE_GROUPS.md) und
  [manueller Chromiumumfang](CI_B_BROWSER_GROUPS.md): tatsächliche Modulverträge.
- [CI_CONTRACT](dev-rules/CI_CONTRACT.md): bewusste Abdeckungsentscheidungen und
  Testlebenszyklus; keine pauschal geschützten Familien oder Mindestmengen.
- [Bestandsquellen](DEVELOPMENT_ARCHIVE.md): aktive Daten, historische Quellen
  und Umgang mit früheren lokalen Restdaten.

Die früheren automatischen Diff-/Vollauswahlen,
CI2-Teilzeitziele als Verpflichtung, Bildquoten, pauschalen Uploads und separaten
P3-A-Fingerprintfreigaben gelten nicht mehr. Funktionale Produktzusagen,
Kompatibilität, Rechte und vereinbarte aktuelle Abnahmen bleiben eigenständig.
Die kurze Historyroute ist im nativen Modulvertrag beschrieben; ihre 20/6/2-Grenzen
sind ein bewusst gewählter Testumfang, keine globale CI-Zeit-/Mengenobergrenze.

## Gebundene Liefernachweise

| Paket | Nachweis und Integration |
| --- | --- |
| CI2-A, Auswahl | [PR #419](https://github.com/venomenon328/picross/pull/419) |
| CI2-B, Fachgruppen/Fixtures | [B-T01](CI2_B_VERIFICATION.md), [PR #420](https://github.com/venomenon328/picross/pull/420) |
| CI2-C, kurzer Browserumfang | [C-T01](CI2_C_VERIFICATION.md), [PR #421](https://github.com/venomenon328/picross/pull/421) |
| CI2-D, native Kürzung | [D-T01](CI2_D_VERIFICATION.md), [PR #422](https://github.com/venomenon328/picross/pull/422) |
| CI2-E, Datenabbau | [E-T01](CI2_E_VERIFICATION.md), [PR #423](https://github.com/venomenon328/picross/pull/423) |
| CI2-F, Kataloglaufzeit | [F-T01](CI2_F_VERIFICATION.md), [Issue #424](https://github.com/venomenon328/picross/issues/424) |

Messungen und damalige Urteile werden nicht umgeschrieben. Ihr aktueller
Abschluss-/Befundstatus steht in den verlinkten Issues/PRs. Alte rote oder fehlende
Nachweise werden durch neue Auswahlregeln nicht nachträglich erfolgreich;
alte Vollmatrizen müssen auch nicht zur Einführung neuer Regeln wiederholt werden.
