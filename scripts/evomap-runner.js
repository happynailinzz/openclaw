#!/usr/bin/env node
/**
 * EvoMap runner: heartbeat + fetch + filter + local report
 * Run once:
 *   node scripts/evomap-runner.js
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = process.cwd();
const ENV_PATH = path.join(ROOT, 'config', 'evomap.env');
const PROFILE_PATH = path.join(ROOT, 'config', 'evomap-task-profile.json');
const STATE_DIR = path.join(ROOT, 'memory');
const STATE_PATH = path.join(STATE_DIR, 'evomap-state.json');

function ensureDir(p) { if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true }); }
function loadJson(p, fallback) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return fallback; }
}
function saveJson(p, data) { fs.writeFileSync(p, JSON.stringify(data, null, 2)); }

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
const profile = loadJson(PROFILE_PATH, { focusKeywords: [], excludeKeywords: [], minBounty: 0, maxTasksKeep: 50 });

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
  const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const txt = await r.text();
  let data; try { data = JSON.parse(txt); } catch { data = { raw: txt }; }
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${txt.slice(0, 500)}`);
  return data;
}
function unwrap(data) { return data && data.payload ? data.payload : data; }

function scoreTask(task) {
  const title = (task.title || '').toLowerCase();
  const signals = (task.signals || '').toLowerCase();
  const hay = `${title} ${signals}`;
  let score = 0;
  for (const k of profile.focusKeywords || []) if (hay.includes(String(k).toLowerCase())) score += 2;
  for (const k of profile.excludeKeywords || []) if (hay.includes(String(k).toLowerCase())) score -= 5;
  const bounty = Number(task.bountyAmount || 0);
  if (bounty >= Number(profile.minBounty || 0)) score += Math.min(5, Math.floor(bounty / 100));
  return score;
}

(async () => {
  ensureDir(STATE_DIR);
  const now = new Date().toISOString();

  const hbRaw = await postJson(`${BASE}/a2a/heartbeat`, { node_id: SENDER });
  const hb = unwrap(hbRaw);

  const fetchRaw = await postJson(`${BASE}/a2a/fetch`, envelope('fetch', { asset_type: 'Capsule', include_tasks: true }));
  const fx = unwrap(fetchRaw);
  const tasks = Array.isArray(fx.tasks) ? fx.tasks : [];
  const results = Array.isArray(fx.results) ? fx.results : [];

  const ranked = tasks
    .map(t => ({ ...t, _score: scoreTask(t) }))
    .sort((a, b) => b._score - a._score)
    .slice(0, Number(profile.maxTasksKeep || 50));

  const promotedCapsules = results
    .filter(r => (r.asset_type === 'Capsule' || (r.payload && r.payload.type === 'Capsule')) && r.status === 'promoted')
    .sort((a, b) => Number(b.gdi_score || 0) - Number(a.gdi_score || 0));

  const nodeAgg = {};
  for (const c of promotedCapsules) {
    const node = c.source_node_id || 'unknown';
    if (!nodeAgg[node]) nodeAgg[node] = { count: 0, sum: 0, max: 0 };
    nodeAgg[node].count += 1;
    nodeAgg[node].sum += Number(c.gdi_score || 0);
    nodeAgg[node].max = Math.max(nodeAgg[node].max, Number(c.gdi_score || 0));
  }
  const topNodes = Object.entries(nodeAgg)
    .map(([nodeId, v]) => ({
      nodeId,
      count: v.count,
      maxGdi: Number(v.max.toFixed(2)),
      avgGdi: Number((v.sum / v.count).toFixed(2)),
    }))
    .sort((a, b) => b.maxGdi - a.maxGdi || b.avgGdi - a.avgGdi)
    .slice(0, 10);

  const state = {
    updatedAt: now,
    sender_id: SENDER,
    heartbeat: {
      status: hb.status,
      node_status: hb.node_status,
      survival_status: hb.survival_status,
      credit_balance: hb.credit_balance,
      next_heartbeat_ms: hb.next_heartbeat_ms,
    },
    stats: {
      totalTasks: tasks.length,
      totalCapsules: results.length,
      promotedCapsules: promotedCapsules.length,
      topPositive: ranked.filter(x => x._score > 0).length,
      topNeutralOrNegative: ranked.filter(x => x._score <= 0).length,
    },
    topTasks: ranked.slice(0, 10).map(t => ({
      id: t.id || t.task_id,
      title: t.title,
      bountyAmount: t.bountyAmount || t.bounty_amount || 0,
      minReputation: t.minReputation || t.min_reputation,
      score: t._score,
      createdAt: t.createdAt || t.created_at,
    })),
    topCapsules: promotedCapsules.slice(0, 10).map(c => ({
      assetId: c.asset_id,
      sourceNodeId: c.source_node_id,
      gdiScore: Number(c.gdi_score || 0),
      confidence: Number(c.confidence || 0),
      triggerText: c.trigger_text || '',
      summary: (c.payload && (c.payload.summary || c.payload.title || c.payload.content || '') || '').toString().replace(/\s+/g, ' ').slice(0, 180),
    })),
    topNodes,
  };

  saveJson(STATE_PATH, state);
  console.log(JSON.stringify(state, null, 2));
})().catch(err => {
  console.error(err.message || String(err));
  process.exit(1);
});
