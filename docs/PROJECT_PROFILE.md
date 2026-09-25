# Projektprofil: picross

## Zweck, Quellen und aktueller Rahmen

`venomenon328/picross` enthält Produktkonzeption, Entwicklungsregeln, Dokumentprüfung, den technischen [P1.0-Preflight](P1_PREFLIGHT.md) und den ausführbaren [P1.3-Mausschnitt](../prototypes/p1/README.md) unter `prototypes/p1/`. P1.1/P1.2 sind über PR #14 als `acc9c51161a18cca17813a8e44c07b2cf074cd44`, P1.3 über PR #15 als `efada37100ddfded50c432e70823b3f0dd446436` in `main` integriert. P1.4/#12 wird auf `chore/12-p1-integration-verification` in einem eigenen Draft-PR technisch geprüft; [aktueller Ergebnisbericht](P1_4_VERIFICATION.md). Der [Workflow](dev-rules/WORKFLOW.md) ist Prozessgrundlage, [AGENTS.md](../AGENTS.md) der Einstieg. Lieferumfang und Freigaben stehen im jeweiligen Issue/PR.

Die [Produktdefinition](PRODUCT_DEFINITION.md) ist bei Produktkonzept, Rätselregeln/-inhalten, Progression/Wertung, UX/UI, Eingabe, Plattformkonzept oder Produktarchitektur vollständig zu lesen. Sie unterscheidet Beschlossenes von Vorschlägen und offenen Fragen; ihr Entwicklungsablauf ist keine Implementierungsfreigabe.

Das [Gestaltungskonzept](DESIGN_CONCEPT.md) ist bei Thematik, Album, Motiventhüllung, UX/UI, Eingabe/Wertung und entsprechenden Prototypen zusätzlich vollständig zu lesen. Positive Mock-Rückmeldung ist keine Abnahme aller dargestellten Details. Revision 0.5 übernimmt das konkrete Mausfeedback einschließlich Zelltrennung, motivtreuer Enthüllung, gemeinsamem Hinweisraster und linienweisen Lesepositionen.

Für P1 außerdem vollständig lesen: [P1-Spezifikation](PROTOTYPE_P1.md), [Issue #5](https://github.com/venomenon328/picross/issues/5) samt späteren Entscheidungen und das beauftragte Paket. Bei technischer P1-Arbeit zusätzlich [P1.0](P1_PREFLIGHT.md), [aktuelle Anleitung](../prototypes/p1/README.md) und die [P1.1-](P1_1_VERIFICATION.md), [P1.2-](P1_2_VERIFICATION.md) und ab #11 [P1.3-Prüfberichte](P1_3_VERIFICATION.md). Der versionierte Fachvertrag steht in der Spezifikation, Auftrag und Abnahmestand in Issue/PR.

**Aktuelle Phase:** #11 ergänzte auf der gemergten P1.2-Basis die isolierte lokale
Persistenz, strikte Savevalidierung, Primary/Backup-Recovery, Viewwiederaufnahme,
bestätigten Einzelreset und den isolierten Zwei-Prozess-Nachweis. Der
[P1.3-Prüfbericht](P1_3_VERIFICATION.md) und die Anleitung beschreiben den technischen
Stand einschließlich R2/B-01+B-02 und D-23 bis D-27. Dieser Stand ist als
`efada371…` integriert. #12 prüft 500 Aktionen, Messung, Windows-Artefakt und
Regressionen; M-04 und die gesamte reale Eigentümerabnahme bleiben offen.
Ältere grüne Läufe belegen den neuen #12-Head nicht.

Die Eigentümerentscheidung Variante A nach Review R7 priorisiert geometrisch
nächsten Hinweis-Snap und monotone direkte Dragbedienung vor maximaler gleichzeitiger
Außenbelegung. Der direkte äußere Draganschlag ist `outer_start`; alle Tokens bleiben
über die Zustandsfolge erreichbar. Der verbindliche Vertrag V-01 bis V-05 steht in
#11 und P1 §5.2. Der nur per Gegenbewegung erreichbare zusätzliche Randzustand entfällt.

Der [Herkunftsnachweis](DEV_RULES_ADOPTION.md) bezeichnet die unveränderte Regelkopie. Keine abschließende Produktarchitektur oder universell erprobte Produkt-Teststrategie behaupten. Weitere Pflichtquellen erst mit tatsächlich beschlossenen Inhalten anlegen.

## Beschlossene Richtung und offene Entscheidungen

[H1 / Issue #19](https://github.com/venomenon328/picross/issues/19) ergänzt die
lösungsunabhängige optionale Erfüllungsmarkierung gemäß P1 §5.2. Der sitzungsweite
Schalter startet aktiv, bleibt bei Blattwechsel/Reset erhalten und wird nicht
persistiert. Nur die vollständigen eigenen Linienhinweise und sichtbaren Zellen
einschließlich Vorschau dürfen eingehen. [H1-Prüfbericht](H1_VERIFICATION.md).

Produktkern: klassische und farbige kuratierte PC-Bildrätsel, Großrasterfokus, präzise Eingabe, Offline-Solo-Spiel, frühe visuelle Gestaltung sowie der bestätigte Progressions-/Wertungsrahmen. Das ursprüngliche Setup hatte weder Spielmechanik noch Technik festgelegt.

Visuelle Grundlage: sich füllendes Album, warme ruhige 2D-Illustration mit klaren Konturen und Farbflächen, motivtreue Abschlussbilder, Perfektion nur ohne Fehler und ohne Undo. Sammelalbum/Reisealbum bleiben Alternativen. Detailliertere Abschlussbilder dürfen die Rasterstilisierung verfeinern; pixelidentische Silhouetten sind kein allgemeines Qualitätskriterium.

P1: native Windows-Desktopfassung, typisiertes GDScript, Godot Standard 4.7.2-stable mit passenden Standard-Exportvorlagen, keine Wertung/Live-Fehlerhilfe/Hypothesen. D-06 bleibt verbindlich: Maus, kein Tastatur-/Controller-Scope oder entsprechendes Gate. Escape bleibt der vereinbarte Abbruch einer Mausgeste. Spätere alternative Produkteingaben werden dadurch nicht gestrichen.

Ab #9: 1080p-Startziel ohne erzwungene Zellvergrößerung, getrennte UI-/Raster-
Skalierung, visuelle Zelltrennung auch an Fünferlinien, direkte Füllung↔X-Umwandlung
mit links/rechts bei einmalig festgelegtem Strichmodus, detaillierteres F-01-Ergebnisbild,
unnummerierte einzeilige farbige Hinweise direkt im Arbeitsbild sowie feiner monotoner
Zoom. Überlaufende Folgen behalten vollständige einzelne Hinweise, verwenden gemeinsame
feste Slots und sind je konkrete Spalte beziehungsweise Zeile unabhängig vom Raster
und allen Nachbarfolgen pannbar. F-02 erhält wie das bestätigte F-01 ein eigenständiges
verfeinertes Ergebnisbild. Verbindliche Details ausschließlich in P1 §§4–5; D-18 bis
D-22 lösen widersprechende alte D-07-/D-14-/D-17-/Hinweisregeln ab.

Referenzhardware aus früheren Nutzerangaben: Windows 11, 2560×1440, Maus, Ryzen 7 5800X, RTX 3070. Tatsächliche Windows-Skalierung, Fensterfläche und Versionskennung des Nutzerlaufs sind nicht aus Screenshotgrößen bestätigt. Fehlende Daten sichtbar lassen und bei der erneuten Probe erfassen.

Endgültige Engine/Sprache, gesamte Betriebssystemmatrix, Produktpersistenz, Solver-/Produktionsverträge, Fehlerzählung, Sternschwellen, Wertungswirkung manueller Neutralisierung und Veröffentlichungsdetails bleiben außerhalb dieser begrenzten Festlegungen offen. Keine Regeln aus anderen Projekten übernehmen. Python dient hier Prüf-/Buildwerkzeugen, nicht der Wahl eines Produktstacks.

## Branches und Befugnisse

H1 verwendet `feat/19-clue-completion` vom aktuellen `main`, Ziel `main`, mit eigenem
Draft-PR. Der Durchführungsauftrag erlaubt H1, Tests, Dokumentation, Commit/Push und
Draft-PR; weder Merge noch Issueschluss. Bei Start ist #17/PR #18 weiterhin offen
und nicht integriert. Seine Lieferung wird nicht geändert; gemeinsame Stellen bei
einer späteren Integration zusammenführen. #12 hat die bisherige reale Eigentümerprobe
bestätigt; H1 verlangt ausschließlich seine zusätzliche gezielte Probe.

Zielbranch `main`; Standardmerge Squash nach ausdrücklicher oder passender bedingter Freigabe. Keine automatische Branchlöschung, kein Force-Push und keine direkten Änderungen am Zielbranch ohne passende Befugnis.

Der beauftragte #12-Arbeitsbranch ist `chore/12-p1-integration-verification` vom aktuellen `main`; sein PR bleibt bis zur erforderlichen Prüfung Draft. PR #14/#15 sind gemergt und werden nicht fortgesetzt. #5 bleibt bis vollständiger Lieferung und Abnahme offen.

Der ausdrückliche Durchführungsauftrag für #12 erlaubt die spezifizierten technischen Änderungen, Tests, Commits, Push und den neuen Draft-PR. Er erlaubt weder Merge, Release noch Schließen von Issues.

Die ursprüngliche Initialisierung ist in #1 dokumentiert. Technischer Branchschutz ist nicht als wirksam verifiziert; die vereinbarten Prüfungen gelten unabhängig davon. Keine Schutzregeln umgehen.

## Dokumentprüfung

Python 3.11 oder neuer, Standardbibliothek. Kleine lokale Prüfungen in geeigneter vorhandener Umgebung sind zulässig; belastbare aktuelle CI darf die Abschlussprüfung liefern. Keine ritualisierte doppelte Vollprüfung. Unbekannte lokale Ressourcen-/Konfigurationsgrenzen vorher prüfen; globale Codex-Einstellungen der Nutzerworkstation sind nicht als geprüft bestätigt.

Verbindliche Befehle im Repository-Root:

```sh
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/check_docs.py
```

Vor Merge muss [Setup verification](../.github/workflows/setup.yml), Job `docs`, für aktuellen Head beziehungsweise zugehörigen Test-Merge erfolgreich sein. Der Job prüft Tests, Dokumente und vollständigen `git diff --check`. Head, Basis und gegebenenfalls Integrationscommit zuordnen; übersprungene oder alte unpassende Checks nicht als bestanden ausgeben.

[Dokumentvalidator](../tools/check_docs.py) und [Tests](../tools/test_check_docs.py) sind aus dem dokumentierten dev-rules-Stand abgeleitet. Geprüft werden Pflichtdateien, UTF-8/LF/Abschlusszeile, nachgestellte Leerzeichen, Versionsformat und einfache lokale Inline-Markdown-Links samt Paketgrenzen. Nicht geprüft: externe URLs, Anker, Referenzlinks, vollständige Markdownvalidierung oder Byteidentität der Regelkopie. Letztere bei Regelpaketaktualisierung separat gegen den Quellcommit prüfen.

## Toolchain- und Produktprüfung

P1.0 wurde nach erfolgreichem `preflight`-/`docs`-Job über PR #13 gemergt. [Preflight-Harness](../tools/p1_preflight.py) und [CI](../.github/workflows/p1-preflight.yml) verwenden ausschließlich die gepinnten offiziellen Standard-Assets. Live-Metadaten und vollständige Archive werden gegen SHA-256 geprüft, temporär verwendet und nicht versioniert/global installiert. Bei Änderungen am Preflight echten Download-/Import-/Test-/Start-/Exportweg nachweisen, nicht nur Mocks oder Dokumenttests.

Der [Produkt-Harness](../tools/p1_product.py) nutzt diese Grundlage mit temporärer Projektkopie und eigenen APPDATA-/LOCALAPPDATA- beziehungsweise XDG-Pfaden. P1.3-Saves liegen ausschließlich unter Godots `user://p1/saves/`; automatisierte Tests erhalten zusätzlich eigene temporäre Speicherroots und dürfen den normalen Benutzerpfad nicht lesen oder verändern. Lokale Windows-Prüfungen sind erlaubt. Prozesslimit 300 Sekunden, Downloadlimit 1200 Sekunden, CI-Joblimit 40 Minuten.

```powershell
$p1Cache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $p1Cache --output-dir artifacts/p1-product
```

Unter Linux `python3` und externen Cachepfad verwenden. Der bestehende Ablauf prüft F-01s Zertifikat, Import, Godot-Tests, erwarteten Negativtest mit Exit 23, begrenzten Start der Hauptszene und Windows-Export mit `P1 Windows x86_64`; auf Windows zusätzlich exportierten Start. Bericht, Phasenlogs und vollständiges ZIP mit EXE-Paar/Anleitung/Commitkennung werden erzeugt. Quellhead, getesteten Checkout/Test-Merge und veränderten Arbeitsbaum unterscheiden.

#9 erweitert diesen Ablauf für F-02/F-03, direkte Gestenumwandlung und Rücknahme,
farbige atomare In-Context-Hinweise in gemeinsamen Slots, individuelle Zeilen-/
Spalten-Lesepositionen, feinen monotonen Zoom,
Ansichts-/Miniaturtransformationen, Resize und unabhängige Abschlussressourcen.
Teständerungen zu D-09 bis D-22 sind
gezielte Vertragsanpassungen; sonstige Regressionen nicht durch Entfernen von Tests
verdecken. F-01-Lösung/Hinweise und logische Nachweise erhalten. Keine neue allgemeine
Solver-/Assetplattform erforderlich.

Für die technische Lieferung von #12 müssen `product` aus [P1 product verification](../.github/workflows/p1-product.yml), `docs` und der weiterhin aktive `preflight` für den finalen Head tatsächlich erfolgreich sein. Der Produktweg enthält Speicher-/Fehler-/Recoverytests, den bestehenden echten Zwei-Prozess-Roundtrip und die neue 500-Aktionen-Folge samt Neustart im isolierten Profil; Windows-Export und Renderregressionen bleiben enthalten. Produktartefakte werden 14 Tage gespeichert. Ein Headless-Start oder synthetisches Event ersetzt M-04 oder die reale Maus-/GUI-Abnahme nicht.

## Abnahme und Übergaben

Für H1 müssen `product`, `docs` und `preflight` am finalen Head/zugehörigen Test-Merge
tatsächlich erfolgreich sein. Der isolierte Produktweg ergänzt unabhängigen
Linienoracle, echte Vorher-/Nachher-Renderbilder und Cache-/Zustandsregressionen;
500-Aktionen-Folge, Neustart, Save-/Recoveryfälle und Windows-Export bleiben Pflicht.
Die gezielte H1-Eigentümerprobe gemäß #19 bleibt ein separates Gate **vor Merge**.
Commit-, Artefakt-, Hash- und Runbindung sowie Selbstreview stehen im eigenen PR.

Vollständigen Diff gegen den Auftrag prüfen: keine versteckten Produktentscheidungen, Secrets, ungeklärten Assets, unerreichbaren Pflichtquellen oder ungefragten Änderungen der gemeinsamen Regeln. Technischen Nachweis, Selbstreview, Nutzerprobe, Merge- und Releasefähigkeit unterscheiden. Ein getrennter Selbstreview ist keine unabhängige Zweitprüfung.

Der Review R1 in PR #14 bezieht sich auf den P1.1-Head `64dcca4df9ed00cecedfdb8cabba09bcb7179ae8`, nicht auf die damaligen noch ausstehenden #9-Funktionen. K-06 wurde anschließend vom Nutzer erprobt und mit zwei Screenshots/vier Folgepunkten beantwortet. **Durchgeführt mit Änderungsbedarf** ist keine pauschale positive Abnahme aller Szenarien. Einzelbestätigungen und tatsächliche Skalierung fehlen teilweise.

Review R2 bezieht sich auf `267df8cdb264070ed1f81e500475657be6f27f9d` und
nennt B-01 (invertierbare Zoomrichtung aus der Gesamtansicht) sowie B-02 (Mojibake im
Projekttitel). Die folgende Eigentümerprobe ergänzt D-11 bis D-15 als neuen Sollstand;
die Probe nach Review R3 ergänzt D-16/D-17 zur Kürzung und Hinweisnavigation.
Die Nacharbeit behebt diese technischen Punkte, ersetzt aber weder ein Review des neuen
Heads noch die weiterhin offene reale Eigentümerprobe.

Review R4 bezieht sich auf `b19f14e0f8c7a599bd04799872ccea3b7ceadc6c` und verlangt
die Grundlagenkorrektur J-01 bis J-06: keine Hinweis-Zusatzkennungen, gemeinsame feste
Slots, unabhängige Navigation jeder konkreten Linie, 1080p-Startbasis, verfeinertes
F-02-Motiv und dazu passende Quellen/Nachweise. D-18 bis D-22 in P1 0.7 setzen diesen
Sollstand um; ältere grüne Läufe und frühere Reviewstände belegen ihn nicht.

Review R5 bezieht sich auf `edd7a28ce11bdb2e0aff4e41ee5fbc6b8c7b7702` und führt
B-03/B-04 als aktive technische Nacharbeit: individuelle Hinweisfolgen müssen bei
Zoom, Resize und UI-Skalierung ihre semantische Leseposition statt nur den numerischen
Offset erhalten; der widersprüchliche Farbrätsel-Satz im Gestaltungskonzept ist mit
D-22 zu vereinheitlichen. Die Nacharbeit ändert weder die übrigen D-18-bis-D-22-
Funktionen noch die getrennte spätere Layout-/Zieldesign-Phase. A-01 bleibt offen.

Review R2 zu PR #15 bezieht sich auf `1a5756f37b1e43b6d8126e5c0e4c817e7e3290c1`:
B-01 verlangt blockierende Pflicht-Flushes bei Fehlern, B-02 die Schreibsperre
eines aus Backup geladenen Slots auch bei fehlendem Primary. #11 ergänzt als
ausdrücklich beauftragte Nacharbeit D-23 bis D-27. Der neue technische Head und
seine CI-/Artefaktnachweise stehen im PR; frühere Läufe bleiben historisch.

Die reale Maus-/Layoutprobe an der integrierten #9-Lieferung bleibt offen; fehlende Metadaten sind dabei zu erfassen. Für #11 prüft der Eigentümer M-04 am commitgebundenen Windows-Artefakt: Bearbeiten, regulär schließen, echten App-Neustart, Zellen/Undo/Redo/Ansicht/Einzelhinweise fortsetzen sowie sichtbare Recovery und bestätigten Einzelreset. Codex liefert Szenarien/Artefakt und darf unbekannte Ergebnisse nicht abhaken. Die positive F-01-Teilbestätigung bleibt erhalten.

Vor Gesamt-P1-Merge gelten weiterhin A-01 bis A-07 und M-01 bis M-04, M-06/M-07 aus P1 §8. M-05 bleibt nicht anwendbar. #11 liefert A-05 technisch und ermöglicht M-04; #12 und vollständige manuelle Abnahme bleiben separat. Ohne passende Freigabe kein Merge/Release.

## Daten und Betriebswirkung

Keine Laufzeitdienste oder Produktionsdaten eingerichtet. Prüfungen verwenden isolierte temporäre Daten; kein Zugriff auf echte Spielstände, private Daten oder kostenpflichtige Dienste aus einer Entwicklungsfreigabe. Öffentliche gepinnte Godot-Assets dürfen für den vereinbarten Prüfweg geladen werden. Zusätzliche Assets/Abhängigkeiten auf Notwendigkeit und Nutzungsrechte prüfen; keine Secrets einchecken.

Setup-, Preflight- und Produkt-CI arbeiten mit lesenden Repositoryrechten. Kein Deployment, Release, Tag oder Hosting. Externe Automatisierungen außerhalb gelesener Repositoryquellen sind nicht als geprüft behauptet.

Die [ChatGPT-Projekteinstellungen](CHATGPT_PROJECT_INSTRUCTIONS.md) werden separat durch den Nutzer eingesetzt. Die lokale Modellheuristik ersetzt alte allgemeine Modellanweisungen einschließlich eines Pflichtverweises auf `Codex-Empfehlung.txt`; keine zweite Heuristik parallel aktivieren.
