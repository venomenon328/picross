# SL-65 · gezeichnete Sidebarrahmen

Erzeugt am 10.10.2026 mit dem nativen ChatGPT-Bildwerkzeug (`image_gen.imagegen`,
transparenter Hintergrund). Kein externes API-Skript, kein API-Key und keine
Modellkennung bekannt. Das unveränderte gewählte [Original](original.png) ist
1254×1254 RGBA, SHA-256
`9e7f10b394caf8cd6b89eb7c990fe443d113286a7ac873ca730b1938ea1c4e33`.
Zwei zusätzlich erzeugte hohe Kandidaten wurden wegen flächiger Ränder verworfen;
sie gehören weder zum Produkt noch zur Beweisgrundlage.

## Verwendeter Bildauftrag

> Create a production game UI bitmap asset, a single square hand-drawn pencil frame on a genuinely transparent background, including completely transparent interior. Warm dark graphite / muted brown ink, calm sketchbook style. An organic slightly crooked freehand square outline, subtly uneven hand pressure, a few delicate diagonal pencil hatching strokes outside the outline fading progressively into transparency. No ruler geometry, no solid panel, no paper texture, no text, no icons, no symbols, no objects, no internal shading. Frame centered, approximately from 12% to 88% of image in both axes; keep the central 70% square fully empty/transparent. All hatching stays outside the outline, fades out before the image edges; leave 3% transparent outside padding. Intended to frame a small puzzle preview and color palette over an existing illustrated book. The frame will display about 130 pixels wide; use clearly legible thin dark principal strokes and restrained hatching, avoiding fuzzy heavy shadows. Output one square asset only.

## Technische Ableitung

Vor Bildherstellung geplant: freie Werkzeugfläche 92×140 × UI (44px Treffer,
4px Abstand), Palette 44²/98² × UI und Miniatur 100²/132² × UI. Rahmen brauchen
zusätzlichen Außenraum; das alte Acht-Button-Layout ist keine verfügbare Fläche.

`python tools/sidebar_assets.py` reproduziert mit Pillow 12.3 die drei PNGs und
`frames.json`. Nur technische Aufbereitung: Alpha ≤1 entfernen, den freien
Innenbereich (210,205)–(1050,1040) von losen Schraffurpartikeln freistellen,
Alpha-Hülle (97,105)–(1154,1148) beschneiden, mit Lanczos skalieren. Kein neuer
Strich wird programmgeneriert. Die hohe Werkzeugableitung skaliert dieselbe
organische Zeichnung; kein Nine-Patch. Sicherheitsrechtecke sind gegenüber dem
Original um mindestens drei Ableitungspixel eingerückt und symmetrisch zur
beschnittenen sichtbaren Hülle. PNG-/Pixelhashes, Maße, Alpha-Hülle und freier
Innenraum stehen im [aktiven Manifest](../../../prototypes/p1/art/book/frames.json).
Der Pixelhash setzt ausschließlich unsichtbare RGB-Kanäle bei Alpha 0 auf 0.
Die drei versionierten Importvorgaben deaktivieren Godots Randfarbreparatur,
damit die gezeichneten semitransparenten Pixel unverändert bleiben. Im fertigen
knappen Layout ist die Miniatur 86×UI groß; der zusätzliche Abstand zur Palette
und zum Werkzeugrahmen hält deren gesamte Alpha-Hüllen getrennt.

Die eigene Herkunft wird separat vom historischen BP-3-Hintergrund ausgewiesen.
Keine fremde Referenz oder eingebrannte Schrift, kein Spielinhalt im Bildauftrag.
