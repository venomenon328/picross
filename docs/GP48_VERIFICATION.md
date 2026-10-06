# GP-48 · technische Lieferung und offene Abnahme

Issue [#48](https://github.com/venomenon328/picross/issues/48), GP-01–GP-03.
Arbeitsbranch `feat/48-gameplay-feedback`, Ziel `main`; vorbereitete und tatsächlich
verwendete Basis `cd4a8db86e51891f13e305b589837a1a4354c5a2`. Beim Start gab es
keine Änderungen seit dieser Basis. PR #47 und sein Branch bleiben unverändert.
Keine Pilotinhalte, Rätseldaten, Paletten, Zertifikate, Save-Schemata oder
Appidentitäten wurden übernommen oder geändert.

## Implementierung

- GP-01 bindet im bestehenden Gestenmodell den ursprünglichen Startzustand.
  Die sechs Fälle schützen oder konvertieren entsprechend der Issue-Tabelle.
  G1 gibt weiterhin nur die Achse frei; Snapshot, Farbe, Modus und Startkategorie
  bleiben gebunden. Vorschau und atomischer Commit verwenden denselben Pfad.
- GP-02 ergänzt die bestehende begrenzte H1-DAG-Analyse um `OPEN`, `FILLED` und
  `CLOSED`. Nur das in allen kompatiblen Belegungen identische, vollständig gefüllte
  Originalintervall kann positiv sein. Für `CLOSED` zählt jedes unmittelbar
  benachbarte X, der echte Linienrand oder eine andere positive Farb-ID. Der
  angrenzende andere Block muss nicht vollständig sein. Keine Enumeration im
  Produktpfad, kein Lösungsvergleich, keine neuen Save-Felder. Die linearen
  Snapshot-Caches und deren Invalidierung bleiben erhalten.
- GP-03 verwendet eine `FontVariation` des vorhandenen Plex Sans mit Gewicht 600.
  Schriftgrößen und gemeinsame Slots bleiben erhalten. Der Zwischenzustand hat
  Alpha 0,78 in seiner Originalfarbe; die bestehende C1-Kontur bleibt erhalten.
  Alle Zeichenpfade einschließlich Tooltip und Drag nutzen dieselben Zustände.

## Nachweise und ihre Grenzen

Der zugehörige Draft-PR bindet den endgültigen Head, Basis, getesteten Checkout
beziehungsweise Test-Merge, Actions-Läufe, Artefakte und SHA-256-Werte. Dieses
Dokument beansprucht keine CI-Erfolge für einen noch nicht geprüften Folgecommit.
`product-report.json` in der Spielerlieferung enthält die konkrete Identität und
Prüfphasen; `report.json` im getrennten GP-Review-ZIP bindet dieselbe Lieferung.

| Akzeptanz | Technischer Prüfpfad |
| --- | --- |
| GP48-A01 | Bestehende P1.2-/G1-Matrix plus `tests/gp48_cases.gd`: echte Mausereignisse in beiden Achsen, sechs gemischte Fälle, eingefrorene Farbe/Modus, Rückzug, tatsächlicher Ursprung versus Projektion, Undo/Redo und Statusvorschau. Bestehende Radierer-, No-op-, Abbruch- und Miniaturprüfungen bleiben aktiv. |
| GP48-A02 | `tests/h1_cases.gd`: unabhängiger kleiner Zellbelegungsoracle, gespiegelte Zufallslinien, 19 explizite Dreizustandsfälle und bestehende Cache-, Vorschau-, Save-/Restore-/Recovery-Szenarien. GP-Ereignistests prüfen Übergänge und Schalter einschließlich Tooltip. |
| GP48-A03 | 40 native Bildpaare, 80 unveränderte PNGs: Mono/Farbe, beide Achsen, Tooltip, Überlauf, Zwischenversatz/Drop, Statusfolgen; 1920×1080/UI 100 % und 1280×720/UI 125 %. Dieselbe Capturedatei wird auf Basis und Lieferung ausgeführt. Zellhash, Ansicht, Skalierung, Schriftgröße, Dragziel und Tooltip werden paarweise verglichen; Statuswechsel erhalten Zeichenpositionen. Bestehende Pixelprüfungen laufen weiterhin. |
| GP48-A04 | Vollständiger Produktweg einschließlich 500 Aktionen mit unabhängigem Oracle, Prozessneustart, negativer Kontrolle, nativen Renderprüfungen, Windows-Export; sechs Pflichtjobs. Separater Slim-Upload, exakte Inhaltsliste und Exporthashes werden geprüft. |
| GP48-A05 | Getrennter vollständiger Selbstreview; unabhängiges technisches und visuelles Review bleibt offen. |

Bewusst angepasste historische Testerwartungen: P1.2-Matrix und Python-
500-Aktionen-Oracle bilden die Startkategorie ab; H1-Oracle vergleicht jetzt
drei Zustände, während die boolesche Eindeutigkeitsabfrage erhalten bleibt.
H1-Off/On-Pixelprüfung zählt Abschwächung und Strich als Darstellungsänderung.
Fontmessungen verwenden den tatsächlichen Hinweisfont. Keine Prüfpfade wurden
deaktiviert; historische Abnahmeberichte bleiben unverändert.

Das GP-Review-ZIP enthält `index.html` mit nebeneinanderliegenden Basis-/Lieferbildern
und direkt anklickbaren nativen PNGs. Die technischen Teilstände sind ausdrücklich
keine normalen Spielstände und werden nicht in die Spielerlieferung aufgenommen.
Die eigene Bildsichtung beurteilt Gewicht, Farbunterscheidbarkeit, C1-Kontrast und
Lesbarkeit; sie ersetzt keine unabhängige Sichtprüfung oder Eigentümerprobe.

## Download und gezielte Probe

Actions-Artefakt `picross-p1-player-<Head>` enthält ausschließlich
`picross-p1-windows-x86_64.zip`. Darin liegen die beiden eingebetteten EXEs,
Lizenzen, Commit-/Produktbericht, neutrale Anleitung und `gp48-owner.ps1`.
Renderbilder, technische Logs, Teststände und synthetische H1-Exporte liegen separat.

[Gezielte Eigentümerprobe](GP48_OWNER_TRIAL.md) / im Spieler-ZIP
`GP48-SPIELPROBE.md`: commitgebundener isolierter Start, sechs Gestenfälle,
Hinweiszustände mit X/Rasterrand/Farbwechsel, Lesbarkeit und leeres Ergebnisprotokoll.
Keine vollständige RP-6-Lösung erforderlich. Normale Benutzersaves bleiben getrennt.

**Offene Mergegates:** unabhängiges technisches/visuelles Review auf dem Lieferhead
und GP48-M01 durch den Eigentümer. Keine davon wurde durch den Implementierer
als bestanden erklärt. Erst eine separate Freigabe erlaubt Merge. Zusammenführung
mit PR #47 und Fortsetzung von RP6-M01–M04 sind spätere, getrennte Schritte.
Kein Release.
