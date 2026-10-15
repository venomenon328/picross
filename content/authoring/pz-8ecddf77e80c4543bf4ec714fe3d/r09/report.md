# Warnemünde · r08 als Runtime-Revision2 übernommen

Die vom Nutzer angenommene r08-Fassung ersetzt im Arbeitscheckout die bisherige
Spieldefinition. Integrationsverpackung r09, **keine neue Rasterfassung**:
Motiv-/Matrix-/Revealbytes identisch zu r08. 30×35, fünf Farben,390 gefüllte
Zellen. Vollständig deduktiv und eindeutig, frischer Linienproof140 Schritte.
[Raster](raster.png) · [Freigabe](approval.json) · [Paket](package.zip) ·
[Handoff](handoff.json) · [Updateplan](update-plan.json) · [Ergebnis](update-result.json) ·
[Dateiprüfung](validation.json).

Runtime-ID `pz-8ecddf77e80c4543bf4ec714fe3d`, Revision2, Slot/Dateistamm `warnemuende_001`, Kategorie
`gebaeude-bauwerke`. Genau ein Katalogeintrag; andere Rätsel unverändert.
Abschlussbild, Nutzungshinweise und Runtime-Registryprojektion bytegleich.
Alter kompakter r05-Beleg und versiegelte r06/r07/r08 bleiben unverändert.
Alte Save-Dateien werden nicht angefasst; wegen abweichender Runtime-Revision
sind ihre Inhalte nicht auf das neue Raster anwendbar.

Export mit tatsächlicher Freigabe und frischer unabhängiger Quellen-/Proofprüfung
bestanden. Lesender Updateplan geprüft, anschließend explizites `update` mit
Erwartungshash der alten Definition `4e37b8adba11be71e4a8870a1ffdfa7ca6ebab1e16c816554316be6db9ca9f1b`.
Update vollständig registriert, Dateihashes geprüft, kein offenes Journal.
Keine handgeschriebene Registry oder umetikettierte historische Motivfreigabe.
Neue Verpackung bindet die tatsächliche Annahme vor einem frischen Direktimport.

Paket-SHA `ef51f857908005fae7986063c8d64a83a773395b75a37c077a8a20270522f030`.
Inventar `cec8ba9d03ac7e7f85a648e1a022ae31a5f6392f08c61f202feb5f7ead2816d4`.
Exportmanifest `7422e24fde86d1614455834ad647beb0138ce784bc5fd30d829481be9030c23c`.
Reine Inhaltsintegration: keine verpflichtende native Rätselprobe oder neuer
Spielerbuild. Die notwendige allgemeine Achtfarb-/Updatecodeprüfung läuft separat
in [Draft-PR146](https://github.com/venomenon328/picross/pull/146).
Inhalts-DraftPR142 basiert auf dessen Branch; zuerst technische Voraussetzung
abnehmen/mergen, dann PR142 auf main umstellen. **Kein Main-Merge ausgeführt.**
