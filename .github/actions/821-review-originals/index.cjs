const crypto = require('node:crypto');
const fs = require('node:fs/promises');
const path = require('node:path');
const { setTimeout: sleep } = require('node:timers/promises');

const env = process.env;
const digest = env.ORIGINAL_DIGEST;
const size = Number(env.ORIGINAL_SIZE);
const phase = env.TRANSFER_PHASE;
const name = 'SYNC-PERF-' + env.PRODUCT_HEAD;
const statePath = path.join(env.RUNNER_TEMP, '821-upload-state.json');

function check(condition, message) {
  if (!condition) throw new Error(message);
}

function blobUrl(value) {
  const url = new URL(value);
  check(url.protocol === 'https:' && url.hostname.endsWith('.blob.core.windows.net') &&
    !!url.searchParams.get('sig'), 'Unexpected artifact storage endpoint');
  return url;
}

async function rpc(method, fields) {
  const url = new URL('/twirp/github.actions.results.api.v1.ArtifactService/' + method, env.ACTIONS_RESULTS_URL);
  const response = await fetch(url, {
    method: 'POST',
    redirect: 'error',
    headers: { authorization: 'Bearer ' + env.ACTIONS_RUNTIME_TOKEN, 'content-type': 'application/json' },
    body: JSON.stringify(fields),
    signal: AbortSignal.timeout(20000)
  });
  check(response.ok, method + ' returned HTTP ' + response.status);
  return response.json();
}

async function prepare(binding) {
  const expiration = new Date(Date.now() + 6 * 86400000).toISOString();
  const result = await rpc('CreateArtifact', { ...binding, version: 4, expires_at: expiration });
  check(result.ok, 'Artifact allocation failed');
  const lease = blobUrl(result.signed_upload_url);
  const publicKey = crypto.createPublicKey({
    key: Buffer.from(env.UPLOAD_PUBLIC_KEY, 'base64'), format: 'der', type: 'spki'
  });
  check(publicKey.asymmetricKeyType === 'rsa' && publicKey.asymmetricKeyDetails.modulusLength >= 2048,
    'Invalid ephemeral transfer key');
  const key = crypto.randomBytes(32);
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  const bytes = Buffer.concat([cipher.update(lease.href, 'utf8'), cipher.final()]);
  const sealed = {
    key: crypto.publicEncrypt({ key: publicKey, oaepHash: 'sha256' }, key).toString('base64'),
    iv: iv.toString('base64'),
    tag: cipher.getAuthTag().toString('base64'),
    ciphertext: bytes.toString('base64'),
    run: env.GITHUB_RUN_ID,
    product: env.PRODUCT_HEAD,
    digest,
    size
  };
  await fs.writeFile(statePath, JSON.stringify(binding), { mode: 0o600 });
  await fs.writeFile(path.join(env.RUNNER_TEMP, '821-upload-ticket.json'), JSON.stringify(sealed));
  console.log('Allocated expiring Actions artifact for ' + name);
}

async function waitForUpload() {
  const statusUrl = env.GITHUB_API_URL + '/repos/' + env.GITHUB_REPOSITORY + '/commits/' +
    env.GITHUB_SHA + '/statuses?per_page=100';
  const context = 'sync-perf/upload-' + env.GITHUB_RUN_ID;
  const deadline = Date.now() + 7 * 60 * 1000;
  while (Date.now() < deadline) {
    const reply = await fetch(statusUrl, {
      headers: { authorization: 'Bearer ' + env.STATUS_READ_TOKEN, accept: 'application/vnd.github+json' },
      redirect: 'error',
      signal: AbortSignal.timeout(12000)
    });
    check(reply.ok, 'Upload acknowledgment lookup returned HTTP ' + reply.status);
    const status = (await reply.json()).find(row => row.context === context);
    if (status) {
      check(status.state === 'success' && status.description === digest, 'Wrong upload acknowledgment');
      return;
    }
    await sleep(6000);
  }
  throw new Error('Timed out waiting for the measured upload');
}

async function finish(binding) {
  const prepared = JSON.parse(await fs.readFile(statePath, 'utf8'));
  check(JSON.stringify(prepared) === JSON.stringify(binding), 'Runner job binding changed');
  await waitForUpload();
  const final = await rpc('FinalizeArtifact', { ...binding, size: String(size), hash: 'sha256:' + digest });
  check(final.ok && final.artifact_id, 'Artifact finalization failed');
  try {
    const result = await rpc('GetSignedArtifactURL', binding);
    const reply = await fetch(blobUrl(result.signed_url), { redirect: 'error', signal: AbortSignal.timeout(30000) });
    check(reply.ok, 'Artifact readback returned HTTP ' + reply.status);
    const bytes = Buffer.from(await reply.arrayBuffer());
    check(bytes.length === size && crypto.createHash('sha256').update(bytes).digest('hex') === digest,
      'Final artifact bytes do not match');
  } catch (error) {
    await rpc('DeleteArtifact', binding);
    throw error;
  }
  console.log('Verified artifact ' + final.artifact_id + ' with ' + size + ' bytes and SHA-256 ' + digest);
}

async function main() {
  check(/^[a-f0-9]{40}$/.test(env.PRODUCT_HEAD) && /^[a-f0-9]{64}$/.test(digest) &&
    Number.isSafeInteger(size) && size > 0 && size <= 20 * 1024 * 1024 &&
    ['prepare', 'finish'].includes(phase), 'Invalid transfer inputs');
  const payload = JSON.parse(Buffer.from(env.ACTIONS_RUNTIME_TOKEN.split('.')[1], 'base64url'));
  const scope = payload.scp.split(' ').find(part => part.startsWith('Actions.Results:'));
  check(scope, 'Actions artifact scope unavailable');
  const [, run, job] = scope.split(':');
  check(run && job, 'Missing artifact execution IDs');
  const binding = { workflow_run_backend_id: run, workflow_job_run_backend_id: job, name };
  await (phase === 'prepare' ? prepare(binding) : finish(binding));
}

main().catch(error => {
  const message = String(error.message);
  console.error(/[?]|https?:|sig=/.test(message) ? 'Artifact transfer failed' : message);
  process.exitCode = 1;
});
