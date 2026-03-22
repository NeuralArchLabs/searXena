<div align="center">
  <p>
    🌎 <b>English</b> | <a href="README.md">Versión en Español</a> | <a href="README.zh.md">中文</a>
  </p>

  <img src="https://img.shields.io/badge/Sear-Xena-6a00ff?style=for-the-badge&logo=search&logoColor=white" alt="searXena Logo"/>
  <h1>searXena</h1>

  <p>
    <b>Search locally, search privately, search the old way.</b>
  </p>
  
  <p>
    An agile native metasearch engine and high-performance data infrastructure built to reclaim the useful web. Designed for humans who want relevance without ads and for AI agents that need to explore the internet without the friction of commercial API keys and their associated costs.
  </p>
  
  <p>
    <a href="#manifesto-the-old-way-search">Manifesto</a> • 
    <a href="#frictionless-ai-infrastructure">AI Infrastructure</a> • 
    <a href="#main-features">Features</a> • 
    <a href="#privacy-architecture">Privacy</a> • 
    <a href="#installation-and-usage">Installation</a> • 
    <a href="#license-and-credits">Credits</a>
  </p>
</div>

---

## 📖 Manifesto: The "Old Way" Search

The internet has changed. What used to be a tool for discovery is now an ecosystem saturated with advertising, forced recommendation algorithms, and persistent tracking. **searXena** was born to give you back control.

Our philosophy is simple: the web must be fast, relevant, and private. 
- **Zero Noise:** Direct results, without ads that distract or confuse.
- **No Profiling:** We don't track your searches or create commercial profiles.
- **Technical Sovereignty:** Everything runs locally on your hardware, eliminating cloud dependencies for your daily research.

## 🤖 Frictionless AI Infrastructure

For Artificial Intelligence developers, real-time web access can be a management odyssey. **searXena breaks traditional barriers**:

*   **Goodbye to API Keys:** Forget about managing multiple API keys, dynamic subscription quotas, or credit depletion for every query. searXena is your own infinite search node.
*   **Zero Cost per Query:** Scale your agents and RAG (*Retrieval-Augmented Generation*) systems without worrying about the bill at the end of the month. 
*   **Industrial-Grade Data:** Delivers a clean, structured data stream (native JSON) designed to be processed by LLMs, removing visual noise and the overhead of traditional browsers.

## ✨ Main Features

* 🚀 **Asynchronous Parallel Metasearch:** A single query triggers dozens of coordinated asynchronous requests, consolidating the best global results in less than 1 second.
* 🧘 **O-ZEN Engine (Reader Mode):** Built-in industrial extraction core (AGPLv3) for reading articles and technical documentation in a pure interface, removing intrusive scripts and distractions.
* 🤖 **AI-First Integration:** Pre-built "Tool Calling" schemas to connect your LLMs to the web instantly.
* 📱 **Modern and Dynamic UI/UX:** Fluid animations, "Space Violet" dark mode, and a responsive interface designed for maximum productivity.
* 🛡️ **Radical Privacy:** Transparently centralizes requests, acting as a neutral interface that protects your identity from the global web.

## 🛠️ Tech Stack

searXena leverages modern technologies for hyper-fluid execution on local hardware:
- **Backend:** Python and FastAPI (High-performance asynchronous).
- **Extraction:** `O-ZEN Engine` (Optimized native extraction core).
- **Processing:** `httpx` for ultra-low latency parallel HTTP/2 requests.
- **Frontend:** Jinja2 with pure Vanilla JavaScript (zero heavy frameworks).

## 🚀 Installation and Usage

1.  **Clone the repository**: `git clone https://github.com/martinezpalomera92/searXena.git`
2.  **Setup environment**: Run `.\win_setup.ps1` (Windows).
3.  **Start the engine**: Run `.\run.ps1`.
4.  Open `http://127.0.0.1:8000` and start searching for real.

## ⚖️ License and Credits

*   **License:** searXena is free software under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
*   **Engine Credits:** The **O-ZEN Engine** extraction motor is a derivative work that utilizes and adapts the processing core of Trafilatura (Copyright Adrien Barbaresi), integrated here under AGPLv3 to ensure user data sovereignty and professional copyleft compliance.
*   **Acknowledgments:** We recognize the theoretical and technical foundation established by the SearXNG ecosystem, whose privacy standards have inspired the architecture of searXena.

---
<div align="center">
  Built with ❤️ for privacy and AI sovereignty.
</div>
