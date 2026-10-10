# Z1.1 · Quellen, Rendering und Prüfumfang

Stand: 26.09.2026 · Lieferung ausschließlich zu Issue #26.

## Gebundene Quellen

| Quelle | Identität / Verwendung |
| --- | --- |
| Arbeitsbasis | `main@831b46f9e373e8691c18088efc9f2495fe3defb8`; eigener Branch `chore/26-art-direction`. |
| Auftrag | Vollständige [#26](https://github.com/venomenon328/picross/issues/26) und [#21](https://github.com/venomenon328/picross/issues/21), beim Start ohne Kommentare; ausdrücklicher Implementierungsauftrag im Nutzerthread. |
| Einstieg | Aktuelle AGENTS.md, lokaler Workflow und Projektprofil; Produktdefinition, Gestaltungskonzept, P1 0.13 und #5 einschließlich späterem Abschluss; lokale Modellauswahl und Katalog. |
| Lesende Referenz | [Z1-Unterlage](https://github.com/venomenon328/picross/blob/df7ac589e900a6d6d7c5080599c6a5ace47c395d/docs/design/Z1_DESIGN_REVIEW.md) und [demo.gd](https://github.com/venomenon328/picross/blob/df7ac589e900a6d6d7c5080599c6a5ace47c395d/prototypes/p1/design/demo.gd) am Head `df7ac589e900a6d6d7c5080599c6a5ace47c395d`. |
| PR-/Reviewgrenze | Vollständiger PR-#25-Body, Kommentare und [R1](https://github.com/venomenon328/picross/pull/25#pullrequestreview-5323317296) gelesen. Keine Nacharbeit an PR #25, kein behauptetes neues Review seines Diffs. B-01 bleibt offen. |
| V2-Bild | Vorhandenes commitgebundenes `z1/renders/v2-f02-1920x1080.png` aus PR #25 visuell als Vergleich angesehen; nicht als neues eigenes Renderbild ausgegeben oder in die neue Lieferung kopiert. |
| Fixtures | Unveränderte F-01/F-02/F-03 auf der Arbeitsbasis; SHA-256 in den öffentlichen Demoexporten, unabhängiger Vergleich gegen `git show <Basis>:<Pfad>` im Test. |
| Demo | Kopie [demo.gd.txt](sources/demo.gd.txt), Revision `z1-demo-1`; SHA-256 im Manifest. Explizite koordinatenbasierte Striche, abschließender Undo berücksichtigt. Kein Laden von Nutzerspielständen. |

Öffentliche Datenexporte: [F-01](sources/f01-public-demo.json),
[F-02](sources/f02-public-demo.json), [F-03](sources/f03-public-demo.json).
Sie enthalten Originalhinweise, Palette und Beispielzellen, weder Lösung noch Reveal.
Der Generator überträgt diese begrenzten disjunkten Striche; er implementiert keine
allgemeine Eingabe-, Hinweis-, H1- oder Solverlogik.

## Eigene Bilder und Schriftquellen

Alle Hintergründe und Icons sind für diese Studie selbst gezeichnete SVG-Pfade;
keine fremden Screenshots oder Assets wurden übernommen. Kein Bildgenerator,
kein externer Bilddienst und keine Netzressource zur Laufzeit der Galerie.

Originalfontdateien aus dem Google-Fonts-Repository, gepinnter Commit
`23e54b51ddffbc7713c583748e3bd86f62b1fa4a`, abgerufen am 26.09.2026:

| Familie | Quelle und Lizenz im Paket |
| --- | --- |
| Fraunces | [Quellordner](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/fraunces), [OFL](fonts/Fraunces-OFL.txt); Copyright 2018 The Fraunces Project Authors. |
| Barlow Condensed SemiBold | [Quellordner](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/barlowcondensed), [OFL](fonts/Barlow-OFL.txt); Copyright 2017 The Barlow Project Authors. |
| IBM Plex Sans | [Quellordner](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/ibmplexsans), [OFL](fonts/PlexSans-OFL.txt); Copyright 2017 IBM Corp., Reserved Font Name Plex. |
| IBM Plex Mono Regular | [Quellordner](https://github.com/google/fonts/tree/23e54b51ddffbc7713c583748e3bd86f62b1fa4a/ofl/ibmplexmono), [OFL](fonts/PlexMono-OFL.txt); Copyright 2017 IBM Corp., Reserved Font Name Plex. |

[Schriftmanifest](sources/fonts.json): exakte Download-URLs und Dateihashes.
Die TTFs sind unveränderte Originale, mit lokalen kurzen Dateinamen. OFL-Lizenztexte
sind ausschließlich auf LF und ohne nachgestellte Leerzeichen normalisiert;
Wortlaut unverändert, Original- und Lieferhash separat. Keine Umbenennung interner
Schriftfamilien, kein Subsetting und keine globale Schriftinstallation. Originale
sind zusätzlich als Data-URL in den SVGs eingebettet; damit sind die Vorlagen
offline portabel. In einem Vektoreditor ohne eingebettete Webfont-Unterstützung
die mitgelieferten Fonts lokal für das Dokument bereitstellen. PNGs bleiben die
verbindlichen Bildnachweise dieses Rendererstands; andere Renderer können abweichen.

## Reproduktion

Der Generator benötigt nur Python 3.11+. Für die optionale Rasterisierung werden
Playwright 1.55.0 und Pillow 12.3.0 in einer separaten temporären Python-Umgebung
benötigt; keine neue Produkt-/Buildplattform. Browserpfad ausdrücklich übergeben.
Verwendet: Python 3.13.14, Microsoft Edge / Chromium 153.0.4234.48, Windows,
Device Scale Factor 1. Font-Load wurde vor jedem Capture abgewartet und aufgezeichnet.

Aus dem Repositoryroot:

```powershell
python tools/design_study/generate.py
python tools/design_study/render.py --browser 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
python tools/design_study/assemble.py
python tools/design_study/render.py --browser 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'
```

Die erste Renderstufe liefert Einzelbilder; `assemble.py` baut daraus die
Übersichts-/Größentafeln und Offline-Galerie. Die zweite Stufe rendert den vollständigen
21er-Satz und schreibt seine Hashes. `generate.py` ersetzt die generierten SVGs
und das Manifest; manuelle SVG-Anpassungen daher zuerst in Kopien oder Generator
übernehmen. `assemble.py` bewahrt die Einzelbilddaten. Bei einer anderen Browserversion
Manifest und Bildkontrolle erneuern; byteidentische PNGs sind dann nicht zugesichert.

`manifest.json` bindet jede SVG-/PNG-Datei an Dimensionen und SHA-256. Hauptscreens
nennen zusätzlich Datenhash, Palette, Zellenhash, Ursprung, Zellgröße, Ausschnitt,
Hinweisflächen, Miniaturfläche, UI-Skalierung und gemessene Hintergrundfläche.
Der finale Git-Commit bindet Generator und Bildsatz; seine SHA steht im Draft-PR,
nicht als sich selbst verändernder Inhalt im eigenen Commit.

## Prüfwege und Grenzen

```powershell
python -m unittest discover -s tools -p 'test_*.py' -v
python tools/check_docs.py
git diff --check 831b46f9e373e8691c18088efc9f2495fe3defb8 HEAD
```

Die acht neuen Standardbibliothek-Tests werden vom vorhandenen `docs`-Job gefunden.
Sie prüfen vollständigen Lieferumfang, SVG-Parsing, alle PNG-Chunk-CRCs und
dekomprimierte Scanlinegrößen, Dateihashes, geladene Fonts, Bilddimensionen,
lokale Galerie-/SVG-Verweise, Original-Fixturehashes, öffentliche Demoexporte,
konkrete erwartete Strichzahlen einschließlich Undo, jedes gezeichnete Raster-/
Miniaturdatum und jeden Hinweiswert samt Originalfarbe, Stilvergleichsidentität,
Tokenfenster, enge Geometrien, UI-Kontrast und Scope gegen die Basis.

Die Renderprüfung misst äußere Textgrenzen; absichtlich ausgeschnittene Bereiche
der Detailtafeln sind davon getrennt. Sie ersetzt keine menschliche Betrachtung.
Alle 21 finalen Tafeln werden durch den Implementierer angesehen; der PR enthält
den getrennten Selbstreview mit konkreten Korrekturen und Bildstand.

Vorhandene ignorierte `artifacts/` aus früheren Aufgaben werden vom Dokumentvalidator
mitgescannt, obwohl sie nicht zur Lieferung gehören. Für einen sauberen lokalen
Dokumentnachweis eine temporäre Kopie ausschließlich des Git-Index verwenden;
Validator und Altartefakte nicht verändern. Der unveränderte CI-Checkout liefert
zusätzlich den erforderlichen finalen `docs`-Nachweis.

`product` und `preflight` bleiben unverändert und laufen nach PR-Erstellung gemäß
Repositoryworkflow. Ihre tatsächlichen Resultate werden im PR genannt. Sie prüfen
den unveränderten Produktstand, nicht die künstlerische Qualität dieser Studie.
Ein vom bestehenden CI-Workflow automatisch erzeugter Produkt-Testexport ist keine
Produktänderung oder neue lokale Windows-Spielprobe. Keine eigene Windows-Fassung
für diese SVG-Studie gebaut oder gestartet.

Offen bleiben unabhängiges technisches Review und ausdrückliche Mergefreigabe;
Eigentümerauswahl zu Stil/UI/Schrift/Kontrast vor #27/#23; native Umsetzung und
Bediennachweise erst in #23, tatsächliche längere Erprobung in #24.
