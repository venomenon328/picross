# Getrennter Selbstreview ZA-1

Geprüfter Implementierungsstand: `71e0d80017a31e661c392e174d14301e74d5f0d4`.
Basis: `039f59d9a94ad6c2fea32a900d03d1d3b8a7df4c`. Der vollständige Diff umfasst
162 Dateien einschließlich der vier versiegelten Testpakete und des kompakten
Referenzderivats. Die anschließenden Belegdateien ändern keinen Produktcode.

Prüfschwerpunkte: Eingangsgrenze/Windows-Pfade, Inventar und ursprüngliche
Handoff-Auswahlbindung, frische RP-3/RP-5-Prüfung, Export aus geschriebenen Bytes,
historische Reservierungen, explizite Savepfade, Fehler-/Wiederholungsverhalten,
Runtime-Spoilergrenze und tatsächlicher PCK-Inhalt. Neue/berührte Quellen wurden
getrennt von der Implementierung gegen Issue und Fachverträge geprüft.

Im Selbstreview erkannt und im genannten Commit behoben:

- **B-SR01:** Parallel abgeschlossene Registrierung konnte einen veralteten Plan
  hinterlassen. Exklusives Journal, erneute Index-/Zielprüfung und atomarer
  Indexersatz verhindern Übernahme eines veralteten Plans. Unterbrechung vor/nach
  zentralem Index wird reproduziert; Recovery stoppt bei fremdveränderten Bytes.
- **B-SR02:** Exportpalette konnte bei lexikografischer Farbabbildung anders als
  die Palette-Buttonreihenfolge liegen. Runtimepalette wird nach numerischer ID
  geschrieben; native Farbspiel- und Rasterpixelprüfung bestätigt die Zuordnung.
- **B-SR03:** Feste Sechserassertions hätten spätere Datenregistrierungen trotz
  gültigen Spiels abgewiesen. Historischer Prefix bleibt fest geprüft, die
  Gesamtzahl folgt der Registry. Smoke erlaubt den echten Abschluss eines gültigen
  Einzellenrätsels. Neue neutrale Blattnummern folgen den neun Reservierungen.

Tatsächlich lokal geprüft: 122 schnelle Tooltests (ein bestehender optionaler
Test übersprungen), 120 Produktionstests, darunter zwölf neue Adaptertests;
vollständiger Produktlauf mit Integration/Piloten/Visual/PERF-B und Windowsstart
im Arbeitsbaum vor den letzten Reviewkorrekturen; Toolchain-Preflight erfolgreich.
Der vollständige Produktlauf blieb bei 60.372.056 Gesamtbytes, davon 20.385.183
technisch, und etwa 384 Sekunden innerhalb der bestehenden Grenzen.

Am genannten Implementierungscommit zusätzlich gebunden: unverändertes
[Original-ZIP](original-input.json), finaler isolierter Windowsdurchstich mit
neuen IDs, vollständiger Save-/Recovery-Suite, gegenseitigen Resetgrenzen und
PCK-/Exportstart. Die finalen Remotechecks beziehen sich auf den PR-Head und
seinen tatsächlichen Test-Merge; sie werden im PR separat verlinkt.

Gezielt visuell geprüft wurden native Mono-/Farbkontexte: ungelöster neutraler
Titel, quadratische Rasterzellen in beiden Rechteckorientierungen, falsche eigene
Miniaturzelle ohne Reveal, proportionales gelöstes Raster/Artwork und verdientes
Albumbild nach Neustart. Die Bilder sind technische künstliche Fixtures, kein
Kunsturteil über Knoblauch.

Urteil: Selbstreview abgeschlossen; unabhängige technische und visuelle
Zweitprüfung bleibt vor Merge offen. Keine mergefähige Endabnahme, keine
Knoblauch-Endfreigabe und kein verpflichtendes Probespielen daraus abgeleitet.
