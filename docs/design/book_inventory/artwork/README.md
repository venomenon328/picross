# BP-2 · Museumsbuch-Illustrationen

Stand: 26.09.2026 · B2-01 bis B2-05 aus [#27](https://github.com/venomenon328/picross/issues/27)
unter [#21](https://github.com/venomenon328/picross/issues/21).

Zwei mit dem nativen Bildwerkzeug erzeugte UI-freie Hintergrundkandidaten auf der
unveränderten BP-1R-Komposition aus PR #30. A: dunkler Inventarband; B: vom geprüften
A abgeleiteter heller Leinen-/Lederkatalog. Keine finale Eigentümerwahl.

| Kandidat | Hintergrund 2560×1440 | Hintergrund 1080p | Native Quelle |
| --- | --- | --- | --- |
| A | [Inventarband](bp2-a-inventarband.png) | [1080p](checks/a-background-1080.png) | [Generator](originals/a-generator.png), [qualifiziert/retuschiert](originals/a-qualified.png) |
| B | [Sammlungskatalog](bp2-b-sammlungskatalog.png) | [1080p](checks/b-background-1080.png) | [Generator](originals/b-generator.png) |

Native Generatorausgaben: **1672×941, RGB-PNG**. Proportionaler zentraler Beschnitt
von insgesamt 0,5 nativen Pixeln in der Höhe, danach Faktor 2560/1672 auf 2560×1440.
Das ist Hochskalierung, kein Nachweis nativer 1440p-Detailqualität. Bei A wurde der
untere Materialrand lokal korrigiert; [Ablauf und Grenzen](PROCESS.md).

[Review-ZIP](bp2-review.zip) · [Datei-/Inputmanifest](manifest.json) ·
[Generierung und Promptzuordnung](generation.json) · [Prüfbericht](VERIFICATION.md).
Unveränderlicher Downloadlink, ZIP-Hash, Head, CI und getrennter Selbstreview stehen
im zugehörigen Draft-PR. Das ZIP enthält Kandidaten, native Quellen, technische
Geometriehilfe, Kontrollen und Metadaten; keine Fonts.

## Unveränderte UI als Assetkontrolle

Diese Montagen verwenden die gelieferten transparenten BP-1R-PNGs unverändert.
Nur das Hintergrundbild wird proportional angepasst. Die technische Fußzeile der
Vorlage bleibt deshalb ebenfalls sichtbar; sie ist keine Produkt-UI und keine neue
Beschriftung im Hintergrund. Die vollständige UI-Gestaltung bleibt BP-3.

| Größenfall | A | B |
| --- | --- | --- |
| F-02, 1920×1080, 40×40 / 18 px | [Montage](checks/a-f02-1920.png) | [Montage](checks/b-f02-1920.png) |
| F-02, 2560×1440, 40×40 / 18 px | [Montage](checks/a-f02-2560.png) | [Montage](checks/b-f02-2560.png) |
| F-01, 2560×1440, 20×20 / 24 px | [Montage](checks/a-f01-2560.png) | [Montage](checks/b-f01-2560.png) |
| F-03, 1920×1080, 57×28 / 24 px | [Montage](checks/a-f03-1920.png) | [Montage](checks/b-f03-1920.png) |
| F-02, 1280×720, UI 125 %, 29×17 / 22 px | [Montage](checks/a-f02-1280.png) | [Montage](checks/b-f02-1280.png) |

Je Montage liegen unskalierte `-numbers`- und `-status`-Ausschnitte in `checks/`.
Die vier `-native-`-Ausschnitte je Kandidat zeigen Einband, Papier, Falz und unteren
Rand in nativer Pixelgröße. [Lokale Textkontraste](checks/contrast.json) sind
Einzeltext-Minima auf dem wirklichen Untergrund, keine Papiermittelwerte.

BP-3 wird erst separat vorbereitet: gleiche materialgerechte UI auf beiden
Hintergründen, dann konkrete Eigentümerwahl. Keine native Integration, neue
Layoutentscheidung, Fortsetzung von #23/#24, Merge oder Release. #27/#21 bleiben offen.
