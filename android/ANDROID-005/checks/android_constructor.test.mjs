/* Независимые проверки маршрутов и журнала. Нет Android, сети, ключей и моделей. */
import assert from "node:assert/strict";
import {createRequire} from "node:module";
import fs from "node:fs";
import vm from "node:vm";
const require = createRequire(import.meta.url);
const api = require("../android/assets/www/ms8at_constructor.js");
let count = 0;
function check(name, fn) { fn(); count++; console.log("PASS " + name); }
function fixture(opts = {}) {
  const values = new Map(); let at = 10000;
  const storage = {getItem: k => values.get(k) || "", setItem: (k, v) => values.set(k, v)};
  const engine = api.create({storage, clock: () => at, timeoutMs: 1000, ...opts});
  return {engine, storage, values, advance: ms => { at += ms; }, reload: () => api.create({storage, clock: () => at})};
}
function provider(id, extra = {}) { return {id, kind: "local", configured: true, enabled: true, tools: true, purposes: ["chat", "tasks", "check", "memory"], ...extra}; }
function ready(opts) { const f = fixture(opts); f.engine.setProviders([provider("p_local"), provider("p_cloud", {kind: "cloud"})]); f.engine.setEnabled(true); return f; }

check("UMD browser export performs no network or timers", () => {
  const context = {fetch() { throw Error("network"); }, setTimeout() { throw Error("timer"); }};
  vm.runInNewContext(fs.readFileSync(new URL("../android/assets/www/ms8at_constructor.js", import.meta.url), "utf8"), context);
  assert.equal(typeof context.MS8ATConstructor.create, "function");
});
check("routing starts disabled and has no implicit current model", () => {
  const {engine} = fixture(); engine.setProviders([provider("p_local")]);
  assert.equal(engine.select("chat").reason, "disabled"); engine.setEnabled(true);
  assert.equal(engine.select("chat").reason, "unassigned");
});
check("manual selection never falls back after provider disappears", () => {
  const {engine} = ready(); engine.assign("tasks", "p_local");
  engine.setProviders([provider("p_cloud", {kind: "cloud"})]);
  assert.equal(engine.select("tasks").reason, "provider_missing");
});
check("provider enabled flag and per-purpose grant cannot be bypassed", () => {
  const {engine} = ready(); engine.assign("tasks", "p_local");
  for (const change of [{enabled: false}, {purposes: ["chat"]}]) {
    engine.setProviders([provider("p_local", change)]);
    assert.equal(engine.select("tasks").reason, "not_allowed");
  }
  engine.setProviders([provider("p_local", {configured: false})]);
  assert.equal(engine.select("tasks").reason, "not_configured");
});
check("tasks require tools even when caller passes tools false", () => {
  const {engine} = ready(); engine.setProviders([provider("p_local", {tools: false})]);
  engine.assign("tasks", "p_local"); engine.assign("chat", "p_local");
  assert.equal(engine.select("tasks", {tools: false}).reason, "no_tools");
  assert.equal(engine.select("chat").ok, true);
  assert.equal(engine.select("chat", {tools: true}).reason, "no_tools");
});
check("auto requires explicit list for each purpose and cannot borrow chat consent", () => {
  const {engine} = ready(); engine.assign("tasks", "auto"); engine.assign("chat", "auto");
  engine.allowAuto("chat", ["p_cloud"]);
  assert.equal(engine.select("tasks").reason, "no_approved_provider");
  assert.equal(engine.select("chat").providerId, "p_cloud");
  engine.allowAuto("tasks", ["p_local"]);
  engine.setProviders([provider("p_cloud", {kind: "cloud"})]);
  assert.equal(engine.select("tasks").reason, "no_approved_provider");
});
check("auto is stable and only uses tools-capable permitted candidates", () => {
  const {engine} = ready();
  engine.setProviders([provider("p_z"), provider("p_a"), provider("p_cloud", {kind: "cloud"}), provider("p_bad", {tools: false})]);
  engine.assign("tasks", "auto"); engine.allowAuto("tasks", ["p_cloud", "p_z", "p_bad", "p_a"]);
  assert.equal(engine.select("tasks").providerId, "p_a");
  engine.setProviders([provider("p_z"), provider("p_a", {enabled: false}), provider("p_cloud", {kind: "cloud"})]);
  assert.equal(engine.select("tasks").providerId, "p_z");
});
check("unknown purposes, prototype keys and malformed ids are refused", () => {
  const {engine} = ready();
  for (const p of ["__proto__", "constructor", "toString", "auxiliary", null]) {
    assert.throws(() => engine.assign(p, "p_local")); assert.throws(() => engine.select(p)); assert.throws(() => engine.allowAuto(p, []));
  }
  for (const id of ["__proto__", "constructor", "prototype", "auto", "http://host", "p secret", "p_".repeat(40)]) assert.throws(() => engine.setProviders([provider(id)]));
  assert.throws(() => engine.select("chat", {tools: "false"}));
  assert.throws(() => engine.setEnabled("true"));
});
check("registry rejects duplicates without replacing working providers", () => {
  const {engine} = ready(); engine.assign("chat", "p_local");
  assert.throws(() => engine.setProviders([provider("p_a"), provider("p_a")]));
  assert.equal(engine.select("chat").providerId, "p_local");
});
check("Codex and native Human Memory remain unavailable", () => {
  const {engine} = ready(); engine.setProviders([provider("p_codex", {kind: "codex"}), provider("p_human", {kind: "human_memory"})]);
  for (const id of ["p_codex", "p_human"]) {
    assert.equal(engine.assign("chat", id).reason, "adapter_unavailable");
    assert.equal(engine.allowAuto("chat", [id]).reason, "adapter_unavailable");
  }
  for (const id of ["codex", "human_memory"]) {
    assert.equal(engine.setBlockEnabled(id, true).ok, false);
    assert.equal(engine.snapshot().blocks.find(b => b.id === id).status, "unavailable");
  }
});
check("purpose routes, explicit auto grants and toggles survive reload", () => {
  const f = ready(); f.engine.assign("chat", "p_local"); f.engine.assign("check", "auto"); f.engine.allowAuto("check", ["p_cloud"]);
  f.engine.setBlockEnabled("doctor", false);
  const reloaded = f.reload(); reloaded.setProviders([provider("p_local"), provider("p_cloud", {kind: "cloud"})]);
  assert.deepEqual(reloaded.getConfig(), f.engine.getConfig());
  assert.equal(reloaded.select("check").providerId, "p_cloud");
  assert.equal(reloaded.select("tasks").reason, "unassigned");
});
check("corrupt or polluted storage resets to disabled without repair calls", () => {
  const f = ready(); f.engine.assign("chat", "p_local"); const saved = f.values.get(api.storageKey);
  const bad = ["{", "[]", " ".repeat(65537), saved.replace('"enabled":true', '"enabled":"true"'), saved.replace('"chat":"p_local"', '"chat":"constructor"')];
  const withSecret = JSON.parse(saved); withSecret.events[0].prompt = "PRIVATE"; bad.push(JSON.stringify(withSecret));
  bad.push(saved.replace('"routes":{', '"routes":{"__proto__":"p_cloud",'));
  for (const raw of bad) {
    f.values.set(api.storageKey, raw); const e = f.reload();
    assert.equal(e.snapshot().enabled, false); assert.equal(e.select("chat").reason, "storage_unavailable");
    assert.equal(e.snapshot().storage, "corrupt_or_unavailable");
    assert.equal(e.begin("chat").reason, "storage_unavailable");
    assert.deepEqual(e.snapshot().inFlight, []);
    assert.equal(f.values.get(api.storageKey), raw);
  }
});
check("provider secrets and raw error text never enter registry, events or storage", () => {
  const f = ready(); f.engine.setProviders([provider("p_local", {token: "TOKEN_PRIVATE", prompt: "PROMPT_PRIVATE", url: "https://PRIVATE"})]);
  f.engine.assign("chat", "p_local"); const run = f.engine.begin("chat");
  f.engine.finish(run.id, {ok: false, category: "network TOKEN_PRIVATE PROMPT_PRIVATE", error: "RAW_PRIVATE"});
  const output = JSON.stringify([f.engine.snapshot(), [...f.values.values()]]);
  assert.equal(output.includes("PRIVATE"), false);
  assert.equal(f.engine.snapshot().events.at(-1).code, "network");
  assert.equal(f.engine.snapshot().events.some(e => own(e, "providerId")), false);
  function own(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }
});
check("bounded journal and returned snapshots cannot mutate policy", () => {
  const {engine} = ready({maxEvents: 5}); engine.assign("chat", "p_local");
  for (let i = 0; i < 10; i++) { const r = engine.begin("chat"); engine.finish(r.id, {ok: true}); }
  assert.equal(engine.snapshot().events.length, 5);
  const view = engine.snapshot(); view.routes.chat = "p_cloud"; view.auto.tasks.push("p_cloud"); view.providers[0].enabled = false;
  assert.equal(engine.select("chat").providerId, "p_local"); assert.deepEqual(engine.getConfig().auto.tasks, []);
});
check("heartbeat times out once as unknown and never retries", () => {
  const f = ready(); f.engine.assign("chat", "p_local"); const run = f.engine.begin("chat");
  f.advance(900); f.engine.signal(run.id); f.advance(900); assert.equal(f.engine.tick().inFlight.length, 1);
  f.advance(100); const expired = f.engine.tick(); assert.equal(expired.inFlight.length, 0);
  assert.equal(expired.events.at(-1).state, "unknown"); assert.equal(expired.events.at(-1).kind, "timeout");
  const rows = expired.events.length; f.advance(5000); assert.equal(f.engine.tick().events.length, rows);
  assert.equal(f.engine.signal(run.id), false); assert.equal(f.engine.finish(run.id, {ok: true}), false);
});
check("restart marks unfinished calls unknown, without creating new calls", () => {
  const f = ready(); f.engine.assign("chat", "p_local"); const run = f.engine.begin("chat");
  const next = f.reload(); assert.deepEqual(next.snapshot().inFlight, []);
  assert.deepEqual(next.snapshot().events.at(-1).state, "unknown"); assert.equal(next.snapshot().events.at(-1).call, run.id);
  assert.equal(next.snapshot().events.at(-1).kind, "interrupted");
  assert.equal(f.reload().snapshot().events.filter(e => e.kind === "interrupted").length, 1);
});
check("diagnosis gives fixed suggestions with no automatic replay", () => {
  for (const [error, code] of [["maximum context length exceeded", "context_overflow"], ["tools not supported", "no_tools"], ["failed to fetch", "network"], ["secret unknown details", "unknown"]]) {
    const result = api.diagnose(error); assert.equal(result.code, code); assert.equal(result.retry, false);
    assert.equal(JSON.stringify(result).includes(error), false);
  }
});
check("doctor health is local, purpose-specific and does not dispatch or write", () => {
  const f = fixture();
  const before = f.engine.snapshot().events.length;
  const initial = f.engine.health();
  assert.equal(initial.status, "attention");
  assert.deepEqual(initial.purposes.map(row => row.code), Array(4).fill("routing_disabled"));
  f.engine.setProviders([provider("p_local", {tools: true})]);
  for (const role of ["chat", "tasks", "check", "memory"]) f.engine.assign(role, "p_local");
  f.engine.setEnabled(true);
  const report = f.engine.health();
  assert.equal(report.status, "ready");
  assert.equal(report.purposes.every(row => row.ok && row.code === "ready"), true);
  assert.equal(f.engine.snapshot().inFlight.length, 0);
  assert.equal(f.engine.snapshot().events.length, before + 5);
  assert.equal(JSON.stringify(report).includes("p_local"), false);
});
check("doctor distinguishes missing task tools and blocked storage", () => {
  const f = ready(); f.engine.setProviders([provider("p_local", {tools: false})]);
  for (const role of ["chat", "tasks", "check", "memory"]) f.engine.assign(role, "p_local");
  f.engine.setEnabled(true);
  assert.equal(f.engine.health().purposes.find(row => row.purpose === "tasks").code, "no_tools");
  const broken = api.create({storage:{getItem(){throw Error("PRIVATE");},setItem(){throw Error("PRIVATE");}}});
  assert.equal(broken.health().status, "blocked");
  assert.equal(JSON.stringify(broken.health()).includes("PRIVATE"), false);
});
check("doctor toggle disables suggestions without changing routing or retrying", () => {
  const {engine} = ready(); engine.assign("chat", "p_local"); engine.setBlockEnabled("doctor", false);
  assert.deepEqual(engine.diagnose("maximum context length exceeded"), {code: "unknown", action: "disabled", retry: false});
  const run = engine.begin("chat"); engine.finish(run.id, {ok: false, category: "context_overflow"});
  assert.equal(engine.snapshot().events.at(-1).code, "unknown");
  assert.equal(engine.select("chat").providerId, "p_local");
});
check("storage failures are visible and do not masquerade as saved state", () => {
  const engine = api.create({clock: () => 1000, storage: {getItem() {throw Error("PRIVATE");}, setItem() {throw Error("PRIVATE");}}});
  assert.equal(engine.snapshot().storage, "corrupt_or_unavailable"); engine.setEnabled(true);
  assert.equal(engine.snapshot().storage, "unavailable"); assert.equal(JSON.stringify(engine.snapshot()).includes("PRIVATE"), false);
  assert.equal(engine.select("chat").reason, "storage_unavailable");
  assert.equal(engine.begin("chat").reason, "storage_unavailable");
  assert.deepEqual(engine.snapshot().inFlight, []);
});
check("failed route save blocks dispatch until an explicit successful save", () => {
  const f = ready(); f.engine.assign("chat", "p_local");
  const saved = f.values.get(api.storageKey), write = f.storage.setItem;
  f.storage.setItem = () => { throw Error("Synthetic disk failure"); };
  f.engine.assign("chat", "p_cloud");
  assert.equal(f.engine.snapshot().storage, "unavailable");
  assert.equal(f.engine.select("chat").reason, "storage_unavailable");
  assert.equal(f.engine.begin("chat").reason, "storage_unavailable");
  assert.deepEqual(f.engine.snapshot().inFlight, []);
  assert.equal(f.values.get(api.storageKey), saved);
  assert.equal(f.reload().getConfig().routes.chat, "p_local");
  f.storage.setItem = write;
  assert.equal(f.engine.begin("chat").reason, "storage_unavailable");
  f.engine.assign("chat", "p_cloud");
  assert.equal(f.engine.snapshot().storage, "ok");
  assert.equal(f.engine.begin("chat").providerId, "p_cloud");
});
check("failure saving call_start never returns a dispatch permit or leaves a running call", () => {
  const f = ready(); f.engine.assign("chat", "p_local");
  const saved = f.values.get(api.storageKey);
  assert.equal(f.engine.select("chat").ok, true);
  f.storage.setItem = () => { throw Error("Synthetic disk failure"); };
  const run = f.engine.begin("chat");
  assert.equal(run.ok, false); assert.equal(run.reason, "storage_unavailable");
  assert.equal(run.id, undefined); assert.deepEqual(f.engine.snapshot().inFlight, []);
  assert.equal(f.values.get(api.storageKey), saved);
  const events = f.engine.snapshot().events.length;
  assert.equal(f.engine.begin("chat").reason, "storage_unavailable");
  assert.equal(f.engine.snapshot().events.length, events);
});
check("disabled heartbeat does not invent completion and call count is bounded", () => {
  const f = ready(); f.engine.assign("chat", "p_local"); f.engine.setBlockEnabled("heartbeat", false);
  for (let i = 0; i < 32; i++) assert.equal(f.engine.begin("chat").ok, true);
  assert.equal(f.engine.begin("chat").reason, "too_many_calls"); f.advance(10000);
  assert.equal(f.engine.tick().inFlight.length, 32);
});
console.log("ALL OK: " + count + " constructor cases; network=0; model_calls=0");
