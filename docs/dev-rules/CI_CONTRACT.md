# CI-Vertrag für Entwicklungsprojekte

## Kern und Module

Der Projektkern besteht nur aus allgemein erforderlicher Quellen-/Planintegrität, dem vereinbarten lieferbaren Produkt und einem ehrlichen Ergebnisgate. Projektprofil und ausführbare Moduldefinition benennen den Kern. Kein Anspruch auf Unveränderlichkeit: Auch Kernprüfungen dürfen nach Nutzen, Kosten und Risiko neu zugeschnitten werden.

Zusatzmodule werden je Issue/Paket bewusst gewählt. Der Plan wird mit der Umsetzung versioniert, ist im PR prüfbar und bindet den vollständigen Änderungsumfang. Ein aus einem abgeschlossenen Paket geerbter Plan darf nicht still weitergelten. Fehlender/ungültiger Plan ist ein Planfehler, kein Auftrag zum unbegrenzten Volltest. Gemeinsame Änderungen verlangen eine begründete Auswahl, nicht automatisch sämtliche Module.

Das Projekt darf eine geänderte Datei einem Prüfmodul vorschlagen; über dauerhafte Standardlast entscheidet ein dokumentierter Prüfvertrag. Ausgewählte Module laufen vollständig nach ihrem aktuellen Vertrag; nicht gewählte werden als nicht angefordert ausgewiesen. Ein erfolgreiches leeres Modul oder fehlende erwartete Ergebnisse sind kein Pass.

## Lebenszyklus statt immer größerer Dauersuite

Vor einer neuen Prüfung klären: Welchen Fehler findet sie? Auf welcher günstigsten Ebene? Was deckt vorhandene Prüfung bereits ab? Welche dauerhaften Kosten entstehen? Muss sie im Kern, nur bei passender Änderung, manuell oder einmalig zur Einführung laufen?

Keine Testfamilie, historische Zahl, Bildpflicht oder bisherige einzigartige Assertion ist pauschal geschützt. Eine Produktgarantie wie sichere Speicherung bleibt ein Produktvertrag; daraus folgt keine ewige Verpflichtung auf eine bestimmte Testkette. Bewusste Abdeckungslücken, Schadenspotenzial und vorhandene Alternativen knapp dokumentieren. Keine Pflicht zu einem gleich teuren 1:1-Ersatzorakel.

Temporäre Featureprüfungen enden spätestens an ihrem benannten Abschluss-/Reviewpunkt oder Datum. Bei Abschluss entscheiden: entfernen, günstiger ersetzen, nur bedarfsabhängig anbieten oder als konkret begründete kleine Dauerregression übernehmen. Neue schwere Kernlast muss im Paket ausdrücklich begründet und im Review bestätigt werden; kein separater Genehmigungsritus für jede kleine Änderung und keine erfundenen Mengenlimits.

## Artefakte

Das Profil definiert das verpflichtende ausführbare Produkt, nötige Laufzeitdateien/Lizenzen und ausdrücklich buildfreie Änderungsklassen. Reine Dokumentenänderungen und reine Inhaltsproduktion benötigen standardmäßig keinen Player-Build; gemischte Entwicklungsänderungen fallen nicht unter diese Ausnahme. Produkt und Laufzeitdateien gehören bei einem Build in einen klaren Download. Technische Reports, Prüfprofile, Exporte und Bildfolgen gehören nicht in das Spieler-/Nutzerpaket.

Technische Daten entstehen nur für einen aktuellen Prüfer oder benannten Review-/Diagnosezweck. Interne Originale möglichst im erzeugenden Lauf unabhängig prüfen und danach entfernen. Ein Joblog oder kompakter Ergebnistext ist kein Grund, ein zweites technisches Downloadpaket zu erzeugen. Uploads haben Zweck, Empfänger und Ablauf; Standard ist kein technischer Upload.

Screenshots und Videos dürfen temporäre aktuelle Prüfinputs/Reviewbelege sein. Dauerhafte Bild-/Videoreferenzen nur für eine tatsächlich verwendete Regression, höchstens der letzte abgenommene Stand pro Referenz. Kein wachsendes Galeriearchiv, keine regelmäßige Neuproduktion für historische Abnahmen und keine automatischen Filme. Referenzwechsel werden inhaltlich geprüft; fehlerhafte Ausgaben nicht selbst zur neuen Wahrheit erklären.

Keine feste maximale Artefaktgröße. Umfang minimieren durch Weglassen unnötiger Produktion, Daten und Doppelverpackung, nicht durch Abschneiden erforderlicher Logs/Originale. Ablauf früherer CI-Artefakte nicht als fortbestehende Verfügbarkeit behaupten. Kompakte Entscheidungen und Quellverweise bleiben in Git/PR; sie garantieren nicht den Erhalt alter Binärbelege.

### Zustellung an einen unabhängigen Reviewer

Schon im Prüfplan festlegen, welche Originale für welches Szenario erforderlich
sind, wer sie öffnen können muss und bis wann. Der Implementierer stellt genau
diese Dateien vor dem Review bereit. Bei einer Layoutprüfung können das etwa
die benannten Original-PNGs und eine kleine Zuordnung von Auflösung und UI-Skala
zum geprüften Produkt-Head sein.

- **Eigener temporärer Reviewbranch.** Einen separaten Ref, etwa
  `review/<issue>-<paket>`, vom geprüften Produkt-Head abzweigen und die Belege nur
  dort committen und pushen. Der Produkt-PR behält seinen Head. Er erhält Links
  auf die Dateien am konkreten Belegcommit. Der Belegbranch hat keinen Merge-PR
  nach main und wird weder in den Produktbranch gemergt noch dorthin übernommen.
- **Befristetes CI-Artefakt.** Wenn der Lauf die geforderten Originale erzeugt,
  ausschließlich die im Paket benannten Dateien samt notwendiger Zuordnung
  bereitstellen. Im PR den direkten Artefaktlink mit Lauf/Versuch und Ablauf
  nennen. Liefert der verfügbare Uploader weitere, für diesen Review irrelevante
  Daten oder fehlen die lokalen Originale im Lauf, den separaten Reviewbranch
  verwenden.

Im Lieferkommentar den geprüften Produkt-Head und gegebenenfalls Test-Merge,
Szenarien/Dateinamen, Empfänger und Endpunkt festhalten. Zugriff auf die
veröffentlichten Bytes testen. Wer im eigenen Konto prüft, benennt eine bekannte
Zugriffsbeschränkung für den Empfänger. Die Sichtprüfung selbst bleibt Aufgabe
des Reviewers. Ein lokaler Pfad, eine Hashliste oder ein erfolgreich gebauter
Spieler allein liefert ihm keine Bilder. Fehlende, abgelaufene oder zum neuen
Head unpassende Originale gezielt nachliefern, das erforderliche Gate bis dahin
offen führen.

Bereinigungszeitpunkt und Zuständigkeit im PR festhalten. Eigene Belege bis
zur erforderlichen Prüfung verfügbar halten. Bei Fristablauf und weiter offenem
Gate den Bedarf und die Zustellung erneut prüfen. Den eigenen temporären Ref im
beauftragten Rückbau entfernen bzw. das CI-Artefakt auslaufen lassen. Vor Merge
prüfen, dass der Produktdiff und seine zu integrierenden Commits frei von reinen
Übergabedateien sind. Im PR bleibt die knappe Entscheidung mit ihrem Stand.

## Zeit und Ergebnis

Das Profil setzt ein weiches Laufzeitziel. Überschreitung erzeugt Messung, Warnung und gegebenenfalls Optimierungsbedarf, keinen Fehlerstatus und keinen verpflichtenden Maximalwert. Keine pauschale Artefaktgrößen- oder CI-Laufzeitobergrenze. Prozess-Hängerschutz, Plattformgrenzen und funktionale Zeitverträge sind gesonderte technische Grenzen; ihre Werte begründen und nicht als Leistungsziel ausgeben.

Gemessene Laufzeit, Wartezeit, Parallelität, erzeugte und hochgeladene Bytes unterscheiden. Nur tatsächliche Messungen als Wirkung behaupten. Erfolgreich, nicht angefordert, fehlend, abgebrochen und fehlgeschlagen bleiben unterscheidbar. Quelle, Basis, Test-Merge und Run/Versuch binden die Aussage. Standard-Main-Nachlauf wiederholt keine gesamte Featureprüfung.

