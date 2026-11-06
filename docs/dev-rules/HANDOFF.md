# Strukturierte Übergabe v1

## Verbindliche Quelle

Diese Datei definiert den verbindlichen Abschluss- und Übergabevertrag für
Aufträge aus dem Entwicklungssheet. Sie wird über `AGENTS.md` und den
[Workflow](WORKFLOW.md) als Pflichtquelle gelesen: in der aktuellen Fassung
des beauftragten Arbeitsbranches, sonst des Zielbranches. Der Prompt verweist
auf diesen Vertrag. Der Verweis kennzeichnet den strukturierten Abschluss auch
ohne Herkunftssatz und ohne mitgegebenes früheres JSON.

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

Für Aufträge aus dem Entwicklungssheet zuerst in wenigen Sätzen das tatsächliche
Ergebnis, die maßgebliche Quelle (sofern vorhanden) und den nächsten Schritt
oder die offene Frage nennen. Danach genau einen vollständigen JSON-Codeblock
liefern. Ihn vor der Ausgabe gegen [handoff.schema.json](handoff.schema.json)
und die Plausibilitätsregeln unten prüfen. Keine separate Handoff-Markdowndatei
oder zusätzlichen Folgeprompt anlegen. Das Sheet generiert den Folgeauftrag.

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

## Was in den nächsten Auftrag gehört

Jede Antwort auf einen Sheet-Auftrag liefert den vollständigen v1-Block, auch bei
Beratung, Blockade, Review und Abschluss. Das Sheet speichert ihn zur Ansicht
und zum Ausfüllen der nächsten Vorlage. Keine der Vorlagen hängt den Block an
den Folgeprompt an. Ein Link auf die konkrete Entscheidung oder Prüfung ist
präziser und bleibt auch bei einer Korrektur im Issue oder PR verwendbar.

| Kopiervorlage | Was der nächste Bearbeiter braucht |
| --- | --- |
| Idee besprechen | Neue Idee und Beratungsauftrag. Es ist noch keine Veröffentlichung beauftragt. |
| Feature spezifizieren, Fehler erfassen | Neue Ziele bzw. Reproduktion und gegebenenfalls vorhandenes Issue/Paket. Bei einem Entwurf nur im vorigen Chat kann eine ausgewählte Gesprächsnotiz die Spezifikation ergänzen. |
| Besprochene Spezifikation freigeben | Ausdrückliche Freigabe und Spezifikationsquelle. Im selben Gespräch genügt der besprochene Entwurf. Beim Chatwechsel ohne dokumentierte Entscheidung die konkreten Punkte als kurze, editierbare Notiz mitgeben. |
| Entscheidung nachführen, Paket vorbereiten, nächstes Paket auswählen | Die neue Entscheidung bzw. das zu prüfende Issue/Paket. Anforderungen, Prüfplan und spätere Entscheidungen dort festhalten und wieder lesen. |
| Paket umsetzen | Freigegebenes Issue/Paket, bei Bedarf ein genauerer Spezifikationslink, vorhandener Arbeitsbranch/PR oder Auftrag zur Neuanlage, gewählte Arbeitsparameter. |
| Umsetzung fortsetzen | Derselbe Arbeitsstand. Den letzten gesicherten Zwischenstand im Issue/PR nachführen. Ausschließlich dort fehlende Zwischenstände oder Blockaden lassen sich als gezielter Text mitgeben. |
| Abschluss zum Review geben, Minimalreview | Aktueller PR, dort Lieferkommentar, CI und erreichbare Revieworiginale. Der normale Review kann einen bekannten Head und aktuelle Hinweise mitgeben. Für den Minimalreview genügt die PR-Nummer im gewählten Projekt. Beide übernehmen die gewählte Mergeoption. |
| Eigene Änderungswünsche vorbereiten | PR und neuer Wunsch in eigenen Worten. Ein früheres Review oder ein zusammen mit dem Auftrag bereitgestelltes Bild kann den Ausgangspunkt zeigen. Die Paketentscheidung aus dem Issue/Paket im PR verlinken. |
| Nacharbeit zu Reviewbefunden vorbereiten, Befunde beheben, Nacharbeit erneut prüfen | PR und konkreter Reviewkommentar, für die Behebung ausdrücklich die beauftragten Befundkennungen. Erfolgskriterien und Befundstatus stehen im Review. |
| Rote CI beheben | PR und dessen aktuell fehlgeschlagener Lauf. Besondere neue Vorgaben im Auftrag kenntlich machen. |
| Manuelle Abnahme melden, Merge freigeben | Bei Abnahme die neu gemeldete tatsächliche Probe, bei Merge die ausdrückliche Freigabe für den PR. Dokumentierte Nachweise und Gates aus dem PR prüfen. |
| Paketabschluss und Rückbau | Issue/Paket und gegebenenfalls Liefer-PR. Noch benötigte eigene lokale Restpfade nur gezielt für die zuständige Arbeitsumgebung mitgeben. |

`branch` benennt einen tatsächlich vorhandenen und zum Paket gehörenden
Arbeitsbranch. Bei reiner Planung ohne Arbeitsbranch sind `branch` und der
unbekannte `head` null. Ein separater Spezifikations-PR kann als `spec_url`
dienen. Seine PR-/Branchkennung gehört nur dann in die Arbeitsbindung der
Umsetzung, wenn diese dort tatsächlich fortgeführt wird. In alten Übergaben
behandelt das Sheet den Zielbranch im Arbeitsbranchfeld als fehlenden Arbeitsbranch.
Bei einem vorhandenen PR lässt sich dessen Branch direkt ermitteln.

Berichtete CI-Module, Checks, Ausführungsempfehlungen, Freigaben und
Bereinigungsreste sind keine neuen Aufträge. Eine neue Modulvorgabe gibt der
Auftraggeber bei Bedarf im dafür vorgesehenen Feld ein. Lokale Pfade, komplette
Prüfprotokolle oder ein weiteres `handoff.json` werden nicht routinemäßig im
Repo archiviert. Für erforderliche Originaldateien gelten Zustellung, Bindung und
Ablauf nach [CI_CONTRACT.md](CI_CONTRACT.md). In `artifacts` steht der erreichbare
Verweis mit Zweck und Ablauf. Ein fehlender Zugriff bleibt als offenes Gate sichtbar.

## Plausibilität

**Beispiel: neue Wünsche nach einem positiven Review.** Ist der erweiterte
Umfang mit Abnahmekriterien und Prüfbedarf im Issue/Paket dokumentiert und
startbereit, meldet die Vorbereitung `phase: "specified"` und
`next.action: "implement"`. `spec_url` verweist möglichst direkt auf die
Paketentscheidung. Bei offener wesentlicher Klärung oder fehlender erforderlicher
Dokumentation den konkreten Grund und `blocked` / `clarify` melden.
Galt das positive Review dem bisherigen Umfang, seinen Link und Geltungsbereich
in der Paketentscheidung festhalten. Für das noch ungeprüfte Folgepaket sind
`review.url`, `review.head` und `review.verdict` jeweils `null`, auch wenn
beide Pakete zu diesem Zeitpunkt denselben PR-Head haben. Ein neuer Wunsch
erzeugt keine Befundkennung. Tatsächlich bestehende relevante Befunde und Gates
mit ihrem Status berücksichtigen. Die ausgeführte und zur Prüfung gelieferte
Umsetzung empfiehlt `next.action: "review"` für den neuen Head.

Umfang, Akzeptanz und Umsetzungshinweise gehören in die verlinkte
Paketentscheidung. Die Arbeitsbindung steckt in `pr` und `branch`.
`execution.preferred` benennt den Ausführenden. Geplante Prüfungen im Paket
festhalten; ein benannter, noch nicht ausgeführter Check kann `not_run` tragen.
Bisher ungemessene `ci.seconds` sind `null`. Eine nur im Chat verfügbare Datei
hat keinen HTTPS-Verweis. Für eine spätere Sichtung die benötigten Originale
nach dem CI-Vertrag zugänglich machen.

`implemented`/`reworked` benötigen Issue, PR, Branch und Head. `reviewed` zusätzlich Reviewlink, Urteil und identischen `review.head`. `merged` benötigt PR und tatsächlichen Mergecommit. `mergeable` ist unzulässig bei offenen B-Befunden oder offenen erforderlichen A-Vor-Merge-Gates. `next.action=merge` benötigt ein vollständiges positives Review. `next.action=rework` benötigt einen konkreten Reviewbezug und offene technische Befunde. `next.action=done` setzt einen tatsächlich gemergten Stand voraus. Befundkennungen müssen eindeutig sein; doppelte JSON-Schlüssel und nicht sicher darstellbare Issue-/PR-Nummern werden abgewiesen. Ein Schemafehler wird korrigiert, nicht mit großzügigen stillen Defaults importiert.

Das Sheet zeigt die Übernahme zuerst als Vorschau. Ein anderes Repository, eine unbekannte Version, ungültige Typen oder widersprüchliche Zustände werden abgewiesen. Ein neuer Issue-/PR-/Headstand wird sichtbar ersetzt; der Benutzer übernimmt ihn ausdrücklich. Persönliche Einstellungen, lokale Arbeitswurzel und Merge-/Bereinigungsoption werden niemals durch Ergebnis-JSON geändert.

JSON ist Arbeitsmaterial und keine Quelle von Autorität. Vor der nächsten Aktion die Repository-/PR-Quellen und aktuellen Commits wieder prüfen. Eine alte Übergabe darf weder einen inzwischen geänderten PR abnehmen noch aus einem selbst berichteten `mergeable` einen unmittelbaren Merge ohne Review machen. Nicht ausgeführte Netz-/Kontoprüfungen werden durch Import nicht nachgeholt.
