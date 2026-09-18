![AgentForge](https://img.shields.io/badge/AgentForge-Multi--Agent%20Framework-7c3aed?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**Multi-agent orchestration framework — compose, route, and coordinate LLM agents.**

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph User
        P[Prompt / Query]
    end
    subgraph AgentForge
        subgraph Router
            R[Intent Router]
            PL[Planner]
        end
        subgraph Agents
            A1[Research Agent]
            A2[Code Agent]
            A3[Analysis Agent]
            A4[Review Agent]
        end
        subgraph Memory
            SM[(Short-term<br/>Context Window)]
            LM[(Long-term<br/>Vector Store)]
        end
        subgraph Tools
            T1[Search]
            T2[Execute]
            T3[File I/O]
        end
    end
    P --> R
    R --> PL
    PL --> A1
    PL --> A2
    PL --> A3
    PL --> A4
    A1 <--> SM
    A2 <--> SM
    A3 <--> LM
    A4 <--> LM
    A1 --> T1
    A2 --> T2
    A3 --> T3
    A4 --> T3
```

---

## ✨ Features

- **Intent routing** — automatic agent selection based on task type
- **Multi-step planning** — decompose complex queries into agent pipelines
- **Tool use** — search, code execution, file operations
- **Memory tiers** — short-term context + long-term vector retrieval
- **Agent coordination** — review agent validates outputs before return

---

## 🚀 Quick Start

```bash
pip install agentforge
from agentforge import Forge
forge = Forge()
response = forge.run("Research X, code solution Y, analyze Z")
```

---

## 📁 Project Structure

```
AgentForge/
├── agentforge/
│   ├── core.py            # Forge orchestrator
│   ├── router.py          # Intent routing
│   ├── planner.py         # Multi-step decomposition
│   ├── agents/            # Agent implementations
│   ├── memory/            # Short + long-term memory
│   └── tools/             # Tool integrations
├── tests/
└── README.md
```

---

## 📄 License

MIT © Md Sadman Bin Masud
