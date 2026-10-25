/* ANDROID-001: язык разговора, слуха и голоса. Сам интерфейс пока остаётся русским.
   Здесь только три разрешённых языка; адреса серверов, ключи и модель не меняются. */
(function () {
  "use strict";
  const modes = {
    ru: { code: "ru", label: "RU", locale: "ru-RU", name: "Русский",
      prompt: "Язык этого разговора — русский. Отвечай по-русски, если пользователь явно не просит другой язык. Это правило языка важнее языка примеров персонажа; имена инструментов и их параметры не переводи.",
      busy: "Смените язык после текущего ответа или записи.",
      voice: "Русский голос устройства недоступен — ответ остаётся текстом. Выберите голос в настройках телефона или настройте сервер голоса.",
      ears: "Русское распознавание недоступно: установите языковой пакет или напишите текстом. Сервер автоматически не включается." },
    en: { code: "en", label: "ENG", locale: "en-US", name: "English",
      prompt: "The conversation language is English. Reply in English unless the user explicitly requests another language. This language rule overrides the language of persona examples; do not translate tool names or parameters.",
      busy: "Change language after the current response or recording.",
      voice: "An English device voice is unavailable. The answer remains as text. Install a device voice or configure a voice server.",
      ears: "English speech recognition is unavailable. Install the language pack or type your message. No server is enabled automatically." },
    "zh-CN": { code: "zh-CN", label: "CH", locale: "zh-CN", name: "简体中文",
      prompt: "本次对话使用简体中文。除非用户明确要求其他语言，否则请用简体中文回答。本语言规则优先于角色示例中的语言；不要翻译工具名称或参数。",
      busy: "请在当前回答或录音结束后切换语言。",
      voice: "设备没有可用的中文语音。回答仍以文字显示。请安装设备语音或配置语音服务器。",
      ears: "中文语音识别不可用。请安装语言包或输入文字。不会自动启用服务器。" }
  };
  const order = ["ru", "en", "zh-CN"];
  function mode(code) { return code === "en" || code === "zh-CN" ? modes[code] : modes.ru; }
  function next(code) { return order[(order.indexOf(mode(code).code) + 1) % order.length]; }
  function paint(button, code) {
    if (!button) return;
    const m = mode(code);
    button.textContent = m.label;
    button.title = "RU / ENG / CH · " + m.name;
    button.setAttribute("aria-label", button.title);
    button.setAttribute("lang", m.locale);
  }
  window.DewiarLanguage = { mode, next, paint };
})();
