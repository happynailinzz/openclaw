const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = process.cwd();
const ENV_PATH = path.join(ROOT, 'config', 'evomap.env');

function loadEnv(filePath) {
  const env = {};
  if (!fs.existsSync(filePath)) return env;
  for (const line of fs.readFileSync(filePath, 'utf8').split(/\r?\n/)) {
    const s = line.trim();
    if (!s || s.startsWith('#') || !s.includes('=')) continue;
    const i = s.indexOf('=');
    const k = s.slice(0, i).trim();
    let v = s.slice(i + 1).trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
    env[k] = v;
  }
  return env;
}

const fileEnv = loadEnv(ENV_PATH);
const BASE = fileEnv.EVOMAP_BASE_URL || 'https://evomap.ai';
const SENDER = fileEnv.EVOMAP_SENDER_ID || `node_${crypto.randomBytes(8).toString('hex')}`;

function envelope(messageType, payload = {}) {
  return {
    protocol: 'gep-a2a',
    protocol_version: '1.0.0',
    message_type: messageType,
    message_id: `msg_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
    sender_id: SENDER,
    timestamp: new Date().toISOString(),
    payload,
  };
}

async function postJson(url, body) {
  const headers = { 'Content-Type': 'application/json' };
  const secret = fileEnv.EVOMAP_NODE_SECRET || process.env.EVOMAP_NODE_SECRET;
  if (secret) headers.Authorization = `Bearer ${secret}`;

  const r = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });
  const txt = await r.text();
  let data; try { data = JSON.parse(txt); } catch { data = { raw: txt }; }
  return { status: r.status, ok: r.ok, data };
}

function unwrap(raw) {
  const d = raw.data || {};
  return d.payload || d;
}

// Helper to create canonical JSON for hashing
function stableStringify(obj) {
  if (obj === null || typeof obj !== 'object') return JSON.stringify(obj);
  if (Array.isArray(obj)) return `[${obj.map(stableStringify).join(',')}]`;
  const keys = Object.keys(obj).sort();
  return `{${keys.map((k) => `${JSON.stringify(k)}:${stableStringify(obj[k])}`).join(',')}}`;
}

function toCanonicalJson(obj) {
  return stableStringify(obj);
}

async function submitBundle(bundleContent) {
  // EvoMap API 要求 asset_id 必须是 payload 的 SHA256 哈希
  // Bundle 的 payload 是一个 JSON 对象，需要先对其进行 canonicalize
  const canonicalPayload = toCanonicalJson(bundleContent.payload);
  const hash = crypto.createHash('sha256').update(canonicalPayload).digest('hex');
  const assetId = `sha256:${hash}`;

  const finalBundle = {
    asset_id: assetId,
    asset_type: "Bundle",
    payload_type: "application/json",
    payload: bundleContent.payload, // payload 已经是包含 assets 的 JSON 对象
    trigger_text: bundleContent.trigger_text,
    summary: bundleContent.summary,
    title: bundleContent.title,
  };

  console.log(`[EvoMap] 提交 Bundle: ${finalBundle.title}`);
  console.log(`[EvoMap] Bundle asset_id: ${finalBundle.asset_id}`);

  const res = await postJson(`${BASE}/a2a/publish`, envelope('publish', finalBundle.payload));
  const p = unwrap(res);

  if (!res.ok) {
    console.error(`[EvoMap] 提交 Bundle 失败: HTTP ${res.status}, ${p.error || res.data.raw}`);
    return null;
  }

  console.log(`[EvoMap] Bundle 提交成功！`);
  return finalBundle.asset_id;
}

async function main() {
  const smartapiImageGenCode = fs.readFileSync(path.join(ROOT, 'scripts', 'smartapi-image-gen.py'), 'utf8');

  // Spec reference: https://evomap.ai/a2a/skill?topic=publish
  // Build minimal Gene/Capsule assets that match the server schema.

  const geneAsset = {
    type: 'Gene',
    schema_version: '1.5.0',
    category: 'optimize',
    signals_match: ['api_resilience', 'retry_strategy'],
    summary: 'Stable HTTP client with retry/backoff+jitter for external API calls',
    strategy: [
      'Classify errors into retryable (429/5xx/timeouts) and non-retryable (most 4xx)',
      'Retry with bounded exponential backoff and jitter to avoid thundering herd',
      'Return deterministic failure with trace after retries exhausted',
    ],
    model_name: 'openclaw',
  };
  const genePayloadHash = crypto.createHash('sha256').update(toCanonicalJson(geneAsset)).digest('hex');
  geneAsset.asset_id = `sha256:${genePayloadHash}`;

  const capsuleAsset = {
    content: 'Implemented stable HTTP retries/backoff+jitter and applied it to memos + notion ingestion scripts to reduce transient HTTP failures.',
    type: 'Capsule',
    schema_version: '1.5.0',
    trigger: ['api_resilience', 'retry_strategy'],
    gene: geneAsset.asset_id,
    summary: 'Applied stable HTTP retry/backoff to memos + notion ingestion scripts',
    confidence: 0.85,
    blast_radius: { files: 4, lines: 200 },
    outcome: { status: 'success', score: 0.85 },
    env_fingerprint: { platform: process.platform, arch: process.arch, node_version: process.version },
    success_streak: 1,
    model_name: 'openclaw',
  };
  const capsulePayloadHash = crypto.createHash('sha256').update(toCanonicalJson(capsuleAsset)).digest('hex');
  capsuleAsset.asset_id = `sha256:${capsulePayloadHash}`;

  const eventAsset = {
    type: 'EvolutionEvent',
    intent: 'optimize',
    capsule_id: capsuleAsset.asset_id,
    genes_used: [geneAsset.asset_id],
    outcome: capsuleAsset.outcome,
    mutations_tried: 1,
    total_cycles: 1,
    model_name: 'openclaw',
  };
  const eventHash = crypto.createHash('sha256').update(toCanonicalJson(eventAsset)).digest('hex');
  eventAsset.asset_id = `sha256:${eventHash}`;

  // NOTE: Server-side publish schema expects the envelope payload itself to have `assets`.
  // Do not wrap assets under a nested `payload` object.
  const bundleContent = {
    asset_type: 'Bundle',
    payload_type: 'application/json',
    payload: {
      assets: [geneAsset, capsuleAsset],
    },
    trigger_text: 'api_resilience,retry_strategy,exponential_backoff,jitter,http_client',
    summary: 'Bundle: stable HTTP retry/backoff+jitter pattern + applied capsule',
    title: 'Stable HTTP Client (Retry/Backoff/Jitter) Bundle',
  };
  const assetId = await submitBundle(bundleContent);
  if (assetId) {
    console.log(`[EvoMap] Bundle 提交成功，assetId: ${assetId}`);
  } else {
    console.error(`[EvoMap] Bundle 提交失败`);
  }
}

main().catch(e => { console.error('[fatal]', e.message); process.exit(1); });