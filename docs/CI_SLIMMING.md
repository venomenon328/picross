# CI2: Kurze CI und begrenzter aktiver Bestand

Stand: 27.10.2026 · freigegebener Sollvertrag · [Gesamtissue #412](https://github.com/venomenon328/picross/issues/412)

## Status und Geltung

Der Eigentümer hat die analysierte Lösung als Spezifikation freigegeben und die
500-Aktionen-Historyroute zusätzlich als unnötig verworfen. CI2-A ist nach
separatem R01 über PR #419 auf `94e3ea7d9674babbdcd6bde6251e233191fd096f`
integriert. CI2-B ist nach separatem R01 über PR #420 auf
`dd56d310d942eee47448df4cdcca5e4af4a49b00` integriert;
[B-T01](CI2_B_VERIFICATION.md) bleibt historisch gebunden, B-O01 offen.
CI2-C ist nach separatem R01 über PR #421 auf
`8e5e99647596bc3ef9d7bd22bd746b73fbb424d5` integriert; [C-T01](CI2_C_VERIFICATION.md)
bleibt an seinen Lieferstand gebunden. CI2-D ist nach separatem R01 über
[PR #422](https://github.com/venomenon328/picross/pull/422) auf
`8c31a69916941aed60ecd7e4d35a8d0d00637bf9` in `main` integriert;
[D-T01](CI2_D_VERIFICATION.md) und das
[separate R01](https://github.com/venomenon328/picross/pull/422#pullrequestreview-5659522486)
bleiben an ihre geprüften Commits gebunden. Der Laufzeitbefund CI2-D-O01 ist
weiterhin offen. CI2-E einschließlich Datenabbau ist nach
[finalem separatem E-R01](https://github.com/venomenon328/picross/pull/423#pullrequestreview-5665843085)
über [PR #423](https://github.com/venomenon328/picross/pull/423) auf
`53f9c1f6d87d752e6b0f3152985fd0a83de2278b` integriert.
[E-T01](CI2_E_VERIFICATION.md) und frühere Reviewstände bleiben historisch gebunden.
CI2-F / #424 optimiert ausschließlich die Katalog-Fachprüfung gemäß
[F-T01](CI2_F_VERIFICATION.md); separates qualifiziertes F-R01 bleibt vor Merge
erforderlich. Aus CI2 folgt keine zusätzliche Merge-, Deployment- oder Releasefreigabe.

Dieser Vertrag ersetzt für die benannten Folgepakete die bisherigen automatischen
Chromiumpflichten, impliziten Browserrechte manueller Scopes, ungekürzten historischen
Fall-/Bildmengen und den generellen Verzicht auf Laufzeitziele. Er ersetzt keine
Spiel-, Speicher-, Rechte- oder Freigabeanforderung. Historische Messungen und
Abnahmen behalten ihren damaligen Quellenbezug.

Die Auswahl-/Aufruf-/Gateänderung von A ist integriert. B liefert integrierte
Fachgruppen, gemessene isolierte Fixtures und die benannten historischen
Helferstilllegungen. C begrenzt Browserfälle, Bilder und Exportbedarf;
die integrierte D-Lieferung begrenzt Nativeumfänge und die native Produkt-CLI.
Gemessene Kürzung und Zielerreichung
werden ausschließlich mit tatsächlichen Läufen belegt. Auswahl, Producer und
Gate werden jeweils gemeinsam im zuständigen Paket umgestellt; ein übersprungener
noch ausgewählter Altjob wird dadurch nicht rückwirkend erfolgreich. Alte Browser-,
500er- und Vergleichsrouten müssen nicht als neue Baseline reproduziert werden.
Der Dokumentdiff verwendet nur den bestehenden Docs-/Werkzeugpfad und `ci-required`.

## 1. Prüfauswahl und ausdrücklicher Browserauftrag

[CI2-A / #413](https://github.com/venomenon328/picross/issues/413) liefert:

- Automatische PR-/Push-Ereignisse installieren und starten keinen Browser.
  `all`, `toolchain`, `runtime`, `visual`, `perf-b`, `production`, unbekannte Pfade
  und gemeinsame Komponenten sind kein impliziter Browserauftrag.
- Ein ausdrücklicher manueller Chromiumaufruf bindet Quellstand und Prüfumfang.
  Auch wiederverwendbare Unterworkflows verlangen diese Anforderung; kein
  Zeitplan, automatischer Nachlauf oder Default ergänzt sie.
- Auswahl, Scheduler und Gate unterscheiden nicht angefordert, Erfolg, fehlend,
  übersprungen, fehlgeschlagen und abgebrochen. Nur angeforderte Browserprüfung
  verlangt passende Browserresultate/-dateien; fehlende Pflichtresultate scheitern.
  Die fest eingebaute PR-411-Ausnahme und ihr Sondertest entfallen.
- Native Prüfung, Fachtests, Toolchain und SSH/HTTP bleiben unabhängig nach
  tatsächlichem Änderungsbezug gewählt. Reine Inhalte behalten ihren kurzen
  Pfad-/Dateimodusschutz; Rename/Delete berücksichtigt beide Seiten.
- Der reguläre Main-Nachlauf wiederholt die teure PR-Fachsuite nicht automatisch.
  Kurze Integritätschecks bleiben; dies ist kein Cachen oder Umdeuten alter Erfolge.
- Die exakt benannten inerten Belegklassen aus [dem Bestandsinventar](DEVELOPMENT_ARCHIVE.md)
  lösen keine sachfremde Vollprüfung aus. Keine pauschale Ausnahme für `docs/`;
  aktive Inputs wie `docs/evidence/kk/native-crops.json` bleiben wirkungsgerecht geprüft.

### Geprüfte SD2-Ergänzung der engen Fachauswahl

Unter `tools/puzzle_production/` sind die reinen Module `sd2_analysis.py`,
`sd2_cli.py`, `sd2_contract.py`, `sd2_io.py`, `sd2_profiles.py`, `sd2_rules.py`,
`sd2_verifier.py`, `sd2_rating.py`, `sd2_rating_cli.py`, `sd2_rating_freeze.py`,
`sd2_rating_identity.py`, `sd2_rating_io.py` und `sd2_reference_checks.py` sowie
`sd2_method_0_4.json`, `sd2_references_0_4.json`, `sd2_calibration_0_4.json`,
`sd2_validation_0_4.json` und `sd2_comparison_0_4.json` zu prüfen und eng zuzuordnen.
Dazu gehören `tests/puzzle_production/test_sd2_analysis.py` und
`tests/puzzle_production/test_sd2_rating.py`. Maßgeblich bleiben aktuelle Abhängigkeiten.
`sd2_catalog_rating.py`, `test_sd2_catalog.py`, `catalog_method.py`,
`catalog_analysis.py`, gemeinsame Schemas, Exporte und Transaktionen erben keine
`sd2*`-Ausnahme. Keine echte Katalogbewertung oder Testgenerierung aus dem Fundus.

## 2. Kleine Fachtests und repräsentative Integrationen

[CI2-B / #414](https://github.com/venomenon328/picross/issues/414) trennt sinnvoll
auswählbare Bereiche für Solver/Analyse, Import/Bilder, Adapter und
Katalog/Transaktionen. Gemeinsame Änderungen wählen deren benötigte Vereinigung.

Gemeinsame technische Fehlergrenzen einmal vollständig am zuständigen kleinen
Mechanismus prüfen; fachliche Einstiege erhalten repräsentative Integrationen.
Keine vollständige Produktionskette für lokale Validierung oder interne Aufrufzahlen.
Unveränderliche Grundfixtures dürfen einmal erzeugt und isoliert kopiert werden,
soweit Quellen-/Pfadbindungen stimmen. Kein gemeinsamer veränderlicher Zustand und
kein Cache von Prüfergebnissen. `za1_fixtures` besitzt bereits einen Bewertungscache;
die untersuchte Wiederholung betrifft gesamte Export-/Registrierungs-/Prüfketten.

Konkrete Stilllegung: 13 BP-Hilfstests samt ausschließlich dafür verwendeten
Herstellerhelfern, fünf RP4-Versuchsauswertertests/Helfer und ein ungenutzter
RP5-Archivhelfertest/Helfer, jeweils nach aktuellem Leserabgleich. Der 20. ermittelte
Python-Kandidat (PR411) gehört CI2-A. RP6, geerbte RP3-/ZS1-Module, aktive Assets,
Lizenzdateien und aktuelle Archiveingangsvalidierung nicht nach Namen entfernen.

Günstige unabhängige Solver-/Verifier-Orakel und aktuelle Analyse-/Bewertung bleiben.
Keine pauschale Halbierungsquote. Unterstützte Altformate erhalten kleine feste
synthetische Eingänge; ihr Wegfall erfordert eine ausdrückliche Kompatibilitätsentscheidung.
Keine Mutation bei fremden/ungültigen Daten, atomare Veröffentlichung, Rollback,
unabhängige Verifikation und bestehende Saves bleiben abgesichert.

## 3. Kleine ausdrücklich gestartete Chromiumprüfung

[CI2-C / #415](https://github.com/venomenon328/picross/issues/415) ersetzt den
33er-Bestand durch ungefähr 8–10 aktuelle Kernfälle im kurzen Browserumfang:
regulärer uninstrumentierter Start; Katalogauswahl/Sortierung; echte Bearbeitung
und Undo/Redo; relevanter Resize-/DPI-Wechsel; kleiner echter Abschluss/Reset;
bestätigte Sicherung, Reload und Prozessneustart; Zweittab/Sperre; Schreibfehler/Retry.

KU-/AT-/HZ-A/B/C-Schichten werden zu aktueller Katalog-/Bedienelementprüfung
zusammengeführt. Ein normaler Viewport wird ausführlich geprüft, weitere Größen
nur für tatsächliche Geometriegrenzen. Ein HZ-C-Rückwechsel rechtfertigt keine
erneute identische Fünfer-Bildgalerie. Kleine synthetische Voraussetzungen ersetzen
aufwendige Vorbereitungsdurchspiele; keine Zustandssetter statt geprüfter Übergänge.

Seltene aktuelle Varianten werden günstig unterhalb des Browsers geprüft.
Zusätzliche Browserprofile benötigen ausdrückliche Auswahl, konkreten Zweck und
begrenzten Fall-/Zeitumfang. Keine automatisch angehängte Vollmatrix oder neuer
unbegrenzter manueller Default. Nur benötigte Builds erzeugen; ein angeforderter
Exportwechsel verlangt weiterhin zwei echte Exporte, keinen umbenannten Build.
Browserinput, bestätigte IndexedDB-Sicherung, Reload und echter Prozessneustart
bleiben für ihre jeweiligen Aussagen erhalten. Firefox bleibt aus CI ausgeschlossen.

## 4. Native Prüfung und kurze Historyroute

[CI2-D / #416](https://github.com/venomenon328/picross/issues/416) ersetzt die
500er-Route vollständig im aktiven Standard-, `history`-, `runtime`-, `all`-,
`--integration`- und gewöhnlichen manuellen Vollumfang. Kein routinemäßiger
Ersatz-Stresstest; spätere spezielle Belastungsversuche brauchen einen eigenen Auftrag.

Der Ersatz umfasst höchstens **20 semantische Benutzerkommandos insgesamt**,
höchstens **sechs neue wirksame History-Transaktionen** und **genau zwei echte
Spielprozesse** (Schreiben, frisches Laden/Redo) im selben isolierten synthetischen Profil.
Werkzeug-/Farbwahl, Blattwahl, Navigation, Undo/Redo und reguläres Beenden zählen mit.
Ein zusammenhängender Down/Move/Up-Strich ist ein Kommando; passive Assertions und
technische Prozessstarts zählen nicht. Keine versteckten Setup-Bearbeitungen,
Mengenauffüllung oder Wiederholung nach Regionen/Fenstergrößen.

Gezielt erhalten: atomarer Strich, exakte Vor-/Nachwerte, Undo/Redo, Abschneiden
eines Redo-Zweigs durch neue Bearbeitung, unveränderte History bei Navigation,
Zellen/History/Cursor/Undo-Merkmal/Ansicht nach Save/Neustart, echter Redo danach
und unveränderte fremde Slotbytes. Das kleine unabhängige Python-Orakel importiert
keine produktive Historylogik. Manipulierte Zelländerung und unvollständige Spur
werden mit zwei günstigen Gegenproben ohne weitere Spielprozesse abgewiesen.

Producer, Trace, Zusammenfassung und Gate binden die tatsächliche kurze Folge.
Exakt 500 Aktionen, mehr als 500 veränderte Zellen, zehn Regionen, fünf 100er-
Segmente und das künstliche 560px-Board entfallen. Gezielte aktuelle
Hinweis-/Eingabegeometrie wird in ihren eigenen Prüfungen abgedeckt.

Weitere Kürzung: abgeschlossener HZ-C-Vergleich 14/15 und 36 HC92-before-Bilder
entfallen. Aktuelle Schriftgrößen/Grundlinien/Fallbacks bleiben geprüft.
Dichte Animationsfolgen werden auf relevante Anfangs-/Zwischen-/Endzustände und
einen echten Bewegungsnachweis begrenzt; Produktanimationen bleiben unverändert.
Katalogmodi und wiederholte Importe werden konsolidiert; eine verifizierte
unveränderliche Importbasis darf geteilt/kopiert werden, mutable Daten bleiben isoliert.
Routineprüfungen verwenden repräsentative Beschriftungen/mehrere Katalogseiten;
256-Kategorien-/128-Zeichen-/300-Einträge-Lastmatrizen nur gezielt.

Untersuchungsziel: mindestens 50 % weniger routinemäßige Bildbelege gegenüber
858 festen PNGs. Tatsächlich erzeugte und gelieferte Mengen getrennt ausweisen;
Abweichungen begründen. Keine bloße Dateinamenquote oder Zusammenfassung zum Megatest.

## 5. Bestand, Abschluss und neue Dateien

[CI2-E / #417](https://github.com/venomenon328/picross/issues/417) und
[DEVELOPMENT_ARCHIVE](DEVELOPMENT_ARCHIVE.md) binden sechs konkrete Bereinigungsklassen:
1.156 Dateien / 837.043.724 Bytes (798,27 MiB) am Ausgangsstand. Aktive Ressourcen,
Freigaben, Rechte, kompakte Daten und offene Produktionen bleiben erhalten.
Kein historischer Blobdownload nur zur Metadatenmessung, keine Historienumschreibung.

[Authoring §9](ai-workflows/PUZZLE_AUTHORING.md#9-produktionsabschluss-und-bereinigung)
ergänzt den eigenständigen Abschluss späterer Bildrevisionen bei bereits kompaktem
ursprünglichem Paket. Keine Rasterneuproduktion, kein Umschreiben versiegelter Receipts.
Die alte enge §9-Mergefreigabe wird durch diese Spezifikation nicht auf technische
CI2-Pakete oder neue Produktarbeit erweitert.

Große Laufbelege liegen grundsätzlich in zeitlich begrenzten CI-Artefakten;
benötigte Originalreferenzen erhalten einen konkreten fortbestehenden Zweck.
Abgeschlossene Beleg-ZIPs/Galerien sind kein aktiver Standardbestand. Ein leichter
Check im vorhandenen Docs-Pfad blockiert neue unzulässige Ablageklassen und macht
zulässigen Datei-/Bytezuwachs sichtbar, ausschließlich mit verfügbaren Metadaten.
Keine neue Testmatrix, kein weiterer CI-Job oder dauerhaft wachsendes Archivmanifest.

## 6. Kosten, Messung und Entwicklung

| Pfad | Freigegebenes Ziel |
| --- | --- |
| Docs/Werkzeuge | unter einer Minute |
| Übliche Standard-CI | möglichst unter fünf Minuten |
| Aufwendigere relevante Integration | unter zehn Minuten |
| Kurzer ausdrücklicher Chromiumlauf einschließlich benötigtem Build | höchstens acht Minuten, typischer Zielkorridor fünf bis acht |
| Gezielt angefordertes zusätzliches Browserprofil | unter zehn Minuten je begrenztem Profil |

Runner, Toolchain, Cachezustand, Queue, Jobdauer, kritischer Pfad und summierte
Rechenzeit auseinanderhalten. Tests messen Zeit einschließlich Aufbau; langsamste
zehn Tests und Gruppenzeiten kommen in den bestehenden kompakten Bericht.
Überschreitungen bleiben sichtbare Optimierungsbefunde, keine behauptete Zielerreichung.
Abbruchgrenzen beenden Hänger als Fehler; sie ersetzen keine Optimierung und
verkürzen keine funktionalen Speicher-/Animationszusagen.

Neue teure Tests benötigen aktuellen Zweck, günstigste passende Ebene und
Kostenbegründung. Vor Addition prüfen, welcher vorhandene Fall erweitert/ersetzt
wird. Neue Module liefern passende Auswahlzuordnung. Ein kleines Dokument-/Daten-
Update erzeugt keine eigene historische Testfamilie. Lieferabschluss umfasst
bereinigte Arbeitsdaten und aktuelle Statusverweise; keine Paketchronik in Einstiegen.

## 7. Pakete und Abnahme

| Paket | Ergebnis | Abhängigkeit |
| --- | --- | --- |
| [CI2-A #413](https://github.com/venomenon328/picross/issues/413) | Auswahl und ausdrücklicher Browserstart | integrierte Spezifikation; zuerst |
| [CI2-B #414](https://github.com/venomenon328/picross/issues/414) | Fachgruppen, Fixtures und historische Helfer | A |
| [CI2-C #415](https://github.com/venomenon328/picross/issues/415) | kurze aktuelle Chromiumprüfung | A |
| [CI2-D #416](https://github.com/venomenon328/picross/issues/416) | native Kürzung einschließlich History | A |
| [CI2-E #417](https://github.com/venomenon328/picross/issues/417) | Bestandsbereinigung, Bildabschluss und Metadatenkontrolle | A |

CI2-A/B/C/D sind nach separaten R01 auf `main` integriert; ihre T01-/R01-
Nachweise bleiben an die damaligen Liefercommits gebunden. D ist über
[PR #422](https://github.com/venomenon328/picross/pull/422) auf
`8c31a69916941aed60ecd7e4d35a8d0d00637bf9` integriert. CI2-D-O01 (Laufzeit) bleibt offen.
CI2-E einschließlich Bestandsabbau ist nach finalem separatem R01 über
[PR #423](https://github.com/venomenon328/picross/pull/423) auf
`53f9c1f6d87d752e6b0f3152985fd0a83de2278b` integriert.
[E-T01](CI2_E_VERIFICATION.md) und die früheren E-Reviewstände behalten ihre
damaligen Bindungen. CI2-F / #424 ist das abgegrenzte Folgepaket zur
Kataloglaufzeit (höchstens 400 s statt 833,015 s); B-/E-O01 und D-O01 bleiben
Gesamtziele. [F-T01](CI2_F_VERIFICATION.md) und separates qualifiziertes F-R01
binden die neue Lieferung; kein Mergeauftrag.
Nach A sind B/C/D/E unabhängig integrierbar; gemeinsame Gate-/Auswahländerungen
gegen den jeweils aktuellen Stand nachführen. Standard ist ein Implementierungs-PR
je Paket. T01 enthält tatsächliche gezielte Positiv-/Negativnachweise, gemessene
Wirkung und getrennten Selbstreview; R01 ist ein separates qualifiziertes Review
vor Merge. Keine neue persönliche Spielabnahme allein durch den CI-Umbau.
Produktabnahmen, Merge und Deployment bleiben getrennt.

Ausgangsmessungen: [Chromium 40:46](https://github.com/venomenon328/picross/actions/runs/40219765031/job/121259857205),
[Fachjob auf main 26:54](https://github.com/venomenon328/picross/actions/runs/40239352091/job/121307827335),
[PR411-Fachjob 34:33](https://github.com/venomenon328/picross/actions/runs/40250428608/job/121341083142).
586 Pythonmethoden (218 Tools/368 Fachtests), 33 Browserszenarien und 923 feste
native Belegdateien sind verschiedene Mengengerüste, keine addierbare Testzahl.
Alte Logs sind Baseline; Wirkung neuer Implementierung wird erst nach ihrem Lauf behauptet.
