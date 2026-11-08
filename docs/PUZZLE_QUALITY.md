# Redaktioneller Qualitätsvertrag für neue Rätsel

**Vertrag 1.0 · Dokumentrevision 1 · 08.11.2026 · Q-A / [#488](https://github.com/venomenon328/picross/issues/488)**

## 1. Geltung und Zuständigkeit

Diese Datei ist die verbindliche redaktionelle Qualitätsreferenz für neue
Produktionen nach [PUZZLE_AUTHORING](ai-workflows/PUZZLE_AUTHORING.md).
Sie bündelt die Anforderungen aus [Produktdefinition §3](PRODUCT_DEFINITION.md),
[Gestaltungskonzept §§2/4.3](DESIGN_CONCEPT.md) und
[Produktionsvertrag §§3/6/7](PUZZLE_PRODUCTION.md) sowie die
Eigentümerpräzisierung in #488. Der Authoringworkflow regelt Aufträge, Budgets,
Dateisicherung und tatsächliche Freigaben; die technischen Fachverträge regeln
ihre eigenen Invarianten. Deren Schemas und Grenzwerte werden hier nicht erneut
definiert. Bei Widersprüchen vor dem betroffenen Schritt die zuständige Quelle
klären, keine günstigere Regel auswählen.

Q-A führt weder automatische Farbberechnung noch Adapter-/Spieländerungen ein.
Die numerische Palettenprüfung bleibt das spätere Ergebnis von **P-A**, ihre
Werkzeugintegration einschließlich eines geprüften Ausnahmewegs **P-B**.
Es gibt heute keine beschlossene Delta-E-Grenze oder universelle Zusicherung
der Farbwahrnehmung. Die visuelle Beurteilung bleibt bereits jetzt Pflicht.
Abgenommene Bestandsrätsel, versiegelte Pakete, Freigaben, technische
Regelversionen und historische Bewertungen werden nicht rückwirkend umgedeutet.

## 2. Einzelurteile, Belege und Klassen

Für jedes an der jeweiligen Phase fällige Kriterium aus §3–4 MUSS ein
Einzelurteil mit kurzer Begründung und konkretem Beleg im vorhandenen
Qualitäts-/Entscheidungsprotokoll stehen. Es bindet Kriterien-ID, diese
Regelversion/Dokumentrevision beziehungsweise ihren Quellcommit und Dateihash,
Kandidaten-ID/Revision, betrachtete Dateien/Hashes, Methode, Zeitpunkt und Prüfer.
Bei Farbfragen die tatsächlich verwendeten Farb-IDs und RGB-Werte einschließlich
der betroffenen Paare nennen. Fehlende Bindungen ausdrücklich offenlassen.
Keine neue technische Pflichtdatei oder Erweiterung geschlossener Schemas.

| Ergebnis | Bedeutung und Folge |
| --- | --- |
| `erfüllt` | Die benannte Prüfung bestätigt das Kriterium am gebundenen Stand. Kein bloßes Erfolgsflag ohne Beleg. |
| `Warnung` | Ein konkreter Prüfanlass oder begrenzter Vorbehalt liegt vor; Befund, motivischer Nutzen und Entscheidung dokumentieren. Kein automatisches Ablehnen. |
| `nicht erfüllt` | Ein benannter Mangel besteht. Korrektur oder eine nach §6 zulässige ausdrückliche redaktionelle Einzelfallentscheidung ist nötig. |
| `nicht geprüft` | Prüfung fehlt, ist unvollständig oder für diese Phase noch nicht fällig; Grund und fälligen Zeitpunkt nennen. Kein positives Urteil aus fehlenden Daten. |

| Klassifikation | Verbindliche Bedeutung |
| --- | --- |
| `unabdingbare Voraussetzung` | Vor dem zugehörigen Freigabe-/Integrationsschritt vollständig nachzuweisen. Eine Qualitätsentscheidung kann sie nicht ersetzen. Nur ein bereits ausdrücklich zugelassener, technisch unterstützter und revisionsgebundener Ausnahmeweg des zuständigen Fachvertrags ist möglich. |
| `redaktionell abweichbar` | Zielqualität, von der der Eigentümer am konkreten Kandidaten nach §6 bewusst abweichen kann. Die KI darf keine Annahme erfinden. Feste Motiv-/Parameterfreigaben bleiben zusätzlich unabdingbare Voraussetzungen. |

Ein Gesamt-Score, ein Solvererfolg oder ein günstiger Durchschnitt kann kein
negatives Einzelurteil überdecken. `Warnung` verlangt eine inhaltliche Bewertung;
vor einem fälligen harten Gate sind `Warnung` und `nicht geprüft` kein Nachweis
seiner Erfüllung. Eine zulässige technische Ausnahme bleibt mit tatsächlichem
negativem Befund und separat akzeptierter Ausnahme sichtbar.

Die Ergebniswörter dieses Dokuments gehören zur redaktionellen Beurteilung.
Sie ersetzen nicht die technischen Gatewerte oder Solverstatus aus Authoring,
RP und ZA-1. Alte Berichte mit `Korrektur nötig`/`verfehlt` bleiben nach ihrem
damaligen Stand lesbar; neue Beurteilungen verwenden die obigen vier Ergebnisse.

## 3. Redaktionelle Kriterien nach Darstellung und Prüfzeitpunkt

Alle folgenden Kriterien sind **redaktionell abweichbar**. Herkunft und fällige
Prüfung stehen je Zeile. Die gemeinsame Identität und geschützte Merkmale aus
einer tatsächlichen Freigabe werden zusätzlich unter H-04 geprüft; eine
redaktionelle Abweichung autorisiert keine materielle Umgestaltung.

### 3.1 Abschlussbildphase

| ID / Kriterium | Herkunft | Methode und Zeitpunkt |
| --- | --- | --- |
| Q-B01 · Motividentität, Silhouette, Perspektive und Proportionen | Produkt §3.3; Design §4.3; Authoring §§2.1–2.4 | Vor Bildauswahl/-freigabe jede tatsächliche Bilddatei mit Briefing/Referenz vergleichen: Hauptgegenstand, Pose, charakteristische Details, Anatomie und notwendige Negativräume benennen; Verzerrungen/Artefakte einzeln ausweisen. |
| Q-B02 · Ausgearbeitete Illustration und ruhige Flächensprache | Design §§2/4.3; Authoring §2.3 | In großer und kleiner Ansicht vor Bildfreigabe Konturen, zusammenhängende Farbflächen, Binnenzeichnung, Oberflächendetails und zurückhaltende Schattierung prüfen. Keine bloß vergrößerte Zellgrafik, zufälligen Kleinstflächen, überladenen Hintergründe oder ungewollte Schrift/Wasserzeichen. |
| Q-B03 · Transparenter Bildgrund und saubere Kanten | [AT §2](REVEAL_TRANSPARENCY.md); Authoring §§2.3/4.4 | Vor Bildfreigabe und bei jeder Bildrevision Außenfläche, echte Aussparungen und Alphakanten auf dem vorhandenen Papier groß und in Kataloggröße ansehen; helle Motivteile und feine Details erhalten. Säume/ausgefranste Kanten benennen. Szenen erhalten eine konkrete motivbezogene transparente Außengestaltung/Vignette bei erhaltener notwendiger Umgebung, keinen pauschalen Verzicht. |

### 3.2 Motivvorlage

| ID / Kriterium | Herkunft | Methode und Zeitpunkt |
| --- | --- | --- |
| Q-M01 · Gemeinsame Identität bei kontrollierter Abstraktion | Produkt §3.3; Design §4.3; Authoring §§2.2–2.4 | Vor Motivfreigabe Abschlussbild und gespeicherte Motivvorlage nebeneinander ansehen. Perspektive, Hauptproportionen, charakteristische Details und wichtige Innen-/Negativräume abgleichen; jede beabsichtigte Zusammenfassung oder Auslassung nennen. Das Abschlussbild nicht nachträglich zur Rechtfertigung eines anderen Rasters ändern. |
| Q-M02 · Darstellbarkeit und motivgerechte Flächennutzung | Produktion §3.2; Authoring §§2.1/2.3/4.3 | Vor Motivfreigabe in vorgeschlagener Rastergröße und kleiner Darstellung prüfen: tragfähige Hauptformen, kräftige Binnenformen, nutzbarer Freiraum und Detaildichte statt entscheidender Haarlinien, Pixelrauschen oder dekorativer Flächenfüllung. Größe/Crop/Modus als konkrete Alternative begründen, falls nötig. |
| Q-M03 · Sinnvolle Farbzahl und benannte Farbrollen | Authoring §2.1; #488 | Vor Motivfreigabe und bei Palettenvarianten jede Farbe einer erkennbaren Motivfunktion zuordnen; Zusammenlegung/kleinere Palette auf Identitätsverlust prüfen. Die technische Obergrenze ist kein Zielwert. Der freigegebene genaue Farbwunsch/Parameterkorridor ist zusätzlich H-01/H-04. Die reichere Palette des Abschlussbilds wird nicht auf Rasterfarben beschränkt. |

### 3.3 Tatsächliches Raster

| ID / Kriterium | Herkunft | Methode und Zeitpunkt |
| --- | --- | --- |
| Q-R01 · Motivtreue und Erkennbarkeit | Produkt §3.3; Design §4.3; Authoring §§2.3/4.1/4.3 | Je Kandidat vor Auswahl sowie nach Reparatur das exakte Raster als verlustfreie Kleinvorschau, ohne Glättung vergrößert und mit Gitter mit Motivvorlage/Abschlussbild vergleichen. Farbe soll selbst ein erkennbares Bild ergeben; bei Mono darf die farbige Enthüllung die stärkere Abstraktion auflösen. In beiden Fällen müssen Hauptform, Perspektive und Identität nachvollziehbar zusammengehören. |
| Q-R02 · Hauptformen, Negativräume und gezielte Details | Produktion §6; Authoring §§4.3–4.4 | An denselben Ansichten zusammenhängende Hauptformen, Proportionen, notwendige Öffnungen und Einzelzellen auf Motivfunktion prüfen. Ein Auge darf eine Zelle sein; eine wichtige Öffnung darf nicht für leichteren Solvererfolg verschwinden. Zufällige Artefakte und überladene Kleinstflächen konkret markieren. |
| Q-R03 · Flächennutzung und Innenleerlinien | Authoring §4.3 | Je Kandidat Belegung, isolierte Einzelzellen und vollständig leere Innenzeilen/-spalten erfassen und ansehen. Die bisherigen 15-/85-%-Belegungswerte bleiben ausschließlich Prüfanlässe: weder automatische Ablehnung noch Rechtfertigung für Strecken, Randpixel oder blindes Entfernen von Leerstreifen. Motivischen Nutzen beziehungsweise störende Wirkung begründen. |
| Q-R04 · Tatsächlich verwendete Palette, alle Farbpaare | Authoring §§2.1/4.3; #488 | Früh bei Paletten-/Rastervergleich und am endgültigen Raster sämtliche verwendeten Vordergrund-IDs samt Farbwerten paarweise visuell beurteilen, auch seltene und unbenachbarte Farben. Unterschiede müssen deutlich sichtbar sein; keine zusätzliche Farbe allein für Solvererfolg oder Verfügbarkeit. Unbenutzte Einträge nicht als verwendete Farben zählen. Kleine Darstellung und Q-H01/Q-H02 mitprüfen; ähnliche Schattierungen konkret nennen. Numerische Prüfung ausdrücklich erst P-A/P-B, heute kein erfundener Validator. |

### 3.4 Hinweisansicht und Spielstruktur

| ID / Kriterium | Herkunft | Methode und Zeitpunkt |
| --- | --- | --- |
| Q-H01 · Farb- und Zelllesbarkeit auf Papier | [Zeichenstil ZS-D02/03/05](UI_DRAWING_STYLE.md); Design §§2/4.4; #488 | Vor Endabnahme die tatsächliche Rasterpalette in repräsentativer Zell-/Hinweisgröße einschließlich kleiner Darstellung auf dem aktuellen Papier unter vorhandener Kontur und Schraffur beurteilen. Vordergrundfarben, Leergrund, Nachbarzellen und Fünferlinien müssen erkennbar bleiben. Große isolierte Farbfelder reichen nicht. Farbsinnsimulation, soweit verfügbar, nur ergänzend mit Methode/Grenzen angeben. |
| Q-H02 · Lesbare Hinweisziffern und Farbzuordnung in allen Zuständen | [Hinweistypografie](CLUE_TYPOGRAPHY.md), [Hinweisstatus](CLUE_STATUS.md), [ZS-D01](UI_DRAWING_STYLE.md) | Vor Endabnahme wirkliche ein-/mehrstellige Hinweise beider Achsen in normalem, abgeschwächtem und zusätzlich ausgekreuztem Zustand prüfen; aktuelle Schrift, C1-Kontur und Papier verwenden. Zahl und Farbzugehörigkeit müssen auch klein erkennbar bleiben. Fehlende Darstellungsmöglichkeit als `nicht geprüft` melden, keine Sichtprüfung aus Proof/Dateihash ableiten. |
| Q-H03 · Spiel-/Hinweisstruktur und Arbeitsumfang | Produkt §§3.2/5; Produktion §7.1; Authoring §§4–5 | Nach finalem Proof vor Endabnahme tatsächliche Hinweisfolgen, Farbabhängigkeiten, Kleinteiligkeit, Engstellen und Umfang anhand des gebundenen Verlaufs beschreiben. Keine pauschale Abwertung vieler kleiner Zahlen/Farben, kein hoher Schwierigkeitsgrad allein aus Größe/Laufzeit. Die gebundene Bewertung ist separat H-06; Probespielen bleibt optional. |

Diese Sichtungen gehören zu den bestehenden Bild-/Motiv-/Endabnahmen. Sie
verlangen keine neue allgemeine Freigabeschleife, keinen Pflicht-Spielstart und
kein manuelles Probespiel je Rätsel. Fehlt die nötige Ansicht, bleibt gerade
dieser Sichtnachweis offen; eine Dokument-/Logikprüfung ersetzt ihn nicht.

## 4. Unabdingbare Voraussetzungen und zuständige harte Normen

Jede folgende Zeile ist eine **unabdingbare Voraussetzung**. Der bestehende
enge Randregel-Ausnahmeweg ist kein allgemeiner Qualitätsbypass. Die konkreten
Schemas, Zahlen und Befehle bleiben ausschließlich in den verlinkten Normen.

| ID / Voraussetzung | Herkunft | Methode und fälliger Zeitpunkt |
| --- | --- | --- |
| H-01 · Maße, Werte, verwendete Farbzahl und Farb-/Randregeln | [Authoring §4.2](ai-workflows/PUZZLE_AUTHORING.md), [ZA-1](ZA1_ADAPTER.md), [CLI](../tools/puzzle_production/README.md) | Bei jedem Import/finalen Kandidaten automatisch an exakter Matrix/Design/Hinweisen prüfen; vor `content_ready` vollständig belegen. Eine Randverletzung nur über die bereits unterstützte konkrete ZA-1-v2-Autorisierung behandeln, tatsächlichen Negativbefund sichtbar erhalten. |
| H-02 · Vollständige Deduktion und unabhängiger Proof | [Produktion §5](PUZZLE_PRODUCTION.md), [Authoring §§4.2/4.2.1](ai-workflows/PUZZLE_AUTHORING.md) | Nach letzter Logikänderung vom unbekannten Start unter benanntem zugelassenem Profil lösen, geschriebenen vollständigen Proof unabhängig frisch prüfen und Endmatrix vergleichen; vor `content_ready`. `stalled`, Abbruch, Such-`unique` und bloßer Exitcode genügen nicht. |
| H-03 · Herkunft, Rekonstruktion und Nutzungsgrundlage | [Produktion §§3–4](PUZZLE_PRODUCTION.md), [Authoring §§4.1/6](ai-workflows/PUZZLE_AUTHORING.md), [ZA-1](ZA1_ADAPTER.md) | Quellenbytes, Bearbeitung, Normalisierung, Parameter, Matrix-/Hinweisbindung und gegebenenfalls Reparatur-Replay dateibasiert prüfen; Rechte/Herkunft vor Freigabe klären. Kein erfundener Rechtetext oder Ersatz durch Eigentümerwunsch. Vor `content_ready` vollständig belegen. |
| H-04 · Tatsächliche Bild-/Motivfreigaben und erlaubte Änderungen | [Authoring §§2.4/4.4/6](ai-workflows/PUZZLE_AUTHORING.md), [AT](REVEAL_TRANSPARENCY.md), [ZA-1](ZA1_ADAPTER.md) | Vor Abstraktion die konkrete Bildfreigabe, vor Rasterproduktion die Motivfreigabe samt Parameterkorridor prüfen. Materielle Änderungen erneut freigeben; vor `content_ready` alle gültigen Bindungen abgleichen. Ein ausdrücklich unterstützter historischer Autorisierungsweg gilt nur unter seinen eigenen Bedingungen. |
| H-05 · Paket-/Inventarbindung, echte Endabnahme und Integrationsauftrag | [Authoring §§6–8](ai-workflows/PUZZLE_AUTHORING.md), [ZA-1](ZA1_ADAPTER.md) | Vor Ausgabe eines Angebots geschriebenes Einzelkandidatenpaket/Inventar prüfen. Endabnahme am tatsächlich ausgewählten Paket extern binden, vor Export/Integration vollständig nachweisen und Arbeitsbefugnis prüfen. `content_ready` darf noch die menschliche Endabnahme offen haben; eine Sheet-Auswahl erteilt sie nicht automatisch. |
| H-06 · Gebundene Schwierigkeit | [Authoring §5](ai-workflows/PUZZLE_AUTHORING.md), [SD2-Integration](SD2_INTEGRATION.md) | Nach finaler Deduktion vor Endabnahme den aktuellen Methoden-/Analysevertrag am konkreten Kandidaten erfüllen; beim Export Definitionsbindung prüfen. Keine Ersatzstufe für fehlenden/abgebrochenen Nachweis und keine Neubewertung alter Pakete aus Q-A. |

## 5. Sichtung ohne vollständig qualifizierten Kandidaten

Nach der vorgesehenen Varianten-/Profil-/Reparatursuche innerhalb der
[Authoringbudgets §§4.1–4.4](ai-workflows/PUZZLE_AUTHORING.md) MUSS die KI bei
null vollständig qualifizierten Kandidaten die **zwei bis drei möglichst
unterschiedlichen besten vorliegenden brauchbaren Entwürfe** zur menschlichen
Ansicht zeigen, sofern vorhanden. Bei nur einem diesen zeigen. Weitere sinnvolle
Entwürfe bleiben im Entscheidungsprotokoll auffindbar; gleiche Matrizen mit
anderem Namen/Profil zählen nicht als Unterschied. Keine künstliche Quote,
Budgetausweitung oder Behauptung, ein Nichtfund beweise Unmöglichkeit. Sind keine
brauchbaren tatsächlichen Entwürfe vorhanden, diesen Umstand und den nächsten
konkreten Korrekturschritt melden, keine Bilder/Dateien erfinden.

Jede Sichtungsansicht MUSS unmittelbar enthalten:

- stabile ID und Revision sowie echte Bild-/Dateilinks auf **tatsächliches
  Raster und Abschlussbild**; Motivvorlage und Palettenbindung zum Vergleich;
- den Status **`Sichtungsentwurf – nicht integrationsbereit`**;
- geprüfte, fehlgeschlagene und ungeprüfte technische Voraussetzungen jeweils
  getrennt, mit ihren tatsächlichen Belegen beziehungsweise konkreten Lücken;
- jedes maßgebliche Qualitätsdefizit mit Kriterien-ID, betroffener Form/Farbe/
  Hinweisansicht, möglicher Korrektur und Auswirkungen auf Freigaben/Neunachweise.

Auch technisch nicht zertifizierte Entwürfe dürfen so zur **Diagnose** betrachtet
werden. Sichtbarkeit ist keine Zertifizierung, Empfehlung keine Auswahl und
Auswahl keine Integrationsfreigabe. Fehlende Proofs oder unklare Rechte bleiben
Blocker. Eine gestalterisch attraktive, technisch ungeprüfte Variante darf nicht
als bereits übernehmbar erscheinen.

Die Sichtung erfolgt im Chat mit echten Links im bestehenden Abschlussbericht,
ohne parallele Oberfläche. `Raster-Optionen` des Sheet-Formats v2 bleibt für
tatsächlich freigabefähige, vollständig gebundene Angebote nach Authoring §4.5/§7
reserviert. Bei null solchen Angeboten ist die Liste `[]`; keinen
Sichtungsentwurf als `content_ready` ausgeben. Den Produktionsstand je nach
tatsächlicher Lage als `raster_review` beziehungsweise `blocked` mit Ursache und
`Korrigieren oder Fehler beheben` als nächstem Schritt führen. Eine nach §6
zulässig angenommene redaktionelle Abweichung kann erst nach vollständiger
technischer Prüfung im bestehenden gültigen Auswahlweg erscheinen.

## 6. Gezielte redaktionelle Einzelfallentscheidung

Der Eigentümer DARF einen konkreten redaktionellen Mangel bewusst akzeptieren.
Dafür legt die KI zuerst den Befund samt Korrekturmöglichkeit nach §5 offen und
benennt ausdrücklich die betroffenen Kriterien. Die tatsächliche Entscheidung
wird im vorhandenen äußeren Entscheidungs-/Freigabebeleg **außerhalb versiegelter
Originale** nachvollziehbar festgehalten:

- Kandidaten-ID/Revision, Matrix-/Logikbindung, tatsächliche Palette mit IDs und
  Werten, Bild-/Motivdateien und Hashes sowie Originalpaket-/Handoff-/Inventarbindung;
- Kriterien-ID und Regelversion/Dokumentrevision/Quellstand, konkreter negativer
  Befund und Umfang der akzeptierten Abweichung einschließlich betroffener Paare;
- Begründung, tatsächlicher Akteur, UTC-Zeitpunkt und Wortlaut der Entscheidung;
- aktuelle technische Prüfbelege und noch offene Freigaben/Integrationsbefugnisse.

Die Einzelfallentscheidung verändert das Urteil `Warnung`/`nicht erfüllt` nicht
in `erfüllt` und ist **kein als bestanden gemeldeter Test**. Die redaktionelle
Annahme wird separat vermerkt. Sie ersetzt weder Bild-/Motiv-/Endfreigaben noch
heilt sie Verstöße gegen feste Auftrags-/Motivgrenzen. Bei materieller Änderung
gelten die Rücksprünge und Neuprüfungen aus Authoring §4.4.

Vor einem freigabefähigen Angebot müssen sämtliche dann fälligen harten Gates
aktuell erfüllt oder durch ihren bereits ausdrücklich zugelassenen, technisch
unterstützten revisionsgebundenen Ausnahmeweg gedeckt sein. Ohne diese Prüfungen
bleibt nur Korrektur/Neunachweis; eine bloße Eigentümerauswahl ist kein Ersatz.
Keine negativen Originalgates oder alten Belege umschreiben. Bei neuer Lieferung
die aktuellen redaktionellen Entscheidungen getrennt dokumentieren und nach
Authoring §6 sichern; Gatefelder behalten ihre bisherige Freigabe-/Belegsemantik.
Kann ein bestehender technischer Weg einen Zustand nicht gültig abbilden, ist
keine Übernahme durch Freitext oder ein zusätzliches `pass` erlaubt.

Insbesondere begründet Q-A keinen neuen technischen Paletten-Ausnahmeweg.
Ein späteres negatives P-B-Prüfergebnis bleibt negativ; eine Übernahme setzt
den erst von P-B zu implementierenden und zu prüfenden, revisions-/paargebundenen
Weg sowie sämtliche übrigen Inhaltsgates voraus. Heute keine solchen Befehle,
Felder oder Prüfungen behaupten. Q-A erlaubt die redaktionelle Sichtung und
konkrete Entscheidung innerhalb der bestehenden technischen Verträge.

## 7. Vier endliche synthetische Entscheidungsbeispiele

Diese Beispiele sind reine Vertragsdurchläufe, keine Produktionspakete,
Bilddateien, Freigaben oder ausgeführten Solverbeweise. Die technischen
Prüfergebnisse sind **gesetzte Szenarioeingaben**, um die Entscheidung zu prüfen;
sie behaupten keine Zertifizierung der hier notierten Miniaturmatrizen.
`A/B` sind unterschiedliche Vordergrundrollen, `.` ist Leer. Als gemeinsames
synthetisches Abschlussmotiv dient ein illustriertes Segelboot; kein Kataloginhalt
oder davon abgeleiteter Testfall. Die Beschreibungen ersetzen in einer echten
Sichtung niemals Bild-/Dateilinks. Kein neuer automatischer CI-Testbestand.

| Fall / endlicher Eingang | Entscheidung und überprüfbarer Ausgang |
| --- | --- |
| S-01 · Vollständig qualifiziert: `S-A/r01`, Raster `A../AA./BBB`, transparentes Boot mit gleicher Perspektive; alle fälligen H-01–H-06 und Q-Kriterien als belegt erfüllt gesetzt, allein menschliche Endabnahme/Integrationsauftrag noch offen. | Ein gebundenes Angebot in `Raster-Optionen`, `content_ready`; keine automatische Auswahl/Endabnahme. Erst tatsächliche Auswahl plus externe Endfreigabe/Integrationsauftrag erlauben Auftrag 4. Ein Angebot genügt, keine Quote. |
| S-02 · Nur redaktioneller Mangel: `S-B/r01`, dasselbe Raster als eigenständiger synthetischer Fall; technische Voraussetzungen vollständig gesetzt, unwichtiges Zierdetail fehlt (Q-M01/Q-R01 `nicht erfüllt`), Identitätskern und freigegebene Invarianten erhalten. | Zunächst Sichtungsentwurf mit echten Ansichten im Produktionsfall, leere Rasteroptionsliste. Korrektur: Detail motivtreu ergänzen und abhängige Prüfungen erneuern. Alternativ nimmt der Eigentümer ausdrücklich genau dieses Detaildefizit an; §6-Bindungen außen ergänzen, negativen Befund erhalten. Erst bei vollständigen aktuellen technischen Belegen/zulässiger Paketbindung darf der Kandidat als Angebot erscheinen; Endabnahme bleibt ein eigener tatsächlicher Schritt. |
| S-03 · Technischer Blocker: `S-C/r01`, Raster `A../AA./BBB`, Bild-/Motivqualität positiv gesetzt, vollständiger unabhängiger Proof H-02 fehlt (`nicht geprüft`). | Nur Diagnose-Sichtung, `Sichtungsentwurf – nicht integrationsbereit`, keine Rasteroption und kein `content_ready`, auch bei ausdrücklichem Gefallen. Nächster Schritt ist vollständiger Deduktions-/Prüfnachweis; eine Qualitätsausnahme heilt den fehlenden Proof nicht. Unklare Rechte H-03 hätten dieselbe Sperrwirkung. |
| S-04 · Null-Treffer nach begrenzter Suche: vier Kandidaten, zwei Reparaturrunden ohne vollständig qualifiziertes Ergebnis als beendet gesetzt. `S-D/r01: A../AA./BBB` mit fehlendem Proof; `S-E/r02: ..A/.AA/BBB` mit sichtbarer Perspektivabweichung Q-R01 und fehlender aktueller Motivfreigabe H-04; `S-F/r03: AA./A../BBB` mit überladener Kleinstform Q-R02 und offenem H-06. Vierter Kandidat ist identisch mit S-D. | Drei verschiedene beste brauchbare Entwürfe mit Status, technischen Lücken, Defiziten und Korrekturmöglichkeiten zeigen; Duplikat und Entstehungswege im Protokoll. `Raster-Optionen=[]`, kein `content_ready`, keine Budgeterhöhung. Behebung: D nachweisen, E motivtreu korrigieren beziehungsweise neue Motivfreigabe einholen, F vereinfachen/neu prüfen und Bewertung binden. Bei nur einem vorhandenen brauchbaren Entwurf genau diesen zeigen; bei keinem den konkreten Nichtfund melden. |

Die einmalige Q-A-Akzeptanzkontrolle geht diese vier Eingaben in Reihenfolge
durch und vergleicht Sichtungsstatus, Optionsliste, Ausnahmebefugnis und nächsten
Schritt mit §2/§4–6. Ergebnisse kompakt im Liefer-PR führen, unabhängigem Review
zugänglich; keine dauerhaften Beispielbilder, technischen Uploads oder neue
Testfamilie. Das prüft den redaktionellen Entscheidungsvertrag, keine
Farbmetrik, Bildqualität oder Adapterfunktion. P-A/P-B erhalten eigene Nachweise.
