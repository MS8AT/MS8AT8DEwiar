import assert from 'node:assert/strict';
import {confirmDisconnect, DISCONNECT_TEXT} from '../src/ui/subscription_disconnect.mjs';

const seen = [];
assert.equal(await confirmDisconnect(async text => { seen.push(text); return true; }, true), true);
assert.match(seen[0], /Основной Codex и Hermes не изменятся/);
assert.equal(await confirmDisconnect(async text => { seen.push(text); return false; }, false), false);
assert.match(seen[1], /Отозвать доступ выбранного аккаунта/);
assert.doesNotMatch(DISCONNECT_TEXT.codex + DISCONNECT_TEXT.account, /token|https?:|file:\/\//i);
await assert.rejects(() => confirmDisconnect(null, true), /ask function is required/);
console.log('ALL OK: PATCH-009 public contract; network=0; account_calls=0; model_calls=0');
