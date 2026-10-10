# Archiv der historischen BP-Lieferpakete

Stand: 09.10.2026 · [CI-Bereinigung #63](https://github.com/venomenon328/picross/issues/63)

BP-1R, BP-2 und BP-3 sind abgeschlossene Entwurfs- und Lieferstände. Ihre drei
Review-ZIPs und 133 abgeleitete Bild-/Kontrolldateien werden nicht mehr bei jedem
Checkout mitgeführt oder als alte Lieferpakete erneut geprüft. Die **136 Dateien
mit zusammen 161.102.998 Bytes** bleiben unverändert im Git-Commit
`fad885344874534629365917a2ab6a8d311cd3a7` verfügbar. Die Git-Historie wurde nicht
umgeschrieben.

[ARCHIVE.json](ARCHIVE.json) führt jeden ursprünglichen Repositorypfad, seine
Git-Blob-SHA, Dateigröße und den unveränderlichen Dateilink auf. Die Blob-SHA ist
die Git-Objektkennung einschließlich Blob-Header, kein einfacher SHA-1-Dateihash.
Die Einträge sind nach Pfad sortiert; die Summe und Dateizahl stehen im Kopf.

## Vollständige historische Lieferungen

| Paket | Gebundenes Review-ZIP | Ursprüngliche Anleitung |
| --- | --- | --- |
| BP-1R · Vorlage | [bp1r-review.zip](https://github.com/venomenon328/picross/blob/fad885344874534629365917a2ab6a8d311cd3a7/docs/design/book_inventory/production/bp1r-review.zip) | [README](https://github.com/venomenon328/picross/blob/fad885344874534629365917a2ab6a8d311cd3a7/docs/design/book_inventory/production/README.md) |
| BP-2 · Hintergründe | [bp2-review.zip](https://github.com/venomenon328/picross/blob/fad885344874534629365917a2ab6a8d311cd3a7/docs/design/book_inventory/artwork/bp2-review.zip) | [README](https://github.com/venomenon328/picross/blob/fad885344874534629365917a2ab6a8d311cd3a7/docs/design/book_inventory/artwork/README.md) |
| BP-3 · Komposition | [bp3-review.zip](https://github.com/venomenon328/picross/blob/fad885344874534629365917a2ab6a8d311cd3a7/docs/design/book_inventory/composition/bp3-review.zip) | [README](https://github.com/venomenon328/picross/blob/fad885344874534629365917a2ab6a8d311cd3a7/docs/design/book_inventory/composition/README.md) |

Das jeweilige ZIP vollständig herunterladen und separat entpacken. Die BP-3-Galerie
funktioniert mit dem darin enthaltenen `index.html` und den ebenfalls enthaltenen
Bildern ohne Server. Einzelne Bilder sind über das Archivmanifest erreichbar.

Native Originalbilder, finale Hintergrunddateien, SVG-Quellen, Font-/Iconinputs,
Lizenzen und historische Manifeste bleiben im aktuellen Baum erhalten. Die
Manifeste beschreiben weiterhin ihre ursprünglichen vollständigen Pakete; sie
werden nicht auf die reduzierte Archivansicht umgeschrieben. Die Ressourcenprüfung
des aktuellen Spiels verwendet weiterhin seine vorhandenen Runtime-Dateien,
Fontbindings und den gewählten A-Hintergrund. Fachliche RP-/VS-Quellen und Proofs
sind von dieser Archivierung nicht betroffen.

## Historischen Lieferstand gezielt prüfen

Die vollständigen alten Lieferprüfungen laufen ausschließlich in einer separaten
Arbeitskopie des gebundenen Commits. Aus dem heutigen Repository zuerst genau
den Archivstand und die drei von den alten Prüfern verwendeten Quellcommits holen:

```sh
git fetch --no-tags --depth=1 origin fad885344874534629365917a2ab6a8d311cd3a7 0d3ad6a921578f94b3249ab83fbb215721549dfb 4ef926fe033418090512d82b9aba151031534c5f 66b9d39dd3dbce908ff663a18c059351cfccf557
git worktree add --detach ../picross-bp-archive fad885344874534629365917a2ab6a8d311cd3a7
cd ../picross-bp-archive
python3 tools/book_inventory/production.py verify
python3 tools/book_inventory/artwork.py verify
python3 tools/book_inventory/composition.py verify
```

Der Zielordner muss neu sein. Die vorhandenen Originaldateien werden geprüft,
nicht neu gerendert. Python 3.11 oder neuer und die Standardbibliothek reichen
für diese drei historischen Verifikationen; Bildgenerierung, Browser und neue
Fontdownloads sind dafür nicht erforderlich. Die ursprünglichen vollständigen
Testdateien liegen ebenfalls in diesem Checkout. Im aktuellen Standardlauf
bleiben ihre kleinen Geometrie-, Navigations-, Alpha- und Korruptionsprüfungen
aktiv; die drei umfassenden Paketprüfungen entfallen.

Ein erfolgreicher historischer Lauf belegt diesen alten Lieferstand. Er ersetzt
keine Prüfung oder Abnahme der aktuellen Spielfassung. Die bisherigen Review-
und Abnahmeaussagen bleiben an ihre ursprünglichen Commits gebunden.
