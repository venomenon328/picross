# Aktiver Bestand und historische Quellen

**P2-F-A-V01-P01 / #502:** Der [native RP6-Vertrag](CI_C_NATIVE_GROUPS.md)
entfernt zwei Captureprozesse und 30 Darstellungszustände aus der Dauer-CI.
Zwei Original-JSONs und zwei Prozesslogs entfallen; keine Erfolgs-PNGs oder
Produktdateien betroffen. Drei kleine Python-Gegenproben und die erweiterten
verbleibenden Originalberichte sind in `tools/ci_lifecycle.json` gebunden.
Die frühere Matrix bleibt über `4a65157063a71ca8f3239fd04994dc6a5e90598c`
erreichbar. Eigene lokale Arbeitsdaten: `artifacts/502-p2f-local/`, Reviewfrist
19.11.2026 beziehungsweise P2-F-A-V01-R01; keine automatische Löschung.
T01 bilanziert tatsächliche Kosten und Restbestand. Geschützte/fremde Daten
bleiben unberührt; technische CI-Belege sieben, Player vierzehn Tage.

**P2-E-B-V01 / #502:** Der [Grafikvertrag](CI_C_NATIVE_GROUPS.md) reduziert mit
D02-Abdeckungserlaubnis die native VS2-Matrix von 96 auf 18 und die fünf kompakten
Renderstufen von 158 auf 66 Frames. Alle bisherigen Originalberichtspfade bleiben;
keine neuen Dateien oder Erfolgs-PNGs. Zwei kleine Python-Negativtests und der
unabhängige Leser sind in `tools/ci_lifecycle.json` gebunden. Die volle frühere
Auswahl bleibt an `d5d3a0c5c7ab1a0e79a4133e5ea47cd675cf02cf` historisch erreichbar.
Eigene lokale Diagnosen liegen unter `artifacts/502-p2eb-local/`, Reviewfrist
19.11.2026 beziehungsweise P2-E-B-V01-R01. T01 bilanziert den Restbestand;
keine automatische Löschung, kein Zugriff auf geschützte/fremde Arbeitsdaten.
Technik sieben Tage, Player vierzehn Tage; unabhängiges R01 und Mergefreigabe offen.

**P2-E-A-V02 / #502:** Die KE-/KK-Dauermatrix wird gemäß
[D02](https://github.com/venomenon328/picross/issues/502#issuecomment-6655391391)
mit bewusstem Abdeckungsverlust verkleinert; das [aktive Inventar](CI_C_NATIVE_GROUPS.md)
nennt jeden verbleibenden Fall und gestrichene Gegenbeispiele. Elf Prozesse,
Original-JSONs und bestehende Artefaktpfade bleiben. Neue kleine Python-Gateprüfungen
und Checkpoint-/Resize-Felder sind in `tools/ci_lifecycle.json` deklariert; keine
neuen PNGs, Filme, Archivfamilien oder Produktquellen. Frühere native Vollmatrizen
bleiben über `main@450b84feff0f43affe3f9dabd5bef94118f0411b` historisch erreichbar.
Eigene lokale Diagnose-/CI-Daten liegen ausschließlich unter
`artifacts/502-p2e-v02-local/`, Reviewfrist 19.11.2026 beziehungsweise V02-R01.
T01 nennt den Restumfang; keine automatische Löschung daraus ableiten.
Geschützte und fremde Alt-/Arbeitsdaten bleiben unberührt. Technikretention sieben,
Player vierzehn Tage; #502 und unabhängiges R01 bleiben offen.

**P2-C-V03 / #502:** [Audit aller 435 früheren PNG-Pflichten](P2_C_V03_AUDIT.md).
Die aktiven HZ-/KE-Vergleichsproducer, HC-Galerie samt Reader, separate V1-/Z2-
Captureproducer und KAT-Crop-Reader entfallen; frühere Quellen bleiben am
[Basiscommit](https://github.com/venomenon328/picross/tree/5471a42e6291d9eeda9b2a04811547d21b0430ff).
ZS2 ist ein kleiner eigenständiger aktueller Animationsproducer ohne Studienreplay;
die Pythonreader enthalten keine historischen ZS2-/VS2-Archiv-/Galeriepaketierer mehr.
Regulär verbleiben zehn minimale AT/HN-Rohpixeldateien; HS/ZS konsumieren und
löschen temporäre Originale. HIL-M01 und persönliche KU-/VS2-Abnahmen bleiben offen.
Kein neues Bildarchiv. Gesperrte V01/V02/HIL/P2-B-Arbeitsdaten wurden nicht angefasst.
Die eigenen V03-Diagnosen unter `artifacts/502-p2cv03-local/` sind lokale,
nicht versionierte Arbeitsdaten; Reviewfrist 18.11.2026 bzw. V03-R01, danach nur
im zulässigen Bereinigungsweg entfernen. T01 nennt ihren tatsächlichen Restumfang.


**B-B / #498:** `game/book/` enthält die gemeinsame Produktdarstellung samt drei
unveränderten Materialbildern und deren Import-/Herkunftsmetadaten. Der reguläre
Windows-/Webstart verwendet diese Quellen. P2-A / #502 entfernt
`game/study/book/` samt 27 Definitions-/Revealpaaren, Vollstudienprüfern und
Exportwegen; die historischen Quellen liegen am
[gebundenen Vorgänger](https://github.com/venomenon328/picross/tree/fc86d2a2eff543f5b0c4ff328a71e815e4bc43a7/game/study/book).
Aktive Reader sind `tools/book_lifecycle.py` für die kurze Hilfe-/Lifecycleprüfung
und `tools/book_windows_probe.py` mit dem externen Beobachter
`game/tests/book_windows_observer.gd` für ausdrücklich beauftragte Windowsdiagnosen.
Beide kopieren den bestehenden kleinen Testkatalog über `product_fixtures`.
B-B-M01/HIL-M01 und der wechselnde Windows-Tooltipbefund P1-R01-O01 bleiben offen;
kein Studienreplay oder neuer Desktopauftrag. Der [Belegvertrag](CI_C_NATIVE_GROUPS.md)
ordnet die erhaltenen aktuellen Produkt-/Tooltip-/Speicher-/PCK-Prüfungen zu.
`game/tests/book_fixture.gd` bindet bestehende Komponentenprüfungen an dieselbe
Produktwurzel, `book_integration.gd` prüft ihren unbeschleunigten Lebenszyklus.
`book-save-v1.json` ist ein einzelner eingefrorener synthetischer Schema-1-Beleg.
`tools/book_contract.py` bindet den begrenzten Runtime-/Prüfbestand; die beiden
neuen Dokumente [Vertrag](BOOK_INTEGRATION.md) und [T01](B_B_VERIFICATION.md)
enthalten aktive Integration beziehungsweise Liefernachweis. Temporäre Originale
und Exporte bleiben in begrenzten Prüfarbeitsdaten; keine neue Bildgalerie.
P1 / [#502](https://github.com/venomenon328/picross/issues/502) entfernt die
aktive Filmproduktion vollständig. Frühere Filme bleiben nur über den
gebundenen historischen Commit-/PR-Stand erreichbar; kein neuer Filmbeleg.

**Historische Herkunft B-A-N06 / #493, #496 (R08/M01 auf PR #497 abgeschlossen):**
Der damalige Bestand unter `game/study/book/` erhielt den ausführbaren isolierten
Untersuchungsstand, zwei eigene Materialshader und kompakte synthetische Inputs
samt deterministischer Erzeugung und studieneigener Doppelseitenanordnung.
Das bestehende A-Bild bleibt unveränderte Qualitätsreferenz. Eine originale
Papiertextur samt Import-/Herkunftsmetadaten und 27 eindeutige Definitions-/Revealpaare
ersetzen die fehlerhafte Wiederverwendung dreier Ressourcenpfade. Die Dateipaare waren der damalige reproduzierbare Studien-/PCK-Bestand;
P2-A entfernt sie nach dem Leserabgleich.
[B-A-N06-T01](BOOK_STUDY.md) und Startanleitung binden
Zweck, Rechte und Nachweise. Filme, Laufbilder und Exporte bleiben temporär; der
reguläre Export schließt die Studie aus. Keine historischen Bildressourcen ersetzen.
N03 ergänzt eine originale homogene Ledertextur mit Import-/Herkunftsmetadaten,
die gemeinsame Rand-/Rückengeometrie und einen aus exportierten Paketen ausgeschlossenen
nativen Tooltipprüfer. Keine neue dauerhafte Bildgalerie; N02-/N03-Vergleiche,
unskalierte Randdetails und Tooltipbilder bleiben befristete technische Belege.
N04 ergänzt genau eine originale Tischbildressource samt Import/Herkunft sowie
einen begrenzten nativen Prüfer für Halbseiten, Scrollkontext und 16:10. Der Prüfer
ist aus Studienpaketen ausgeschlossen, die gesamte Studie aus regulären Paketen.
Vorher-/Nachherbilder, Windowsbelege und Film bleiben in befristeten Artefakten;
keine zusätzliche dauerhafte Galerie oder Handoffdatei.
N05 ergänzt zwei studienlokale Bausteine für Informationslayout und
Ursprungs-/Bewegungszustände, einen aus Paketen ausgeschlossenen nativen Prüfer
und erweitert den vorhandenen unabhängigen Python-Ergebnisguard. Alle haben einen aktuellen Runtime-
beziehungsweise Ergebnisgatezweck. N05-Originalbilder, Windowsbelege und Film
bleiben befristete Prüfarbeitsdaten; keine neuen Bild-/Font-/Materialressourcen.
F01 ergänzt einen nativen GUI-Dispatchprüfer, einen rein lesenden Windows-
Beobachter und einen begrenzten Win32-Eingabetreiber. Beide GDScripts bleiben aus
Spielerpaketen ausgeschlossen. Nur die private Diagnosekopie erhält den Beobachter
als externes Autoload; EXE und PCK bleiben bytegleich. Crash-/WER-Originale,
OS-/Engine-Spuren und wenige Clientbilder bleiben bis zum offenen F01-Review in
einem kompakten temporären Prüfpaket; keine dauerhafte Laufchronik oder Galerie.
N06 ergänzt ein gemeinsames Shaderinclude für Falz-/Gelenkprofile und einen
aus Spielerpaketen ausgeschlossenen nativen Tiefen-/Geometrieprüfer. Der bestehende
Windows-Treiber erhält einen begrenzten Sichtweg; der Ergebnisguard prüft vier
Tiefenbilder, Gegenproben und Mengen. Keine neuen Bildressourcen. Vorher-/Nachher-
Originale bleiben bis R08/M01 begründete temporäre Belege; der kompakte Windows-
Sichtkandidat enthält keine Entwicklungsgalerie und keinen Film.

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
