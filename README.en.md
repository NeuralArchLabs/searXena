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
    <a href="#why-we-have-no-rival-on-windows">No Rival</a> • 
    <a href="#frictionless-ai-infrastructure">AI Infrastructure</a> • 
    <a href="#transparent-privacy-architecture">Privacy</a> • 
    <a href="#installation-and-usage">Installation</a> • 
    <a href="#license-and-credits">Credits</a>
  </p>
</div>

---

## 📖 Manifesto: The "Old Way" Search

The internet has changed. What used to be a tool for discovery is now an ecosystem saturated with advertising, forced recommendation algorithms, and persistent tracking. **searXena** was born to give you back control.

Our philosophy is to reclaim the web from decades ago: fast, based on relevant text, and free of noise. 
- **Zero Noise:** Direct results, without ads that distract or confuse.
- **No Profiling:** We don't track your searches or create commercial profiles.
- **Technical Sovereignty:** Everything runs locally on your hardware, eliminating cloud dependencies for your daily research.

## 🥊 Why We Have No Rival on Windows?

Historically, open-source metasearch engines focused on privacy were designed for Linux. searXena breaks that barrier by being **100% native**.

| Feature | 👾 The "Rivals" (Docker / WSL2) | 👑 searXena |
| :--- | :--- | :--- |
| **Architecture** | Forced Virtualization | **Direct to Kernel** (Native Python) |
| **Memory Consumption** | ~1 GB to 2 GB | **~30 MB - 60 MB** |
| **Startup Time** | Slow (Starts Docker Engine) | **Instantaneous** (Less than 1 sec) |
| **Installation** | Complex (Sysadmin commands) | **Simple** (`.ps1` auto-setup scripts) |
| **Tool Calling LLM** | External adapters required | **Native JSON API** from day one |

## 🤖 Frictionless AI Infrastructure

For Artificial Intelligence developers, searXena eliminates web access obstacles:

*   **Goodbye to API Keys:** Forget about managing multiple API keys or subscription quotas. searXena is your own infinite search node.
*   **Zero Cost per Query:** Scale your agents and RAG systems without worrying about the bill.
*   **Industrial-Grade Data:** Delivers a clean, structured data stream (native JSON) through our proprietary extraction engine.

## ✨ Main Features

* 🚀 **Asynchronous Parallel Metasearch:** A single query triggers dozens of coordinated asynchronous requests, consolidating global results in less than 1 second.
* 🧘 **O-ZEN Engine (Reader Mode):** Built-in industrial extraction core (AGPLv3) for reading articles and technical documentation without ads or intrusive scripts.
* 🛡️ **Radical Privacy:** Transparently centralizes requests, protecting your identity from the global web.
* 📱 **Modern UI/UX:** "Space Violet" dark mode, responsive interface, and high-level animations.

## 🔒 Transparent Privacy Architecture

### Absolute DOM Proxification
When you search, searXena protects your identity through our asynchronous engine. Every returned image URL passes through our internal `/proxify` system, ensuring your IP is not exposed to external servers.

### Maps Module: OSM (OpenStreetMap)
- **Clean Geocoding**: Search requests are shielded through the backend.
- **IP Transparency**: For interactivity (zoom/drag), we inject a dynamic `iframe` from `openstreetmap.org`. This causes a temporary direct connection to download tiles, which is safe as OSM is a pro-privacy foundation without commercial trackers.

### Trusted Asset Acceleration (Wikipedia/Wikimedia)
We identify high-trust public servers (Wikipedia) for direct media resource loading, optimizing performance without sacrificing security, as these institutions do not use advertising telemetry.

## 🚀 Installation and Usage (Local Mode)

1.  **Clone the repository**: `git clone https://github.com/martinezpalomera92/searXena.git`
2.  **Script Permissions (Optional)**: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3.  **Automatic Installer**: Run `.\win_setup.ps1` in the terminal.
4.  **Start**: Run `.\run.ps1` and open `http://127.0.0.1:8000`.

## ⚖️ License and Credits

*   **License:** searXena is free software under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
*   **Engine Credits:** The **O-ZEN Engine** extraction motor is a derivative work that utilizes and adapts the processing core of [Trafilatura](https://github.com/adbar/trafilatura) (Copyright Adrien Barbaresi), integrated here under AGPLv3 to ensure user data sovereignty.
*   **Acknowledgments:** We recognize the technical foundation established by the SearXNG ecosystem, whose privacy standards have inspired this native architecture.

---
<div align="center">
  Built with ❤️ for privacy and AI sovereignty.
</div>
