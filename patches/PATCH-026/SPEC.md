# PATCH-026 — WAV import and reviewable transcription / Импорт WAV и проверяемая расшифровка / WAV 导入与可检查转写

## RU — цель и поведение

Человек выбирает запись AotoMic или другой WAV-файл в чате Dewiar и проверяет
расшифровку до отправки ассистенту.

- Выбор WAV просит подтверждение и предупреждает: при удалённом распознавателе
  аудио будет отправлено на этот сервер.
- Принимается только несжатый PCM WAV: 16 бит, mono/stereo, 8–48 кГц, до 10 МиБ
  и 5 минут. Файл обрабатывается в памяти, приводится к mono 16 кГц и делится
  на фрагменты по 20 секунд с перекрытием 250 мс.
- Используется выбранный в настройках распознаватель. При сбое показывается
  ошибка; скрытой смены сервиса нет.
- Повторы слов на границах фрагментов убираются. Текст помещается в редактируемое
  поле ввода и не исполняется как команда. Продолжение происходит только после
  проверки текста и нажатия «Отправить».
- Запись не сохраняется адаптером; сетевой слушатель не открывается; прошивка и
  устройство AotoMic не меняются. Действуют текущие настройки распознавания и
  приватности.
- При перебивании человеком ассистент уступает очередь. Предсказательная речь
  поверх человека отключена.

Это ручной импорт готовой записи, а не автоматическая передача AotoMic→PC.
Изученный отправитель `TransferManager` пока заглушка. Захват микрофона,
кольцевой буфер, pre/post-roll, AGC/VAD, транспорт пакетов, повторная доставка
и совместимость приёмника остаются отдельными этапами и здесь не тестировались.

## EN — goal and behavior

A person selects an AotoMic or other WAV recording in the Dewiar chat and reviews
the transcript before sending it to the assistant.

- WAV selection asks for confirmation and warns that a remote recognizer receives
the audio.
- Only uncompressed PCM WAV is accepted: 16-bit, mono/stereo, 8–48 kHz, up to
10 MiB and five minutes. The file stays in memory, is converted to mono 16 kHz,
and split into 20-second chunks with 250 ms overlap.
- The recognizer selected in settings is used. A failure is shown; there is no
silent provider switch.
- Repeated words at chunk boundaries are trimmed. Text goes into the editable
message field and is never executed as a command. The person reviews it and
presses Send to continue.
- The adapter does not save audio, open a network listener, or modify AotoMic
firmware/device. Existing recognizer and privacy settings remain authoritative.
- When a person interrupts, the assistant yields. Predictive speech over a person
is disabled.

This is manual import of a completed recording, not automatic AotoMic-to-PC
transfer. The inspected `TransferManager` sender is a stub. Microphone capture,
ring buffer, pre/post-roll, AGC/VAD, packet transport/retry, and receiver
compatibility remain separate, untested stages.

## 中文 — 目标与行为

用户在 Dewiar 聊天中选择 AotoMic 或其他 WAV 录音，并在发送给助手之前检查
转写文本。

- 选择 WAV 后会请求确认，并说明：如果使用远程识别器，音频会发送到该服务器。
- 仅接受未压缩 PCM WAV：16 位、单声道/双声道、8–48 kHz，最大 10 MiB、5 分钟。
  文件只在内存中处理，转换为 16 kHz 单声道，并按 20 秒分块，重叠 250 毫秒。
- 使用设置中选择的识别器。失败时显示错误，不会静默切换服务。
- 删除分块边界处重复的词。文本放入可编辑输入框，不会作为命令执行；用户检查后
  按“发送”才继续。
- 适配器不会保存录音、开放网络监听端口或修改 AotoMic 固件/设备；继续遵循现有
  识别器与隐私设置。
- 用户插话时，助手让出发言顺序；禁止故意压过用户说话。

这是手动导入已完成录音，不是 AotoMic 到电脑的自动传输。检查到的
`TransferManager` 发送端仍是空实现。麦克风采集、环形缓冲区、前后音频保留、
AGC/VAD、数据包传输与重试以及接收端兼容性仍属于后续阶段，当前未测试。

## Touched files / Изменённые файлы / 修改文件

Runtime: `core/audio_ingest.py`, `core/engine_commands.py`,
`core/fork_update_policy.py`, `ui/hud.html`.
Test: `tests/audio_ingest_test.py`.

## Rollback / Откат / 回滚

Remove the WAV picker branch and `audio_file_transcribe` command, remove
`audio_file_ingest_v1`, and restore the prior build manifests. No audio storage
or data migration needs rollback. / Удалить ветку WAV в выборе файлов и команду
`audio_file_transcribe`, убрать `audio_file_ingest_v1` и восстановить предыдущие
манифесты сборки. Хранилища записей и миграции данных нет. / 删除 WAV 文件选择分支和
`audio_file_transcribe` 命令，移除 `audio_file_ingest_v1` 并恢复之前的构建清单；无需回滚
录音存储或数据迁移。
