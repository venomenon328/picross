# RI: Zuverlässige und messbare Rätselintegration

**RI-ONE · 16.11.2026.** Maßgeblich sind [Issue #660](https://github.com/venomenon328/picross/issues/660#umsetzungsvorbereitung-ri-one) und der [freigegebene gemeinsame Vertrag](PUZZLE_INTEGRATION_SINGLE_PATH.md). Dieser Vertrag ersetzt die bisherigen RI-A/B/C- und v1–v10-Integrationsvarianten. Historische Lieferstände sind über Git erreichbar und keine aktuellen Zulassungsregeln.

## Ein aktueller Eingang und Kern

`integration_input.Input` prüft `picross-integration-input-v1`. [ZA-1](ZA1_ADAPTER.md) beschreibt die geschlossenen Daten. `target_adapter`, Builder/Finalizer, Assistent und Integrationsbatch benutzen denselben Eingang. `catalog_integration.integrate` ist der einzige Erstintegrationskern; `content_registry.registration` delegiert darauf. `apply=False` plant lesend, `apply=True` prüft und plant selbst frisch. Ein früherer Plan ist keine Schreibautorität.

Finale Definition, Hinweise, Palette, expliziter Modus, aktuelles Reveal, Hintergrundpräferenz, Rechte, Metadaten, Bewertung, vollständiger unabhängig geprüfter Logiknachweis und tatsächliche Inhalts-/Integrationsentscheidung sind erforderlich. Vorhandenen gültigen Proof gegen das endgültige Raster prüfen; im Integrator läuft kein Suchsolver. Producer, alte Toolmodule, Original-ZIP, Reparaturgeschichte und historische Regelwerksstände sind keine Eingangsbedingungen.

## Inhaltsautorität und Zugriffsgrenze

`content/registry.json` verwendet `picross-content-registry-v5`: exakt `format,entries,metadata,backgrounds`. Jeder Entry enthält exakt `id,key,save_slot,definition,reveal,visible,mode,category_id`. `mode` ist ausdrücklich `mono|color`; einfarbiges Color bleibt Color. `production` und Paket-/Receiptfelder entfallen. Die sortierten Metadaten und Hintergrundrefs führen alle IDs genau einmal.

Aktuelle Reveal-/Hintergrundsources verwenden v5/v7 und enthalten `format,id,record_revision,binding,current,record_hash`. `binding` enthält ausschließlich `identity`: `key,save_slot,definition` als Ref und `runtime_revision`. `current` enthält `image_revision,asset`, beim Hintergrund zusätzlich `status=selected|none|standard`. Ein Ref hat `file,bytes,sha256`. Der `record_hash` ist der kanonische Hash aller übrigen Felder. PNG/SVG-Reveal und ausgewähltes Hintergrund-PNG bleiben durch aktuelle Bytes gebunden. Notices erhalten die benötigten Rechte.

Runtime bleibt bytekompatibel v8. Aktive Bewertungen, Added-Daten, Metadaten, Slots und Revisionen werden bei der Bestandsumstellung nicht neu berechnet. Historische gültige Ratinghüllen dürfen aktuelle Werte tragen; ihre Produktionsschritte werden nicht wiederholt. Neue Bewertungen verwenden [SD-Catalog](SD_CATALOG.md).

Ein Integrationsaufruf liest die gemeinsamen Indizes, Kategorien, aktive Methode, Capability und ausschließlich die betroffene ID sowie den vollständigen neuen Eingang. Keine fremden Paket-/Bildbäume, Archive, historischen Tooldateien oder vollständige Katalogaufnahme vor `register`, No-op, Batch-Ergebnisprüfung oder Resume. Ein expliziter Gesamtkatalogcheck und eine ausdrücklich gewählte Gesamtbewertung bleiben eigene Operationen.

## Planung, Konflikt und Veröffentlichung

Identische aktuelle Entry-/Definitions-/Metadaten-/Bild-/Notice-/Hintergrund-/Bewertungsdaten ergeben einen No-op ohne neue Datumswerte, Bytes oder mtimes. Abweichende belegte ID erfordert einen separaten Änderungsauftrag. ID, Key, Slot, Definitionspfad und Bildstamm sind kollisionsfrei einschließlich Windows-Groß-/Kleinschreibung und reservierter Gerätenamen. Aktuelle Ressourcen liegen unmittelbar unter `data/content` bzw. `art/content`; es gibt keine freien externen Schreibziele.

Der gemeinsame Lock ist `content/.registration-pending.json`. Der aktuelle Erstintegrationswriter benutzt ausschließlich `picross-current-registration-journal-v1` mit `format,id,dependencies,files`; `files` bindet alte/neue Bytes, `dependencies` die unveränderten gemeinsamen Quellen. Das Journal ist vor Nutzdaten fsynced und ohne Ersetzen publiziert. Es führt höchstens zwölf Dateien und 128 MiB. Neue Ziele dürfen keine vorhandenen Bytes ersetzen. Sichere temporäre Dateien, frischer Byte-/Lock-/Quellenvergleich, atomare Umbenennung und Readback gelten bei jedem Schritt. Runtime wird zuletzt publiziert.

Kontrollierte Eingabe-, Ressourcen- oder I/O-Fehler versuchen eine getrennt budgetierte Rückführung. Ein Prozessabbruch kann Journal/Staging hinterlassen. Recovery prüft ausschließlich das aktuelle Journal und seine erlaubten Deltas, die tatsächlichen Zwischenbytes, Abhängigkeiten und eigenen temporären Präfixe. Fremde oder nicht eindeutig eigene Bytes bleiben erhalten; ein blockierter Rollback ist kein Erfolg. Rückführung entfernt zuerst die neue Runtimezeile, danach werden eigene übrige Änderungen rückgängig gemacht. Wiederholte Recovery ist möglich; nach vollständigem Abschluss ist sie No-op. Alte Journalgenerationen werden nicht migriert oder interpretiert.

Separate Editor-/Metadaten-/Bewertungs-/Datums-/Methodenoperationen bleiben eigene fachliche Operationen am selben aktuellen Katalog. Sie haben ihre eigenen aktuellen Journale und teilen die Sperre, keinen alternativen Erstregistrierungswriter. Raster-/Bildänderungen bleiben im [Editorvertrag](PUZZLE_EDITOR.md).

## Budgets und Diagnose

Publikation und aktuelle Registrierungsrecovery haben getrennte endliche Defaults von je 1800 Sekunden, mit 300-Sekunden-Warnung. Vorab gewählte Overrides müssen endlich und positiv sein. Ein verbrauchter äußerer Publikationsrahmen darf die Rückführung nicht auf Restzeit verkürzen. Die Zeitgrenzen werden außerhalb injizierbarer Testcheckpoints geprüft. Andere fachliche Operationen behalten ihre eigenen Grenzen.

`--operation-report <neue-datei>` schreibt optional den tatsächlichen RI-Diagnosebefund außerhalb von Checkout/Eingang/Ausgabe. Er ist keine Katalogautorität. Inklusive Zeiten nicht addieren; fehlende Messungen bleiben als solche benannt. stdout enthält ein Ergebnis-JSON; Fortschritt und nicht zustellbare Diagnoseausgabe stehen auf stderr. Eine gescheiterte Berichtzustellung macht eine bereits dauerhafte Integration nicht rückgängig.

## Abschluss und Nachweise

Completion prüft denselben aktuellen Eingang gegen den wirklich registrierten Zustand und den gewählten Commit. Die Arbeitsprojektion darf die aktuelle Lieferung binden; daraus entsteht kein dauerhafter Integrationsreceipt. Nach bestätigtem Merge `origin/main` aktualisieren und [Authoring Schritt 5 §9](ai-workflows/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung) ausführen. Frühere Phasen und gemeinsame Arbeit werden ausdrücklich anhand des tatsächlichen Verlaufs ausgewählt, niemals anhand kleinerer Revisionsnummern.

T01 deckt kleine aktuelle Fälle und gezielte Fremdänderungen/Unterbrechungen ab. T02 vergleicht den tatsächlichen Startbestand, sämtliche wirksamen Werte und Livebytes sowie die schreibfreie Wiederholung. T03 verwendet dieselben kleinen Mono-/Colorfälle in derselben Umgebung vor/nach Umstellung und erfasst Zeit und Zugriffe. Die einmaligen Rohbelege und das temporäre Übergangsskript werden für RI-ONE-A01 separat zugestellt; kein dauerhafter Legacyimporter, kein Korpusreplay und keine neue Performancegarantie.
