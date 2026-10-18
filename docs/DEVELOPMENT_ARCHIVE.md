# Aktiver Bestand und historische Quellen

Eigentümerentscheidung 14.10.2026, [#116](https://github.com/venomenon328/picross/issues/116):
Abgeschlossene Produktion muss nicht wiederholbar sein. Historische Arbeitsdateien
gehören nicht dauerhaft in den aktiven Tree, Builds oder neue CI-Artefakte.

## Aktuell benötigt

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
angelegt. Die Originalarbeitsbundles bleiben bis zur Reviewfortsetzung außerhalb
des Repositorys erhalten; finales Datenreview und Merge bleiben offen.
Referenzen werden unabhängig synthetisch kuratiert; reale Katalogrätsel oder
deren Kopien werden weder Kalibrierungskorpus noch automatischer Testbestand.

### Freigegebene CI-Straffung

Die Entscheidung vom 18.10.2026 in [CI-Policy](CI_POLICY.md) /
[#246](https://github.com/venomenon328/picross/issues/246) erlaubt gezielte Auswahl
und schnellere Herstellung aktueller Nachweise in den gestuften Paketen CI-A,
CI-B und [CI-C (#249)](https://github.com/venomenon328/picross/issues/249).
Sie erklärt keine aktiven Tests allein wegen ihres historischen Namens für
entbehrlich. Bis zur Integration des jeweiligen Pakets bleiben die ausführbaren
Pflichtchecks maßgeblich.

CI-C ordnet aktuelle native Checks und Pflichtartefakte unabhängig auswählbaren
Gruppen zu. Bildaufbereitung wird gemessen und verlustfrei beschleunigt:
Dekodierte Pixel einschließlich Alpha, Maße, Ausschnitte und Pflichtbildmenge
bleiben erhalten; PNG-Datei-Bytes dürfen sich ändern. Keine feste Zeit-/Bytegrenze,
kein Weglassen angeforderter Belege und keine historische Replaypflicht.
Quellgebundene Referenzläufe und konkrete Vergleichsmessungen stehen in Issues/PRs;
dieses Inventar sammelt keine neue Laufchronik.

## Aus dem aktiven Tree entfernt

Quelle vor dieser Bereinigung: `37f500d5e6599a6c8ff85c8ca8edb4d190474c5f`.

| Bereich | Historische Quelle / verbleibender Zweck |
| --- | --- |
| Arbeitsstände der zehn auf main integrierten Workflow-Rätsel | [Authoring](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/content/authoring); Runtime-Definitionen, Abschlussbilder und Nutzungshinweise bleiben. |
| Vollständige Prüfkopien dieser Rätsel | [Pakete](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/content/packages); ersetzt durch kompakte Manifestbindung, keine neue Zertifizierung. |
| RP4-Vergleichsproduktion, RP5-Archiv/Versuche, RP6-Pilot, VS1-Produktion | [Beispiele](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/examples); aktuelle technische VS1-UI-Fälle unter `game/full_view_study/` bleiben. RP5-README bleibt als Reparaturformatvertrag. |
| RP3 gespeicherte Ergebnisse/Exporte | Quelle, Design und Reveal bleiben als kleines ausführbares Importbeispiel; alte Ergebnisdateien entfallen. |
| RP3–RP6-Lieferberichte, alte F01/F02-Proofberichte und früheres Archivmanifest | Über den gebundenen Vorgänger erreichbar; aktuelle technische Verträge bleiben. |
| Historische Korpus-/Review-/Ownerprogramme | [Werkzeuge](https://github.com/venomenon328/picross/blob/37f500d5e6599a6c8ff85c8ca8edb4d190474c5f/tools); keine RP6-Ownerhilfe mehr im Spielerpaket. RP4/RP5 behalten nur noch die vorhandenen getesteten Hilfsfunktionen. |

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
