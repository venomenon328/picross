# RI-A-T01: Registrierung, Betriebsgrenzen und Messung

RI-A-V01/P01 zu [#478](https://github.com/venomenon328/picross/issues/478).
Drei wiederholte Vorher/Nachher-Läufe pro Plattform/Pfad sind abgeschlossen.
Die kleine feste Registrierung benötigt nachher im Median 5,004 s unter Linux,
25,930 s auf kurzem Windows-Pfad und 32,838 s auf verschachteltem Windows-Pfad.
Das ist keine Abnahme großer Kataloge. Der unabhängige RI-A-R01 bleibt offen;
[PR #484](https://github.com/venomenon328/picross/pull/484) bleibt Draft. Kein Merge.

## Quellen und Messmethode

- Vorher: `main@f47a30b904a8d4eba79ca9d3f82576aebcceaa38` (P01).
- Nachher: Produktcode `a2c28518cead1f29f0fdc64afe0b65769947eded`. Spätere Test-/Dokumentkorrekturen ändern diese gemessenen Werkzeugbytes nicht.
- Treiber: [ri_a_measurement.py](../tests/puzzle_production/ri_a_measurement.py), identisch auf beiden Ständen; SHA-256 `62c2ef840b2df0edcd1a1ac25c35f54c84ed98cf02fbddd862a77ab125efb820`.
- Einmalig erzeugter, danach unveränderter `direct-mono`-Eingang: 57 inventarisierte Dateien einschließlich eines Exports mit 30 Dateien. Katalog vorher 0, nachher 1 synthetischer Eintrag; explizit vorgeprüfter 0.3-Ratinginput, keine echte Katalogdatei.
- Eingangsmanifest SHA-256 `d754e43ffb1b8765f3eaab81d6938e19d79a092be07c60362c79f62e60d87fc4`. Alle sechs Berichte besitzen identische Eingangs- und Treiberbindung; die vollständigen Quellmodul-Hashes stimmen je Vorher/Nachher mit den genannten Git-Objekten überein.
- Drei Wiederholungen je Variante, jeweils frischer Katalog. Gleiche Argumente, keine erhöhte Testausnahme, kein Überschreiben eines Ergebnisses. Setup, Export, Plan, Registrierung und separate Recovery nach injiziertem Abbruch werden tatsächlich ausgeführt. Die erste Inputs-Erzeugung ist nicht Teil der Laufzeiten.
- Instrumentierte API-Aufrufe mit demselben Treiber: er zählt tatsächliche Funktionsaufrufe, gelesene/gehashte Bytes und veröffentlichte Dateien. Keine Ergebniswiederverwendung. Reproduzierbarer Aufruf: `python ri_a_measurement.py --repo <quellbaum> --inputs <feste-inputs> --work <neuer-ordner> --output <bericht.json> --source <commit>`; einmaliges `--prepare` erzeugt nur synthetische Inputs.

## Umgebung

Windows: Windows 11 Build 26200, Python 3.13.14 AMD64, Pillow 12.3.0 in eigener venv, Laufwerk E: NTFS. Kurz: `E:/ri478/final/{old,new}/<0..2>/checkout`; verschachtelt: `E:/Zeuch/Coding/ri-a-measurements/final/project/catalog/{old,new}/<0..2>/checkout`. Die jeweiligen Vorher-/Nachher-Pfade sind gleich tief.

Linux: Kernel `6.18.33.2-microsoft-standard-WSL2`, glibc 2.41, Python 3.13.18, Pillow 12.3.0 in eigener venv; Docker-Image `python:3.13-slim`, Digest `sha256:2d44738ebf4ce5f63b9d9ea871e9c7cfdc0426f7b0c97cac915fd88ded1d86bb`. Messpfad `/work/final/{old,new}/<0..2>/checkout`: `stat -f` bestätigt `overlayfs`, Container-Mountliste `[]`; kein Windows-Bindmount. Quellen/Inputs wurden zuvor in dieses native Linux-Dateisystem kopiert.

Gemessen wurde sequenziell pro Plattform mit normalen warmen Dateisystemcaches; kein Cache-Flush, keine CPU-Pinnung oder Garantie völliger Fremdlastfreiheit. Plattformen verwenden unterschiedliche Python-Patchstände; nur Vorher/Nachher innerhalb derselben Umgebung ist ein kontrollierter Vergleich.

## Reale Laufzeiten

Alle Angaben Sekunden: Median [Minimum–Maximum], jeweils n=3. API-Gesamtdauer `register` enthält Input, Snapshot/Plan, Staging und Writer. Inklusive Unterphasen sind nicht additiv.

| Umgebung | Phase | Vorher | Nachher |
| --- | --- | ---: | ---: |
| Linux / OverlayFS | Katalog-Setup | 0.003 [0.002–0.003] | 0.003 [0.003–0.003] |
| Linux / OverlayFS | Export | 0.058 [0.054–0.068] | 0.056 [0.053–0.063] |
| Linux / OverlayFS | Plan | 0.189 [0.185–0.196] | 0.191 [0.184–0.212] |
| Linux / OverlayFS | Register gesamt | 5.108 [4.961–5.153] | 5.004 [4.853–5.109] |
| Linux / OverlayFS | Recovery-Setup | 0.003 [0.003–0.003] | 0.002 [0.002–0.003] |
| Linux / OverlayFS | Registrierung bis injiziertem Abbruch | 0.691 [0.678–0.705] | 0.661 [0.655–0.702] |
| Linux / OverlayFS | Recovery gesamt | 0.360 [0.342–0.372] | 0.351 [0.342–0.376] |
| Windows / kurz | Katalog-Setup | 0.006 [0.005–0.008] | 0.006 [0.005–0.011] |
| Windows / kurz | Export | 0.380 [0.379–0.455] | 0.370 [0.368–0.373] |
| Windows / kurz | Plan | 0.928 [0.912–1.059] | 0.952 [0.932–0.967] |
| Windows / kurz | Register gesamt | 27.212 [26.697–28.609] | 25.930 [25.670–25.994] |
| Windows / kurz | Recovery-Setup | 0.005 [0.005–0.009] | 0.006 [0.005–0.006] |
| Windows / kurz | Registrierung bis injiziertem Abbruch | 2.516 [2.499–2.631] | 2.614 [2.564–2.661] |
| Windows / kurz | Recovery gesamt | 1.865 [1.854–2.026] | 1.903 [1.787–2.044] |
| Windows / verschachtelt | Katalog-Setup | 0.005 [0.005–0.012] | 0.005 [0.005–0.010] |
| Windows / verschachtelt | Export | 0.393 [0.389–0.453] | 0.379 [0.371–0.401] |
| Windows / verschachtelt | Plan | 1.029 [1.020–1.053] | 0.942 [0.930–0.970] |
| Windows / verschachtelt | Register gesamt | 35.354 [33.729–35.939] | 32.838 [32.816–33.160] |
| Windows / verschachtelt | Recovery-Setup | 0.004 [0.004–0.005] | 0.005 [0.005–0.007] |
| Windows / verschachtelt | Registrierung bis injiziertem Abbruch | 3.011 [2.943–3.022] | 3.015 [2.945–3.064] |
| Windows / verschachtelt | Recovery gesamt | 2.429 [2.405–2.506] | 2.462 [2.430–2.481] |

Unterphasen des vollständigen Registrierungsaufrufs, ebenfalls inklusive:

| Umgebung | Gemessener Aufruf | Vorher | Nachher |
| --- | --- | ---: | ---: |
| Linux / OverlayFS | Snapshot | 0.013 [0.013–0.014] | 0.011 [0.010–0.012] |
| Linux / OverlayFS | Plan-/Journalvorbereitung | 0.157 [0.148–0.158] | 0.157 [0.148–0.160] |
| Linux / OverlayFS | Gemeinsamer Writer inkl. Vorprüfung/P0–P6 | 4.856 [4.715–4.917] | 4.769 [4.608–4.860] |
| Linux / OverlayFS | Alle Guards des register-Aufrufs | 4.152 [3.998–4.220] | 4.048 [3.898–4.123] |
| Linux / OverlayFS | Alle Staging-/Checkoutprüfungen | 0.090 [0.083–0.091] | 0.090 [0.087–0.090] |
| Linux / OverlayFS | Verzeichnis-Durability | 0.199 [0.191–0.223] | 0.205 [0.201–0.222] |
| Linux / OverlayFS | OS-fsync | 0.350 [0.345–0.384] | 0.365 [0.358–0.374] |
| Windows / kurz | Snapshot | 0.074 [0.071–0.075] | 0.063 [0.061–0.065] |
| Windows / kurz | Plan-/Journalvorbereitung | 0.662 [0.646–0.679] | 0.626 [0.625–0.707] |
| Windows / kurz | Gemeinsamer Writer inkl. Vorprüfung/P0–P6 | 26.052 [25.546–27.435] | 24.750 [24.573–24.895] |
| Windows / kurz | Alle Guards des register-Aufrufs | 23.831 [23.378–25.147] | 22.603 [22.467–22.746] |
| Windows / kurz | Alle Staging-/Checkoutprüfungen | 0.374 [0.371–0.385] | 0.356 [0.356–0.418] |
| Windows / kurz | Verzeichnis-Durability | 0.105 [0.104–0.116] | 0.107 [0.105–0.112] |
| Windows / kurz | OS-fsync | 0.117 [0.107–0.134] | 0.099 [0.099–0.111] |
| Windows / verschachtelt | Snapshot | 0.105 [0.095–0.115] | 0.084 [0.083–0.093] |
| Windows / verschachtelt | Plan-/Journalvorbereitung | 0.730 [0.697–0.770] | 0.716 [0.699–0.794] |
| Windows / verschachtelt | Gemeinsamer Writer inkl. Vorprüfung/P0–P6 | 34.127 [32.422–34.680] | 31.613 [31.459–31.964] |
| Windows / verschachtelt | Alle Guards des register-Aufrufs | 31.578 [29.867–31.953] | 29.007 [28.911–29.392] |
| Windows / verschachtelt | Alle Staging-/Checkoutprüfungen | 0.361 [0.339–0.369] | 0.359 [0.349–0.408] |
| Windows / verschachtelt | Verzeichnis-Durability | 0.106 [0.105–0.108] | 0.110 [0.104–0.112] |
| Windows / verschachtelt | OS-fsync | 0.171 [0.164–0.202] | 0.164 [0.159–0.172] |

## Tatsächliche Zähler

Diese Aufruf-/Bytezahlen sind innerhalb der drei Wiederholungen gleich. Read-Zähler zählen Aufrufe von `catalog_io.read`, einschließlich festgestellter Abwesenheit; sie sind keine OS-read-Syscallzahl. Der neue fehlend-erlaubte Read erklärt zusätzliche Read-Helferaufrufe bei weniger Pfadprüfungen.

| Vollständiges register, alle drei Umgebungen | Vorher | Nachher |
| --- | ---: | ---: |
| Kandidatenprüfung | 4 | 4 |
| Einzelproof-Verifier | 4 | 4 |
| Vollständige Exportprüfung | 4 | 4 |
| Vollständige Guards | 80 | 80 |
| Pfadprüfungen | 12363 | 12079 |
| Sichere Read-Helferaufrufe | 6191 | 6642 |
| Methodenfreeze-Prüfungen | 14 | 14 |
| Vollständige Staging-/Checkoutprüfungen | 3 | 3 |
| Verzeichnisflushs | 127 | 127 |
| Bytes aus catalog_io-Reads | 3627169 | 3627169 |
| Bytes an catalog_io.checksum | 3456296 | 3456296 |
| Veröffentlichte Dateien | 37 | 37 |
| Veröffentlichte Bytes | 40834 | 40834 |

| Umgebung | Geprüfte Pfadkomponenten vorher → nachher | OS-fsync vorher → nachher |
| --- | ---: | ---: |
| Linux / OverlayFS | 131755 → 129626 | 196 → 196 |
| Windows / kurz | 132527 → 130398 | 69 → 69 |
| Windows / verschachtelt | 180435 → 177170 | 69 → 69 |

Unter POSIX enthält `os.fsync` auch die 127 Verzeichnisflushs; Windows verwendet dafür `FlushFileBuffers`. Deshalb ist 196 gegenüber 69 kein abweichender fachlicher Schreibumfang. Export/Plan/Register behalten 2/2/4 vollständige Kandidaten- und Einzelproofprüfungen (acht im normalen Ablauf). RI-B bleibt unberührt.

Die zusätzliche sichere Recoveryklassifikation liest die Originaljournalbytes erneut: gemessene Readbytes 227195 → 267351, Hashbytes unverändert 42298. Windows-Recovery verbessert sich in dieser Messung nicht durchgängig. 300/1800 s wurden in keinem realen Messlauf erreicht; ein ausgebliebener Timeout wird nicht als Beschleunigung ausgegeben.

## Aussagegrenzen und Auswertung

284 weniger Pfadprüfungen je Registrierung (−2,30 %) sind direkt belegt. Die Registrierungsmediane liegen um 2,04 % (Linux), 4,71 % (Windows kurz) und 7,11 % (Windows verschachtelt) niedriger. Linux-Spannweiten überlappen; keine statistische oder allgemeine Leistungszusage. Guards dominieren weiterhin. Aus dieser Auswertung folgt kein Auftrag zur Guardausdünnung oder Proofwiederverwendung.

Offene Messabdeckung: große/echte Kataloge und aktiver 0.4-Bestand, nackte Linux-Hardware statt WSL2, andere Datenträger/OS-Versionen, CLI-Prozessstart-/stdout-/stderr-/Berichtskosten, harte OS-Blockaden sowie komplexe Reparatur-/Paarproofkorpora. Der Betriebsbericht zählt zusammengesetzte vollständige Kandidaten-/Proofaufrufe an der Adaptergrenze; innere Einzelproofs bleiben dort ausdrücklich unbekannt. T01 zählt für den festen Direktimport zusätzlich die wirklichen Verifieraufrufe. Read-/Hashbytes decken nur die genannten Helfer ab. Unbekannt bedeutet nicht null Arbeit.

Die sechs Rohberichte mit Eingangs-/Quellinventaren liegen für den laufenden Review außerhalb des Repositorys unter `E:/ri478/`; sie bleiben begrenzt bis zum Arbeits-/Reviewabschluss, danach gelten CI2-Aufbewahrungsregeln. Keine gespeicherten Rätselkopien oder neuen Dauerjobs im aktiven Tree.

| Rohbericht | SHA-256 |
| --- | --- |
| `final-linux-before.json` | `9adec8fcf7ecc9ac9067c5945a67db22287b12d32e00a8b42db2ba61721fbef1` |
| `final-linux-after.json` | `0cbcabbf774e1bb1955f1cecc138cfdfb2a09ba6017d8d15b34869bf9a6845b3` |
| `final-windows-short-before.json` | `9d450615302aa02c57c37597180955bcf30903f6319cc3985d73bebe75df5dd6` |
| `final-windows-short-after.json` | `d8b294391ebb42d8b84cb2a966a310a12d1124dc9a5526fcb7a112a33f0d8995` |
| `final-windows-nested-before.json` | `a35609c8098829389d141e1665e4230e4ec6047d877717102c64d5ce89e60723` |
| `final-windows-nested-after.json` | `bded63ccd889d6b78f028d30884abbebc23ea39b17caa54bbfef5a5ab2779289` |

## Funktionsprüfung, Selbstreview und CI

- 16 feste neue RI-A-Tests: positive 300-s-Warnung mit späterem Erfolg; Ablauf vor Mutation, während Publikation und Recovery; wiederholte Recovery; kürzere Außenbudgets und Dauerabschluss nach P6; nichtendliche/falsche Parameter; fremde Bytes, geänderte Identitäten, Alias/Hardlink/Dateityp; No-op-Bytes/mtime; Journal-/Stagingklassifikation und nachträglicher Bytetausch; anderer Recoverydefault 300; Berichtskollision und Berichtsfehler nach Commit.
- Linux: 23 gezielte RI-A- und historische Recoverytests erfolgreich in 24,644 s. Windows: 17 RI-A-/CLI-Negativtests einschließlich der korrigierten Additivhülle erfolgreich in 79,073 s.
- 232 Werkzeugtests auf Windows erfolgreich in 65,085 s; drei plattformbedingte Skips. Dokumentvalidator, vollständiger Diffcheck, exakter Offline-Snapshot und Bytevergleich beider Methodenfreezes erfolgreich. Guard-Körper per AST gegen P01 unverändert.
- [Getrenntes Selbstreview](RI_A_SELF_REVIEW.md); dies ersetzt kein unabhängiges RI-A-R01.
- Vollständige automatische Auswahl: `solver, images, adapter, catalog`; native `core, history, catalog, completion, adapters, graphics, export`; außerdem Docs, Preflight und Delivery. Browsergruppen leer, kein Chromium-Auftrag.
- Erster CI-Lauf stoppte am zusätzlichen Leerzeilenabschluss der neuen Testdatei; korrigiert in `27c531f6d9d0d0cbb7868bcd1d83c995e75edcfb`. [Lauf 40948421511](https://github.com/venomenon328/picross/actions/runs/40948421511) prüft Head `27c531f6…`, Base `8f903d7e…`, Test-Merge `7e268ee7219541c741a9e209f84f6d1220e73a93`: 382 Fachtests, zwei Fehler in der bisherigen exakten CLI-JSON-Erwartung für das neue Diagnosefeld. Fachliche Blockade, Exit 2, beide Integrationen und alle RI-A-Fälle bestanden. Die Erwartung wurde ausdrücklich um die additive Diagnose erweitert, ohne alte Felder oder Byteprüfungen zu lockern.
- Der korrigierte vollständige Lauf und `ci-required` müssen auf dem endgültigen PR-Head erfolgreich sein. Dessen exakte Head-/Base-/Test-Merge-/Run-Bindung wird in PR #484 geführt; fehlende oder rote Checks gelten nicht als Pass.

Offen vor Merge: unabhängiger qualifizierter RI-A-R01 sowie bis zum tatsächlichen grünen Abschluss das CI-Ergebnisgate. Keine neue Ausnahme vom Ergebnisgate. Keine RI-B-/RI-C-Implementierung und keine echte Rätselintegration.
