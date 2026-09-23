# Projektprofil: picross

## Zweck, Quellen und aktueller Rahmen

`venomenon328/picross` enthält Produktkonzeption, Entwicklungsregeln, Dokumentprüfung, den technischen [P1.0-Preflight](P1_PREFLIGHT.md) und den ausführbaren [P1.2-Mausschnitt](../prototypes/p1/README.md) unter `prototypes/p1/`. P1.2 liegt im gemeinsamen Draft-PR #14 vor, noch nicht auf `main`. Der [Workflow](dev-rules/WORKFLOW.md) ist Prozessgrundlage, [AGENTS.md](../AGENTS.md) der Einstieg. Lieferumfang und Freigaben stehen im jeweiligen Issue/PR, nicht in einer parallelen Roadmap.

Die [Produktdefinition](PRODUCT_DEFINITION.md) ist bei Produktkonzept, Rätselregeln/-inhalten, Progression/Wertung, UX/UI, Eingabe, Plattformkonzept oder Produktarchitektur vollständig zu lesen. Sie unterscheidet Beschlossenes von Vorschlägen und offenen Fragen; ihr Entwicklungsablauf ist keine Implementierungsfreigabe.

Das [Gestaltungskonzept](DESIGN_CONCEPT.md) ist bei Thematik, Album, Motiventhüllung, UX/UI, Eingabe/Wertung und entsprechenden Prototypen zusätzlich vollständig zu lesen. Positive Mock-Rückmeldung ist keine Abnahme aller dargestellten Details. Revision 0.4 übernimmt das konkrete Mausfeedback einschließlich Zelltrennung, motivtreuer Enthüllung und pannbarer atomarer Hinweisabschnitte.

Für P1 außerdem vollständig lesen: [P1-Spezifikation](PROTOTYPE_P1.md), [Issue #5](https://github.com/venomenon328/picross/issues/5) samt späteren Entscheidungen und das beauftragte Paket. Bei technischer P1-Arbeit zusätzlich [P1.0](P1_PREFLIGHT.md), [aktuelle Anleitung](../prototypes/p1/README.md) und [P1.1-Prüfbericht](P1_1_VERIFICATION.md), ab #9 auch [P1.2-Prüfbericht](P1_2_VERIFICATION.md). Der versionierte Fachvertrag steht in der Spezifikation, Auftrag und Abnahmestand in Issue/PR.

**Aktuelle Phase:** #9 implementiert D-07 bis D-17 der Spezifikation 0.6 samt
Farb-/Großrasterbedienung und der Nacharbeit zu Review R2/B-01/B-02 auf dem bestehenden
P1-Draft. Der [P1.2-Prüfbericht](P1_2_VERIFICATION.md) und die aktuelle Anleitung
beschreiben Umsetzung und technische Nachweise. Reale Eigentümerabnahme, #11/#12 und
Gesamtmerge bleiben offen. Der historische #8-Nachweis und die alten grünen Läufe auf
`267df8c…`/`bd6730d…` werden dadurch nicht rückwirkend zum Nachweis des neuen Heads.

Der [Herkunftsnachweis](DEV_RULES_ADOPTION.md) bezeichnet die unveränderte Regelkopie. Keine abschließende Produktarchitektur oder universell erprobte Produkt-Teststrategie behaupten. Weitere Pflichtquellen erst mit tatsächlich beschlossenen Inhalten anlegen.

## Beschlossene Richtung und offene Entscheidungen

Produktkern: klassische und farbige kuratierte PC-Bildrätsel, Großrasterfokus, präzise Eingabe, Offline-Solo-Spiel, frühe visuelle Gestaltung sowie der bestätigte Progressions-/Wertungsrahmen. Das ursprüngliche Setup hatte weder Spielmechanik noch Technik festgelegt.

Visuelle Grundlage: sich füllendes Album, warme ruhige 2D-Illustration mit klaren Konturen und Farbflächen, motivtreue Abschlussbilder, Perfektion nur ohne Fehler und ohne Undo. Sammelalbum/Reisealbum bleiben Alternativen. Detailliertere Abschlussbilder dürfen die Rasterstilisierung verfeinern; pixelidentische Silhouetten sind kein allgemeines Qualitätskriterium.

P1: native Windows-Desktopfassung, typisiertes GDScript, Godot Standard 4.7.2-stable mit passenden Standard-Exportvorlagen, keine Wertung/Live-Fehlerhilfe/Hypothesen. D-06 bleibt verbindlich: Maus, kein Tastatur-/Controller-Scope oder entsprechendes Gate. Escape bleibt der vereinbarte Abbruch einer Mausgeste. Spätere alternative Produkteingaben werden dadurch nicht gestrichen.

Ab #9: größerer Fensterstart ohne erzwungene Zellvergrößerung, getrennte UI-/Raster-
Skalierung, visuelle Zelltrennung auch an Fünferlinien, direkte Füllung↔X-Umwandlung
mit links/rechts bei einmalig festgelegtem Strichmodus, detaillierteres F-01-Ergebnisbild,
unnummerierte Hinweise direkt im Arbeitsbild, farbige Hinweiszahlen mit optionalen
A–D-Kennungen sowie feiner monotoner Zoom. Überlaufende Folgen behalten vollständige
einzelne Hinweise und sind in einem vertikalen Spalten- beziehungsweise horizontalen
Zeilenbereich unabhängig vom Raster pannbar. Verbindliche Details ausschließlich in
P1 §§4–5; D-11 bis D-17 lösen widersprechende alte D-09-/Hinweisregeln ab.

Referenzhardware aus früheren Nutzerangaben: Windows 11, 2560×1440, Maus, Ryzen 7 5800X, RTX 3070. Tatsächliche Windows-Skalierung, Fensterfläche und Versionskennung des Nutzerlaufs sind nicht aus Screenshotgrößen bestätigt. Fehlende Daten sichtbar lassen und bei der erneuten Probe erfassen.

Endgültige Engine/Sprache, gesamte Betriebssystemmatrix, Produktpersistenz, Solver-/Produktionsverträge, Fehlerzählung, Sternschwellen, Wertungswirkung manueller Neutralisierung und Veröffentlichungsdetails bleiben außerhalb dieser begrenzten Festlegungen offen. Keine Regeln aus anderen Projekten übernehmen. Python dient hier Prüf-/Buildwerkzeugen, nicht der Wahl eines Produktstacks.

## Branches und Befugnisse

Zielbranch `main`; Standardmerge Squash nach ausdrücklicher oder passender bedingter Freigabe. Keine automatische Branchlöschung, kein Force-Push und keine direkten Änderungen am Zielbranch ohne passende Befugnis.

Der beauftragte gemeinsame Arbeitsbranch ist `feat/5-p1-prototype`, Draft-PR #14. #9 setzt dort auf #8 auf, nicht auf einem frisch von `main` abgezweigten Parallelbranch. Bestehenden Branch/PR nicht ersetzen. #9, #11 und #12 werden separat beauftragt, im gemeinsamen P1-Draft integriert und mit ihren eigenen Tests/Nachweisen geliefert. #5 bleibt bis vollständiger Lieferung und Abnahme offen.

Vorbereitung allein erlaubt keine Spielimplementierung. Der ausdrückliche Implementierungsauftrag für #9 erlaubt die spezifizierten Änderungen, Tests, Commits, Push und Aktualisierung desselben Draft-PRs, nicht die Ausführung von #11/#12 oder Merge.

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

Der [Produkt-Harness](../tools/p1_product.py) nutzt diese Grundlage mit temporärer Projektkopie und eigenen APPDATA-/LOCALAPPDATA- beziehungsweise XDG-Pfaden. P1.1/P1.2 haben noch keine dauerhaften Spielstände. Lokale Windows-Prüfungen sind erlaubt. Prozesslimit 300 Sekunden, Downloadlimit 1200 Sekunden, CI-Joblimit 40 Minuten.

```powershell
$p1Cache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $p1Cache --output-dir artifacts/p1-product
```

Unter Linux `python3` und externen Cachepfad verwenden. Der bestehende Ablauf prüft F-01s Zertifikat, Import, Godot-Tests, erwarteten Negativtest mit Exit 23, begrenzten Start der Hauptszene und Windows-Export mit `P1 Windows x86_64`; auf Windows zusätzlich exportierten Start. Bericht, Phasenlogs und vollständiges ZIP mit EXE-Paar/Anleitung/Commitkennung werden erzeugt. Quellhead, getesteten Checkout/Test-Merge und veränderten Arbeitsbaum unterscheiden.

#9 erweitert diesen Ablauf für F-02/F-03, direkte Gestenumwandlung und Rücknahme,
farbige atomare In-Context-Hinweise, zwei Hinweis-Panachsen, feinen monotonen Zoom,
Ansichts-/Miniaturtransformationen, Resize und unabhängige Abschlussressourcen.
Teständerungen zu D-09 bis D-17 sind
gezielte Vertragsanpassungen; sonstige Regressionen nicht durch Entfernen von Tests
verdecken. F-01-Lösung/Hinweise und logische Nachweise erhalten. Keine neue allgemeine
Solver-/Assetplattform erforderlich.

Für die technische Lieferung von #9 müssen `product` aus [P1 product verification](../.github/workflows/p1-product.yml), `docs` und der weiterhin aktive `preflight` für den aktuellen Stand tatsächlich erfolgreich sein. Produktartefakte werden im bestehenden Weg 14 Tage gespeichert. Ein Headless-Start oder synthetisches Event ersetzt keine reale Maus-/GUI-Abnahme. Die neuen Layout-/Zelltrennungs-/Reveal-Kriterien benötigen außerdem echte Renderkontrolle mit dokumentierten Größen, nicht nur Assertions über Objektmaße.

## Abnahme und Übergaben

Vollständigen Diff gegen den Auftrag prüfen: keine versteckten Produktentscheidungen, Secrets, ungeklärten Assets, unerreichbaren Pflichtquellen oder ungefragten Änderungen der gemeinsamen Regeln. Technischen Nachweis, Selbstreview, Nutzerprobe, Merge- und Releasefähigkeit unterscheiden. Ein getrennter Selbstreview ist keine unabhängige Zweitprüfung.

Der Review R1 in PR #14 bezieht sich auf den P1.1-Head `64dcca4df9ed00cecedfdb8cabba09bcb7179ae8`, nicht auf die damaligen noch ausstehenden #9-Funktionen. K-06 wurde anschließend vom Nutzer erprobt und mit zwei Screenshots/vier Folgepunkten beantwortet. **Durchgeführt mit Änderungsbedarf** ist keine pauschale positive Abnahme aller Szenarien. Einzelbestätigungen und tatsächliche Skalierung fehlen teilweise.

Review R2 bezieht sich auf `267df8cdb264070ed1f81e500475657be6f27f9d` und
nennt B-01 (invertierbare Zoomrichtung aus der Gesamtansicht) sowie B-02 (Mojibake im
Projekttitel). Die folgende Eigentümerprobe ergänzt D-11 bis D-15 als neuen Sollstand;
die Probe nach Review R3 ergänzt D-16/D-17 zur Kürzung und Hinweisnavigation.
Die Nacharbeit behebt diese technischen Punkte, ersetzt aber weder ein Review des neuen
Heads noch die weiterhin offene reale Eigentümerprobe.

Der ausdrückliche Folgeauftrag zur Umsetzung von #9 bearbeitet dieses Feedback; fehlende Metadaten sind weiterhin bei der erneuten Probe zu erfassen. Die erneute reale Maus-/Layoutprobe an der #9-Lieferung erfasst diese Daten und prüft Teilhinweise, beide Hinweis-Panachsen, ihre feste Rasterzuordnung sowie die übrigen offenen Bedien-/Motivfälle. Der Eigentümer ist dafür zuständig; Codex liefert Szenarien/Artefakt und darf unbekannte Ergebnisse nicht abhaken.

Vor Gesamt-P1-Merge gelten weiterhin A-01 bis A-07 und M-01 bis M-04, M-06/M-07 aus P1 §8. M-05 bleibt nicht anwendbar. Es entsteht kein neuer verpflichtender Hardware- oder Zwischenmergeprozess. #9 liefert einen technisch geprüften Zwischenstand; #11/#12 und vollständige manuelle Abnahme bleiben separat. Ohne passende Freigabe kein Merge/Release.

## Daten und Betriebswirkung

Keine Laufzeitdienste oder Produktionsdaten eingerichtet. Prüfungen verwenden isolierte temporäre Daten; kein Zugriff auf echte Spielstände, private Daten oder kostenpflichtige Dienste aus einer Entwicklungsfreigabe. Öffentliche gepinnte Godot-Assets dürfen für den vereinbarten Prüfweg geladen werden. Zusätzliche Assets/Abhängigkeiten auf Notwendigkeit und Nutzungsrechte prüfen; keine Secrets einchecken.

Setup-, Preflight- und Produkt-CI arbeiten mit lesenden Repositoryrechten. Kein Deployment, Release, Tag oder Hosting. Externe Automatisierungen außerhalb gelesener Repositoryquellen sind nicht als geprüft behauptet.

Die [ChatGPT-Projekteinstellungen](CHATGPT_PROJECT_INSTRUCTIONS.md) werden separat durch den Nutzer eingesetzt. Die lokale Modellheuristik ersetzt alte allgemeine Modellanweisungen einschließlich eines Pflichtverweises auf `Codex-Empfehlung.txt`; keine zweite Heuristik parallel aktivieren.
