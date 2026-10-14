# Konkrete technische Integrationslücke für Hamburger r04

Inhalt vom Nutzer abgenommen, Randregel-Ausnahme für genau diese hashgebundene Auswahl akzeptiert. Original-ZIP, Handoff und Inventar bleiben unverändert.

Tatsächlicher Exportversuch: Exit 2, `Package is not content_ready`; kein Export erzeugt, keine Registry geändert. Zusätzlich durch aktuellen Code belegt:

- `authoring_package.py`: versiegelte `blocked`-Handoffs besitzen keinen externen, aufgelösten Ausnahmeweg.
- `target_adapter.py`: Randregel wird bedingungslos verlangt; neuer Rasterquellimport muss unverändert zur ursprünglichen Motivdatei und ihrem Crop passen.
- `manual_derivation.py`: ausschließlich feste Mono-Entfernungen (`remove-ink-only`). r04 enthält zusätzlich eine Einfügung und nutzt einen offen dokumentierten, neu importierten Rasterquellstand.

Notwendige begrenzte Erweiterung, noch nicht implementiert: externe echte Endfreigabe und genau gebundene Eigentümerausnahme einlesen; beide festen Edits einschließlich Einfügung aus dem vollständigen Originalreferenzbundle replayen und mit Endmatrix/Logik/Proof vergleichen; historischen blocked-Handoff nur bei exakt passender Erklärung akzeptieren. Randregel weiterhin berechnen und Verletzung sichtbar lassen; nur diese explizit akzeptierte Ausnahme zur Registrierung zulassen. Keinen allgemeinen Force-Schalter oder blanket waiver hinzufügen. Originalpaket nicht umschreiben.

Danach kategorisierten Export, offline Exportprüfung, plan und register über den Adapter durchführen. Synthetische positive/negative Werkzeugregressionen für falsche Bindungen, unautorisierte Einfügung/Ausnahme und geänderten Proof; keine realen Rätseldaten als neue Tests/CI-Fälle. Aktuelle ausgewählte Fach-/Produktchecks folgen dem tatsächlichen Code-Diff. Spiel-/Save-/UI-Verträge nicht erweitern.

Befugnisgrenze: PUZZLE_AUTHORING §1.5 nennt ausdrücklich: „Werkzeugänderungen, Merge und Veröffentlichung sind jeweils getrennte Befugnisse nach Entwicklungsworkflow.“ §8.5 verbietet einen handgeschriebenen Registryeintrag als Ersatz. Der vorliegende Standardauftrag 4 autorisiert die Inhaltsintegration; daraus leite ich keine zusätzliche Änderung des allgemeinen Produktionswerkzeugs ab. Dafür ist ein entsprechender Werkzeugauftrag erforderlich. Keine erneute Bild-/Inhaltsfreigabe anfordern.
