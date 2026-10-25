# PATCH-027 — Audio pipeline roadmap / План аудиотракта / 音频链路路线图

**State / Статус / 状态: design only — NOT_IMPLEMENTED / только проектирование / 仅设计。**
The working code in this candidate is PATCH-026 WAV import. This document records
the wider AotoMic/Lyra request without claiming streaming transport or device
integration is already working.

## RU — что найдено и куда идём

### Фактическая основа

- Dewiar уже непрерывно держит выбранный в настройках микрофон открытым. Поток
  обрабатывается кадрами по 32 мс; Silero VAD выделяет фразы, после завершения
  фраза уходит в очередь распознавания. Есть локальные и удалённые STT, эхоподавление
  и режимы реакции на речь во время ответа.
- Сейчас нет настроенного 10-секундного кольца для сохранения записи и нет потока
  частичных исправляемых текстов: обычная фраза передаётся STT целиком после паузы.
  Текущий предбуфер фразы — около 0,4 с; хвост тишины ограничен примерно 0,2 с.
- PATCH-026 добавляет отдельный путь готового WAV: подтверждение, ограничения
  размера/длительности, выбранный STT, текст в поле проверки, без исполнения.
- В AotoMic найдены включаемые настройки AGC/VAD, кольцевой буфер и предбуфер.
  При этом `TransferManager::sendPacket` — заглушка: файл по сети фактически не
  передаётся. `SpkCodec` документирован как PCM passthrough; сжатие отложено.
- Исходники и статусы AotoMic изучены только чтением. Плата, прошивка, сетевой
  приёмник и физические записи в этой работе не проверялись.

### Блоки внедрения

1. **PC capture buffer.** PATCH-028 now keeps the Windows callback queue bounded and
   drops stale frames first under load. The requested 10-second history ring and
   manual recording/export are still not implemented. The next block is a shared
   source interface for selected mic, WAV, and later AotoMic; a bounded 10-second
   history ring; configurable pre/post-roll; sequence and timestamps. Disk,
   encoding and network work remain separate consumers so they cannot delay
   capture. Overflow is counted without blocking the microphone.
2. **Local recording.** Явные начало/стоп записи, фраза отдельным WAV, атомарное
   завершение файла, лимиты и настройки хранения. Частичный файл никогда не считается
   готовым; отмена удаляет только временный файл этой записи.
3. **AotoMic transport.** Сначала согласовать бинарный контракт и совместимый приёмник;
   затем реализовать идентификатор сессии/фразы, sequence, формат/частоту/каналы,
   время, begin/data/end, checksum, ACK/NACK, bounded queue, timeout, reconnect и
   защиту от дублей. Нужны mock-приёмник и воспроизведение потерь/перестановки пакетов.
   Пока отправитель AotoMic заглушка, этот путь остаётся отключённым.
4. **Streaming ASR.** Независимый адаптер backend, стабильные partial/final события с
   временными отметками и revision ID. Изменение гипотезы отменяет подготовленный ответ.
   До финализации текста команды не выполняются.
5. **Compression gate.** Сохранить PCM как эталон; измерить SPK и anchor codec на
   одинаковых записях. Сравнить байты после кодирования, задержку, CPU/RAM и качество
   распознавания. Не выбирать кодек по меньшему размеру пакета.
6. **Barge-in after audio tests.** По умолчанию выключено. Человек заговорил — Лира
   останавливает/приглушает свой ответ, слушает дальше и отменяет устаревшую реплику.
   Эхо Лиры не должно считаться речью человека. Ранний ответ — лишь отменяемая гипотеза
   по реально распознанным словам, без приписывания намерений и без речи поверх человека.

### Конфигурация — первоначальный безопасный профиль

| Группа | Настройки и первая базовая величина | Примечание |
|---|---|---|
| Источник | `AUDIO_SOURCE=pc_mic`; `INPUT_DEVICE_ID=default`; `INPUT_FILE_PATH` пусто | AotoMic станет selectable только после транспорта |
| Формат/буфер | `SAMPLE_RATE=16000`; `CHANNELS=1`; `BUFFER_SECONDS=10`; `PRE_ROLL_MS=400`; `POST_ROLL_MS=200` | смена устройства/частоты — перезапуск; память ограничена расчётным бюджетом |
| Усиление | `GAIN_MIN=1`; `GAIN_MAX=4`; `GAIN_INITIAL=1`; `GAIN_STEP=0.1`; `GAIN_UPDATE_MS=100`; `TARGET_LEVEL_DBFS=-24`; `CLIP_THRESHOLD_DBFS=-1` | software AGC отдельно от аппаратного; тесты не усиливают цифровую тишину |
| Речь | `NOISE_ESTIMATION_MS=1000`; `MIN_SNR_DB=6`; `VAD_THRESHOLD=0.6`; `SPEECH_START_MS=64`; `SPEECH_END_MS=650` | стартовые значения кандидата, требуют проверки на записях |
| Очистка/кодек | `DENOISE_ENABLED=false`; `DENOISE_STRENGTH=0`; `CODEC_MODE=pcm` | PCM — контрольный путь; anchor codec выключен до измерений |
| Транспорт | `TRANSFER_MODE=off`; `FRAME_MS=32`; `PACKET_PAYLOAD_BYTES=1024`; `QUEUE_LIMIT_MS=500`; `MAX_PACKET_AGE_MS=1000`; `RETRY_LIMIT=3`; `RECONNECT_MS=1000` | сетевой порт/маршрут не включается до реализации и проверки приёмника |
| Файл | `OUTPUT_DIRECTORY` — пусто до выбора пользователем; `MAX_FILE_BYTES=10485760`; `FILE_UPLOAD_TIMEOUT_MS=30000`; `KEEP_LOCAL_RECORDINGS=false` | запись не сохраняется без явного действия |
| ASR/фраза | `ASR_BACKEND=selected`; `ASR_MODEL=selected`; `LANGUAGE=ru`; `PARTIAL_UPDATE_MS=250`; `STABLE_TEXT_MS=500`; `THINK_PAUSE_MS=600`; `END_OF_UTTERANCE_MS=650`; `MAX_FINAL_WAIT_MS=30000`; `MAX_UTTERANCE_SECONDS=300` | фактический backend определяется настройкой Dewiar; адреса и ключи не придумываются |
| Перебивание | `BARGE_IN_ENABLED=false`; `EARLY_REPLY_ENABLED=false`; `INTERRUPT_MIN_SPEECH_MS=250`; `PREDICTION_CONFIDENCE_THRESHOLD=0.85`; `INTERRUPT_COOLDOWN_MS=1500`; `MAX_INTERRUPTS_PER_MINUTE=6`; `ECHO_CONTROL_ENABLED=true` | весь блок остаётся выключен до отдельной проверки безопасного поведения |
| Диагностика | `SAVE_RAW_AUDIO=false`; `SAVE_PROCESSED_AUDIO=false`; `SAVE_RECEIVED_AUDIO=false`; `SAVE_TRANSCRIPTS=false`; `LOG_LEVEL=INFO` | тексты, ключи и содержимое аудио не пишутся в обычный журнал |

Значения являются тестовым контрактом, а не утверждением, что эти переменные уже
подключены к runtime. Безопасные параметры можно будет менять на лету; устройства,
формат потока и лимит кольца — после остановки/перезапуска источника. Все диапазоны
должны быть ограничены валидатором до использования.

### План проверок и критерии

- Записи: тишина, тихая речь, шум, щелчки, речь в шуме, первая/последняя фонема,
  паузы и фразы до максимума. Одни и те же PCM-файлы для baseline и каждого варианта.
- Транспорт: дубли, пропуск, перестановка, отключение сети, очередь/timeout, отмена,
  retry с тем же ID без второго задания, повреждение и неполный файл.
- Метрики по стадиям: объём «речь против тишины», сжатие отдельно от packet overhead,
  latency первого partial и финала, CPU/RAM, потерянные кадры, ложный VAD и ошибки ASR.
- `PASS` только для воспроизводимого mock/записей в заявленном диапазоне; физический
  микрофон, AotoMic и реальная сеть отмечаются отдельно. До этого — `PARTIAL` или
  `NOT_RUN`, а не общий зелёный статус.

## EN — scope and status

Dewiar already keeps the selected PC microphone open, processes 32 ms frames,
segments speech with Silero VAD, and queues a completed utterance for the
selected local or remote recognizer. Echo cancellation and existing barge-in
modes are present. It does not yet retain a configured 10-second history or
stream revisable partial transcripts. PATCH-026 adds manual WAV import only.

The AotoMic source contains configurable AGC/VAD and ring/pre-buffer code, but
`TransferManager::sendPacket` is a stub and SPK is documented as PCM passthrough;
compression is deferred. The safe sequence is: bounded PC capture/history and
explicit recordings; tested receiver protocol; streaming ASR revisions; measured
codec comparison; then an opt-in barge-in phase. Firmware, device, and LAN
receiver were not modified or physically tested.

The Russian section is the normative parameter contract for the first test
profile. Its values are proposals, not active runtime settings. Every stage needs
mock and recorded-audio tests, followed by separate physical microphone, network,
and AotoMic validation. No commands run from unfinished ASR hypotheses. Human
barge-in yields the floor; predictive speech remains disabled until reviewed.

## 中文 — 范围与状态

Dewiar 已持续打开所选电脑麦克风，按 32 毫秒帧处理音频，使用 Silero VAD 分段，
并在一句话结束后把整段音频交给所选本地或远程识别器。已有回声消除和现有的
插话模式，但尚无可配置的 10 秒历史缓冲，也没有可修订的流式 partial 文本。
PATCH-026 目前只实现手动导入 WAV。

AotoMic 源码中有可配置的 AGC/VAD 与环形/预缓冲代码，但
`TransferManager::sendPacket` 仍是空实现；SPK 文档说明当前只是 PCM 直通，压缩尚未
实现。安全顺序是：电脑端有界缓冲与显式录音；验证接收端协议；流式 ASR 修订；
实测编解码；最后再测试可选的插话模式。没有修改或实测固件、设备或局域网接收端。

俄文部分的参数表是首个测试配置建议，并不表示这些变量已接入运行代码。每个阶段先
用模拟接收端和录音测试，再单独进行真实麦克风、网络和 AotoMic 测试。未完成的识别
假设不得执行命令。用户插话时助手让出发言顺序；预测性插话在审查前保持关闭。

## Rollback / Откат / 回滚

This is a design-only document. Remove its link and file; no runtime setting or
device state changes. / Это только документ проекта: удалить ссылку и файл; настройки
runtime и состояние устройства не менялись. / 本文件仅为设计文档；删除链接和文件即可，运行时
设置与设备状态均未改变。


## Progress — build 35

Shared Capture/WAV framing, bounded queue, opt-in history, WAV export and the
synthetic lab are implemented in [PATCH-030](../PATCH-030/SPEC.md). The
revision adapter is tested separately. AGC, live streaming ASR, model warmup,
semantic-memory prefetch and Android native capture remain unimplemented here.
