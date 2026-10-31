# Aktiver Bestand und historische Quellen

**Buchstudie B-A-N01 / #493:** `game/study/book/` erhält den ausführbaren isolierten
Untersuchungsstand, zwei eigene Materialshader und kompakte synthetische Inputs
samt deterministischer Erzeugung und studieneigener Doppelseitenanordnung.
Das bestehende A-Bild bleibt unveränderte Materialquelle.
[B-A-N01-T01](BOOK_STUDY.md) und Startanleitung binden
Zweck, Rechte und Nachweise. Filme, Laufbilder und Exporte bleiben temporär; der
reguläre Export schließt die Studie aus. Keine historischen Bildressourcen ersetzen.

Eigentümerentscheidung 14.10.2026, [#116](https://github.com/venomenon328/picross/issues/116):
Abgeschlossene Produktion muss nicht wiederholbar sein. Historische Arbeitsdateien
gehören nicht dauerhaft in den aktiven Tree, Builds oder neue CI-Artefakte.

## Aktuell benötigt

RI-A / #478 ergänzt genau einen operativen Diagnose-/Budgetbaustein,
ein festes synthetisches Testmodul und den manuell gestarteten begrenzten
T01-Messtreiber; keine echten Kataloginputs oder gespeicherten Testkopien.
[RI-A-T01](RI_A_VERIFICATION.md) hält den kompakten Liefernachweis.
Messarbeitsbäume und rohe lokale Berichte bleiben außerhalb des Repositorys
für den laufenden Review, anschließend gelten die CI2-Abschlussregeln.
Es entsteht kein dauerhafter Benchmarkjob und kein neues Replaykorpus.

- `game/`: tatsächliche Spielressourcen und Nutzungsrechte; feste technische Testinputs
  liegen getrennt unter Tests/Studien und sind aus dem Export ausgeschlossen.
- `content/authoring/`: ausschließlich laufende Arbeit. Ein Draft mit `registered`
  ist noch keine finale Main-Integration.
- `content/packages/`: bis zum Abschluss vollständiger Export, danach nur kompakte
  Integrationsbindung gemäß [ZA-1](ZA1_ADAPTER.md). Runtime bleibt bytegleich.
- Allgemeine Produktionswerkzeuge und feste synthetische Tests. Historische Namen
  bedeuten nicht automatisch historische Funktion. Bestehenden Prüfumfang nur nach
  Eigentümerentscheidung ändern.
- Aktive Buch-/Font-/Atlasquellen, Rechte und die noch von Tests gelesenen Layoutinputs.
  Offene Designarbeit und die geschützte Eigentümerreferenz gemäß CI-Policy bleiben.

### Freigegebener SD-Sollstand

[Rätselschwierigkeit](PUZZLE_DIFFICULTY.md), Ursprung
[#235](https://github.com/venomenon328/picross/issues/235), ergänzt nach SD-C die
dauerhaften Daten um kompakte aktive Bewertungen, Eingangsbindungen und den
gebundenen Methoden-/Referenzstand außerhalb versiegelter Produktionsoriginale.
Manuelle Neubewertung nutzt erhaltene Runtime-Logikeingänge; sie benötigt keine
Wiederherstellung von Quellen, Proofs oder ZIPs und begründet keine allgemeine
Produktions-Replaypflicht. SD-C1 hat die Ablage mit PR #242 nach qualifiziertem
R2 integriert. Die [SD-C2-Übernahme](SD_CATALOG.md) hat nach bestandenem
Vor-Übernahme-Review 26 aktive Bestands-Sidecars und zwei kompakte Dauerberichte
angelegt und ist über [PR #243](https://github.com/venomenon328/picross/pull/243)
auf `main` integriert. Frühere offene Review-/Mergeangaben beschreiben den
damaligen Lieferstand; sie begründen keine neue Aufbewahrungs- oder Replaypflicht.
Referenzen werden unabhängig synthetisch kuratiert; reale Katalogrätsel oder
deren Kopien werden weder Kalibrierungskorpus noch automatischer Testbestand.

### Freigegebene CI-Straffung

Die neue Eigentümerentscheidung vom 26.10.2026 in
[CI2: CI und Repository verschlanken](CI_SLIMMING.md) /
[#412](https://github.com/venomenon328/picross/issues/412) löst die folgenden
früheren Vollinventarpflichten und den Verzicht auf feste Laufzeit-/Volumengrenzen
gezielt ab. Sie ist eine Spezifikationsfreigabe; die ausführbaren Checks werden
erst durch die getrennten Umsetzungspakete geändert. Historische Prüfergebnisse
behalten ihre damalige Bindung und werden nicht umgeschrieben.

Die Entscheidung vom 18.10.2026 in [CI-Policy](CI_POLICY.md) /
[#246](https://github.com/venomenon328/picross/issues/246) erlaubt gezielte Auswahl
und schnellere Herstellung aktueller Nachweise in den gestuften Paketen CI-A,
CI-B und [CI-C (#249)](https://github.com/venomenon328/picross/issues/249).
Sie erklärt keine aktiven Tests allein wegen ihres historischen Namens für
entbehrlich. Bis zur Integration des jeweiligen Pakets bleiben die ausführbaren
Pflichtchecks maßgeblich.

[CI-B](CI_B_BROWSER_GROUPS.md) hält das bisherige Browserinventar,
Gruppenvoraussetzungen und Belegbindungen fest. Die serielle
instrumentierte Baseline bleibt an ihren PR-Commit/Run gebunden; sie ist kein
neuer dauerhaft zu wiederholender Testpfad. Aktuelle Builddateien dürfen
innerhalb desselben gebundenen Runs geteilt werden, Prüfergebnisse nicht.

[CI-C](CI_C_NATIVE_GROUPS.md) ordnet die bisherigen nativen Checks und Pflichtartefakte
unabhängig auswählbaren Gruppen zu. Das gebundene Inventar enthält technische
Dateinamen und Ergebnisfelder, keine Kopie historischer Bild-/Rätseldaten.
Die frühere Pflicht zur vollständigen Bildmenge und der frühere Verzicht auf
Zeit-/Bytegrenzen gelten nicht als Vorgabe für CI2. Dessen gekürzter Sollumfang
und Budgets sind maßgeblich; bestehende erfolgreiche Nachweise werden dadurch
weder nachträglich erweitert noch abgewertet. Keine historische Replaypflicht.
Quellgebundene Referenzläufe und konkrete Vergleichsmessungen stehen in Issues/PRs;
dieses Inventar sammelt keine neue Laufchronik.

## Freigegebene Folgebereinigung vom 26.10.2026

Der folgende [CI2-E-Umfang / #417](https://github.com/venomenon328/picross/issues/417)
ist auf `chore/417-ci2-e-cleanup` bereinigt; [CI2-E-T01](CI2_E_VERIFICATION.md)
weist aktuelle Zahlen, Leserprüfung und erhaltene Quellen nach. Unabhängiges
CI2-E-R01 bleibt vor Merge offen. Die folgende historische Ausgangsmessung gehört zu
[`main@967314538df376a281020fb4c34f93f370a491df`](https://github.com/venomenon328/picross/tree/967314538df376a281020fb4c34f93f370a491df).
Die Zahlen summieren Datei-Bytes des aktiven Trees, nicht die Größe der Git-Historie.

| Abgeschlossene Arbeits-/Nachweisdaten | Dateien | MiB |
| --- | ---: | ---: |
| `content/authoring/*/at-b-r01/` | 755 | 258,067 |
| `docs/design/at_b_integration/` | 145 | 224,541 |
| `docs/evidence/hz-c/` | 60 | 115,948 |
| `docs/evidence/hz-b/` | 44 | 114,109 |
| `docs/evidence/hz-a/` | 7 | 59,642 |
| `docs/evidence/at-a/` | 145 | 25,960 |
| **Kandidatenumfang** | **1.156** | **798,267** |

Die sechs Klassen enthielten zusammen 837.043.724 Bytes. Vor der Entfernung wurden
tatsächliche Main-Integration, aktuelle Leser, offene Nacharbeit derselben IDs
und Rechtebindungen geprüft. Verbleibende Dokumentlinks erhalten gebundene
historische Commit-/PR-Verweise. Kompakte aktive Verträge und nötige Abschlussverweise
bleiben; keine Kopie in einem neuen Archiv, Spielerbuild oder CI-Artefakt.
Die nachträglichen AT-B-Bildrevisionen schließen nach
[Authoring §9](ai-workflows/PUZZLE_AUTHORING.md#9-produktionsabschluss-und-bereinigung)
auch dann ab, wenn die ursprüngliche Rasterproduktion bereits einen kompakten
Integrationsdatensatz hat. Bestehende versiegelte Integrationsbelege bleiben erhalten.

Erhalten bleiben aktive Runtime-, Reveal-, Rechte-, Registry- und Schwierigkeitsdaten,
synthetische Fachinputs sowie tatsächlich gelesene technische Ressourcen. Dazu gehören
`docs/evidence/kk/native-crops.json`, aktive Buch-/Font-/Atlasquellen und benötigte
Layoutinputs. Offene Senf-/Level-1-1-Arbeit, Pentagramm und offene Designarbeit gehören
nicht zu diesem Umfang. Ein historischer Pfadname oder eine Dateiendung genügt
nicht als Löschgrund.

Abnahme: ausgewiesener Tree-Rückgang von ungefähr 798 MiB, bereinigte Authoringindizes,
unveränderte aktive Inhalte und erhaltene Rechte; nötige Restdaten und andere
Abweichungen vom Kandidatenumfang werden konkret begründet. Die Git-Historie bleibt
unangetastet. CI2-E führt keinen Merge aus und erweitert keine frühere Mergefreigabe
auf CI2-Codepakete.

Der nach CI2 vorgesehene schnelle Check überwacht Pfade, Datei-/Bytezuwachs und
unzulässige Ablageklassen aus verfügbaren Metadaten. Er lädt keine historischen
Nutzdaten zum Messen nach und startet keine Produktion, Engine oder Browserprüfung.
Kein zusätzlicher CI-Job, Archivkatalog oder laufender Lieferbericht. Aktuelle
Autorität sind Fachverträge und neue Entscheidungen; alte Lieferstatus und Urteile
bleiben an ihren damaligen Stand gebunden und werden nicht erneut Pflicht.

## Aus dem aktiven Tree entfernt

Quelle vor dieser Bereinigung: `37f500d5e6599a6c8ff85c8ca8edb4d190474c5f`.

| Bereich | Historische Quelle / verbleibender Zweck |
| --- | --- |
| Arbeitsstände der zehn auf main integrierten Workflow-Rätsel | [Authoring](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/content/authoring); Runtime-Definitionen, Abschlussbilder und Nutzungshinweise bleiben. |
| Vollständige Prüfkopien dieser Rätsel | [Pakete](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/content/packages); ersetzt durch kompakte Manifestbindung, keine neue Zertifizierung. |
| RP4-Vergleichsproduktion, RP5-Archiv/Versuche, RP6-Pilot, VS1-Produktion | [Beispiele](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/examples); aktuelle technische VS1-UI-Fälle unter `game/full_view_study/` bleiben. RP5-README bleibt als Reparaturformatvertrag. |
| RP3 gespeicherte Ergebnisse/Exporte | Quelle, Design und Reveal bleiben als kleines ausführbares Importbeispiel; alte Ergebnisdateien entfallen. |
| RP3–RP6-Lieferberichte, alte F01/F02-Proofberichte und früheres Archivmanifest | Über den gebundenen Vorgänger erreichbar; aktuelle technische Verträge bleiben. |
| Historische Korpus-/Review-/Ownerprogramme | [Werkzeuge](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/tools); keine RP6-Ownerhilfe mehr im Spielerpaket. CI2-B entfernt nach aktuellem Leserabgleich auch die exklusiven RP4-/RP5-Hilfen und ihre sechs Tests; RP6 und aktive Archiveingangsprüfung bleiben. |

Die freigegebene Folgearbeit entfernt außerdem die wirkungslose Ansichts-/Pan-
Galerie und die erzwungenen alten Raster-/Hinweis-Replays aus `capture.gd` sowie
den alten H1-Komponentenlauf. Ihre Quelle liegt im
[Stand vor der Testkürzung](https://github.com/venomenon328/picross/tree/2519695767c6fabf0b23970ab9ae17024de44bae/game/tests).
Die aktuellen Vollansichts-, Hinweis-, Eingabe-, Schrift- und Animationsverträge
bleiben gemäß CI-Policy geprüft; aktive gemeinsame Renderer werden nicht entfernt.

Die Git-Historie wird nicht umgeschrieben. Ein vollständiger Commit-/PR-Verweis
ersetzt neue riesige Archivmanifeste oder Kopien gelöschter Dateien. Bei Bedarf
historische Untersuchungen in einem getrennten Checkout durchführen; keine
Wiederherstellung als Voraussetzung zukünftiger Entwicklung.

Die früheren Bereinigungen (#63/#70/#114), Prüfzuordnungen und Einzelinventare
stehen im [gebundenen Vorgänger](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/docs/DEVELOPMENT_ARCHIVE.md).
Aktuelle Messwerte und der geprüfte Diff stehen in dem zu #116 gehörenden PR; sie werden
nicht als dauerhaft wachsender Lieferbericht in diesem Dokument gesammelt.
