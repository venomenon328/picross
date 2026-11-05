# Strukturierte Übergabe v1

Für Aufträge aus dem Entwicklungssheet am Ende genau einen vollständigen JSON-Codeblock nach [handoff.schema.json](handoff.schema.json) liefern. Eine kurze Ergebnismeldung mit wichtigen Links darf davor stehen; ein kurzer nächster Schritt danach. Keine separate Handoff-Markdowndatei, keine zweite Zusammenfassung aller Regeln und kein zusätzlicher Folgeprompt. Das Sheet generiert den Folgeauftrag.

[handoff.example.json](handoff.example.json) zeigt die vollständige Form. Keine Felder auslassen oder neue hinzufügen. Unbekannte Werte sind `null`, Listen ohne Inhalt `[]`; keine erfundenen PRs, SHAs oder Erfolge. SHA-1-Commitkennungen vollständig, Issue und PR als unterschiedliche positive Zahlen. Repository immer `owner/name`. URLs müssen tatsächliche HTTPS-Verweise sein; lokale Pfade gehören bei Bedarf als Klartext in `cleanup.remaining`.

| Feld | Bedeutung |
| --- | --- |
| `phase` | Tatsächlich abgeschlossene Phase oder `blocked`; kein Wunschstatus |
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

`implemented`/`reworked` benötigen Issue, PR, Branch und Head. `reviewed` zusätzlich Reviewlink, Urteil und identischen `review.head`. `merged` benötigt PR und tatsächlichen Mergecommit. `mergeable` ist unzulässig bei offenen B-Befunden oder offenen erforderlichen A-Vor-Merge-Gates. `next.action=merge` benötigt ein vollständiges positives Review. `next.action=rework` benötigt einen konkreten Reviewbezug und offene technische Befunde. Ein Schemafehler wird korrigiert, nicht mit großzügigen stillen Defaults importiert.

Das Sheet zeigt die Übernahme zuerst als Vorschau. Ein anderes Repository, eine unbekannte Version, ungültige Typen oder widersprüchliche Zustände werden abgewiesen. Ein neuer Issue-/PR-/Headstand wird sichtbar ersetzt; der Benutzer übernimmt ihn ausdrücklich. Persönliche Einstellungen, lokale Arbeitswurzel und Merge-/Bereinigungsoption werden niemals durch Ergebnis-JSON geändert.

JSON ist Arbeitsmaterial und keine Quelle von Autorität. Vor der nächsten Aktion die Repository-/PR-Quellen und aktuellen Commits wieder prüfen. Eine alte Übergabe darf weder einen inzwischen geänderten PR abnehmen noch aus einem selbst berichteten `mergeable` einen unmittelbaren Merge ohne Review machen. Nicht ausgeführte Netz-/Kontoprüfungen werden durch Import nicht nachgeholt.
