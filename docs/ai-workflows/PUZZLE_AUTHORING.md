# Picross: Produktionsregeln

**Version 0.8.0 · Dokumentrevision 9 · 16.11.2026 · RI-ONE**

## 1. Einstieg und Befugnisse

### 1.1 Pflichtquellen nach Phase

Für normale Produktion: Produktionseinstieg der aktuellen [AGENTS.md](../../AGENTS.md),
diesen gemeinsamen Kern vollständig und den vollständigen [Bildstil](../PUZZLE_IMAGE_STYLE.md)
lesen; danach die beauftragte Phasendatei. Deren benannte
Qualitätsabschnitte sind Pflicht. Querverweise lösen keine rekursive Volllektüre aus.

| Schritt | Phasendatei |
| --- | --- |
| 1 · Abschlussbilder | [Schritt 1](PUZZLE_AUTHORING_STEP_1.md) |
| 2 · Motivvorlage | [Schritt 2](PUZZLE_AUTHORING_STEP_2.md) |
| 3 · Rasterangebote | [Schritt 3](PUZZLE_AUTHORING_STEP_3.md) |
| 4 · Kontextzeichnungen | [Schritt 4](PUZZLE_AUTHORING_STEP_4.md) |
| 5 · Abschluss/Integration | [Schritt 5](PUZZLE_AUTHORING_STEP_5.md) |

Korrektur/Wiederaufnahme: tatsächliche Phase lesen, gültige Entscheidungen und
verbrauchte Budgets fortführen; bei geänderten Bytes zusätzlich
[Änderungsregeln §4.4](PUZZLE_AUTHORING_STEP_3.md#44-reparaturen-und-änderungen).
Nur Abhängiges erneuern. Integrierte Bildrevisionen/Retirement
folgen ihrem eigenen [Schritt-5-Weg](PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung).

Vor technischer Benutzung zusätzlich Referenz lesen:

| Operation | Pflichtquelle |
| --- | --- |
| Paketbau/Veröffentlichung | [PW-B](../PW_B_CONTRACT.md), Tool-README PW-B/PB-A, unten §6 |
| Rasterimport/Endproof | Tool-README RP-3, Datenvertrag/Ressourcen; [Produktion](../PUZZLE_PRODUCTION.md) §§4–5 |
| Paarprofil | [PAIRED_LINES](../PAIRED_LINES.md) vollständig; Tool-README Paarlinienprofil; kein Routinepaarlauf bei gelöster Linienlogik |
| Feste Korrektur/RP-5 | [FIXED_RASTER](../FIXED_RASTER.md) bzw. Tool-README RP-5; Schritt 3 §4.4 und benutzter Ableitungsvertrag |
| Difficulty/Rebind | [SD2-Integration](../SD2_INTEGRATION.md), Tool-README SD2-C/SD2-B; Analyse-/Bewertungsvertrag nach tatsächlichem Befehl |
| Hintergrundableitung | [Hintergrund](../PUZZLE_BACKGROUNDS.md) §4, Tool-README HP-W2; nur gewähltes Original |
| Export/Plan/Register/Recovery | [RI](../PUZZLE_INTEGRATION.md), aktuelles [ZA-1](../ZA1_ADAPTER.md), entsprechende CLI-Anleitung, Schritt 5 §8 |
| Retirement/Bildrevision | Schritt 5 §9 und dort gerouteter revisionsgenauer Zielvertrag |

[Tool-README](../../tools/puzzle_production/README.md), PW/ZA-1/Produktion,
Produktdefinition/Gestaltung und historische Lieferberichte nicht pauschal voll lesen.
Felder/Grenzen nie erraten; fehlende Quellen/Widersprüche blockieren nur
abhängige Operationen. Vorhandene Arbeitsoriginale und Freigaben bleiben bytegleich. Alt-WIP ist kein
Kompatibilitätsziel; keine automatische WIP-Migration. Integration benutzt
ausschließlich den aktuellen Eingang nach RI-ONE. Neue Rev9-Snapshots:
[PW-B](../PW_B_CONTRACT.md#pw-perf-d--regelquellen-und-snapshotgeneration).
Regeln/Stil/Fachquellen vom selben vollen Quellcommit lesen. Separate Entwicklung
an Regeln/Werkzeugen/Spiel/CI folgt vollständig AGENTS.

### 1.2 Gemeinsame Arbeitsregeln

Zu Beginn Kategorienquelle/Arbeitsindex/Runtime-Registry lesen, keine Bestandsrätsel
laden/nachprüfen. Kategorie nach Auftrag/Hauptgegenstand gemäß [Kategorien](../CATEGORIES.md)
im Briefing/Record führen.
Repository-/Toolstand mit voller SHA binden; Datei-/Bild-/Repository-/Ausführungszugriff
prüfen. Nur verfügbare Originale/Fähigkeiten und ausgeführte Prüfungen/Erfolge melden. Bestehende Formate, Farbregeln, Solverprofile,
Nachweise und Reparaturverträge benutzen; normale Produktion entwickelt keine Tools
oder direkte Modell-API. MODEL_SELECTION/MODEL_CATALOG weder laden noch dafür
recherchieren; keine Modell-/Reasoning-/Eigenumsetzungsempfehlung. Fehlende nötige Fähigkeiten als Blocker melden.

Repositoryauftrag erlaubt beauftragte Paketsicherung samt Index; Integrationsauftrag
zusätzlich Schritt 5 §§8–9. Ablage-/Integrationsmerge braucht passende ausdrückliche
oder bedingte Freigabe; bestehende passende Aufträge nicht erneut erfragen. Kein
direktes Schreiben auf main, keine fremden Änderungen, ungeklärten Fremdassets,
Secrets oder privaten Daten übernehmen. Beauftragte Arbeitswurzel und
[WORKSPACE](../dev-rules/WORKSPACE.md) vor lokaler Ablage/Bereinigung lesen.

Probespiel ist optional; echte Bild-/Motiv-/Parameter-/Raster-/Hintergrundentscheidung
und Endabnahme am Gegenstand bleiben Pflicht. Empfehlung/Datei/Klick/Kopieren/
Aktualisierung/Schweigen geben nichts frei, Korrekturwünsche keine künftigen Bytes.
Materielle kreative Änderungen verlangen passende neue Entscheidungen.

### Prüfungen gehören zur Produktion, nicht zur CI

Lösbarkeit/Eindeutigkeit, unabhängigen Proof, Herkunft, Reparatur, Gestaltung und
Zielintegration revisionsgebunden tatsächlich prüfen; unveränderte passende Belege
wiederverwenden (Schritt 3 §4.4). Keine rätselspezifischen Unit-Tests/Snapshots/
CI-Falllisten/Dauerreplays; Auftragsskripte temporär außerhalb Discovery, Ergebnisse
im Paket. Vor Inhalts-/Ablage-/Cleanup-PR [CI v2](../CI_WORKFLOW_V2.md) Paketplan/
buildfreie Klassen lesen: aktueller `.ci/package.json`, begründet `modules=[]`,
`evidence.mode=none`, Quellen-/Plankern ohne Player auch nach main. Keine Fach-/
Solver-/Proof-/native Volltests allein für neue Rätsel. Code, gemeinsame Spielassets
und CI folgen Entwicklungsprüfplan, keine Inhaltsausnahme oder manuelles `all`.

## 3. Gesamtfolge

Revealwahl → Motiv-/Parameterfreigabe → qualifizierte Raster → Rasterwahl → drei
Kontexte/Wahl oder none → Endabnahme → Finalizer → Export → frischer Plan →
autorisiertes Register → Git/Draft-PR → bestätigtes main → Schritt 5 §9.
PW2-B verbindet Hintergrundwahl/none, Endabnahme und Integration samt Commit/PR,
unabhängigem Review und bedingtem Squash-Merge nach aktuellen Vor-Merge-Gates/§9.
Ausdrücklicher Draftumfang bleibt. Erst Absenden erklärt Rechte, Gitdaten belegen Erfolg.

## Darstellungen und Sichtung

Ursprungsidee/Bildquelle bindet Auftrag/Referenz, Original, Herkunft und Nutzungsgrundlage.
Abschlussbild: zuerst erzeugte farbige detaillierte Illustration, nach echter
Wahl/Freigabe gestalterische Referenz/Belohnungsansicht. Motivvorlage ist die
vereinfachte Ableitung genau daraus mit eigener Motiv-/Parameterfreigabe vor Rasterarbeit.
Das exakte diskrete Lösungsraster allein bestimmt Hinweise/Logik. Hintergrund bleibt
eigener Kontext mit eigener Bildrevision/Wahl und liefert keine Lösungszellen.
Input → Reveal → freigegebene Abstraktion → Raster ist verbindlich; motivische Konsistenz,
keine Pixelidentität. Dateien/Revisionen trennen, detailliertes Original nie überschreiben.

[Q-B02/Q-B03](../PUZZLE_QUALITY.md#31-abschlussbildphase)
und [AT §2](../REVEAL_TRANSPARENCY.md#2-verbindlicher-bildstandard) behalten Einzelurteile,
echte Transparenz, helle Motivteile, saubere Alphakanten und notwendige Szenenumgebung
mit bewusster transparenter Außenkomposition. Originale direkt groß/klein, bei Bedarf neutral/auf Schachbrett ansehen; keine
Routine-Buch-/Katalogmontage, Fadeprobe oder Testintegration, auch nicht später. Je fälligem Kriterium erfüllt/Warnung/nicht erfüllt/nicht geprüft mit Grund/Datei/Revision
binden; Gesamteindruck verdeckt kein Negativurteil. Q-H01/Q-H02 brauchen echte Zell-/Hinweissicht,
keinen obligatorischen Spielstart. Matrixwerte bleiben diskret; Textur/Zwischenfarben
sind keine Zellzustände, Revealtransparenz ändert weder EMPTY noch weiße Vordergrundfarbe.

## Gemeinsame Bildkorrektur

Nur gewählte Darstellung korrigieren; ausgenommen ist die eigenständige
[Format- und dadurch nötige Kompositionskorrektur laufender Hintergrundkandidaten](PUZZLE_AUTHORING_STEP_4.md#631-formatkorrektur-vor-der-bildwahl),
die bereits vor der Bildwahl zum Produktionsauftrag gehört, einschließlich
gezielter zeichnerischer Erweiterung oder passender Neugenerierung im bestehenden
Bildkorrekturbudget. Zulässige schraffierte Objektflächen sind allein kein
Korrekturgrund; bloßes transparentes Seitenpadding behebt kein falsches Format.
Schutzmerkmale nennen, neue Revision sichern. Nach zwei erfolglosen Bildkorrekturrunden
Ursache/geänderten Plan vorlegen.
Ungeeignete Abstraktion: Vereinfachung/Größe/Palette überdenken; anderes Reveal neu
freigeben, nie technischen Fehlschlägen anpassen. Materielles/Neuprüfungen: Schritt 3 §4.4.

## 6. Dateien, Übergabe und Wiederaufnahme

### 6.1 Repositoryablage während der laufenden Produktion

Neue pz-ID und stabilen Branch `content/pw/<puzzle_id>` von main anlegen; alle
Phasen/Varianten/Korrekturen/Wiederaufnahmen bleiben dort. Index/Kollisionen prüfen,
fremde Arbeit erhalten. Jede Übergabe bekommt vollständige Einzelrevision unter
`content/authoring/<puzzle_id>/<revision>/` und Arbeitsindexeintrag.
Unversiegelten Request v4/Handoff v5 mit expliziter Dateiliste und geschlossenem
Rev9-Snapshot nach PW-B/PB-A verwenden:

```text
python -m tools.puzzle_production.authoring_builder build --request <request-v4.json> --source-root <vorbereitete-dateien> --output-root <eigene-arbeitswurzel> --publish-to <produktionscheckout> --history-repo <produktionscheckout>
```

Builder validiert Quellen und geschriebenen ZIP, erzeugt Inventar v1, bytegleiche
Handoffkopie, Record v4 und geprüfte workspace.json. [Ansichtsverweis](../PRODUCTION_CURRENT_VIEW.md)
bindet genau diese Übergabe; Finalizer/Completion führen ihn auch In-place nach.
Frühphasen sind keine Zertifikate. raster_ready/spätere Inhaltsphasen frisch prüfen.
Presentation enthält tatsächliche Angebote; weitere Raster binden bereits gesicherte
qualifizierte Einzelrecords. Keine erfundene Galerie oder HTTP-Projektwriter.

Alle nötigen Originale einschließlich sichtbarer Alternativen, Index, Projektion
und Ansichtsverweis committen/pushen, feste Remote-Commit-/Dateipfade wirklich prüfen.
Sicherungscommit erst nach Erfolg melden; repo_commit ist gelesene Herkunft,
kein Sicherungsbeleg. Lokale Pfade/localhost/ungesicherte SHAs sind keine Cloudquelle.
Neuere Quellen ausdrücklich laden; passive Suche erhält Ansicht/Eingaben,
Job-/Quellwechsel verwirft Auswahlabsichten. Wiederaufnahme prüft aktuelle Quellen,
gültige Freigaben, verbrauchte Budgets und offene Arbeit ohne historische Wiederholung.

### 6.2 Übergabedatensatz

[PW-B](../PW_B_CONTRACT.md) schließt Request v4/Handoff v5/Record v4/Resultat v4;
Rasterwahl, Inspektion v2, Projektion v2, Inventar/Index v1 und technische Bild-/
Proof-/Freigabeformen bleiben. Früh background/raster_selection null, beide
Hintergrundgates pending und Belege null; null ist kein none. Erst background_review/
content_ready besitzen Hintergrundarbeit und qualifizierte Rasterwahl.
Registered erst nach Registrierung, main nach bestätigtem Merge melden.
Originale nie umetikettieren/neu versiegeln. Konflikte, Restpfade und Teilpublikation
offen melden. Nur vollständig geprüft identische Wiederholung ist No-op;
keine pauschale Locklöschung/verdeckte Recovery.

## 7. Freigaben und Abschlussausgabe

Jede Chatübergabe nennt erreichte Phase, feste Quelle, ausgeführte Prüfungen,
offene Entscheidung/nächsten Schritt, echte Bild-/Dateilinks und stabile Angebots-IDs.
Der Assistent liest veröffentlichte Originale; keine zweite Sheet-JSON-Sammlung
oder Entwicklungs-HANDOFF-Ausgabe. Software prüft Aufzeichnungen/Bytes, authentifiziert keine Menschen.
Arbeitswurzel/Merge sind ausdrückliche Auftragsoptionen, keine
Recordrechte. Produktionsprompts beauftragen keine lokale Zusatzbereinigung;
separater Auftrag nach WORKSPACE, fachlicher Schritt-5-§9-Abschluss bleibt.
Neue Briefingentwürfe behaupten keine ID/Quelle/Freigabe; spätere eigene
Hintergrundrevisionen benutzen HP-I1b2, keinen Alt-Sheet-Sitzungsimport.
