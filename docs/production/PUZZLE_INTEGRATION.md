# RI: Zuverlässige und messbare Rätselintegration

Bei der gebundenen PW-Erstintegration liefert Schritt 5 die gewählten Dateien mit den vorhandenen Sichtungen, technischen Nachweisen und Erklärungen. Vor dem Schreiben die Quellbytes, das aktuelle Ziel und die Berechtigung prüfen. Die beiden Katalogprofile werden für die Erstregistrierung zusammen erzeugt.

## Geltung und Quellen

- **Status:** aktiver technischer Vertrag für aktuelle Inhaltsformen, Erstintegration und Recovery.
- **Fachliche Grenze:** [RI-ONE](PUZZLE_INTEGRATION_SINGLE_PATH.md); [Paketentscheidung #660](https://github.com/venomenon328/picross/issues/660#umsetzungsvorbereitung-ri-one).
- **Eingangsmanifest und CLI:** [ZA-1](ZA1_ADAPTER.md).
- **Hintergrundprofile und Capability:** ausschließlich [Hintergrundvertrag](PUZZLE_BACKGROUNDS.md#hg31--zwei-geschlossene-bildprofile); keine eigene Größen- oder Profildefinition in RI.
- **Historische Integrationen:** frühere RI-A/B/C- und v1–v10-Varianten sind abgelöst. Ihre Lieferstände in Git sind keine aktuellen Zulassungsregeln.

## Ein aktueller Eingang und Kern

`integration_input.Input` prüft `picross-integration-input-v1`. [ZA-1](ZA1_ADAPTER.md) beschreibt die geschlossenen Daten. `target_adapter`, Builder/Finalizer, Assistent und Integrationsbatch benutzen denselben Eingang. `catalog_integration.integrate` ist der einzige Erstintegrationskern; `content_registry.registration` delegiert darauf. `apply=False` plant lesend, `apply=True` prüft und plant selbst frisch. Ein früherer Plan ist keine Schreibautorität.

Finale Definition, Hinweise, Palette, expliziter Modus, aktuelles Reveal, Hintergrundpräferenz, Rechte, Metadaten, Bewertung, vollständiger unabhängig geprüfter Logiknachweis und tatsächliche Inhalts-/Integrationsentscheidung sind erforderlich. Vorhandenen gültigen Proof gegen das endgültige Raster prüfen; im Integrator läuft kein Suchsolver. Producer, alte Toolmodule, Original-ZIP, Reparaturgeschichte und historische Regelwerksstände sind keine Eingangsbedingungen.

## Inhaltsautorität und Zugriffsgrenze

Der vollständige Datenvertrag für `content/puzzles/<id>.json` steht in [RI-ONE §2](PUZZLE_INTEGRATION_SINGLE_PATH.md#2-aktuelle-inhalte-als-einzige-bestandsautorität). Das flache ID-Inventar und die eingecheckte Runtime v9 liefern den gemeinsamen abgeleiteten Index. Für bestehende IDs vergleicht der Kern die aktuelle Recordprojektion mit der Zeile des gebundenen Checkouts. Erstintegration prüft den vollständigen Eingang sowie Pfade, Slots, Kategorien, aktive Methode und die benötigte Capability. Der Vollcheck rekonstruiert jede Zeile einschließlich unsichtbarer Rätsel und vergleicht die Runtimebytes.

## Planung, Konflikt und Veröffentlichung

Identische aktuelle Entry-/Definitions-/Metadaten-/Bild-/Notice-/Hintergrund-/Bewertungsdaten ergeben einen No-op ohne neue Datumswerte, Bytes oder mtimes. Abweichende belegte ID erfordert einen separaten Änderungsauftrag. ID, Key, Slot, Definitionspfad und Bildstamm sind kollisionsfrei einschließlich Windows-Groß-/Kleinschreibung und reservierter Gerätenamen. Aktuelle Ressourcen liegen unmittelbar unter `data/content` bzw. `art/content`; es gibt keine freien externen Schreibziele.

Der gemeinsame Lock ist `content/.registration-pending.json`. Der aktuelle Erstintegrationswriter benutzt ausschließlich `picross-puzzle-registration-journal-v1` mit `format,id,dependencies,files`; `files` bindet alte/neue Bytes, `dependencies` die unveränderten gemeinsamen Quellen. Das Journal ist vor Nutzdaten fsynced und ohne Ersetzen publiziert. Es führt genau sieben Ziele bzw. neun mit ausgewähltem Hintergrund und 128 MiB. Neue Ziele dürfen keine vorhandenen Bytes ersetzen. Sichere temporäre Dateien, frischer Byte-/Lock-/Quellenvergleich, atomare Umbenennung und Readback gelten bei jedem Schritt. Runtime wird zuletzt publiziert.

Kontrollierte Eingabe-, Ressourcen- oder I/O-Fehler versuchen eine getrennt budgetierte Rückführung. Ein Prozessabbruch kann Journal/Staging hinterlassen. Recovery prüft ausschließlich das aktuelle Journal und seine erlaubten Deltas, die tatsächlichen Zwischenbytes, Abhängigkeiten und eigenen temporären Präfixe. Fremde oder nicht eindeutig eigene Bytes bleiben erhalten; ein blockierter Rollback ist kein Erfolg. Rückführung entfernt zuerst die neue Runtimezeile, danach werden eigene übrige Änderungen rückgängig gemacht. Wiederholte Recovery ist möglich; nach vollständigem Abschluss ist sie No-op. Alte Journalgenerationen werden nicht migriert oder interpretiert.

Separate Editor-/Metadaten-/Bewertungs-/Datums-/Methodenoperationen bleiben eigene fachliche Operationen am selben aktuellen Katalog. Sie haben ihre eigenen aktuellen Journale und teilen die Sperre, keinen alternativen Erstregistrierungswriter. Raster-/Bildänderungen bleiben im [Editorvertrag](../tools/PUZZLE_EDITOR.md).

## Budgets und Diagnose

Publikation und aktuelle Registrierungsrecovery haben getrennte endliche Defaults von je 1800 Sekunden, mit 300-Sekunden-Warnung. Vorab gewählte Overrides müssen endlich und positiv sein. Ein verbrauchter äußerer Publikationsrahmen darf die Rückführung nicht auf Restzeit verkürzen. Die Zeitgrenzen werden außerhalb injizierbarer Testcheckpoints geprüft. Andere fachliche Operationen behalten ihre eigenen Grenzen.

`--operation-report <neue-datei>` schreibt optional den tatsächlichen RI-Diagnosebefund außerhalb von Checkout/Eingang/Ausgabe. Er ist keine Katalogautorität. Inklusive Zeiten nicht addieren; fehlende Messungen bleiben als solche benannt. stdout enthält ein Ergebnis-JSON; Fortschritt und nicht zustellbare Diagnoseausgabe stehen auf stderr. Eine gescheiterte Berichtzustellung macht eine bereits dauerhafte Integration nicht rückgängig.

## Abschluss und Nachweise

Completion prüft denselben aktuellen Eingang gegen den wirklich registrierten Zustand und den gewählten Commit. Die Arbeitsprojektion darf die aktuelle Lieferung binden; daraus entsteht kein dauerhafter Integrationsreceipt. Nach bestätigtem Merge `origin/main` aktualisieren und [Authoring Schritt 5 §9](authoring/PUZZLE_AUTHORING_STEP_5.md#9-produktionsabschluss-und-bereinigung) ausführen. Frühere Phasen und gemeinsame Arbeit werden ausdrücklich anhand des tatsächlichen Verlaufs ausgewählt, niemals anhand kleinerer Revisionsnummern.

Aktuelle Prüfungen sichern neue Eingänge, No-op, Konflikte und begrenzte Recovery nach der jeweiligen CI-Auswahl. Der einmalige Bestands-/Aufwandvergleich und seine Nachweise stehen in [Issue #660](https://github.com/venomenon328/picross/issues/660) und der [damaligen Spezifikation](https://github.com/venomenon328/picross/blob/6fe91a08a4d073547df43c6aebbe8ead4c45ae0f/docs/PUZZLE_INTEGRATION.md#abschluss-und-nachweise). Daraus entsteht weder ein dauerhafter Legacyimporter noch ein Korpusreplay oder eine allgemeine Performancegarantie.
