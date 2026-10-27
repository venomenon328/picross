# Projektprofil: picross

**CI2 · 27.10.2026, A/B/C/D integriert; E implementiert, R01 offen:**
[Kurze CI und begrenzter aktiver Bestand](CI_SLIMMING.md) bindet #412–#417.
CI2-A/B sind nach ihren separaten Reviews über PR #419/#420 integriert;
Basis für C ist `dd56d310d942eee47448df4cdcca5e4af4a49b00`.
[Auswahl](CI_A_SELECTION.md) und [B-T01](CI2_B_VERIFICATION.md) bleiben gebunden,
CI2-B-O01 bleibt im Gesamtvorhaben offen. [Browserumfang](CI_B_BROWSER_GROUPS.md)
und [C-T01](CI2_C_VERIFICATION.md) bleiben historisch gebunden; C ist nach
separatem R01 über PR #421 auf `8e5e99647596bc3ef9d7bd22bd746b73fbb424d5`
integriert. D ist nach separatem R01 über PR #422 auf
`8c31a69916941aed60ecd7e4d35a8d0d00637bf9` integriert; [D-T01](CI2_D_VERIFICATION.md)
bleibt historisch gebunden. E ist auf `chore/417-ci2-e-cleanup` implementiert;
[E-T01](CI2_E_VERIFICATION.md) weist den tatsächlichen Datenabbau nach.
Unabhängiges E-R01 bleibt vor Merge offen. Kein Merge oder Deployment.

Chromium läuft ausschließlich auf ausdrücklichen manuellen Auftrag,
auch nicht implizit durch `all`, `toolchain` oder gemeinsame Änderungen.
Der kurze Browserumfang umfasst ungefähr 8–10 Kernfälle; der native Historyweg
höchstens 20 Benutzerkommandos, höchstens sechs neue wirksame Transaktionen und
genau zwei echte Spielprozesse. Die 500er-Route entfällt aus den aktiven Standard-
und gewöhnlichen manuellen Vollumfängen. Kleine Fachtests, repräsentative
Integrationen, gezielte Bildbelege, Laufzeitziele und begrenzte Ablagen ersetzen
die in CI_SLIMMING ausdrücklich abgelösten Altpflichten. Quellenbindung,
Fail-closed-Gate und aktuelle Produkt-/Speicherverträge bleiben erhalten.
Gemessene Browserbeschleunigung folgt C-T01; native Kürzung und Messung folgen
D-T01. Revisionsabschluss und Bestandsbereinigung folgen E-T01.

**HZ · HZ-A/B am 20.10.2026, HZ-C am 21.10.2026 integriert:**
[Handgezeichnete Bedienoberfläche](HAND_DRAWN_UI.md) bindet die normale
Spieler-UI gemäß HZ-A-FONT02 an Tidy Hand als Standardtext (Überschriften
unverändert) und stärker gezeichnete kleine Rahmen, vollständige
Dropdowns und eine gemeinsame Piktogrammfamilie. [HZ-A](HZ_A_VERIFICATION.md)
und [HZ-B](HZ_B_VERIFICATION.md) sind über
[PR #288](https://github.com/venomenon328/picross/pull/288) (`e9a957d`) und
[PR #289](https://github.com/venomenon328/picross/pull/289) (`18152d0`) integriert.
Ihre Abnahmen stehen im abgeschlossenen
[Issue #284](https://github.com/venomenon328/picross/issues/284).

Das integrierte [HZ-C / #294](https://github.com/venomenon328/picross/issues/294)
führt optische Textausrichtung, stabile Grundlinien und die gemeinsame kleine
Schriftrolle gemäß HZ-D07 zusammen. Die [Lieferung](HZ_C_VERIFICATION.md)
begründet nach direktem Vergleich der korrigierten 14/15 die Wahl 15 bei UI100
und 19 bei UI125 einschließlich Kategorien; Blattkennungen bleiben 15/19. Delight-Hinweise samt Geometrie,
Überschriften, Originalfontbytes und die drei großen SL-Rasterrahmen bleiben.
HZ-C ist mit [PR #296](https://github.com/venomenon328/picross/pull/296)
auf `a969105` integriert. Die paketbezogenen Liefer-/Review-/Eigentümernachweise
bleiben an ihre jeweiligen Quellen gebunden; CI2 schreibt sie nicht um und
verlangt keine neue historische 14/15-Vergleichsgalerie.

**AT / #256 · AT-A und AT-B am 19.10.2026 integriert:**
[Transparente Abschlussbilder](REVEAL_TRANSPARENCY.md) ist bei Abschlussbildern,
deren Katalogvorschau und Bildrevisionen samt den dort benannten Fachquellen
vollständig zu lesen. Dasselbe freigegebene Bild lässt in beiden Ansichten den
Papieruntergrund durch neutrale Außenflächen und echte Aussparungen durchscheinen.
Helle Motivteile, Konturen und Komposition bleiben erhalten; Szenen benötigen
eine tatsächlich vorgelegte transparente Gestaltung und neue Bildfreigabe.
Kein Renderer-Weißfilter, keine Änderung von Fragezeichen, eigener Füllminiatur,
Spoilergrenzen oder EA-Enthüllung.

AT-A liefert den sicheren gemeinsamen Weg für reine Bildrevisionen samt
Quellenbindung, versionierter binärer Ersetzung/Recovery, Produktionsstandard
und synthetischen Regressionen. AT-B stellt anschließend den vollständig
inventarisierten Startbestand mit konkreten Bildfreigaben kontrolliert um.
Definitionsbytes, Puzzle-Runtime-Revision, IDs/Slots/Pfade, Spielstände,
Schwierigkeits-/Hinzugefügt-Metadaten und ursprüngliche Freigabebelege bleiben
erhalten. Aktive Bildrevisionen erhalten eine getrennte überprüfbare Bindung;
spätere gemeinsame Operationen dürfen sie nicht verlieren.

AT-A ist mit [PR #263](https://github.com/venomenon328/picross/pull/263)
auf `a0cb25eda49d29d3062fd3bcfeab9fda220c7aa9`, AT-B mit
[PR #264](https://github.com/venomenon328/picross/pull/264) auf `8dac7a6`
integriert. [Gesamtissue](https://github.com/venomenon328/picross/issues/256),
[AT-A-Nachweise](AT_A_VERIFICATION.md), [AT-B-Bericht](AT_B_VERIFICATION.md)
und [Eigentümerabnahme](AT_B_OWNER_APPROVAL.md) binden die damaligen Lieferungen,
Reviews und konkreten Bildfreigaben. Sie sind keine offenen Implementierungsaufträge
und keine neue CI-Matrix pro Bestandsbild. Historische KE-/KU-Nachweise behalten
ebenfalls ihren Quellenbezug.

[ZA-1](ZA1_ADAPTER.md), [Auflösung](CATEGORIES.md), [Transaktionen](SD_CATALOG.md)
und [CLI](../tools/puzzle_production/README.md) enthalten exakte Quellen-,
Plan-, Binärjournal- und Recoveryregeln. AT ließ Inhalts-v2 und Save-Schema 1
unverändert; die aktuelle Runtime-/Bewertungsversion folgt dem unten genannten
integrierten SD2-Vertrag.

**Ausführbare CI-Ausgangsbasis aus #246/#261:**
[CI-A-Auswahl](CI_A_SELECTION.md), [CI-B-Browsergruppen](CI_B_BROWSER_GROUPS.md)
und [CI-C-Nativgruppen](CI_C_NATIVE_GROUPS.md) beschreiben die bestehenden
Mechanismen und gebundenen Nachweise. Ihre automatischen/impliziten Browserrechte,
ungekürzten Altfall-/Bildmengen, 500er-Route und der allgemeine Budgetverzicht
sind durch CI2 als Sollvertrag gezielt abgelöst. Bis zur jeweiligen Umsetzung
werden ausgewählte fehlende oder übersprungene Jobs nicht zu Erfolgen umgedeutet.
Die Entfernung von Firefox aus CI gemäß #261, die Sperre alter Workflow-IDs,
exakte Diff-/Quellenbindung, isolierte Prüfdaten und getrennte Produktgates bleiben.
Historische Reruns sind kein Mergegate und werden nicht neu beauftragt.

**KU / #244, integrierte Ausgangsbasis für HZ:** KU-A und KU-B sind über
PR #254/#255 integriert. [KU-A-Nachweise](KU_VERIFICATION.md),
[KU-B-Nachweise](KU_B_VERIFICATION.md) und die getrennten offenen persönlichen
Abnahmen bleiben an ihre jeweiligen Stände im Issue gebunden.
[Katalogdarstellung](CATALOG_PRESENTATION.md) und
[Katalogsortierung](CATALOG_SORTING.md) sind bei Katalog-/Metadatenarbeit
vollständig zu lesen. KU-A ersetzt die zweizeilige KE-Infobox durch einen
gemeinsamen Papierstreifen mit Größe, gefülltem Schwierigkeitskreis samt vollem
Namen und größeren Modussymbolen; der einzelne Monostift verliert die Farbprobe.
Schwierigkeitstooltips entfallen, Modus-/Resettooltips bleiben. Die Fußzeile zeigt
Blattkennung links und Neu/Begonnen/Gelöst rechts. Gemeinsame Kartenbreite folgt
den tatsächlichen vollständigen Text-/Symbolmaßen bei UI100/125, bei Bedarf mit
weniger Spalten. KU-B ergänzt Kategorie-/Zellzahl-/Schwierigkeits-/Hinzugefügt-
Sortierung, eigene gemerkte UI-Präferenz und den kompatiblen Metadatenweg für
erste Katalogaufnahme samt belegter historischer Übernahme. Werte, IDs und
Spielstände werden dadurch nicht neu bewertet oder migriert.

KU-A und KU-B wurden als eigene Pakete im
[Gesamtissue](https://github.com/venomenon328/picross/issues/244) geliefert.
Die dort auf `main` verlegten Eigentümerproben sind keine HZ-Abnahme;
damalige Mergeausnahmen werden nicht auf HZ übertragen.
Die folgenden KE-/KAT-Abschnitte beschreiben die integrierte Ausgangsbasis;
ihre gezielt abgelösten Anzeige-/Sortierregeln gelten nicht als neuer KU-Sollstand.

**SD2 / #402 · SD2-A/B/C/D integriert; aktive Methode 0.4 für alle 45 Inhalte:**
[Menschennähere Schwierigkeit](PUZZLE_DIFFICULTY_V2.md) führt den neuen Sollvertrag:
Denkanspruch, Suchaufwand und Bearbeitungsumfang, menschennähere Basistechniken,
fein abgestufte interne Bewertung mit festen Grenzen und unabhängiger breiter
Referenz-/Validierungsbasis. Die sichtbare Skala 1–5 bleibt; keine Quoten,
Zeitprognosen oder neuen UI-Funktionen. SD2-A/B/C/D (#403–#406) liefern sequenziell
Analyse, eingefrorene Methode, kompatible Integration und tatsächliche Umstellung.
SD2-A liefert über [PR #408](https://github.com/venomenon328/picross/pull/408)
den vor Code versionierten [Analysevertrag](SD2_ANALYZER.md), neue Regeln,
unabhängige Spurprüfung, drei Rohprofile und eigene CLI. Bei SD2-Analyse ist
dieser Vertrag zusätzlich vollständig zu lesen. [SD2-A-T01](SD2_A_VERIFICATION.md)
bindet die historischen technischen Nachweise. Nach separatem R01 integriert
auf `c7c6156ac27dc033036443bc06ef398bbf94f32f`.
SD2-B liefert über [PR #409](https://github.com/venomenon328/picross/pull/409)
36 unabhängige synthetische Referenzen, getrennte Validierung, den
[numerischen/technischen Vertrag](SD2_CALIBRATION.md) und den eigenständigen
0.4-Freeze. Bei SD2-Bewertung diesen Vertrag vollständig lesen.
[SD2-B-T01](SD2_B_VERIFICATION.md) bindet technische Nachweise und Selbstreview;
SD2-B ist nach separatem R01 auf `0ae6535073fb808af44dcf3e12130a33ba49cdbc`
integriert. Die B-Nachweise behalten ihre historische Headbindung.
Der vor Code festgelegte [SD2-C-Integrationsvertrag](SD2_INTEGRATION.md) ist bei
Integrationsarbeit vollständig zu lesen. Er ergänzt die alten Quellen-/Runtime-/
Journalverträge explizit versioniert. Tatsächliche Bestandsumstellung und Aktivierung
bleiben #406 vorbehalten; C prüft ausschließlich synthetische Fälle.
[SD2-C-T01](SD2_C_VERIFICATION.md) behält seine historische Headbindung.
C ist nach separatem R01 über [PR #410](https://github.com/venomenon328/picross/pull/410)
auf `4e23e644f3457362e02b75f78fdb575a99265494` integriert. Die dortige
[Eigentümerausnahme](https://github.com/venomenon328/picross/pull/410#issuecomment-6404111838)
zum fehlenden Gesamt-CI-/Chromium-Gate gilt ausschließlich für #410.
[SD2-D-V01](SD2_D_VERIFICATION.md) bindet den tatsächlichen Bestandslauf,
Vergleich und Planungsstand. [SD2-D-OM01](SD2_D_OM_FOLLOWUP.md) ergänzt den
frischen Om-Nachweis und die vollständige Vorschau mit 45 gültigen Ratings.
Alle 45 Vorschläge einschließlich Om sind abgenommen. Der ausdrückliche
Eigentümerverzicht auf separates SD2-D-VR01 gilt nur für diesen Auftrag;
es wurde nicht durchgeführt. [F01/T01](SD2_D_ADOPTION.md) bindet die Übernahme
aller 45 Ratings und Aktivierung von 0.4, jeweils mit unmittelbarem echtem No-op.
SD2-D ist am 26.10.2026 mit [PR #411](https://github.com/venomenon328/picross/pull/411)
auf `967314538df376a281020fb4c34f93f370a491df` integriert: Runtime-v5,
Ratingrevisionen 2, Defaultrevision 1. Der damalige fehlende Web-/Gesamt-CI-Nachweis
bleibt als solcher an den Auftrag gebunden; Integration macht ihn nicht nachträglich
grün. Aktuelle Review-/Mergeentscheidungen stehen im PR, nicht in einer weiterhin
offenen Arbeitsbranch-Anweisung dieses Profils.

**Historische SD-Basis / #235:** SD-A/B/C1/C2 sind mit PR #240–#243 abgeschlossen;
letzter Merge `72ba39391833f6fd834d0a6afaf881c86c7bdc3a` nach finalem C2-Review.
[SD](PUZZLE_DIFFICULTY.md), [Analysator](SD_ANALYZER.md),
[0.3-Freeze](SD_CALIBRATION.md) und [Daten-/Recoveryvertrag](SD_CATALOG.md)
bleiben als Altverträge gültig. 0.4 ist separat eingefroren und durch D aktiviert; historische Quellen,
Bewertungen und Freigaben werden nicht umgeschrieben. Der echte Katalog dient
nur einer ausdrücklich beauftragten manuellen Plausibilitätsprüfung und Übernahme,
nicht der Kalibrierung von Skalenenden oder automatisierten Tests. Keine
Analyse/Aktivierung durch CI, Runtime, Build oder bloße Methodeninstallation.

**KE / #233 (17.10.2026), mit PR #234 in `main` integriert:**
Bei Katalog-/Metadatenarbeit zusätzlich [Katalogdarstellung](CATALOG_PRESENTATION.md)
vollständig lesen. Papieretikett mit Größe, Moduspiktogramm, Schwierigkeit und
Status; gezeichnetes Fragezeichen nur für Neu. KE ersetzt gezielt KK-Metadaten,
Fußzeilenstatus und leere Neu-Vorschau, ergänzt gezielte Modus-/Schwierigkeits-
Tooltips und eine minimale kompatible Runtimeprojektion der Schwierigkeit.
KE-T01, KE-R01, KE-M01 und zugehörige Abnahmeentscheidungen bleiben in #233/PR #234
dokumentiert; SD öffnet diese Lieferung nicht erneut.
Der folgende KK-Abschnitt beschreibt die integrierte Ausgangsbasis; die historischen
offenen KK-R01/KK-M01 in #174 werden durch KE weder erledigt noch erneut beauftragt.

**EA / #170:** Abschlussenthüllung auf dem integrierten KB-Stand aus PR #169.
[EA-Prüfzuordnung](EA_VERIFICATION.md) zusätzlich lesen: sofortiger Commit/Save,
transiente 2,15-s-Präsentation, neutrale Blattüberschrift, proportionale Bildfläche,
ursprungsgebundener Reset. EA-T01 verlangt aktuelle technische Lieferung samt
nativer Bewegung, Windows und Browsern; EA-R01 und EA-M01 bleiben getrennt vor Merge.

**KK / #174:** Feste gleiche Katalogkarten/-Grid-Zellen, zweizeilige kleinere
Bakso-Motivüberschrift oder `???`, feste Metadaten/Bildfläche/Fußzeile. Kartenfläche
öffnet; Reset allein oben rechts, bei gültigem fehlerfreiem Neu verborgen, bei
Bearbeitung und Speicher-/Recoveryzuständen erreichbar. Fehler und Backupaktionen
bleiben innerhalb des Bildraums, Kacheltooltips entfallen. KK löst gezielt die
betroffenen KB-D01/D02-Regeln ab; BookButtons, Ressourcen, KAT/EA und Saveverträge
bleiben. [KK-Prüfzuordnung](KK_VERIFICATION.md) zusätzlich zu
[KB](KB_VERIFICATION.md), KAT-1/ZA-1/KAT-2 und EA lesen. KK-T01 bindet technische
Lieferung samt Windows/Web; **KK-R01 und KK-M01 bleiben getrennt vor Merge**.

**ZR / #143 (15.10.2026):** [Zellstriche und Cursorzähler](CELL_DRAG.md) ist als
Sollvertrag freigegeben und im PR #145 umgesetzt. Zähler ab Länge 2 in der aktiven
Hinweisfont, ohne Kasten, am tatsächlichen Cursor; außerhalb des Fensters bleibt er
am inneren Clientrand sichtbar. Begonnene Striche folgen der Maus bis zum Rasterrand,
auch über anderer UI und bei fokussiertem Windows-Fenster außerhalb der Clientfläche.
Fokusverlust bleibt vollständiger Abbruch. Der Vertrag ersetzt gezielt die alten
P1-/Designregeln zu sichtbarer 1, Strichendanker und eingefrorenem Außenendpunkt;
Laufzeit, Spielanleitung und native Hilfe folgen dem ZR-Vertrag.
[Prüfzuordnung](CELL_DRAG_VERIFICATION.md) und #143/#145 führen aktuelle Nachweise;
native Windows-Eingabeprüfung bleibt getrennt von CI und Eigentümerprobe gebunden.
Der Eigentümer hat am 15.10.2026 für diesen Merge ausdrücklich auf das unabhängige
Review und ZR-M01 verzichtet. Beide gelten damit nicht als durchgeführt;
Pflicht-CI und technische native Windows-Probe bleiben erforderlich.

**WEB-1 / #162:** Zusätzlich ist ein statischer Godot-Webentwicklungsweg für
Desktop/Maus ursprünglich in Chromium und Firefox beauftragt. Firefox ist gemäß
#261 aus CI entfernt; CI2 verlangt Chromium ausschließlich bei ausdrücklichem
Auftrag und mit dem dort begrenzten Umfang. [Webanleitung und Grenzen](WEB_HOSTING.md)
binden Browserpersistenz, getrennten Build, manuelles SSH-Deployment und isolierte
Referenztests. Windows bleibt erhalten; keine endgültige Plattformmatrix oder
Livefreigabe. Bei Web-/Hostingarbeit diese Anleitung zusätzlich vollständig lesen.

**Aktuelle Inhalts-CI (12.10.2026):** Die [CI-Policy](CI_POLICY.md) ersetzt die
unten historisch beschriebenen RP-Korpus-/Zertifikats-Replays. Reine neue
Rätseldateien erhalten nur Pfad-/Dateimodusprüfung und `ci-required`, keine
Tool-/Spiel-/Render-/Exporttests. Sämtliche konkreten Rätselprüfungen erfolgen im
Produktionsauftrag; keine rätselspezifischen Unit-Tests anlegen. Allgemeine
Code-Regressionen verwenden einen festen technischen Testbestand.

[KAT-1](CATEGORIES.md) bindet `content/categories.json`, genau eine Kategorie je sichtbarem Rätsel, Inhaltsregistry v2 und Runtimeprojektion v3 (Loader auch v2, KE) und kategorisierte ZA-1-v2-Exporte. Bei Kategorien-/Katalog-/Adapterarbeit zusätzlich diesen Vertrag und [ZA-1](ZA1_ADAPTER.md) vollständig lesen. [KAT-1-Prüfzuordnung](KAT1_VERIFICATION.md) ergänzt die bestehenden Prüfwege; Saves, Definitionen und Freigabebindungen bleiben unverändert. KAT-2 (#79) verwendet diesen Vertrag für den regulären Katalogstart. Bei Katalogarbeit zusätzlich [KAT-2-Prüfzuordnung](KAT2_VERIFICATION.md) lesen; unabhängiges Review und Eigentümerabnahme KAT2-M01 bleiben vor Merge erforderlich.

**CI-Folgearbeit #116 (14.10.2026):** Die freigegebene aktuelle Grafikabdeckung
und ihre drei gemeinsamen Fenster-/UI-Konfigurationen stehen in der
[CI-Policy](CI_POLICY.md). Historische erzwungene Raster-Replays entfallen;
aktuelle gezielte Funktions-/Pixelprüfungen bleiben. Der Windows-Debugexport
liefert Ressourcen separat in `picross-p1.pck`; EXE und PCK gehören zusammen.

## Entwicklungsbasis und Grenzen

Das reguläre Spiel liegt unter [game/](../game/README.md). Ausgangspunkt der
Konsolidierung #70 ist `main@0f89f08729539bbb4a02a590cbd18e58fbbda305`, einschließlich
[PR #66](https://github.com/venomenon328/picross/pull/66) (Sidebar und PERF-A/B).
Frühere Draft-/Mergegate-Meldungen zu #47/#55/#56/#62/#66 sind historische Lieferstände.
Die dortigen Abnahmen bleiben an ihre jeweiligen Quellen gebunden.

Der Katalog enthält ausschließlich registrierte Workflow-Inhalte aus
`content/registry.json`; diese Registry führt den aktuellen Bestand.
[#114](https://github.com/venomenon328/picross/issues/114) ersetzt die
frühere aktive Reservierung der Prototypen F-01 bis F-09. Definitionen und Reveals
werden nicht mehr mit dem Spieler ausgeliefert. Historische Nachweise bleiben
commitgebunden; eingefrorene Save-Kompatibilitätsinputs liegen nur unter Tests.
Reguläre Rätsel sind gemäß #68 höchstens 50×50 groß. IDs, Revisionen, Dateien und
Freigabebindungen aller Workflow-Rätsel bleiben unverändert. Appidentität, Save-Schema
und Speicherroot bleiben erhalten; verwaiste Savedateien werden nicht angefasst.

Laufende Arbeitsstände und ZIPs der Rätselproduktion liegen in
[content/authoring](../content/authoring/README.md); Wiederaufnahme und Integration
folgen [PUZZLE_AUTHORING](ai-workflows/PUZZLE_AUTHORING.md), Abschnitten 6 und 8.
Die Arbeitsablage ist keine Runtime-Registrierung. Nach Endabnahme und Main-Merge
werden Produktionsdaten nach PUZZLE_AUTHORING §9 entfernt; kompakte Integrations-
bindung und Runtime-Dateien genügen für die abgeschlossene Produktion; keine
dauerhafte Wiederholungspflicht für Bild-/Rasterproduktion oder alte Proofs.
SD-C1 ergänzt dauerhaft erhaltene kompakte Bewertungsdaten und Berichte
für ausdrücklich beauftragte Neueinstufungen aus den vorhandenen Definitionen.

[ZA-1](ZA1_ADAPTER.md) ermöglicht weitere freigegebene Workflow-Inhalte über eine
zentrale Datenregistry mit expliziten Slots, einschließlich Mono/Farbe und Rechtecken.
Künstliche Fixtures bleiben isoliert. Registrierte Pakete tragen ihre eigenen
gebundenen Freigaben; frühere Aussagen zu offenen Einzelfreigaben sind historisch.

[#139 B/C](PAIRED_LINES.md) ergänzt ausdrücklich gewählte Paarlinienprofile,
unabhängige Proof-v3-Prüfung und Schwierigkeit 0.2/R4 innerhalb L5. Authoring
0.5.0 und ZA-1-v4 binden die neue Zertifizierung; Paket A und alte Linienverträge
bleiben erhalten. Diese Werkzeugänderung registriert keine neuen Inhalte.

Aktuelle Bindung: Godot Standard 4.7.2-stable, typisiertes GDScript, native
Windows-Desktopfassung, Maus als verpflichtender Eingabepfad (D-06), Escape als
Gestenabbruch. Keine Wertung, Live-Fehlerhilfe oder Hypothesen. Endgültige Engine,
Sprache, Betriebssystemmatrix, Produktpersistenz und Veröffentlichungsdetails
bleiben offen. Der Entwicklungsablauf erteilt keine Produkt- oder Releasefreigabe.
Die offenen Designarbeiten #25/#28 und ihre Issues bleiben unentschieden.

## Pflichtquellen nach Auftrag

Immer [AGENTS.md](../AGENTS.md), [Workflow](dev-rules/WORKFLOW.md), dieses Profil
und den vollständigen aktuellen Issue-/Paketbody lesen; bei Review/Nacharbeit
zusätzlich PR, tatsächlichen Diff und den konkret benannten Reviewstand.
Bei Vorbereitung noch offener Implementierung/Nacharbeit zusätzlich die
[Modellauswahl](dev-rules/MODEL_SELECTION.md) und den
[Modellkatalog](dev-rules/MODEL_CATALOG.md) vollständig lesen.

| Arbeit | Zusätzlich vollständig lesen |
| --- | --- |
| Produkt, Regeln, Inhalte, Progression, UX/UI, Eingabe, Plattform oder Architektur | [Produktdefinition](PRODUCT_DEFINITION.md) |
| Thematik, Album, Motiventhüllung, UX/UI oder Eingabe/Wertung | [Gestaltungskonzept](DESIGN_CONCEPT.md) |
| Spieltechnik und P1-Verträge | [P1](PROTOTYPE_P1.md), [Issue #5](https://github.com/venomenon328/picross/issues/5) samt Entscheidungen, [Preflight](P1_PREFLIGHT.md), [Spielanleitung](../game/README.md) |
| Zellgesten, Cursorzähler oder deren Raster-/Fenstergrenzen | [ZR-Vertrag](CELL_DRAG.md), aktuelles [Paket #143](https://github.com/venomenon328/picross/issues/143), [Hinweisfont](CLUE_TYPOGRAPHY.md) |
| Zeichensprache, statische Vorschau, Zellanimationen | [UI_DRAWING_STYLE](UI_DRAWING_STYLE.md), betroffene ZS-Verträge/-Nachweise |
| UI-Schrift, kleine Rahmen, Dropdowns und Piktogramme | [HZ](HAND_DRAWN_UI.md), [Zeichensprache](UI_DRAWING_STYLE.md), [Z2-Ressourcenweg](Z2_SELECTION.md); bei Katalog-/Hinweisbezug zusätzlich die dort gerouteten Fachverträge |
| Spriteherstellung, Zellrendering, Cache/Invalidierung, PERF-01 | [CELL_RENDERING](CELL_RENDERING.md), [PERF-A](PERF_A_IMPLEMENTATION.md), [PERF-B](PERF_B_IMPLEMENTATION.md) |
| Sidebar/Zoomnormalisierung | [SL65](SL65_IMPLEMENTATION.md), aktuelle P1-/Saveverträge |
| Neue Rätsel konzipieren, gestalten, produzieren oder redaktionell abnehmen | [KI-Arbeitsanweisung zur Rätselproduktion](ai-workflows/PUZZLE_AUTHORING.md) und deren Pflichtquellen |
| Produktion, Import, Reparatur, Assets, Proofs | [PUZZLE_PRODUCTION](PUZZLE_PRODUCTION.md), [Werkzeuganleitung](../tools/puzzle_production/README.md), betroffene versionierte Manifeste und Paketnachweise |
| Schwierigkeitsanalyse, Kalibrierung, Bewertungsdaten oder deren Katalog-/Integrationsweg | [SD2-Sollvertrag](PUZZLE_DIFFICULTY_V2.md), [SD-Fachvertrag](PUZZLE_DIFFICULTY.md), [SD-A](SD_ANALYZER.md), [SD-B](SD_CALIBRATION.md), [SD-C1](SD_CATALOG.md), [Rätselproduktion](PUZZLE_PRODUCTION.md), [Paarlinienvertrag](PAIRED_LINES.md), [Kategorien](CATEGORIES.md), [ZA-1](ZA1_ADAPTER.md), [Katalogdarstellung](CATALOG_PRESENTATION.md), [CI-Policy](CI_POLICY.md) |
| CI, Prüfprogramme, Artefakte, Archivierung, Bestandsbereinigung oder neue Tests | [CI2-Sollvertrag](CI_SLIMMING.md), [CI-Policy und ausführbare Ausgangsbasis](CI_POLICY.md), [Bestandsinventar](DEVELOPMENT_ARCHIVE.md); bei Browserarbeit zusätzlich [Webvertrag](WEB_HOSTING.md), bei nativer Arbeit die betroffenen [KAT-2](KAT2_VERIFICATION.md)-, [EA](EA_VERIFICATION.md)- und [ZA-1](ZA1_VERIFICATION.md)-Verträge |

PERF-A/PERF-B sind historische Lieferberichte, keine aktuellen Hersteller- oder
A/B-Vergleichsgates. #70/N70-HIST-01 entfernt deren Reproduktion; die sechs
aktiven Zellatlanten, Import-/Shader-/Rendererverträge und native PERF-B-/PCK-
Prüfungen bleiben unabhängig über `tools/cell_atlas_reference.json` gebunden.

Historische Nachweise führen ihren damaligen Test-/Abnahmestand. Aktuelle
Fachentscheidungen stehen in den verlinkten Verträgen; CI2 und CI-Policy ersetzen
die dort ausdrücklich benannten älteren Auswahl-/Vollumfangs-/Budgetpflichten.
Bei konkreter historischer Nacharbeit zusätzlich sämtliche dort gebundenen
Quellen und damaligen Issues lesen; Erinnerungen ersetzen keinen Quellenzugriff.

## Aktuelle Spielverträge

Für die normalen UI-Schriftrollen und kleinen Bedienelemente ist
[HZ](HAND_DRAWN_UI.md) der maßgebliche Vertrag: HZ-A/B und der Typografieschritt
HZ-C gemäß HZ-D07 sind integriert. Tidy Hand bleibt
Standardtext; Überschriften einschließlich Vollhinweis sowie Zahlen-/Slot-/Fitvertrag
bleiben gemäß Eigentümerentscheidung HZ-A-FONT02 unverändert.

[HC / #92](CLUE_TYPOGRAPHY.md) bindet Delight Coffee für Hinweisziffern samt
gemeinsamer gemessener Schrift-/Slot-/Fit-/Draggeometrie und Exportnachweis.
Bei Hinweisarbeit zusätzlich diesen Vertrag lesen. Originalhinweise und
HC-E01-Quellenentscheidung werden mitgeliefert; HC-M01 und unabhängiges Review
bleiben vor Merge offen. Historische Chalkboard-/24/18-Maße sind abgelöst.

P1 bleibt der Vertragsname. Vollsicht und Hinweise sind nach VS2 integriert:
Sammlungsstart, Rasteransicht/Gesamtansicht, passives proportionales Miniaturbild,
Linksdrag ausschließlich für eine konkrete überlaufende Hinweisfolge gemäß
[HN](CLUE_INTERACTION.md), MMB ohne Hinweisnavigation, keine Hand- oder
Raster-/Miniaturverschiebung. Raster samt Außenrahmen bleibt innerhalb der
angebotenen Fitgrenze sichtbar. Die sechs Sidebaraktionen stehen in 2×3 mit
gezeichneten Rahmen; UI 100/125 % und Rückweg bleiben erreichbar.

Schema 1 und Appname `picross · P1` bleiben erhalten. Saves liegen unter
`user://p1/saves/`. Vollständige Validierung geht der Normalisierung alter
Ansichtswerte voraus; `overview=false`, gültiger Zoomwunsch, Inhalte, History/Redo
und Recoverygrenzen bleiben gemäß SL65/P1 erhalten. Keine Tests an echten Saves.

Startzustandsschutz und Hinweiszustände nach GP48, statische 56-%-Vorschau,
gerichteter Strichaufbau und Gegentasten-Abbruch nach ZS2 bleiben aktiv.
Spielaktion, History, Save und Abschluss werden durch Animation nicht verzögert.
Chalkboard-/Bakso-Nutzungshinweise und OFL-Texte sind mitzuliefern; keine
unbegründeten Lizenzannahmen. Details stehen in den Fachverträgen, keine neue
Abnahme wird aus alten grünen Läufen oder Standbildern abgeleitet.

## Befugnisse und Abnahme

Zielbranch `main`, reguläre Arbeit auf dem beauftragten Branch; Standardmerge
Squash nur mit passender ausdrücklicher/bedingter Freigabe. #70 beauftragt
Commit, Push und Draft-PR, keinen Merge. Kein Force-Push, Branchlöschen, Release,
Tag, Hosting, Branchschutz-/Secretwechsel oder kostenpflichtiger Dienst.
Technischer Branchschutz ist nicht als wirksam verifiziert; keine Schutzregeln umgehen.

`docs` und `ci-required` sowie alle ausgewählten Fach-/Produkt-/Toolchainjobs
müssen für den finalen Head/zugehörigen Test-Merge tatsächlich erfolgreich sein.
Head, Basis, Checkout und Run auseinanderhalten. Fehlend, abgebrochen oder
übersprungen ist bei Pflichtjobs kein Pass. Vollständiger Diff und getrennter
Selbstreview sind erforderlich; eigener Selbstreview ist keine unabhängige Zweitprüfung.
Persönliche Abnahme, technische Prüfung, Mergefreigabe und Release sind getrennt.
Die abgeschlossene Produktionsphase #34 wird nicht erneut geöffnet; offene
persönliche Befunde aus #24 werden durch Cleanup nicht abgenommen.

## Dokumentprüfung und Umgebungen

Python 3.11+, Standardbibliothek für den schnellen Pfad. Kleine lokale Prüfungen
in geeigneter vorhandener Umgebung sind erlaubt; aktuelle CI darf die
Abschlussprüfung liefern. Keine ritualisierte doppelte Vollprüfung.
Unbekannte Ressourcen-/Konfigurationsgrenzen prüfen; globale Workstation-
Einstellungen sind nicht als geprüft bestätigt.

```sh
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/check_docs.py
```

Der [Dokumentvalidator](../tools/check_docs.py) prüft Pflichtdateien, UTF-8/LF,
Abschlusszeile, Whitespace, Versionsformat und einfache lokale Inline-Links.
Externe URLs, Anker, Referenzlinks und vollständige Markdownsyntax sind nicht
abgedeckt. Die [Regelkopie](DEV_RULES_ADOPTION.md) bei deren Aktualisierung separat
gegen den Quellcommit prüfen; keine ungefragte zentrale Regeländerung.

## Produktionswerkzeuge

Eigenes headless Werkzeug unter `tools/puzzle_production/`, Python 3.11+;
Bildbefehle nutzen Pillow exakt 12.3.0. Fachtests unter `tests/puzzle_production/`
verwenden feste synthetische Inputs für Solver, unabhängigen Verifier, Import,
Reparatur, Export, Registrierung und abgeschlossene Integrationsbindungen.
Der Spieler benötigt weder Python noch Produktionspakete. Aktuelle Befehle und
Formate stehen in der [Werkzeuganleitung](../tools/puzzle_production/README.md)
und [ZA-1](ZA1_ADAPTER.md). CI-Auswahl und Nachweise regeln CI2 und CI-Policy.

```sh
python3 -m unittest discover -s tests/puzzle_production -p 'test_*.py' -v
python3 -m tools.puzzle_production.benchmark --output-dir artifacts/puzzle-production
```

Abgeschlossene RP1–RP6-Korpusproduktionen, Codec-/Reparaturstudien und damalige
Abnahmen sind [historische Quellen](DEVELOPMENT_ARCHIVE.md). Sie sind keine
aktuellen Start-, Replay- oder CI-Pflichten. Allgemeine Code- und Sicherheits-
regressionen bleiben aktiv; CI2-B grenzt die freigegebene Verschlankung und
Stilllegung historischer Hilfsfunktionen nach aktuellem Leserabgleich ab.

## Toolchain, Product und Betriebswirkung

[Preflight](P1_PREFLIGHT.md) bindet offizielle Editor-/Exportarchive mit
vollständigen SHA-256-Hashes. Keine globale Engineinstallation, keine gecachten
Prüfergebnisse. Bei Preflightänderungen echten Download-/Import-/Test-/Start-/
Exportweg nachweisen. Der [Product-Harness](../tools/p1_product.py) kopiert `game/`
in ein temporäres Projekt und isoliert APPDATA/LOCALAPPDATA beziehungsweise XDG.
Tests erhalten zusätzliche temporäre Speicherroots. Native Windows-Prüfungen
sind erlaubt. Linux-Renderprüfung benötigt Xvfb/Mesa, Bildprüfung eine eigene
Pillow-12.3.0-venv. Grenzen, Auswahl und Aufbewahrung stehen in der CI-Policy.

```powershell
$gameCache = Join-Path $env:TEMP 'picross-p1-preflight-cache'
python tools/p1_product.py --cache-dir $gameCache --output-dir artifacts/p1-product
```

Am ausführbaren Ausgangsstand ist lokal die Vereinigung aller sieben nativen
Gruppen aktiv; CI übergibt `--groups` mit ihrer exakten Auswahl.
Der [Gruppenvertrag](CI_C_NATIVE_GROUPS.md) beschreibt diese Auswahl.
CI2-D ersetzt die bisherige 500er-Route auch in `history`, `runtime`, `all`,
`--integration` und gewöhnlichen manuellen Vollumfängen durch den kurzen
20/6/2-Vertrag. Diese Dokumentlieferung führt keinen neuen CLI-Schalter ein.
Der allgemeine Harness verwendet sechs feste synthetische Muster T-01/T-02/T-04/
T-06/T-08/T-09, unabhängig vom Produktionsbestand. Der weiterhin `--pilots` genannte
Bereich prüft vier dieser technischen Fälle; echte Rätsel werden nicht replayt.
Spielerexport und tatsächlicher PCK-Inhalt sind zusätzlich zu Tests zu kontrollieren.
Laufzeiten und Artefaktgrößen werden gemessen; die Laufzeitziele und
Abbruchgrenzen richten sich nach CI2 §6. Der frühere allgemeine Verzicht auf
Laufzeitbudgets ist abgelöst, Zielerreichung erst nach tatsächlichem Lauf belegt.
Historische Studien-/Vergleichspakete entstehen im Standardpfad nicht neu.
Notwendige Referenzen, Quellen, Lizenzen und Prüfinputs bleiben erhalten.

Keine Laufzeitdienste eingerichtet. Nur isolierte temporäre Prüfdaten, keine
echten Spielstände, privaten Daten oder Secrets. Öffentliche gebundene
Godot-Archive dürfen geladen werden. Neue Assets/Abhängigkeiten auf Notwendigkeit
und Nutzungsrechte prüfen. CI arbeitet mit lesenden Repositoryrechten.
[ChatGPT-Projekteinstellungen](CHATGPT_PROJECT_INSTRUCTIONS.md) setzt der Nutzer
separat ein. Frühere Paketchronologie ist im
[gebundenen Profil vor Cleanup](https://github.com/venomenon328/picross/blob/0f89f08729539bbb4a02a590cbd18e58fbbda305/docs/PROJECT_PROFILE.md) erreichbar.
