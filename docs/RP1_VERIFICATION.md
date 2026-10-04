# RP-1: Prüfvertrag und Nachweiszuordnung

Stand: 04.10.2026 · Arbeitsfassung 0.2 · RP-1 unabhängig reviewt und integriert

Auftrag: [Issue #35](https://github.com/venomenon328/picross/issues/35), vollständiger
Body einschließlich Umsetzungsvorbereitung vom 04.10.2026; Parent
[#34](https://github.com/venomenon328/picross/issues/34) bleibt offen.
[Fachvertrag](PUZZLE_PRODUCTION.md), [Werkzeuganleitung](../tools/puzzle_production/README.md).
Kein P1-Code übernommen oder verändert; F-01/F-02/H1 bleiben begrenzte Referenzen.

## Basis und Integration

Historische Startprüfung: #41 offen und Draft, Head unverändert
`fc8494b57f7fe59515f12fb1b4f3fc89a12f91bf`; `main` unverändert
`409febeeb5209ef18e8e27e77fd93a09c9850488`. Keine späteren Kommentare in #34/#35,
keine Kommentare/Reviews in #41, keine zusätzlichen AGENTS-Bereichsregeln.
Arbeitsbranch `feat/35-monochrome-deduction-core`; Draft-Ziel
`chore/34-puzzle-production-spec`. Der Paketdiff enthält ausschließlich RP-1.
Nicht in den Spezifikationsbranch mergen. Bei Integration von #41 regulär mit dem
aktuellen `main` integrieren, PR umstellen, Diff und alle Nachweise neu zuordnen;
kein Force-Push und kein bloßer Zielwechsel. Diese Integration wurde anschließend
ausgeführt: #41 als `79b1dc05a2139e20924c3c8f2772f3a178b3814e`, #42 als
`b18a23460708509adac2f04e724809cf0cc8b959` nach `main`.
[Integrationsreview R3](https://github.com/venomenon328/picross/pull/42#pullrequestreview-5405127592)
bindet Head `72cb63b3b3f51d50c2f9b2911b4520988e325f7d`, Basis `79b1dc05...`
und Test-Merge `547ec1d...`: B-01/A-01 abgeschlossen, alle vier Jobs erfolgreich.
Diese Nachweise bleiben historisch; die [RP-2-Erweiterung](RP2_VERIFICATION.md)
benötigt eigene aktuelle Checks und unabhängiges Review.

## Fachliche Abdeckung

| Kriterium | Ausführbarer Nachweis |
| --- | --- |
| RP1-A01 | `test_lines.py`: 22557 vollständige Domainvergleiche für n=1..6, alle 1/2/3-Domainkombinationen, alle realisierbaren Hinweise plus übervolle Listen. Solver und Prüfer jeweils gegen unabhängige Bitfolgenaufzählung; partielle Unterstützung, Leer-/Volllinien, Lücken, gleiche Hinweise, Widerspruch und Langlinie. |
| RP1-A02 | `test_core.py` + vier Logikfixtures: 3×3 vollständig deduktiv/1 Lösung; 4×4 eindeutig aber Fixpunkt/1 Lösung; 2×2 mehrdeutig/2 Lösungen; 1×1 widersprüchlich/0 Lösungen. Alle Eigenschaften über unabhängige komplette kleine Rasteraufzählung; Rechtecke und beide 1D-Richtungen zusätzlich. |
| RP1-A03 | `ProofAttackTests`: Daten-/Profiltausch, manipulierte Voraussetzungen/Folgerungen/Offsets, versteckte Startdomains, Reihenfolge-/Spurkürzung, falsche Enddomains und unbegründeter Widerspruch. Gezielter vergifteter Linienchecker belegt zusätzlich die direkte Endrasterprüfung. Logikeingang lehnt Zielbild/Lösung/Motiv ab; Prüfer funktioniert mit gesperrten Solverfunktionen. |
| RP1-A04 | Drei zulässige Linienreihenfolgen mit identischen Fixpunkten; korrekte Teilspur mit mindestens einem Schritt als falscher Fixpunkt/Abschluss abgewiesen; Arbeits-/Zeitlimit und Cancellation; CLI-MemoryError, technischer Fehler, Timeout/Prozesstod im Benchmark ohne Abnahme/Zertifikat. |
| RP1-A05 | `benchmark.py`: tatsächlich ausgeführte 40×40-/100×100-Balkenfälle und informationsarmer 100er-Linienfall, jeweils isolierter Solve und frische Prüfung; Messung und Budgets unten. |
| RP1-A06 | CLI-Subprozesstests an gespeicherten Dateien, dokumentierte Befehle, eigener CI-Job `puzzle-production`, aktueller `docs`-Job und vollständiger Diffcheck. Bestehende Produkt-/Preflight-Jobs unverändert und gesondert berichtet. |

Der kleine unabhängige Oracle gehört ausschließlich zu den Tests. Solver und Prüfer
erhalten weder Testwitness noch Zielmatrix. Der eindeutig stagnierende 4×4-Fall hat
Zeilen `[], [], [2], [1,1]` und vier Spalten `[1]`. Sein einziges gültiges Raster
wird durch erschöpfende unabhängige Enumeration bestätigt; Stillstand allein macht
diese Aussage nicht. Ein vollständiger geprüfter Deduktionsnachweis beweist Eindeutigkeit.

## Vorab gebundene Referenzabnahme

Vor dem Abschlusslauf festgelegt, unverändert aus #35: **120 Sekunden je Fall für
Solve/Serialisierung/frische Prüfung zusammen**, **512 MiB gemessener Peak-RSS je
isoliertem Prozess** auf Linux. Ubuntu-24.04-Joblimit 15 Minuten, Python 3.11+.
Keine nachträgliche Budgeterhöhung oder Erleichterung nach Fehlschlag.

Linux-Worker messen ihren eigenen Peak via `resource.getrusage(RUSAGE_SELF).ru_maxrss`
in KiB und speichern Bytes. Solve-/Serialisierungs-/interne Prüfdauer sowie frische
Prüfdauer, Prozesszeiten und gemeinsame Walltime werden getrennt gespeichert.
Virtuelles `RLIMIT_AS=1024 MiB` ist zusätzlich durchgesetzt und vom RSS-Budget getrennt.
Timeout beendet den Worker und lässt `accepted=false`; fehlende Worker-Messdaten und
Prozessfehler ebenso. Der Bericht speichert Hardware/Python, Head, Checkout/Test-Merge,
Basis, Arbeitsbaum, Logik-/Profil-/Proofhash, Status und tatsächlich ausgeführte Schritte.

Die Balkenreferenzen besitzen variierende Zeilen-/Spaltenhinweise, Leer- und Füllzellen.
40×40 führt 276 Solver-Linienauswertungen und 230 Fortschrittsschritte aus;
100×100 führt 1038 Auswertungen und 938 Schritte aus. Frische unabhängige Replayprüfungen
bearbeiten 310 beziehungsweise 1138 Linien einschließlich vollständiger Endkontrolle.
Das ist keine bloße Dimensionsakzeptanz. Der informationsarme Fall prüft 200 Linien
im Solver und 200 Linien im unabhängigen Fixpunktcheck; jede unbekannte 100er-Linie
hat `C(81,20)=4694436188839116720` Möglichkeiten ohne Materialisierung dieser Liste.

## Prüfstand und Gates

Lokale Entwicklungsprüfung: Windows 11, temporäre offizielle portable CPython-3.12.10-
Laufzeit im ignorierten `.venv`-Verzeichnis, keine global installierten Abhängigkeiten.
Die Fachtests und tatsächlichen Referenzabläufe wurden lokal ausgeführt. Frische
Prüfung bestätigt beide vollständigen Raster und den informationsarmen Fixpunkt.
Die lokale Windows-Messung liefert keinen Linux-Peak-RSS; der Benchmark meldet deshalb
korrekt `accepted=false`. Sie ist **kein RP1-A05-Abnahmenachweis**. Maßgebliche
vollständige Abschlussprüfung erfolgt in Remote-CI am gelieferten Head/Test-Merge.
Konkrete damalige Runs, Messwerte, Artefaktlinks und Ergebnisse stehen in PR #42.

Verbindlicher Dokumentweg zusätzlich zum neuen Fachjob:

```sh
python3 -m unittest discover -s tools -p 'test_*.py' -v
python3 tools/check_docs.py
git diff --check <tatsaechliche-pr-basis> <head>
```

`docs`, `puzzle-production`, vollständiger Diffcheck und unabhängiges technisches
Review am konkreten Head waren Mergegates, außerdem die Integration von #41.
Sie wurden im oben gebundenen finalen Integrationsstand erfüllt.
Selbstreview ist keine unabhängige Zweitprüfung. Reale Motiv-/Spielabnahme ist für
RP-1 nicht anwendbar; kein Release oder allgemeiner Produktionsqualitätsnachweis.
