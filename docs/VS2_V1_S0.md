# VS2-V1 · Eingangsdiagnose S0

Stand: 10.10.2026 · Diagnose, kein positiver Produktnachweis.

## Ergebnis und Grenze

**S0 bleibt offen; N01/N02/N04 wurden nicht begonnen.** Der fehlgeschlagene
[Produktjob 113954966256](https://github.com/venomenon328/picross/actions/runs/37970317549/job/113954966256)
endet beim nativen Godot-Import des historischen GP48-Vorherprojekts mit
Prozessstatus `-11` (unter Linux Signal 11/SIGSEGV). Der Python-Harness behandelt
diesen Prozessabbruch korrekt als Fehler und beendet den Produktprüfschritt mit
Exit 1. Es handelt sich nicht um einen fehlgeschlagenen Layout-Sollwert oder den
absichtlichen Negativtest mit Exit 23.

Der letzte Ressourcenmarker ist `Fraunces.ttf`. Ohne Stacktrace, Crashdump oder
isolierte Reproduktion beweist dies weder einen defekten Font noch einen konkreten
Enginefehler, Ressourcenmangel oder transientes Verhalten. Die unmittelbare
Abbruchursache ist belegt; die tiefere native Absturzursache bleibt unbekannt.
Es wurde kein Rerun gestartet und kein Test abgeschaltet oder abgeschwächt.

## Unverwechselbare Laufbindung

| Feld | Tatsächlich geprüft |
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

Run-API, Job-/Schritt-API, vollständiges Joblog und Git-Commit-API bestätigen
diese Bindung unabhängig voneinander. Der Test-Merge ist nicht mit dem
Quellhead gleichzusetzen. Gegenüber Produkthead `2c332ad688315bfa851f7c0d8642d2ab4ac3709c`
ändert `8d6b929` ausschließlich die fünf Markdown-Spezifikationen; Produkt,
Tests, Fonts und Harness sind unverändert.

## Fehlerpfad und tatsächlich erreichter Umfang

`tools/p1_product.py` ruft nach dem aktuellen GP48-Capture
`gp48_review.before_project()` und anschließend Godot mit
`--headless --path <temporäres gp48-before> --import` auf.
`tools/gp48_review.py` rekonstruiert dafür `prototypes/p1` aus
`add7a7e6aa507d54d6e0e2ac8a3a2c5e2d1d6912` und kopiert die aktuellen
`gp48_capture.gd` und `vs2_measurements.gd` hinein. Dies ist ein historisches
Vergleichsprojekt, kein Start des regulären Windows-Spielerpakets.

Vor dem Abbruch protokolliert der Lauf:

- `P1_TEST_RESULT checks=26623 failures=0` und `P1_TESTS_OK`;
- erfolgreiche Schreib-/Leseprozesse, alle sechs Pilot-Prozessfolgen sowie
  fünf 100-Aktionen-Prozesse und `P1_INTEGRATION_READ_OK cells/history/view/clues/redo`;
- den vorgesehenen Negativtest, kontrollierten Start und mehrere Renderphasen;
- zuletzt `GP48_CAPTURE_OK images=40` für den aktuellen Stand.

Diese Teilergebnisse sind kein erfolgreicher Gesamtproduktlauf. Spätere Vergleiche,
abschließende Verpackung und Windows-Export wurden nicht erreicht. Sämtliche
Uploadschritte sind `skipped`; die Artefakt-API liefert für den Fehllauf keine
Artefakte. Ein neuer EXE-/PCK-Nachweis oder neue V1-Bilder existieren daraus nicht.
Die [kompakte API-/Logbindung](../examples/vs2/v1-s0-evidence.json) hält die
diagnostisch relevanten Originalzeilen und Quellen fest.

## Aktualitätsbefund und notwendiger Anschluss

Der vorhandene Worktree `picross-vs2` war sauber und stand lokal auf `2c332ad`.
Er wurde ausschließlich per Fast-forward auf den Remotehead `8d6b929` aktualisiert.
Die unversionierten Dateien des anderen Worktrees wurden nicht angefasst.

`main` ist inzwischen durch [PR #64 / Issue #63](https://github.com/venomenon328/picross/pull/64)
auf `d7ec4e1e4a29d82b6979537a33868d57732d3713` weitergelaufen. Der aktuelle
#61-Body und die dort integrierte
[CI-Policy](https://github.com/venomenon328/picross/blob/d7ec4e1e4a29d82b6979537a33868d57732d3713/docs/CI_POLICY.md)
verlangen vor weiterer Umsetzung die Integration des neuen CI-Stands und der
aktuellen VS2-Prüfungen. Historische Vorherimporte gehören danach nicht mehr
in den Standardlauf. Das ist eine bereits separat beschlossene Policyänderung,
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
Der separate [endliche V1-Vergleichsplan](../examples/vs2/v1-plan.json) wurde
in `06f695f` vor neuen Vergleichen versioniert. Historische Pläne und Nachweise bleiben unverändert. V2/N03/N05,
kombinierte Abnahmen, persönliche VS2-M01 und Mergefreigabe bleiben offen.

## Integrationsmessung und begrenzte Harnesskorrektur

Der neue [CI-Lauf 38047039151](https://github.com/venomenon328/picross/actions/runs/38047039151)
prüft `1149552bac8f47fc4807cdd66bf6a7379530e543` gegen `d7ec4e1`, tatsächlich
auf `d47982dde9d8d0b577bb5d388d1d26f3357b3cd8`. Docs, Preflight und alle drei
Fachjobs bestehen. Product wird am unveränderten 15-Minuten-Limit während
`vs2-regular-matrix` abgebrochen; der letzte laufende Bericht steht bei
880,287 Sekunden. Das ist kein Pass. Das kleine technische Fehlerartefakt
`11667917786` enthält Bericht und Phasenlogs; kein Spielerpaket wurde hochgeladen.

Der parallele lokale Windowslauf desselben Ausgangsheads besteht Kernchecks,
500 Aktionen/Neustart, sechs Piloten, aktuelle Zeichen-/Pixelprüfungen, 1.443.529
GF1-Assertions und die 304 VS2-Fälle/23 Bilder. Danach scheitert der exportierte
Start mit Exit 3: Der neu angeschlossene `vs2_roundtrip.gd` übernahm das vom
Harness gesetzte `P1_TEST_SAVE_ROOT` nicht und hinterließ seine neun Teststände
im normalen **isolierten** Harnessprofil. Der frische Smoke-Start erwartete dort
unbespielte Blätter. Keine echten Benutzerdaten waren beteiligt.

Die Integrationskorrektur hält Prüfumfang und Zeitlimits fest: unabhängige
VS2-Prüfungen laufen überlappend in einer eigenen importierten Projektkopie,
eigenem Profil und eigenen laufenden Phasenberichten. Der Hauptlauf verlangt
ihren vollständigen Erfolg vor Export/Pass. Der Roundtrip übernimmt seinen
expliziten CI-Slotroot und prüft ihn; die native Downloadprobe ohne diese Variable
prüft weiterhin den normalen Speicherweg im isolierten Benutzerprofil.

Zusätzlich bleiben die aktuellen strengen H1-Überlauf-/Tooltip-/Statuspixeltests
neben den regulären VS2-Paaren aktiv. Die explizite Rendererkomponente wird über
den vorhandenen Entwickler-Testhelfer positioniert, nicht über den bewusst
wirkungslosen regulären Panaufruf. Lokaler Einzelbeleg: 82 native Aufnahmen,
9.911 Pixelassertions, kein Fehler. Das ist kein Ersatz für den noch erforderlichen
vollständigen integrierten Lauf. Weiterhin keine V1-Layoutänderung.
