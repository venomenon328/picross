# RI-B-T01: Prozesslokaler Paketprüfkontext

## Auftrag, Vertrag und Quellen

Beauftragt: #479 auf `feat/479-ri-b-verified-context`, Basis
`864c4e6289df15ea7b3522b850542ece3489160f` (RI-A/PR #484).
RI-B-V01 wurde vor der ersten Codeänderung am 30.10.2026 im
[Issue #479](https://github.com/venomenon328/picross/issues/479) gespeichert und
exakt zurückgelesen (`updatedAt=2026-10-30T15:08:53Z`); der unabhängige
[B/C-Schnittstellenabgleich](https://github.com/venomenon328/picross/issues/480)
ebenso (`15:08:58Z`). Die frühere Kontoblockade ist behoben.
Keine echte Rätselintegration, kein Merge und kein Chromiumauftrag.

RI-A-T01/N01 meldete historisch 4 Kandidaten-/Proof-/Exportprüfungen und
80 Guards je Registrierung; Export/Plan/Register 2/2/4. Historische
Registermediane Linux/Windows kurz/verschachtelt: 4,340/24,126/28,897 s;
P3 2,8836/16,6250/19,9770 s. Guards dominieren. Das sind keine Messungen
der aktuellen A-Basis oder des neuen B-Codes. Deshalb wird A erneut gemessen.

## Fachnachweise

Das neue [Testmodul](../tests/puzzle_production/test_registration_verification.py)
erweitert kleine unabhängige synthetische Fälle. Ein unveränderliches Export-
Grundfixture wird isoliert kopiert; keine echten Kataloginputs oder Cachematrix.

| Vertrag | Nachweis |
| --- | --- |
| B01/B02 | Tatsächlich erfolgreicher Eingang plus unabhängiger Staging-Replay; spätere P3/P5-Nachprüfungen kontrollieren vollständige sichere Inventare, Bytes und Identitäten. Byte-/Freigabeänderung, zusätzliche/fehlende Dateien, leeres Zusatzverzeichnis, bytegleicher Datei-/Stagingaustausch und Austausch des geschriebenen Pakets werden abgewiesen. |
| B01/B03 | Originalexport, Checked-Datei samt Identität, Ausgangssnapshot, vollständiges Journal, Addition-Mapping und tatsächliche Methoden-/Werkzeugbytes sind gebunden. Geänderte Kategorie bleibt durch die eigenständigen vollständigen Guards blockiert. Externes Pass-Objekt, rekonstruierte/kopierte/serialisierte, fremde Prozess-/Thread- oder beendete Instanz autorisieren keine Wiederverwendung. Fehlgeschlagener Replay erzeugt keinen aktiven Kontext. |
| B04/B05/B06 | Plan bleibt lesend und vollständig prüfend; positiver Registerlauf zählt zwei vollständige Kandidatenprüfungen, zwei gebundene Nachprüfungen und weiterhin exakt 80 Guards. Runtime-Definition/Reveal sind bytegleich zum Export. No-op erhält Bytes/mtimes; Updates und getrennte Befehle behalten ihren bisherigen Weg. |
| B07 | Gewöhnlicher Fehler, Ressourcenabbruch und Crash entziehen den Kontext. Automatischer/expliziter Rollback erhält den Altzustand. Fremde Bytes blockieren Recovery ohne Mutation; nach kontrollierter Rückgabe eigener Bytes gelingt sie ohne Kontext. Bestehende RI-A-Uhr-/Budget-/Journalregressionen bleiben aktiv. |

Globale Guard-Aufrufstellen/-frequenz, P0–P6/R0–R2 und Recoverysemantik bleiben
unverändert. Keine neue Journalgeneration; beide Methodenfreezes bleiben bytegleich.
Die eigenständigen Quell-/Namespacebindungen sind keine Autorität des B-Paketbeweises.

## RI-B-T01 · Tatsächlicher Plattformvergleich

Werkzeugbasis A: `864c4e6289df15ea7b3522b850542ece3489160f`; gemessener
B-Werkzeug-/Testhead: `a46d7c9945d2f06af7a5943ca4c9504a829fc59f`.
Alle Dateien beider vollständigen Werkzeugbäume wurden byteweise gegen diese
Git-Objekte geprüft; jedes Quellinventar aller sechs Berichte stimmt mit dem
jeweiligen Baum überein. Nachfolgende T01-/Reviewtexte und die unten erklärte
reine Testhakenkorrektur ändern keine gemessenen Werkzeugbytes.
Finale PR-Head-/Basis-/Test-Merge-/Runbindung und
CI-Ergebnisse werden im ausdrücklich benannten RI-B-T01-CI-Anhang im PR geführt.

Der unveränderte vorhandene manuelle RI-A-Treiber lief mit `--observe`,
SHA-256 `dcadd6f0d676bf7504f7689e875af5527fd1e9016c5fe0cdda2eb9db1f30f5cf`.
Einmal unter A erzeugte, danach vollständig inventarisierte identische Inputs:
57 Dateien ohne das Inventar selbst, 30 Exportdateien, Katalog 0→1;
fester synthetischer Direktimport mit explizit geprüftem 0.3-Rating, keine
echten Katalogdaten. Eingangsmanifest SHA-256
`00e26594215d39c4c7a400ab2e89cb4e4f800f43f048378f8737ac939710d42a`.

Je drei reale Wiederholungen, immer frischer Katalog, ohne Budgetausnahme.
Windows 11 Build 26200 / Python 3.14.7 AMD64 / NTFS C:, Linux WSL2-Kernel
`6.18.54.1-microsoft-standard-WSL2` / Python 3.14.4 / natives ext4
(`stat -f`: ext2/ext3, 4096-Byte-Blöcke). Je isoliert Pillow exakt 12.3.0.
Linuxquellen, Eingänge und Messcheckouts liegen unter einem eigenen
`/var/tmp/picross-ri479.*` auf dem Linux-Dateisystem, kein Windows-Bindmount.
Nur die fertigen Berichte/Logs werden nach Windows übertragen.

Windows-Checkouts: `artifacts/ri-b-measure/{native-a,final--b}/<0..2>/checkout`
und `artifacts/ri-b-measure/normal/project/{pair-a-2,pair-b-2}/<0..2>/checkout`
unter `C:/Zeuch/picross/picross/`. Linux: entsprechend
`{linux-a,b-final}/<0..2>/checkout`. A/B je gleicher Pfadtiefe und Namenslänge.
Die Test-Tempwurzeln sind isoliert außerhalb des Checkout; unter Windows
vollständig ausgeschriebener Benutzer-Temp-Pfad ohne 8.3-Alias.

Warme Caches, keine CPU-Pinnung/Lastkontrolle. Linux/Windows teilen Hardware;
einzelne Läufe überlappten andere kleine Prüfungen, deutliche Windowsstreuung.
Die Baselinearchive haben keine Gitmetadaten; manche Rohberichte verwenden
Quelllabels statt Git-SHAs und melden den internen Exportcommit als unbekannt.
Die tatsächliche Commitbindung liefert der vollständige Byte-/Inventarvergleich.
CLI-Start-/Ausgabekosten, große Kataloge und komplexe Proofketten sind offen.

Sekunden: Median [Minimum–Maximum], n=3. Unterphasen sind inklusive und
nicht mit Gesamtzeiten oder enthaltenen Unterphasen zu summieren.

| Umgebung | Operation | A | B |
| --- | --- | ---: | ---: |
| Linux / natives ext4 | `setup` | 0.001 [0.001–0.001] | 0.001 [0.001–0.001] |
| Linux / natives ext4 | `export` | 0.022 [0.020–0.050] | 0.022 [0.022–0.037] |
| Linux / natives ext4 | `plan` | 0.064 [0.063–0.072] | 0.066 [0.060–0.075] |
| Linux / natives ext4 | `register` | 1.674 [1.663–1.707] | 2.037 [1.946–2.089] |
| Linux / natives ext4 | `recovery_setup` | 0.001 [0.001–0.001] | 0.001 [0.001–0.001] |
| Linux / natives ext4 | `interrupted_registration` | 0.261 [0.247–0.274] | 0.463 [0.429–0.480] |
| Linux / natives ext4 | `recovery` | 0.112 [0.106–0.114] | 0.106 [0.104–0.115] |
| Windows / NTFS kurz | `setup` | 0.005 [0.005–0.005] | 0.006 [0.005–0.006] |
| Windows / NTFS kurz | `export` | 0.289 [0.288–0.321] | 0.320 [0.279–0.389] |
| Windows / NTFS kurz | `plan` | 0.528 [0.505–0.565] | 0.627 [0.476–0.706] |
| Windows / NTFS kurz | `register` | 8.498 [7.939–8.561] | 12.530 [11.167–13.512] |
| Windows / NTFS kurz | `recovery_setup` | 0.005 [0.005–0.005] | 0.006 [0.005–0.006] |
| Windows / NTFS kurz | `interrupted_registration` | 1.152 [1.142–1.162] | 2.474 [2.452–2.938] |
| Windows / NTFS kurz | `recovery` | 0.539 [0.532–0.584] | 0.613 [0.599–0.672] |
| Windows / NTFS verschachtelt | `setup` | 0.006 [0.004–0.007] | 0.006 [0.005–0.006] |
| Windows / NTFS verschachtelt | `export` | 0.337 [0.294–0.362] | 0.346 [0.321–0.360] |
| Windows / NTFS verschachtelt | `plan` | 0.637 [0.505–0.642] | 0.595 [0.498–0.621] |
| Windows / NTFS verschachtelt | `register` | 11.019 [9.873–11.081] | 13.221 [12.635–13.451] |
| Windows / NTFS verschachtelt | `recovery_setup` | 0.006 [0.006–0.007] | 0.005 [0.005–0.007] |
| Windows / NTFS verschachtelt | `interrupted_registration` | 1.335 [1.326–1.356] | 2.588 [2.580–2.591] |
| Windows / NTFS verschachtelt | `recovery` | 0.731 [0.702–0.810] | 0.741 [0.727–0.757] |

Publikationsphasen, Median Sekunden A → B:

| Umgebung | P0 | P1 | P2 | P3 | P4 | P5 | P6 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Linux / natives ext4 | 0.1329 → 0.1848 | 0.0028 → 0.0034 | 0.0093 → 0.0105 | 1.0869 → 1.1989 | 0.2241 → 0.2044 | 0.1090 → 0.1521 | 0.0254 → 0.0226 |
| Windows / NTFS kurz | 0.2767 → 0.6443 | 0.0125 → 0.0154 | 0.0615 → 0.0554 | 5.5579 → 7.6080 | 1.1035 → 1.3332 | 0.6621 → 1.0297 | 0.1215 → 0.1561 |
| Windows / NTFS verschachtelt | 0.3589 → 0.6469 | 0.0130 → 0.0144 | 0.0715 → 0.0719 | 7.2230 → 8.2395 | 1.5044 → 1.4719 | 0.8486 → 1.1121 | 0.1754 → 0.1787 |

Zusätzliche Aufrufanteile, Median Sekunden A → B (inklusive):

| Gemessener Aufruf | Linux | Windows kurz | Windows verschachtelt |
| --- | ---: | ---: | ---: |
| `capture` | 0.0036 → 0.0033 | 0.0203 → 0.0239 | 0.0305 → 0.0194 |
| `prepare` | 0.0465 → 0.0484 | 0.3557 → 0.4042 | 0.4217 → 0.3912 |
| `execute` | 1.5905 → 1.7803 | 7.8026 → 10.7676 | 10.2207 → 11.6350 |
| `guard` | 1.2375 → 1.1771 | 6.8573 → 8.1272 | 9.0672 → 8.9915 |
| `_stage_check` | 0.0213 → 0.0204 | 0.2397 → 0.2752 | 0.2756 → 0.2687 |
| `frozen_method` | 0.0280 → 0.0302 | 0.0566 → 0.0686 | 0.0743 → 0.0660 |
| `sync_directory` | 0.1211 → 0.1035 | 0.0516 → 0.0649 | 0.0610 → 0.0618 |
| `fsync` | 0.2184 → 0.1898 | 0.0472 → 0.0513 | 0.0483 → 0.0502 |

Recoveryphasen, Median Sekunden A → B:

| Umgebung | R0 | R1 | R2 |
| --- | ---: | ---: | ---: |
| Linux / natives ext4 | 0.0359 → 0.0345 | 0.0320 → 0.0305 | 0.0420 → 0.0424 |
| Windows / NTFS kurz | 0.1776 → 0.1814 | 0.1501 → 0.1889 | 0.2106 → 0.2342 |
| Windows / NTFS verschachtelt | 0.1974 → 0.2112 | 0.2249 → 0.2153 | 0.2989 → 0.2920 |

## Gemessene Arbeit und Befund RI-B-O01

In jeder der 18 positiven Registrierungen: Kandidaten-/Einzelproof-/Export-
prüfungen A=4, B=2; B zählt zusätzlich zwei erfolgreiche gebundene
Nachprüfungen. Export/Plan bleiben jeweils 2: Gesamtweg 8→6.
Guards=80, drei isolierte Checkoutprüfungen, 127 Verzeichnisflushs und
37 publizierte Dateien / 40.872 Bytes bleiben identisch. Die richtige
Definition/Revealbindung ist zusätzlich durch den unabhängigen Test geprüft.

| `register`-Zähler | A, alle Umgebungen | B Linux | B Windows, beide Pfade |
| --- | ---: | ---: | ---: |
| `path_checks` | 12079 | 16136 | 16154 |
| `safe_reads` | 6642 | 7517 | 7523 |
| `bytes_read` | 3628575 | 77789766 | 70497168 |
| `bytes_hashed` | 3458538 | 77617032 | 70324434 |
| `method_validations` | 14 | 15 | 15 |
| `verified_package_reuses` | 0 | 2 | 2 |

Die frischen Bindungen lesen/hashieren zusätzliche Paket-, Werkzeug-,
Python-/Pillow-Binärbytes und prüfen Stagingidentitäten vor jedem Addition-
schritt. Das erklärt zusätzliche Arbeit; vermiedene vollständige Proofs
sind kein Beleg geringerer Gesamt-I/O. Bytezähler decken ausschließlich
catalog_io ab; etwa stat-/Listing- und andere Leserarbeit ist nicht vollständig
erfasst. Windows/POSIX unterscheiden sich außerdem bei Dateisystem- und
Verzeichnis-fsync-Aufrufen; daraus folgt kein abweichender Publikationsinhalt.

**RI-B-O01 bleibt offen:** Das explizite Zählerziel B06 ist belegt, eine
Wallclockbeschleunigung nicht. Im kleinen Fall steigen die Mediane auf allen
drei Umgebungen. Keine allgemeine Beschleunigungs-/Skalierungszusage.
Dieser Befund und der unverändert enge Umfang sind im Body von #477
verbindlich dokumentiert und zurückgelesen (`2026-10-30T15:37:39Z`).
Keine Sicherheitsbindung wurde für bessere Zeiten entfernt; Guards und
RI-C-Scope bleiben getrennt. Komplexe/echte Kataloge wurden nicht gemessen.

Verworfene Versuche zählen nicht als erfolgreiche Messungen: ein zu tiefer
Windowspfad scheiterte im bestehenden Addition-Preflight; eine spätere
verschachtelte Reihe wurde bei Exportveröffentlichung mit WinError 5
abgebrochen (nur eine Wiederholung). Die vollständige frische A/B-Reihe oben
ersetzt sie. Erste Sandbox-/8.3-Temp-Prüfungen und die lokale volle Docs-/
Toolprüfung im Sparse-Checkout scheiterten ebenfalls; kein behaupteter Pass.
WSL hatte kein ensurepip/pip/Pillow; das gebundene Wheel wurde in eine eigene
venv entpackt, ohne globale Installation. Keine fehlende Plattform ersetzt.

## Rohbelege und Prüfung

Die sechs Rohberichte enthalten sämtliche Wiederholungen, Mengen, Phasen,
Quell- und Eingangsdateihashes. Sie liegen lokal unter dem ignorierten
`artifacts/ri-b-measure/` ausschließlich für die laufende Prüfung, nicht als
neue Dauerdateien oder CI-Inputs. Nach Review gelten die CI2-Abschlussregeln.

| Rohbericht | SHA-256 |
| --- | --- |
| `linux-a.json` | `e9efd0f84a6d09b59dd3944bd887b093d82f5f124eb8767d1f6e23bba64dc279` |
| `linux-b-final.json` | `b8de19fa80df4c26b7b34bf775c7f6e3ba9bcc0d3a926d11c4b29970094810ce` |
| `native-windows-short-a.json` | `d4977e5a25db35b17f4829953b8087799b8656e5619ab622a32b7bc6abc8de45` |
| `native-windows-short-b-final.json` | `5f7e0cb5e639115ec513af1342a433efcfbcd322a339d0c85b1fef93d2454b6b` |
| `native-windows-nested-a-final2.json` | `e07c9186c9292e35d29df24a890691f673d4f64325c3462c3eeaaabb36f41261` |
| `native-windows-nested-b-final2.json` | `cbcda789de7a24c09d6213bfd88b774dd0a330e90fd3331a1ac935bc6d260fcf` |

Linux: 31 gezielte RI-B-/RI-A-Tests auf dem gemessenen finalen Werkzeugstand
erfolgreich in 13,896 s. Windows: 31 gezielte Tests vor dem abschließenden
Checkoutidentitätszusatz in 73,310 s erfolgreich; alle sechs abschließenden
B-Tests auf dem finalen Werkzeugstand bestanden in 50,034 s.
Acht CI2-Auswahl-/Ergebnisprüfungen bestanden.
Der lokale vollständige Tool-/Dokumentlauf ist wegen Sparse-Checkout und
vorhandenen ignorierten Arbeitsartefakten kein Pass; aktuelle vollständige
Remote-CI liefert den Abschlussnachweis. Kein Chromium gestartet.

## CI-Nachkorrektur: Kategorien-Race tatsächlich injizieren

Der erste [CI-Lauf 41083589687](https://github.com/venomenon328/picross/actions/runs/41083589687)
auf Lieferhead `d05a69621cdaef8596f8bd7a9b83f5963a60b9ae` bestand den Fachjob
nicht: 397 Tests, zwei Assertions desselben Kategorien-Race-Tests fehlgeschlagen.
Der Originalbericht bestätigt: der dritte `verify_export`-Aufruf entfällt durch
RI-B bestimmungsgemäß; der alte Mock injizierte deshalb keine Fremdänderung.
Dies ist kein erfolgreicher CI-Lauf und wird nicht umgedeutet.

Der vorhandene Test injiziert jetzt nach den tatsächlich ausgeführten vier
Prüfgrenzen: Eingangsproof, Staging-Replay, geschriebene P3- und P5-Nachprüfung.
Er prüft zusätzlich genau eine tatsächliche Injektion. Seine bisherigen
Fremdbyte-/Journal-/Recovery-Orakel bleiben unverändert; der P5-Fall kommt hinzu.
Gezielte Gegenprobe erfolgreich: Linux 5,433 s, Windows 43,979 s; die acht
CI2-Zuordnungs-/Ergebnisprüfungen erneut erfolgreich. Kein Produktionscode,
kein Guard und keine Methodenquelle geändert. Alle sechs Plattformmessungen
bleiben deshalb an exakt dieselben vollständig inventarisierten Werkzeugbytes
gebunden. Neue vollständige Pflicht-CI für den korrigierten PR-Head erforderlich.

[Getrenntes Selbstreview](RI_B_SELF_REVIEW.md) prüft den vollständigen Diff,
Bindungen und unveränderten Guard-/Recoveryvertrag; keine unabhängige Zweitprüfung.
Finale CI-Ergebnisse, Head/Basis/Test-Merge und offene Gates stehen im
RI-B-T01-CI-Anhang des Draft-PR. Pflichtjobs bleiben bis tatsächlichem Erfolg
offen; separates qualifiziertes Review und ausdrückliche Mergefreigabe ebenso.
