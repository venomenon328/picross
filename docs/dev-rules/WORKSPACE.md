# Arbeitsablage und Bereinigung

Der Auftrag kann eine absolute lokale Arbeitswurzel vorgeben. Neue eigene Checkouts, Worktrees, Downloads und temporäre Arbeitsdaten darunter in einem eindeutig zum Auftrag gehörenden Unterordner anlegen; temporäre Prozessumgebungen entsprechend konfigurieren. Einen bestehenden beauftragten Checkout respektieren. Ist die vorgegebene Wurzel in der ausführenden Umgebung nicht verfügbar, den konkreten Konflikt melden statt unbemerkt einen anderen Datenträger zu verwenden.

Die Wurzel ist kein Löschauftrag für ihren gesamten Inhalt. Eigene Neuanlagen von vorbestehenden Dateien unterscheiden; pro Auftrag einen kleinen Besitz-/Zweckvermerk im Arbeitsordner führen. Keine fremden unversionierten Daten aufnehmen oder entfernen. Symlinks/Junctions dürfen keine Bereinigung in fremde Pfade lenken.

Ein Implementierungsauftrag mit aktivierter Bereinigung erlaubt und verlangt, selbst erzeugte entbehrliche Arbeitsdaten nach Abschluss zu entfernen. Vorher Commits pushen, erforderliche aktuelle Reviewbelege übergeben und alle ungesicherten/fremden Änderungen ausschließen. Eigene saubere Worktrees mit dem dafür vorgesehenen Git-Befehl entfernen. Keine Löschung des Benutzer-Checkouts, des Arbeitswurzelverzeichnisses selbst oder entfernter Branches daraus ableiten.

Testprozesse verwalten ihre temporären Unterordner mit Kontextmanagern oder `try/finally` und kontrollieren den tatsächlichen Abschluss. Nach hartem Abbruch dürfen nur markierte eigene verwaiste Ordner nach Pfad-, Besitz-, Alter- und Lockprüfung aufgeräumt werden. Keine pauschale TEMP-/artifacts-Löschung, keine Umgehung einer abgelehnten Aktion und keine Änderung der Berechtigungssteuerung. Ein Full-Access-Profil ist keine Garantie, dass eine Plattform jede einzelne Löschung erlaubt.

Ergebnis: bereinigt, noch für konkreten Review benötigt oder blockiert mit Restpfad und Grund. Keine vollständige Löschung bei Dateisperren oder Policyblockade behaupten. Abgelaufene lokale Altbestände anderer Läufe benötigen nachvollziehbares Eigentum und den passenden Auftrag; ein historischer Dateiname allein reicht nicht.
