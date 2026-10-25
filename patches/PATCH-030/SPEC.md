# PATCH-030 — PC audio buffer and local verification / Буфер звука / 本地音频缓冲

Base: Dewiar 0.45.3 (`32fcd918f21fc606efc0ed37870ac8edb9d1a290`). MS8AT build 35.

## RU — назначение и поведение

Один поток `Capture` обслуживает микрофон ПК и WAV. Он отдаёт кадры PCM16 mono
16 кГц: номер, позицию sample, monotonic timestamp получения и ID потока. История
звука отделена от рабочей очереди. Callback не вызывает модель, сеть или диск;
используется короткий mutex, это не обещание hard realtime.

- Рабочая очередь — 480 мс по умолчанию; при перегрузе удаляется старейший кадр.
  Потери считаются. Ядро сбрасывает незавершённую фразу и отменяет удерживаемую
  диктовку при разрыве: слова до и после пропуска не склеиваются в команду.
- История — 10 секунд, диапазон 1–30, **выключена по умолчанию**. Включается
  человеком в «Звук и поведение». При mute/закрытии очищается. Изменение размера
  перезапускает поток, переключение хранения действует сразу.
- «Проверить буфер» показывает заполнение, возраст очереди, потерянные миллисекунды.
  «Сохранить WAV» спрашивает подтверждение и скачивает файл человеку. Автоматической
  отправки в распознавание, модель, облако или память нет. Кнопки переведены RU/ENG/CH.
- WAV читается полностью, включая последний неполный кадр. Для существующего VAD
  `read()` дополняет его нулями до 512 samples; история и `read_frame()` сохраняют
  точную длину. При закрытии освобождается и WAV handle.
- `audio_context.py` — отдельно тестируемая машина версий partial/final текста:
  задержка стабильности, ограниченный recall ticket, отмена устаревшего результата,
  TTL и бюджет символов. **К живому ASR и MCP она пока не подключена**. Она не
  предсказывает речь, не отвечает человеку и не записывает память.

## Интерфейсы и проверка

В уже аутентифицированном API ядра:

```json
{"cmd":"audio_buffer_status","args":{}}
{"cmd":"audio_history_export","args":{"confirm":true,"seconds":10}}
{"cmd":"settings_save","args":{"patch":{"audio":{"history_enabled":true,"history_seconds":10}}}}
```

Ограниченный диагностический доступ отдаёт только метаданные и запрещает экспорт PCM:

```text
python core/diagnostic_cli.py audio
python core/diagnostic_cli.py api
python core/diagnostic_cli.py test
python tests/audio_buffer_test.py
python tests/audio_protocol_test.py
python tests/audio_buffer_ui_test.py
python tests/audio_pipeline_lab_test.py
python tests/voice_ring_browser_test.py
python tools/audio_pipeline_lab.py --out NEW_LOCAL_FOLDER --repeats 17 --graphs
```

Для тестов нужны numpy, websockets, Playwright с Chromium. Для графиков — matplotlib
в отдельной среде разработки. В runtime matplotlib не добавляется. Лаборатория
отказывается заменять существующую папку результатов. `audio_local.save_wav`
атомарно публикует файл через hard link; при неподдерживаемой файловой системе
завершается ошибкой, не перезаписывая существующий файл.

## Дорожная карта и критерии

| Блок | Критерий | Результат build 35 |
| --- | --- | --- |
| Захват и история | Точные samples, хвост WAV, 10 s после wrap | PASS на синтетике |
| Перегрузка | Ограниченная очередь, полный учёт кадров, сброс фразы при разрыве | PASS, виртуальное время + fake PortAudio |
| API/CLI | Реальный loopback, неверный token отклонён, экспорт только полным доступом и confirm | PASS на временном ядре Bridge |
| Кнопки | Проверить / отменить / скачать / ошибка / RU-ENG-CH | PASS в Chromium с mock ядром |
| Подготовка контекста | Старый ticket не применяется после исправления фразы; TTL | PASS, самостоятельный адаптер |
| Кодеки | 8 сигналов × 5 вариантов × 17 повторов; JSON, CSV, WAV, графики | PASS, 680 измеряемых round trips |
| Диктовка в полном ядре | От начала удержания до финального текста | PARTIAL: в среде нет Vosk; исходные FAIL-логи сохранены |
| ASR и память | WER, first partial/final, настоящий scoped recall | NOT_RUN |
| Микрофон и динамики | Разрешения ОС, устройства, эхо, акустика | NOT_RUN по выбранному пользователем режиму |
| Android | Нативный источник -> тот же контракт кадров и независимые тесты | NOT_RUN; этот патч не устанавливает Python-захват в APK |

Рекомендация этого этапа: оставить PCM контрольным форматом. Zlib хорошо сжимает
регулярные тестовые сигналы, но на шуме экономия мала. Log-μ-law сокращает PCM вдвое
с потерями и даже изменяет цифровой ноль на 3 LSB; это исследовательский compander,
не побитово совместимый G.711. На основании синтетики нельзя выбирать кодек для ASR.
Сначала нужна проверка распознавания на разрешённом корпусе с одинаковыми фразами.
Нативный AotoMic anchor codec, AGC и отправка пакетов в этот патч не входят.

## ENG — scope and integration prompt

Integrate only on the exact base above. Keep one Capture source, a bounded work
queue and a separate opt-in RAM history. Preserve final short WAV frames, close
the WAV handle, clear retained audio on mute and reset unfinished recognition on
sample gaps. Expose metadata through the existing diagnostic scope; permit WAV
export only through the authenticated application API with an explicit confirm.
Keep the context revision adapter independent: it has no live ASR/MCP connection,
model calls, memory writes or automatic speech. Run the five tests above, inspect
the deterministic lab outputs and verify every runtime hash. Record full-engine
dependency failures separately. Never call synthetic codec timing ASR latency.
This is a PC candidate patch, not an Android APK or an installed release.

## CH — 范围与集成提示词

仅在上述精确版本上集成。一个 Capture 音频源连接有限工作队列和独立的内存历史。
历史默认关闭；静音时清空。保留 WAV 最后一个不完整帧，关闭文件句柄。
丢帧时重置未完成的语句并取消按住录音，不能把缺口两侧的词拼成命令。
诊断 API 只返回元数据；WAV 导出需要应用身份验证和明确确认。
文本版本适配器单独测试，尚未连接真实 ASR 或 MCP；不调用模型、不写入记忆、
不自动发言。执行上述五项测试并检查所有运行文件哈希。八种合成信号、五种编码、
十七次测量不能证明真实语音识别质量。完整内核测试缺少 Vosk，保留失败记录。
这是 PC 候选补丁，不是 Android APK；真实麦克风、扬声器、模型预加载及安装未执行。

## Применение и откат

Патч проверяется в отдельной исходной копии. Для полной сборки нужна точная база
upstream; для delta — сохранённое дерево build 34 с совпадающими before-хешами.
Сначала `git apply --check`, затем применение и `verify_ms8at_overlay.py --json`.
Откат delta проверяется `git apply --reverse --check` и обратным применением в
тестовой копии. Установленное приложение, настройки, ключи и Android-диск не меняются.
Канал автоматической установки остаётся `effective=false`.
