# Picross: Produktionsregeln

**Version 0.8.0 · Dokumentrevision 13 · 23.11.2026 · PW-LOCAL-Spezifikation**

## 1. Einstieg und Befugnisse

### 1.1 Pflichtquellen nach Phase

Für normale Produktion: Produktionseinstieg der aktuellen [AGENTS.md](../../../AGENTS.md),
diesen gemeinsamen Kern und [Bildverträge](../images/README.md) vollständig
lesen. Danach die beauftragte Phasendatei und die zugeordneten Bildnormen lesen.
Deren benannte Qualitätsabschnitte sind Pflicht; Querverweise lösen keine
rekursive Volllektüre aus.

| Schritt | Ablaufquelle | Gestalterische Pflichtquelle |
| --- | --- | --- |
| 1 · Abschlussbilder | [Schritt 1](PUZZLE_AUTHORING_STEP_1.md) | [REVEAL](../images/REVEAL.md) |
| 2 · Motivvorlage | [Schritt 2](PUZZLE_AUTHORING_STEP_2.md) | [MOTIF](../images/MOTIF.md); das gewählte Reveal als Originalreferenz |
| 3 · Rasterangebote | [Schritt 3](PUZZLE_AUTHORING_STEP_3.md) | [RASTER](../images/RASTER.md); freigegebene Motivvorlage und Reveal als Originalreferenzen |
| 4 · Kontextzeichnungen | [Schritt 4](PUZZLE_AUTHORING_STEP_4.md) | [BACKGROUND](../images/BACKGROUND.md) |
| 5 · Abschluss/Integration | [Schritt 5](PUZZLE_AUTHORING_STEP_5.md) | Vorhandene gültige Bildurteile verwenden; bei neuer Sichtung die betroffene Bildtypnorm lesen |

Korrektur/Wiederaufnahme: tatsächliche Phase lesen, gültige Entscheidungen und
verbrauchte Budgets fortführen; bei geänderten Bytes zusätzlich
[Änderungsregeln §4.4](PUZZLE_AUTHORING_STEP_3.md#44-reparaturen-und-änderungen).
Nur Abhängiges erneuern. Integrierte Bildrevisionen/Retirement
folgen ihrem eigenen [Schritt-5-Weg](PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung).

Vor technischer Benutzung zusätzlich Referenz lesen:

| Operation | Pflichtquelle |
| --- | --- |
| Befundannahme, Behandlung, Widerruf und Fortführung auf Nachfolger | [Qualität §6 einschließlich §6.1](../PUZZLE_QUALITY.md#6-gezielte-redaktionelle-einzelfallentscheidung); für die Umsetzung im aktuellen Job zusätzlich unten §6.3 |
| Paketbau/Veröffentlichung | [PW-B](../../tools/PW_B_CONTRACT.md), Tool-README PW-B/PB-A, unten §6 |
| Rasterimport/Endproof | Tool-README RP-3, Datenvertrag/Ressourcen; [Produktion](../PUZZLE_PRODUCTION.md) §§4–5 |
| Paarprofil | [PAIRED_LINES](../PAIRED_LINES.md) vollständig; Tool-README Paarlinienprofil; kein Routinepaarlauf bei gelöster Linienlogik |
| Feste Korrektur/RP-5 | [FIXED_RASTER](../FIXED_RASTER.md) bzw. Tool-README RP-5; Schritt 3 §4.4 und benutzter Ableitungsvertrag |
| Difficulty/Rebind | [SD2-Integration](../../difficulty/SD2_INTEGRATION.md), Tool-README SD2-C/SD2-B; Analyse-/Bewertungsvertrag nach tatsächlichem Befehl |
| Hintergrundableitung | [Hintergrund](../PUZZLE_BACKGROUNDS.md) §4, Tool-README HP-W2; nur gewähltes Original |
| Export/Plan/Register/Recovery | [RI](../PUZZLE_INTEGRATION.md), aktuelles [ZA-1](../ZA1_ADAPTER.md), entsprechende CLI-Anleitung, Schritt 5 §8 |
| Retirement/Bildrevision | Schritt 5 §9 und dort gerouteter revisionsgenauer Zielvertrag |

[Tool-README](../../../tools/puzzle_production/README.md), PW/ZA-1/Produktion,
Produktdefinition/Gestaltung und historische Lieferberichte nicht pauschal voll lesen.
Felder/Grenzen nie erraten; fehlende Quellen/Widersprüche blockieren nur
abhängige Operationen. Aktuelle gewählte Ergebnisse und echte Entscheidungen erhalten. Verworfene oder
ersetzte Dateien nach ihrer letzten aktuellen Nutzung entfernen; kein Archiv,
Regelbuchsnapshot, Erzeuger-/Normalisierungs-/Reparaturreplay als Zulassung.
Der geschlossene aktuelle Datenvertrag steht in [PW-B](../../tools/PW_B_CONTRACT.md).
Separate Entwicklung
an Regeln/Werkzeugen/Spiel/CI folgt vollständig AGENTS.

### 1.2 Gemeinsame Arbeitsregeln

Zu Beginn Kategorienquelle/Arbeitsindex/Runtime-Registry lesen, keine Bestandsrätsel
laden/nachprüfen. Kategorie nach Auftrag/Hauptgegenstand gemäß [Kategorien](../../game/CATEGORIES.md)
im Briefing/Record führen.
Aktuellen Quellenstand mit voller SHA zuordnen; Datei-/Bild-/Repository-/Ausführungszugriff
prüfen. Nur verfügbare Originale/Fähigkeiten und ausgeführte Prüfungen/Erfolge melden. Bestehende Formate, Farbregeln, Solverprofile,
Nachweise und Reparaturverträge benutzen; normale Produktion entwickelt keine Tools
oder direkte Modell-API. MODEL_SELECTION/MODEL_CATALOG weder laden noch dafür
recherchieren; keine Modell-/Reasoning-/Eigenumsetzungsempfehlung. Fehlende nötige Fähigkeiten als Blocker melden.

Repositoryauftrag erlaubt beauftragte Paketsicherung samt Index; Integrationsauftrag
zusätzlich Schritt 5 §§8–9. Ablage-/Integrationsmerge braucht passende ausdrückliche
oder bedingte Freigabe; bestehende passende Aufträge nicht erneut erfragen. Kein
direktes Schreiben auf main, keine fremden Änderungen, ungeklärten Fremdassets,
Secrets oder privaten Daten übernehmen. Beauftragte Arbeitswurzel und
[WORKSPACE](../../dev-rules/WORKSPACE.md) vor lokaler Ablage/Bereinigung lesen.

Bei normaler Rätsel-Erstintegration bezeichnet Review die fachliche unabhängige
Proofprüfung und die eigene Kontrolle des vollständigen PR-Diffs. Kein unabhängiges
GitHub-PR-Zweitreview und kein Copilot-Review anfordern. Keine Reviewer-Konten oder
Zustimmung zur Weitergabe des PR-Inhalts verlangen. Die Regeln für zusätzliche
persönliche Prüfaufträge und tatsächliche GitHub-Mergesperren stehen in
[Schritt 5 §8](PUZZLE_AUTHORING_STEP_5.md#8-abgenommenes-ergebnis-ins-spiel-integrieren).

Probespiel ist optional; echte Bild-/Motiv-/Parameter-/Raster-/Hintergrundentscheidung
und Endabnahme am Gegenstand bleiben Pflicht. Empfehlung/Datei/Klick/Kopieren/
Aktualisierung/Schweigen geben nichts frei, Korrekturwünsche keine künftigen Bytes.
Materielle kreative Änderungen verlangen passende neue Entscheidungen.

### Prüfungen gehören zur Produktion, nicht zur CI

Lösbarkeit/Eindeutigkeit, unabhängigen aktuellen Proof, Nutzungsgrundlage, Gestaltung und
Zielintegration revisionsgebunden tatsächlich prüfen; unveränderte passende Belege
wiederverwenden (Schritt 3 §4.4). Keine rätselspezifischen Unit-Tests/Snapshots/
CI-Falllisten/Dauerreplays; Auftragsskripte temporär außerhalb Discovery, nur aktuell benötigte Ergebnisse im Arbeitsstand. Vor Inhalts-/Ablage-/Cleanup-PR [CI v2](../../ci/CI_WORKFLOW_V2.md) Paketplan/
buildfreie Klassen lesen: aktueller `.ci/package.json`, begründet `modules=[]`,
`evidence.mode=none`, Quellen-/Plankern ohne Player auch nach main. Keine Fach-/
Solver-/Proof-/native Volltests allein für neue Rätsel. Code, gemeinsame Spielassets
und CI folgen Entwicklungsprüfplan, keine Inhaltsausnahme oder manuelles `all`.

## 3. Gesamtfolge

Revealwahl → Motiv-/Parameterfreigabe → qualifizierte Raster → Rasterwahl → drei
Kontexte/Wahl oder none → Endabnahme → Finalizer → Export → frischer Plan →
autorisiertes Register → Git/Draft-PR → bestätigtes main → Schritt 5 §9.
PW2-B verbindet Hintergrundwahl/none, Endabnahme und Integration samt Commit/PR,
unabhängiger Proofprüfung und vollständigem Diff-Selbstreview. Bei grünen
Pflichtchecks, Konfliktfreiheit, gebundener Endabnahme und passender Mergebefugnis
direkt per Squash-Merge integrieren. Die normale Abschlusskette läuft ohne
Zweitreviewer, Copilot-Anfrage oder Weitergabe des PR-Inhalts an Copilot.
Nach bestätigter autorisierter Integration führt der Akteur den gebundenen
Abschluss samt Branch, Arbeitsrelease und Tag direkt nach Schritt 5 §9 aus.
Ausdrücklicher Draftumfang bleibt. Erst Absenden erklärt Rechte, Gitdaten belegen Erfolg.

## Darstellungen und Sichtung

Das aktuelle Briefing bindet Auftrag/aktive Referenz, gewählte Ergebnisse und
tatsächlich erforderliche Nutzungsgrundlagen. Die Gegenstände und gestalterischen Zuständigkeiten definiert
[Bildverträge IMG-03](../images/README.md#img-03-gegenstände-und-geltung).
Input → freigegebenes Reveal → freigegebene Abstraktion → Raster bleibt die
verbindliche Produktionsfolge; der Hintergrund ist ein eigener Auswahlgegenstand.

Einzelurteile, Belegbindung und Sichtmethoden folgen den für die Phase gerouteten
[Qualitätsabschnitten](../PUZZLE_QUALITY.md). Prompt, Hash oder Toolerfolg ersetzen
keine tatsächliche Sichtung. Q-H01/Q-H02 brauchen echte Zell-/Hinweissicht, keinen
obligatorischen Spielstart. Rendertransparenz ändert weder EMPTY noch eine weiße
Vordergrundfarbe.

## Gemeinsame Bildkorrektur

Nur gewählte Darstellung korrigieren; ausgenommen ist die eigenständige
[Format- und dadurch nötige Kompositionskorrektur laufender Hintergrundkandidaten](PUZZLE_AUTHORING_STEP_4.md#631-formatkorrektur-vor-der-bildwahl),
die bereits vor der Bildwahl zum Produktionsauftrag gehört, einschließlich
gezielter zeichnerischer Erweiterung oder passender Neugenerierung im bestehenden
Bildkorrekturbudget. Ob ein Bildmangel besteht, bestimmt ausschließlich die
zuständige Bildtypnorm mit den zugehörigen Qualitätskriterien.
Schutzmerkmale und aktuellen korrigierten Kandidaten sichern; ersetzte Fassungen
nach Ende ihrer aktuellen Nutzung entfernen. Nach zwei erfolglosen Bildkorrekturrunden
Ursache/geänderten Plan vorlegen.
Ungeeignete Abstraktion: Vereinfachung/Größe/Palette überdenken; anderes Reveal neu
freigeben. Die Grenzen einer Revealänderung stehen in
[RV-02](../images/REVEAL.md#rv-02-illustration).
Materielles/Neuprüfungen: Schritt 3 §4.4.

## 6. Dateien, Übergabe und Wiederaufnahme

### 6.1 Ein aktueller Arbeitsstand

Das freigegebene Soll für die lokale Ablage steht in
[PW-LOCAL](../../tools/PRODUCTION_GIT_WORKSPACE.md): gemeinsame Git-Datenbank,
stabiler Worktree je Rätsel und Sparse-Materialisierung. Umsetzung und Abnahme
sind in [#859](https://github.com/venomenon328/picross/issues/859) noch offen;
dieser Verweis behauptet keinen bereits verfügbaren Helfer.

Neue pz-ID und stabilen Arbeitsbranch `content/pw/<puzzle_id>` von main anlegen.
Je Job genau `content/authoring/<puzzle_id>/current/record.json` und die aktuell
benötigten Nutzdateien nach [PW-B](../../tools/PW_B_CONTRACT.md) führen. Der
Arbeitsindex enthält nur Verweise. Ansichten und Folgeaufträge werden direkt
daraus abgeleitet, keine zusätzliche Handoff-/Inventar-/workspace-/Pointerdatei.
Vorhandene aktive Referenzbilder sicher referenzieren, nicht je Job kopieren.

Der Akteur übergibt `picross-authoring-current-request-v1` an den bestehenden
Builder: `build --request ... --source-root ... --output-root ... --publish-to ...`.
Er verwendet aktuelle Ergebnisse und echte Erklärungen. Kein Benutzer muss JSON
pflegen. Builder und Finalizer prüfen dieselbe geschlossene Form, aktuellen Proof,
Dateien, Phase und Entscheidungen; sichere Pfade, Lock, atomare Publikation,
Konfliktschutz und identische Wiederaufnahme bleiben wirksam. Ein temporäres
Operationsjournal endet nach Abschluss des Aufrufs.

### 6.2 Auswahl und Wiederaufnahme

Aktuell angebotene Alternativen bleiben bis zur tatsächlichen Wahl erreichbar.
Danach ausgeschiedene Varianten und ausschließlich zugehörige Hilfsdateien
entfernen, sobald keine aktuelle Nutzung mehr besteht. Kein Archivieren und
keine Wartepflicht auf Main. Gewählte Bilder/Raster/Proofs nur so lange erhalten,
wie die aktuelle Phase sie braucht; wiederverwendete Dateien nicht duplizieren.

Die im abgesendeten Auftrag ausdrücklich erklärte, aktuelle und eindeutig an
Kandidaten-ID sowie unveränderte Originalbytes/Revision gebundene Wahl umfasst
die anschließende Entfernung der dadurch ausgeschiedenen, nachweislich nicht
mehr benötigten eigenen Alternativen samt exklusiver Hilfsdateien und
Arbeitsrelease-Assets. Für diese gebundene Bereinigung bei Reveal, Motiv, Raster
oder Hintergrund keine zweite menschliche Freigabe, Löschbestätigung oder
Rückfrage verlangen. Ein bloßer Klick, das Kopieren oder ein unabgesendeter
Entwurf sind keine Wahl. Unklare Eigentums- oder Referenzbindung sperrt nur die
betroffene Löschung; fremde und weiterhin benötigte Originale bleiben erhalten.
Ein Bereinigungsfehler setzt die gültige Auswahl unveränderter Bytes nicht
zurück. Nach gesicherter Fortschreibung denselben Stand technisch fortsetzen,
ohne die Bild- oder Rasterentscheidung erneut einzufordern.

Keine Prompts, Seeds, Such-/Reparaturverläufe, Ablehnungs- oder Korrekturhistorie
aufbewahren oder rekonstruieren. Temporäre Laufdaten sind erlaubt, ihr Fortbestand
ist nach Vorliegen des aktuellen Ergebnisses keine Voraussetzung. Suchbudgets
bleiben begrenzt; Wiederaufnahme setzt sie nicht zurück und verlangt kein
Versuchstagebuch. Aktuelle offene Blocker und noch relevante Entscheidungen
kompakt im Record führen; fehlende Erklärungen niemals erfinden.

Den [lesenden Publisher-Preflight](../../tools/PW_B_CONTRACT.md#bau-auswahl-und-sichere-fortschreibung) vor Originalabruf, Finalizer oder großem Checkout mit der erwarteten SHA und vorgesehenen Authquelle aufrufen. Den Arbeitsstand mit `python -m tools.work_publish publish <id> --expected <new-oder-arbeitscommit>` und derselben Authquelle sichern. Der Publisher liefert Originale als Releaseassets und den Record mit Index im Arbeitsref. Feste Remotequelle tatsächlich prüfen. Ungesicherte lokale Dateien
sind keine Cloudquelle. Wiederaufnahme prüft aktuelle Dateien, Freigaben,
Parameter und offene Arbeit. Reine Pfadumstellung gleicher Bytes erhält die
Auswahl; materiell geänderte Inhalte invalidieren abhängige Freigaben.

Integration erhält einen eigenen sauberen Branch vom aktuellen Main und übernimmt
nur gewählte finale Produktdaten und wirklich benötigte aktive Metadaten. Der
Arbeitsbranch mit Alternativen wird nicht nach Main gemergt. Abschluss prüft das
tatsächliche aktuelle Ergebnis. Der gültige Mainkatalog blendet registrierte
IDs dauerhaft im Produktionsassistenten aus. Spätere Pflege folgt dem
bestehenden Editor-/Revisionsweg.

### 6.3 PW-FIND · phasenübergreifende Befundentscheidungen

Neue Produktionen verwenden den v3-Record mit konkreten Befunden.
Bestehende aktuelle v2-Stände lassen sich gezielt fortschreiben. Die Annahmesemantik
steht in [Qualität §6.1](../PUZZLE_QUALITY.md#61-pw-find--befundentscheidungen-in-allen-phasen),
ihre technische Bindung in [PW-B](../../tools/PW_B_CONTRACT.md#pw-find--freigegebene-erweiterung-der-entscheidungsdaten).

Dieser Weg gilt für Abschlussbild, Motivvorlage, Raster, Kontextzeichnung und
Schlussübersicht. Ein Auftrag kann konkrete zulässige Befundannahmen samt
Behandlung, aktuelle Kandidatenwahl und fällige Folgeaktion verbinden. Keine
zusätzliche menschliche Runde allein zur Veröffentlichung der Annahmen.
Fällige harte Voraussetzungen, echte Bild-/Motiv-/Parameterwahlen und Endabnahme
bleiben erforderlich; auf spätere Phasen entfallende Prüfungen nicht vorziehen.

„Korrigieren“ bezeichnet eine konkrete Arbeitsgrundlage, auch einen blockierten
Kandidaten. Geltende Behandlungen bei den beauftragten Änderungen beachten;
Annahme allein verlangt keine Reparatur. Nur die nach Qualität §6.1 gedeckten
Befundannahmen auf neu beurteilte Nachfolger übertragen, keine kreative Wahl
neuer Bytes. Korrigierte Ergebnisse zur fälligen tatsächlichen Wahl vorlegen.
Budgets und freigegebener Korridor bleiben wirksam.

Aktuelle Behandlungsvorgaben bis Endabnahme und Integration erhalten. Ein
angenommener, weiterhin gedeckter Befund wird nicht erneut zum Blocker. Gültige
Annahmen aus dem abgesendeten Auftrag bei anderen offenen Voraussetzungen im
tatsächlichen Reviewstand sichern, ohne einen falschen Phasenerfolg zu behaupten.
Für Übernahme/Widerruf genügt die noch relevante kompakte Entscheidungsbindung;
keine neue Herstellungs-/Korrekturhistorie oder dauerhafte Produktionsakte.
Schritt 5 §9 bleibt der Abschlussweg; spätere Spiel-/Editorarbeit ist ein eigener
Auftrag. Der aktuelle Akteur prüft die relevanten Behandlungsvorgaben vor seiner
Folgearbeit, statt nur den Phasenstatus oder eine alte Blockerliste zu übernehmen.

## 7. Freigaben und Abschlussausgabe

Jede Chatübergabe nennt erreichte Phase, feste Quelle, ausgeführte Prüfungen,
offene Entscheidung/nächsten Schritt, echte Bild-/Dateilinks und stabile Angebots-IDs.
Der Assistent liest veröffentlichte Originale; keine zweite Sheet-JSON-Sammlung
oder Entwicklungs-HANDOFF-Ausgabe. Software prüft Aufzeichnungen/Bytes, authentifiziert keine Menschen.
Arbeitswurzel/Merge sind ausdrückliche Auftragsoptionen, keine
Recordrechte. Produktionsprompts beauftragen keine lokale Zusatzbereinigung;
separater Auftrag nach WORKSPACE, fachlicher Schritt-5-§9-Abschluss bleibt.
Neue Briefingentwürfe behaupten keine ID/Quelle/Freigabe; spätere eigene
Hintergrundrevisionen folgen dem gezielten Bildwechsel aus Schritt 5 §9,
keinem Alt-Sheet-Sitzungsimport.
