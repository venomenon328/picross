# Deutsche Trennstellen für den Katalog

Produktfälle und Grenzen stehen in [Katalogdarstellung](CATALOG_PRESENTATION.md).

- Quelle: [Wortliste deutscher Wörter mit gewichteten Trennungen](https://github.com/hyphenation/languages-german/blob/4330a0b1254e88615cb4c83e4b3dc2f0810c76d9/wortliste),
  Commit `4330a0b1254e88615cb4c83e4b3dc2f0810c76d9` (01.05.2016),
  SHA-256 `55b457fac8e322146853f45bbda59046a55496a3e3deb32d3a88feb908eca243`.
  [Format und Trenngewichte](https://github.com/hyphenation/languages-german/blob/4330a0b1254e88615cb4c83e4b3dc2f0810c76d9/dokumente/README.wortliste).
- [MIT-Lizenz samt Copyright](../../game/data/hyphenation/LICENSE.txt), unverändert
  aus dem gepinnten Commit, SHA-256 `3dc8ca573654facf18b8046dad2fae36b8d0acb254ccea888c283c60c7b62c99`.
- Ableitung mit `python tools/derive_catalog_hyphenation.py wortliste game/data/hyphenation/de-1996.deflate`.
  Das Skript prüft den Quellhash, verwendet die reformierte Schreibweise und verlangt
  einen exakten Vollworttreffer mit identischer Schreibweise. Es überspringt
  mehrdeutige oder schreibungsändernde Formen sowie als ungünstig markierte
  Stellen. Bei mehrfach vorkommenden Formen behält es nur gemeinsame Stellen.
  Die Gewichtung bevorzugt unter passenden Stellen die Wortfuge.
- [Ausgelieferte Ressource](../../game/data/hyphenation/de-1996.deflate),
  1.828.775 Bytes, SHA-256 `59f8ffa6147be4a40b94ff0f6630e2cd5fdf49c90dfcf3687b4a31c551df870b`.
  Das zlib-komprimierte UTF-8-Lexikon enthält 445.382 nach exakter Wortform
  sortierte Einträge mit belegten Zeichenpositionen. Ein Treffer belegt die
  Wortform in dieser Liste. Unbekannte Schreibweisen, Eigennamen, neuere
  Komposita und abweichend geschriebene Wörter können ohne Treffer bleiben.
- Windows und Web enthalten Ressource und MIT-Text im PCK. Die regulären
  Spielerdateien liefern zusätzlich `licenses/GermanHyphenation-MIT.txt`.
  Der Webvalidator akzeptiert ältere WEB-1-Pakete auch weiterhin.
