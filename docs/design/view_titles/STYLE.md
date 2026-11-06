# BTI-C-1 · Stilquelle und Originale

Die drei Originale unter [view_titles](../../../game/art/drawing/view_titles/manifest.json)
bilden die gemeinsame Referenzfamilie für [BTI](../../VIEW_TITLE_ART.md).
Sie sind Implementierungskandidaten; die persönliche Freigabe erfolgt erst mit
BTI-A-M01 am gebundenen Spieler. Keine Freigabe aus der früheren Vergleichsskizze.

## Textunabhängige Grammatik

Eine Zeile eigenständiger organischer Kalligrafie, leichte Rechtsneigung,
unterschiedliche kräftige Abstriche und dünne Federzüge, gut erkennbare
Buchstaben, leicht unregelmäßige Grundlinie und Abstände. Warme sehr dunkle
braune Tinte mit feinen trockenen Graphit-/Pinselspuren nur innerhalb der Züge.
Umlaute gehören zum Wort. Keine eigene Ornamentik, Unterstreichung, Blätter,
Papierfläche, Icons, Schatten oder weitere Wörter. Kurze Wörter behalten ihre
Proportionen. Freigestellte vollständige Konturen mit transparenter Randreserve.
Die drei endgültig abgenommenen Titel können später als bildliche Referenz für
ausdrücklich separat beauftragte Wörter dienen.

## Tatsächlicher Herstellungsweg

Am 06.11.2026 mit dem eingebauten `image_gen.imagegen` erzeugt,
`transparent_background=true`. Modell-/Backendversion, Seed, Sampler und
weitere Parameter wurden vom Werkzeug nicht offengelegt. Ein Aufruf je Titel;
Hilfe referenziert das neue Katalogbild, Einstellungen die beiden neuen Bilder.
Keine fremde Bildvorlage, kein Font und keine frühere Chatdatei wurde eingelesen.
Die drei gelieferten PNGs sind zugleich die unbearbeiteten Masterquellen und
Exports; keine Vektorquelle vorhanden. Maße, Größen, Originaldateinamen und
SHA-256 stehen im Manifest. Keine manuelle Textkorrektur, Retusche oder
nachträgliche Freistellung/Neukodierung. Sichtkontrolle: alle drei Wörter,
insbesondere die beiden Umlautpunkte und die beiden l in Einstellungen.
Native UI-Größe und Alpha-Ränder werden separat im technischen Lieferbeleg geprüft.

Godot: verlustfreier Texture-Import, echte Alpha, Mipmaps, lineares Sampling.
Die Anzeige passt die sichtbare Alphahülle proportional in den Titelbereich
mit vier Pixeln Rand ein. Damit zentriert nicht ein ungleicher transparenter
Dateirand das sichtbare Wort. Originalbytes bleiben erhalten.

Reproduzierbarkeit meint eine konsistent erweiterbare Zeichenfamilie. Identische
Prompts/Referenzen garantieren keine pixelidentische Neugenerierung. Deshalb
bleiben Originale und Produktionsangaben dauerhaft erhalten; weitere Varianten
oder eine dauerhafte Reviewgalerie gehören nicht zur Quelle.
[Herkunftsnotiz](../../../game/art/drawing/view_titles/NOTICE.txt).

## Tatsächlich verwendete Prompts

### Katalog · ohne Bildinput

```text
Use case: stylized-concept. Create one production game UI title asset: only the exact German word “Rätselkatalog” (R ä t s e l k a t a l o g), one line. Bespoke organic calligraphic hand lettering, slight rightward lean, individual readable letters, expressive contrast between thick dry-brush downstrokes and thin pen strokes, gently irregular baseline, subtle graphite/dry-ink grain INSIDE strokes. Warm very dark brown ink. Quiet illustrated-book aesthetic, rough natural contour, not a computer font. Entire word including the two umlaut dots and all terminals visible. Wide composition with evenly tight transparent safety margins; suitable for a book page heading. Genuine transparent alpha background. Absolutely no paper, rectangular background, leaves, objects, ornaments, floating flourishes, separate underlines, frames, shadows, 3D block text, watermark, other words. The only visible pixels belong to the letters. High resolution lossless PNG. This is the first of a consistent family of three titles, with Hilfe and Einstellungen later.
```

### Hilfe · Katalogoriginal als Stilreferenz, num_last_images_to_include=1

```text
Use case: stylized-concept. Reference image is STYLE ONLY, not an edit target. Create a separate matching game book heading, exact word “Hilfe” (H i l f e), ONE word, ONE line. Match the reference's bespoke organic slightly italic dry brush calligraphy, warm very dark brown ink, thick/thin stroke contrast and internal graphite grain. Individual letterforms, subtle irregularity, immediately readable. Keep natural short-word proportions and similar capital/lowercase proportions as reference; do not stretch horizontally. Complete word with generous but tight even transparent safety margin all around. Genuine alpha transparent background. No underline, no detached flourishes, no leaves, no paper, no icons, no frames, no other text, no shadows, no background. Only visible letter pixels. Lossless high resolution PNG.
```

### Einstellungen · beide Originale als Stilreferenzen, num_last_images_to_include=2

```text
Use case: stylized-concept. Both input images are STYLE REFERENCES ONLY. Create the third separate matching book UI heading: exact German word “Einstellungen” (E i n s t e l l u n g e n). ONE word ONE line, complete letters including both l. Bespoke hand-drawn organic calligraphy matching reference warm very dark brown dry-ink/graphite lettering, light italic lean, variable thick/thin brush/pen strokes, softly irregular rhythm and internal fine texture. Clear legibility at small display size, not a rendered computer font. Wide natural composition, full word and all letter terminals inside frame with balanced transparent safety margin. Actual transparent alpha background. Nothing except letters: no underline, no independent flourishes or decorations, no paper/banner, no icons/leaves, no frames, no background, no shadows, no extra words, no 3D. High resolution lossless PNG.
```
