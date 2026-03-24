#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const workflowPath = path.join(__dirname, '..', 'workflow_inbound_whatsapp_google_sheets.json');

function readWorkflow() {
  return JSON.parse(fs.readFileSync(workflowPath, 'utf8'));
}

function findNode(workflow, name) {
  const node = workflow.nodes.find((n) => n.name === name);
  if (!node) throw new Error(`Node not found: ${name}`);
  return node;
}

function normalizeText(value) {
  return String(value || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .trim();
}

function assertEqual(actual, expected, label) {
  if (actual !== expected) {
    throw new Error(`[FAIL] ${label}: expected="${expected}" actual="${actual}"`);
  }
  console.log(`[OK] ${label}: ${actual}`);
}

function runClassifierTests(classifierCode) {
  const classify = new Function('$json', '$env', classifierCode);
  const env = {
    INBOUND_BLOCK_ON_NEGATIVE: 'true',
    INBOUND_BLOCK_ON_POSITIVE: 'false',
  };

  const cases = [
    {
      text: 'nao tenho interesse, pare de mandar',
      expectedClass: 'negativo',
      expectedBlock: true,
    },
    {
      text: 'sim, tenho interesse',
      expectedClass: 'positivo',
      expectedBlock: false,
    },
    {
      text: 'qual valor e disponibilidade?',
      expectedClass: 'positivo',
      expectedBlock: false,
    },
    {
      text: 'agora nao, fala depois',
      expectedClass: 'neutro',
      expectedBlock: false,
    },
    {
      text: 'ok',
      expectedClass: 'neutro',
      expectedBlock: false,
    },
  ];

  console.log('\n== Classifier tests ==');
  for (const c of cases) {
    const out = classify({ text_norm: normalizeText(c.text) }, env)[0].json;
    assertEqual(out.classificacao, c.expectedClass, `classificacao: ${c.text}`);
    assertEqual(Boolean(out.bloquear_envio), c.expectedBlock, `bloquear_envio: ${c.text}`);
    if (typeof out.classificacao_score !== 'number') {
      throw new Error(`[FAIL] score ausente: ${c.text}`);
    }
    console.log(`[OK] score ${out.classificacao_score} para: ${c.text}`);
  }
}

function runWithNow(fakeNowMs, fn) {
  const originalNow = Date.now;
  Date.now = () => fakeNowMs;
  try {
    return fn();
  } finally {
    Date.now = originalNow;
  }
}

function runDedupeTests(dedupeCode) {
  const dedupe = new Function('$json', '$env', '$getWorkflowStaticData', dedupeCode);
  const globalState = {};
  const getWorkflowStaticData = () => globalState;

  const env = {
    INBOUND_DEDUPE_TTL_SECONDS: '172800',
    INBOUND_DEDUPE_TEXT_WINDOW_SECONDS: '600',
    INBOUND_DEDUPE_MAX_KEYS: '50000',
  };

  const baseNow = 1700000000000;
  const windowMs = 600000;

  console.log('\n== Dedupe tests ==');

  const byMessageA = runWithNow(baseNow, () => dedupe({
    event: 'messages.upsert',
    message_id: 'msg-1',
    phone_norm: '5511999999999',
    text_norm: normalizeText('sim'),
  }, env, getWorkflowStaticData)[0].json);

  assertEqual(byMessageA.is_duplicate, false, 'message_id first seen');
  assertEqual(byMessageA.dedupe_reason, 'message_id_new', 'message_id reason first seen');

  const byMessageB = runWithNow(baseNow + 1000, () => dedupe({
    event: 'messages.upsert',
    message_id: 'msg-1',
    phone_norm: '5511999999999',
    text_norm: normalizeText('sim'),
  }, env, getWorkflowStaticData)[0].json);

  assertEqual(byMessageB.is_duplicate, true, 'message_id duplicate');
  assertEqual(byMessageB.dedupe_reason, 'message_id', 'message_id reason duplicate');

  const byTextA = runWithNow(baseNow + 2000, () => dedupe({
    event: 'messages.upsert',
    message_id: '',
    phone_norm: '5511888888888',
    text_norm: normalizeText('ok manda'),
  }, env, getWorkflowStaticData)[0].json);

  assertEqual(byTextA.is_duplicate, false, 'text window first seen');
  assertEqual(byTextA.dedupe_reason, 'text_window_new', 'text window reason first seen');

  const byTextB = runWithNow(baseNow + 4000, () => dedupe({
    event: 'messages.upsert',
    message_id: '',
    phone_norm: '5511888888888',
    text_norm: normalizeText('ok manda'),
  }, env, getWorkflowStaticData)[0].json);

  assertEqual(byTextB.is_duplicate, true, 'text window duplicate same bucket');
  assertEqual(byTextB.dedupe_reason, 'text_window', 'text window reason same bucket');

  const byTextCrossBucket = runWithNow(baseNow + windowMs + 3000, () => dedupe({
    event: 'messages.upsert',
    message_id: '',
    phone_norm: '5511888888888',
    text_norm: normalizeText('ok manda'),
  }, env, getWorkflowStaticData)[0].json);

  assertEqual(byTextCrossBucket.is_duplicate, true, 'text window duplicate previous bucket');
  assertEqual(byTextCrossBucket.dedupe_reason, 'text_window', 'text window reason previous bucket');

  const byTextAfterTwoBuckets = runWithNow(baseNow + (2 * windowMs) + 3000, () => dedupe({
    event: 'messages.upsert',
    message_id: '',
    phone_norm: '5511888888888',
    text_norm: normalizeText('ok manda'),
  }, env, getWorkflowStaticData)[0].json);

  assertEqual(byTextAfterTwoBuckets.is_duplicate, false, 'text window accepted after two buckets');
}

function main() {
  const workflow = readWorkflow();
  const classifierNode = findNode(workflow, 'Classificar Resposta PT-BR');
  const dedupeNode = findNode(workflow, 'Deduplicar Evento (TTL)');

  runClassifierTests(classifierNode.parameters.jsCode);
  runDedupeTests(dedupeNode.parameters.jsCode);

  console.log('\nAll inbound workflow logic tests passed.');
}

main();
