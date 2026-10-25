/* MS8AT: отдельная память Android. Хранит только явно добавленные заметки; без сети и логов.
   create({storage:{read:()=>JSON, write:JSON=>true}, permissions:{enabled,read,write,tasks}}).
   CRUD возвращает Promise с {ok,...}; configure/status/attach — синхронные.
   read/get/search({purpose:"task"}) дополнительно требуют tasks. UI обязано передавать эту цель.
   tasks разрешает только чтение для задач; запись остаётся отдельным действием человека.
   Semantic/Human подключаются только явным attach: read({limit}), search(query,{limit}),
   get(id) (необязательно), write(note) и remove(id) (необязательно, возвращают true).
   Adapter возвращает только {id,text,tags}, без embeddings, токенов и служебных полей.
   Этот модуль не добавляет заметки в prompt и не переносит local notes в другие источники. */
(function (root) {
  "use strict";
  const LIMITS = Object.freeze({ items: 200, text: 4000, tags: 8, tag: 32, id: 64, query: 256, result: 50, storage: 2000000 });
  const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  const object = o => o !== null && typeof o === "object" && !Array.isArray(o);
  const error = code => ({ ok: false, error: code });
  const copy = note => ({ id: note.id, text: note.text, tags: [...note.tags] });
  const validId = id => typeof id === "string" && /^[A-Za-z0-9_-]{1,64}$/.test(id);

  function note(value) {
    if (!object(value) || Object.keys(value).some(k => !["id", "text", "tags"].includes(k)) ||
        !own(value, "id") || !validId(value.id) || !own(value, "text") || typeof value.text !== "string" ||
        !value.text.trim() || value.text.length > LIMITS.text || !own(value, "tags") ||
        !Array.isArray(value.tags) || value.tags.length > LIMITS.tags ||
        value.tags.some(t => typeof t !== "string" || !t.trim() || t.length > LIMITS.tag)) return null;
    return { id: value.id, text: value.text, tags: [...new Set(value.tags)] };
  }

  function notes(value) {
    if (!Array.isArray(value) || value.length > LIMITS.items) return null;
    const result = value.map(note);
    return result.some(n => n === null) || new Set(result.map(n => n.id)).size !== result.length ? null : result;
  }

  function options(value = {}) {
    if (!object(value) || Object.keys(value).some(k => !["source", "purpose", "limit"].includes(k))) return null;
    const source = !own(value, "source") || value.source === undefined ? "local" : value.source;
    const purpose = !own(value, "purpose") || value.purpose === undefined ? "user" : value.purpose;
    const limit = !own(value, "limit") || value.limit === undefined ? 20 : value.limit;
    if (!["local", "semantic", "human"].includes(source) || !["user", "task"].includes(purpose) ||
        !Number.isInteger(limit) || limit < 1 || limit > LIMITS.result) return null;
    return { source, purpose, limit };
  }

  function create(config = {}) {
    const storage = config.storage;
    const permissions = { enabled: false, read: false, write: false, tasks: false };
    const adapters = { semantic: null, human: null };
    let version = 0, serial = 0, storeState = "unchecked", queue = Promise.resolve();
    const ready = () => !!storage && typeof storage.read === "function" && typeof storage.write === "function";

    function configure(value) {
      if (!object(value) || Object.keys(value).some(k => !own(permissions, k) || typeof value[k] !== "boolean")) return error("invalid_permissions");
      Object.assign(permissions, value); version++;
      return { ok: true, permissions: { ...permissions } };
    }

    function attach(source, adapter) {
      if (!["semantic", "human"].includes(source)) return error("invalid_source");
      if (adapter !== null && (!object(adapter) || typeof adapter.read !== "function" || typeof adapter.search !== "function")) return error("invalid_adapter");
      adapters[source] = adapter; version++;
      return { ok: true, source, status: adapter ? "adapter_ready" : "not_connected" };
    }

    function allowed(mode, opt) {
      return permissions.enabled && permissions[mode] && (opt.purpose !== "task" || (mode === "read" && permissions.tasks));
    }

    function gate(mode, opt, stamp) {
      if (!allowed(mode, opt)) return error("permission_denied");
      if (stamp !== version) return error("permission_changed");
      return null;
    }

    async function load() {
      if (!ready()) return error("storage_unavailable");
      let raw;
      try { raw = await storage.read(); } catch (_) { storeState = "unavailable"; return error("storage_read_failed"); }
      if (raw === "" || raw === null || raw === undefined) { storeState = "ready"; return { ok: true, notes: [] }; }
      try {
        if (typeof raw !== "string" || raw.length > LIMITS.storage) throw new Error();
        const parsed = JSON.parse(raw);
        if (!object(parsed) || parsed.schema !== 1 || Object.keys(parsed).some(k => !["schema", "notes"].includes(k))) throw new Error();
        const values = notes(parsed.notes);
        if (!values) throw new Error();
        storeState = "ready"; return { ok: true, notes: values };
      } catch (_) { storeState = "corrupt"; return error("storage_corrupt"); }
    }

    async function save(values) {
      try {
        const result = await storage.write(JSON.stringify({ schema: 1, notes: values }));
        if (result !== true) throw new Error();
        storeState = "ready"; return { ok: true };
      } catch (_) { storeState = "unavailable"; return error("storage_write_failed"); }
    }

    function status() {
      return { permissions: { ...permissions }, local: { available: ready(), status: ready() ? storeState : "unavailable", search: "lexical" },
        semantic: { available: !!adapters.semantic, status: adapters.semantic ? "adapter_ready" : "not_connected" },
        human: { available: !!adapters.human, status: adapters.human ? "adapter_ready" : "not_connected" } };
    }

    async function fetchNotes(kind, arg, value) {
      const opt = options(value);
      if (!opt) return error("invalid_options");
      if (!allowed("read", opt)) return error("permission_denied");
      const stamp = version;
      let result;
      if (opt.source === "local") {
        result = await load();
      } else {
        const adapter = adapters[opt.source];
        if (!adapter) return error("not_connected");
        try {
          let rows;
          if (kind === "search") rows = await adapter.search(arg, { limit: opt.limit });
          else if (kind === "get") {
            if (typeof adapter.get !== "function") return error("unsupported_action");
            const item = await adapter.get(arg); rows = item === null ? [] : [item];
          } else rows = await adapter.read({ limit: opt.limit });
          const values = notes(rows);
          result = values ? { ok: true, notes: values } : error("invalid_adapter_result");
        } catch (_) { result = error("adapter_failed"); }
      }
      const denied = gate("read", opt, stamp);
      if (denied) return denied;
      if (!result.ok) return result;
      let values = result.notes;
      if (kind === "get") return { ok: true, note: values.find(n => n.id === arg) || null, source: opt.source };
      if (kind === "search" && opt.source === "local") {
        const terms = arg.toLowerCase().trim().split(/\s+/);
        values = values.filter(n => { const text = [n.text, ...n.tags].join(" ").toLowerCase(); return terms.every(term => text.includes(term)); });
      }
      return { ok: true, notes: values.slice(0, opt.limit).map(copy), source: opt.source, kind: opt.source === "local" ? "lexical" : opt.source };
    }

    function read(value) { return fetchNotes("read", null, value); }
    function get(id, value) { return validId(id) ? fetchNotes("get", id, value) : Promise.resolve(error("invalid_id")); }
    function search(query, value) {
      if (typeof query !== "string" || !query.trim() || query.length > LIMITS.query) return Promise.resolve(error("invalid_query"));
      return fetchNotes("search", query, value);
    }

    function mutate(kind, input, value) {
      const opt = options(value);
      if (!opt) return Promise.resolve(error("invalid_options"));
      if (!allowed("write", opt)) return Promise.resolve(error("permission_denied"));
      const stamp = version;
      let item;
      // Capture the approved fields now; another queued write must not see later form edits.
      if (kind === "add") {
        if (!object(input) || Object.keys(input).some(k => !["id", "text", "tags"].includes(k)) || !own(input, "text")) return Promise.resolve(error("invalid_note"));
        const id = !own(input, "id") || input.id === undefined ? "n_" + Date.now().toString(36) + "_" + (++serial).toString(36) + "_" + Math.random().toString(36).slice(2, 10) : input.id;
        item = note({ id, text: input.text, tags: !own(input, "tags") || input.tags === undefined ? [] : input.tags });
        if (!item) return Promise.resolve(error("invalid_note"));
      } else if (!validId(input)) return Promise.resolve(error("invalid_id"));
      const work = async () => {
        let denied = gate("write", opt, stamp);
        if (denied) return denied;
        if (opt.source !== "local") {
          const adapter = adapters[opt.source], method = kind === "add" ? "write" : "remove";
          if (!adapter) return error("not_connected");
          if (typeof adapter[method] !== "function") return error("unsupported_action");
          try {
            const result = await adapter[method](kind === "add" ? copy(item) : input);
            denied = gate("write", opt, stamp);
            // A dispatched adapter write may already have happened; never retry it automatically.
            if (denied) return { ...denied, write_may_have_completed: true };
            if (result !== true) return error("adapter_write_failed");
          } catch (_) { return { ...error("adapter_write_failed"), write_may_have_completed: true }; }
        } else {
          const loaded = await load();
          denied = gate("write", opt, stamp);
          if (denied) return denied;
          if (!loaded.ok) return loaded;
          const values = loaded.notes;
          if (kind === "add") {
            if (values.some(n => n.id === item.id)) return error("duplicate_id");
            if (values.length >= LIMITS.items) return error("capacity_reached");
            values.push(item);
          } else {
            const at = values.findIndex(n => n.id === input);
            if (at < 0) return error("not_found");
            values.splice(at, 1);
          }
          const saved = await save(values);
          if (!saved.ok) return { ...saved, write_may_have_completed: true };
          denied = gate("write", opt, stamp);
          if (denied) return { ...denied, write_may_have_completed: true };
        }
        return kind === "add" ? { ok: true, note: copy(item), source: opt.source } : { ok: true, removed: input, source: opt.source };
      };
      const pending = queue.then(work);
      queue = pending.catch(() => {});
      return pending;
    }

    if (config.permissions !== undefined) configure(config.permissions);
    if (config.adapters) for (const source of ["semantic", "human"]) if (own(config.adapters, source)) attach(source, config.adapters[source]);
    return { configure, status, attach, read, get, search, add: (value, opt) => mutate("add", value, opt), remove: (id, opt) => mutate("remove", id, opt) };
  }

  root.MS8ATMemory = Object.freeze({ create, limits: LIMITS });
})(typeof window === "undefined" ? globalThis : window);
