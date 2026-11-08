# Erste Modellhypothese H1 · vor F08-Auswertung

08.11.2026 · Referenzplan 1ac4d44a75af9a604bffcb985c0570954beea761.
Noch keine Eigentümerurteile, Normfreigabe oder menschliche Kalibrierung.

F01/F03/F04 haben Oklab-Abstände 30.055702/22.237591/35.939433.
F02 und die seltene Paarung F07 c01/c08 liegen bei 1.341811.
F06 enthält dunkle Tonabstufungen bei 8.714125 und 9.475212;
die Zuordnung der kleinen blassen Ziffern ist deutlich anspruchsvoller als
bei F01/F03. F05 zeigt auf Papier unzureichende helle Hinweisfarben trotz
einzelner großer Paarabstände (weiß/gelb 17.641978).
Dies sind Implementiererbeobachtungen an Originalen, keine Eigentümerlabels.

Eine reine Helligkeits-/Kontrastuntergrenze zwischen Vordergrundfarben wäre
ungeeignet: F01/F03 haben trotz unterschiedlicher Farbtöne nur 1.101501 bzw.
1.028384 Verhältnis. Oklab erfasst dagegen Farbton und Helligkeit gemeinsam.
Auch Oklab misst keine Pixelgröße, C1-Zuordnung oder Lesbarkeit auf Papier.

H1 als begrenzter Vorschlag: paarweiser Abstand D < 10 technisch negativ;
10 <= D < 15 technisch positiv mit expliziter Grenzfallwarnung;
D >= 15 technisch positiv ohne Distanzwarnung. Dazu zwingend die bereits
bestehende visuelle Raster-/Hinweisprüfung, Luminanz-/Kontrastwerte nur Diagnose.
Die runden Grenzen sind eine konservative Arbeitshypothese im beobachteten
Intervall zwischen problematischen dunklen Nahpaaren und klaren Farbtonpaaren,
kein empirisch bestimmtes Optimum. Die Breite der Warnzone macht gerade
die offene Eigentümerentscheidung sichtbar. Keine Grenzverschiebung für
ein erwünschtes Urteil im zurückgehaltenen F08-Satz.

F08-Farben bleiben unverändert. Erst nach Veröffentlichung dieses Texts
seine sechs Paarwerte und seine echten Zell-/Hinweisbilder beurteilen.
Die genaue ganzzahlige Vergleichs-/Rundungssemantik wird im Normvorschlag
präzisiert; keine laufende Produktionsimplementierung.
