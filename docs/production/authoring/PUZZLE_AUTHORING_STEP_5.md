# Schritt 5: Abschluss und Integration

**Version 0.8.0 · Dokumentrevision 12 · 21.11.2026 · PROD-SLIM**

Pflicht: [Kern und Phasenroute](PUZZLE_AUTHORING.md#11-pflichtquellen-nach-phase),
danach diese Phase. Vorhandene passende Bild-/Rasterbelege verwenden; ihre
Produktion nicht wiederholen. Sicherung, Wiederaufnahme, Bildkorrektur und
Abschlussausgabe folgen Kern §§6–7.

## 8. Abgenommenes Ergebnis ins Spiel integrieren

Bei der Fortsetzung liest der Main-Worker die gespeicherte Qualifikation und die gewählten Dateien aus dem gebundenen Arbeitsstand. Fehlende Sichtungen oder Ableitungen gehören in die zugehörige Produktionsphase. Ein frischer Chat kann eine kombinierte Wahl und Schlussentscheidung anhand des qualifizierten Angebots übermitteln.

Vor Benutzung [RI](../PUZZLE_INTEGRATION.md), den aktuellen Eingang in [ZA-1](../ZA1_ADAPTER.md) und die passende CLI-Anleitung lesen. Schritt 5 setzt vollständige aktuelle Raster-/Hintergrundbereitschaft und tatsächliche Endfreigabe voraus. Bestehende gültige Entscheidungen verwenden, fehlende Entscheidungen niemals technisch erzeugen. Der Finalizer führt vorhandene tatsächliche Entscheidungen im einen aktuellen Record nach; Arbeitsmaterial ist keine Katalogautorität.

Den aktuellen `picross-integration-input-v1` aus endgültiger Definition, Hinweisen/Palette, explizitem Mono-/Color-Modus, gewähltem Reveal, Hintergrund selected/none/standard, benötigten Notices/Rechten, Metadaten, geprüfter Difficulty, gültigem vollständigem Proof und wirklicher Inhalts-/Integrationsentscheidung zusammenstellen. Der unabhängige Linien- oder Paarliniennachweis und der Endmatrixvergleich gehören vor das Rasterangebot. In Schritt 5 die Identität und Bytes der gewählten Lieferung gegen diesen Stand prüfen. Für separat eingereichte Eingangsverzeichnisse gilt die vollständige Eingangsprüfung nach ZA-1.

```text
python -m tools.puzzle_production.authoring_builder prepare-integration --repository <arbeitscheckout> --record <aktueller-record> --output-dir <neue-übergabe>
python -m tools.puzzle_production.target_adapter plan --input <übergabe> --pw-worktree <arbeitscheckout> --checkout <produktionscheckout>
python -m tools.puzzle_production.target_adapter register --input <übergabe> --pw-worktree <arbeitscheckout> --checkout <produktionscheckout>
```

Im verwalteten PW-Arbeitscheckout bindet `prepare-integration` die Lieferung an Job, Arbeitscommit und SHA-256 des qualifizierten Records. Plan und Register lesen diesen Stand über `--pw-worktree` und vergleichen Manifest und Lieferbytes mit der freigegebenen Auswahl. Der Plan prüft auch die vorgesehenen Profilpfade und lässt das Ziel schreibfrei. Erst die tatsächliche Erstregistrierung erzeugt die beiden Katalogprofile. Eine identische Wiederholung ist ein No-op. Eine belegte ID mit anderem Inhalt braucht den gesonderten Änderungsauftrag.

Publikation und Registrierungsrecovery haben getrennte 1800-s-Defaults und 300-s-Warnung. Fremde/unklare Bytes und offene Journale erhalten. Kontrollierter Abbruch, erfolgreiche Rückführung und offene Recovery getrennt berichten. Der Integrationsbatch benutzt denselben Kern nur für ausdrücklich vorbereitete und autorisierte Jobs; kein zusätzlicher Batchauftrag wird aus einer Einzelintegration abgeleitet.

Im [Remote-Einstieg](../../tools/PW_REMOTE.md) übermittelt der Akteur die gebundenen Entscheidungen an den Main-Worker. Der Worker liefert den Produkt-PR und den tatsächlichen CI-Stand. Nach bestätigtem Merge folgt der separate Retirement-Aufruf.

Für die Integration einen sauberen Branch vom aktuellen Main verwenden und nur gewählte finale Produktdaten übernehmen. Nach Registrierung Diff und Lieferbytes prüfen, den Registrierungsstand committen und Completion an denselben aktuellen Eingang binden:

```text
python -m tools.production_workspace.projector --repository <checkout> --complete-record <recordpfad> --integration-commit <volle-SHA> --input <übergabe>
```

Den aktuellen Arbeitsrecord danach mit `tools.work_publish publish` auf dem
Arbeitsref sichern, finale Produktcommits mit `tools.publish_git` veröffentlichen
und Draft-PR im beauftragten Umfang erstellen. Reine Produktion erhält den CI-Kern
ohne Windowsbau und ohne neue rätselspezifische Tests.

Den vollständigen PR-Diff einschließlich Lieferdaten selbst prüfen und das
Selbstreview an Head und Basis binden. Für die normale Rätsel-Erstintegration
kein unabhängiges GitHub-PR-Zweitreview und kein Copilot-Review anfordern und
keine PR-Inhalte an Copilot weitergeben. Keine
Reviewer-Konten oder Freigaben zur Weitergabe des PR-Inhalts verlangen. Eine
fehlgeschlagene oder verweigerte Copilot-Anfrage ist kein Mergeblocker. Nur eine
vom Auftraggeber konkret zusätzlich beauftragte Zweitprüfung gilt als persönliches
Vor-Merge-Gate. Daraus folgt keine Befugnis zur Weitergabe von PR-Inhalten.

Unmittelbar vor dem Merge aktuellen Head und Basis, vollständiges Selbstreview,
erfolgreiche Pflichtchecks (`docs`, `ci-required` und tatsächlich verlangte weitere
Checks), Konfliktfreiheit, gebundene Endabnahme und passende Mergebefugnis
bestätigen. Bei erfüllten Bedingungen direkt per Squash-Merge nach main integrieren.
Ein von GitHub gemeldeter Konflikt (`dirty`) blockiert den Merge. Meldet GitHub eine
Mergesperre wegen eines erforderlichen Approvals oder Branchschutzes, die konkrete
API-/UI-Meldung und die zuständige Schutzregel angeben, soweit sie einsehbar ist.
Die Schutzregeln einhalten und unverändert lassen. Im ausdrücklich beauftragten
Draftumfang beim Draft-PR bleiben. Main erst am zurückgelesenen Mergecommit melden.
Werkzeug- und CI-Pakete brauchen eine eigene Mergebefugnis.

### PW-FIND · Behandlung in der Schlussentscheidung

Für aktuelle Befundentscheidungen gilt der Weg nach
[Kern §6.3](PUZZLE_AUTHORING.md#63-pw-find--phasenübergreifende-befundentscheidungen):
Die Schlussübersicht zeigt alle noch relevanten Annahmen und Behandlungsvorgaben
an der gewählten Kombination beziehungsweise ihren Bestandteilen. Gedeckte
Annahmen werden nicht erneut verlangt. Neue zulässige Befunde dürfen zusammen
mit der tatsächlichen Endentscheidung angenommen werden. Endabnahme sowie
Integrations-/Mergebefugnis bleiben eigenständig erforderlich.
Am [Integrationseingang](../ZA1_ADAPTER.md#pw-find--entscheidungen-bis-zur-integration)
dürfen frühere Behandlungsvorgaben nicht verlorengehen. Die normale
Abschlussbereinigung erzeugt daraus kein neues Archiv.

## 9. Produktionsabschluss und Bereinigung

Eigentümerentscheidung vom 14.10.2026: Ein final auf main integriertes Rätsel muss nicht erneut produzierbar sein. Produktionsunterlagen sind Arbeitsmaterial.

1. Tatsächliche Endabnahme und autorisierte Mainintegration prüfen, origin/main
   aktualisieren und die gewählte Lieferung mit dem bestätigten Maincommit
   vergleichen. Der Listenfilter nach PW-DONE blendet jede registrierte ID aus.
2. Für v2 führt der ausführende Akteur direkt den bestehenden Befehl aus:
   `python -m tools.work_publish retire <id> --expected <erwarteter-Arbeitscommit>`.
   `--expected` ist die nach Completion veröffentlichte SHA der eigenen
   Arbeitsgeneration. Der Publisher liest das Fehlen des Remote-Branches
   `content/pw/<id>`, des gebundenen Arbeitsreleases und des Tags
   `work-prod-<id>` zurück. Der autorisierte Schlussauftrag umfasst diesen
   Akteursschritt bereits.
3. Bei Fehlern oder fehlendem Schreibrecht Integration, konkrete offene
   Bereinigungsreste und den Wiederholungsbefehl getrennt melden. Nach Klärung
   im selben Checkout mit derselben Arbeits-SHA fortsetzen. Vollständig
   abgebaute Arbeitsgenerationen ergeben nach Readback einen No-op. Fremde
   oder geänderte Generationen werden erhalten.
4. Für lokale v1-Arbeit gilt `retire-production --checkout <arbeitscheckout>
   --integrated-commit <main-SHA> --puzzle-id <id>`. Der Befehl prüft eigene
   Arbeit gegen den tatsächlichen Arbeitscommit und das aktuelle Produkt gegen
   Main. Ausschließlich zugehörige entbehrliche Dateien und Indexverweise
   entfallen. Unbekannte Dateien und offene Transaktionen blockieren.
5. Wenn der lokale Abschluss einen Cleanup-PR benötigt, Diff und Produktdaten
   prüfen, committen, pushen und die bestehenden Pflichtchecks erfüllen.
   Die Eigentümerfreigabe vom 15.10.2026 umfasst den eng gebundenen
   Nachintegrations-Cleanup einschließlich Merge. Ein ausdrücklicher
   Draftauftrag gilt weiter. Für den Inhalts-Cleanup einen aktuellen
   Paketplan mit begründetem `modules=[]` verwenden.

Dauerhaft bleiben aktuelle Definition, Matrix, Hinweise, Bilder, Rechte, Notices,
IDs, Save-Slots, Revisionen, Namen, Kategorien, Bewertungen und Added-Daten.
Aktuelle Bildquellen binden die aktuelle Identität und Bildbytes.

Spätere echte Änderungen bleiben eigene Aufträge. Fehlende frühere Arbeitsdateien sind kein Defekt. Raster-/Reveal-/Hintergrundänderungen verwenden den [gezielten Editorvertrag](../../tools/PUZZLE_EDITOR.md#13-pe-edit2-gezielte-pflege-statt-vollbestandsprüfung), keinen neuen alten Export. Gültige aktuelle Bilder und Korrekturbefugnisse bleiben erhalten. Ihre eindeutig zugeordneten Arbeitsdaten nach tatsächlich bestätigtem Mainstand gezielt abschließen; aktuelle Rechte/Notices erhalten. Lokale Checkoutbereinigung richtet sich gesondert nach WORKSPACE und Benutzerauftrag.

## Katalogprofile für Abschlussbilder

Bei der Erstintegration erzeugt der Fachkern automatisch beide Katalogprofile. Für den Abschluss werden die aktuelle Revealquelle und die gelieferten Profilbytes mitgeprüft.
