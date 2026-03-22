<div align="center">
  <p>
    🌎 <b>中文版</b> | <a href="README.md">Versión en Español</a> | <a href="README.en.md">English</a>
  </p>

  <img src="https://img.shields.io/badge/Sear-Xena-6a00ff?style=for-the-badge&logo=search&logoColor=white" alt="searXena Logo"/>
  <h1>searXena</h1>

  <p>
    <b>Search locally, search privately, search the old way.</b>
  </p>
  
  <p>
    一个敏捷的原生元搜索引擎和高性能数据基础设施，旨在回归网络初衷。专为追求纯净搜索体验的人类以及需要绕过商业 API 密钥限制、降低开发成本的 AI 智能体而设计。
  </p>
  
  <p>
    <a href="#宣言回归初衷的搜索">宣言</a> • 
    <a href="#🥊-为什么我们在-windows-平台没有对手">无对手</a> • 
    <a href="#🤖-零摩擦的-ai-基础设施">AI 基础设施</a> • 
    <a href="#🔒-透明的隐私架构">隐私</a> • 
    <a href="#🚀-安装与使用本地模式">安装</a> • 
    <a href="#⚖️-受限许可与鸣谢">致谢</a>
  </p>
</div>

---

## 📖 宣言：回归初衷的搜索

互联网已经改变。曾经的发现工具如今充斥着广告、强制推荐算法和持续追踪。**searXena** 的诞生是为了让您重新掌控。

我们的理念是回归几十年前的网络体验：快速、基于相关文本且零噪音。
- **零噪音:** 直接的搜索结果，没有广告干扰。
- **无画像:** 我们不追踪您的搜索，也不创建商业画像。
- **技术主权:** 所有操作都在您的本地硬件上运行，消除对商业云端的依赖。

## 🥊 为什么我们在 Windows 平台没有对手？

历史上，开源隐私搜索引擎是为 Linux 设计的。searXena 通过 **100% 原生** 化打破了这一障碍。

| 特性 | 👾 所谓的"对手" (Docker / WSL2) | 👑 searXena |
| :--- | :--- | :--- |
| **Windows 架构** | 强制虚拟化 | **内核直通** (原生 Python) |
| **内存占用** | 约 1 GB 到 2 GB | **~30 MB - 60 MB** |
| **启动时间** | 缓慢 (需先加载 Docker) | **瞬间极速** (不到一秒钟) |
| **安装体验** | 复杂 (Linux 管理员命令) | **极简** (`.ps1` 自动设置脚本) |
| **Tool Calling LLM** | 需额外安装适配器 | **原生 JSON API** 首日内置 |

## 🤖 零摩擦的 AI 基础设施

对于人工智能开发者来说，searXena 消除了网络访问障碍：

*   **告别 API 密钥:** 无需再管理各种商业 API 密钥或订阅配额。searXena 是您自己的无限搜索节点。
*   **每笔查询零成本:** 即使大规模部署您的智能体系统，也无需为高额的搜索账单感到担忧。
*   **工业级数据流:** 通过我们专有的提取引擎向 LLM 提供纯净、结构化的 JSON 数据流。

## ✨ 主要功能

* 🚀 **异步并发元搜索:** 一次查询触发数十个协调的异步请求，并在 1 秒内聚合全球结果。
* 🧘 **O-ZEN Engine (阅读模式):** 内置工业级提取核心 (AGPLv3)，可在纯净界面中阅读文章和技术文档，自动拦截侵入性脚本。
* 🛡️ **激进的隐私保护:** 透明地集中请求，作为一个中性接口保护您的身份。
* 📱 **现代 UI/UX:** "太空紫"深色模式、响应式界面以及高水准动画。

## 🔒 透明的隐私架构

### 绝对 DOM 代理化
当您查询时，searXena 通过异步引擎保护您的身份。所有图像 URL 均通过内部 `/proxify` 系统，确保您的 IP 不会被直接暴露给第三方服务器。

### 地图模块: OSM (OpenStreetMap)
- **干净的地理编码**: 搜索请求首先经过后端屏蔽。
- **IP 透明化**: 为了提供交互体验，我们嵌入了引向 `openstreetmap.org` 的 `iframe`。这会导致浏览器暂时向其全球节点下载瓦片图块而表露公网 IP。OSM 是一家坚定奉行隐私至上的开放基金会，这种暴露是良性的。

### 可信资产加速 (维基百科/维基媒体)
我们将维基百科服务器识别为高信任的公共基础设施，允许直接加载其多媒体资源。这在确保流畅体验的同时，也符合 searXena 建立的内部隐私协议。

## 🚀 安装与使用 (本地模式)

1.  **克隆储存库**: `git clone https://github.com/martinezpalomera92/searXena.git`
2.  **脚本权限 (可选)**: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3.  **自动安装程序**: 在终端中执行 `.\win_setup.ps1`。
4.  **启动**: 执行 `.\run.ps1` 并打开 `http://127.0.0.1:8000`。

## ⚖️ 受限许可与鸣谢

*   **许可证:** searXena 是自由软件，采用 **GNU Affero General Public License v3.0 (AGPL-3.0)** 许可证分发。
*   **引擎鸣谢:** **O-ZEN Engine** 提取引擎是一个衍生作品，使用并适配了 Trafilatura (Copyright Adrien Barbaresi) 的处理核心，并在 AGPLv3 许可下整合，以确保用户数据主权。
*   **鸣谢:** 我们郑重向 SearXNG 项目及其隐私标准设计致敬，其架构风格深度启发了 searXena 的实现。

---
<div align="center">
  Built with ❤️ for privacy and AI sovereignty.
</div>
