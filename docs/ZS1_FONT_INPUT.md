# ZS-1 · Fontinput und konkrete Liefergrenze

Stand: 07.10.2026 · ZS1-N03 **blockiert durch fehlende Rechtebelege**, Dateien vorhanden

Beide TTFs aus dem nicht versionierten Eigentümerordner
`E:\Downloads\zs1-fonts` wurden vollständig gelesen und gehasht. Der Eigentümer
benannte anschließend die unten verlinkten DaFont-Fundstellen. Die daraus frisch
abgerufenen Originalarchive enthalten byteidentische TTFs. Keine Kandidatenbytes
wurden in Repository, CI-Eingaben oder Export kopiert. Die zusätzliche OTF von
Bakso Daging ist kein dritter Kandidat.

| Kandidat | Identität und Herkunft | Vorliegender Beleg / offene Rechte |
| --- | --- | --- |
| Bakso Daging Regular | Hasna / Viola Type, Silverdav Studio; Version 1.000, PostScript BaksoDaging; 128924 Bytes. [Eigentümerquelle](https://www.dafont.com/de/bakso-daging.font), [Originalpaket](https://dl.dafont.com/dl/?f=bakso_daging). | Autorenhinweis erlaubt private und kommerzielle Nutzung; entsprechender Hinweis auch in name-ID 13. Keine beigefügte EULA/README. App-Einbettung, Weitergabe eingebetteter Fontsoftware und öffentliche Rohdateiverteilung nicht ausdrücklich geklärt. |
| Chalkboard Regular | Florence S laut [Eigentümerquelle](https://www.dafont.com/de/chalkboard-3.font); Version 001.001, Calligraphr-ID vom 24.07.2021; 21976 Bytes. [Originalpaket](https://dl.dafont.com/dl/?f=chalkboard_3). | DaFont-Kategorie „100% Kostenlos“, kein Autoren-Lizenztext, keine name-ID 13/14, Originalpaket enthält nur die TTF. Konkrete Bedingungen für kommerzielle Nutzung, App-Einbettung und öffentliche Weitergabe fehlen. |

Die anfängliche Suchzuordnung von Chalkboard zu einer Privatnutzungslizenz war
falsch: Sie betraf eine andere Zuordnung bei einem gleichnamigen Font.
Maßgeblich ist die bytebestätigte Florence-S-Quelle. Weder „100% Kostenlos“ noch
die technischen OS/2-fsType-Werte (Bakso 8, Chalkboard 0) ersetzen eine
Weitergabe-/App-Lizenz. Es wird kein Verbot erfunden; die nötige Erlaubnis ist
mit den vorhandenen Belegen nicht hinreichend nachgewiesen.

**Konkreter Bedarf:** je Kandidat die zu diesen Bytes gehörenden Lizenzbedingungen
oder eine ausdrückliche Erlaubnis des Rechteinhabers für kommerzielle Spielnutzung,
Einbettung und Verteilung im Windows-Studienpaket sowie Aufnahme der TTF in das
öffentliche GitHub-Repository. Auch eine nur bestimmte Verteilform erlaubende
Lizenz muss genau zu diesem Lieferweg passen. Keine Lizenz wird eigenmächtig
gekauft, kein Rechteinhaber ohne Auftrag angeschrieben.

Die unabhängige Lieferung verwendet ausschließlich die bereits gebündelte
**IBM-Plex-Sans-Referenz**. Sie ist kein Ersatzkandidat und keine neue Fontwahl.
N03, A01/A02 für beide Kandidaten und der vollständige kombinierte Abschluss
bleiben offen. Nach Klärung gehören beide Ressourcen ausschließlich unter
`prototypes/p1/study/`; der reguläre Export muss sie weiterhin ausschließen.
Der dann nötige echte Hinweisvergleich einschließlich Metriken, Ziffern bis 100,
C1/Marker/Tooltip und eventuell explizitem Markerfallback ist nicht durchgeführt.

[Maschinenlesbare Identitäten und Hashes](zs1-font-input.json).
