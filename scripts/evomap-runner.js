#!/usr/bin/env node
/**
 * EvoMap runner v2
 * 功能：
 *   1. 心跳保活（节点存活）
 *   2. 拉取 topCapsules，提取高 GDI 知识点，写入本地 evomap-state.json
 *   3. 若有高分 Capsule（GDI >= 62），触发写入 capability-tree 候选
 *   4. 不再查"任务池"（EvoMap 无此功能）
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = process.cwd();
const ENV_PATH = path.join(ROOT, 'config', 'evomap.env');
const STATE_DIR = path.join(ROOT, 'memory');
const STATE_PATH = path.join(STATE_DIR, 'evomap-state.json');
const CANDIDATES_PATH = path.join(STATE_DIR, 'evomap-evolution-candidates.md');

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

// 心跳限速：每5分钟一次，加 jitter
const HEARTBEAT_WINDOW_MS = 300000;

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
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
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

async function doHeartbeat() {
  const state = loadJson(STATE_PATH, {});
  const lastHb = state.heartbeat?.lastSentAt ? new Date(state.heartbeat.lastSentAt).getTime() : 0;
  const now = Date.now();
  const jitter = Math.floor(Math.random() * 200) + 50;

  if (now - lastHb < HEARTBEAT_WINDOW_MS - 5000) {
    const waitMs = HEARTBEAT_WINDOW_MS - (now - lastHb);
    console.log(`[heartbeat] 距上次 ${Math.round((now - lastHb)/1000)}s，限速未到，跳过（还需等 ${Math.round(waitMs/1000)}s）`);
    return { skipped: true, credit: state.heartbeat?.credit_balance ?? 0 };
  }

  const res = await postJson(`${BASE}/a2a/heartbeat`, envelope('heartbeat', {
    capabilities: ['content_writing', 'digital_transformation', 'agent_orchestration', 'system_engineering'],
    node_type: 'agent',
  }));

  const p = unwrap(res);

  if (p.error === 'rate_limited') {
    console.log(`[heartbeat] 限速，${Math.round((p.retry_after_ms || 300000)/1000)}s 后重试`);
    return { skipped: true, credit: state.heartbeat?.credit_balance ?? 0 };
  }

  console.log(`[heartbeat] 状态=${p.node_status || 'ok'} credit=${p.credit_balance ?? '?'} survival=${p.survival_status || 'ok'}`);
  return {
    skipped: false,
    lastSentAt: new Date().toISOString(),
    node_status: p.node_status,
    survival_status: p.survival_status,
    credit_balance: p.credit_balance ?? 0,
    next_heartbeat_ms: p.next_heartbeat_ms ?? HEARTBEAT_WINDOW_MS,
  };
}

async function doFetch() {
  const res = await postJson(`${BASE}/a2a/fetch`, envelope('fetch', {
    asset_type: 'Capsule',
    include_tasks: false,  // 任务池不存在，不再请求
  }));

  const fx = unwrap(res);
  const capsules = Array.isArray(fx.results) ? fx.results : [];
  const lessons = Array.isArray(fx.relevant_lessons) ? fx.relevant_lessons : [];

  console.log(`[fetch] capsules=${capsules.length} lessons=${lessons.length} mode=${fx.mode || '?'}`);

  // 高 GDI capsule（>= 62）提取为能力候选
  const GDI_THRESHOLD = 62;
  const topCapsules = capsules
    .filter(c => (c.gdi_score || 0) >= GDI_THRESHOLD)
    .sort((a, b) => (b.gdi_score || 0) - (a.gdi_score || 0))
    .slice(0, 10)
    .map(c => ({
      assetId: c.asset_id,
      sourceNodeId: c.source_node_id,
      gdiScore: c.gdi_score,
      confidence: c.confidence,
      triggerText: c.trigger_text,
      summary: (c.payload?.summary || c.payload?.content || '').slice(0, 180),
    }));

  // 节点统计
  const nodeMap = {};
  for (const c of capsules) {
    const nid = c.source_node_id || 'unknown';
    if (!nodeMap[nid]) nodeMap[nid] = { nodeId: nid, count: 0, maxGdi: 0, avgGdi: 0, gdis: [] };
    nodeMap[nid].count++;
    nodeMap[nid].gdis.push(c.gdi_score || 0);
    if ((c.gdi_score || 0) > nodeMap[nid].maxGdi) nodeMap[nid].maxGdi = c.gdi_score || 0;
  }
  const topNodes = Object.values(nodeMap).map(n => ({
    ...n,
    avgGdi: n.gdis.length ? Math.round(n.gdis.reduce((a,b)=>a+b,0)/n.gdis.length * 100)/100 : 0,
    gdis: undefined,
  })).sort((a,b)=>b.maxGdi-a.maxGdi).slice(0,7);

  return { topCapsules, topNodes, lessonCount: lessons.length,
    stats: { totalCapsules: capsules.length,
      promotedCapsules: capsules.filter(c=>c.status==='promoted').length,
      topPositive: topCapsules.length,
      topNeutralOrNegative: capsules.filter(c=>(c.gdi_score||0)<GDI_THRESHOLD).length } };
}

function appendCandidates(topCapsules) {
  // 把新的高分 capsule 写入候选文件（去重）
  const existing = fs.existsSync(CANDIDATES_PATH) ? fs.readFileSync(CANDIDATES_PATH,'utf8') : '';
  const newEntries = topCapsules.filter(c => !existing.includes(c.assetId));
  if (newEntries.length === 0) return 0;

  const lines = [`\n## 新增候选 ${new Date().toISOString().slice(0,10)}\n`];
  for (const c of newEntries) {
    lines.push(`- **GDI ${c.gdiScore}** | ${c.triggerText}`);
    lines.push(`  摘要: ${c.summary}`);
    lines.push(`  assetId: \`${c.assetId}\``);
    lines.push('');
  }
  fs.appendFileSync(CANDIDATES_PATH, lines.join('\n'));
  return newEntries.length;
}

async function main() {
  console.log(`[evomap-runner v2] sender=${SENDER} time=${new Date().toISOString()}`);

  const prevState = loadJson(STATE_PATH, {});

  // 1. 心跳
  const hbResult = await doHeartbeat();

  // 2. 拉取 Capsule（无限速问题，直接拉）
  let fetchResult = null;
  try {
    fetchResult = await doFetch();
  } catch (e) {
    console.error('[fetch] 失败:', e.message);
  }

  // 3. 更新状态
  const newState = {
    updatedAt: new Date().toISOString(),
    sender_id: SENDER,
    heartbeat: hbResult.skipped
      ? { ...(prevState.heartbeat || {}), status: 'ok' }
      : { status: 'ok', ...hbResult },
    stats: fetchResult?.stats || prevState.stats || {},
    topTasks: [],  // EvoMap 无任务池，保留空数组保持兼容
    topCapsules: fetchResult?.topCapsules || prevState.topCapsules || [],
    topNodes: fetchResult?.topNodes || prevState.topNodes || [],
  };

  saveJson(STATE_PATH, newState);

  // 4. 新增候选写入
  const newCount = fetchResult ? appendCandidates(fetchResult.topCapsules) : 0;

  // 5. 输出摘要
  const stats = newState.stats;
  console.log(`\n[摘要]`);
  console.log(`  capsules: ${stats.totalCapsules || 0} 总 / GDI≥62: ${stats.topPositive || 0} 条`);
  console.log(`  新增候选: ${newCount} 条`);
  console.log(`  credit: ${newState.heartbeat?.credit_balance ?? '?'}`);
  if (newCount > 0) {
    console.log(`  ⚡ 有新能力候选，建议进入 B2 评估流程`);
  } else {
    console.log(`  无新候选，HEARTBEAT_OK`);
  }
}

main().catch(e => { console.error('[fatal]', e.message); process.exit(1); });
