#!/usr/bin/env node
/**
 * Minimal EvoMap client (Node 18+)
 * Usage:
 *   node scripts/evomap-client.js hello
 *   node scripts/evomap-client.js heartbeat
 *   node scripts/evomap-client.js fetch
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ENV_PATH = path.resolve(process.cwd(), 'config', 'evomap.env');

function loadEnv(filePath) {
  const env = {};
  if (!fs.existsSync(filePath)) return env;
  const lines = fs.readFileSync(filePath, 'utf8').split(/\r?\n/);
  for (const line of lines) {
    const s = line.trim();
    if (!s || s.startsWith('#') || !s.includes('=')) continue;
    const i = s.indexOf('=');
    const k = s.slice(0, i).trim();
    let v = s.slice(i + 1).trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
      v = v.slice(1, -1);
    }
    env[k] = v;
  }
  return env;
}

const fileEnv = loadEnv(ENV_PATH);
const EVOMAP_BASE_URL = fileEnv.EVOMAP_BASE_URL || process.env.EVOMAP_BASE_URL || 'https://evomap.ai';
const EVOMAP_SENDER_ID = fileEnv.EVOMAP_SENDER_ID || process.env.EVOMAP_SENDER_ID || `node_${crypto.randomBytes(8).toString('hex')}`;
const EVOMAP_REFERRER = fileEnv.EVOMAP_REFERRER || process.env.EVOMAP_REFERRER || undefined;
const EVOMAP_WEBHOOK_URL = fileEnv.EVOMAP_WEBHOOK_URL || process.env.EVOMAP_WEBHOOK_URL || undefined;

function envelope(messageType, payload = {}) {
  return {
    protocol: 'gep-a2a',
    protocol_version: '1.0.0',
    message_type: messageType,
    message_id: `msg_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
    sender_id: EVOMAP_SENDER_ID,
    timestamp: new Date().toISOString(),
    payload,
  };
}

async function postJson(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { raw: text }; }
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${JSON.stringify(data)}`);
  }
  return data;
}

function unwrapPayload(data) {
  return data && typeof data === 'object' && data.payload && typeof data.payload === 'object' ? data.payload : data;
}

async function hello() {
  const payload = {
    capabilities: {},
    gene_count: 0,
    capsule_count: 0,
    env_fingerprint: { platform: process.platform, arch: process.arch, node_version: process.version },
    ...(EVOMAP_REFERRER ? { referrer: EVOMAP_REFERRER } : {}),
    ...(EVOMAP_WEBHOOK_URL ? { webhook_url: EVOMAP_WEBHOOK_URL } : {}),
  };
  const raw = await postJson(`${EVOMAP_BASE_URL}/a2a/hello`, envelope('hello', payload));
  const data = unwrapPayload(raw);
  console.log(JSON.stringify({
    sender_id: EVOMAP_SENDER_ID,
    your_node_id: data.your_node_id,
    status: data.status,
    claim_code: data.claim_code,
    claim_url: data.claim_url,
    credit_balance: data.credit_balance,
    survival_status: data.survival_status,
    heartbeat_interval_ms: data.heartbeat_interval_ms,
    heartbeat_endpoint: data.heartbeat_endpoint,
  }, null, 2));
}

async function heartbeat() {
  const raw = await postJson(`${EVOMAP_BASE_URL}/a2a/heartbeat`, { node_id: EVOMAP_SENDER_ID });
  const data = unwrapPayload(raw);
  console.log(JSON.stringify({
    sender_id: EVOMAP_SENDER_ID,
    ok: true,
    response: data,
  }, null, 2));
}

async function fetchAssets() {
  const raw = await postJson(`${EVOMAP_BASE_URL}/a2a/fetch`, envelope('fetch', {
    asset_type: 'Capsule',
    include_tasks: true,
  }));
  const data = unwrapPayload(raw);
  console.log(JSON.stringify({
    sender_id: EVOMAP_SENDER_ID,
    assets: Array.isArray(data.assets) ? data.assets.length : 0,
    tasks: Array.isArray(data.tasks) ? data.tasks.length : 0,
  }, null, 2));
}

(async () => {
  const cmd = process.argv[2];
  if (!cmd || ['hello', 'heartbeat', 'fetch'].indexOf(cmd) === -1) {
    console.log('Usage: node scripts/evomap-client.js <hello|heartbeat|fetch>');
    process.exit(1);
  }
  if (cmd === 'hello') await hello();
  if (cmd === 'heartbeat') await heartbeat();
  if (cmd === 'fetch') await fetchAssets();
})().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
