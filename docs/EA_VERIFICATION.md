# EA · Abschlussenthüllung (#170)

Vertrag: [vollständiges Issue #170 einschließlich Umsetzungsvorbereitung V1](https://github.com/venomenon328/picross/issues/170).
Basis: KB aus PR #169 ist als `bdf22e5e226a058ce47d00cea59853ec2db01a8b`
in main integriert. Der EA-Branch beginnt auf diesem Commit; kein Kopieren oder
Merge der KB-Arbeit durch EA. Ein Paket, keine neuen Assets oder Produktoptionen.

## Umsetzung und technische Prüfzuordnung

| Kriterium | Umsetzung / gezielter Nachweis |
| --- | --- |
| EA-A01 | Bestätigter Commit startet `completion.gd`: 250/650/400/650/200 ms. `ea_probe.gd` prüft Previewgrenze, sofortigen Save/History, Ausgangsgeometrie, vollständige Füllungen und reale native Bewegungsframes. |
| EA-A02 | Gapless Raster aus bestätigten Spielerzellen, Originalpalette und leere Hintergründe; vorhandener Atlaszeichner liefert exakt dieselben Schraffurkommandos. Native Farb-/Rechteckprobe, keine neue Zelltextur. |
| EA-A03 | Eigene Seitenverhältnisse, gemeinsamer Mittelpunkt im reservierten Papierbereich. Drei Kontexte 1280×720/UI125, 1920×1080/UI100, 2560×1440/UI125; zusätzlicher langer Name, Rechteck und Hochformat. |
| EA-A04 | Vorhandener BookButton/reset.svg, 44/55-Ziel. Zeiger öffnet Bestätigung, Abbruch unverändert, Fehler sichtbar, stabile ID und Dialogursprung auch bei zwischenzeitlichem Blattwechsel; erfolgreicher Abschlussreset öffnet das leere Blatt. Katalogreset bleibt bestehend. |
| EA-A05 | Fokusverlust, Resize, UI-Skalierung, Web-Lifecycle, Katalog und Blattwechsel stoppen den Controller. Bestehende Save-/Recovery-/Quitregressionen bleiben im Pflichtpfad. |
| EA-A06 | Wiederöffnung ohne Replay; zweiter tatsächlicher Prozess mit demselben isolierten Profil. Browser-Reinitialisierung nach bestätigtem IndexedDB-Sync. |
| EA-A07 | Keine Animation im Save, keine Timer je Zelle, keine dauerhafte Frameverarbeitung. Transiente Kommandos/Materialreferenz werden am Ende freigegeben; Artwork beim Verlassen. Regulärer Export-/PCK-Audit und PERF-B bleiben verpflichtend. |
| EA-A08 | Vertragstexte und Spielanleitung aktualisiert; tatsächlicher Voll-Diff, getrenntes Selbstreview und aktuelle Head-/Basis-/Checkout-/Run-Bindung im Draft-PR. |

`tools/ea_product.py` läuft im bestehenden `--integration`-Pfad des Produktharness.
Er verwendet ausschließlich temporär erzeugte technische Fixtures aus dem festen
Katalog und den kleinen Web-Fällen, keine rätselspezifische Produktionsrekonstruktion.
Die technische Lieferung enthält JSON-Berichte, kompakte Phasen-/Endbilder und
`ea/motion.apng` aus tatsächlichen nativen Frames mit gemessenen Zeitabständen.
Keine künstlich interpolierte Vorschau. Vollständige lokale Frames bleiben lokal.
`tools/web_tests/browser.py` prüft Chromium und Firefox mit echten Zeigerereignissen,
Bestätigung, Abbruch, Reset, wiederholtem Lösen und dauerhaftem Browser-Neustart.

Reproduktion: `python tools/p1_product.py --cache-dir <verifizierter-cache>
--output-dir <leeres-ziel>` gemäß Projektprofil. Änderungen am Renderer aktivieren
zusätzlich die regulären Ressourcen-/Cache-/Pixelprüfungen. Konkrete Ergebnisse,
Downloadbindungen und der native Windows-EXE/PCK-Nachweis stehen im aktuellen PR;
diese Zuordnung allein behauptet keinen bestandenen Lauf.

Der Produktharness serialisiert ausschließlich die Editor-Importworker über eine
vorübergehende `override.cfg` (`editor/import/use_multiple_threads=false`). Zwei
Linux-CI-Läufe stürzten zuvor im parallelen Fontimport mit
`propagate_notification()` / Signal 11 ab. Die Datei wird auch nach Fehlern
entfernt; Laufzeitprüfungen und Spielerexport verwenden wieder das unveränderte
Projekt. Vorhandene Overrides werden nicht überschrieben, Fehler nicht ignoriert.
Die Einstellung ist im [gebundenen Godot-Quellstand](https://github.com/godotengine/godot/blob/4.7.2-stable/editor/file_system/editor_file_system.cpp)
vorhanden; Engine, Importressourcen und Pflichtselektion bleiben unverändert.

## Getrennte Gates

- **EA-T01:** technische Lieferung des Implementierers einschließlich aktueller CI,
  nativer Bewegung, Windows-Export, Browsern und getrenntem Selbstreview vor Übergabe.
- **EA-R01:** unabhängiges technisches Review des gebundenen Heads **vor Merge**.
- **EA-M01:** persönliche Maus-/Sichtprobe des Eigentümers am gebundenen Windows-Build
  **vor Merge**: Timing, Papierzentrum, Motivname, Reset/Abbruch, Wiederöffnung und
  Neuabschluss. Technische Zeigersimulation ersetzt diese Abnahme nicht.

EA-R01 und EA-M01 bleiben offen, bis getrennte Nachweise vorliegen. Draft-PR,
Selbstreview und grüne CI sind keine Merge-, Release- oder Deploymentfreigabe.
