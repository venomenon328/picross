# BTI-C-T01 · aktuelle Revieworiginale

Produkt-Head **031565d941a60df5643adef561926d5721285322**, Basis
`b8829d6df6b40fb15e278689821d6a7e35f0f326`, PR-Testmerge
`47e21e61c0375bc59567de02e631a9d1e81cc41d`.
[Paketentscheidung](https://github.com/venomenon328/picross/issues/533#bti-c),
[Draft-PR #534](https://github.com/venomenon328/picross/pull/534).

Empfänger: anschließender **unabhängiger Codex-Reviewer von PR #534 mit
binärfähigem Git-/HTTP-Zugang**, ergänzend Eigentümer. Zugang dieses separaten
Reviewrefs bis **14.11.2026, 00:00 Uhr Europe/Berlin (13.11., 23:00 UTC)**.
Das ist eine vereinbarte Rückbaufrist, kein automatischer GitHub-TTL. Bei weiter
offenem Gate vor Ablauf Zugang neu abgleichen. Nicht in den Produktbranch/main
mergen. Keine dauerhafte Galerie und kein Technik-ZIP im Spieler.

## Unveränderte Produktoriginale

Die drei bereits in BTI-B-M01 freigegebenen PNGs liegen ohne Duplikate im
Produktbaum dieses Reviewcommits. Für unabhängige Sichtung **Raw binär laden**
oder den konkreten Commit mit Git auschecken, gegen das
[aktive Manifest](../../game/art/drawing/view_titles/manifest.json) prüfen und
selbst öffnen. GitHubs textgebundenes Contents-Objekt ist bei >1 MiB kein
ausreichender Binärweg. Ein Text-/Vorschaulink allein beweist keine Sichtung.

- [catalog.png](../../game/art/drawing/view_titles/catalog.png), 1814749 B,
  SHA-256 `0931abd9e2b67211b6895575f7ab157d10547348d62d2e99c4ba067ee4772cc4`.
- [help.png](../../game/art/drawing/view_titles/help.png), 2500745 B,
  SHA-256 `5ae830d1fe70007c67ed04570c034b446a3007c8ec78676cc335875bf3f8e87a`.
- [settings.png](../../game/art/drawing/view_titles/settings.png), 1427565 B,
  SHA-256 `d4c84fbe95279c51e1a07df9511e3482b3d65591942d1849655c2ef8dc452c75`.

## Sieben aktuelle Windows-PNGs

| Original | Tatsächlicher Client / UI | Zweck |
| --- | --- | --- |
| [catalog-1280-ui125.png](catalog-1280-ui125.png) | 1280×720 / 125 % | linker projizierter Kopf, Filter/Karte/Fußnavigation |
| [help-1280-ui125.png](help-1280-ui125.png) | 1280×720 / 125 % | f-Schwung, feststehender Titel und erreichtes Scrollende |
| [settings-1920-ui100.png](settings-1920-ui100.png) | 1920×1080 / 100 % | g-Schwung, zwei Gruppen, untere Navigation |
| [catalog-2560-ui125.png](catalog-2560-ui125.png) | 2560×1440 / 125 % | großer Katalogkopf, natürliche Wortbreite |
| [help-2560-ui125.png](help-2560-ui125.png) | 2560×1440 / 125 % | große rechte Hilfe mit Kapitelzugang |
| [settings-2560-ui125.png](settings-2560-ui125.png) | 2560×1440 / 125 % | große linke Einstellungen |
| [help-save-failure.png](help-save-failure.png) | 1920×1080 / 100 % | tatsächlicher Dateisystemfehler, gebundener Rücktooltip und Retry |

Tatsächliche Windows-EXE/PCK mit synthetischem Testkatalog, regulärem
`res://book/main.gd`, NVIDIA GeForce RTX 3070, 96 DPI. Kleine/1080p-/16:10-Größen
über bestätigte vorhandene Fensterpresets; 1440p als vorhandenes rahmenloses
Fenster am 2560×1440-Desktop, keine Desktopauflösungsänderung.
PNG-Originale des nativen Framebuffers, keine Nachskalierung, Bildkomposition
oder beschleunigte Animation. Der externe **lesende** Observer ist nur über
eine private override.cfg hinzugefügt; EXE/PCK bleiben bytegleich zum Export.
Der reguläre CI-Spieler für M01 enthält diesen Observer nicht.

## Bedienung, Import und Paketinhalt

[windows.json](windows.json) bindet 107 erfolgreiche aktuelle Assertions,
Szenarien, echte Titel-/Scroll-/Hitboxmaße, Quellcode- und EXE-/PCK-Hashes.
Geprüft: Kapitel-/Scrollgedächtnis über natürliche Pans, beide Scrollenden,
Katalog-/Arbeitsursprung, UI100→125→100, 1920×1200, sichtbarer Rücktooltip und
Tastaturfokus, Captureabbau. Eine eigene `.tmp`-Verzeichnisblockade erzeugte einen
echten Savefehler; beide Rückwege blieben gesperrt und funktionierten nach
Entfernen der Blockade wieder. Zellen/History blieben bei Navigation unverändert.
[os.jsonl](os.jsonl) enthält den OS-Ablauf; Treiber und Observer liegen daneben.
Ein am Desktop überdecktes 16:10-Ziel wurde nach Repositionierung des eigenen
Fensters erneut geprüft. Der Treiber prüft nun vor Klicks die Zielprozess-ID.
Keine Produktkorrektur aus diesem Umgebungsbefund abgeleitet.

Die kurze lokale [Informationsprobe](information.json) hat 1548 Assertions ohne
Fehler. Sie lief auf `f95c8b07f57576825de5ff98b2a58f2b27079b1d` mit identischem
Runtime-/Testcode und identischen PNGs; der finale Nachtrag ergänzt ausschließlich
Displaydokumentation und vorgeschaltete generative Herkunft. Die finale Package-CI
prüft den finalen Head/Testmerge gesondert. Lokaler Dokumentvalidator/Diffcheck
erfolgreich. Der lokale Windows-CI-Vertragstest hat einen unveränderten
Pfadseparatorbefund in `CORE_PATHS`; nicht als lokalen Gesamtpass ausgegeben.
Die reguläre Linux-CI liefert den verpflichtenden Kernnachweis.

Je 27 erfolgreiche Paketassertions: [Windows-PCK](pck-windows.json),
[synthetischer Web-PCK](pck-web.json), [regulärer Web-PCK](pck-regular-web.json).
Alle Alphabytes jedes importierten Titelbilds mit dem freigegebenen PNG verglichen,
einschließlich Alpha-1-Resten; Mipmaps, Maße, semantische Fallbacks ohne Duplikate,
exakte NOTICE-/Manifest-/Provenancebytes bestätigt. Der reguläre Webbuild besteht
zusätzlich Bundle-/Hash-/PCK-Grenzprüfung. Kein Chromium, Hosting oder Deployment.

[fit-comparison.json](fit-comparison.json) stellt die **tatsächlich gemessenen
neuen** Alpha-≥16-Höhen dem **rechnerischen alten BTI-A-Fit** gegenüber, kein alter
Windows-Neulauf: eng +23/+25 % bei Einstellungen/Hilfe, Katalog +54 %; große
Informationstitel etwa 1,9-fach, großer Katalog 2,34-fach. Sichere Navigation und
Scrollfläche haben im engen/Fehlerfall Vorrang vor weiterer dekorativer Größe.

[manifest.json](manifest.json) bindet die ausgewählten Dateien per Größe/SHA-256.
Binären Rückdownload und Öffnung dokumentiert der PR-Lieferkommentar am konkreten
Belegcommit. Produktdiff und Prüfauswahl bleiben ausschließlich BTI-C.

Diese technischen Belege und das getrennte Selbstreview sind keine unabhängige
BTI-C-R01-Abnahme oder persönliche Windows-Spielabnahme BTI-C-M01. Beide bleiben
vor Merge offen. Kein Merge beauftragt.
