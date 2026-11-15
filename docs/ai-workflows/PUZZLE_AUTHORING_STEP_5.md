# Schritt 5: Abschluss und Integration

**Version 0.8.0 · Dokumentrevision 7 · 15.11.2026 · PW-PERF-D**

Pflicht: [gemeinsamer Kern](PUZZLE_AUTHORING.md) vollständig und vollständiger
[Bildstil](../PUZZLE_IMAGE_STYLE.md), danach diese Phase. Zusätzlich: Vorhandene passende Bild-/Rasterbelege prüfen, ihre Produktion nicht wiederholen. Technische Operationsverträge nach §8 vor Benutzung lesen.
Sicherung, Wiederaufnahme, gemeinsame Bildkorrektur und Abschlussausgabe: Kern §§6–7.

## 8. Abgenommenes Paket ins Spiel integrieren

Schritt 5 setzt vollständige gültige Raster-/Hintergrundbereitschaft und echte
Endfreigabe v2 am unveränderten Original-ZIP voraus. Vorhandene äußere Entscheidung,
Ableitung und Endfreigabe über Finalizer v2 nachtragen; Originale bleiben bytegleich.
Atomare Recordfortschreibung und geprüfte Projektion verwenden denselben Stand.
Fehlende Freigaben sind keine technische Kleinigkeit.

Vor Erstintegration, Wiederaufnahme und jeder registrierenden Mutation tatsächlich
origin/main aktualisieren, vollständige SHA und beauftragten Zielcheckout feststellen.
Aktuelles main sicher in den Produktionsbranch einbeziehen, schmutzige WIP/Fremddaten
nicht überschreiben. Gültige Inhaltsregistry v4, die vom aktuellen gemeinsamen
Writer unterstützte Runtimegeneration und je ID genau eine aktuelle Metadatenzeile
mit gültiger Kategorie prüfen. Die [PE-A2-Zielregeln](../PUZZLE_EDITOR.md#8-pe-a2-geschlossener-bild--und-präferenzvertrag)
gehören zum bestehenden Zielvertrag, nicht zu einer Migration durch dieses Regelpaket.
Veraltete/inkonsistente Ziele, Konflikte, Locks/Journale oder ungeklärte Recovery
stoppen vor Mutation; keine implizite Zielmigration oder Rückstufung.

Registered auf Draftbranch ist kein Mainabschluss. Bei verändertem Zielkatalog
mit unveränderten gebundenen Originalen und gültigen Freigaben frisch export → plan →
register gegen aktuellen Zielcheckout ausführen. Zielabhängige Index-/Runtime-/
Source-/Receipt-/Abschlussdaten fachlich neu erzeugen. Alte generierte Registries
nicht als Ersatz für aktuellen Bestand oder durch bloße Textkonfliktauflösung
übernehmen; alle bestehenden Inhalte/Metadaten erhalten. Original-ZIP, Raster-/
Revealbytes, historische Herkunft/Freigaben bleiben unverändert. Gültiges
Difficulty-Rebind benutzen, bei neuer ID --runtime-revision 1 beibehalten.
Technisch unmögliche Neubindung oder ungeklärte Herkunft konkret melden, nicht
erfinden/umschreiben. Keine direkte Mainmutation oder Umgehung von Guards.

```text
python -m tools.puzzle_production.authoring_builder finalize-background --request <finalize-v2.json> --source-root <neue-belege> --output-root <produktionscheckout> --history-repo <produktionscheckout>
python -m tools.puzzle_production.target_adapter export --allow-background --input <original-package.zip> --external-root <produktionscheckout> --approval <echte-endfreigabe.json> --name <motivname> --runtime-revision 1 --stem <stamm> --save-slot <slot> --category-id <kategorie> --categories content/categories.json --output-dir <neuer-export>
python -m tools.puzzle_production.target_adapter plan --export <neuer-export> --checkout <produktionscheckout> --difficulty <geprüfte-difficulty.json>
python -m tools.puzzle_production.target_adapter register --export <neuer-export> --checkout <produktionscheckout> --difficulty <geprüfte-difficulty.json>
```

Nur gewählte Lieferung übernehmen. Export v6 prüft vollständig vor Veröffentlichung;
frischer lesender Plan vor autorisierter Registrierung. Register plant selbst neu,
kein fremder Plan als Vertrauenscache. Historisch gespeicherte false-Readinessfelder
bleiben; Zielbereitschaft und registrierter Checkout werden frisch ermittelt.
RI, ZA-1 und aktuelle Katalogguards behalten sichere Pfade/Namespaces/Dateitypen,
Quelle/Capability/Provenienz, Bilder/Palette/Proof, Kategorie/Difficulty, IDs/Slots
und test_only. Keine Save-/Registry-/Runtimeänderung als Abkürzung.

Registrierung und Recovery behalten getrennte 1800-s-Schutzrahmen und 300-s-Warnung;
ein äußerer Ablauf darf Recovery nicht auf verbrauchte Restzeit beschränken.
Export/Plan/Eingangsprüfung behalten ihre eigenen Grenzen. Unterbrechung, Rollback,
offene Recovery und Abschluss getrennt berichten. Unklare/fremde Bytes und Journal
erhalten. Der bestehende BA-B-Runner bleibt nur bei ausdrücklich vorbereiteten
passenden Einzelintegrationen nutzbar, mit eigenen Mengen-/Budget-/Publikationsgrenzen.
Kein neuer Batchauftrag, versteckter Solverlauf oder zweites Hintergrundregister.

Nach wirklicher Registrierung Diff/Lieferbytes prüfen und Registrierungsstand
committen. Den Abschluss binden mit:

```text
python -m tools.production_workspace.projector --repository <checkout> --complete-record <recordpfad> --integration-commit <volle-SHA>
```

Record, Projektion und Ansichtsverweis danach committen/pushen und Draft-PR im
beauftragten Umfang erstellen. Reine Produktion erhält CI-Kern ohne Windowsbau
und ohne neue rätselspezifische Tests. Vor Merge aktuellen Head/Basis, unabhängiges
Review am tatsächlichen Stand, ausgewählte Pflichtchecks, Konfliktfreiheit,
erforderliche Abnahmen und ausdrückliche/bedingte Befugnis prüfen; Squash verwenden,
keine Release-/Deploymentfreigabe ableiten. Main erst am zurückgelesenen Mergecommit
melden; danach der revisionsgenaue Abschluss nach §9. Ein lokaler Erfolg reicht nicht.

## 9. Produktionsabschluss und Bereinigung

Eigentümerentscheidung vom 14.10.2026: Ein fertiggestelltes und final auf main
integriertes Rätsel muss nicht erneut produzierbar sein. Produktionsunterlagen
sind Arbeitsmaterial, kein dauerhaft wachsender Spiel-/CI-Bestand.

1. Tatsächliche Endabnahme und Merge nachweisen, origin/main aktualisieren und
   vollständigen enthaltenen Commit nennen. Registered auf Draft genügt nicht.
   Neuere/offene Arbeit derselben ID zuerst klären, fremde/offene Produktion erhalten.
2. Nach Merge in eigenem kleinen Cleanup-Diff zuerst den
   [abgeschlossenen Ansichtsverweis](../PRODUCTION_CURRENT_VIEW.md) frisch gegen
   Revision/Mainbeleg prüfen und entfernen. Verweis auf neuere/offene Arbeit erhalten;
   bei ungeklärter ID vor Abschluss stoppen. Dann:

   ```sh
   python -m tools.puzzle_production.target_adapter retire-production --checkout . --integrated-commit <vollstaendige-main-SHA> --puzzle-id <pz-ID>
   ```

   Mehrere bestätigte IDs durch wiederholtes --puzzle-id. Der Befehl prüft Main-
   Abstammung und unveränderte Integrations-/Arbeitsbytes, entfernt abgeschlossene
   Authoringrevisionen/Indexeinträge und ersetzt das Produktionspaket durch einen
   kompakten Integrationsdatensatz. Kein Solver-, Proof- oder Bildreplay.
3. Dauerhaft bleiben Runtime-Definition mit Matrix/Hinweisen, Reveal, Rechte/Notices,
   ID/Runtime-Revision/Save-Slot, Kategorie und relevante Schwierigkeit. Kompakter
   Datensatz bindet diese Daten, ursprünglichen Exporthash und bestätigten Maincommit.
   Aktive Bildbindung samt Herkunft/Freigaben erhalten, nicht auf Vorgänger zurücksetzen
   oder historische Belege für nachträgliche Freigaben umschreiben. Aktive Bewertung,
   kompakte Berichte und Eingangs-/Methoden-/Referenzbindungen bleiben außerhalb
   versiegelter Produktion. Manuelle Neubewertung verlangt keinen Produktionsreplay.
4. Entfernt werden Quellen-/Abstraktionsbilder, verworfene Varianten, Prompts, ZIPs,
   duplizierte Exporte, Proofs, Reparaturspuren, Galerien und Zwischenberichte. Keine
   Kopien in neuen Archiven, Builds oder CI-Artefakten. Git-Historie und kompakte
   Commit-/PR-Entscheidungsbezüge genügen; Nutzungsrechte/Attribution nicht verlieren.
5. Diff und unveränderte Runtime kontrollieren, Cleanup committen/pushen, getrennt
   selbst prüfen und nach erfolgreichen Pflichtchecks unmittelbar mergen.
   Eigentümerfreigabe vom 15.10.2026: Genau dieser eng begrenzte Nachintegrations-
   Cleanup einschließlich Merge ist beauftragt, auch nach zuvor als Draft geliefertem
   Integrations-PR. Kein weiterer Routineprompt oder dauerhaft offener Cleanup-Draft.
   Vor tatsächlichem Integrationsmerge nichts bereinigen; konkrete Blocker melden.
   Eigener aktueller Paketplan mit begründet modules=[], Quellen-/Plankern ohne
   Player-Build und ohne rätselspezifische Tests. Maincommit/erhaltene Runtime nachweisen.

Spätere echte Rätseländerungen sind neue Aufträge. Fehlende alte Arbeitsdateien
sind kein Defekt und keine Wiederherstellungspflicht. Neue Exporte bleiben vollständig
geprüft; Bestandsregistrierung/Kategorienpflege benutzen die kompakte Integrationsbindung.
Diese fachliche Cleanupfreigabe erweitert keine lokale Checkoutbereinigung und
keine Befugnis für Werkzeug-/CI-Pakete.

### Abschluss nachträglicher Bildrevisionen · CI2 vom 26.10.2026

Spätere Revealrevisionen bereits integrierter Rätsel haben einen eigenen
revisionsgenauen Abschluss; eine bereinigte Rasterproduktion wird dafür nicht
wiederhergestellt. Vor Abschluss tatsächliche Bildfreigabe, aktive Bildbindung
und enthaltenen Maincommit prüfen; neuere/offene Arbeit erhalten. Zugehörige
erledigte Quellen, Prompts, Varianten, ZIP-/Rohkopien und Indexeinträge entfernen,
aber aktuelle Bilddatei, Rechte, Herkunft/Freigaben und aktive Revision behalten.
Definitionsbytes, Runtime-Revision, Save-Slot, Registrierung und Bewertungen bleiben.
Ursprüngliche versiegelte Integrationsbelege nicht neu erzeugen/umschreiben.

```sh
python -m tools.puzzle_production.target_adapter retire-reveal-production --checkout . --integrated-commit <vollstaendige-main-SHA> --authoring-revision <pz-ID> <Authoringrevision>
```

Jede Revision ausdrücklich wiederholen, kein impliziter ID-Gesamtabbau.
Origin/main vorher aktualisieren. Main muss Record, finale Freigabe und exakt
aktuelle Bildquelle binden. Offene Journale, fremde Bytes, Teilentfernung und
betroffene Indexänderungen blockieren vor Löschung. Neuere/offene Geschwister
bleiben. Identische Wiederholung nach vollständiger Entfernung ist nach frischer
Prüfung No-op, auch ohne alte Pakete. Unterstützte kompakte v1-Datensätze und
vollständige ursprüngliche Pakete unverändert belassen; retire-production bleibt
der Rasterabschlussweg. Begrenzter Datei-/Referenzvergleich, kein Solver-/Bild-/
Katalog-/Spielerreplay allein zur Bereinigung. Die enge Nachintegrationsfreigabe
aus §9 bleibt, nicht eine neue Befugnis aus historischen CI2-Lieferberichten.

### Abschluss der Hintergrundarbeit

[Hintergrundvertrag §10](../PUZZLE_BACKGROUNDS.md#10-hp-i1b1--erste-registrierung-und-kompakter-produktionsabschluss)
ergänzt Erstintegration: retire-production erhält aktive kompakte Hintergrundsource,
echte Freigabe-/Rechte-/Ableitungsbindungen, PNG/none/Notice und ursprünglichen
Exportanker; Mainbeleg separat im Receipt v2. Vor Löschung gewählte IDs/Bytes
gegen tatsächliches main prüfen. Offene/neuere/fremde Arbeit erhalten, bei nicht
trennbarem ID-Baum stoppen. Alte innere Refs sind danach historische Identitäten,
keine wieder zu öffnenden Pflichtdateien. Retire-reveal-production ist kein
Hintergrundabschlusswriter.

Bis Auswahl drei Einzelbilder erreichbar halten; bis tatsächlicher Integration
alle noch nötigen Arbeits-/Rechte-/Wahlbindungen. Nach bestätigter Endabnahme und
Mainintegration nur abgeschlossene Hintergrundarbeit entfernen: verworfene
Kandidaten, Prompts, Quellen-/Ableitungskopien, ZIPs und temporäre Review-/Diagnosedaten.
Kein Kandidatenarchiv, keine Wiederherstellung alter Rasterproduktion oder Solver-/
Bild-/Buchreplay. Aktives Asset bzw. echte Leerentscheidung, Rechte/Attribution,
aktive Bildrevision und kompakte Wahl-/Ableitungs-/Integrationsbindungen bleiben.
Historische Originale nicht umschreiben, aktive Bilder nicht zurücksetzen.

### HP-I1b2: eigene Hintergrundrevision und ihr Abschluss

[Hintergrundvertrag §11](../PUZZLE_BACKGROUNDS.md#11-hp-i1b2--eigenständiger-hintergrundwechsel)
definiert den unveränderlichen picross-background-adoption-request-v1. Tatsächliche
Auswahl/Entfernung und Zielautorisierung aufzeichnen, keine Dummy-ZIPs oder neue
Rasterfreigabe. Bytegleiche aktuelle Source/freigegebenes Reveal binden, ursprüngliche
Revealautorität in initial erhalten. Eigener Folgeauftrag nach §7.6 bleibt
unveränderlich; historische Sheetbedienung ist kein paralleler Assistent.
Aktuelle integrierte Herkunft lesen, Arbeitsrevision via catalog_background_change
store samt Index sichern, dann plan und autorisiertes adopt nach CLI. Fehlende/
false-Capability blockiert, kein Override. Gültige Freigaben nicht erneut verlangen;
Raster-/Revealneubindung folgt gegebenenfalls HP-I1c, nicht einem erfundenen Ersatzweg.

Nach bestätigter Mainintegration origin/main aktualisieren und gezielt ausführen:

```text
python -m tools.puzzle_production.target_adapter retire-background-production --checkout <checkout> --integrated-commit <vollständige-main-SHA> --authoring-revision <pz-ID> <revision>
```

Nur ausdrücklich gewählte vollständig belegte Revisionen/Indexzeilen entfernen;
neuere Arbeit, aktives PNG/none/Notice/Receipt bleiben. Eine inzwischen abgelöste,
tatsächlich integrierte Revision darf mit historischem Mainbeleg abgeschlossen
werden. Vollständig entfernte Revision plus Index ergibt nach frischer Prüfung
No-op, Teilreste nicht. Kein altes Raster-ZIP rekonstruieren oder Solver-/Buchreplay.
Der Befehl liefert lokalen Diff, keinen automatischen Commit/Merge.

## PW-PERF-B · Begrenzte Erstregistrierungsprüfung

Für Erstregistrierung auf v4/v8 gilt ausschließlich die neue geschlossene
[v10-Semantik](../PUZZLE_INTEGRATION.md). Gemeinsame Indizes, neue Produktion samt Freigaben/Proof,
abhängige Quellen und Schreibziele bleiben vollständig gebunden. Unbeteiligte
alte Paket-/Liveasset-/Sidecardateien werden nicht gelesen oder als intakt
bestätigt; ihre Defekte erkennt der zuständige Reader oder ein expliziter
Gesamtaudit. P0/P2 prüfen neue Quellen und freie/eigene Ziele, P5/P6 die neue
Publikation, R0/R2 eigene Zwischenstände und alte Indizes. Alte Journalgenerationen
und andere Writer behalten ihre bisherigen Prüfverträge. Keine Garantie gegen
nichtkooperierendes ABA-/OS-Racing; keine Änderung menschlicher Freigaben.


## PW-PERF-E · Gezielter Abschluss aktueller Quellen

Für `retire-production` gilt der geschlossene [Receipt-v4- und Prüfvertrag](../ZA1_ADAPTER.md#pw-perf-e--ausgewählter-produktionsabschluss-und-receipt-v4).
Aktuelle Background v6 (selected/none/standard) und Reveal v4 (PNG/SVG) werden
an binding/current geprüft, ohne erfundenen initial-Ursprung. Aktive
Editorrasterpakete v1/v2 bleiben vollständige aktive Autorität. Alte Receipts
v1/v2/v3 bleiben unverändert. V4 erhält Originalexport, Rechte und tatsächlichen
Main-/Quellcommit getrennt; Sonderimportquellen werden je ID ausdrücklich mit
`--source-commit ID SHA` gebunden. Keine erneute Endfreigabe oder Completion.
Nur ausgewählte Abhängigkeiten werden gelesen, keine fremden Paket-/Bildbäume.
Alle Preflights vor erster Löschung, gezielter Abschlussreadback, frischer
Byte-/mtime-No-op und ehrliche Teilfehlerreste sind verbindlich. Dieses
Werkzeugpaket beauftragt keine reale Bereinigung; sie braucht einen separaten Auftrag.
