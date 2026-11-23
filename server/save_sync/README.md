# Konto- und Snapshotdienst

Der Dienst implementiert den Serverteil des [SYNC-Vertrags](../../docs/game/SAVE_SYNC.md).
Die Spielclients und der öffentliche Betrieb folgen in eigenen Paketen.
Der Dienst hat keine Rätsellösungen. Die geprüfte Eigenschaft eines Snapshots heißt
`progress_structure_checked`. Sein vollständiges Schema und die Endpunkte liefert
`GET /openapi.json`.

Start und `sync.admin migrate` aktualisieren Datenbankstand 1 atomar auf 2.
Alle gespeicherten Snapshot- und Kandidatenfassungen erhalten die acht Felder von
`picross-progress/v1`. Ein fehlerhafter Altbestand bricht die gesamte Transaktion
ab. Backup und Restore unterstützen Stand 2. Alte Archive werden beim Restore
vor der Veröffentlichung zurückgewiesen.

## Lokaler Betrieb

Die Befehle laufen in diesem Verzeichnis mit Docker Compose und Python 3.11+.
Vor dem ersten Start `SYNC_DB_PASSWORD` als zufälliges Geheimnis in der
Prozessumgebung setzen. Im Produktivbetrieb ist ein geschützter Secret-Speicher
Aufgabe des Betreibers. Die isolierte Datenbank hat keinen Hostport. Der API-Port
bindet an Loopback. Ein fester Projektname trennt das Datenvolume von anderen Diensten.

```sh
docker compose up -d --build --wait
docker compose exec -T api python -m sync.admin migrate
curl --fail http://127.0.0.1:8000/health/ready
docker compose exec -T api python -m sync.admin invite
docker compose stop
docker compose up -d --wait
```

Der normale Start führt ausstehende Migrationen vor der API aus. Die erneute
Migration ist idempotent. Eine Einladung gilt sieben Tage. Die einmalige
Standardausgabe vertraulich übergeben. Register erzeugt Geräte-ID, Sitzung und
Recoverycode. Login mit bekannter Geräte-ID ersetzt nur deren Sitzung. Tokens
und Codes werden als SHA-256-Abdruck gespeichert. Passwörter verwenden die
Argon2id-Empfehlung der gebundenen pwdlib/argon2-cffi (64 MiB, drei Iterationen,
Parallelität vier). Jede Mutation bindet Antwort und Gerätewasserstand in derselben
Transaktion wie den Spielstand. Das Kontoschloss serialisiert konkurrierende
Entscheidungen und Quotenprüfung für dieses Konto.

| Prozessvariable | Standard und Wirkung |
| --- | --- |
| `SYNC_PORT` | 8000, Hostport an 127.0.0.1 |
| `SYNC_ORIGINS` | leer, sonst kommagetrennte exakte Weborigins |
| `SYNC_AUTH_NAME`, `SYNC_AUTH_IP` | 10 je Name, 100 je IP pro gleitenden 15 Minuten, gemeinsame DB |
| `SYNC_BYTES`, `SYNC_PUZZLES`, `SYNC_DEVICES` | 536870912 Snapshotbytes, 2000 Rätsel und 100 Geräte je Konto |
| `COMPOSE_PROJECT_NAME` | picross-save-sync, für unabhängige Instanzen eigene Namen setzen |

Zehn frühere Revisionen und fünf offene Konflikte je Rätsel. Eine Quotensenkung
löscht keine Daten. Proxyheader sind deaktiviert. Bei Weiterleitung zählt die
tatsächliche Peer-IP für das IP-Limit. Für einen öffentlichen Anschluss müssen
TLS, vertrauenswürdige Proxygrenze und Betriebswerte in SYNC-C eingerichtet
und geprüft werden. Containerbasis und PostgreSQL-Image sind per Digest,
Python-Pakete einschließlich transitiver Abhängigkeiten per Version/Hash gebunden.

## Sicherung und kontrollierte Rücksicherung

Ein privates, vom DB-Volume getrenntes Sicherungsverzeichnis anlegen. Nur
vertrauenswürdige Archive des eigenen Dienstes zurückspielen. Der Betreiber
startet täglich `backup` mit eigenem Tagesnamen, hält sieben tägliche und vier
wöchentliche Stände und rotiert erst nach erfolgreicher neuer Sicherung.
Eine wöchentliche Fassung vor dem Entfernen der Tagesfassung geschützt kopieren.
Eine externe Kopie und deren Wiederherstellungsprobe gehören zum Livebetrieb.
Der Dump enthält vertrauliche Kontodaten. Verzeichnisrechte und Backups schützen.

```sh
python db_archive.py backup /private/backup/picross.dump
export COMPOSE_PROJECT_NAME=picross-save-sync-restore
export SYNC_PORT=8001
docker compose up -d --wait db
python db_archive.py restore /private/backup/picross.dump
docker compose up -d --wait
docker compose exec -T api python -m sync.admin restore-code spielername
```

Die zweite DB bleibt bis zum Restore leer und die API aus. Der Befehl dekodiert
das Archiv zuerst vollständig. Einspielen, Generationswechsel, Kontosperren und
Entwertung alter Zugangsdaten werden gemeinsam veröffentlicht. Bei Fehlern ist
der Exitcode ungleich null. Der ursprüngliche Dienst bleibt unabhängig.
Pro identifiziertem Kontoinhaber einen neuen Code geschützt übergeben. Nach
Recovery mit neuem Passwort und Login zuerst alle Inventarseiten lesen. Alte
Warteschlangen anhand des Bestands und der Gerätewasserstände abgleichen.
Ein alter Generationsheader wird abgewiesen. Reguläre Neustarts behalten die
Generation bei.

## Prüfweg

Das optionale Modul `sync.server` baut das Image und führt die neun Szenarien
aus [Issue 821](https://github.com/venomenon328/picross/issues/821#sync-a) aus.
Zwei technische Clients verwenden echte HTTP-Verbindungen. Die beiden
Compose-Projekte verwenden eigene Namen, lokale Ports, Datenvolumes und
synthetische Konten. Das Modul entfernt sie nach dem Lauf. Der CI-Reader
verlangt alle Kriterien und die konkrete Commit-/Laufbindung.

## Gerätebeleg und Requestabbruch

Der authentisierte Client kann für sein eigenes Gerät den letzten
Requesthash, HTTP-Status und gespeicherten Receipt über GET /v1/device/checkpoint
abgleichen. POST /v1/device/abandon schließt eine freie Originalsequenz
ausdrücklich unter ihrem Originalhash ab. Beide Operationen verwenden die
Generation und denselben Kontolock wie normale Mutationen. Die vorhandenen
Gerätespalten werden durch Backup und Restore mitgeführt. Wireformen und
Sequenzentscheidungen stehen in [SAVE_SYNC](../../docs/game/SAVE_SYNC.md).
