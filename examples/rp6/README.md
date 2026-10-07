# RP-6: fester Sechserpilot

Vorabplan vom 06.10.2026 zu [Issue #40](https://github.com/venomenon328/picross/issues/40).
[plan.json](plan.json) bindet die sechs unveränderten Quellen, Endmatrizen,
Nachweise, Referenzbilder, Versionen, Motivbriefings und Budgets vor neuer Bildarbeit.
F-04 bleibt unverändert; F-05 bis F-09 sind zusätzliche feste Pilotplätze.
Keine neue Rasterproduktion, Reparatursuche oder automatische Ersatzproduktion.

Pro zusätzlichem Motiv höchstens eine Erstfassung und eine Korrekturrunde;
fehlgeschlagene und verworfene native Aufrufe zählen mit, insgesamt maximal zehn.
Geeignete vorhandene Illustrationen dürfen nach tatsächlicher Paarprüfung dienen.
Unverzerrte Format-/Rahmenanpassungen werden separat protokolliert.

Kanne: einfache Silhouette. Katze: etwa 100×66 Motivfläche in 100×100.
Größe belegt weder Schwierigkeit noch vollflächige Detailkomposition.
Rechteckexport ist nicht Teil dieser P1-Abdeckung. Menschliche Minuten sind
nicht beobachtet. Eigene Agentensichtung ersetzt kein unabhängiges Review.

Eigentümerproben und Phasenentscheidung bleiben offen; keine Pilotgesamtfreigabe,
kein Merge/Release und kein vorzeitiger Abschluss von Parent #34.

## Lieferung und Bilanz

[Manifest](manifest.json) bindet sechs technisch zertifizierte Paare, mit
begründetem tatsächlichem eigenem Sichturteil. Redaktionelle Endfreigabe,
unabhängiges Review und Eigentümerproben sind offen. Fünf neue Registrierungen,
keine neuen Raster oder Reparatursuchen. Zwei neue native Bilddateien (je ein
Aufruf, keine verworfene Fassung), drei vorhandene Illustrationen übernommen;
[Prompts](artwork/prompts.json), [Dateiaufbereitung](artwork/preparation.json).

Paaransichten mit Motivspoiler: [F-04](views/f04.html), [F-05](views/f05.html),
[F-06](views/f06.html), [F-07](views/f07.html), [F-08](views/f08.html), [F-09](views/f09.html).
Die PNG-Raster enthalten exakt eine Bildzelle je finaler Matrixzelle; HTML zeigt
sie ohne Glättung neben den echten Ressourcen. Ergänzende PNG-Kontaktansichten
sind reine Ansichten, keine neuen Bildfassungen.

[Produktionsbilanz und technische Zuordnung](../../docs/RP6_VERIFICATION.md)
trennt ursprüngliche RP-4/RP-5-Ausbeute, neue Export-/Bildarbeit und noch fehlende
reale Befunde. [Neutrale Eigentümeranleitung](../../docs/RP6_OWNER_TRIAL.md),
[leeres Protokoll](owner-protocol.json). Kein Eigentümerumfang automatisch festgelegt.

```sh
python -m tools.puzzle_production.rp6 --output-dir artifacts/rp6-replay
```

Die isolierte Image-Umgebung mit Pillow exakt 12.3.0 ist erforderlich.
Frischer Replay überschreibt keine Originaldatei. Er prüft Quellen, alle
Definitionen/Assets, vollständige Import-/Reparaturnachweise und Pair-Raster.
Laufzeitwerte, Commit-/Basis-/Checkout-/Runbindung stehen im erzeugten Report.
Das getrennte kleine CI-Artefakt `rp6-review` enthält alle 60 nativen Produktbilder
und bindet das vollständige Windows-ZIP samt EXE-Hashes.
