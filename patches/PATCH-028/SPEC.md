# PATCH-028 — PC capture queue / Очередь захвата PC / 电脑端采集队列

## RU — поведение

Windows захватывает звук выбранного микрофона через существующий PortAudio
`RawInputStream`. Его callback должен быстро передать кадр рабочему потоку и сразу
вернуться: в нём нет распознавания, сети, записи на диск или ожидания очереди.

Раньше при полной очереди новый кадр отбрасывался, а старые оставались. Это могло
превращать задержку в устаревший звук. Теперь очередь ограничена 200 кадрами
(около 6,4 секунды при 32 мс на кадр): при переполнении удаляется самый старый
кадр, помещается самый свежий и увеличивается счётчик потерь. Предупреждение
пишется в журнал не чаще раза в 5 секунд. Очередь bounded; callback не ждёт
свободное место.

Выбор устройства, повторное обнаружение отключённого микрофона и настройки
Windows остаются в существующих механизмах Dewiar. Код не включает доступ к
микрофону Windows, не меняет аппаратное усиление и не открывает новый аудиопоток.
Проверяется только синтетическими кадрами. Физический микрофон, 10-секундное
кольцо, запись файлов, измерение реальной задержки и ASR сюда не входят.

## EN — behavior

On Windows, the selected microphone already uses PortAudio `RawInputStream`.
Its callback must hand a frame to the worker quickly and return; it must not run
recognition, network, disk recording, or wait for queue capacity.

Previously a full queue discarded the new frame and retained older ones, which
could turn overload into stale audio latency. The queue is now capped at 200
frames (about 6.4 seconds at 32 ms per frame). On overflow it removes the oldest
frame, keeps the newest, and increments a loss counter. A warning is logged no
more than once every five seconds. The queue is bounded and the callback never
waits for room.

Device selection, reconnect discovery, and Windows permissions remain with the
existing Dewiar and OS controls. This does not grant microphone permission,
change hardware gain, or open another stream. Tests use synthetic frames only;
physical microphone, 10-second history, file recording, real latency, and ASR
are outside this patch.

## 中文 — 行为

Windows 上所选麦克风继续使用现有 PortAudio `RawInputStream`。回调只需快速把音频帧
交给工作线程并返回；不得在回调中执行识别、网络传输、磁盘写入或等待队列空间。

之前队列满时会丢弃最新帧并保留旧帧，过载时可能造成音频越来越滞后。现在队列最多
保存 200 帧（每帧 32 毫秒时约 6.4 秒）。队列满后移除最旧帧、保留最新帧并增加丢帧计数；
日志警告最多每 5 秒一次。队列有上限，回调不会等待空位。

设备选择、断开后的重新发现和 Windows 权限仍由 Dewiar 现有机制及操作系统管理。本补丁
不会授予麦克风权限、修改硬件增益或打开第二条音频流。测试只使用合成帧；不包含真实麦克风、
10 秒历史缓冲、文件录音、真实延迟测量或 ASR。

## Files and test / Файлы и тест / 文件与测试

Runtime: `core/audio_queue.py`, `core/audio_io.py`.
Offline test: `tests/audio_capture_queue_test.py`.

## Rollback / Откат / 回滚

Restore the previous callback queue and remove `core/audio_queue.py`, its test,
and `audio_capture_freshness_queue_v1` from the manifests. / Восстановить прежнюю
очередь callback и удалить `core/audio_queue.py`, тест и функцию
`audio_capture_freshness_queue_v1` из манифестов. / 恢复之前的回调队列，并从清单中删除
`core/audio_queue.py`、对应测试和 `audio_capture_freshness_queue_v1`。
