# PATCH-029 — Offline audio pipeline simulation / Симуляция аудиотракта / 音频链路离线模拟

## RU

Цель: быстро сравнить варианты кодирования аудио и проверить форму будущего пути
«захват → подготовка → контекст → краткий ответ → предложение уточнения», не включая
микрофон, сеть или модель.

`tools/audio_pipeline_sim.py` генерирует детерминированную пятисекундную
синтетическую voiced-like волну 16 кГц mono и сравнивает PCM16, zlib уровни 1/6/9
и μ-law 8-bit. Отчёт содержит размер, отношение к PCM, время кодирования/декодирования
и ошибку восстановления. Текст разговора является только фикстурой: скрипт не
распознаёт синтезированную волну.

Один локальный прогон на ПК:

| Вариант | Размер | От PCM | encode / decode | RMSE |
|---|---:|---:|---:|---:|
| PCM16 | 160000 B | 100% | 0.057 / 0.008 ms | 0 LSB |
| zlib PCM16 level 1 | 148915 B | 93.1% | 5.068 / 1.016 ms | 0 LSB |
| zlib PCM16 level 6 | 150853 B | 94.3% | 5.881 / 0.982 ms | 0 LSB |
| zlib PCM16 level 9 | 150853 B | 94.3% | 5.674 / 0.898 ms | 0 LSB |
| μ-law 8-bit | 80000 B | 50% | 1.870 / 1.955 ms | 83.51 LSB |

Вывод только для этой синтетической волны: zlib почти не уменьшает поток и
добавляет работу; μ-law вдвое меньше, но он с потерями. Выбрать кодек для речи
по этому опыту нельзя: нужны одни и те же реальные тестовые фразы и WER/ошибки
распознавания, а также latency p50/p95, CPU и память. Тестовые миллисекунды
зависят от машины и не являются real-time гарантией.

Диалоговый блок проверяет передачу короткого текстового контекста и предлагает
один вопрос только по уже подтверждённому тексту. Это детерминированная фикстура,
не предсказание мысли и не результат модели. Ответ не озвучивается и не выполняет
действий автоматически.

Human Memory адаптер PATCH-019 предоставляет только read-only health/recall.
Симуляция готовит пример scoped memory packet, но не сохраняет и не отправляет его.
Для записи нужна отдельная явно разрешённая функция памяти с согласием пользователя,
просмотром черновика, ограничением срока хранения и удалением. Никакой новый
модельный файл не установлен и не прогрет; ASR и AI inference — `NOT_RUN`.

Тест: `tests/audio_pipeline_sim_test.py`. Запуск: `python tools/audio_pipeline_sim.py`.

## EN

This offline experiment generates a deterministic five-second, 16 kHz mono
speech-like waveform and compares PCM16, zlib levels 1/6/9, and 8-bit μ-law.
It reports bytes, ratio, encode/decode time, and reconstruction error. The
dialogue text is a fixture; no ASR is performed. On this single synthetic input,
zlib saves only about 6–7% with lossless reconstruction, while μ-law uses half
the bytes with measurable loss. This does not select a production codec: use
identical recorded phrases and WER, p50/p95 latency, CPU, and RAM first.

The short answer and timely follow-up are deterministic fixture behavior based
only on finalized text, not model prediction. PATCH-019 Human Memory is
read-only; the simulation emits an unpersisted scoped preview packet. A write
path needs separate consent and retention controls. Model loading, ASR, live
memory writes, microphone capture, and network calls are `NOT_RUN`.

## 中文

此离线实验生成确定性的 5 秒、16 kHz 单声道类语音波形，并比较 PCM16、zlib 1/6/9
级和 8 位 μ-law。报告包含字节数、压缩比例、编码/解码时间与重建误差。对本次合成波形，
zlib 仅节省约 6–7% 且无损；μ-law 约减半但有可测失真。不能据此选生产语音编码器；
还需用相同录音比较 WER、p50/p95 延迟、CPU 和内存。

简短回答和适时追问仅由已确认文本触发，是确定性测试样例，不是模型预测。
PATCH-019 Human Memory 只有只读能力；本模拟仅生成未保存的带范围预览。写入必须单独实现
用户同意和保留期限控制。模型加载、ASR、记忆写入、真实麦克风和网络调用均为 `NOT_RUN`。

## Rollback / Откат / 回滚

Remove this simulation tool, test, feature flag and documentation. No runtime
capture or memory storage is changed. / Удалить симулятор, тест, feature-флаг и
описание; захват и память runtime не меняются. / 删除模拟器、测试、功能标记及文档；
运行时采集和记忆存储不变。
