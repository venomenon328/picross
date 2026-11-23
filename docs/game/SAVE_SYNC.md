# SYNC: optionale Konten und gemeinsame Spielstände

Dokument-ID: `save-sync`
Status: `approved-specification`
Zuständigkeit: Konto-/Gastgrenze, synchronisierter Spielstand, Protokoll,
Konflikte und Wiederherstellung. Freigabe und Paketstatus: [#821](https://github.com/venomenon328/picross/issues/821).

## 1. Geltung und Liefergrenze

Der [isolierte Konto-/Snapshotdienst](../../server/save_sync/README.md) implementiert den Serverumfang von SYNC-A. SYNC-B
bindet die Windows-/Webclients an; SYNC-C umfasst den separat beauftragten
Livebetrieb und die persönliche geräteübergreifende Abnahme. Paketkriterien,
Prüfplan, Ausführungswahl und tatsächlicher Lieferstatus stehen im Issue.

Das bestehende lokale Saveformat und seine vollständige Validierung bleiben in
[P1 §6](PROTOTYPE_P1.md#6-speicherung-und-wiederaufnahme), die Browserpersistenz
in [WEB_HOSTING](../operations/WEB_HOSTING.md) maßgeblich. Dieser Vertrag ergänzt
eine äußere Konten-/Übertragungsschicht. Er behauptet keine heutige Cloudfunktion.

## 2. Produktgarantien

### SYNC-G01: vollständiger Betrieb ohne Konto

Ohne Anmeldung bleibt die bisherige lokale Speicherung bestehen: Appidentität
`picross · P1`, Schema 1 und `user://p1/saves/`. Windows und unterschiedliche
Browserorigins/-profile bleiben getrennt. Kein Syncrequest, Registrierungszwang
oder neues Onlinegate für Rätsel, Speichern und Wiederaufnahme.

### SYNC-G02: getrennte Kontoprofile und Offlinebetrieb

Eine Anmeldung aktiviert ein gesondertes lokales Profil, gebunden an
Serveridentität und unveränderliche Konto-ID. Dazu gehören Saves, Fortsetzen-
Merker, Syncmetadaten, offene Konflikte und dauerhaft gespeicherte Uploads.
Konten oder Server dürfen diese Daten nicht teilen. Gerätebezogene Anzeige-/
Fensterpräferenzen bleiben lokal; sie werden nicht als Spielstand synchronisiert.

Der bisherige lokale Stand wird weder verschoben noch automatisch überschrieben.
Seine Übernahme ist eine ausdrückliche Auswahl einzelner/aller angebotenen
Rätsel und verwendet denselben konfliktgesicherten Uploadweg. Abmelden kehrt
zum bisherigen lokalen Profil zurück. Ausstehende Kontodaten bleiben für eine
spätere Anmeldung erhalten. Eine Löschung solcher Daten verlangt eine gesonderte
bewusste Entscheidung; Logout oder Tokenablauf genügt dafür nicht.

Ein bereits lokal verfügbares Kontoprofil bleibt offline spielbar. Lokale
Save-/Recoverygarantien, im Web einschließlich bestätigtem IDBFS-Callback,
gelten auch dort. Uploadwarteschlange und unveränderliche ausstehende Requests
überstehen einen regulären Neustart. Netzfehler blockieren keinen erfolgreich
lokal gesicherten Stand; lokale Sicherungsfehler bleiben echte Savefehler.
„Lokal gespeichert“, „Synchronisierung ausstehend“, „Synchronisiert“ und ein
behebbarer Fehler/Konflikt müssen unterscheidbar sein. Ein Servererfolg bestätigt
nur die zugehörige lokale Generation, niemals später entstandene Änderungen.

### SYNC-G03: vollständige Fassungen statt Zellmerge

Ein Snapshot überträgt die Rätselidentität, Rasterrevision, Dimensionen, aktuelle
Zellen und die Durchgangsmerkmale `undo_used` und `completed`. Undo/Redo wirkt
über den resultierenden Fortschritt. History, Cursor, aktive Farbe und sämtliche
Ansichtsdaten bleiben im vollständigen lokalen Save. Eine identische Projektion
braucht keinen weiteren Upload. Der B2-Sender bündelt ausstehende
Fortschritte zu den [beschlossenen Sammelanlässen](https://github.com/venomenon328/picross/issues/821#issuecomment-7095903230).
Verschiedene Rätsel haben unabhängige aktuelle Stände. Für dasselbe Rätsel bleiben
konkurrierende Fassungen erhalten, bis der Spieler ausdrücklich eine auswählt.

Die Auswahloberfläche zeigt den lokalen und den Serverstand mit verständlichen
Geräte-/Fortschrittsangaben. Inkompatible Rätselrevisionen werden als solche
erkennbar; der Client darf einen nicht vollständig validierbaren Stand nicht
anwenden. Vor einer Konfliktentscheidung wird der aktuelle Serverstand erneut
abgeglichen. Bei einem neuen Konflikt bleibt die bisherige Auswahl erhalten.

### SYNC-G04: Reset, Inhalte und Abschluss

Ein bewusster Rätselreset ist eine eigene versionierte Operation. Eine fehlende
lokale Datei, ein leeres neues Profil oder der automatische lokale Rasterreset
nach [PE §9.3](../tools/PUZZLE_EDITOR.md#93-sicherer-automatischer-save-neustart)
sind keine Löschanweisung an den Server. Alte Rasterfassungen werden nicht
stillschweigend in neue umgeschrieben. Vor lokalem Revisionsreset bleiben im
Kontoprofil noch nicht übertragene alte Fassungen als eigene Syncdaten erhalten.

`completed` bezeichnet weiter den Abschluss dieses konkreten gespeicherten
Durchgangs und dieser Rasterrevision. SYNC führt kein dauerhaftes „jemals gelöst“,
keine Sterne, neue Progression, Wertung oder Rangliste ein. Ein vorausgehendes
Export-/Importprojekt ist keine Voraussetzung dieses Vorhabens.

## 3. SYNC-A: Dienst und kleine Kontofunktion

### SYNC-S01: abgegrenzte Technik

Der Dienst liegt unter `server/save_sync/`: Python/FastAPI, psycopg und PostgreSQL,
versionierte SQL-Migrationen, eigener Container-/Compose-Betrieb und eigene
Abhängigkeiten. Kein ORM-/Jobplattformzwang. Umsetzung bindet konkrete unterstützte
Versionen und Containerdigests; keine ungebundenen `latest`-Images. Der Buildkontext
bleibt im Serverbereich, ohne versteckte Abhängigkeit auf Spiel-/Produktionsdaten.

Ein eigener Compose-Projektname, eigenes DB-Volume und eigener DB-Benutzer trennen
Picross von Mise en Dice und Gridwords. Die Datenbank erhält keinen Hostport;
der API-Port bindet am Host nur Loopback. Öffentliches HTTPS kommt vom separat
konfigurierten Reverse Proxy. CORS erlaubt ausschließlich konfigurierte Weborigins.
Erlaubte Requestheader umfassen `Authorization`, `Content-Type` und
`X-Picross-Generation`; für den Webclient lesbar sind `X-Picross-Generation`
und `Retry-After`. Die konfigurierte API-Basis ist die feste Serveridentität
des lokalen Profils; eine Restoregeneration eröffnet kein neues lokales Profil.
HTTP ist nur für isolierte Loopback-/CI-Prüfungen zulässig. Proxyheader gelten
nur von ausdrücklich konfigurierten vertrauenswürdigen Proxys.

Der angebotene Host wurde für SYNC nicht geprüft. Eine Beispielkonfiguration
ist Lieferung; Installation, Domain, Secrets und Änderungen an laufenden Diensten
sind ein späterer Betriebsauftrag. Kein automatisches Deployment durch Merge.

### SYNC-S02: Zugang

Benutzername und Passwort genügen. Registrierung verlangt zusätzlich einen
einmaligen Einladungscode, den der Betreiber über einen lokalen Verwaltungsbefehl
erstellt. Einladungen gelten sieben Tage und werden atomar verbraucht. Kein
öffentlicher Adminendpunkt, Maildienst, OAuth oder gemeinsames Botkonto.

- Benutzername: ASCII `[a-z0-9][a-z0-9_-]{2,31}` nach alleiniger Umwandlung
  von ASCII-Groß- in Kleinbuchstaben; eindeutig, kein Trim oder weiterer Alias.
- Passwort: 12–128 Unicode-Codepunkte, höchstens 1024 UTF-8-Bytes; keine stille
  Normalisierung oder Kürzung. Argon2id über `pwdlib[argon2]`, Bibliotheksparameter
  dokumentieren; keine selbst entwickelte Passworthashfunktion.
- Einladung, Recoverycode und Sitzungstoken: jeweils 32 kryptografisch zufällige
  Bytes als ungepaddetes base64url, also 43 Zeichen. Serverseitig nur geeignete
  Hashes speichern. Codes/Tokens, Passwörter und Snapshotinhalte gehören nicht
  in Logs, URLs oder Repositorydateien.
- Sitzung: opaque Bearer-Token, an Konto und Gerät gebunden, 30 Tage ab Ausstellung
  gültig. Login auf einem bekannten eigenen Gerät ersetzt dessen bisherige Sitzung,
  ohne Spielstände, Requestsequenz oder letzte Antwort zu löschen. Andere Geräte
  bleiben angemeldet. Logout widerruft die betreffende Sitzung.
- Gerätekennung: vom Server erzeugte UUIDv4, niemals vom Client frei anlegbar
  oder wiederzuverwenden. Login kann eine bekannte eigene Gerätekennung erneut
  binden. Eine fremde/ungültige Kennung erzeugt keine Ersatzidentität. Ohne lokale
  Kennung entsteht ein neues Gerät; alte Uploads werden erst nach Bestandsabgleich
  bewusst neu vorbereitet, nicht blind umnummeriert.
- Authendpunkte begrenzen Versuche: Standard höchstens 10 je normalisiertem
  Benutzernamen und 100 je Quell-IP innerhalb 15 Minuten. Grenzen zählen auch
  unbekannte Namen, liefern `429` mit `Retry-After` und gelten pro Dienstbestand,
  nicht unabhängig je Worker. Konfiguration darf diese Betriebsgrenzen ändern;
  ausgelieferte Werte und ihr Test sind zu dokumentieren.

Bei Registrierung wird ein Recoverycode einmal angezeigt. Recovery mit
Benutzername, Code und neuem Passwort verbraucht den Code, ändert das Passwort
und widerruft alle Sitzungen atomar. Ein neuer Code wird einmal zurückgegeben;
Spielstände und Gerätewasserstände bleiben erhalten. Eine angemeldete Person
kann mit erneuter Passwortbestätigung einen neuen Recoverycode erzeugen, wodurch
der alte ungültig wird. Das deckt auch eine verlorene Registrierungs-/Recovery-
Antwort ab: mit dem bekannten Passwort erneut anmelden und Code neu erzeugen.
Recoverycodes haben keine Zeitablauffrist, gelten aber nur einmal.

## 4. Protokoll und Daten

### SYNC-P01: gemeinsame Grenzen und Identität

Protokoll v1 verwendet UTF-8-JSON, `application/json` und `/v1`. Fehlende Pflicht-
felder, unbekannte Schlüssel/Enumwerte, doppelte Schlüssel, ungültiges UTF-8,
NaN/Infinity und unzulässiges `null` sind Fehler. Keine stillen Typkonvertierungen.
Ganzzahlig bedeutet eine endliche JSON-Zahl ohne Bruchteil im jeweils angegebenen
Bereich, niemals Boolean; Obergrenze ist `9007199254740991`. Zeiten sind serverseitige
UTC-Zeitpunkte als RFC3339-String mit `Z`, nur Anzeige-/Betriebsinformation.

Konto- und Geräte-IDs sind kanonische kleingeschriebene UUIDv4-Strings. Rätsel-IDs
sind 1–128 Zeichen aus `[A-Za-z0-9_-]`, ohne Pfadbedeutung; der Client bestätigt
zusätzlich die exakte registrierte Inhalts-ID. Identität ist `(account_id, puzzle_id)`.
Die Konto-ID stammt aus der Sitzung, nie aus einem frei wählbaren Uploadfeld.
Fremde Ressourcen sind nicht lesbar oder auflistbar; ihre Existenz wird nicht
durch unterschiedliche Ressourcenantworten offengelegt.

| Version | Bedeutung |
| --- | --- |
| `format = "picross-sync/v1"` | Äußerer Übertragungsvertrag. |
| `save.schema = 1` | Bestehender lokaler Savevertrag. |
| `definition_revision` | Rasterrevision; bei Snapshot gleich dem inneren Savefeld. |
| `server_revision` | Monotoner Zähler pro Konto/Rätsel; erste angenommene Fassung 1, nie angelegt 0. |
| `request_seq` | Monotoner Mutationszähler pro Konto/Gerät, erste Anfrage 1. |

Der aktuelle Stand ist Snapshot oder Resetmarker. Der Zähler und ein aktueller
Resetmarker werden durch Historienbereinigung niemals entfernt oder auf 0 gesetzt.
Serverrevision und Definitionsrevision sind nicht austauschbar. Entfernen eines
alten Payloads erzeugt keine neue fachliche Revision und hebt keine Sperre auf.

### SYNC-P02: Mutationsform und atomare Ergebnisse

`POST /v1/puzzles/{puzzle_id}/mutations` enthält genau die vier gemeinsamen Felder
`format`, `request_seq`, `base_server_revision`, `operation` plus die Felder der
jeweiligen Zeile. `request_seq >= 1`, `base_server_revision >= 0`; andere Zahlen
in dieser Tabelle sind ebenfalls sicher darstellbare ganze Zahlen.

| `operation` | Zusätzliche Pflichtfelder | Wirkung |
| --- | --- | --- |
| `snapshot` | `save`: `picross-progress/v1` nach P04 | Aktuellen Fortschritt anbieten. |
| `reset` | `definition_revision`: Zahl >= 1 | Bewussten Reset für diese Rasterrevision anbieten. |
| `resolve` | `candidate_id`: UUIDv4 | Genau diesen erhaltenen Konflikt zum aktuellen Stand machen. |
| `discard` | `candidate_id`: UUIDv4 | Genau diesen Konflikt ausdrücklich verwerfen; aktuellen Stand nicht ändern. |
| `restore` | `history_revision`: Zahl >= 1 | Genau diese noch gespeicherte frühere Fassung erneut zum aktuellen Stand machen. |

Bei `snapshot`/`reset` stimmen Basis und, falls ein aktueller Stand existiert,
Rasterrevision überein: neue aktuelle Fassung, `server_revision + 1`. Bei abweichender
Basis **oder** Rasterrevision bleibt der aktuelle Stand unverändert und der
vollständige angebotene Snapshot/Reset wird als Konfliktkandidat gesichert.
Das gilt auch für eine unerwartet höhere Basis; keine Annahme durch Clientzeit.

`resolve` und `restore` sind ausdrückliche Entscheidungen und dürfen auch eine
andere Rasterrevision auswählen; der Spielclient darf dennoch nur mit seiner
Definition vollständig validierbare Daten anwenden. Beide verlangen die aktuelle
Basis und erzeugen eine neue Serverrevision. Die vorige aktuelle Fassung wird
Historie. Bei `resolve` wird nur der gewählte Kandidat nach erfolgreicher Übernahme
entfernt; andere Kandidaten bleiben bestehen. `discard` verlangt ebenfalls die
aktuelle Basis, entfernt nur den benannten Kandidaten und erhöht keine Serverrevision.
Veraltete Auswahl, falsches Rätsel oder fehlender Kandidat ändern nichts.

DB-Transaktion und Sperren/bedingte Updates umfassen Kontingent, aktuellen Stand,
Historie/Konflikt, Gerätewasserstand und Antwortbeleg. Zwei konkurrierende neue
Schreiber auf derselben Basis können nicht beide neue aktuelle Fassung werden.
Ein `409` mit gespeichertem Kandidaten ist ein fachlicher Konflikt, kein
gescheiterter Transport: nur `candidate_id != null` bestätigt dessen Speicherung.
Kann der Server den Kandidaten nicht speichern, behält der Client seine Fassung
dauerhaft lokal und zeigt die fehlende Serversicherung.

### SYNC-P03: sichere Wiederholung

Je Gerät dauerhaft speichern: `last_request_seq`, SHA-256 des letzten verarbeiteten
Requests, HTTP-Status und exakten Antwortbody. Hashinput ist UTF-8 von Methode,
Newline, kanonischem API-Pfad, Newline und den unveränderten Requestbodybytes;
kein Tokenheader. Geräte-/Kontobindung kommt zusätzlich aus der DB-Zuordnung.

| Sequenz | Verhalten |
| --- | --- |
| `last + 1` | Einmal atomar verarbeiten und fachliche Antwort samt Wasserstand speichern. |
| `last`, identische Requestbytes | Gespeicherten Status/Body zurückgeben, keine erneute Mutation. |
| `last`, andere Bytes | `409 sequence_reused`, keine Änderung. |
| `< last` | `409 sequence_stale`, keine Änderung, auch nach Historienbereinigung. |
| `> last + 1` | `409 sequence_gap`, keine Änderung. |

Nach erfolgreicher Syntax-/Schema-/Authprüfung verbrauchen auch terminale
Fachantworten eine Sequenz: gespeicherter Konflikt, veraltete Auswahl, fehlende
historische Fassung oder ausgeschöpftes Kontingent. `400/401/413/415/422/429`,
Sequenzfehler und ein vor Commit zurückgerollter `5xx` verbrauchen keine Sequenz.
Eine verlorene Antwort ist keine Information über Commit/Verbrauch; der Client
wiederholt exakt die dauerhaft gespeicherten Bytes, bis das Ergebnis feststeht.
Anschließend wird erst die nächste Mutation vorbereitet. Keine parallelen
Mutationen desselben Geräts; verschiedene Geräte dürfen parallel schreiben.

Erneute Anmeldung/Tokenrotation verändert den Wasserstand nicht. Bei Verlust
lokaler Metadaten zuerst anmelden und Bestand abgleichen. Niemals alte Requests
unter neuer Sequenz/Identität automatisch als neue Entscheidung ausgeben.
Eine unbekannte Gerätekennung wird bei Mutationen nicht implizit angelegt.

### Gerätebeleg und ausdrücklicher Abbruch (B2)

GET /v1/device/checkpoint liest unter dem Kontolock ausschließlich das
Sitzungsgerät. Die Antwort picross-device-checkpoint/v1 bindet account_id,
device_id, last_request_seq, last_request_hash, response_status und response_body.
Die letzten drei Felder sind bei Sequenz null leer (JSON null). Sonst enthält
response_body den unverändert gespeicherten UTF-8-Text. Ein Wiederholungsbeleg
muss Methode, Pfad und Originalbytes über den P03-Hash bestätigen.

POST /v1/device/abandon erwartet picross-request-abandon/v1 mit request_seq,
expected_last_request_seq, request_hash und puzzle_id. Dieselbe bereits
verbrauchte Sequenz mit demselben Hash liefert den bestehenden Beleg. Für die
nächste freie Sequenz speichert der Dienst unter dem Originalhash einen
terminalen 409-Receipt mit rejected/request_abandoned und liefert den
Checkpoint mit HTTP 200. Rätselbestand, Historie und Konflikte bleiben dabei
erhalten. Die im Abbruchreceipt beobachtete Revision bestätigt keinen Upload.
Restore verlangt weiterhin einen vollständigen Bestandsabgleich.

### SYNC-P04: strukturelle Saveprüfung und Aussagegrenze

Das innere Objekt `save` hat genau acht Pflichtfelder. `format` ist
`picross-progress/v1`, `definition_id` entspricht dem URL-Rätsel und
`definition_revision` ist eine positive sichere Ganzzahl. `width` und `height`
liegen jeweils zwischen 1 und 50. `cells` enthält genau Breite × Höhe
sichere Ganzzahlen ab −1 und höchstens acht verschiedene positive Farb-IDs.
`undo_used` und `completed` sind boolesch. Zusätzliche Felder, null-Werte und
der frühere Vollsave ergeben `422 invalid_request` vor dem Sequenzverbrauch.

`progress_structure_checked` bestätigt diese Struktur. Palette und Lösung kennt
der Dienst nicht. Die B2-Übernahme validiert gegen die eigene Definition.
Gleicher Fortschritt erhält History und Ansicht. Ein übernommener anderer Stand
beginnt mit einer lokalen Ausgangsmatrix und leerer History am Cursor 0. Eigene
gültige Ansicht und Farbe bleiben erhalten. Der Empfang gehört zum B2-Paket.

### SYNC-P05: HTTP-Schnittstelle

Die Umsetzung liefert einen geschlossenen, versionierten OpenAPI-Vertrag mit
den folgenden Requests/Antworten; keine weiteren Produktfunktionen über freie
Zusatzfelder. Alle unten genannten Objektfelder sind Pflicht. Nur ausdrücklich
als nullable bezeichnete Felder erlauben `null`. Listen sind auch leer zulässig.

| Methode und Pfad | Request / Erfolg |
| --- | --- |
| `POST /v1/auth/register` | Exakt `username`, `password`, `invitation`, `device_name`; `201 Session`. |
| `POST /v1/auth/login` | Exakt `username`, `password`, `device_name`, `device_id` (UUID oder null für neues Gerät); `200 Session`. |
| `POST /v1/auth/logout` | Bearer, kein Body; `204`, Token widerrufen. |
| `POST /v1/auth/recover` | Exakt `username`, `recovery_code`, `new_password`; `200 Recovery`. Danach normal anmelden. |
| `POST /v1/auth/recovery-code` | Bearer, exakt `password`; `200 Recovery`, vorheriger Code ungültig. |
| `GET /v1/account` | Bearer; exakt `account_id`, `username`, `device_id`, `last_request_seq`. |
| `GET /v1/puzzles` | Bearer; `List` mit `Inventory`-Einträgen, nur eigenes Konto, einschließlich Rätseln mit Konflikten ohne aktuellen Stand. |
| `GET /v1/puzzles/{id}` | Bearer; `Record` oder `404`, falls nie angelegt. |
| `GET /v1/puzzles/{id}/history` | Bearer; `List` mit früheren `Summary`-Einträgen, absteigende Revision. |
| `GET /v1/puzzles/{id}/history/{revision}` | Bearer; `Record` oder `404`, falls nicht mehr vorhanden. |
| `GET /v1/puzzles/{id}/conflicts` | Bearer; `List` mit `CandidateSummary`, aufsteigende Erstellzeit/ID. |
| `GET /v1/puzzles/{id}/conflicts/{candidate_id}` | Bearer; `Candidate` oder `404`. |
| `POST /v1/puzzles/{id}/mutations` | Bearer, SYNC-P02; `200 Mutation`, bei Fachkonflikt `409 Mutation`. |
| `GET /health/live`, `GET /health/ready` | Ohne Auth, kein Body; exakt `{"status":"ok"}` mit `200`, Ready bei nicht nutzbarer DB/Migration `503` mit `{"status":"unavailable"}`. Keine Infrastrukturdetails. |

`device_name` ist ein nichtleerer String mit höchstens 64 Unicode-Codepunkten,
ohne Steuerzeichen; rein beschreibend. Authrequests höchstens 16 KiB.

| Form | Exakte Felder und Bedeutung |
| --- | --- |
| `Session` | `account_id`, `username`, `device_id`, `token`, `expires_at`, `last_request_seq` (>= 0), `recovery_code` (nur Register String, bei Login null). |
| `Recovery` | `recovery_code`: neuer String. |
| `Inventory` | `puzzle_id`, `server_revision` (>= 0; 0 ohne aktuellen Stand), `conflict_count` (>= 0, höchstens konfigurierte Konfliktquote). |
| `Summary` | `puzzle_id`, `server_revision` (>= 1), `definition_revision` (>= 1), `kind` (`snapshot`/`reset`), `updated_at`, `device_id`, `device_name` (beschreibender Name zum Schreibzeitpunkt). |
| `Record` | Alle `Summary`-Felder plus `save` (bei Snapshot Objekt, bei Reset null), `validation` (`progress_structure_checked` bei Snapshot, null bei Reset). |
| `CandidateSummary` | `candidate_id`, `puzzle_id`, `base_server_revision` (>= 0), `definition_revision`, `kind`, `created_at`, `device_id`, `device_name` (beschreibender Name zum Schreibzeitpunkt). |
| `Candidate` | Alle `CandidateSummary`-Felder plus `save` und `validation` wie bei `Record`. |
| `List` | `items`: Liste der pfadspezifischen Form; `next_cursor`: opaker String oder null. |
| `Mutation` | `format`, `request_seq`, `outcome` (`applied`/`conflict`/`discarded`/`rejected`), `server_revision` (>= 0), `candidate_id` (UUID oder null), `code` (unten), `sequence_consumed` (Boolean). |
| `Error` | `code`: unten definierter String. Keine Geheimnisse oder Frameworkdetails. |

Listen erlauben ausschließlich `limit` (1–100, Default 100) und `cursor` (opaker,
servervalidierter Fortsetzungsschlüssel, 1–1024 UTF-8-Bytes; bei erster Anfrage
weglassen). Unbekannte Queryparameter sind `422`.
Puzzlelisten sortieren nach ID; Fortsetzung ist Schlüssel-basiert und nicht
offsetbasiert. Gleichzeitige Änderungen garantieren keinen Gesamtsnapshot über
mehrere Seiten; ein Client wiederholt den Abgleich vor Upload. Historie/Konflikte
sind ohnehin durch SYNC-P06 begrenzt. Cursor binden Konto und Listenart; fremde
oder ungültige Cursor sind `422` und öffnen keine andere Liste.

`Mutation.code` ist `ok`, `conflict_saved`, `revision_conflict`, `candidate_missing`,
`history_missing`, `conflict_limit`, `storage_limit`, `sequence_reused`,
`sequence_stale` oder `sequence_gap`. Nur `ok` ergibt `200`; andere ergeben `409`.
`conflict_saved` hat `outcome=conflict` und eine gespeicherte Kandidaten-ID,
`ok` bei `discard` hat `outcome=discarded`, sonst `applied`; andere Codes haben
`outcome=rejected`. Bei `code=ok` für `resolve`/`discard` nennt der Erfolg den
betroffenen Kandidaten; bei anderen `ok`-Ergebnissen und bei `rejected` ist das
Feld null. `conflict_saved` behält seine gespeicherte Kandidaten-ID.
Sequenzfehler haben `sequence_consumed=false`,
andere terminale Mutationsantworten true. Alle HTTP-Responses sind `no-store`.

Außerhalb terminaler Mutationsantworten gilt `Error`: `400 malformed_json`,
`401 authentication_failed`, `404 not_found`, `409 registration_unavailable`,
`413 payload_too_large`, `415 unsupported_media_type`, `422 invalid_request`,
`429 rate_limited`, `503 unavailable`. Falscher Benutzer, Passwort oder Recoverycode
ergeben denselben Authfehler; fremde Ressourcenschlüssel ergeben `404`. Bei
Registrierung sind ungültige/verbrauchte Einladungen und belegte Namen einheitlich
`registration_unavailable`. Fehler oder Timeout sind kein Sicherungsnachweis.

### SYNC-P06: begrenzte Historie und Kontingente

Default: aktueller Stand plus zehn frühere angenommene Fassungen je Rätsel;
maximal fünf offene Konfliktkandidaten je Rätsel. Überzählige älteste **angenommene**
Historienfassungen dürfen beim erfolgreichen Schreiben entfernt werden, offene
Konflikte nie automatisch. Bei voller Konfliktablage folgt `conflict_limit`
ohne neuen Kandidaten. Eine Auswahl, bewusste Verwerfung oder Historienrestauration
läuft ausschließlich über SYNC-P02 und die aktuelle Basis.

Ein Mutationsrequest ist höchstens 16 MiB UTF-8; dessen Grenze wird vor teurem
JSON-Aufbau geprüft. Authbodygrenze steht in SYNC-P05. Der gesamte gespeicherte
Snapshotbestand aus aktuell/Historie/Konflikten hat standardmäßig höchstens
512 MiB je Konto, maximal 2000 Rätsel und 100 registrierte Geräte. Berechnung auf
der tatsächlich gespeicherten UTF-8-Snapshotdarstellung, nach der regulären
Historienrotation der beabsichtigten Transaktion. Keine Komprimierung als Umgehung
der Eingangsgrenze. Metadaten haben die geschlossenen Formen dieses Vertrags.
Der Betreiber kann Quoten dokumentiert erhöhen; keine automatische Entfernung
aktueller Stände, Konflikte oder Gerätewasserstände zur Platzgewinnung.
Eine volle Gerätequote verhindert nur die Neuanlage eines Geräts und meldet
`409 registration_unavailable`. Login auf einem bekannten eigenen Gerät bleibt
möglich. Es gibt keine automatische Geräteentfernung, die Wasserstände verliert.

Bei Überschreitung `storage_limit`, ohne fachliche Änderung außer dem terminalen
Requestbeleg. Lokaler Fortschritt bleibt gültig; eine Transportgrenze macht aus
einem lokalen Save keinen defekten Save. Grenzsenkung entfernt keine Bestandsdaten.
Ein ausdrücklich gewähltes `discard` bleibt auch oberhalb einer nachträglich
gesenkten Quote zulässig: es entfernt nur den gewählten Kandidaten und fügt
keinen Payload hinzu. Für neue Stände/Kandidaten gelten die aktuellen Grenzen.
Tombstones und monotone Zähler bleiben erhalten. Sichern/Wiederherstellen umfasst
auch diese Metadaten; bloßes Kopieren aktueller Snapshotdateien genügt nicht.

## 5. Sicherung und Wiederherstellung

SYNC-A liefert ausführbare Betreiberbefehle für konsistenten PostgreSQL-Dump und
Restore in eine **leere, isolierte** Zieldatenbank einschließlich Schema/Migration,
Konten, Einladungen/Recovery, Sitzungen, Geräten/Wasserständen/Antwortbelegen,
aktuellen Ständen, Historie und Konflikten. Erfolgreicher Exit allein genügt nicht:
Restoreprüfung liest Werte, prüft die unten definierte Zugangsentwertung und
lässt nach kontrollierter Wiederanmeldung einen alten Request erneut abweisen
sowie einen neuen korrekt fortsetzen. Kein Restore in eine produktive DB im Testweg.

Backups liegen getrennt vom DB-Volume, mit eingeschränktem Dateizugriff. Der
Lieferumfang beschreibt tägliche Sicherung und Rotation mit sieben täglichen
und vier wöchentlichen Fassungen; vorhandene gültige Sicherungen werden erst
nach neuer erfolgreicher Sicherung rotiert. Automatische Einrichtung auf dem
realen Host bleibt SYNC-C. Dort müssen externe Kopie, Zugang und tatsächliche
Wiederherstellbarkeit nachgewiesen werden. Ein Dump auf derselben Maschine
ist kein Schutz gegen den vollständigen Verlust dieser Maschine.

Nach Rücksicherung einer älteren DB können zuvor bestätigte neue Stände und
Sequenzen fehlen; auch alte Passwörter und bereits verbrauchte Codes kämen zurück.
Der Restoreweg sperrt deshalb zunächst alle restaurierten Konten für normalen
Login und entwertet sämtliche Sitzungen, Einladungen und Recoverycodes. Ein lokaler
Betreiberbefehl stellt pro geprüftem Konto einen neuen einmaligen, an die neue
Generation gebundenen Recoverycode bereit. Nur Recovery mit diesem Code, neuem
Passwort und normaler Codeerneuerung
hebt dessen Sperre auf. Gesicherte Spielstände und Gerätewasserstände bleiben
erhalten. Ausgabe/geschützte Übergabe eines solchen Codes ist eine ausdrückliche
Betreiberhandlung; keine öffentliche Selbstfreischaltung mit alten Zugangsdaten.
Gesperrter Login ergibt den allgemeinen `401 authentication_failed`. Der Restore
ist erst nach atomarem Abschluss von neuer Generation, Kontosperren und
Zugangsentwertung für Anfragen bereit; ein Teilabbruch bleibt gesperrt.

Zusätzlich erzeugt der Restore eine neue serverseitige Instanzgeneration als
UUIDv4. Nach kontrollierter Wiederanmeldung ist vor weiteren Uploads ein
Bestandsabgleich erforderlich. Die Generation wird als zusätzlicher
Pflichtheader `X-Picross-Generation` auf allen `/v1`-Antworten ausgegeben und
bei authentifizierten Requests verlangt. Falsche Generation ergibt
`409 Error` mit `code=server_generation_changed`, ohne Mutation oder
Sequenzverbrauch; fehlender/ungültiger Header ergibt `422 invalid_request`.
Nur wenn die Generation wegen fehlender DB-Bereitschaft noch nicht ermittelt
werden kann, darf sie in einer `503 unavailable`-Antwort fehlen. Login/Register/
Recovery und Health verlangen den Header nicht. Kein automatisches Replay alter
Warteschlangen gegen einen zurückgesetzten Serverbestand. Gerätewasserstände aus
dem Dump werden trotzdem nicht genullt. Generation wechselt nur bei Restore,
nicht bei normalem Dienst-/DB-Neustart.

## Lokaler Profilkern und B2-Client

[AccountProfile](../../game/model/account_profile.gd) ist der native Einstieg für
explizite Kontokontexte. Der Aufrufer liefert die konfigurierte HTTPS-API-Basis
und die vom Dienst erhaltenen Konto-, Geräte- und Generationskennungen.
`open(..., initialize=true)` ist ausschließlich für ein neu zugeordnetes Gerät
mit bestätigtem Wasserstand 0 vorgesehen. Die Neuanlage beansprucht ein noch
fehlendes Kontoverzeichnis. Das normale Öffnen prüft die vorhandenen Metadaten.
Der Root ist `user://p1/accounts/<SHA-256 der API-Basis>/<Konto-UUID>/`.
Die Profilinstanz kapselt SaveStore (`saves/`) und RecentPuzzle
(`recent-puzzle.json`). Aufrufer bearbeiten Kontodaten nur über diese Instanz.
Gerätepräferenzen und der Startpfad der Anwendung bleiben gerätelokal.

`journal.json` enthält Format `picross-local-sync/v3`, den vollständigen
JSON-Payload als UTF-8-Text und dessen SHA-256. Er bindet Kontext, erwartete
Servergeneration, lokale Generation, verbrauchte Sequenz, ausstehende
Fassungen/Entscheidungen, höchsten bekannten Stand pro Rätsel, einen vorbereiteten
Request, den letzten Antwortbeleg, Schreibabsicht, gesicherte alte Rasterbytes und
Abgleichsgrund. Mutationen halten während der kurzen lokalen Transaktion ein
exklusiv angelegtes Lockverzeichnis und prüfen den zuvor gelesenen Journalhash.
Ein zweiter, inzwischen veralteter Kontext muss erneut öffnen. Journalpublikation
schreibt einen Geschwistertemp, flusht, schließt, vergleicht alle Bytes und
ersetzt per Rename (unter Windows MoveFileEx mit Write-through). Erst ein
erfolgreicher Vergleich des Ziels schließt die Publikation ab.

Vor Slotänderung sichert das Journal die vollständige Schreib-/Resetabsicht
einschließlich des SHA-256 der erwarteten Primarybytes bei einem Save. Je Rätsel
bindet es die letzte lokale Generation und einen Hash der Fortschrittsprojektion.
Bei unverändertem Hash wird der lokale Save bestätigt, während Warteschlange und
vorbereiteter Request ihre Identität behalten. Nur die acht P04-Felder gelangen
in sendefähige Snapshots. Ein Journal im Vorgängerformat `picross-local-sync/v1`
bleibt einschließlich Originalrequest unverändert für den Bestandsabgleich gesperrt.
Nach dem P1-Temp-/Backupweg liest der Kern das Primary bzw. die Abwesenheit
aller Resetziele zurück. Erst dann veröffentlicht er die zugeordnete Generation.
Beim Wiederanlauf kann ein passendes Primary eine noch offene Absicht abschließen.
Eine widersprüchliche Teilrotation, fremde Metadaten oder ein nach hartem
Prozessabbruch stehengebliebener Lock sperren Änderungen bis zur Wiederherstellung.
Die Übergabe `reconciliation()` benennt den eigenen Root, das Journal und die
erhaltene Bindung. Der Kern stiehlt keine Locks. Ein Backup verlangt weiterhin
ausdrückliche Reparatur. PE liest beim Rasterwechsel ausschließlich den
Profilmerker. Vor der Bereinigung werden ältere Slotbytes mit ihrem Hash ins
Journal übernommen. Vorbereitete Requests und Konfliktfassungen bleiben erhalten.

`save`, `reset` und `decision` geben eine lokale Generation bzw. 0 bei einem
Fehler zurück. `locally_confirmed` unterscheidet den abgeschlossenen nativen
Dateivorgang von einem noch ausstehenden Adaptercallback. Jede Rückmeldung ist
einmalig an ihren ursprünglichen Kontext und ihre Generation gebunden. Beim
nativen Wiederöffnen belegt das zurückgelesene Journal die dauerhaften Einträge.
Der jüngere Stand desselben Slots kann einen wartenden, bereits lokal bestätigten
Snapshot derselben Rasterrevision ablösen. Ausstehende Requests, explizite
Entscheidungen, alte Rasterrevisionen und abgewiesene Fassungen bleiben erhalten.

`prepare` benötigt die lokale Generation und eine ausdrücklich übergebene
Basisrevision. `resume_request` gibt den gespeicherten Auftrag zurück. Der
Sender verwendet Methode, Pfad, Generationsheader und `body.to_utf8_buffer()`
ohne erneute Serialisierung. Zugangsdaten kommen außerhalb dieses Bestands hinzu.
`receive` verlangt den Originalauftrag, die beobachtete Servergeneration,
HTTP-Status und den strikt dekodierten v1-Antwortbody. Ein Transportfehler lässt
den Auftrag offen. Ein verbrauchtes Ergebnis veröffentlicht Beleg, Wasserstand,
Slotstatus und Freigabe gemeinsam. Gesicherte Kandidaten behalten ihre ID,
abgelehnte Fassungen den angebotenen Fortschritt. Unverbrauchte
Sequenzfehler und eine andere Servergeneration sperren automatische Wiederholung.
Der spätere Bestandsabgleich entscheidet ausdrücklich über die weitere Verwendung.

Der reguläre Buchclient verwendet die Kontoauswahl in den Einstellungen. Die
feste API-Basis ist Teil der Profilidentität. Zugangsdaten der Sitzung liegen
getrennt von den Rätseldateien in session.json des Kontos. Die Auswahl im
Serververzeichnis bleibt über einen Neustart erhalten.

Jede ausstehende Fassung bindet ihre lokale Generation, base_server_revision
und parent_local. Letzteres bezeichnet die zugehörige vorbereitete lokale
Vorgängerfassung. Ein eigener angewendeter Snapshot kann diese Bearbeitungslinie
auf seine bestätigte Revision fortführen. Ein späterer GET ändert die
Bearbeitungsbasis einer bereits ausstehenden Fassung nicht. Die lokale
Schreibabsicht eines Empfangs führt received_revision. Ihre Veröffentlichung
aktualisiert Basis und lokalen Stand ohne einen Rückupload. Ein Abbruchauftrag
liegt mit unveränderten Bodybytes unter abandon neben dem Originalrequest.
Auf Web warten Slot-/Dirtyzustand, vorbereiteter Request oder Abbruch und
anschließender Receipt jeweils auf eine eigene IDBFS-Transaktion.

Der Sender bündelt beim Verlassen eines Rätsels und bei neuem Abschluss zwei
Sekunden. Bei durchgehender Bearbeitung prüft er nach 600 Sekunden, ob sich
der Fortschritt geändert hat. Fehlversuche verwenden 30, 60, 120, 240 und
anschließend 300 Sekunden Wartezeit. Ein längeres Retry-After gilt weiter.
Der Transporttimeout beträgt 30 Sekunden.

Die Migration von Datenbankstand 1 auf 2 projiziert aktuelle und frühere
Versionen sowie Konfliktkandidaten in einer Transaktion. Resetmarker, Identitäten,
Revisionen, Zeiten, Gerätewasserstände, Requesthashes und Antwortbelege bleiben
erhalten. Readiness und Sicherung/Restore setzen Datenbankstand 2 voraus.

## 6. Prüfung und Zuständigkeit

Die konkrete Auswahl, Kernbaupflicht und Aufbewahrung stehen ausschließlich in
[CI v2](../ci/CI_WORKFLOW_V2.md#sync-a-servermodul), die paketbezogenen
Kriterien SYNC-A-01–10 und ausgelassene Abdeckung in [#821 / SYNC-A](https://github.com/venomenon328/picross/issues/821#sync-a).
SYNC-A benötigt echte HTTP-/PostgreSQL-/Compose-Prüfungen mit synthetischen Konten;
ein erfolgreicher Diensttest ist keine Windows-/Web-Spielabnahme.

Fachliche Implementierungsquellen: [FastAPI zu pwdlib/Argon2](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/),
[psycopg-Transaktionen](https://www.psycopg.org/psycopg3/docs/basic/transactions.html),
[PostgreSQL pg_dump](https://www.postgresql.org/docs/17/app-pgdump.html) und
[pg_restore](https://www.postgresql.org/docs/17/app-pgrestore.html).
Die gewählte Bibliothek ersetzt nicht den hier festgelegten Zugriffs-, Konkurrenz-
und Wiederholungsvertrag. Versionsbindung und tatsächlich ausgeführte Tests
stehen im Serverbereich und im zugehörigen Implementierungs-PR.
