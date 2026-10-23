export const DISCONNECT_TEXT = Object.freeze({
  codex: 'Выйти только из выбранного локального профиля Codex? Основной Codex и Hermes не изменятся.',
  account: 'Отозвать доступ выбранного аккаунта для этого локального приложения?'
});

export async function confirmDisconnect(ask, codex) {
  if (typeof ask !== 'function') throw new TypeError('ask function is required');
  return (await ask(codex ? DISCONNECT_TEXT.codex : DISCONNECT_TEXT.account)) === true;
}
