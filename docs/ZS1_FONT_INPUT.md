# ZS-1 · Fontinput und Verwendung nach E2

Stand: 07.10.2026 · **Beide Kandidaten gemäß Eigentümerentscheidung E2 aufgenommen**

Die beiden Original-TTFs aus `E:\Downloads\zs1-fonts` wurden vollständig gelesen,
gehasht und mit den vom Eigentümer benannten DaFont-Originalarchiven bytegenau
verglichen. Die zusätzliche Bakso-OTF ist kein weiterer Kandidat.

| Kandidat | Identität / Quelle | Verfügbare Nutzungshinweise |
| --- | --- | --- |
| Bakso Daging Regular | Hasna / Viola Type / Silverdav Studio; Version 1.000, PostScript BaksoDaging; 128924 Bytes. [Quelle](https://www.dafont.com/de/bakso-daging.font), [Originalpaket](https://dl.dafont.com/dl/?f=bakso_daging). | Autorenhinweis erlaubt private und kommerzielle Nutzung; auch in name-ID 13. Keine zusätzliche EULA/README im Archiv. |
| Chalkboard Regular | Florence S laut [Quelle](https://www.dafont.com/de/chalkboard-3.font); Version 001.001, Calligraphr-ID vom 24.07.2021; 21976 Bytes. [Originalpaket](https://dl.dafont.com/dl/?f=chalkboard_3). | Veröffentlichungskategorie „100% Kostenlos“; kein Autoren-Lizenztext in der Datei, keine name-ID 13/14, Archiv enthält nur die TTF. |

[ZS1-E2](https://github.com/venomenon328/picross/pull/55#issuecomment-6042067344)
hält die ausdrückliche Eigentümerentscheidung fest: Beide Fonts wurden durch die
Designer mit „100% free“ beziehungsweise privater/kommerzieller Nutzung veröffentlicht;
weitere Bedingungen sind nicht verfügbar. Die vorhandenen Hinweise werden für die
beauftragte Kandidatenverwendung im öffentlichen Studienpfad und Windows-Studienexport
akzeptiert. Damit entfällt der vorherige Rechtebeleg-Blocker. Es wird keine zusätzliche
EULA, OFL oder neue Rechteinhabererlaubnis behauptet. Die technischen fsType-Werte
(Bakso 8, Chalkboard 0) werden nur als Metadaten dokumentiert.

Die anfängliche Zuordnung von Chalkboard zu einer Privatnutzungslizenz betraf einen
anderen gleichnamigen Font und bleibt korrigiert. Maßgeblich ist die bytebestätigte
Florence-S-Quelle. [Mitgelieferte Hinweise](../prototypes/p1/study/fonts/NOTICES.md)
und [Maschinenmanifest mit Font-/Archivhashes](zs1-font-input.json).

## Native Darstellung

Beide unveränderten Ressourcen liegen ausschließlich unter `prototypes/p1/study/fonts/`.
Der reguläre Export schließt `study/*` aus; nur die Studien-EXE enthält sie.
Der Export-Smoke prüft die eingebetteten TTF-Bytes erneut gegen beide Originalhashes.
Plex bleibt die ausdrücklich beschriftete historische Referenz, kein dritter Kandidat.

Beide Kandidaten enthalten 0–9 vollständig. Chalkboard fehlen `…` und `–`.
Bakso enthält Zuordnungen für diese Zeichen, sein Auslassungszeichen ist in der
nativen Probe aber nicht als übliche Ellipse erkennbar. Deshalb verwenden beide
Kandidaten bewusst die bestehenden Plex-Zeichen `…` und `–` für die Navigation.
Dies gilt auch für Markermaße und leere Tooltipfolgen. Systemfallback ist für
die Kandidaten ausgeschaltet. Kein Austausch von Ziffern.

Bakso verwendet den bisherigen nominalen Schriftgrad. Chalkboard wird wegen seiner
kleineren Ziffern innerhalb des em gleichmäßig mit Faktor 1,35 (auf ganze Pixel gerundet)
gezeichnet, im Raster zusätzlich auf Zellbreite minus 4 px begrenzt (Minimum
11 px bei Chalkboard, 8 px bei Bakso); beide Kandidaten werden anhand ihrer gemessenen Glyphengrenzen vertikal zentriert.
Keine veränderten Fontbytes, künstliche Fettung oder verzerrten Konturen. Die
Ziffernprobe und Tooltips verwenden dieselbe Größennormalisierung. Status/C1 bleiben.
Die Spaltenrandprüfung verwendet gemessene Glyphengrenzen einschließlich Marker;
Zeilen-/Spaltenslots bleiben 30/18 px × UI-Skalierung. Native Berichte protokollieren
Schriftgrad, tatsächliche maximale Hinweisbreite, Glyphengrenzen und Slotmaße.

Die finale Fontwahl ist weiterhin Teil von ZS1-M01; E2 ist die Freigabe beider
Kandidaten für den Vergleich, keine vorweggenommene Auswahl oder Mergefreigabe.
