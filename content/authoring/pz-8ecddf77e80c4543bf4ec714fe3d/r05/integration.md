# Warnemünde r05 · Im Arbeitsbranch registriert

Die tatsächliche [Endabnahme](approval.json) bindet weiterhin das unveränderte
Inventar `8b506c2444cc98eda9d7c8dea7eb4bbb22eebd5fc549926bb07f6af46138aa34`.
Paket-SHA-256: `455540730bc87a3dbda5af59cc0bccc4d8892943d7f2ffd5a5321cca70605f6b`.
[Erweiterungs-/Integrations-/Mergeauftrag](tool-authorization-evidence.json),
[externe Autorisierung](manual-authorization.json), [Eigentümererklärung](owner-override.json).
Die spätere ausdrückliche Mergebeauftragung ersetzt das frühere Mergeverbot für
diese Lieferung; die ursprüngliche Endabnahme wird dafür nicht umgeschrieben.

**B-PZ-03 behoben:** ZA-1-v3 bindet die nachträgliche Motiv-/Parameterannahme extern.
Der Originalhandoff bleibt `raster_review` mit offenem historischem Motivgate.
Keine Neuversiegelung oder erfundene rückdatierte Annahme. Die bestehende
RP-3-/RP-5-Herkunft sowie beide festen Änderungen wurden frisch replayt:
260 Gebäudezellen, danach zwei Sonnenzellen. Die historische Regionsmaske bleibt
erhalten; eine zusätzliche exakte Maske schützt alle nicht gelisteten Positionen.
Maße, Palette, Randregel, Hinweise, Zwischen-/Endproofs und Endmatrix geprüft.
Der vollständige finale Proof bleibt bei 102 Schritten, unbekanntem Start und
exakter Singleton-Endmatrix. Schwierigkeit L2 geschätzt, L1–L4, Vertrauen niedrig;
keine Zeitprognose. Raster und Abschlussbild bleiben bytegleich zur Endabnahme.

**export → plan → register erfolgreich**, einschließlich interner Offlineprüfung:
[Export](integration-export.json), [konkreter Plan](integration-plan.json),
[Registrierung](integration-registration.json), [Dateikontrolle](integration-validation.json).
Runtime-ID `pz-8ecddf77e80c4543bf4ec714fe3d`, Runtime-Revision **1**,
Name **Warnemünde**, Slot/Stem **warnemuende_001**, Kategorie **Gebäude & Bauwerke**
(`gebaeude-bauwerke`). Der Katalog hat elf Einträge; die zehn bisherigen bleiben
unverändert. Runtime-Matrix/Hinweise entsprechen der abgenommenen Auswahl,
Reveal/Nutzungshinweis dem geprüften Export. Beide Gebäudesymmetrien und die
zwei Sonnenfarben nochmals an den übernommenen Zellen kontrolliert.

Neue allgemeine Regressionen verwenden ausschließlich künstliche Raster.
Bestehende Mono-/reguläre Adapterverträge bleiben erhalten. Der erste technische
Farbexportversuch deckte die größere historische Regionsmaske auf und stoppte
vor Ausgabe; die zusätzliche exakte Autorisierungsmaske wurde implementiert und
synthetisch geprüft. Kein ursprüngliches Paket dafür verändert.
Die frühere [Inkompatibilitätsdiagnose](export-attempt.json) bleibt als Verlauf.

Native Tests je Rätsel sind nicht erforderlich. Die wegen Werkzeugänderungen
ausgewählten allgemeinen Fach-/Spiel-/Exportregressionen sind ein separater
Pflichtnachweis. Aktuelle CI mit Head/Basis/Test-Merge, getrennter Selbstreview
und tatsächlicher Merge werden in PR113 geführt. Noch kein Main-Merge behauptet.
Danach folgt die Produktionsbereinigung nach Authoring §9 in einem eigenen Diff.
