# Strukturierte Übergabe v1

## Verbindliche Quelle

Diese Datei definiert den verbindlichen Abschluss- und Übergabevertrag für
Aufträge aus dem Entwicklungssheet. Sie wird über `AGENTS.md` und den
[Workflow](WORKFLOW.md) als Pflichtquelle gelesen: in der aktuellen Fassung
des beauftragten Arbeitsbranches, sonst des Zielbranches. Der Prompt verweist
auf diesen Vertrag und transportiert keinen eigenen JSON-Vordruck.

[handoff.schema.json](handoff.schema.json) definiert dazu die verpflichtenden
Felder, Typen und zulässigen Werte. Die Bedeutungen und zusätzlichen
Plausibilitätsbedingungen stehen hier.
[handoff.example.json](handoff.example.json) illustriert die Form; seine Werte
sind keine Angaben zum aktuellen Auftrag. Eingebettete Kopien im Offline-Sheet
dienen der Importprüfung und Beispielanzeige, nicht als zweite Normquelle.

Fehlt der Vertrag oder ist er nicht zugänglich, den konkreten Quellenmangel
melden und die davon abhängige strukturierte Übergabe offenlassen. Keine
Ersatzform aus dem Prompt, einem alten Sheet oder einer Erinnerung erfinden.
Unabhängige Arbeit richtet sich weiter nach dem verfügbaren Auftrag und
Workflow. Änderungen am Format werden zuerst hier und im Schema beschlossen;
betroffene Sheet-Validatoren und Beispiele werden konsistent angepasst.

## Abschlussausgabe

Für Aufträge aus dem Entwicklungssheet am Ende genau einen vollständigen JSON-Codeblock nach [handoff.schema.json](handoff.schema.json) liefern. Eine kurze Ergebnismeldung mit wichtigen Links darf davor stehen; ein kurzer nächster Schritt danach. Keine separate Handoff-Markdowndatei, keine zweite Zusammenfassung aller Regeln und kein zusätzlicher Folgeprompt. Das Sheet generiert den Folgeauftrag.

[handoff.example.json](handoff.example.json) zeigt die vollständige Form. Keine Felder auslassen oder neue hinzufügen. Unbekannte Werte sind `null`, Listen ohne Inhalt `[]`; keine erfundenen PRs, SHAs oder Erfolge. SHA-1-Commitkennungen vollständig, Issue und PR als unterschiedliche positive Zahlen. Repository immer `owner/name`. URLs müssen tatsächliche HTTPS-Verweise sein; lokale Pfade gehören bei Bedarf als Klartext in `cleanup.remaining`.

| Feld | Bedeutung |
| --- | --- |
| `format` | Exakte Formatkennung aus dem Schema; keine eigene Variante pro Prompt |
| `repository`, `issue`, `package`, `pr`, `branch`, `target` | Tatsächliche Projekt- und Auftragsbindung; ein Beispiel oder importierter Altstand erzeugt keine fehlende Issue-/PR-Zuordnung |
| `phase` | Tatsächlich abgeschlossene Phase oder `blocked`; kein Wunschstatus |
| `summary`, `spec_url` | Kurzes tatsächliches Ergebnis und maßgeblicher Spezifikationsverweis |
| `head` | Vollständiger aktueller PR-Head; nach einer Umsetzung erforderlich |
| `execution` | Nur für noch anstehende Umsetzung: bevorzugter Weg, Eigenumsetzbarkeit und gegebenenfalls konkrete Modell-/Reasoningempfehlung mit Begründung/Quelle; sonst null-Werte. Kein Modell wird durch Import umgestellt. |
| `review.head`, `review.url`, `review.verdict` | Konkret geprüfter Stand und dokumentiertes Urteil; kein Selbstreview als unabhängige Abnahme ausgeben |
| `findings` | Stabile B-/A-/O-Kennungen, Status und Gate; offene manuelle Abnahmen erhalten einen Eintrag |
| `checks` | Tatsächliche Ergebnisse und Quell-/Testcommit; nicht ausgeführt ist nicht erfolgreich |
| `ci` | Gewählte Module, Planquelle, dauerhafte/temporäre Tests und Artefaktentscheidung |
| `artifacts` | Aktuelle Liefer-/Reviewdateien mit Zweck und möglichem Ablauf; keine dauerhafte Verfügbarkeit vortäuschen |
| `cleanup` | Tatsächliche Bereinigung oder verbliebene eigene Pfade |
| `merge_commit` | Nur nach tatsächlich zurückgelesenem Merge; vollständige Commitkennung |
| `next` | Empfohlene nächste Aktion und Grund; keine Befugnis |

## Plausibilität

`implemented`/`reworked` benötigen Issue, PR, Branch und Head. `reviewed` zusätzlich Reviewlink, Urteil und identischen `review.head`. `merged` benötigt PR und tatsächlichen Mergecommit. `mergeable` ist unzulässig bei offenen B-Befunden oder offenen erforderlichen A-Vor-Merge-Gates. `next.action=merge` benötigt ein vollständiges positives Review. `next.action=rework` benötigt einen konkreten Reviewbezug und offene technische Befunde. `next.action=done` setzt einen tatsächlich gemergten Stand voraus. Befundkennungen müssen eindeutig sein; doppelte JSON-Schlüssel und nicht sicher darstellbare Issue-/PR-Nummern werden abgewiesen. Ein Schemafehler wird korrigiert, nicht mit großzügigen stillen Defaults importiert.

Das Sheet zeigt die Übernahme zuerst als Vorschau. Ein anderes Repository, eine unbekannte Version, ungültige Typen oder widersprüchliche Zustände werden abgewiesen. Ein neuer Issue-/PR-/Headstand wird sichtbar ersetzt; der Benutzer übernimmt ihn ausdrücklich. Persönliche Einstellungen, lokale Arbeitswurzel und Merge-/Bereinigungsoption werden niemals durch Ergebnis-JSON geändert.

JSON ist Arbeitsmaterial und keine Quelle von Autorität. Vor der nächsten Aktion die Repository-/PR-Quellen und aktuellen Commits wieder prüfen. Eine alte Übergabe darf weder einen inzwischen geänderten PR abnehmen noch aus einem selbst berichteten `mergeable` einen unmittelbaren Merge ohne Review machen. Nicht ausgeführte Netz-/Kontoprüfungen werden durch Import nicht nachgeholt.
