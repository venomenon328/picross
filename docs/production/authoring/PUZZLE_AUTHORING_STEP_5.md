# Schritt 5: Abschluss und Integration

**Version 0.8.0 · Dokumentrevision 10 · 17.11.2026 · PROD-SLIM**

Pflicht: [Kern und Phasenroute](PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase),
danach diese Phase. Vorhandene passende Bild-/Rasterbelege verwenden; ihre
Produktion nicht wiederholen. Sicherung, Wiederaufnahme, Bildkorrektur und
Abschlussausgabe folgen Kern §§6–7.

## 8. Abgenommenes Ergebnis ins Spiel integrieren

Vor Benutzung [RI](../PUZZLE_INTEGRATION.md), den aktuellen Eingang in [ZA-1](../ZA1_ADAPTER.md) und die passende CLI-Anleitung lesen. Schritt 5 setzt vollständige aktuelle Raster-/Hintergrundbereitschaft und tatsächliche Endfreigabe voraus. Bestehende gültige Entscheidungen verwenden, fehlende Entscheidungen niemals technisch erzeugen. Der Finalizer führt vorhandene tatsächliche Entscheidungen im einen aktuellen Record nach; Arbeitsmaterial ist keine Katalogautorität.

Den aktuellen `picross-integration-input-v1` aus endgültiger Definition, Hinweisen/Palette, explizitem Mono-/Color-Modus, gewähltem Reveal, Hintergrund selected/none/standard, benötigten Notices/Rechten, Metadaten, geprüfter Difficulty, gültigem vollständigem Proof und wirklicher Inhalts-/Integrationsentscheidung zusammenstellen. Vorhandenen Proof anhand des finalen Rasters unabhängig prüfen; kein zusätzlicher Suchsolverlauf zur Rekonstruktion alter Produktion. Keine Original-ZIP-, Producer-, Toolversions- oder historische Regelwerkszulassung.

```text
python -m tools.puzzle_production.authoring_builder prepare-integration --repository <arbeitscheckout> --record <aktueller-record> --output-dir <neue-übergabe>
python -m tools.puzzle_production.target_adapter plan --input <übergabe> --checkout <produktionscheckout>
python -m tools.puzzle_production.target_adapter register --input <übergabe> --checkout <produktionscheckout>
```

`prepare-integration` prüft und kopiert denselben vollständigen aktuellen Eingang wie `target_adapter export`; keine Entscheidungen werden ergänzt. Register prüft und plant selbst frisch. Identische aktuelle Wiederholung ist byte-/mtimegleicher No-op. Eine belegte ID mit anderem Inhalt braucht den gesonderten Änderungsauftrag. Aktuelle Qualitäts-, Bild-, Paletten-, Proof-, Rechte-, Kategorie-, Difficulty-, Pfad-, Slot- und test_only-Gates bleiben Pflicht.

Publikation und Registrierungsrecovery haben getrennte 1800-s-Defaults und 300-s-Warnung. Fremde/unklare Bytes und offene Journale erhalten. Kontrollierter Abbruch, erfolgreiche Rückführung und offene Recovery getrennt berichten. Der Integrationsbatch benutzt denselben Kern nur für ausdrücklich vorbereitete und autorisierte Jobs; kein zusätzlicher Batchauftrag wird aus einer Einzelintegration abgeleitet.

Für die Integration einen sauberen Branch vom aktuellen Main verwenden und nur gewählte finale Produktdaten übernehmen. Nach Registrierung Diff und Lieferbytes prüfen, den Registrierungsstand committen und Completion an denselben aktuellen Eingang binden:

```text
python -m tools.production_workspace.projector --repository <checkout> --complete-record <recordpfad> --integration-commit <volle-SHA> --input <übergabe>
```

Den aktuellen Arbeitsrecord danach auf dem Arbeitsref committen/pushen und Draft-PR im beauftragten Umfang erstellen. Reine Produktion erhält CI-Kern ohne Windowsbau und ohne neue rätselspezifische Tests. Vor Merge aktuellen Head/Basis, unabhängiges Review, Pflichtchecks, Konfliktfreiheit, erforderliche Abnahmen und tatsächliche Befugnis prüfen. Squash verwenden. Main erst am zurückgelesenen Mergecommit melden; lokaler Erfolg genügt nicht. Werkzeug-/CI-Pakete erben keine Produktions-Mergefreigabe.

## 9. Produktionsabschluss und Bereinigung

Eigentümerentscheidung vom 14.10.2026: Ein final auf main integriertes Rätsel muss nicht erneut produzierbar sein. Produktionsunterlagen sind Arbeitsmaterial.

1. Tatsächliche Endabnahme und Mainmerge prüfen, origin/main aktualisieren und
   aktuellen Lieferzustand gegen den bestätigten Maincommit vergleichen.
2. `retire-production --checkout <arbeitscheckout> --integrated-commit <main-SHA>
   --puzzle-id <id>` prüft die eigene abgeschlossene Arbeit gegen ihren tatsächlichen
   Arbeitscommit und das aktuelle Produkt gegen Main. Arbeitsdateien müssen nie
   zuvor in Main gelegen haben. Der aktuelle Record und ausschließlich zugehörige
   entbehrliche Nutzdateien samt Indexverweis entfallen. Fremde/neue/offene Arbeit
   bleibt erhalten; unbekannte Dateien und offene Transaktionen blockieren.
3. Dauerhaft bleiben aktuelle Definition/Matrix/Hinweise, aktive Bilder, Rechte/Notices, IDs, Save-Slots, Revisionen, Namen/Kategorien, Bewertungen und Added-Daten. Aktuelle Bildsources binden ausschließlich die aktuelle Identität und Bildbytes. Es entsteht kein neuer Receipt mit Originalexport-/Source-/Maincommit-Historie.
4. Entbehrliche Arbeitsdateien entfernen. Verworfene Varianten wurden bereits nach ihrer Auswahlentscheidung ohne Archivierung entfernt. Unbekannte Dateien innerhalb einer ausgewählten Revision blockieren vor Mutation; nicht manuell vorlöschen. Ungewählte neue/offene Arbeit bleibt. Teilfehler mit tatsächlichen Resten melden und denselben Mainanker benutzen. Vollständige Wiederholung ist No-op.
5. Diff und unveränderte Nutzdaten/Runtime kontrollieren, Cleanup committen/pushen, getrennt selbst prüfen und die bestehenden Pflichtchecks erfüllen. Eigentümerfreigabe vom 15.10.2026 beauftragt genau diesen engen Nachintegrations-Cleanup einschließlich Merge nach bestätigter Integration. Kein weiterer Routineprompt. Diese Befugnis gilt nicht für Werkzeug-/CI-Pakete; ein ausdrückliches „kein Merge“ bleibt maßgeblich. Eigener aktueller Paketplan mit begründet `modules=[]`, kein Playerbau oder rätselspezifischer Dauerfall.

Spätere echte Änderungen bleiben eigene Aufträge. Fehlende frühere Arbeitsdateien sind kein Defekt. Raster-/Reveal-/Hintergrundänderungen verwenden den [gezielten Editorvertrag](../../tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung), keinen neuen alten Export. Gültige aktuelle Bilder und Korrekturbefugnisse bleiben erhalten. Ihre eindeutig zugeordneten Arbeitsdaten nach tatsächlich bestätigtem Mainstand gezielt abschließen; aktuelle Rechte/Notices erhalten. Lokale Checkoutbereinigung richtet sich gesondert nach WORKSPACE und Benutzerauftrag.
