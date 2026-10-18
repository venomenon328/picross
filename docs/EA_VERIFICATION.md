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

Bis zur Integration von [CI-C (#249)](https://github.com/venomenon328/picross/issues/249)
läuft `tools/ea_product.py` im bestehenden `--integration`-Pfad des Produktharness.
Der am 18.10.2026 freigegebene Sollvertrag der [CI-Policy](CI_POLICY.md) ist noch
nicht implementiert. CI-C trennt eine unabhängig auswählbare native Abschlussgruppe
von der 500er-Route; gemeinsame Save-/UI-/Renderabhängigkeiten wählen weiterhin
alle betroffenen Gruppen. Aktuelle Bewegung, sofortiger Commit/Save, echter
Prozessneustart, Reset und Exportaussagen bleiben erhalten. Vor CI-C gelten die
vorhandenen ausführbaren Auswahlpflichten weiter.

Der Harness verwendet ausschließlich temporär erzeugte technische Fixtures aus dem festen
Katalog und den kleinen Web-Fällen, keine rätselspezifische Produktionsrekonstruktion.
Die technische Lieferung enthält JSON-Berichte, kompakte Phasen-/Endbilder und
`ea/motion.apng` aus tatsächlichen nativen Frames mit gemessenen Zeitabständen.
Keine künstlich interpolierte Vorschau. Vollständige lokale Frames bleiben lokal.
`tools/web_tests/browser.py` prüft Chromium und Firefox mit echten Zeigerereignissen,
Bestätigung, Abbruch, Reset, wiederholtem Lösen und dauerhaftem Browser-Neustart.
Nach CI-A bleibt jede ausgewählte Browserroute bis CI-B vollständig; erst CI-B
trennt Abschluss/Reset und Persistenz/Lifecycle nach dem [Webvertrag](WEB_HOSTING.md).
Keine Verkürzung der Produktanimation oder Ersetzung echter Persistenz/Neustarts.

Reproduktion: `python tools/p1_product.py --cache-dir <verifizierter-cache>
--output-dir <leeres-ziel>` gemäß Projektprofil. Änderungen am Renderer aktivieren
zusätzlich die regulären Ressourcen-/Cache-/Pixelprüfungen. Konkrete Ergebnisse,
Downloadbindungen und der native Windows-EXE/PCK-Nachweis stehen im aktuellen PR;
diese Zuordnung allein behauptet keinen bestandenen Lauf.

Der Produktharness serialisiert ausschließlich die Editor-Importworker über eine
vorübergehende Einstellung in der isolierten `project.godot`
(`editor/import/use_multiple_threads=false`). Linux-CI-Läufe stürzten zuvor im
parallelen Fontimport mit `propagate_notification()` / Signal 11 ab.
`override.cfg` genügt hierfür nicht: Godot ignoriert Overrides im Editormodus.
Die ursprünglichen Projektbytes werden auch nach Fehlern wiederhergestellt;
Laufzeitprüfungen und Spielerexport verwenden das unveränderte Projekt.
Vorhandene Importeinstellungen/Overrides werden nicht überschrieben, Fehler nicht ignoriert.
Die Einstellung ist im [gebundenen Godot-Quellstand](https://github.com/godotengine/godot/blob/4.7.2-stable/editor/file_system/editor_file_system.cpp)
vorhanden; Engine, Importressourcen und Pflichtselektion bleiben unverändert.

## Getrennte Gates

KE-N1 / #233 ergänzt den gemeinsamen Reveal-Bildpfad: pro verdienter Anzeige
auf das Anzeigemaß mit Lanczos verkleinerte Textur auch während der EA-Überblendung,
im Endbild und bei Wiederöffnung. Die bisherige lineare Abschlussfilterung allein
war bei starker Verkleinerung nicht ausreichend. Originale, Bildgeometrie, Timing,
Save-/Abbruchverhalten bleiben gleich. `ke_graphics.gd` ergänzt native Vorher-/Nachher-
Ausschnitte für ein festes hochauflösendes PNG und ein transparentes SVG in allen
vier KE-Ansichten. Die bisherigen EA-Bewegungs-/Neustartprüfungen bleiben aktiv.
Aktuelle Ergebnisbindung und getrennte KE-Abnahmen: [KE_VERIFICATION](KE_VERIFICATION.md).

- **EA-T01:** technische Lieferung des Implementierers einschließlich aktueller CI,
  nativer Bewegung, Windows-Export, Browsern und getrenntem Selbstreview vor Übergabe.
- **EA-R01:** unabhängiges technisches Review des gebundenen Heads **vor Merge**.
- **EA-M01:** persönliche Maus-/Sichtprobe des Eigentümers am gebundenen Windows-Build
  **vor Merge**: Timing, Papierzentrum, Motivname, Reset/Abbruch, Wiederöffnung und
  Neuabschluss. Technische Zeigersimulation ersetzt diese Abnahme nicht.

EA-R01 und EA-M01 bleiben offen, bis getrennte Nachweise vorliegen. Draft-PR,
Selbstreview und grüne CI sind keine Merge-, Release- oder Deploymentfreigabe.
