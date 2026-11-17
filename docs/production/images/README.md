# Bildnormen nach Bildtyp

Dokument-ID: `production-images`
Status: `active`
Stand: 17.11.2026 · [#696](https://github.com/venomenon328/picross/issues/696)

## IMG-01 Zuständigkeit

| Gegenstand | Alleinige gestalterische Norm |
| --- | --- |
| Farbige Abschlussillustration | [REVEAL](REVEAL.md) |
| Vereinfachte Motivvorlage | [MOTIF](MOTIF.md) |
| Diskretes Lösungsraster | [RASTER](RASTER.md) |
| Kontextzeichnung hinter dem Rätsel | [BACKGROUND](BACKGROUND.md) |
| Handschriftliche UI-Titelgrafik | [TITLES](TITLES.md) |

- Ablauf, Kandidatenzahl, Budgets, tatsächliche Entscheidungen und Übergaben: [Authoring](../authoring/PUZZLE_AUTHORING.md).
- Kriterien-IDs, Einzelurteile, Prüfzeitpunkte und zulässige redaktionelle Abweichungen: [Qualität](../PUZZLE_QUALITY.md).
- Datei-/Profil-/Runtimeverträge: [Hintergrundtechnik](../PUZZLE_BACKGROUNDS.md) und [Revealtechnik](../REVEAL_TRANSPARENCY.md).
- Die Phasenroute im Authoring bestimmt die Pflichtlektüre. Ein Querverweis verlangt keine rekursive Volllektüre.
- Stilregeln nur in der zuständigen Bildtypdatei ändern. Andere Quellen verweisen auf diese Regel; sie führen keine zweite Formulierung derselben Norm.
- UI-Titelgrafiken gehören zur Spielgestaltung. Ihre Produktion und Abnahme folgen dem jeweiligen Entwicklungsauftrag; TITLES ist keine zusätzliche Pflichtquelle oder Snapshotdatei der fünf Rätselphasen.

Weitere Bilddarstellungen besitzen eigene Zuständigkeiten außerhalb der kreativen
Rätselproduktion:

| Gegenstand | Zuständige Quelle und Abgrenzung |
| --- | --- |
| Buchflächen und Kategoriezeichnungen | [Buchintegration](../../game/BOOK_INTEGRATION.md), [Zeichenstil](../../game/UI_DRAWING_STYLE.md) und [Ressourcenbindung](../../game/Z2_SELECTION.md); Herkunft im [Designindex](../../design/README.md). Keine Anwendung des neuen Kontextbildformats auf bestehende Kategoriezeichnungen. |
| UI-Schrift, Rahmen und Piktogramme | [HAND_DRAWN_UI](../../game/HAND_DRAWN_UI.md); Hinweisziffern nach [CLUE_TYPOGRAPHY](../../game/CLUE_TYPOGRAPHY.md). Keine generativen Abschlussbilder. |
| Zelltexturen, Sprites und Atlanten | [CELL_RENDERING](../../game/CELL_RENDERING.md) und [Zeichenstil](../../game/UI_DRAWING_STYLE.md); technische Spielressourcen ohne eigene Bildfreigabe im Authoring. |
| Raster-, Katalog- und Prüfansichten | Ableitungen des jeweils gebundenen Rasters beziehungsweise Originalbilds nach [Qualität](../PUZZLE_QUALITY.md) und [Katalogdarstellung](../../game/CATALOG_PRESENTATION.md). Eine Ansicht ersetzt weder Lösungszellen noch freigegebene Originalbytes. |

## IMG-02 Normwörter

| Wort | Bedeutung |
| --- | --- |
| `MUSS` | Verbindliche positive Anforderung an den bezeichneten Gegenstand. |
| `DARF NICHT` | Verbindlicher Ausschluss. |
| `DARF` | Zulässig, aber nicht erforderlich. Das Fehlen ist kein Mangel. |
| `EMPFEHLUNG` | Unverbindliche Gestaltungsrichtung; kein eigenständiger Ablehnungsgrund. |

- Beispiele erzeugen keine weitere Pflicht, Quote oder technische Grenze.
- Eine Stilanforderung beschreibt den Zielzustand. Für die vier Gegenstände der Rätselproduktion bestimmt ausschließlich die Kriterienklassifikation im Qualitätsvertrag, ob eine konkrete Abweichung angenommen werden darf. Titelgrafiken folgen ihrem eigenen Abnahmevertrag.
- Harte Voraussetzungen und deren ausdrücklich unterstützte Ausnahmewege bleiben getrennt. Insbesondere ist [H-07](../PUZZLE_QUALITY.md#4-unabdingbare-voraussetzungen-und-zuständige-harte-normen) kein redaktionell abweichbares Kriterium.

## IMG-03 Gegenstände und Geltung

| Darstellung | Funktion und Bindung |
| --- | --- |
| Abschlussbild | Gewählte Illustration und gestalterische Referenz. |
| Motivvorlage | Gesondert freigegebene Abstraktion genau dieses Abschlussbilds. |
| Lösungsraster | Eigene diskrete Abstraktion; alleinige Quelle der Lösungszellen und Hinweise. |
| Hintergrund | Eigenständiger Kontext mit eigener Bildrevision und Entscheidung; keine Lösungszellen. |

- MUSS: Dateien, Revisionen und Entscheidungen der vier Gegenstände unterscheiden; das detaillierte Original nicht überschreiben.
- Geltung: neue Bilder und ausdrücklich beauftragte Bildrevisionen. Eine Normänderung erklärt vorhandene ausgewählte oder integrierte Bilder nicht automatisch für ungültig.
- MUSS: aktive Bilder bis zur tatsächlichen Wahl und Integration ihrer neuen Fassung unverändert erhalten. Historische Originale, Snapshots und Freigaben nicht umschreiben, übertragen oder neu etikettieren.
- Auftragsumfang, Bestandskohorte und Abnahmen stehen im jeweiligen Issue/PR; diese Dateien erteilen keinen zusätzlichen Produktions-, Integrations- oder Mergeauftrag.
