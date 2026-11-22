# ZA-1: Aktueller Integrationseingang und kreative Vorbereitung

## Geltung und Quellen

- **Status:** aktiver Vertrag für das geschlossene aktuelle Integrationsmanifest, seine Prüfung und die CLI.
- **Fachliche Grenze:** [RI-ONE](PUZZLE_INTEGRATION_SINGLE_PATH.md); aktuelle Inhalts-/Transaktionsformen besitzt [RI](PUZZLE_INTEGRATION.md).
- **Bildgestaltung:** [Bildtypnormen](images/README.md); Hintergrundprofile und Capability ausschließlich im [Hintergrundvertrag](PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile).
- **Vertragshistorie:** [Paketentscheidung #660](https://github.com/venomenon328/picross/issues/660#umsetzungsvorbereitung-ri-one). Frühere Export-/Registrierungs-/Receiptgenerationen und ihre Zulassungsmatrizen sind abgelöst; historische Originale bleiben in Git und sind kein Integrationsinput.

## Eingang und Grenzen

Ein Verzeichnis enthält `manifest.json` und die darin referenzierten aktuellen Dateien. Das Manifest hat exakt:

| Feld | Aktueller Inhalt |
| --- | --- |
| `format` | `picross-integration-input-v1` |
| `entry` | `id,key,save_slot,definition,reveal,visible,mode,category_id` gemäß RI |
| `metadata` | `id,name,category_id`, passend zum Entry |
| `definition` | Ref auf finale Definition, Matrix, Hinweise und Palette |
| `reveal` | `asset,notice,rights`; Ref, Ref, Rechteobjekt |
| `background` | `status` selected/none/standard; `image` mit derselben Bildform oder null |
| `difficulty` | Ref auf aktuell geprüfte Bewertung nach SD-Catalog |
| `proof` | Ref auf vollständigen passenden Logiknachweis |
| `quality` | `review` als Ref und `exceptions` als Liste |
| `approval` | `actor,timestamp_utc,statement,selection_sha256,evidence,checks` |
| `test_only` | echter Boolean; true darf nicht in den Produktkatalog |

Ein Ref enthält exakt `file,bytes,sha256`: sicherer relativer Dateipfad, positive tatsächliche Länge und SHA-256. Keine Links/Aliase, Pfadtraversierung, Gerätepfade oder versteckte Quellenauflösung. Die Definition ist höchstens 2 MiB, das Manifest 1 MiB, Proof 64 MiB, ein Bild 32 MiB und ein Textbeleg 64 KiB. UTF-8 und geschlossene JSON-Formen gelten. Export kopiert ausschließlich referenzierte Dateien und prüft den geschriebenen Eingang vollständig.

Definition und Modus müssen zusammenpassen: Mono hat genau eine benutzte Vordergrundfarbe, Color zwei bis acht. Gezählt werden die unterschiedlichen belegten Zellwerte. Ein ungenutzter Paletteintrag zählt nicht. Widersprüche stoppen Export, Planung und Erstregistrierung vor Schreiboperationen. Die Palette enthält genau die benutzten Farben; Hinweise und Lösungsmatrix sind konsistent. Finale Revealadresse und Name stimmen mit Entry/Metadaten überein. Ein unabhängiger Verifier bestätigt vollständige Deduktion und exakt das finale Raster. Vorhandene gültige Nachweise benutzen; keine erneute Suchproduktion allein zur Herkunftszulassung.

## Rechte, Bildqualität und tatsächliche Entscheidung

`rights` enthält exakt `author,usage_basis,source,changes` als nichtleere Texte. Die aktuelle Notice enthält diese benötigten Angaben. Reveal-PNG/SVG wird nach den geltenden Größen-, Alpha-, Sicherheits- und Bildregeln geprüft. Ein ausgewählter Hintergrund muss einem nach [Hintergrundvertrag](PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile) zugelassenen Profil und der Ziel-Capability entsprechen; `none` und `standard` führen keine künstliche Textur. Die tatsächliche Auswahl oder der tatsächliche Verzicht muss aus der Entscheidung hervorgehen.

`quality.review` enthält JSON mit `actor,timestamp_utc,statement,criteria`. `criteria` führt exakt Q-R04, Q-H01 und Q-H02; jeder Befund hat `result=fulfilled|borderline|failed`, Boolean `accepted` und nichtleeren `reason`. Ein Grenzfall braucht tatsächliche ausdrückliche Annahme; ein negatives redaktionelles Urteil bleibt negativ und braucht seine tatsächliche ausdrückliche Annahme. Ungeprüft bleibt blockiert. Der Integrator berechnet Randregel und technische Palettenabstände frisch. Negative Befunde benötigen genau ihre ausdrücklich dokumentierten Ausnahmen: `criterion=frame` oder `palette:<id1>:<id2>`, dazu `actor,timestamp_utc,statement,evidence`. Keine pauschale Forcefreigabe.

`approval.checks` führt exakt `reveal,motif,raster,palette,hint_legibility,background,final_content,integration`, jeweils true als dokumentierte tatsächliche Annahme. `evidence` bindet den realen Entscheidungstext. `selection_sha256` ist der kanonische Hash des vollständigen Manifests ohne `approval`. Bestehende gültige Entscheidungen dürfen übernommen werden; ein technischer Hash, erfundener Text oder Schweigen ist keine menschliche Freigabe. Neue kreative Bytes benötigen eine passende tatsächliche Entscheidung. Die technischen Grenzen allein ersetzen keine direkte Bildsichtung nach den [Bildtypnormen](images/README.md).

## PW-FIND · Entscheidungen bis zur Integration

Der v3-Finalizer liefert `picross-integration-input-v2`. Der ältere v1-Eingang
behält seinen geschlossenen Reviewvertrag. Bei v2 enthält `quality.review`
die vier gewählten Bestandteile (`components`), Parameter, Briefing,
fortgeltende Vorgaben (`instructions`), konkrete `findings` und die tatsächliche
Schlusserklärung. Die technische Ausnahme bindet zusätzlich `definition_sha256`.
Die Prüfung gleicht die ausgewählten Produktbytes mit dem Manifest ab.

Finalizer, Export und Integration erhalten alle noch relevanten Befundannahmen
und Behandlungsvorgaben aus sämtlichen Produktionsphasen. Im v2-Eingang wird der vollständige gewählte Befundumfang geprüft. Urteil, tatsächliche Annahme und Behandlung bleiben getrennt und an
die gewählten Inhalte gebunden. Die fachliche Wirksamkeit definiert
[Qualität §6.1](PUZZLE_QUALITY.md#61-pw-find--befundentscheidungen-in-allen-phasen).
Ein gedeckt angenommener Befund darf nicht erneut blockieren; übrige technische
Voraussetzungen, Rechte, Inhaltsbindungen und tatsächliche Endabnahme bleiben.

Die Daten gehören zum aktuellen Integrationseingang. Sie werden keine zweite
Runtime-Autorität und keine neue dauerhafte Produktionsakte. Erforderliche
Produkt-/Rechtenachweise und technische Ausnahmen bleiben erhalten; normale
Completion und Bereinigung folgen [RI-ONE §5](PUZZLE_INTEGRATION_SINGLE_PATH.md#5-completion-und-produktionsabschluss).
Eine Behandlung ist kein automatischer Auftrag zu späterer Spiel-/Editoränderung.

## Aufruf und Ausgabe

```text
python -m tools.puzzle_production.authoring_builder prepare-integration --input <finaler-eingang> --output-dir <neuer-eingang>
python -m tools.puzzle_production.target_adapter inspect --input <eingang>
python -m tools.puzzle_production.target_adapter export --input <eingang> --output-dir <neuer-export>
python -m tools.puzzle_production.target_adapter verify-export --input <export>
python -m tools.puzzle_production.target_adapter plan --input <eingang> --checkout <checkout>
python -m tools.puzzle_production.target_adapter register --input <eingang> --checkout <checkout>
python -m tools.puzzle_production.target_adapter recover-registration --checkout <checkout>
```

`prepare-integration` und `export` sind dieselbe aktuelle geprüfte Übergabe, keine kreative Produktion und kein Converter für alte ZIPs. Der beauftragte Produzent stellt den finalen Eingang aus den vorhandenen gültigen Nutzdaten/Entscheidungen zusammen. Separate inspect/verify-Aufrufe sind für gezielte Diagnose verfügbar und keine redundante Routinepflicht vor einem ohnehin vollständig prüfenden register. Der frische lesende Plan bleibt vor autorisiertem Schreiben sinnvoll; register plant selbst erneut. API: `catalog_integration.integrate(input, checkout, apply=False|True)`. Belegte ID mit anderem Inhalt ist ein konkreter Konflikt; eigene Raster-/Bildpflege nach PE verwenden.

## Kreative Werkzeuge und fachliche Qualität

Die Verfahren für direkten Import, feste motivtreue Korrektur, manuelle Ableitung, angenommene Pixelvorlage und Paarprofile bleiben kreative Werkzeuge. Aktuelle Vorbereitung prüft erlaubte Masken/Budgets während der konkreten Operation und vollständige aktuelle Endproofs. Keine Herstellungsnachweise oder historischen Arbeitsdateien als neue Zulassung. Diese werkzeugspezifischen Arbeitsformen sind keine alternativen Katalogexporter und keine Herkunftsallowlist des Integrators. Autorisierungen dürfen keine unabhängigen harten Inhaltsgates aufheben. Paarprofil allein belegt weder R4-Notwendigkeit noch ein Difficultylabel.

Neue reguläre Produktion folgt [Authoring](authoring/PUZZLE_AUTHORING.md), [PW-B](../tools/PW_B_CONTRACT.md), [fester Rasterkorrektur](FIXED_RASTER.md) und der beauftragten Phase. Vorhandene gültige Bilder/Proofs nicht nachproduzieren. Bildformat- und Korrekturbefugnisse aus aktuellem Main bleiben erhalten. Alt-WIP ist kein Kompatibilitätsziel und wird nicht automatisch konvertiert.

## PW-RETIRE · Abschluss mehrphasiger Produktion

Nach tatsächlichem Mainmerge dessen vollen Commit und frisch aktualisiertes origin/main prüfen. `retire-production` bestätigt die aktuelle ausgewählte Lieferung, nicht einen Originalexport oder Receipt. Aktuelle Jobs haben einen einzelnen registrierten Record. Ihre Arbeitsbytes werden am eigenen Arbeitsref geprüft; sie müssen nicht im Produkt-Maincommit enthalten sein. Nur bei ausdrücklich älteren mehrphasigen Formen frühere zugeordnete Arbeit zusätzlich auswählen:

```text
python -m tools.puzzle_production.target_adapter retire-production --checkout <checkout> --integrated-commit <main-SHA> --puzzle-id <pz-ID> --completed-revision <pz-ID> <frühere-revision> --completed-work <pz-ID> <relativer-arbeitsordner>
```

Zusatzoptionen sind wiederholbar und gehören zur bestehenden Abschlussbefugnis, ohne neue Freigabe pro Vorgängerrecord. Zuordnung aus tatsächlicher aktueller Arbeit und deren unveränderten Arbeitsbytes, keine numerische Revisionsheuristik. Aktuelle Bild-/Definitions-/Notice-/Rating-/Datumsdaten bleiben erhalten.

**Keine neue Abschluss-Notice:** Aktuelle PE-EDIT2-Hintergründe haben keine
Pflicht-`.txt` am Hintergrundstamm. `retire-production` prüft den ausgewählten
Livebild-/Quellen-/Runtimezustand und die dazugehörigen tatsächlichen Bytes
gegen bestätigtes `main`; eine vorhandene historische Hintergrund-`.txt`
wird dabei bytegleich geprüft, ihre Abwesenheit ebenso. Keine künstliche
Textdatei, rückwirkende Herkunftserklärung oder zusätzliche Abschlussformalität.
Die weiterhin erforderliche Reveal-Notice sowie tatsächlich vorhandene
Rechte-/Lizenztexte bleiben geschützt. Dieser Kompatibilitätsgrundsatz hebt
keine Fremdarbeits-, Main-, Byte- oder Recoveryguards auf.

Der Pointer entfällt nur, wenn er exakt auf eine ausgewählte abgeschlossene Revision zeigt; neue/offene Arbeit und fremde Bytes bleiben. Unbekannte Dateien innerhalb ausgewählter Arbeit blockieren vor Löschung. Teilentfernung ist ehrlich zu melden und anhand desselben Mainankers wiederholbar; vollständige Wiederholung ist schreibfreier No-op. Keine neue historische Dauerakte.

Eigenständige aktuelle Bild-/Rasteränderungen verwenden den gezielten Editor. Deren ausgewählte abgeschlossene Arbeitsdateien können nach tatsächlichem Mainnachweis über denselben ausgewählten Abschlussweg bereinigt werden; bestehende aktuelle Rechte und Bilder bleiben. Alte `retire-reveal-production`-/`retire-background-production`-Receiptpfade sind abgelöst.

## Katalogprofile für Abschlussbilder

Die Erstintegration bereitet zwei Profile aus dem gewählten Original vor. Registrierungsjournal v2 bindet elf Ziele, mit gewähltem Hintergrund dreizehn. Ein belegter identischer Eintrag endet vor der Ableitung als No-op. Recovery verwendet die bereits gebundenen Schreibseiten und prüft fremde Bytes vor jeder Änderung.
