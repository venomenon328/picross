# PE-MIG1/M2 · befristete Revieworiginale

Nur für **PE-MIG1-M2-A01**, unabhängiger technischer Reviewer von
[Draft-PR #644](https://github.com/venomenon328/picross/pull/644).
Produkthead `7e14963525ec9a6f82064535ecbca263be3270dc`,
Basis `15ceb9b8fe54e2003883d623d1358d3cfc2d062d`,
GitHub-Testmerge `25e882ddbf12c3454348297d19841a56d02e7eed`.
Maßgeblich sind die [M2-Paketentscheidung](https://github.com/venomenon328/picross/issues/641#issuecomment-6881046691)
und die ausdrücklich beauftragte [enge Readerkorrektur](https://github.com/venomenon328/picross/issues/641#issuecomment-6881270569).

**Ablauf: 21.11.2026, 17:00 UTC.** Zweck und Empfänger stehen auch im
`manifest.json`. Keine dauerhafte Regressionssammlung, kein Merge-PR dieses
Refs nach main. Zuständiger Implementierer prüft bei Ablauf den tatsächlichen
Reviewbedarf und baut den eigenen Belegref im beauftragten Rahmen zurück;
bei weiter offenem Gate muss die Zustellung neu entschieden werden. Keine
automatische Löschung oder dauerhaft garantierte Verfügbarkeit behauptet.
Lokale Arbeitsdaten werden nach Remoteprüfung bereinigt; M1-Reste und fremde
Refs gehören nicht dazu.

## Was tatsächlich geändert wurde

114 Datenpfade: exakt 56 Reveal-v4- und 56 Hintergrund-v6-Quellen sowie
Inhaltsregistry und Runtime. Zusätzlich Paketplan, Importreader, ein kleiner
synthetischer Test und dessen fachliche Importpräzisierung: **118 Produktpfade**.
Keine Definition, Palette, Matrix, Hinweise, Save-/Logikrevision, ID/Key/Slot,
aktuelle Namen/Kategorien, Difficulty/Added, Bildbytes, Notice, Produktionspakete,
Freigaben oder Reports verändert. Die 20 Kategorien bleiben gleich.

26 alte Revealentscheidungen behalten Bildrevision 1, ihre neue technische
Recordrevision ist 2. 30 bisher sourcefreie Reveals erhalten initiale technische
Bild-/Recordrevision 1. Die drei selected-Hintergründe behalten Bildrevision 1,
Status und Assetref; ihre neue technische Recordrevision ist 2. Die übrigen 53
werden explizit von `legacy/null/null` nach `standard/1/null` projiziert und
erhalten Recordrevision 1. Das sind initiale technische Quellen, **keine neue
menschliche Bild-/Standardentscheidung**. Sechs geschlossene Felder, kein
erfundenes origin/authority/actor/provenance.

## Originale und ihre Bindung

- `migration-plan-final.json`: vor dem echten Apply erzeugte vollständige
  Inventarbindung und exakt vorbereitete Alt-/Neubytes/Hashes aller 114 Ziele.
  `final-plan-review.json` prüft die erlaubte Deltamatrix mit einem getrennten
  Oracle. `apply-final.log` ist die tatsächliche Übernahmequittung.
- `postcomparison-noop.json`: vollständiger Vorher/Nachher-Dateivergleich,
  exakt erlaubte 118-Pfadmenge und beide vollständigen No-op-Wege: alter Plan
  nochmals übernehmen sowie neu planen/übernehmen. Je alle **1.716 Dateien**
  byte- und mtimegleich, kein Lock/Journal/Temp im Produktcheckout.
- `migrate_m2.py`: enger **externer Einmal-Runner**, nicht im Produkt-PR oder
  im Editor/Starter/API. Vollständiger Quell-/Namespacevergleich vor und unter
  gemeinsamem Lock; exklusiv publiziertes dauerhaftes Journal, sichere lokale
  Altbyteguards, atomare Veröffentlichung, Runtime zuletzt und gezielter Readback.
  Sein eigener expliziter `rollback` prüft Journal, alle Eigen-/Fremdbytes und
  eine unabhängig rekonstruierte vollständige Altansicht vor Mutation.
  Unbekannte Journale/Stagingreste bleiben erhalten. Normales Editor-Recovery
  wird um diese temporäre Journalgeneration nicht erweitert.
- `guard-rollback.json` / `probe_m2.py`: zehn tatsächlich ausgeführte positive
  Negativ-/Recoveryfälle und ein nicht ausführbarer Datei-Symlinkfall
  (`WinError 1314`, keine Rechteänderung). Abbrüche nach Journal, erster Quelle,
  vor Runtime und nach Runtime: jeweils exakter Rollback, erneuter Rollback
  No-op. Fremde Recoverybytes bleiben mit Journal erhalten. Ergänzend
  `junction-guard.json`: echter Windows-Verzeichnisjunction wird beim Apply
  vor Mutation zurückgewiesen; 1.726 Dateien/mtimes des Testziels unverändert.
- Diese Guardfälle verwenden `migration-plan.json` und
  `guard-ci-package.json` am unveränderten Ausgangscode. Nach der ausdrücklich
  erweiterten Reader-/CI-Änderung wurde der finale Plan neu erzeugt und erneut
  unabhängig geprüft. **Alle 114 Alt-/Neudatenpaare beider Pläne sind exakt
  gleich**; nur die mitgebundenen vier Code-/Dokument-/Paketplandateien ändern
  sich. Der echte Produktlauf und beide No-ops verwenden den finalen Plan.
- `reader-all56.json`: echte `editor_cli list/detail`-Prozesse und gemeinsame
  Reveal-/Hintergrund-/Produktionsresolver für alle 56 migrierten IDs in der
  zweiten isolierten Kopie. `editor-preview-all56.json` ergänzt den echten
  Editorworker, Raster und bytegebundene Bild-/Papier-/Kategorie-Vorschaupfade
  für jede ID. `final-product-reader.json` liest nach den Testmutationen im
  **unveränderten finalen Produktcheckout** alle 56 Quellenpaare und Bindungen
  gezielt erneut zurück.
- `editor-plan-apply.json`, vier Request-/Planpaare und `editor_probe.py`:
  wirkliche Metadaten-, Bild-, Präferenz- und Rasterübernahme **nur** in der
  zweiten Kopie. Der Bildinput ist eine bytegleiche Kopie der vorhandenen
  Drachenfrucht-PNG; die Rasterprobe verwendet eine klar getrennte 2×2-Testmatrix
  samt tatsächlichem Solver-/Rating-/Proofweg. Die vorbereiteten Planseiten
  enthalten die benötigten Originalbytes. Keine neue kreative Bildproduktion.
- `import-reader-blocker.log` dokumentiert den tatsächlichen v6-KeyError vor
  Korrektur. `import-unit.log`: 13 erfolgreiche gezielte Importtests;
  `local-core.log`: 21 Kernprüfungen, Dokumentvalidator und ihre Grenzen.
  Vorhandene historische TXT-Dateien bleiben erhalten und hashgebunden;
  kompakte Quellen erhalten keine neue Notice-/Herkunftspflicht.

Die Originalscripte sind gezielte aktuelle Nachweise, keine neue Dauersuite.
Für eine eigene Runnerreproduktion einen **neuen** isolierten Checkout der
Basis verwenden; für den finalen Plan dessen vier Nichtdaten-Dateien exakt aus
dem Produkthead übernehmen. Python/Pillow 12.3.0 isoliert betreiben,
`PYTHONDONTWRITEBYTECODE=1` und eigene externe TEMP-/Planablage setzen.
`migrate_m2.py plan --root CHECKOUT --plan EXTERN_NEU.json`, anschließend
Plan wirklich prüfen, dann `apply --root CHECKOUT --plan EXTERN_NEU.json`.
Bei Unterbrechung nur den eigenen expliziten `rollback --root CHECKOUT`
verwenden; ein fremdes oder unsicheres Journal bleibt ein Blocker.

## Gezielte echte Spieleroriginale

Windows, Godot **4.7.2-stable official ed1daf0bf**, OpenGL 3.3,
NVIDIA GeForce RTX 3070. Der Programm-/Datenstand stammt vom Produkthead;
Engineimport und Prozesse ausschließlich in eigener separater Spielkopie und
eigenen leeren Profilen. Keine echte SaveStore-/Benutzersave-Migration,
kein persönliches Probespielen und keine Browserabnahme.

`player-source-inventory.json`, `godot-import.log` und
`player-import-report.json` binden alle drei echten selected-PNGs, Notices,
Importparameter, tatsächliche Remaps und elf Mipmaps je Bild. Die Quellbytes
sind unverändert. `player/player-probe.json` liest alle 56 echten Definitionen
und Revealtexturen, baut 56 Spielersessions und prüft vier gezielte Öffnungen.
Der erste Prüfhelfer wartete die nachgelagerte Übergangsbarriere nicht ab;
dieser Prüfhelfer wurde korrigiert und der vollständige finale Lauf erfolgreich
wiederholt. Keine entsprechende Produktkorrektur vorgenommen.

Genau **fünf unveränderte PNG-Originale** werden für die erforderliche Sichtung
zugestellt, mit Bytezahl, Auflösung und SHA-256 in `render-inventory.json`:

| Original | Tatsächliches Szenario |
| --- | --- |
| `player/category-visible-standard.png` | Seepferdchen, 1920×1080; beide bestehenden Wasserwelt-Randzeichnungen sichtbar. |
| `player/category-visible-legacy.png` | Dieselbe tatsächliche Szene mit alter Legacyprojektion nur im Reader-Speicher. **Exakt gleiche Pixel und PNG-Bytes**; keine Quelldatei geändert. |
| `player/case-2-selected.png` | Birne, 1280×720; reales selected-Bild rechtzeitig geladen, sichtbar und auf Bildrevision 1 gebunden. |
| `player/reveal-pz-00f37200bcee4d548e2c910ce551d077.png` | Aktuelles Drachenfrucht-Reveal aus bisher sourcefreier Produktion in echter Abschlussdarstellung. |
| `player/reveal-pz-023b50b44d1c4698a6e17e65b6ea4337.png` | Aktuelles Ho-Chi-Minh-Reveal aus alter AT-v1-Quelle in echter Abschlussdarstellung. |

`category-probe.json` prüft sichtbar platzierte Kategoriezeichnungen und
vollständige Pixelequality. Bei der kleineren 1280er Ausgangsprobe sind
Kategoriezeichnungen layoutbedingt ausgelassen; für deren Sichtbeleg wurde
deshalb gezielt die sichtbare 1920er Szene geprüft. Die übrigen dort erzeugten
kleinen Kontrollaufnahmen wurden im Lauf verglichen und nicht zusätzlich
zugestellt (`delivered=false` im Renderinventar). Ihre Namen im unveränderten
Originalbericht behaupten keine Verfügbarkeit. Die fünf oben benannten Dateien
sind die Revieworiginale; keine pauschale Galerie des Bestands.

`reveal-probe.json` und `m2_reveal_probe.gd` kennzeichnen die abgeschlossenen
Zellen ausdrücklich als **reine Speicher-Testzustände** der eigenen Instanz.
Die echte Completion-/Revealkomponente rendert die unveränderten aktuellen
Assets. Das ist keine erspielte Eigentümerfreigabe und kein Nutzersave.
Originale lokal geöffnet: sichtbare Kategoriezeichnung, eigenes Bild,
Papierdurchsicht und beide Revealansichten überprüft; diese Selbstsichtung
ersetzt A01 nicht.

## Zugriff und verbleibende Gates

`manifest.json` bindet die übrigen gelieferten Originale mit echten Größen und
Hashes; vor eigenem Urteil Originalbytes vom **konkreten Belegcommit** laden,
gegen dieses Manifest prüfen und die fünf PNGs tatsächlich öffnen. Für Dateien
über 1 MiB einen binärfähigen Raw-/Contents-Download oder Git verwenden;
ein leeres Contents-Feld ist kein geöffnetes Bild. Keine verkleinerte Vorschau
als Original ausgeben. Der Lieferkommentar im PR nennt den überprüften Zugang.

Aktuelle CI und finales Selbstreview stehen im PR. **PE-MIG1-M2-A01 bleibt
offenes unabhängiges Vor-Merge-Gate; PE-B-U01 bleibt persönliche Eigentümerprobe
vor Release.** Kein Merge und kein Abschluss von #576 durch diese Lieferung.
