/* Конструктор Android: явные назначения мозгов и местный журнал состояний.
   Здесь нет сети, таймеров, запуска моделей и повторов. Адаптер передаёт только
   возможности профиля; ключи, адреса, запросы и сырые ошибки сюда не сохраняем. */
(function(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.MS8ATConstructor = api;
})(typeof globalThis === "object" ? globalThis : this, function() {
  "use strict";
  const PURPOSES = ["chat", "tasks", "check", "memory"];
  const KINDS = ["local", "cloud", "codex", "human_memory"];
  const BLOCKS = ["routing", "heartbeat", "doctor", "codex", "human_memory"];
  const KEY = "ms8at_android_constructor_v1";
  const REASONS = ["context_overflow", "no_tools", "network", "unknown"];
  const STATES = ["completed", "failed", "unknown", "interrupted"];
  const EVENTS = ["enabled", "route", "auto", "block", "call_start", "call_signal", "call_end", "timeout", "interrupted"];
  const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  const clone = o => JSON.parse(JSON.stringify(o));
  const object = o => o && typeof o === "object" && !Array.isArray(o) && Object.getPrototypeOf(o) === Object.prototype;
  const exact = (o, keys) => object(o) && Object.keys(o).length === keys.length && keys.every(k => own(o, k));
  const validId = id => typeof id === "string" && /^[A-Za-z][A-Za-z0-9_-]{0,63}$/.test(id) && !["constructor", "prototype", "toString", "hasOwnProperty"].includes(id);
  function purpose(value) { if (!PURPOSES.includes(value)) throw new Error("Unknown purpose"); return value; }
  function flag(value) { if (typeof value !== "boolean") throw new Error("Expected boolean"); return value; }
  function providerId(value) { if (!validId(value) || value === "auto") throw new Error("Invalid provider id"); return value; }
  function defaults() {
    return { version: 1, enabled: false, routes: {chat: "", tasks: "", check: "", memory: ""},
      auto: {chat: [], tasks: [], check: [], memory: []},
      blocks: {routing: false, heartbeat: true, doctor: true, codex: false, human_memory: false} };
  }
  function config(value) {
    if (!exact(value, ["version", "enabled", "routes", "auto", "blocks"]) || value.version !== 1 ||
        !exact(value.routes, PURPOSES) || !exact(value.auto, PURPOSES) || !exact(value.blocks, BLOCKS)) throw new Error("Invalid config");
    flag(value.enabled);
    for (const p of PURPOSES) {
      const id = value.routes[p], ids = value.auto[p];
      if (id !== "" && id !== "auto") providerId(id);
      if (!Array.isArray(ids) || ids.length > 32 || new Set(ids).size !== ids.length) throw new Error("Invalid auto list");
      ids.forEach(providerId);
    }
    BLOCKS.forEach(id => flag(value.blocks[id]));
    if (value.blocks.routing !== value.enabled || value.blocks.codex || value.blocks.human_memory) throw new Error("Unavailable block");
    return clone(value);
  }
  function diagnose(error) {
    // Читаем лишь ограниченный фрагмент для классификации; строку не возвращаем.
    const text = typeof error === "string" ? error.slice(0, 2048) : "";
    let code = REASONS.includes(text) ? text : "unknown";
    if (/context[_ ](?:length|window|overflow)|maximum context|too many tokens|окн[ао] контекст|контекст.*переполн/i.test(text)) code = "context_overflow";
    else if (/no_tools|tools? (?:not supported|unsupported)|does not support (?:tools|function)|ни одного действия/i.test(text)) code = "no_tools";
    else if (/network|failed to fetch|ECONN|ETIMEDOUT|timeout|сеть|соединен/i.test(text)) code = "network";
    return {code, action: {context_overflow: "compact_context", no_tools: "choose_tool_provider", network: "check_connection", unknown: "inspect_locally"}[code], retry: false};
  }
  function create(options) {
    options = options || {};
    const storage = options.storage, clock = options.clock || (() => Date.now());
    const maxEvents = Number.isInteger(options.maxEvents) ? Math.max(1, Math.min(200, options.maxEvents)) : 100;
    const timeoutMs = Number.isFinite(options.timeoutMs) ? Math.max(1000, Math.min(3600000, options.timeoutMs)) : 90000;
    let settings = defaults(), providers = [], events = [], runs = [], sequence = 0, storageState = "memory";
    function now() { const value = clock(); if (!Number.isFinite(value) || value < 0) throw new Error("Invalid clock"); return Math.floor(value); }
    function event(kind, data) {
      // Только перечисленные поля; даже переданный по ошибке prompt/key исчезает.
      const row = {seq: ++sequence, at: now(), kind};
      if (data && PURPOSES.includes(data.purpose)) row.purpose = data.purpose;
      if (data && Number.isSafeInteger(data.call) && data.call > 0) row.call = data.call;
      if (data && STATES.includes(data.state)) row.state = data.state;
      if (data && REASONS.includes(data.code)) row.code = data.code;
      events.push(row); events = events.slice(-maxEvents);
    }
    function save() {
      if (!storage || typeof storage.setItem !== "function") return;
      try {
        storage.setItem(KEY, JSON.stringify({config: settings, events, sequence,
          pending: runs.map(r => ({id: r.id, purpose: r.purpose}))}));
        storageState = "ok";
      } catch (_) { storageState = "unavailable"; }
    }
    function restore() {
      if (!storage || typeof storage.getItem !== "function") return;
      try {
        const raw = storage.getItem(KEY);
        if (!raw) { storageState = "ok"; return; }
        if (typeof raw !== "string" || raw.length > 65536) throw new Error("Oversized storage");
        const value = JSON.parse(raw);
        if (!exact(value, ["config", "events", "sequence", "pending"]) || !Number.isSafeInteger(value.sequence) || value.sequence < 0 ||
            !Array.isArray(value.events) || value.events.length > 200 || !Array.isArray(value.pending) || value.pending.length > 32) throw new Error("Invalid journal");
        const checked = config(value.config);
        for (const row of value.events) {
          if (!object(row) || Object.keys(row).some(k => !["seq", "at", "kind", "purpose", "call", "state", "code"].includes(k)) ||
              !Number.isSafeInteger(row.seq) || row.seq < 1 || row.seq > value.sequence || !Number.isFinite(row.at) || row.at < 0 || !EVENTS.includes(row.kind) ||
              (own(row, "purpose") && !PURPOSES.includes(row.purpose)) || (own(row, "call") && (!Number.isSafeInteger(row.call) || row.call < 1)) ||
              (own(row, "state") && !STATES.includes(row.state)) || (own(row, "code") && !REASONS.includes(row.code))) throw new Error("Invalid event");
        }
        for (const run of value.pending) {
          if (!exact(run, ["id", "purpose"]) || !Number.isSafeInteger(run.id) || run.id < 1 || run.id > value.sequence || !PURPOSES.includes(run.purpose)) throw new Error("Invalid pending call");
        }
        settings = checked; sequence = value.sequence; events = value.events.slice(-maxEvents); storageState = "ok";
        // Перезапуск не доказывает исход запроса и не даёт права отправить его снова.
        for (const run of value.pending) event("interrupted", {call: run.id, purpose: run.purpose, state: "unknown"});
        if (value.pending.length) save();
      } catch (_) { settings = defaults(); events = []; runs = []; sequence = 0; storageState = "corrupt_or_unavailable"; }
    }
    restore();
    function setProviders(list) {
      if (!Array.isArray(list) || list.length > 32) throw new Error("Invalid provider registry");
      const clean = list.map(p => {
        if (!object(p) || !KINDS.includes(p.kind) || !Array.isArray(p.purposes) || new Set(p.purposes).size !== p.purposes.length) throw new Error("Invalid provider");
        p.purposes.forEach(purpose);
        return {id: providerId(p.id), kind: p.kind, configured: p.configured === true, enabled: p.enabled === true, tools: p.tools === true, purposes: p.purposes.slice()};
      });
      if (new Set(clean.map(p => p.id)).size !== clean.length) throw new Error("Duplicate provider");
      providers = clean;
      return clone(providers);
    }
    function setEnabled(value) { settings.enabled = flag(value); settings.blocks.routing = value; event("enabled"); save(); return settings.enabled; }
    function setBlockEnabled(id, value) {
      if (!BLOCKS.includes(id)) throw new Error("Unknown block");
      flag(value);
      if (id === "codex" || id === "human_memory") return {ok: false, reason: "adapter_unavailable"};
      if (id === "routing") setEnabled(value);
      else { settings.blocks[id] = value; event("block"); save(); }
      return {ok: true, enabled: value};
    }
    function assign(role, id) {
      purpose(role);
      if (id !== "" && id !== "auto") {
        providerId(id);
        const candidate = providers.find(p => p.id === id);
        if (!candidate || ["codex", "human_memory"].includes(candidate.kind)) return {ok: false, reason: "adapter_unavailable"};
      }
      settings.routes[role] = id; event("route", {purpose: role}); save(); return {ok: true};
    }
    function allowAuto(role, ids) {
      purpose(role);
      if (!Array.isArray(ids) || ids.length > 32 || new Set(ids).size !== ids.length) throw new Error("Invalid auto list");
      ids.forEach(providerId);
      if (ids.some(id => !providers.some(p => p.id === id && !["codex", "human_memory"].includes(p.kind)))) return {ok: false, reason: "adapter_unavailable"};
      settings.auto[role] = ids.slice(); event("auto", {purpose: role}); save(); return {ok: true};
    }
    function select(role, opts) {
      purpose(role); opts = opts || {};
      if (!object(opts) || Object.keys(opts).some(k => k !== "tools") || (own(opts, "tools") && typeof opts.tools !== "boolean")) throw new Error("Invalid routing options");
      const denied = reason => ({ok: false, purpose: role, reason});
      if (storageState === "unavailable" || storageState === "corrupt_or_unavailable") return denied("storage_unavailable");
      if (!settings.enabled) return denied("disabled");
      const id = settings.routes[role], tools = role === "tasks" || opts.tools === true;
      function reason(p) {
        if (!p) return "provider_missing";
        if (["codex", "human_memory"].includes(p.kind)) return "adapter_unavailable";
        if (!p.configured) return "not_configured";
        if (!p.enabled || !p.purposes.includes(role)) return "not_allowed";
        if (tools && !p.tools) return "no_tools";
        return "";
      }
      if (!id) return denied("unassigned");
      if (id !== "auto") {
        const p = providers.find(p => p.id === id), error = reason(p);
        return error ? denied(error) : {ok: true, purpose: role, providerId: p.id, kind: p.kind, mode: "manual"};
      }
      // Список задаёт человек. При равных условиях предпочитаем local, затем ID.
      const candidates = providers.filter(p => settings.auto[role].includes(p.id) && !reason(p));
      candidates.sort((a, b) => (a.kind === "local" ? 0 : 1) - (b.kind === "local" ? 0 : 1) || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
      const p = candidates[0];
      return p ? {ok: true, purpose: role, providerId: p.id, kind: p.kind, mode: "auto"} : denied("no_approved_provider");
    }
    function begin(role, opts) {
      const chosen = select(role, opts);
      if (!chosen.ok) return chosen;
      if (runs.length >= 32) return {ok: false, purpose: role, reason: "too_many_calls"};
      const id = sequence + 1, at = now();
      runs.push({id, purpose: role, providerId: chosen.providerId, started: at, signalAt: at});
      event("call_start", {call: id, purpose: role}); save();
      if (storageState === "unavailable") { runs = runs.filter(r => r.id !== id); return {ok:false,purpose:role,reason:"storage_unavailable"}; }
      return Object.assign({}, chosen, {id});
    }
    function signal(id) {
      const run = runs.find(r => r.id === id);
      if (!run) return false;
      run.signalAt = Math.max(run.signalAt, now());
      event("call_signal", {call: id, purpose: run.purpose}); save(); return true;
    }
    function finish(id, result) {
      const index = runs.findIndex(r => r.id === id);
      if (index < 0) return false;
      if (!object(result) || typeof result.ok !== "boolean") throw new Error("Expected call result");
      const run = runs.splice(index, 1)[0];
      event("call_end", {call: id, purpose: run.purpose, state: result.ok ? "completed" : "failed", code: result.ok ? undefined : inspectError(result.category).code});
      save(); return true;
    }
    function inspectError(error) {
      return settings.blocks.doctor ? diagnose(error) : {code: "unknown", action: "disabled", retry: false};
    }
    function health() {
      const purposes = PURPOSES.map(role => {
        if (!settings.enabled) return {purpose: role, ok: false, code: "routing_disabled"};
        const selected = select(role, role === "tasks" ? {tools: true} : {});
        return {purpose: role, ok: selected.ok, code: selected.ok ? "ready" : selected.reason};
      });
      const storageOk = storageState === "ok" || storageState === "memory";
      const ready = storageOk && purposes.every(row => row.ok);
      return {status: !storageOk ? "blocked" : ready ? "ready" : "attention", storage: storageState, purposes};
    }
    function snapshot() {
      return clone({enabled: settings.enabled, routes: settings.routes, auto: settings.auto, providers, storage: storageState,
        blocks: BLOCKS.map(id => ({id, enabled: settings.blocks[id], status: ["codex", "human_memory"].includes(id) ? "unavailable" : settings.blocks[id] ? "ready" : "disabled"})),
        inFlight: runs.map(r => Object.assign({state: "running"}, r)), events});
    }
    function tick() {
      if (settings.blocks.heartbeat) {
        const at = now(), expired = runs.filter(r => at - r.signalAt >= timeoutMs);
        if (expired.length) {
          runs = runs.filter(r => !expired.includes(r));
          for (const run of expired) event("timeout", {call: run.id, purpose: run.purpose, state: "unknown"});
          save();
        }
      }
      return snapshot();
    }
    return {setProviders, setEnabled, setBlockEnabled, assign, allowAuto, select, begin, signal, finish, tick, snapshot, health,
      diagnose: inspectError, getConfig: () => clone(settings)};
  }
  return {create, diagnose, purposes: PURPOSES.slice(), storageKey: KEY};
});
