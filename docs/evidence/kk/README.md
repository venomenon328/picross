# Native KK-Originalausschnitte

18 unverkleinerte Kartenrechtecke aus dem isolierten synthetischen Windows-/NVIDIA-
OpenGL-Lauf. Keine echten Spielstände oder produktiven Motivdaten.
[Manifest](native-crops.json) bindet Host, Framebuffer, UI, Quellrechtecke,
Prüfergebnis, tatsächliche Bereichsmaße und Runtime-Dateihashes.

| Fläche / UI | Neu → Begonnen → Gelöst → Reset | Langer Motivname |
| --- | --- | --- |
| 1280×720 / 125 % | [Neu](kk-new-1280-card.png), [Begonnen](kk-begun-1280-card.png), [Gelöst](kk-solved-1280-card.png), [Reset](kk-reset-1280-card.png) | [Zwei Zeilen / Auslassung / Resettooltip](kk-long-name-1280-card.png) |
| 1920×1080 / 100 % | [Neu](kk-new-1920-card.png), [Begonnen](kk-begun-1920-card.png), [Gelöst](kk-solved-1920-card.png), [Reset](kk-reset-1920-card.png) | [Zwei Zeilen / Auslassung / Resettooltip](kk-long-name-1920-card.png) |
| 2560×1440 / 125 % | [Neu](kk-new-2560-card.png), [Begonnen](kk-begun-2560-card.png), [Gelöst](kk-solved-2560-card.png), [Reset](kk-reset-2560-card.png) | [Zwei Zeilen / Auslassung / Resettooltip](kk-long-name-2560-card.png) |

[Ungültige Daten](kk-error-card.png), [Backupübernahme](kk-recovered-card.png) und
[Backuperneuerung](kk-backup_invalid-card.png) zeigen dieselbe Geometrie mit innen
scrollbarer Diagnose. Die Recoveryausschnitte zeigen den nach unten gescrollten
Textaktionsbereich; die vollständige Diagnose bleibt nach oben erreichbar.

Die Bilder wurden im neuen nativen Windows-Lauf der KK-Reviewnacharbeit aus
den manifestgebundenen Runtimebytes aufgenommen. Die 17 unveränderten Ausschnitte
wurden neu erzeugt; die Fehlerkarte zeigt den aktuellen Scrollbar-Hoverzustand. `tools/kk_windows_probe.py` verlangt am finalen sauberen
Head dieselben Bytes und reproduziert alle 18 PNG-Hashes. Der PR führt diesen
erneuten Windows-Lauf samt finaler Head-/Basis-/CI-/Checkout-/EXE-/PCK-Bindung.
Erst dieser Nachweis bindet die Bilder an den finalen Stand. Quellprobe und echter
CI-Spielerstart sind getrennte Prüfschritte. Kein unabhängiges Review oder
persönliche Eigentümerabnahme durch diese technische Lieferung.
