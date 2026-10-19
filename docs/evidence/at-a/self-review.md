# AT-A · Getrennter Selbstreview

Stand 19.10.2026. Selbstreview des Implementierers, keine unabhängige
AT-A-R01-Abnahme. Basis: `9cc58651518e3a28e97f46932d69554210b0abcb`.
Die getrennte Diff-/Vertragsprüfung begann nach dem sauberen Windowsnachweis
auf `742f1837cf3a5600e4160c54744b87dfa88dcba1`; die folgenden Korrekturen gehören
zur selben Lieferung. Die abschließende Head-/Basis-/CI-Bindung steht im
[Draft-PR #263](https://github.com/venomenon328/picross/pull/263).

## Selbst geprüfter Umfang

Geprüft wurden der tatsächliche Gesamtdiff und die unveränderten Anschlussstellen
gegen AT/P01-D01–D07, ZA-1, Kategorien, SD-C1, Soll-CLI und CI-Policy:

- Geschlossene Quellen-, Freigabe-, Herkunfts- und Bindungsketten; historische
  Exportbindung neben wirksamen Bild-/Noticebytes; Register-No-op, Raster-Rebind,
  Cleanup, Sync, SD-/Added-Adoption und die jeweiligen Stale-Plan-Grenzen.
- Vollständige T/K-Mengen und erwartete Abwesenheiten; Namespace-, Pfad-, Link-,
  JSON-, Byte-, Zeit- und Revisionsgrenzen; vor Mutation erneut geprüfte Pläne.
- Unveränderte alte Journalgenerationen gegenüber genau acht Feldern der neuen
  Generationen; begrenzter Dispatch und Base64-Prüfung vor Decode; dauerhafte
  Journal-/Lockpublikation; P0–P6 und wiederholbares R0–R2 mit Fremddatenschutz.
- Tatsächliche Prozessabbrüche, OS-eigene unvollständige Pakettemps, binäre
  Altseiten und Runtime-v2/v3/v4. Unvollständige oder fremde Journale werden
  erhalten und blockieren; sie werden nicht als eigene vollständige Transaktion
  ausgegeben oder ungeprüft aufgeräumt.
- Synthetische RGBA-Quellen, tatsächliche Import-/Exportpfade, unabhängige
  Originalpixelprüfung, vollständige Artefaktinventare und Save-/Exportbindung.
  Der Probe-Code beobachtet den tatsächlichen Player; normale Spielerpakete
  enthalten weder Probe noch Testbilder.
- Scope und Dokumentkonsistenz: kein realer Kataloginhalt, keine Saveimplementierung,
  kein Inhalts-/Runtime-Schemawechsel, keine AT-B-Bildfreigabe und kein Deployment.

## Befunde und Nacharbeit

| Kennung | Auslöser und Auswirkung | Korrektur und Erfolgskriterium |
| --- | --- | --- |
| B-AT-SR01 · behoben | Snapshot und Journal leiteten Pfadmengen vor vollständiger Registryvalidierung ab. Falsche Objekttypen konnten interne Fehler auslösen. | Registry/Kategorien werden vor jeder Namespaceableitung validiert; Paketmanifest muss ein Objekt sein. Die Gegenprobe sperrt den Namespace-/Paketpfadzugriff und erwartet kontrolliertes `InvalidInput`; bestanden. |
| B-AT-SR02 · behoben | Ein Speicherabbruch und unhashbare Elemente eines manipulierten Namespaceplans brauchten kontrollierte CLI-/Typgrenzen. | `MemoryError` ergibt `aborted`, `resource_limit`, Exit 4. Namespaceelemente werden vor Mengenbildung auf Strings geprüft. Beide gezielten Gegenproben bestanden. |
| B-AT-SR03 · behoben | Die allgemeine Git-Textnormalisierung würde originale Windows-Logs beim Commit verändern. | Die Originalartefakte sind eng in `.gitattributes` von Textnormalisierung ausgenommen. Der Git-Index wird byteweise gegen die ursprünglichen Ausgaben geprüft. |

Eine zusätzlich geschlossene Nachweislücke betrifft gültige Runtime-v2/v3:
echte Bildadoption, unterbrochene Adoption mit Recovery und anschließendes No-op
erhalten Runtimebytes und deren mtime. Beide Versionen bestanden dieselbe Probe.
Bei unveränderter Runtime bleibt P5 eine prüfbare Grenze ohne künstlichen Rewrite.

Die Windows-Originalbilder wurden selbst visuell geprüft: neuer Bildfarbstand,
weißer Motivteil, transparente Innenfläche und weicher Ring bleiben sichtbar;
neue und begonnene Karten enthüllen das Bild nicht vorzeitig. Die Prozessfolge
wird durch PID plus tatsächliche Startzeit belegt, weil Windows einen PID nach
Prozessende erneut vergeben darf. Die sechs PNGs liegen unverändert bei.

## Urteil und Grenze

**Prüfung/Abnahme offen.** Die vollständige CI-Abschlussprüfung und ihre
Originalartefakte werden in [AT-A-T01](../../AT_A_VERIFICATION.md) gebunden.
Das unabhängige qualifizierte AT-A-R01 bleibt ein eigenes verpflichtendes Gate
vor Merge; dieser Selbstreview ersetzt es nicht. Merge, Deployment,
Issue-Abschluss und AT-B sind nicht Teil dieses Auftrags.
