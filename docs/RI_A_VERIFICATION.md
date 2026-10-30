# RI-A-T01: Registrierung, Betriebsgrenzen und Messung

## RI-A-N01: Nacharbeit zu B-01/B-02/B-03 · 30.10.2026

Verbindlich: [RI-A-R01](https://github.com/venomenon328/picross/pull/484#pullrequestreview-5709431225)
und [RI-A-N01](https://github.com/venomenon328/picross/pull/484#issuecomment-6517789353).
Ausgangshead `29349ffbfa9fd42d4e20e7065d2d0c4f9b721211`, korrigierter Werkzeug-
und Teststand `bca790bf4a8a0e5f32e746cc0d2e0723e3f878c8`.
Die Befunde sind aus Autorensicht behoben; das erneute unabhängige qualifizierte
Review auf dem neuen Head bleibt erforderlich. [PR #484](https://github.com/venomenon328/picross/pull/484)
bleibt Draft. O-01, RI-B/RI-C und echte Rätselintegrationen sind nicht beauftragt.

### Befundbezogene Regressionen

Alle Fälle stehen im festen synthetischen [RI-A-Testmodul](../tests/puzzle_production/test_registration_budgets.py).

| Befund | Konkrete Orakel |
| --- | --- |
| B-01 | `classification_ticks_enforce_300_before_operation_is_known`: mehrere Ticks innerhalb der Klassifikation bei 100/299/301 s; unbekannte Registrierung und Sync bleiben bis zur Zuordnung bei höchstens 300 s, auch mit langem Override. `classified_registration_uses_original_origin_and_selected_limit`: 1800/600/10 s, Klassifikationsverbrauch und 250-s-Außenrahmen, unveränderte Bytes/mtimes beim Abbruch. `classification_cannot_revive_expired_frame_or_outer_deadline`: keine Wiederbelebung abgelaufener Fristen oder Erweiterung eines verschachtelten Operationsframes. Bestehende Fälle erhalten v1-Blockade, geschlossene Generationen, vollständiges/ungültiges Staging und Originalbytebindung. |
| B-02 | `publication_and_recovery_phase_times_follow_actual_work`: echte Writer-/Recoveryaufrufe, ungleiche Uhrschritte vor Validierung, Schreiben, Flush und Bereinigung; jede Phase P0–P6/R0–R2 und alle wiederholten Dateischritte werden am Arbeitsort geprüft. Exakte Phasensummen entsprechen der verstrichenen Uhrzeit; inklusive Kinder werden nicht nochmals addiert. `timeout_in_p0_records_partial_work_before_any_mutation`: P0=1801 s, Prevalidation=0, keine P1-Arbeit/Mutation oder erfundener Fortschritt. Automatischer Rollback bleibt außerhalb der angehaltenen P3-Teilzeit. |
| B-03 | `complete_checks_count_only_successful_returns`: vier Kandidatenversuche, ein Erfolg; Fehler, I/O-Fehler und Abbruch behalten Zeit/Versuche ohne Abschlussfortschritt. `failed_export_and_input_checks_do_not_claim_completion`: Fehler und tatsächlicher Deadline-Tick innerhalb der Kandidatenverifikation liefern je einen begonnenen Input-/Export-/Kandidatenversuch, null Vollprüfungen; erfolgreicher Export je eine Vollprüfung. Innere Einzelproofs bleiben eigenständige Messung. |

22 RI-A-Tests: Linux **22,052 s**, Windows **92,115 s**, jeweils erfolgreich.
Die ausgewählten B-01/B-02/B-03-Regressionen scheitern auf `29349ffb`;
zusätzlich zeigt die direkte Gegenprobe nach einem Erfolg plus einem Abbruch
vorher `full_candidate_proof_checks=2`, nachher zwei Versuche und genau einen
Vollprüfungsabschluss. Lokale Logs: `n01-before-regressions.log`,
`n01-linux-final-tests.log`, `n01-windows-final-tests.log` unter `E:/ri478/`.

### Erneuter begrenzter Messvergleich

Drei reale Wiederholungen pro Stand auf Linux/native OverlayFS sowie Windows/NTFS
mit kurzen und normal verschachtelten Pfaden. Derselbe feste 57-Dateien-Eingang,
0→1 synthetische Katalogeinträge und 30 Exportdateien wie im historischen Vergleich.
Alle sechs vollständigen Quellinventare wurden gegen die aus den genannten
Git-Commits erzeugten Archive verglichen; Eingangsmanifest unverändert
`d754e43ffb1b8765f3eaab81d6938e19d79a092be07c60362c79f62e60d87fc4`.
Der identische aktuelle [Messtreiber](../tests/puzzle_production/ri_a_measurement.py)
(SHA-256 `dcadd6f0d676bf7504f7689e875af5527fd1e9016c5fe0cdda2eb9db1f30f5cf`)
misst beide Stände diesmal mit `--observe`, einschließlich der operativen
Phasen/Zähler. Sonstige Argumente wie unten; keine neue Inputerzeugung.

Windowspfade: `E:/ri478/n01/runs/{before,after}/<0..2>/checkout` sowie
`E:/Zeuch/Coding/ri-a-measurements/n01/project/catalog/{before,after}/<0..2>/checkout`.
Linux: `/work/n01/runs/{before,after}/<0..2>/checkout`; `stat -f` erneut OverlayFS,
Containermountliste `[]`. OS-/Python-/Pillow-/Imageversionen wie unten und in den
Rohberichten. Sequenziell je Plattform; Linux und Windows teilen die Hosthardware.
Warme Caches, keine CPU-Pinnung oder Lastkontrolle; deutliche Windowsstreuung.
Die Quellarchive besitzen keine `.git`-Metadaten: interne Export-Commitangabe
bleibt unbekannt (unter Windows sichtbare Git-Meldungen); reale Commitbindung
kommt aus dem überprüften vollständigen Quellinventar. Kein CLI-/Startkostenbeleg.

Sekunden, Median [Minimum–Maximum], n=3; Register umfasst Vorarbeit und Writer:

| Umgebung | Operation | 29349ffb | bca790bf |
| --- | --- | ---: | ---: |
| Linux | Register | 4.331 [4.143–4.366] | 4.340 [4.311–4.428] |
| Linux | Recovery | 0.297 [0.296–0.315] | 0.308 [0.308–0.351] |
| Windows kurz | Register | 24.538 [19.198–25.225] | 24.126 [23.875–25.303] |
| Windows kurz | Recovery | 1.823 [1.678–1.840] | 1.683 [1.635–1.685] |
| Windows verschachtelt | Register | 30.591 [23.609–30.643] | 28.897 [28.430–29.740] |
| Windows verschachtelt | Recovery | 2.037 [1.816–2.280] | 2.078 [2.045–2.137] |

Neue operative Publikationsphasen, Mediane in Sekunden (inklusive, keine
Addition mit ihren Unterphasen oder der gesamten Registrierungsdauer):

| Umgebung | P0 | P1 | P2 | P3 | P4 | P5 | P6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Linux | 0.2671 | 0.0054 | 0.0316 | 2.8836 | 0.5874 | 0.2950 | 0.0703 |
| Windows kurz | 0.6972 | 0.0166 | 0.1792 | 16.6250 | 3.4544 | 1.7681 | 0.3974 |
| Windows verschachtelt | 0.8283 | 0.0171 | 0.2374 | 19.9770 | 4.1534 | 2.0661 | 0.4734 |

Auf allen sechs Varianten und in jeder Wiederholung unverändert: 80 Guardaufrufe,
4 Kandidatenprüfungen, 4 unabhängige Einzelproofs, 4 Exportprüfungen, 12079
Pfadprüfungen, 6642 sichere Read-Helferaufrufe; 3627169 gelesene und 3456296
gehashte Bytes, 37 veröffentlichte Dateien/40834 Bytes. Die neuen operativen
Zähler melden für diesen positiven Registerlauf je 4 Input-/Export-/Kandidaten-
versuche und je 4 erfolgreiche Vollprüfungen. Das belegt keine fehlgeschlagenen
Versuche als vollständig. Keine weiteren Reads oder Guards wurden entfernt.

Die alten P01-Laufzeiten bleiben gültige **historische** Messungen ihrer damaligen
Quellstände; sie sind kein Laufzeitbeleg für N01. Alte operative P-/R-Labels und
Fehlerfall-Vollprüfungszähler sind durch R01 widerlegt und werden nicht übernommen.
Die damaligen extern gemessenen Funktionsaufrufe/Bytezahlen bleiben an ihren
positiven Lauf gebunden; der neue Vergleich bestätigt deren erhaltenen Umfang.
Spannweiten überlappen: keine allgemeine Beschleunigungs- oder Skalierungszusage.
Die nachfolgenden historischen Messlücken (große Kataloge, 0.4-Bestand, andere
Hardware, CLI-/Prozesskosten und komplexe Proofketten) bleiben offen. Kein realer
Messlauf erreichte 300/1800 s; deren Vertrag wird durch kontrollierte Uhr geprüft.

Rohberichte außerhalb des aktiven Trees unter `E:/ri478/`, begrenzt bis zum
Reviewabschluss; danach CI2-Aufbewahrung. Keine neue Dauerdatei/Testkopie im Repo.

| Rohbericht | SHA-256 |
| --- | --- |
| `n01-linux-before.json` | `1ff7665b59655977b81ae186bcd15f39235e78bb56a374e00914b4cc3392155b` |
| `n01-linux-after.json` | `7df9665812fe7c4f4d40e9bc814dbdf023c2c99aff53f3be121ca79cea227c2e` |
| `n01-windows-short-before.json` | `03cee9fa53f5a6406d1bf3939a6c3593f1d3ceab31c738d545a6f280d6d2247f` |
| `n01-windows-short-after.json` | `618aba5ee1d644df5b391807af8fda0370e110d1bce7bf1813a677d27b53afec` |
| `n01-windows-nested-before.json` | `f1d81def2f08d03acbf2da2eda55ab7c841bdeaf204a402a25f13a7c591c8378` |
| `n01-windows-nested-after.json` | `7511b4eb666e52edc810fd7c5e4e8648fd9dd97b48849388021e46dbaa273fbc` |

### Selbstreview und aktuelle Pflicht-CI

[Getrenntes Selbstreview](RI_A_SELF_REVIEW.md): Transaktions-/Checkpointkörper
nach Abzug reiner Beobachtungsaufrufe per AST unverändert; sichere I/O und
Methodenvertragsdateien bytegleich. 232 Werkzeugtests in 49,432 s erfolgreich,
drei bestehende Plattform-Skips. Dokumentvalidator, Whitespacecheck und exakter
Authoring-/Offline-Snapshotvergleich bestanden.

Der vollständige PR-Diff wählt `solver, images, adapter, catalog`, native
`core, history, catalog, completion, adapters, graphics, export`, Docs, Preflight
und Delivery. Browsergruppen leer, kein Chromium-Auftrag. Die abschließende
CI einschließlich `ci-required` muss den neuen Head und Test-Merge prüfen;
die exakte endgültige Head-/Base-/Test-Merge-/Run- und Ergebnisbindung wird in
PR #484 geführt. Lokale Tests und der alte grüne Lauf ersetzen sie nicht.
Offen bleibt das erneute unabhängige qualifizierte Review; kein Merge.

## Historischer P01-Vergleich vor R01/N01

Die folgenden Tabellen und Aussagen betreffen ausschließlich P01→ursprüngliches
RI-A, nicht die Nacharbeit. Historischer grüner CI-Abschluss:
[Lauf 40950193706](https://github.com/venomenon328/picross/actions/runs/40950193706),
Head `29349ffbfa9fd42d4e20e7065d2d0c4f9b721211`, Basis
`8f903d7ecb6c111451ae359ecca44156987daa19`, Test-Merge
`f00f8982932843f7ef62d78fb5a6d42340cedaea`. R01 hat danach die oben genannten
Blocker festgestellt; damaliges CI-Grün ist keine aktuelle Abnahme.

## Quellen und Messmethode

- Vorher: `main@f47a30b904a8d4eba79ca9d3f82576aebcceaa38` (P01).
- Nachher: Produktcode `a2c28518cead1f29f0fdc64afe0b65769947eded`. Die Test-/Dokumentkorrekturen bis `29349ffb` änderten diese gemessenen Werkzeugbytes nicht; N01 wird oben neu gemessen.
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

### R02-B01-Korrektur auf dem bestehenden PR (eigener Umsetzungsstand)

Nach dem unabhängigen [RI-A-R02](https://github.com/venomenon328/picross/pull/484#pullrequestreview-5710915426)
ist die zu strenge 300-s-Vorfrist bei bereits identifizierter
Registrierungs-Recovery korrigiert: Die erste sichere vollständige Lektüre der
Originaljournalbytes bleibt zunächst im konservativen Rahmen. Ein kleiner
begrenzt arbeitender, nicht autorisierender Top-Level-Discriminator prüft
danach vor der vollständigen teureren JSON-/Journalvalidierung nur zulässige
Format-/Operationspaarung und die obligatorischen Top-Level-Feldformen.
Nur bei passender Registrierung darf der Schutz vom ursprünglichen
Aufrufbeginn auf 1800 s beziehungsweise den festgelegten Override wechseln.
Abgelaufene Anfangs- und äußere Fristen bleiben abgelaufen;
fremde, unvollständige oder widersprüchliche Paare erhalten keine Erweiterung.
Alle bisherigen vollständigen Byte-, Schema-, Quellen-, Delta- und Lockchecks
bleiben vor jeglicher Mutation Pflicht.

Neue feste Uhr-Gegenproben prüfen erfolgreiche gültige Registrierungs-Recovery
nach 301 s strikter Klassifikationsarbeit innerhalb von 600/1800 s, die
konservative Grenze vor Erkennung, unzulässige Format-/Operationspaare
und nicht autorisierende Vorzuordnung bei ungültigen inneren Journalbytes.
Der vorhandene Klassifikationstest ist auf die tatsächlich *noch nicht*
erfolgte frühe Zuordnung angepasst, statt die widersprochene harte
300-s-Grenze nach sicherer Registrierungserkennung weiter festzuschreiben.

**Ausführungsnachweise:** Stand, Ergebnis, tatsächliche CI-Bindung und getrenntes
Review sind an den neuen PR-Head zu binden. Die vorherigen Messreihen bleiben
historische Quellen; keine neue Laufzeitverbesserung aus Uhrsimulation ableiten.
