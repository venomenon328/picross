CREATE TABLE instance (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    version integer NOT NULL,
    generation uuid NOT NULL DEFAULT gen_random_uuid(),
    cursor_key bytea NOT NULL DEFAULT uuid_send(gen_random_uuid()) || uuid_send(gen_random_uuid())
);
INSERT INTO instance(version) VALUES (1);
CREATE TABLE invitations (digest bytea PRIMARY KEY, expires_at timestamptz NOT NULL);
CREATE TABLE accounts (
    account_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    username text UNIQUE NOT NULL,
    password_hash text NOT NULL,
    recovery bytea UNIQUE,
    restored boolean NOT NULL DEFAULT false,
    locked boolean NOT NULL DEFAULT false
);
CREATE TABLE devices (
    device_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id uuid NOT NULL REFERENCES accounts,
    device_name text NOT NULL,
    token bytea UNIQUE,
    expires_at timestamptz NOT NULL,
    needs_inventory boolean NOT NULL DEFAULT false,
    last_request_seq bigint NOT NULL DEFAULT 0,
    request_hash bytea, response_status integer, response_body text
);
CREATE INDEX ON devices(account_id);
CREATE TABLE attempts (username text NOT NULL, ip text NOT NULL, at timestamptz NOT NULL DEFAULT clock_timestamp());
CREATE INDEX ON attempts(at);
CREATE INDEX ON attempts(username);
CREATE INDEX ON attempts(ip);
CREATE TABLE puzzles (
    account_id uuid NOT NULL REFERENCES accounts, puzzle_id text COLLATE "C" NOT NULL,
    server_revision bigint NOT NULL DEFAULT 0,
    PRIMARY KEY (account_id, puzzle_id)
);
CREATE TABLE versions (
    account_id uuid NOT NULL, puzzle_id text COLLATE "C" NOT NULL, server_revision bigint NOT NULL,
    definition_revision bigint NOT NULL, device_id uuid NOT NULL, device_name text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp(), save text,
    PRIMARY KEY(account_id, puzzle_id, server_revision),
    FOREIGN KEY(account_id, puzzle_id) REFERENCES puzzles ON DELETE CASCADE
);
CREATE TABLE candidates (
    account_id uuid NOT NULL, puzzle_id text COLLATE "C" NOT NULL,
    candidate_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    base_server_revision bigint NOT NULL, definition_revision bigint NOT NULL,
    device_id uuid NOT NULL, device_name text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), save text,
    FOREIGN KEY(account_id, puzzle_id) REFERENCES puzzles ON DELETE CASCADE
);
CREATE INDEX ON candidates(account_id, puzzle_id, created_at, candidate_id);
