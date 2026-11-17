# Redaktioneller Qualitätsvertrag für neue Rätsel

**Vertrag 1.0 · Dokumentrevision 16 · 17.11.2026 · PROD-SLIM / [#700](https://github.com/venomenon328/picross/issues/700)**

## 1. Geltung und Zuständigkeit

Status: `active`. Diese Datei definiert Kriterien-IDs, Ergebniswörter,
Belegbindungen, Prüfzeitpunkte, harte Voraussetzungen, redaktionelle
Einzelfallentscheidungen und die numerische Farbprüfung.

- Gestalterische Normen: ausschließlich die [Bildtypverträge](images/README.md).
- Ablauf, Kandidatenzahl, Budgets, Sicherung und tatsächliche Freigaben: [Authoring 0.8.0, Dokumentrevision 10](authoring/PUZZLE_AUTHORING.md).
- Datenformen: [PW-B](../tools/PW_B_CONTRACT.md), [ZA-1](ZA1_ADAPTER.md) und die tatsächlich benutzten technischen Einzelverträge.
- §7 und §§8.1–8.3.1 sind historische Entscheidungs-/Referenzbeispiele; keine neuen Produktionsaufträge oder zusätzlichen Pflichtprüfungen. Operative Farbpflichtquelle ist ausschließlich §8.4–8.5.
- Technische Prüfung erzeugt kein Sichturteil und keine menschliche Entscheidung. Historische Originale, Freigaben und Bewertungen werden nicht migriert.

Die [Phasenroute](authoring/PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase)
bestimmt die fällige Lektüre. Querverweise sind Zuständigkeitsangaben und verlangen
keine rekursive Volllektüre. Die bestehende Farbregel, ihre frühe automatische
Ist-Matrixprüfung und die abschließende Endprüfung gelten unverändert.

## 2. Einzelurteile, Belege und Klassen

Für jedes fällige Kriterium steht ein knappes aktuelles Einzelurteil mit
Begründung, Methode und tatsächlichem Prüfer im einen aktuellen Arbeitsrecord
nach [PW-B](../tools/PW_B_CONTRACT.md). Die gebundenen Bild-/Rasterdateien
bestimmen den Gegenstand. Bei Farbfragen verwendete IDs/RGB und betroffene Paare
benennen. Unbekannter Zeitpunkt bleibt ausdrücklich unbekannt; keine erfundene
Prüfung. Keine separaten Protokoll-, Herkunfts-, Prompt- oder Korrekturdateien.

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

### 2.1 Sichtmethode für Bilddateien

Gespeicherte Originale direkt ansehen; bei Abschlussbildern groß und klein,
bei Bedarf auf neutralem Grund/Schachbrett. Die jeweiligen Kriterien ergänzen
die benötigten Vergleiche. Keine routinemäßige Buch-/Katalogmontage, Fadeprobe,
Kandidaten-Testintegration, Godot-Start oder zusätzliche persönliche Buchabnahme;
dies gilt auch für spätere Phasen. Bestehende technische Tests tragen ihre
Render-/Integrationsgarantien. Q-H01/Q-H02 behalten den eigenen Zell-/Hinweisgegenstand.

## 3. Redaktionelle Kriterien nach Darstellung und Prüfzeitpunkt

Alle folgenden Kriterien sind **redaktionell abweichbar**. Herkunft und fällige
Prüfung stehen je Zeile. Die gemeinsame Identität und geschützte Merkmale aus
einer tatsächlichen Freigabe werden zusätzlich unter H-04 geprüft; eine
redaktionelle Abweichung autorisiert keine materielle Umgestaltung.

### 3.1 Abschlussbildphase

| ID / Kriterium | Gestalterische Norm | Methode und Zeitpunkt |
| --- | --- | --- |
| Q-B01 · Motividentität, Silhouette, Perspektive und Proportionen | [RV-01](images/REVEAL.md#rv-01-motividentität) | Vor Bildauswahl/-freigabe jedes gespeicherte Original mit Briefing/Referenz und geschützten Merkmalen vergleichen; konkrete Abweichungen einzeln ausweisen. |
| Q-B02 · Ausgearbeitete Illustration und ruhige Flächensprache | [RV-02](images/REVEAL.md#rv-02-illustration) | Vor Bildfreigabe das tatsächliche Original in großer und kleiner Ansicht gegen alle zugeordneten Stilanforderungen beurteilen. Optionale Zeichentechniken nicht in Pflichten umdeuten. |
| Q-B03 · Transparenter Bildgrund und saubere Kanten | [RV-03–RV-05](images/REVEAL.md#rv-03-transparenz-und-kanten) | Vor Bildfreigabe und nach jeder Bildrevision Original groß/klein ansehen; Außenfläche, Aussparungen, Alphakanten, helle Motivteile und Szenenumgebung tatsächlich prüfen. Bei Bedarf neutralen Grund/Schachbrett verwenden. |

### 3.2 Motivvorlage

| ID / Kriterium | Gestalterische Norm | Methode und Zeitpunkt |
| --- | --- | --- |
| Q-M01 · Gemeinsame Identität bei kontrollierter Abstraktion | [MV-01](images/MOTIF.md#mv-01-ableitung-und-identität) | Vor Motivfreigabe Abschlussbild und gespeicherte Motivvorlage nebeneinander ansehen; jede beabsichtigte Zusammenfassung/Auslassung benennen und ihre Wirkung auf die geschützten Merkmale beurteilen. |
| Q-M02 · Darstellbarkeit und motivgerechte Flächennutzung | [MV-02](images/MOTIF.md#mv-02-darstellbarkeit) | Vor Motivfreigabe in vorgeschlagener Rastergröße und kleiner Darstellung prüfen; bei einem Mangel Größe, erlaubten Crop oder Modus als konkrete Alternative begründen. |
| Q-M03 · Sinnvolle Farbzahl und benannte Farbrollen | [MV-03](images/MOTIF.md#mv-03-farbrollen) | Vor Motivfreigabe und bei Palettenvarianten die Farbrollen und die Wirkung einer Zusammenlegung vergleichen. Den freigegebenen Farbwunsch/Parameterkorridor getrennt als H-01/H-04 prüfen. |

### 3.3 Tatsächliches Raster

| ID / Kriterium | Gestalterische Norm | Methode und Zeitpunkt |
| --- | --- | --- |
| Q-R01 · Motivtreue und Erkennbarkeit | [RS-01](images/RASTER.md#rs-01-diskrete-abstraktion) | Je Kandidat vor Auswahl und nach Reparatur das exakte Raster als verlustfreie Kleinvorschau, ohne Glättung vergrößert und mit Gitter mit Motivvorlage/Abschlussbild vergleichen. Mono- und Farbanforderung getrennt anwenden. |
| Q-R02 · Hauptformen, Negativräume und gezielte Details | [RS-02](images/RASTER.md#rs-02-formen-und-details) | An denselben Ansichten Hauptformen, Proportionen, Öffnungen und Einzelzellen auf Motivfunktion prüfen; konkrete Artefakte markieren. |
| Q-R03 · Flächennutzung und Innenleerlinien | [RS-03](images/RASTER.md#rs-03-flächennutzung) | Je Kandidat Belegung, isolierte Einzelzellen und vollständig leere Innenzeilen/-spalten erfassen und ansehen; Prüfanlässe motivisch bewerten, nicht als automatische Ablehnung behandeln. |
| Q-R04 · Tatsächlich verwendete Palette, alle Farbpaare | [RS-04](images/RASTER.md#rs-04-palette-und-sichtbare-zuordnung), §8.4–8.5 | Früh beim Paletten-/Rastervergleich und am endgültigen Raster alle tatsächlich verwendeten IDs/RGB-Werte paarweise visuell beurteilen, einschließlich seltener/unbenachbarter Paare. Q-H01/Q-H02 separat prüfen; numerische Diagnose und Sichturteil getrennt binden. |

### 3.4 Hinweisansicht und Spielstruktur

| ID / Kriterium | Herkunft | Methode und Zeitpunkt |
| --- | --- | --- |
| Q-H01 · Farb- und Zelllesbarkeit auf Papier | [Zeichenstil ZS-D02/03/05](../game/UI_DRAWING_STYLE.md); Design §§2/4.4; #488 | Vor Endabnahme die tatsächliche Rasterpalette in repräsentativer Zell-/Hinweisgröße einschließlich kleiner Darstellung auf dem aktuellen Papier unter vorhandener Kontur und Schraffur beurteilen. Vordergrundfarben, Leergrund, Nachbarzellen und Fünferlinien müssen erkennbar bleiben. Große isolierte Farbfelder reichen nicht. Farbsinnsimulation, soweit verfügbar, nur ergänzend mit Methode/Grenzen angeben. Auch eine positive Diagnose nach §8 ersetzt dieses Sichturteil nicht. |
| Q-H02 · Lesbare Hinweisziffern und Farbzuordnung in allen Zuständen | [Hinweistypografie](../game/CLUE_TYPOGRAPHY.md), [Hinweisstatus](../game/CLUE_STATUS.md), [ZS-D01](../game/UI_DRAWING_STYLE.md) | Vor Endabnahme wirkliche ein-/mehrstellige Hinweise beider Achsen in normalem, abgeschwächtem und zusätzlich ausgekreuztem Zustand prüfen; aktuelle Schrift, C1-Kontur und Papier verwenden. Zahl und Farbzugehörigkeit müssen auch klein erkennbar bleiben. Fehlende Darstellungsmöglichkeit als `nicht geprüft` melden, keine Sichtprüfung aus Proof/Dateihash oder positivem Paarwert (§8) ableiten. |
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
| H-01 · Maße, Werte, verwendete Farbzahl und Farb-/Randregeln | [Authoring §4.2](authoring/PUZZLE_AUTHORING_STEP_3.md), [ZA-1](ZA1_ADAPTER.md), [CLI](../../tools/puzzle_production/README.md) | Bei jedem Import/finalen Kandidaten automatisch an exakter Matrix/Design/Hinweisen prüfen; vor `content_ready` vollständig belegen. Eine Randverletzung nur über die bereits unterstützte konkrete ZA-1-v2-Autorisierung behandeln, tatsächlichen Negativbefund sichtbar erhalten. |
| H-02 · Vollständige Deduktion und unabhängiger Proof | [Produktion §5](PUZZLE_PRODUCTION.md), [Authoring §§4.2/4.2.1](authoring/PUZZLE_AUTHORING_STEP_3.md) | Nach letzter Logikänderung vom unbekannten Start unter benanntem zugelassenem Profil lösen, geschriebenen vollständigen Proof unabhängig frisch prüfen und Endmatrix vergleichen; vor `content_ready`. `stalled`, Abbruch, Such-`unique` und bloßer Exitcode genügen nicht. |
| H-03 · Aktuelle Inhaltsbindung und Nutzungsgrundlage | [Produktion](PUZZLE_PRODUCTION.md), [PW-B](../tools/PW_B_CONTRACT.md), [ZA-1](ZA1_ADAPTER.md) | Aktuelle Bilder, Matrix/Hinweise, Motiv-/Parameterkonformität und tatsächlich nötige Rechte/Notices prüfen. Keine Normalisierungs-, Generator-, Codec-, Toolhash-, Import- oder Reparaturhistorie und kein Herstellungsreplay als Zulassung. Ungeklärte Rechte bleiben Blocker. |
| H-04 · Tatsächliche Bild-/Motivfreigaben und erlaubte Änderungen | [Bildwahl §2.4](authoring/PUZZLE_AUTHORING_STEP_1.md) / [Motiv §2.4](authoring/PUZZLE_AUTHORING_STEP_2.md) / [Änderung §4.4](authoring/PUZZLE_AUTHORING_STEP_3.md) / [Sicherung §6](authoring/PUZZLE_AUTHORING.md), [AT](REVEAL_TRANSPARENCY.md), [ZA-1](ZA1_ADAPTER.md) | Vor Abstraktion die konkrete Bildfreigabe, vor Rasterproduktion die Motivfreigabe samt Parameterkorridor prüfen. Materielle Änderungen erneut freigeben; vor `content_ready` alle gültigen Bindungen abgleichen. Ein ausdrücklich unterstützter historischer Autorisierungsweg gilt nur unter seinen eigenen Bedingungen. |
| H-05 · Aktuelle Auswahl, echte Endabnahme und Integrationsauftrag | [PW-B](../tools/PW_B_CONTRACT.md), [Integration](authoring/PUZZLE_AUTHORING_STEP_5.md), [ZA-1](ZA1_ADAPTER.md) | Aktuelle angebotene/gewählte Dateien mit Kennung und Inhaltsbindung prüfen. Tatsächliche Entscheidungen an unveränderte aktuelle Inhalte binden; kein ZIP, Inventar, Handoff oder historischer Angebotsrecord erforderlich. content_ready kann die menschliche Endabnahme noch offen haben; eine UI-Absicht erteilt sie nicht. |
| H-06 · Gebundene Schwierigkeit | [Authoring §5](authoring/PUZZLE_AUTHORING_STEP_3.md), [SD2-Integration](../difficulty/SD2_INTEGRATION.md) | Nach finaler Deduktion vor Endabnahme den aktuellen Methoden-/Analysevertrag am konkreten Kandidaten erfüllen; beim Export Definitionsbindung prüfen. Keine Ersatzstufe für fehlenden/abgebrochenen Nachweis und keine Neubewertung alter Pakete aus Q-A. |
| H-07 · Vollständige oder weich auslaufende Hintergrundkomposition | [HG-06](images/BACKGROUND.md#hg-06-randabschluss), Q-HG03/Q-HG04 | Vor Angebot jede der vier Kanten der gespeicherten Originale visuell gegen HG-06 prüfen; nach materieller Korrektur und nach Ableitung am fertigen Bild wieder kontrollieren. Unabdingbare Voraussetzung ohne redaktionelle Abweichungsannahme. Dateimaße oder ein vorhandener Alphakanal belegen die Bildqualität nicht. |

Für neue 0.8-Angebote erfüllt bereits `raster_ready` alle fälligen Rastergarantien;
nur Hintergrundbereitschaft und nachfolgende echte Endabnahme bleiben getrennt.
Die ältere `content_ready`-Formulierung ist keine Erlaubnis, Rasterangebote
ungeprüft vorzuziehen. Weniger Angebote senken keines dieser Gates.

## 5. Sichtung ohne vollständig qualifizierten Kandidaten

Nach der vorgesehenen bedarfsweisen Varianten-/Profil-/Reparatursuche innerhalb
der [Authoringbudgets §§4.1–4.4](authoring/PUZZLE_AUTHORING_STEP_3.md) MUSS die KI bei
null vollständig qualifizierten Kandidaten die **zwei bis drei möglichst
unterschiedlichen besten vorliegenden brauchbaren Entwürfe** zur menschlichen
Ansicht zeigen, sofern vorhanden. Bei nur einem diesen zeigen. Weitere aktuell angebotene
Entwürfe bleiben im aktuellen Record erreichbar; gleiche Matrizen mit
anderem Namen/Profil zählen nicht als Unterschied. Keine künstliche Quote,
Budgetausweitung oder zusätzliche Erzeugung allein für diese Sichtungszahl.
Ein geeigneter vollständig qualifizierter Kandidat genügt dagegen nach Authoring
§4.5; bereits sinnvolle qualifizierte Alternativen dürfen angeboten werden.
Sind keine brauchbaren tatsächlichen Entwürfe vorhanden, diesen Umstand und den
nächsten konkreten Korrekturschritt melden, keine Bilder/Dateien erfinden.

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

Die Sichtung erfolgt mit echten Links im bestehenden Abschlussbericht und der
vorhandenen Produktionsansicht, ohne parallele Datenhaltung. Qualifizierte
Rasterangebote bleiben vollständig gebundenen Kandidaten nach Authoring §4.5/§7
vorbehalten. Bei null solchen Angeboten ist die Angebotsliste leer; keinen
Sichtungsentwurf als `raster_ready` oder `content_ready` ausgeben. Den Stand je
nach Lage als `raster_review` beziehungsweise `blocked` mit Ursache führen.
Eine nach §6 zulässig angenommene redaktionelle Abweichung kann erst nach
vollständiger technischer Prüfung im bestehenden gültigen Auswahlweg erscheinen.

## 6. Gezielte redaktionelle Einzelfallentscheidung

Der Eigentümer DARF einen konkreten redaktionellen Mangel bewusst akzeptieren.
Dafür legt die KI zuerst den Befund samt Korrekturmöglichkeit nach §5 offen und
benennt ausdrücklich die betroffenen Kriterien. Die tatsächliche Entscheidung
wird im aktuellen Record am konkreten gebundenen Ergebnis nachvollziehbar festgehalten:

- Kandidaten-ID/Revision, Matrix-/Logikbindung, tatsächliche Palette mit IDs und
  Werten, Bild-/Motivdateien und Hashes ohne Originalpaket-/Handoff-/Inventarpflicht;
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
Authoring §6 sichern; Negative Urteile und ausdrücklich angenommene Abweichungen bleiben getrennt.
Kann ein bestehender technischer Weg einen Zustand nicht gültig abbilden, ist
keine Übernahme durch Freitext oder ein zusätzliches `pass` erlaubt.

Dieser Qualitätsvertrag begründet den redaktionellen Weg. Die geschlossenen
Sicht- und Ausnahmeformen einschließlich ihrer Generationen stehen ausschließlich
in [PW-B · Palettenausnahme](../tools/PW_B_CONTRACT.md#palettenausnahme).
Ein negatives Messergebnis bleibt auch bei Übernahme negativ. Sämtliche übrigen
Inhaltsgates bleiben erforderlich; die bloße Sichtung oder ein Freitextvermerk
ist keine technische Ausnahme.

## 7. Vier endliche synthetische Entscheidungsbeispiele

Diese Beispiele sind reine historische Vertragsdurchläufe, keine Produktionspakete,
Bilddateien, Freigaben oder ausgeführten Solverbeweise. Die technischen
Prüfergebnisse sind **gesetzte Szenarioeingaben**, um die Entscheidung zu prüfen;
sie behaupten keine Zertifizierung der hier notierten Miniaturmatrizen.
`A/B` sind unterschiedliche Vordergrundrollen, `.` ist Leer. Als gemeinsames
synthetisches Abschlussmotiv dient ein illustriertes Segelboot; kein Kataloginhalt
oder davon abgeleiteter Testfall. Die Beschreibungen ersetzen in einer echten
Sichtung niemals Bild-/Dateilinks. Kein neuer automatischer CI-Testbestand.
Die historischen Sheet-/Auftragsnummern in dieser Tabelle bezeichnen die damalige
Generation; neue Produktion folgt der fünfstufigen Authoringroute.

| Fall / endlicher Eingang | Entscheidung und überprüfbarer Ausgang |
| --- | --- |
| S-01 · Vollständig qualifiziert: `S-A/r01`, Raster `A../AA./BBB`, transparentes Boot mit gleicher Perspektive; alle fälligen H-01–H-06 und Q-Kriterien als belegt erfüllt gesetzt, allein menschliche Endabnahme/Integrationsauftrag noch offen. | Ein gebundenes Angebot in `Raster-Optionen`, `content_ready`; keine automatische Auswahl/Endabnahme. Erst tatsächliche Auswahl plus externe Endfreigabe/Integrationsauftrag erlauben Auftrag 4. Ein Angebot genügt, keine Quote. |
| S-02 · Nur redaktioneller Mangel: `S-B/r01`, dasselbe Raster als eigenständiger synthetischer Fall; technische Voraussetzungen vollständig gesetzt, unwichtiges Zierdetail fehlt (Q-M01/Q-R01 `nicht erfüllt`), Identitätskern und freigegebene Invarianten erhalten. | Zunächst Sichtungsentwurf mit echten Ansichten im Produktionsfall, leere Rasteroptionsliste. Korrektur: Detail motivtreu ergänzen und abhängige Prüfungen erneuern. Alternativ nimmt der Eigentümer ausdrücklich genau dieses Detaildefizit an; §6-Bindungen außen ergänzen, negativen Befund erhalten. Erst bei vollständigen aktuellen technischen Belegen/zulässiger Paketbindung darf der Kandidat als Angebot erscheinen; Endabnahme bleibt ein eigener tatsächlicher Schritt. |
| S-03 · Technischer Blocker: `S-C/r01`, Raster `A../AA./BBB`, Bild-/Motivqualität positiv gesetzt, vollständiger unabhängiger Proof H-02 fehlt (`nicht geprüft`). | Nur Diagnose-Sichtung, `Sichtungsentwurf – nicht integrationsbereit`, keine Rasteroption und kein `content_ready`, auch bei ausdrücklichem Gefallen. Nächster Schritt ist vollständiger Deduktions-/Prüfnachweis; eine Qualitätsausnahme heilt den fehlenden Proof nicht. Unklare Rechte H-03 hätten dieselbe Sperrwirkung. |
| S-04 · Null-Treffer nach begrenzter Suche: vier Kandidaten, zwei Reparaturrunden ohne vollständig qualifiziertes Ergebnis als beendet gesetzt. `S-D/r01: A../AA./BBB` mit fehlendem Proof; `S-E/r02: ..A/.AA/BBB` mit sichtbarer Perspektivabweichung Q-R01 und fehlender aktueller Motivfreigabe H-04; `S-F/r03: AA./A../BBB` mit überladener Kleinstform Q-R02 und offenem H-06. Vierter Kandidat ist identisch mit S-D. | Drei verschiedene beste brauchbare Entwürfe mit Status, technischen Lücken, Defiziten und Korrekturmöglichkeiten zeigen; Duplikat und Entstehungswege im Protokoll. `Raster-Optionen=[]`, kein `content_ready`, keine Budgeterhöhung. Behebung: D nachweisen, E motivtreu korrigieren beziehungsweise neue Motivfreigabe einholen, F vereinfachen/neu prüfen und Bewertung binden. Bei nur einem vorhandenen brauchbaren Entwurf genau diesen zeigen; bei keinem den konkreten Nichtfund melden. |

Die einmalige Q-A-Akzeptanzkontrolle ging diese vier Eingaben in Reihenfolge
durch. Sie ist kein neu auszuführendes PW2-A-Produktions- oder CI-Gate.
Das prüfte den redaktionellen Entscheidungsvertrag, keine Farbmetrik,
Bildqualität oder Adapterfunktion. Historische Nachweise behalten ihren Umfang.

## 8. P-A-V01: Freigegebene Regel für paarweise Farbunterscheidbarkeit

### 8.1 Status, Referenzplan und Grenzen

**Verbindliche Regel-ID `picross-palette-separation-1` (Version 1);
fachlich freigegeben, P-B1-Diagnose ausführbar; automatische Pflicht seit 0.6.0 durch P-B2.**
Die frühere Vorschlagskennung `picross-palette-separation-1-draft1`
bezeichnet die mathematisch **unveränderte** Fassung, deren Formel,
Quantisierung, Grenzen D=10/15 und Warnzone der Eigentümer
[für die unveränderten Referenzen vollständig freigegeben hat](https://github.com/venomenon328/picross/issues/488#issuecomment-6721785147).
Die ursprünglichen Referenzbilder und Testrechnungen bleiben nachvollziehbar.
Die vollständige Originalbildsicht konnte mangels funktionierendem
Binärzugang nicht erfolgen und wurde ausdrücklich als Merge-Gate erlassen;
sie wird **nicht** als tatsächlich durchgeführt dargestellt.
Die unabhängige Quellen-/Rechenprüfung ist im PR #546 dokumentiert.

Die Regel ist ab ihrem Normmerge verbindlicher Sollstand für **neue** Rätsel.
Der freiwillige Diagnosebericht `picross-palette-assessment-v1` aus P-B1 bindet
die unveränderte Berechnung ausdrücklich an Normrevision 4 am Quellcommit
`45b8fe697364bf73f4277c8b76f92d5c00400919`; auch Dokumentrevision 14 ändert
Formel, Quantisierung, Grenzen, Referenzwerte und bestehende Bindungen nicht.
P-B2 führte Früh-/Endintegration und den geprüften äußeren Ausnahmeweg für 0.6.0 ein;
die Garantien gelten im 0.8-Weg weiter. Die visuelle Produktionsprüfung bleibt
eigenständig. Authoring 0.5.0, Sheet v2 und versiegelte Altformate behalten ihre
Semantik. Kein rückwirkendes Gate, keine Neubewertung oder Umfärbung des Bestands.

Der [vor der Auswertung veröffentlichte Plan](https://github.com/venomenon328/picross/issues/488#issuecomment-6720934579)
bindet `main@059bb003dc761e862b304957143b0dd45d92bb82`, synthetische 40×30-Matrizen,
alle Farbwerte/Nutzungen und offene Fragen. Plancommit
`1ac4d44a75af9a604bffcb985c0570954beea761`, `plan.json` SHA-256
`ebeb0fdd518cc1da23e2ed50a730b9b81e04a8ce2cbf53058e4d670c7b1b74b7`.
Kein Katalogrätsel oder Bestandsderivat. Die folgende kleine Textreferenz bleibt;
Originalbilder, Berechnungsscripte und vollständige Paaroutputs sind befristete
Reviewdaten im separaten Ref gemäß [CI-Vertrag](../dev-rules/CI_CONTRACT.md).
Der Lieferkommentar verlinkt ihren unveränderlichen Belegcommit und das Manifest
mit Produkt-Head, Dateihashes/Bytes, Bildmaßen und Abruf-/Reproduktionsweg.

Je Liste sind `c01…` aufsteigende Vordergrund-IDs, in Klammern die tatsächlichen
Nutzungszahlen. Leer: 162 Zellen, außer F07 mit 161; 1.200 Zellen insgesamt.
Alle ungeordneten Paare werden verglichen, nicht nur Nachbarschaften.

| Familie / Frage | Eingangsfarben in ID-Reihenfolge |
| --- | --- |
| F01 · deutlich verschiedene Farbtöne | `#cc3333 (520), #2678bd (518)` |
| F02 · nahe Schattierungen | `#447799 (520), #487b9d (518)` |
| F03 · anderer Farbton bei ähnlicher Luminanz | `#b04444 (520), #337744 (518)` |
| F04 · ähnliche Farbtonrolle, andere Helligkeit | `#284c70 (520), #8bb8e4 (518)` |
| F05 · helle Farben auf Papier/C1 | `#fff4cf (269), #eadca8 (263), #ffffff (251), #f1d273 (255)` |
| F06 · dunkle Füllungen/Fünferlinien | `#232b32 (354), #39414a (348), #645248 (336)` |
| F07 · acht Farben, seltenes unbenachbartes kritisches Paar | `#447799 (159), #dd9944 (158), #995577 (142), #557744 (148), #774433 (152), #778899 (148), #ddddbb (131), #487b9d (1)` |
| F08 · zurückgehaltene abgestufte Nahpaare | `#447799 (269), #5a8daf (263), #6a9dbf (251), #77aacc (255)` |

F07 c08 sitzt bei (x=39,y=29), ihre direkten Nachbarn sind c02; c01 ist nicht
benachbart. F08 war bereits im Plan fixiert. Die
[erste Hypothese](https://github.com/venomenon328/picross/blob/0c740677931dc3e5f38631a94c7b0f91045b4a46/review-evidence/pa-v01/hypothesis.md)
wurde nach F01–F07 und vor F08-Auswertung veröffentlicht; danach keine Farben
oder Grenzen passend zum gewünschten Ergebnis geändert. Fragen und eigene
Beobachtungen sind keine erfundenen Eigentümerurteile.

### 8.2 Tatsächlich ausgeführte native Ansichten

Godot Standard **4.7.2-stable**, Enginecommit
`ed1daf0bf001b61586d9930840f2f1394092c079`, Windows/OpenGL Compatibility,
NVIDIA GeForce RTX 3070. Je Familie und Kontext eine reguläre Buch-/Rasteransicht
und ein isoliertes natives Zahlenpanel: insgesamt 32 Original-PNGs. Das Panel
ruft denselben `full_view_board.gd`-/`draw_clue_number`-/`clue_typography.gd`-Pfad
mit gemessener Geometrie auf. Zustände werden dort zur vollständigen Sichtprobe
explizit eingespeist; dies ist kein H1-Status-/Logiknachweis. Der Produktzeichner,
Atlas, Schrift und Buchshader sind unverändert. Der Diagnosekatalog verwendet nur
die fixierten synthetischen Matrizen; keine echten Saves oder Produktionsfreigaben.

| Kontext | Gemessene Zelle | Gemessener Schriftgrad / Slots horizontal × vertikal |
| --- | --- | --- |
| 1280×720, UI125, G, Zoomwunsch 24 | F01–06/F08: 13,49 px; F07: 13,40 px | 6; 13×13 px, auch im Panel |
| 1920×1080, UI100, G, Zoomwunsch 24 | alle 23,69 px | F01–04: 17 / 26×23 px; F05–08: 18 / 25×23 px, jeweils auch im Panel |

Das Raster zeigt reale Atlasfüllungen einschließlich kleiner Detailstufe,
Schraffur, X, unbekannte Zellen/Papier, normale und Fünferlinien sowie farbige
Hinweise beider Achsen. Das ergänzende Panel zeigt für jede Farbe `1` und `11`
jeweils zeilenweise und spaltenweise in OPEN/FILLED/CLOSED auf dem echten
Buchpapier. FILLED/CLOSED verwenden die bestehenden 60 %, CLOSED das bestehende X.
C1 wird tatsächlich nach der aktuellen Runtimezuordnung für Farb-IDs 2/4
angewendet, nicht anhand einer neuen Helligkeitsregel. F05 enthält deshalb
helle Farben mit und ohne C1. Große Paarfelder im Panel sind nur Orientierung.
Die Größen sind Messergebnisse dieses endlichen Satzes, keine Kapazitätsgarantie.
Bei 720p sind Ziffern bereits sehr klein; diese Einschränkung bleibt ausdrücklich
Teil der Eigentümersichtung und wird nicht durch Vergrößern des Originals verdeckt.

### 8.3 Kandidatenvergleich und begründete Wahl

Verglichen wurden Oklab-Distanz und getrennt relative Luminanz samt Kontrast.
Quellen: [Ottossons Oklab, aktualisierte lineare sRGB-Matrizen von 2021](https://bottosson.github.io/posts/oklab/)
und [W3C-Luminanzdefinition](https://www.w3.org/TR/WCAG22/#dfn-relative-luminance).
Die Distanz berücksichtigt Helligkeit und Farbton gemeinsam; die Luminanzdiagnose
verwendet `Y=0.2126 R+0.7152 G+0.0722 B` nach sRGB-Linearisierung,
`C=(max(Y1,Y2)+0.05)/(min(Y1,Y2)+0.05)` und `abs(Y1-Y2)`.
Diese Werte haben kein zusätzliches Gate und behaupten keine WCAG-Konformität.
Papier `#faf6ec` und Linie `#343f42` sind nur feste Diagnose-Surrogate;
der echte beleuchtete Papiergrund variiert. Keine daraus erfundene Pixelmessung.

| Fall / Paar | Oklab D gemäß §8.4, Anzeige auf 6 Stellen | Luminanz-Kontrast unquantisiert | Berechneter Referenzbefund |
| --- | --- | --- | --- |
| F01 c01/c02 | 30.055714 | 1.101501 | positiv |
| F02 c01/c02 | 1.341814 | 1.057795 | negativ |
| F03 c01/c02 | 22.237602 | 1.028384 | positiv |
| F04 c01/c02 | 35.939437 | 4.272436 | positiv |
| F05 c02/c04 (kleinstes Paar) | 5.573296 | 1.077067 | negativ |
| F05 c03/c04 (weiß/gelb) | 17.642013 | 1.478212 | metrisch positiv; F05 redaktionell angenommen, siehe §8.3.1 |
| F06 c01/c02 (kleinstes Paar) | 8.714149 | 1.386788 | negativ |
| F07 c01/c08 (kleinstes von 28 Paaren) | 1.341814 | 1.057795 | negativ, ungeachtet einer einzigen c08-Zelle |

Ein Kontrastgate würde F01/F03 ähnlich wie F02 behandeln, obwohl die Originale
deutlich andere Farbtöne zeigen. Oklab trennt diese Beispiele. Die frühere
Implementiererbewertung schwacher F05-Hinweise ist durch das positive
Eigentümer-Teilfeedback aus §8.3.1 als redaktionelles Urteil ersetzt.
F05 zeigt nun den ausdrücklich offengelegten konservativen Modellfehlfall:
metrischer Ausschluss trotz visueller Annahme dieser Referenz. F06 c01/c02
ist dagegen auch nach Eigentümerurteil unzureichend, obwohl die Zellen durch
Fugen weiterhin von Linien getrennt bleiben. Die **freigegebene Norm** ist
**Oklab-Ausschluss plus bestehende visuelle Prüfung mit getrennter
Einzelfallsemantik nach §6/§8.5**; ihre automatische Durchsetzung gilt mit P-B2 für 0.6.0. Kontrast/Luminanz bleiben erklärende Diagnosen.

Die vor F08 gewählten runden D-Grenzen 10/15 waren eine konservative
Arbeitshypothese zwischen dunklen Nahpaaren unter 10 und den deutlich anderen
Farbtonpaaren über 22; sie sind **inzwischen als Normgrenzen freigegeben**.
Keine statistisch optimierte Schwelle, keine validierte menschliche Fehlerquote.
10–15 bleibt bewusst als Unsicherheitszone sichtbar.
Im zurückgehaltenen Satz ergeben sich ohne Nachjustierung:

| F08-Paar | Exaktes ganzzahliges S gemäß §8.4 | D, Anzeige | Befund |
| --- | --- | --- | --- |
| c01/c02 | 5340838202 | 7.308104 | negativ |
| c01/c03 | 15668070476 | 12.517216 | positiv mit Warnung |
| c01/c04 | 27850476761 | 16.688462 | positiv |
| c02/c03 | 2713502054 | 5.209129 | negativ |
| c02/c04 | 8799172997 | 9.380391 | negativ |
| c03/c04 | 1739945433 | 4.171265 | negativ |

Die ganze F08-Palette bleibt metrisch negativ. Der Unterschied c01/c03 ist
weiterhin ein **visueller Warnfall bei einem konkreten Rätsel**, nicht eine
offene P-A-Normentscheidung; das positive Eigentümer-Teilfeedback zu c01/c04
bestätigt nur dieses Paar. P-A-M01 hat die **gesamte Regel einschließlich
Warnzonenbehandlung und F05-Modellfehlfall** inzwischen verbindlich freigegeben.
Restunsicherheit:
Schriftgröße, Konturzuordnung, Display/Farbmanagement, Sehvermögen und Kontext
werden nicht durch einen skalaren Farbraumabstand beschrieben. Keine universelle
Zugänglichkeitszusage oder neue Symbol-/Musterkennung.

#### 8.3.1 B-01: gebundenes Eigentümer-Teilfeedback und Referenzeinordnung

Quelle ist [P-A-R01 / B-01](https://github.com/venomenon328/picross/pull/546#pullrequestreview-5817832898)
am geprüften Produkt-Head `3e2bcfbd590a38e1a74764c3a52e88668f20edbe`.
Der Bericht dokumentiert das Teilfeedback der Eigentümerperson; veröffentlichender
Akteur `venomenon328`, Berichtszeitpunkt **08.11.2026, 12:15:10 UTC**.
Zeitpunkt und Umgebung der tatsächlichen Eigentümersichtung sowie die dabei
einzeln geöffneten Dateien sind nicht separat berichtet. Die folgende Bindung
ordnet das Feedback dem dort benannten unveränderten Referenzstand zu; sie
behauptet keine nachträglich ausgeführte Sichtung aller Größen/Zustände.

Gemeinsamer Originalstand: Belegcommit
`1d5b7e90db4c8843d7737f83411f896ceeee6231`,
[Manifest mit Datei-SHA-256, Bytes und Bildmaßen](https://github.com/venomenon328/picross/blob/1d5b7e90db4c8843d7737f83411f896ceeee6231/review-evidence/pa-v01/manifest.json).
Je Familie gelten die Originaldateien
`review-evidence/pa-v01/originals/Fxx-small-board.png`, `Fxx-small-tokens.png`,
`Fxx-normal-board.png` und `Fxx-normal-tokens.png`; `Fxx` steht in den folgenden
Zeilen für genau F05, F06 oder F08. Die Originale bleiben unverändert;
der Nacharbeitsnachweis im PR bindet sie außen an den neuen Dokument-Head.

| Referenz / Farb- und Paarbindung | Historisch berichtetes Eigentümer-Teilurteil | Getrennte Einordnung |
| --- | --- | --- |
| F05, Revision 1; c01 `#fff4cf`, c02 `#eadca8`, c03 `#ffffff`, c04 `#f1d273`; alle sechs Paare unten | „finde ich okay“ zur gezeigten F05-Referenz | Redaktionell positiv als Ganzes. Kein separat erklärtes Urteil zu jedem Paar oder jeder Bilddatei. Die früher behauptete visuelle Ablehnung des weiß/gelben Paars wird nicht fortgeführt; alle metrischen Negativ-/Warnbefunde bleiben erhalten. |
| F08, Revision 1; c01 `#447799` / c04 `#77aacc`, S `27850476761`, D `16.688462` | „in Ordnung“ | Redaktionell positives Teilurteil zu genau diesem metrisch positiven Paar; weder Annahme der ganzen F08-Palette noch der gesamten Regel. c01/c03 bleibt offen. |
| F06, Revision 1; c01 `#232b32` / c02 `#39414a`, S `7593640091`, D `8.714149` | c02 soll heller/blasser sein, um sich von c01 zu unterscheiden | Originalpaar unzureichend, konsistent mit `negative`. F06 bleibt unveränderter Negativfall. Keine neue Vergleichsvariante für diese redaktionelle Nacharbeit erforderlich. |

Für F05 unter der unveränderten Berechnung der freigegebenen Regel
`picross-palette-separation-1` gilt weiterhin:

| Paar | Exaktes S | D, Anzeige | Berechneter Referenzbefund |
| --- | --- | --- | --- |
| c01/c02 | 5757002441 | 7.587491 | negativ |
| c01/c03 | 3569810205 | 5.974789 | negativ |
| c01/c04 | 14157451021 | 11.898509 | positiv mit Warnung |
| c02/c03 | 16196735686 | 12.726640 | positiv mit Warnung |
| c02/c04 | 3106163242 | 5.573296 | negativ |
| c03/c04 | 31124061110 | 17.642013 | positiv |

**Entscheidung der Nacharbeit: begründete Referenzeinordnung, keine metrische
Revision.** F05 ist eine visuell angenommene synthetische Referenz mit negativem
metrischem Gesamtbefund und drei negativen Paaren. Damit ist ein Fehlfall des
konservativen Ausschlussvorschlags ausdrücklich bekannt. Eine globale Absenkung
zur nachträglichen Erzeugung eines positiven F05-Werts wäre unbegründet: Das
damalige Teilfeedback akzeptierte F05 als Referenz, legte aber keine
alternative Grenze fest und hob die unzureichende F06-Trennung nicht auf.
Die spätere vollständige [P-A-M01-Freigabe](https://github.com/venomenon328/picross/issues/488#issuecomment-6721785147)
bestätigt Formel, Grenzen 10/15, Quantisierung und Warnzone
**einschließlich** dieses offengelegten Modellfehlfalls ohne Revision.
Sämtliche ursprünglichen Paaroutputs bleiben unverändert.

Die Trennung von negativem Messbefund und separater redaktioneller Annahme folgt
§6. Hier wird **keine Produktionsausnahme erteilt**: Die Referenzen besitzen kein
freigabefähiges Produktionspaket/Inventar oder Inhaltszertifikat; eine solche
Bindung wird nicht erfunden. Das historische Teilfeedback wird nicht zu einer ausdrücklich
paargebundenen P-B-Ausnahme oder zu `pass` ergänzt. Auf Wunsch des
Eigentümers entsteht **keine zusätzliche formale F05-Ausnahmeakte**. Eine spätere reale Übernahme
mit negativem Palettenbefund benötigt weiterhin den von P-B implementierten und
geprüften Ausnahmeweg mit vollständigen §6-Bindungen und harten Inhaltsgates.
Vorabplan, Bilder und versiegelte Originalbelege werden nicht umgeschrieben.
P-A-M01 ist für die vollständige Farbregel ausdrücklich erteilt.
Die frühere Originalzugriffslücke bleibt als Tatsache dokumentiert; der
Eigentümer hat die vollständige unabhängige Bildoriginalsicht mangels
funktionierendem Binärzugriff [ausdrücklich erlassen](https://github.com/venomenon328/picross/issues/488#issuecomment-6721785147).
Daraus wird keine tatsächlich ausgeführte Vollsicht. Ein neuer PR-Head
benötigt weiterhin die aktuellen CI-/Diff-/Quellenchecks, aber keine
erneute persönliche Farbregel- oder Originalbildabnahme.

### 8.4 Verbindliche Berechnung und Randwerte

Eingang: exakte Kandidatenmatrix mit zulässigen Maßen und stabilen Vordergrund-IDs;
1–8 **tatsächlich verwendete** IDs mit jeweils opakem `#rrggbb` in sRGB.
Alle Zellen validieren; unbekannte ID, ungültiges RGB oder null verwendete Farben
sind Eingabefehler. Leer wird nicht als Farbe oder Paarpartner geprüft. Unbenutzte
Einträge getrennt melden, nicht in die Paarmenge aufnehmen; dies hebt Authorings
Bereinigungspflicht nicht auf. Gleiche RGB-Werte verschiedener verwendeter IDs
ergeben Abstand null und bleiben ein negatives Paar. Eine verwendete Farbe:
`positive`, Paarzahl 0, schlechtestes Paar/D null; Papierlesbarkeit weiter prüfen.

IDs nach ihrer bestehenden ASCII-Grammatik lexikografisch sortieren. Paare
`(i,j)` mit `i<j`, lexikografisch nach beiden IDs; bei acht Farben genau 28.
Keine Nutzungsgewichtung und kein Mittelwert. Für jeden 8-Bit-Kanal `v`:

```text
c = v / 255
linear(c) = c / 12.92                         falls c <= 0.04045
            ((c + 0.055) / 1.055) ** 2.4      sonst

(l,m,s) = M1 * (Rlinear,Glinear,Blinear)
(L,a,b) = M2 * (l ** (1/3), m ** (1/3), s ** (1/3))

M1 = ((0.4122214708, 0.5363325363, 0.0514459929),
      (0.2119034982, 0.6806995451, 0.1073969566),
      (0.0883024619, 0.2817188376, 0.6299787005))
M2 = ((0.2104542553, 0.7936177850,-0.0040720468),
      (1.9779984951,-2.4285922050, 0.4505937099),
      (0.0259040371, 0.7827717662,-0.8086757660))

q = round_half_even(1000000 * (L,a,b))         komponentenweise, ganze Zahlen
Sij = sum((qi[k] - qj[k]) ** 2 for k=0,1,2)   exakte Ganzzahlarithmetik
Dij = sqrt(Sij) / 10000                      nur Anzeige
```

Referenzarithmetik: Python `decimal` im lokalen Kontext Präzision 80,
`ROUND_HALF_EVEN`, Dezimalkonstanten aus den obigen Zeichenfolgen; Divisionen,
Potenzen und Einzeloperationen in diesem Kontext. Skalarprodukte von links nach
rechts mit Startwert Dezimal-0, kein FMA. Kubikwurzel als Potenz mit dem im
selben Kontext berechneten `1/3`; für 0 Ergebnis 0. Erst am Schluss komponentenweise
`to_integral_value(ROUND_HALF_EVEN)` für q. Keine vorzeitige Kürzung der
Matrixkonstanten. Eine alternative Implementierung muss diese q-Werte liefern;
die unabhängige binary64-Rechnung stimmt für sämtliche fixierten Eingangsfarben
überein, ist aber keine Zusage für ungeprüfte Rundungsrandfälle.
Die Koordinatenquantisierung präzisiert H1 um weniger als 0,0002 D; sie ändert
keinen der 47 Referenzpaarbefunde. Sie gehört ausdrücklich zur freigegebenen Regelversion.

| Exakter Vergleich, ohne Epsilon | Technischer Regelstatus nach P-B-Aktivierung |
| --- | --- |
| irgendein S < 10000000000 | `negative`; alle verletzten Paare ausgeben |
| kein negatives Paar, aber irgendein S < 22500000000 | `positive` mit `borderline`-Warnung und Liste dieser Paare |
| alle S >= 22500000000 oder genau eine Farbe | `positive`, keine Distanzwarnung |

Gleichheit an 10000000000 ist positiv mit Warnung, an 22500000000 positiv ohne
Distanzwarnung. Angezeigte gerundete D-Werte entscheiden niemals. Ein negativer
Gesamtbefund kann zusätzlich Warnpaare enthalten; keines verschweigen.
Kleinreferenzen: F02 q(c01) = `(547849,-38928,-65872)`,
q(c02) = `(561264,-38955,-65583)`; S = `180046475`.
Schwarz q = `(0,0,0)`. Reduzergleichheit separat mit q-Differenz `(100000,0,0)`
beziehungsweise `(150000,0,0)` prüfen; das sind künstliche Koordinatenproben,
keine behaupteten exakten sRGB-Farbpaare. Zusätzlich S direkt eine Einheit unter/
auf/über jeder Grenze prüfen. Diese endlichen Rechenproben sind einmalige
Akzeptanzbelege, keine neue permanente CI-Familie.

### 8.5 Ablauf, Bindung, Ausgabe und Freigabe

Frühprüfung bei Entwurfs-/Palettenauswahl darf vorläufige Farben verwenden;
ohne konkrete Matrix/Nutzung muss sie als vorläufig gekennzeichnet bleiben.
Finale Prüfung liest ausschließlich die endgültige Ist-Matrix und ihre tatsächlich
verwendete Palette. RGB, ID, Nutzung, Matrix oder Regelstand geändert: jede davon
abhängige positive Aussage ist veraltet und vollständig neu zu berechnen/binden.
Hinweise/Proof/Herkunft/Freigaben nach den bestehenden Fachverträgen neu prüfen,
nicht allein wegen eines guten Palettenwerts als gültig übernehmen.

Der aktuelle Bericht muss Regel-ID/Version und Normquellstand, Kandidaten-ID/
Revision, exakte Matrixbindung einschließlich Maße und Zellreihenfolge,
verwendete IDs/RGB/Nutzungszahlen, unbenutzte Einträge und getrennte Leerzahl binden.
Paarliste vollständig und kanonisch mit q/S/angezeigtem D; schlechtestes Paar
nach kleinstem S, Gleichstand nach Paarreihenfolge. Negativ- und Warnpaare nennen
IDs, Werte, genaue verletzte Regel und Korrekturmöglichkeit. Kein Globalmittel.
Visuelle Einzelurteile Q-R04/Q-H01/Q-H02 samt Ansichten/Stand separat binden.
Der [P-B1-Diagnosevertrag](../../tools/puzzle_production/README.md#diagnoseformat-picross-palette-assessment-v1)
konkretisiert Hash-/Berichts-/Readerbindung separat; geschlossene
Altformate erhalten dadurch keine neuen Pflichtfelder. Die aktuelle
Generationsbindung des getrennten äußeren Ausnahmerecords steht in
[PW-B · Palettenausnahme](../tools/PW_B_CONTRACT.md#palettenausnahme).

Vereinbarte Fehlersemantik für die P-B-Implementierung: `invalid_input` bei ungültiger Domäne/Bindung,
`aborted` bei Budget-/Prozessabbruch, `error` bei Rechen-/Dateifehler;
fehlende Prüfung `not_checked`. Keiner dieser Zustände ist `positive`.
Kein teilweise ausgewerteter Satz als vollständiges Ergebnis. Ein lokaler
Vergleich dieser Referenzen ist keine ausgeführte Produktionsprüfung.

| Technischer / visueller Stand | Konsequenz nach Aktivierung in P-B |
| --- | --- |
| positiv, visuell erfüllt, aktuelle technische Inhaltsgates vollständig | Im bestehenden Auswahlweg grundsätzlich freigabefähig; echte Endabnahme/Integration weiterhin getrennt. |
| positiv mit Warnung | Betroffene Paare in bestehenden Sicht-/Endabnahmen gezielt beurteilen und Entscheidung belegen. Kein automatisches Ablehnen oder automatisches visuelles Bestehen. |
| positiv, Q-H01/Q-H02 visuell nicht erfüllt | Korrektur oder konkret gebundene redaktionelle Entscheidung nach §6; kein `content_ready` allein aufgrund des Messwerts. |
| negatives Paar, auch wenn das Bild gefällt | Überarbeiten/kleinere Palette/neue motivtreue Variante oder als `Sichtungsentwurf – nicht integrationsbereit` zeigen. Kein Umbenennen in `pass`. |
| negatives Paar plus ausdrückliche Eigentümerausnahme | Befund bleibt negativ. Übernahme über den von P-B2 implementierten/geprüften revisions- und paargebundenen Ausnahmeweg plus alle unveränderten harten Inhaltsgates. Keine Freitext-Umgehung. |
| fehlender Proof, ungeklärte Rechte oder stale/fehlende Bindung | Technischer Blocker unabhängig von Farbe oder redaktioneller Annahme; Diagnose-Sichtung möglich, kein freigabefähiges Sheet-Angebot. |

Ausnahmebindungen folgen §6 einschließlich Regelversion, konkreten Farbpaaren,
aktuelle Kandidaten-/Palettenbindung, Begründung, Akteur und UTC-Zeitpunkt.
Das technische Negativurteil und die separate Annahme bleiben beide sichtbar.
Keine zusätzliche allgemeine Freigabeschleife oder Pflicht-Probespielrunde.

## 9. Hintergrundzeichnungen

Aktueller Produktionsweg: [Schritt 4](authoring/PUZZLE_AUTHORING_STEP_4.md).
Gestalterische Norm: [BACKGROUND](images/BACKGROUND.md).
Technische Arbeits-/Entscheidungs-/Ableitungsformen:
[PUZZLE_BACKGROUNDS](PUZZLE_BACKGROUNDS.md). Eine Werkzeuglieferung ist keine
Bildproduktion, ausgeführte Sichtung oder menschliche Entscheidung.

### 9.1 Isolierte visuelle Beurteilung

Jedes Urteil verwendet die Ergebniswörter aus §2, nennt Befund und Methode
und bindet Regelstand, Kandidat, Bildrevision, tatsächlich betrachtete Datei/Hash,
Prüfer und Zeitpunkt. Die Kontextgrenze und tatsächlichen Datei-/Freigabebindungen
des Hintergrundvertrags bleiben Voraussetzungen; eine redaktionelle Annahme
ersetzt sie nicht.

| Kriterium | Gestalterische Norm | Gegenstand und Zeitpunkt der isolierten Sichtung |
| --- | --- | --- |
| Q-HG01 · Kontext statt Rätselsubjekt | [HG-01](images/BACKGROUND.md#hg-01-kontext) | Vor Auswahl jede Datei mit Briefing, freigegebenem Abschlussbild und geschützten Merkmalen vergleichen; Kontextgrenze tatsächlich beurteilen. |
| Q-HG02 · Helle Graphitzeichnung | [HG-02–HG-03](images/BACKGROUND.md#hg-02-beiläufige-handskizze), [HG-08](images/BACKGROUND.md#hg-08-stilbezogene-korrektur) | Vor Auswahl am Original Skizzencharakter, Striche, Schraffur und Helligkeit beurteilen. Leitfrage: beiläufige gekonnte Skizze oder professionell fertig ausgearbeitete Graphitzeichnung? Technische Korrektheit oder Schönheit ersetzt dieses Urteil nicht. |
| Q-HG03 · Luftige gemeinsame Komposition | [HG-05–HG-07](images/BACKGROUND.md#hg-05-ganze-leinwand) | Vor Vorlage tatsächliche PNG-Maße aus den Bytes lesen und binden; Gesamtleinwand, Breitenverteilung, geplante Positionen und vier Bildkanten ansehen. Nach Ableitung Maße, erhaltene Komposition und Strichqualität am fertigen Bild erneut prüfen. H-07 bleibt hart; HG-07 bleibt unverbindlich. |
| Q-HG04 · Echte Transparenz und saubere Striche | [HG-04](images/BACKGROUND.md#hg-04-transparenz), [HG-06](images/BACKGROUND.md#hg-06-randabschluss) | Vor Auswahl, nach materieller Änderung und am fertigen Ableitungsbild freie Außen-/Zwischenräume, feine Striche, Säume und tatsächlich erreichte Kanten sichten; bei Bedarf neutrale Prüfgründe/Transparenzraster verwenden. Alpha-Zählungen allein genügen nicht. |

Einen Mangel mit gezieltem Korrekturvorschlag benennen. Keine positive
Dateidiagnose als Ersatz für ein ausstehendes oder negatives Bildurteil verwenden.
Der harte Randabschluss H-07 darf nicht als Q-HG03-/Q-HG04-Abweichung angenommen
werden. Hintergrundbereitschaft und zulässige `accepted_deviations` folgen
[Hintergrundtechnik §3.4](PUZZLE_BACKGROUNDS.md#34-effektiver-zustand-und-referenzgraph).

### 9.2 Technische Diagnose und Entscheidung

Datei-, Format-, Maß-, Hash- und Alphadiagnosen betreffen gespeicherte Bytes.
Sie beweisen weder visuelle Qualität, Herkunft/Rechte noch eine tatsächliche
Bildwahl. Ein lokaler PNG-Befund ist kein Nachweis von Engineimport oder Mipmaps.

- Technische Prüfung und Nullbefund: [Hintergrundtechnik §4](PUZZLE_BACKGROUNDS.md#4-hp-w2-eigenständige-datei--und-ableitungsschnittstelle).
- Kandidatenvorlage, Wahl/none, Korrektur und Übergabe: [Schritt 4](authoring/PUZZLE_AUTHORING_STEP_4.md).
- Materielle Änderung und Wiederverwendung unveränderter Nachweise: [Schritt 3 §4.4](authoring/PUZZLE_AUTHORING_STEP_3.md#44-reparaturen-und-änderungen).
- Integration und Abschluss: [Schritt 5](authoring/PUZZLE_AUTHORING_STEP_5.md).

Die gemeinsame Sichtmethode steht in §2.1; die vier Hintergrundkriterien
benötigen keine zusätzliche Darstellungs- oder persönliche Abnahmeschleife.
