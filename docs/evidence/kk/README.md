# KK-Diagnoseeingänge

Dokument-ID: `kk-diagnostic-inputs`
Status: `reference`
Zuständigkeit: Erhaltene Originale für die ausdrücklich aufrufbare KK-Diagnose.

Die vorhandenen JSON-/PNG-Dateien werden von `tools/kk_windows_probe.py` konsumiert.
Sie bleiben deshalb mit ihren tatsächlichen Byte- und Quellenbindungen erhalten.
Sie sind keine aktuelle Pflichtgalerie und keine eigenständige Katalog-Sollnorm.
Aktuelle Darstellung steht in [CATALOG_PRESENTATION](../../game/CATALOG_PRESENTATION.md),
ausgewählte Dauerprüfungen im [nativen Modulvertrag](../../ci/CI_C_NATIVE_GROUPS.md).

Frühere Berichtstexte und deren Prüfstand sind über
[history](../../history/README.md) erreichbar. Eine erneute Diagnose benötigt
einen passenden aktuellen Anlass; alte Liefertexte sind kein neuer Auftrag.

## Gebundene Originale

Die 18 unverkleinerten Kartenrechtecke stammen aus einem isolierten synthetischen
Windows-/NVIDIA-Lauf. Das [Manifest](native-crops.json) bindet Host, Framebuffer, UI,
Quellrechtecke, Prüfwerte und die damaligen Runtime-Dateihashes.

| Fläche / UI | Neu → Begonnen → Gelöst → Reset | Langer Motivname |
| --- | --- | --- |
| 1280×720 / 125 % | [Neu](kk-new-1280-card.png), [Begonnen](kk-begun-1280-card.png), [Gelöst](kk-solved-1280-card.png), [Reset](kk-reset-1280-card.png) | [Zwei Zeilen / Auslassung / Resettooltip](kk-long-name-1280-card.png) |
| 1920×1080 / 100 % | [Neu](kk-new-1920-card.png), [Begonnen](kk-begun-1920-card.png), [Gelöst](kk-solved-1920-card.png), [Reset](kk-reset-1920-card.png) | [Zwei Zeilen / Auslassung / Resettooltip](kk-long-name-1920-card.png) |
| 2560×1440 / 125 % | [Neu](kk-new-2560-card.png), [Begonnen](kk-begun-2560-card.png), [Gelöst](kk-solved-2560-card.png), [Reset](kk-reset-2560-card.png) | [Zwei Zeilen / Auslassung / Resettooltip](kk-long-name-2560-card.png) |

[Ungültige Daten](kk-error-card.png), [Backupübernahme](kk-recovered-card.png) und
[Backuperneuerung](kk-backup_invalid-card.png) zeigen dieselbe Geometrie mit innen
scrollbarer Diagnose. Die Recoveryausschnitte zeigen den nach unten gescrollten
Textaktionsbereich; die vollständige Diagnose bleibt nach oben erreichbar.
