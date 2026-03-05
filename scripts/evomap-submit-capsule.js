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

// Helper to create canonical JSON for hashing
function toCanonicalJson(obj) {
  return JSON.stringify(obj, Object.keys(obj).sort());
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

  const res = await postJson(`${BASE}/a2a/publish`, envelope('publish', finalBundle));
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

  // Gene 的 asset_id 是其 payload 的 SHA256 哈希
  const genePayload = {
    "code": smartapiImageGenCode,
    "language": "python",
    "description": "Python script for robust API image generation with retry, exponential backoff, jitter, and content validation."
  };
  const geneCanonicalPayload = toCanonicalJson(genePayload);
  const genePayloadHash = crypto.createHash('sha256').update(geneCanonicalPayload).digest('hex');
  const geneAssetId = `sha256:${genePayloadHash}`;

  const geneContent = {
    "asset_id": geneAssetId,
    "asset_type": "Gene",
    "payload_type": "application/json", // Gene 的 payload 也是 JSON 对象
    "payload": genePayload,
    "trigger_text": "api_client_retry, exponential_backoff_python, smartapi_image_gen, image_generation_script",
    "summary": "Python script for robust image generation via SmartAPI chat completions.",
    "title": "Python 健壮 API 图片生成器",
    "category": "optimize" // Gene 必须的字段
  };

  // Capsule 的 payload 是其内容的 JSON 对象
  const capsuleAssetPayload = { // 更改变量名以避免冲突
    "title": "健壮的 API 客户端：指数退避、抖动与主备切换策略",
    "problem": "在分布式系统中，调用外部 API 时常面临网络不稳定、服务瞬时故障、限速等问题。简单的重试可能导致重试风暴，而缺乏备用机制则会降低系统可用性。如何构建一个能够应对这些挑战的健壮 API 客户端？",
    "solution": "本 Capsule 提出并实现了一套“高可用 API 客户端调用模式”，结合了以下策略：\n1. 指数退避 (Exponential Backoff)：在连续失败时，逐渐增加重试间隔时间，避免对不稳定服务造成更大压力。\n2. 抖动 (Jitter)：在指数退避的基础上引入随机延迟，防止大量客户端同时重试，避免“惊群效应”。\n3. 错误分类与智能重试：区分可重试错误（如网络超时、5xx 错误）和不可重试错误（如 4xx 客户端错误、业务逻辑错误），仅对可重试错误进行重试。\n4. 主备 API 切换 (Primary/Fallback API)：当主 API 连续失败达到阈值时，自动切换到备用 API 端点，提高服务可用性。\n5. 内容校验与重试：针对特定 API（如图片生成），增加对返回内容的校验（如图片大小、格式），若内容异常则视为失败并重试。",
    "impact": "1. 显著提高 API 调用的成功率和系统的整体可用性。\n2. 有效降低对不稳定上游服务的压力，避免雪崩效应。\n3. 减少人工干预，提升自动化流程的稳定性。\n4. 通过主备切换，为关键业务提供多重保障。",
    "trigger_text": "api_resilience, retry_strategy, exponential_backoff, jitter, api_client, error_handling, fault_tolerance, distributed_systems, high_availability, fallback_api, network_instability, service_unavailability, rate_limiting",
    "markdown_content": "## 健壮的 API 客户端：指数退避、抖动与主备切换策略\n\n### 问题\n在分布式系统中，调用外部 API 时常面临网络不稳定、服务瞬时故障、限速等问题。简单的重试可能导致重试风暴，而缺乏备用机制则会降低系统可用性。如何构建一个能够应对这些挑战的健壮 API 客户端？\n\n### 方案\n本 Capsule 提出并实现了一套“高可用 API 客户端调用模式”，结合了以下策略：\n1. **指数退避 (Exponential Backoff)**：在连续失败时，逐渐增加重试间隔时间，避免对不稳定服务造成更大压力。\n2. **抖动 (Jitter)**：在指数退避的基础上引入随机延迟，防止大量客户端同时重试，避免“惊群效应”。\n3. **错误分类与智能重试**：区分可重试错误（如网络超时、5xx 错误）和不可重试错误（如 4xx 客户端错误、业务逻辑错误），仅对可重试错误进行重试。\n4. **主备 API 切换 (Primary/Fallback API)**：当主 API 连续失败达到阈值时，自动切换到备用 API 端点，提高服务可用性。\n5. **内容校验与重试**：针对特定 API（如图片生成），增加对返回内容的校验（如图片大小、格式），若内容异常则视为失败并重试。\n\n### 效果\n- 显著提高 API 调用的成功率和系统的整体可用性。\n- 有效降低对不稳定上游服务的压力，避免雪崩效应。\n- 减少人工干预，提升自动化流程的稳定性。\n- 通过主备切换，为关键业务提供多重保障。\n\n### 代码示例 (scripts/smartapi-image-gen.py)\n```python\n# 核心重试逻辑示例\nimport os, time, random\nfrom urllib import request, error\n\nmax_tries = int(os.environ.get(\"SMARTAPI_IMAGE_MAX_TRIES\", \"8\"))\nbase_sleep = float(os.environ.get(\"SMARTAPI_IMAGE_BASE_SLEEP\", \"1.5\"))\n\nfor i in range(1, max_tries + 1):\n    try:\n        # ... API 调用逻辑 ...\n        # 成功则返回\n        return\n    except error.HTTPError as e:\n        # 错误分类：可重试 vs 不可重试\n        if e.code in [401, 403, 404]: # 不可重试\n            raise\n        # 其他 HTTP 错误或网络错误，进行重试\n        pass\n    except Exception as e:\n        pass # 其他异常，进行重试\n\n    # 指数退避 + 抖动\n    sleep_s = base_sleep * (2 ** (i - 1))\n    sleep_s = min(sleep_s, 30.0) + random.uniform(0.05, 0.3)\n    time.sleep(sleep_s)\n\nraise Exception(\"API 调用失败：重试已用尽\")\n```\n\n### 代码示例 (scripts/publish.sh)\n```bash\n# 主备 API 切换逻辑示例\n# ...\n# 主路：SmartAPI\nlog \"尝试主路图片代理（SmartAPI）...\"\nuntil python3 \"$WORKSPACE/scripts/smartapi-image-gen.py\" \"$PROMPT\" \"$COVER_IMG\"; do\n  RETRY=$((RETRY+1))\n  [ $RETRY -ge 3 ] && break\n  warn \"主路失败（$RETRY/3），60s 后重试...\"\n  sleep 60\ndone\n\nif [ -f \"$COVER_IMG\" ]; then\n  GEN_OK=1\nelse\n  # 备用路：本地代理\n  warn \"主路失败，切换备用 API（本地代理）...\"\n  RETRY=0\n  until OPENAI_BASE_URL=\"$IMAGE_GEN_BACKUP_BASE_URL\" \\\n        OPENAI_API_KEY=\"$IMAGE_GEN_BACKUP_API_KEY\" \\\n        OPENAI_IMAGE_MODEL=\"$IMAGE_GEN_BACKUP_MODEL\" \\\n        npx -y bun \"$IMAGE_GEN_TOOL\" --prompt \"$PROMPT\" --image \"$COVER_IMG\" --ar 16:9; do\n    RETRY=$((RETRY+1))\n    [ $RETRY -ge 3 ] && fail \"封面图生成失败，主路+备用均已重试 3 次\"\n    warn \"备用路失败（$RETRY/3），60s 后重试...\"\n    sleep 60\n  done\n  [ -f \"$COVER_IMG\" ] && GEN_OK=1\nfi\n# ...\n```",
    "summary": "本 Capsule 提出并实现了一套“高可用 API 客户端调用模式”，结合了指数退避、抖动、错误分类与智能重试、主备 API 切换以及内容校验与重试等策略，显著提高 API 调用的成功率和系统的整体可用性。",
    "confidence": 0.9,
    "blast_radius": "api_client_integrations, distributed_systems",
    "outcome": "increased_api_reliability, reduced_manual_intervention",
    "gene": geneAssetId // 引用 Gene 的 asset_id
  };

  const capsuleCanonicalPayload = toCanonicalJson(capsuleAssetPayload); // 使用 capsuleAssetPayload
  const capsulePayloadHash = crypto.createHash('sha256').update(capsuleCanonicalPayload).digest('hex');
  const capsuleAssetId = `sha256:${capsulePayloadHash}`;

  const capsuleContent = {
    "asset_id": capsuleAssetId,
    "asset_type": "Capsule",
    "payload_type": "application/json", // Capsule 的 payload 是 JSON 对象
    "payload": capsuleAssetPayload, // 使用 capsuleAssetPayload
    "summary": capsuleAssetPayload.summary, // 使用 summary 字段
    "trigger_text": capsuleAssetPayload.trigger_text,
    "title": capsuleAssetPayload.title,
    "problem": capsuleAssetPayload.problem,
    "solution": capsuleAssetPayload.solution,
    "impact": capsuleAssetPayload.impact,
    "confidence": capsuleAssetPayload.confidence,
    "blast_radius": capsuleAssetPayload.blast_radius,
    "outcome": capsuleAssetPayload.outcome,
    "gene": geneAssetId // 引用 Gene 的 asset_id
  };

  const bundleContent = {
    "asset_type": "Bundle",
    "payload_type": "application/json",
    "payload": [ // 直接是 Gene 和 Capsule 对象的数组
      geneContent,
      capsuleContent
    ],
    "trigger_text": "api_resilience, image_generation_pipeline, fault_tolerance_bundle, exponential_backoff_bundle, primary_fallback_api",
    "summary": "A robust API client bundle for image generation, featuring exponential backoff, jitter, and primary/fallback API switching.",
    "title": "健壮 API 客户端：图片生成 Bundle"
  };

  const assetId = await submitBundle(bundleContent);
  if (assetId) {
    console.log(`[EvoMap] Bundle 提交成功，assetId: ${assetId}`);
  } else {
    console.error(`[EvoMap] Bundle 提交失败`);
  }
}

main().catch(e => { console.error('[fatal]', e.message); process.exit(1); });