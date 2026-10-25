/* Android memory contract: synthetic storage/adapters only. No sockets, accounts or models. */
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";
const scope = { window: {}, console: { log() { throw new Error("memory must not log notes"); } } };
vm.runInNewContext(fs.readFileSync(new URL("../android/assets/www/ms8at_memory.js", import.meta.url), "utf8"), scope);
const api = scope.window.MS8ATMemory;
const plain = value => JSON.parse(JSON.stringify(value));
const checks = [];
async function test(name, run) { await run(); checks.push(name); console.log("PASS " + name); }
function fixture(initial = "", permissions = {}) {
  let raw = initial, reads = 0, writes = 0;
  const storage = { read: () => { reads++; return raw; }, write: value => { writes++; raw = value; return true; } };
  const memory = api.create({ storage, permissions });
  return { memory, storage, raw: () => raw, counts: () => ({ reads, writes }), set: value => { raw = value; } };
}
const enabled = { enabled: true, read: true, write: true, tasks: true };
const sample = { id: "note1", text: "Синтетическая заметка", tags: ["demo"] };

await test("defaults deny all content operations without reading storage", async () => {
  const f = fixture();
  for (const result of [await f.memory.read(), await f.memory.search("demo"), await f.memory.get("note1"), await f.memory.add(sample), await f.memory.remove("note1")]) assert.equal(result.error, "permission_denied");
  assert.deepEqual(f.counts(), { reads: 0, writes: 0 });
  assert.equal(f.memory.status().human.status, "not_connected");
  assert.equal(f.memory.status().semantic.status, "not_connected");
});

await test("permission values and keys are strict and changes are atomic", async () => {
  const f = fixture();
  assert.equal(f.memory.configure({ enabled: true, read: "true" }).error, "invalid_permissions");
  assert.equal(f.memory.status().permissions.enabled, false);
  assert.equal(f.memory.configure({ token: "synthetic" }).error, "invalid_permissions");
  assert.equal(f.memory.configure({ enabled: true, write: true }).ok, true);
  assert.equal((await f.memory.add(sample)).ok, true);
  assert.equal((await f.memory.read()).error, "permission_denied");
});

await test("local persistence contains only versioned approved note fields", async () => {
  const f = fixture("", enabled);
  assert.equal((await f.memory.add(sample)).ok, true);
  assert.deepEqual(JSON.parse(f.raw()), { schema: 1, notes: [sample] });
  const again = api.create({ storage: f.storage, permissions: enabled });
  assert.deepEqual(plain((await again.get("note1")).note), sample);
  const result = await again.read(); result.notes[0].tags.push("outside");
  assert.deepEqual(plain((await again.get("note1")).note.tags), ["demo"]);
  assert.equal((await again.remove("note1")).ok, true);
  assert.equal((await again.get("note1")).note, null);
  assert.equal((await again.remove("note1")).error, "not_found");
});

await test("task permission enables reads only, never writes", async () => {
  const f = fixture("", { enabled: true, read: true, write: true }); await f.memory.add(sample);
  assert.equal((await f.memory.read({ purpose: "task" })).error, "permission_denied");
  assert.equal((await f.memory.search("demo", { purpose: "task" })).error, "permission_denied");
  f.memory.configure({ tasks: true });
  assert.equal((await f.memory.get("note1", { purpose: "task" })).ok, true);
  assert.equal((await f.memory.add({ text: "Task cannot write" }, { purpose: "task" })).error, "permission_denied");
  assert.equal((await f.memory.remove("note1", { purpose: "task" })).error, "permission_denied");
  f.memory.configure({ enabled: false });
  assert.equal((await f.memory.read({ purpose: "task" })).error, "permission_denied");
});

await test("local search is lexical, case insensitive and supports Chinese substrings", async () => {
  const f = fixture("", enabled);
  await f.memory.add({ id: "a", text: "Android module", tags: ["Тест"] });
  await f.memory.add({ id: "b", text: "中文记忆测试", tags: [] });
  assert.equal((await f.memory.search("android тест")).notes[0].id, "a");
  assert.equal((await f.memory.search("记忆")).notes[0].id, "b");
  assert.equal((await f.memory.search("unrelated")).notes.length, 0);
  assert.equal((await f.memory.search("module")).kind, "lexical");
  assert.equal(f.memory.status().local.search, "lexical");
});

await test("note, query and result bounds reject oversized or ambiguous inputs", async () => {
  const f = fixture("", enabled);
  for (const input of [null, {}, { text: " " }, { text: "x".repeat(4001) }, { text: "x", tags: ["y".repeat(33)] },
    { text: "x", tags: Array(9).fill("x") }, { text: "x", id: "../path" }, { text: "x", token: "synthetic" }, { text: "x", tags: "x" }]) {
    assert.equal((await f.memory.add(input)).error, "invalid_note");
  }
  for (const query of ["", " ", null, "x".repeat(257)]) assert.equal((await f.memory.search(query)).error, "invalid_query");
  for (const options of [{ source: "__proto__" }, { purpose: "auto" }, { limit: 0 }, { limit: 51 }, { limit: "3" }, { apiKey: "synthetic" }]) assert.equal((await f.memory.read(options)).error, "invalid_options");
  assert.equal((await f.memory.get("../path")).error, "invalid_id");
  assert.deepEqual(f.counts(), { reads: 0, writes: 0 });
});

await test("serialized concurrent additions do not lose notes or overwrite ids", async () => {
  const f = fixture("", enabled);
  const added = await Promise.all(Array.from({ length: 30 }, (_, i) => f.memory.add({ text: "note " + i })));
  assert.ok(added.every(item => item.ok));
  const listed = await f.memory.read({ limit: 50 });
  assert.equal(listed.notes.length, 30); assert.equal(new Set(listed.notes.map(n => n.id)).size, 30);
  const duplicate = await f.memory.add({ id: listed.notes[0].id, text: "must not overwrite" });
  assert.equal(duplicate.error, "duplicate_id");
  assert.equal((await f.memory.read({ limit: 2 })).notes.length, 2);
});

await test("queued writes capture approved input and inherited options cannot route exports", async () => {
  const f = fixture("", enabled);
  const input = { id: "stable", text: "approved", tags: ["original"] };
  const pending = f.memory.add(input); input.text = "later edit"; input.tags[0] = "changed";
  assert.equal((await pending).note.text, "approved");
  assert.deepEqual(plain((await f.memory.get("stable")).note.tags), ["original"]);
  let remoteCalls = 0;
  f.memory.attach("human", { read: () => { remoteCalls++; return []; }, search: () => [] });
  const result = await f.memory.read(Object.create({ source: "human" }));
  assert.equal(result.source, "local"); assert.equal(remoteCalls, 0);
});

await test("capacity rejects new notes and preserves existing data", async () => {
  const rows = Array.from({ length: api.limits.items }, (_, i) => ({ id: "n" + i, text: "fixture", tags: [] }));
  const raw = JSON.stringify({ schema: 1, notes: rows }); const f = fixture(raw, enabled);
  assert.equal((await f.memory.add({ text: "overflow" })).error, "capacity_reached");
  assert.equal(f.raw(), raw); assert.equal(f.counts().writes, 0);
});

await test("corrupt and oversized storage is never replaced by empty data", async () => {
  const corrupt = ["{", "[]", "null", JSON.stringify({ schema: 2, notes: [] }), JSON.stringify({ schema: 1, notes: [sample, sample] }),
    JSON.stringify({ schema: 1, notes: [{ ...sample, token: "synthetic" }] }), JSON.stringify({ schema: 1, notes: [], token: "synthetic" }),
    JSON.stringify({ schema: 1, notes: Array(201).fill(sample) }), " ".repeat(api.limits.storage + 1)];
  for (const raw of corrupt) {
    const f = fixture(raw, enabled);
    assert.equal((await f.memory.read()).error, "storage_corrupt");
    assert.equal((await f.memory.add({ text: "no silent repair" })).error, "storage_corrupt");
    assert.equal(f.raw(), raw); assert.equal(f.counts().writes, 0);
  }
});

await test("storage exceptions and unconfirmed writes expose only stable error codes", async () => {
  const unavailable = api.create({ permissions: enabled });
  assert.equal((await unavailable.read()).error, "storage_unavailable");
  const readFail = api.create({ permissions: enabled, storage: { read() { throw Error("secret fixture"); }, write: () => true } });
  assert.deepEqual(plain(await readFail.read()), { ok: false, error: "storage_read_failed" });
  for (const response of [false, undefined]) {
    const store = api.create({ permissions: enabled, storage: { read: () => "", write: () => response } });
    assert.equal((await store.add(sample)).error, "storage_write_failed");
  }
});

await test("revoking permission before a pending read completes prevents content export", async () => {
  let finish;
  const store = api.create({ permissions: enabled, storage: { read: () => new Promise(resolve => { finish = resolve; }), write: () => true } });
  const reading = store.read(); store.configure({ read: false }); finish(JSON.stringify({ schema: 1, notes: [sample] }));
  assert.deepEqual(plain(await reading), { ok: false, error: "permission_denied" });
});

await test("revocation while loading a write prevents storage mutation", async () => {
  let finish, writes = 0;
  const store = api.create({ permissions: enabled, storage: { read: () => new Promise(resolve => { finish = resolve; }), write: () => { writes++; return true; } } });
  const pending = store.add(sample); await Promise.resolve();
  store.configure({ write: false }); finish("");
  assert.equal((await pending).error, "permission_denied"); assert.equal(writes, 0);
});

await test("empty semantic and Human adapters remain unavailable and no local notes are exported", async () => {
  const f = fixture("", enabled); await f.memory.add(sample);
  assert.equal(f.memory.attach("human", {}).error, "invalid_adapter");
  for (const source of ["human", "semantic"]) assert.equal((await f.memory.search("query", { source })).error, "not_connected");
  assert.equal(f.memory.status().human.available, false);
});

await test("explicit adapter calls receive only the requested operation and limited parameters", async () => {
  const f = fixture("", enabled); await f.memory.add(sample); const calls = [];
  const adapter = { read: opt => { calls.push(["read", opt]); return [sample]; }, search: (query, opt) => { calls.push(["search", query, opt]); return [sample]; }, get: id => id === sample.id ? sample : null };
  assert.equal(f.memory.attach("human", adapter).status, "adapter_ready"); assert.equal(calls.length, 0);
  assert.equal((await f.memory.search("explicit query", { source: "human", limit: 3 })).notes.length, 1);
  assert.deepEqual(plain(calls), [["search", "explicit query", { limit: 3 }]]);
  assert.equal((await f.memory.get(sample.id, { source: "human" })).note.id, sample.id);
  assert.equal((await f.memory.add(sample, { source: "human" })).error, "unsupported_action");
  assert.equal(f.memory.status().human.status, "adapter_ready");
});

await test("adapter secret metadata, oversize responses and raw errors do not escape", async () => {
  const f = fixture("", enabled);
  const responses = [[{ ...sample, token: "synthetic" }], [{ ...sample, embedding: [1, 2] }], Array(201).fill(sample), { notes: [sample] }];
  for (const response of responses) {
    f.memory.attach("semantic", { read: () => response, search: () => response });
    assert.deepEqual(plain(await f.memory.read({ source: "semantic" })), { ok: false, error: "invalid_adapter_result" });
  }
  f.memory.attach("semantic", { read() { throw Error("secret fixture"); }, search() { throw Error("secret fixture"); } });
  assert.deepEqual(plain(await f.memory.search("query", { source: "semantic" })), { ok: false, error: "adapter_failed" });
});

await test("detached or replaced adapters cannot finish stale content delivery", async () => {
  let finish; const f = fixture("", enabled);
  f.memory.attach("human", { read: () => new Promise(resolve => { finish = resolve; }), search: () => [] });
  const pending = f.memory.read({ source: "human" }); f.memory.attach("human", null); finish([sample]);
  assert.deepEqual(plain(await pending), { ok: false, error: "permission_changed" });
});

await test("explicit adapter writes require confirmation and ambiguous completion never retries", async () => {
  let writes = 0; const f = fixture("", enabled);
  f.memory.attach("human", { read: () => [], search: () => [], write: () => { writes++; throw Error("unknown result"); } });
  const result = await f.memory.add(sample, { source: "human" });
  assert.deepEqual(plain(result), { ok: false, error: "adapter_write_failed", write_may_have_completed: true });
  assert.equal(writes, 1);
});

console.log("ALL OK: " + checks.length + " Android memory checks; network=0; model_calls=0; local search=lexical");
