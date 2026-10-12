# Entscheidungen – r03

- Eingangsprüfung: alle 35 Inventardateien, Inventarhash, beide PNGs und Pflichtquellen stimmen. Im Eingang fehlte die separate Motivfreigabe; bis zur tatsächlichen Antwort wurde kein Raster produziert.
- Nutzer gibt MA-r01 samt 40×40-Mono-/area-/Hintergrundcrop-Korridor ausdrücklich frei. Erklärung und UTC-Empfangsprotokoll stehen in `approvals/motif-MA-r01.json`; genaue historische Sendezeit dieser neuen Antwort ist nicht exponiert.
- Vor Import fixiert: Crop [66,40,1240,1214], exact, Schwellen 96/128/160/192, Budgets 120 s/100000 Linien je Solver/Prüfer. Vier unterschiedliche Matrizen, keine Zusatzkandidaten.
- area-96/128: geprüfte Fixpunkte mit 10/8 offenen Zellen. Keine Unlösbarkeits-/Mehrdeutigkeitsbehauptung aus dem Status abgeleitet. area-160/192: zertifiziert, jedoch schwächere Wurzel-/Negativraumdarstellung.
- area-128 als Motivreferenz gewählt. Vor Suche harte Maske für 1597 Zellen, drei erlaubte lokale Korrekturstellen, maximal zwei Zelländerungen, 96 Vorschläge/16 Bewertungen, Seed 39; keine Lockerung.
- Reparatur gefunden nach drei Vorschlägen und drei Bewertungen einschließlich Referenz: (27,28) ink→empty, (14,37) empty→ink, nullbasiert. Bestehende Trennung verbreitert und vorhandener Wurzelast verbunden. Keine materielle Motivänderung festgestellt; eigene Sichtprüfung ersetzt keine Endabnahme.
- Neuer finaler Nachweis vom unbekannten Raster, unabhängige CLI-Prüfung und vollständiger RP-5-Replay erfolgreich; Hinweise und Endmatrix stimmen exakt. Endkandidat bleibt explizit Reparatur, kein unveränderter Originalimport.
- L3 als editorial_estimate, plausibel L2–L4, Vertrauen low. Kein validierter Schwierigkeitsanalysator und keine Lösungszeit erfunden.
- Endabnahme ausstehend. `content_ready` ist keine Katalogfähigkeit oder Veröffentlichung. Neuer Zieladapter und gemeinsamer Index bleiben spätere Kataloggrenzen.
- Historische Quelldokumente/Provenienz bleiben unverändert und enthalten damalige offene Felder. Aktueller Stand ist ausschließlich r03-Handoff mit separaten Freigabebelegen; r02 zusätzlich vollständig als Original-ZIP erhalten.
