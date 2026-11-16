# SD-Catalog: Aktuelle Bewertung und getrennte Katalogpflege

**RI-ONE · 16.11.2026.** [Issue #660](https://github.com/venomenon328/picross/issues/660#umsetzungsvorbereitung-ri-one) und [RI](PUZZLE_INTEGRATION.md) ersetzen historische Integrations-/Recoverygenerationen dieses Vertrags. Difficultyalgorithmen, Methodendefinitionen, Kalibrierungen, Labels und fachliche Abnahmegrenzen bleiben unverändert. Maßgeblich dafür sind [SD](PUZZLE_DIFFICULTY.md), [SD2](PUZZLE_DIFFICULTY_V2.md) und [SD2-Integration](SD2_INTEGRATION.md).

## Aktive Hülle und geprüfter Arbeitsinput

Neue Integration und neue Ratingadoption verwenden `picross-current-difficulty-v1` mit exakt `format,method,production_mode,current_source,logic_binding,rating,compact_analysis,rating_revision,record_hash`. `production_mode` ist der ausdrücklich übernommene aktuelle Modus, keine Herkunft und keine Ableitung aus der Palettengröße. `rating_revision` ist positiv, `record_hash` bindet alle übrigen kanonischen Felder. `current_source` und `logic_binding` binden die endgültige Definition und deren logischen Inhalt. `rating` und `compact_analysis` behalten die gültigen geschlossenen Werteformen der angegebenen Methode 0.3 oder 0.4.

`current_rating.validate` prüft Form, Werte, Hashes, Methodenkonsistenz, Definition/Modus, Geometrie, Hinweise und erforderliche R4-Profile. Ein aktueller gültiger vollständiger Bewertungsbefund ist erforderlich. `current_rating.from_checked` übernimmt die bereits tatsächlich geprüften Werte des bestehenden Analyzers in diese Hülle; es berechnet keine neue Bewertung und erfindet keine Herkunft. Ein Analyzer-Checked-Bericht ist Arbeitsmaterial. Der aktuelle Integrator verlangt weder dessen historischen Producer noch Werkzeugdateien, alte Quellenbilder oder einen Originalexport.

Aktive Bestandsratings bleiben bei der einmaligen Bestandsumstellung bytegleich, einschließlich bestehender Methodenmischung und Bewertungsrevision. Die aktiven Dateien werden direkt anhand ihrer aktuellen Werte und Definitionsbindung gelesen. Keine Bericht-/Produktionshistorie wird nachgespielt. Neue Neuregistrierungen verlangen die heute aktive Defaultmethode; identische bereits registrierte Ergebnisse werden durch eine spätere Defaultänderung nicht automatisch neu bewertet.

## Quellenpriorität und Projektion

Aktuelle Definition und expliziter Entry-Modus sind die Eingänge einer ausdrücklich beauftragten Neubewertung. Neue Rasterlogik verlangt passende neue Analyse und vollständigen unabhängigen Proof. Reine Namens-/Kategorie-/Bildänderungen dürfen vorhandene Bewertung, Added-Datum und Saves nicht ändern. Runtime v8 enthält ausschließlich die bestehende kleine Projektion; keine Produktionsnotizen oder Werkzeughüllen werden ins Spiel projiziert.

`catalog_rating.load_sources` liest die aktuellen Ratingdateien der gewählten Katalogautorität. `catalog_added.load_sources` liest die aktuellen Datumsdateien; alte Referenzen im gespeicherten Datum sind keine Pflicht zum erneuten Lesen früherer Reports. Fehlende/ungültige erforderliche aktuelle Werte sind Fehler, kein Fallback auf `entry.production`.

## Auswahlbericht und getrennte Übernahme

`catalog_analysis.preview` erzeugt die explizite Auswahl und tatsächlich geprüften Vorschauwerte; `adopt` übernimmt nur die unveränderten geprüften Daten. Neue aktuelle Quellenbindungen schließen aktuelle Indizes, Definitionen, Bildsources, Ratings, Added-Dateien und aktive Methode ein. Gespeicherte Pläne werden vor Mutation frisch verglichen. Gleiche bereits übernommene Werte/Reports sind No-op; Konflikte werden nicht neu berechnet oder überschrieben. Abgebrochene Analyse behält die bisherige aktive Bewertung und darf kein L5 erfinden.

Methodenaktivierung ist eine eigene ausdrückliche Operation. Der neue Defaultrecord bindet Vorgängerhash und nächste Revision. Sie ändert keine bisherigen Ratings. Datumsrekonstruktion bleibt eine eigene beauftragte Operation mit überprüfbarem aktuellen Plan und den tatsächlich verfügbaren historischen Datumsbelegen; sie ist keine Registrierung oder Produktionswiederholung.

## Aktuelle Katalogjournale

`picross-current-catalog-journal-v1` enthält `format,operation,report_run,old,new,retained,additions,replacements`. `additions` und `replacements` sind leer: dieser Writer schreibt ausschließlich kleine aktuelle Katalogtexte. Zulässig sind `metadata`, `adoption`, `added-adoption`, `method-activation` und `sync`; jede Operation hat ihre geschlossene Dateimenge und erlaubten Deltas. Keine neue ID, keine Definitions-/Bildänderung und kein alternativer Erstregistrierungsweg.

Alte/neue Ansichten werden vollständig aus den aktuellen Daten projiziert. Definitionen, aktive Bilder und alle nicht autorisierten Werte bleiben gebunden. Gemeinsamer Lock, dauerhaftes Journal vor Mutation, frischer Phasenvergleich, atomare Schreibvorgänge, Readback und Runtime zuletzt gelten. Recovery prüft eigene tatsächliche Alt-/Neu-/temporäre Bytes und unveränderte Abhängigkeiten, erhält Fremdänderungen und ist wiederholbar. Alte Journalgenerationen werden nicht unterstützt.

Gezielte Editoränderungen benutzen den eigenen kleinen aktuellen [Editorplan und sein Journal](PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung). Erstintegration benutzt ausschließlich den [aktuellen RI-Writer](PUZZLE_INTEGRATION.md). Die ehemaligen gemeinsamen Export-/Package-/Receiptmatrizen sind abgelöst.

## Nachweise und Lebenszyklus

Kleine synthetische Fälle prüfen aktuelle Bewertung/Modebindung, beide Methoden, explizite Aktivierung, Adoption/No-op, Metadaten-/Bildpflege und Recovery. Der reale RI-ONE-Bestandsvergleich hält alle bisherigen Bewertungs-/Datumsbytes und Runtimeprojektionen fest. Keine automatische Neubewertung, kein echter Savezugriff und kein dauerhafter Korpusreplay. Historische Lieferstände sind über Git erreichbar und keine neuen Readerpflichten.
