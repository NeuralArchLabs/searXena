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
    <a href="#宣言-回归初衷的搜索">宣言</a> • 
    <a href="#零摩擦的-ai-基础设施">AI 基础设施</a> • 
    <a href="#主要功能">功能</a> • 
    <a href="#隐私架构">隐私</a> • 
    <a href="#安装与使用">安装</a> • 
    <a href="#受限许可与鸣谢">致谢</a>
  </p>
</div>

---

## 📖 宣言：回归初衷的搜索

互联网已经改变。曾经的发现工具如今充斥着广告、强制推荐算法和持续追踪。**searXena** 的诞生是为了让您重新掌控。

我们的理念很简单：网络应该是快速、相关且私密的。
- **零噪音:** 直接的搜索结果，没有广告干扰。
- **无画像:** 我们不追踪您的搜索，也不创建商业画像。
- **技术主权:** 所有操作都在您的本地硬件上运行，消除对商业云端的依赖。

## 🤖 零摩擦的 AI 基础设施

对于人工智能开发者来说，实时网络访问通常是一场管理的噩梦。**searXena 打破了传统障碍**:

*   **告别 API 密钥:** 无需再管理各种商业 API 密钥、订阅配额或担忧查询信用额度的枯竭。searXena 是您自己的无限搜索节点。
*   **每笔查询零成本:** 即使大规模部署您的智能体或 RAG（检索增强生成）系统，也无需为高额的搜索账单感到担忧。
*   **工业级数据流:** 向大语言模型（LLM）提供纯净、结构化且 native 的 JSON 数据，自动过滤视觉噪音和传统浏览器的系统开销。

## ✨ 主要功能

* 🚀 **异步并发元搜索:** 一次查询触发数十个协调的异步请求，并在 1 秒内聚合全球最佳结果。
* 🧘 **O-ZEN Engine (阅读模式):** 内置工业级提取核心 (AGPLv3)，可在纯净界面中阅读文章和技术文档，自动拦截侵入性脚本。
* 🤖 **AI-First 优先集成:** 预构建的 "Tool Calling" 规范模式，支持将您的 LLM 瞬间连入互联网。
* 📱 **现代动态 UI/UX:** 流畅的动画、"太空紫"深色模式以及为最高生产力设计的响应式界面。
* 🛡️ **激进的隐私保护:** 透明地集中请求，作为一个中性接口保护您的身份不被全球网络识别。

## 🛠️ 技术栈

searXena 利用极轻量级的现代技术在本地硬件上实现超流畅执行：
- **后端:** Python 与 FastAPI（高性能异步架构）。
- **提取:** `O-ZEN Engine`（经过优化的原生提取核心）。
- **网络:** 使用 `httpx` 处理极低延迟的异步、并发 HTTP/2 请求。
- **前端:** Jinja2 配合原生 JavaScript（零重型框架）。

## 🚀 安装与使用

1.  **克隆储存库**: `git clone https://github.com/martinezpalomera92/searXena.git`
2.  **环境配置**: 运行 `.\win_setup.ps1` (Windows)。
3.  **启动引擎**: 运行 `.\run.ps1`。
4.  打开 `http://127.0.0.1:8000` 即可开始真实的搜索。

## ⚖️ 受限许可与鸣谢

*   **许可证:** searXena 是自由软件，采用 **GNU Affero General Public License v3.0 (AGPL-3.0)** 许可证分发。
*   **引擎鸣谢:** **O-ZEN Engine** 提取引擎是一个衍生作品，使用并适配了 Trafilatura (Copyright Adrien Barbaresi) 的处理核心，并在 AGPLv3 许可下整合，以确保用户数据主权和专业 Copyleft 合规。
*   **鸣谢:** 我们郑重向 SearXNG 项目及其隐私标准设计致敬，其架构风格深度启发了 searXena 的实现。

---
<div align="center">
  Built with ❤️ for privacy and AI sovereignty.
</div>
