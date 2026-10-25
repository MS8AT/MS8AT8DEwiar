# PATCH-021 — Android 控制适配器

[RU](README.md) · [ENG](README.en.md) · [CH](README.zh.md)

为已有 Android 虚拟机提供 Windows 控制：经认证的 HTTPS API、CLI、SSH 包装命令及可配置的 WireGuard 路由保护。不是 Android 安装程序，不包含密钥、证书、磁盘或路由器配置。

[接口约定](INTEGRATION.md) · [提示词](PROMPT.md) · [清单](manifest.json)。先 inspect 后 test；控制测试需要 src/android_control/control-requirements.txt，依赖安装为独立步骤。

离线接口测试 PASS；本次交付未进行安装、公网入口或真实 VPN 变更。[当前 Android 模块](../../android/ANDROID-005/README.md)。
