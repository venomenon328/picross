# Warnemünde r05 · Endabnahme gebunden, Integration blockiert

Die tatsächliche Endabnahme des Nutzers für **r05**, Inventar
`8b506c2444cc98eda9d7c8dea7eb4bbb22eebd5fc549926bb07f6af46138aa34`,
ist in [approval.json](approval.json) separat an Originalhandoff, Auswahl,
Matrix, Logik und Abschlussbild gebunden. [Wortlaut und Herkunft](acceptance-evidence.json)
halten auch den Integrationsauftrag, Draft-PR und das Mergeverbot fest.
Die UTC-Zeit bezeichnet die Protokollierung, keine erfundene Nachrichtensendezeit.

[Dateiprüfung](acceptance-validation.json): ZIP-Grenzen, sichere Dateinamen,
CRC, vollständige Dateimenge, alle 101 Dateigrößen/Hashes, Handoffkopie und
Auswahlbindungen bestanden. ZIP, Handoff, Inventar, Bilder und Produktionsbelege
bleiben unverändert. Die technischen Produktionsprüfungen sind in
[validation.json](validation.json) und im versiegelten Paket dokumentiert;
hier wird kein erfolgreicher neuer ZA-1-Prüflauf behauptet.

## B-PZ-03 · Versiegelter Korrekturstand hat keinen passenden Adaptereingang

Der tatsächliche [Exportversuch](export-attempt.json) mit der echten Endabnahme
stoppt bei `Package is not content_ready`. Ursache ist die vorherige Paketerstellung:
Codex hat r05 als `raster_review` mit offenem Motivgate, `motif.approval=null`
und leerem `approved_parameters` versiegelt. Die jetzt vorliegende menschliche
Endabnahme ist gültig; der aktuelle Adapter kann diese Angaben für diesen Eingang
aber nicht über separate Freigabebelege schließen.

`tools/puzzle_production/authoring_package.py` akzeptiert regulär nur
`content_ready`, `editorially_approved` oder `catalog_ready`. Seine begrenzten
historischen Ausnahmen gelten für andere manuelle Eingänge.
`target_adapter.py` erwartet zusätzlich inventarisierte Motivfreigabe und
Parameter. `--approval` bindet ausschließlich die Endabnahme. Der vorhandene
manuelle Autorisierungsweg unterstützt feste monochrome Edits; r05 ist ein
Vierfarbraster mit `candidate.source_type=import` und dem gesonderten
Begleitfeld `editorial_manual_derivation`. Es ist kein kompatibler v1/v2-Eingang.

Ein Umschreiben des Originalhandoffs würde die freigegebene Inventarbindung
verletzen. Ein neues versiegeltes Paket hätte eine andere Bindung. Ein äußerer
Record mit anderem Status allein ändert den Adaptereingang nicht.

## Konkrete getrennte Nacharbeit zur Beauftragung

Den ZA-1-Vertrag um einen eng begrenzten, extern autorisierten Weg für bereits
versiegelte feste Farbkorrekturen erweitern. Die Entscheidung soll exakt den
hier abgenommenen Inhalt und seine gespeicherte Herkunftskette erfassen:

- Original-ZIP, Handoff und Inventar bytegleich erhalten; externe menschliche
  Erklärung an Paket, ausgewählten Kandidaten, Matrix/Logik, Reveal und echte
  Endabnahme binden. Den akzeptierten Motivstand MR-r04 und den bereits
  vorgeschlagenen Korridor 30×40, color, vier Vordergrundfarben, area, exact,
  Crop `[0,0,30,40]` ausdrücklich führen. Keine rückdatierte Freigabe erfinden.
- Die gespeicherte feste Ableitungskette bis r05 einschließlich Gebäudesymmetrie
  und Sonnenkorrektur frisch replayen: tatsächliche Vorwerte, exakte Edits,
  Schutz aller anderen Zellen, Referenz-/Quellenbindungen und Endmatrix.
  Kein Suchen nach einer anderen Matrix oder Ersetzen des Abschlussbildes.
- Alle Inhaltsgates weiter prüfen: Herkunft, Rechte, Palette, Maße, Randregel,
  deterministische Hinweise, vollständiger unabhängiger Proof und exakte
  Enddomains. Historische Metadaten und nachträgliche menschliche Annahme im
  Prüfbericht getrennt zeigen; kein allgemeiner Force-Schalter.
- Externe Belege offline mitliefern und bei Exportprüfung, Plan und Register
  erneut binden. Vorhandene reguläre und monochrome Wege kompatibel halten.
  Allgemeine Regressionen ausschließlich mit synthetischen Eingängen;
  dieses Rätsel nicht in Tests oder CI aufnehmen.

Nach dieser technischen Nacharbeit den bestehenden Integrationsauftrag mit
`export → plan → register` fortsetzen. Geplante Runtime-ID ist unverändert
`pz-8ecddf77e80c4543bf4ec714fe3d`, Runtime-Revision **1**, Name **Warnemünde**,
Stem/Save-Slot **warnemuende_001**, Kategorie **gebaeude-bauwerke**.
Diese Angaben sind noch keine Registrierung. Kein Exportziel wurde erzeugt;
Plan/Register wurden nicht ausgeführt, Runtime und Registry bleiben unverändert.
Eine erneute Endabnahme desselben unveränderten Inventars ist nicht erforderlich.

Die technische Erweiterung ist noch **nicht beauftragt oder implementiert**.
Grund: [PUZZLE_AUTHORING §1.5](../../../../docs/ai-workflows/PUZZLE_AUTHORING.md)
legt fest: „Werkzeugänderungen, Merge und Veröffentlichung sind jeweils getrennte
Befugnisse nach Entwicklungsworkflow.“ Der Produktions- und Integrationsauftrag
erlaubt die Paketsicherung und Abschnitt 8, erweitert aber nicht automatisch
den technischen Autorisierungsvertrag.

Draft-PR **113**, kein Merge. Native Spiel-/PCK-Prüfungen sind für diesen reinen
Inhaltsstand nicht erforderlich. Separate Dateibindungs-/Diff-Selbstprüfung und
die aktuellen Pflichtchecks werden im PR für den tatsächlichen Head ausgewiesen.
