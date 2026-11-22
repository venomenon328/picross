# Dokumentation: Zuständigkeiten und Einstieg

Dokument-ID: `docs-index`
Status: `active`
Zuständigkeit: Navigation, Dokumentrollen und Regeln zur Pflege der Quellen.

## 1. Passende Quellen wählen

1. Mit [AGENTS](../AGENTS.md) beginnen und den passenden Auftragsweg wählen.
2. Für Entwicklungsarbeit [PROJECT_PROFILE](PROJECT_PROFILE.md) und die dort
   benannten Regeln/Fachquellen lesen. Für Rätselproduktion die Phasenroute im
   [Authoring](production/authoring/PUZZLE_AUTHORING.md) verwenden.
3. Den aktuellen Auftrag, Lieferstand und tatsächliche Abnahmen am zuständigen
   Issue/PR prüfen. Ein datierter Bericht beweist nur seinen damaligen Stand.

Diese Seite ersetzt keine Fachnorm. Ein Querverweis verlangt keine rekursive
Volllektüre sämtlicher verlinkter Dokumente. Maßgeblich sind die expliziten
Pflichtquellen des aktuellen Aufgabenbereichs und die unmittelbar benötigte Norm.

## 2. Ordner und Dokumentrollen

| Pfad | Inhalt und Geltung |
| --- | --- |
| [PROJECT_PROFILE.md](PROJECT_PROFILE.md) | Stabile Projekteigenschaften und aufgabenbezogene Fachroute. |
| [dev-rules/](dev-rules/WORKFLOW.md) | Lokaler generischer Entwicklungsworkflow, Befugnisse, Modellwahl, CI- und Übergabevertrag. |
| [project/](project/PRODUCT_DEFINITION.md) | Produktanforderungen, gestalterische Richtung und Herkunft des Regelpakets. |
| [game/](game/PROTOTYPE_P1.md) | Spielverhalten, Buch/UI, Kategorien, Eingabe, Anzeige und Darstellung; [SYNC](game/SAVE_SYNC.md) als freigegebenes Soll für optionale Konten und gemeinsame Spielstände. |
| [production/authoring/](production/authoring/PUZZLE_AUTHORING.md) | Kern und fünf Phasen der Rätselproduktion: Ablauf, Auswahl und Übergaben. |
| [production/images/](production/images/README.md) | Gestalterische Norm je Bildtyp; keine zweite Ablaufbeschreibung. |
| [production/](production/PUZZLE_PRODUCTION.md) | Technische Produktion, Qualität, Bildprofile, Rasterableitung und Integration. |
| [tools/](tools/PRODUCTION_WORKSPACE.md) | Produktionsworkspace, Batch, Bestandseditor, Anzeigeverträge und App-Updates. |
| [difficulty/](difficulty/PUZZLE_DIFFICULTY_V2.md) | Aktuelle und weiterhin lesbare Bewertungsmethoden, Analyzer und Kalibrierung. |
| [ci/](ci/CI_WORKFLOW_V2.md) | Projektspezifische Modulauswahl, Toolchain und tatsächliche Prüfgruppen. |
| [operations/](operations/WEB_HOSTING.md) | Webbuild, Persistenz, manuelles Deployment und [Windows-Spielinstaller](operations/WINDOWS_GAME_APP.md). |
| [workflow/](workflow/Entwicklungsworkflow_Cheat-Sheet.html) | Offline-Bedienhilfe für den Entwicklungsworkflow. |
| [design/](design/README.md) | Benötigte Originale, Freigaben, Nutzungsrechte und Ressourcenherkunft. |
| [font-inputs/](font-inputs/delight_coffee.zip) | Unveränderte Schriftoriginale als gebundene Herstellungsinputs. |
| [legacy/](legacy/README.md) | Noch konsumierte frühere Eingänge und Diagnoseverträge; keine aktuelle Produktionsroute. |
| [history/](history/README.md) | Kompakter Wegweiser zu entfernten Berichten und tatsächlich benötigten historischen Freigaben. |
| [evidence/kk/](evidence/kk/README.md) | Weiterhin verwendete Eingänge einer ausdrücklich aufrufbaren Diagnose. |

## 3. Eindeutige Zuständigkeit

- Eine Regel hat genau eine maßgebliche Quelle. Andere Dokumente verlinken den
  zuständigen Abschnitt und beschreiben nur ihre eigene Anwendung oder Schnittstelle.
- Ablauf, Gestaltung, Qualität, technische Form und Darstellung sind getrennte
  Zuständigkeiten. Beispielsweise bestimmt Authoring Schritt 4 die Hintergrundphase,
  `images/BACKGROUND.md` ihren Stil und `PUZZLE_BACKGROUNDS.md` Profil und Ableitung.
- Bei einer Änderung die überholte Fassung direkt ersetzen. Keine Kette aus
  vorangestellten Zusätzen, die widersprüchliche Absätze erst nachträglich übersteuert.
- Aktuelle Formate und weiterhin unterstützte Altformate ausdrücklich benennen.
  Eine historische Spezifikation ist kein Nachweis, dass ihr Reader noch existiert.
- Eine vorgeschlagene Funktion, bestätigte Anforderung, Implementierung, erfolgreiche
  Prüfung und Abnahme sind verschiedene Aussagen. Keine davon aus einer anderen ableiten.

## 4. Schreib- und Parsekonventionen

Aktive Fachquellen nennen am Anfang Gegenstand und Geltung. Neue Regelabschnitte
verwenden stabile IDs oder eindeutige Überschriften. Strukturierte Formen nennen
exakte Feldmengen, Typen, Grenzen, Pflicht-/Nullwerte und unbekannte Werte ausdrücklich.
Beispiele sind als Beispiele gekennzeichnet und erweitern keine geschlossene Form.

Tabellen dienen der Zuordnung gleichartiger Felder und Kriterien. Nummerierte
Listen beschreiben Reihenfolgen; Aufzählungen beschreiben unabhängige Regeln.
Ganze Fachverträge nicht in Fußnoten, Screenshots oder HTML-Bedienhilfen verstecken.
Die Normwörter der Bildproduktion stehen zentral im
[Bildindex](production/images/README.md#img-02-normwörter).

Relative Markdownlinks verweisen auf aktuelle Repositoryquellen. Historische
Behauptungen verwenden einen festen Commit oder den tatsächlichen Issue-/PR-Beleg.
Dateiverschiebungen aktualisieren Links und reale Dateileser gemeinsam. Bereits
gebundene Snapshots, Originale, Freigaben, Methodendaten und Nutzungsrechte behalten
ihre Bytes; sie werden nicht auf neue Pfade oder Revisionen umetikettiert.

## 5. Entfernte Dokumente

Obsolete Lieferberichte, abgelöste Sammelnormen und die alte Produktions-Bedienhilfe
stehen nicht mehr als konkurrierende aktuelle Quellen im Arbeitsbaum. Ihre noch
gültigen Einzelregeln sind in den zuständigen Fachquellen enthalten. Der
[Historienwegweiser](history/README.md) erklärt die verbliebenen Bestände und
verlinkt die vollständigen früheren Quellen im Git-Verlauf.
