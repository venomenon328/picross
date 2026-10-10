# VS2-V1 Â· Eingangsdiagnose S0

Stand: 10.10.2026 Â· Diagnose, kein positiver Produktnachweis.

## Ergebnis und Grenze

**S0 bleibt offen; N01/N02/N04 wurden nicht begonnen.** Der fehlgeschlagene
[Produktjob 113954966256](https://github.com/venomenon328/picross/actions/runs/37970317549/job/113954966256)
endet beim nativen Godot-Import des historischen GP48-Vorherprojekts mit
Prozessstatus `-11` (unter Linux Signal 11/SIGSEGV). Der Python-Harness behandelt
diesen Prozessabbruch korrekt als Fehler und beendet den ProduktprÃ¼fschritt mit
Exit 1. Es handelt sich nicht um einen fehlgeschlagenen Layout-Sollwert oder den
absichtlichen Negativtest mit Exit 23.

Der letzte Ressourcenmarker ist `Fraunces.ttf`. Ohne Stacktrace, Crashdump oder
isolierte Reproduktion beweist dies weder einen defekten Font noch einen konkreten
Enginefehler, Ressourcenmangel oder transientes Verhalten. Die unmittelbare
Abbruchursache ist belegt; die tiefere native Absturzursache bleibt unbekannt.
Es wurde kein Rerun gestartet und kein Test abgeschaltet oder abgeschwÃ¤cht.

## Unverwechselbare Laufbindung

| Feld | TatsÃ¤chlich geprÃ¼ft |
| --- | --- |
| Lauf / Versuch | `37970317549` / `1`, Ereignis `pull_request` |
| Quellhead | `8d6b929099f552f1e1582b2cca478f35eef2f415` |
| damalige Basis | `fad885344874534629365917a2ab6a8d311cd3a7` |
| ausgecheckter Test-Merge | `bed4ca33736b6b12c7540efb7ac41df4833f2bb2` |
| Test-Merge-Tree | `32961b6a1da9505385c4cbd34f9b5db80c392864` |
| Eltern in Reihenfolge | damalige Basis, Quellhead |
| Runner | Ubuntu 24.04.5, Image `20261004.327.1`, Runner `2.337.0` |
| Engine | `4.7.2.stable.official.ed1daf0bf` |
| Beginn / Ende der Fehlerphase | `2026-10-09T18:17:05.4528094Z` / `2026-10-09T18:17:09.2897641Z` |

Run-API, Job-/Schritt-API, vollstÃ¤ndiges Joblog und Git-Commit-API bestÃ¤tigen
diese Bindung unabhÃ¤ngig voneinander. Der Test-Merge ist nicht mit dem
Quellhead gleichzusetzen. GegenÃ¼ber Produkthead `2c332ad688315bfa851f7c0d8642d2ab4ac3709c`
Ã¤ndert `8d6b929` ausschlieÃŸlich die fÃ¼nf Markdown-Spezifikationen; Produkt,
Tests, Fonts und Harness sind unverÃ¤ndert.

## Fehlerpfad und tatsÃ¤chlich erreichter Umfang

`tools/p1_product.py` ruft nach dem aktuellen GP48-Capture
`gp48_review.before_project()` und anschlieÃŸend Godot mit
`--headless --path <temporÃ¤res gp48-before> --import` auf.
`tools/gp48_review.py` rekonstruiert dafÃ¼r `prototypes/p1` aus
`add7a7e6aa507d54d6e0e2ac8a3a2c5e2d1d6912` und kopiert die aktuellen
`gp48_capture.gd` und `vs2_measurements.gd` hinein. Dies ist ein historisches
Vergleichsprojekt, kein Start des regulÃ¤ren Windows-Spielerpakets.

Vor dem Abbruch protokolliert der Lauf:

- `P1_TEST_RESULT checks=26623 failures=0` und `P1_TESTS_OK`;
- erfolgreiche Schreib-/Leseprozesse, alle sechs Pilot-Prozessfolgen sowie
  fÃ¼nf 100-Aktionen-Prozesse und `P1_INTEGRATION_READ_OK cells/history/view/clues/redo`;
- den vorgesehenen Negativtest, kontrollierten Start und mehrere Renderphasen;
- zuletzt `GP48_CAPTURE_OK images=40` fÃ¼r den aktuellen Stand.

Diese Teilergebnisse sind kein erfolgreicher Gesamtproduktlauf. SpÃ¤tere Vergleiche,
abschlieÃŸende Verpackung und Windows-Export wurden nicht erreicht. SÃ¤mtliche
Uploadschritte sind `skipped`; die Artefakt-API liefert fÃ¼r den Fehllauf keine
Artefakte. Ein neuer EXE-/PCK-Nachweis oder neue V1-Bilder existieren daraus nicht.
Die [kompakte API-/Logbindung](../examples/vs2/v1-s0-evidence.json) hÃ¤lt die
diagnostisch relevanten Originalzeilen und Quellen fest.

## AktualitÃ¤tsbefund und notwendiger Anschluss

Der vorhandene Worktree `picross-vs2` war sauber und stand lokal auf `2c332ad`.
Er wurde ausschlieÃŸlich per Fast-forward auf den Remotehead `8d6b929` aktualisiert.
Die unversionierten Dateien des anderen Worktrees wurden nicht angefasst.

`main` ist inzwischen durch [PR #64 / Issue #63](https://github.com/venomenon328/picross/pull/64)
auf `d7ec4e1e4a29d82b6979537a33868d57732d3713` weitergelaufen. Der aktuelle
#61-Body und die dort integrierte
[CI-Policy](https://github.com/venomenon328/picross/blob/d7ec4e1e4a29d82b6979537a33868d57732d3713/docs/CI_POLICY.md)
verlangen vor weiterer Umsetzung die Integration des neuen CI-Stands und der
aktuellen VS2-PrÃ¼fungen. Historische Vorherimporte gehÃ¶ren danach nicht mehr
in den Standardlauf. Das ist eine bereits separat beschlossene PolicyÃ¤nderung,
keine nachgewiesene Reparatur des alten nativen Absturzes.

Der Eigentümer hat am 10.10.2026 im Auftrag ausdrücklich zugestimmt:
„Neue CI-Policy aus #63 übernehmen (empfohlen)“. Die Integration übernimmt
`d7ec4e1` und löst die sieben Konflikte unter Erhalt der regulären Vollsicht.
Der aktuelle Harness ergänzt die 304 VS2-Matrixfälle (neun reguläre, zehn
technische Fälle), GF1-Regressionen und echte Schreib-/Leseprozesse. Er prüft
alle 23 nativen VS2-Aufnahmen vor der begrenzten Evidenzauswahl; historische
Vorherimporte bleiben ausschließlich separat aufrufbar. Das Spielerpaket
enthält die aktive VS2-Spielprobe. Die sechs pauschalen Altjobs sind durch die
Auswahl und das verpflichtende `ci-required` gemäß CI-Policy abgelöst.

S0 bleibt bis zum positiven aktuellen Produktlauf offen. Dessen Head,
Test-Merge, Lauf und Ergebnisse werden hier ergänzt. Die Policyintegration
beweist keine Reparatur des historischen Engineabsturzes.

V1 bleibt ein nicht implementierter Zwischenstand des offenen Gesamtauftrags.
Der separate endliche V1-Vergleichsplan ist weiterhin vor neuen Vergleichen zu
versionieren. Historische PlÃ¤ne und Nachweise bleiben unverÃ¤ndert. V2/N03/N05,
kombinierte Abnahmen, persÃ¶nliche VS2-M01 und Mergefreigabe bleiben offen.
