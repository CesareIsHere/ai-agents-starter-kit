# AI Agents Server Template

A scalable, extensible, and production-ready template for building AI agent servers with automatic triage and domain-specialist agents.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🚀 Overview

This project provides a robust foundation for creating multi-agent AI systems. It enables you to:

- Deploy a network of specialized agents (math, history, news, utility, etc.)
- Automatically triage and route user queries to the most appropriate agent
- Easily add new agents and tools via configuration
- Scale horizontally with Docker and orchestration
- Integrate with OpenAI and other LLM providers

## 🏗️ Architecture

- **Agent Factory**: Dynamically creates agents from YAML configuration
- **Tool Loader**: Auto-discovers and registers tools
- **Triage Agent**: Entry point that routes queries to specialists
- **Specialist Agents**: Domain experts (math, history, news, etc.)
- **Persistence**: Redis (cache), PostgreSQL (long-term storage)
- **API Layer**: FastAPI endpoints for interaction

## 📁 Project Structure

```
agents-company/
├── app/
│   ├── api/                 # FastAPI endpoints
│   ├── agents/              # Agent logic
│   ├── core/                # Core (factory, config, loader)
│   ├── db/                  # Database models and connections
│   └── main.py              # FastAPI entry point
├── config/                  # YAML agent and system configs
├── tools/                   # Pluggable tool implementations
├── main.py                  # CLI test entry point
├── run_dev.py               # Dev server script
├── init_db.py               # DB initialization
├── Dockerfile               # Container definition
├── docker-compose.yml       # Service orchestration
└── requirements.txt         # Python dependencies
```

## ⚡ Quick Start

### With Docker (Recommended)

1. Copy and configure environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys
```

2. Start all services:

```bash
docker-compose up --build -d
```

3. Initialize the database (first time only):

```bash
docker-compose exec api python init_db.py
```

4. Access API docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy and configure environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Start the API:

```bash
python run_dev.py
```

4. Access API docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧩 Configuration

Agents and tools are defined in YAML under `config/agents.yaml`. Example:

```yaml
agents:
  math_tutor:
    name: "Math Tutor"
    type: "specialist"
    instructions: "You are a helpful math tutor..."
    tools: ["calculate"]
    model: "gpt-4"
    enabled: true
  triage:
    name: "Triage Agent"
    type: "orchestrator"
    instructions: "You route questions to the right specialist..."
    handoffs:
      ["math_tutor", "history_tutor", "news_researcher", "utility_agent"]
    is_default: true
    enabled: true
```

## 🔧 Adding New Agents or Tools

1. Define the agent or tool in the YAML config.
2. Implement the tool in `tools/` if needed.
3. (Optional) Add the agent to the triage handoff list.
4. Restart the service.

## 📡 API Usage

### Ask a Question

```bash
curl -X POST "http://localhost:8000/api/v1/ask" \
    -H "Content-Type: application/json" \
    -d '{
     "question": "What is 2 + 2?",
     "context": {},
     "conversation_id": "optional-id"
    }'
```

### Example Response

```json
{
  "answer": "2 + 2 equals 4. This is basic arithmetic addition...",
  "agent_used": "Math Tutor",
  "conversation_id": "uuid-here",
  "metadata": {
    "processing_time": 1.23,
    "tokens_used": 150
  }
}
```

### Other Endpoints

- `GET /api/v1/health` - Health check (API, DB, cache)
- `GET /api/v1/agents` - List available agents
- `GET /api/v1/conversations` - Conversation history
- `GET /api/v1/metrics` - Agent usage metrics
- `POST /api/v1/feedback` - Submit feedback

## 🛡️ Features

- Modular, extensible agent and tool system
- Automatic triage and handoff between agents
- Dockerized for easy deployment
- Redis caching and PostgreSQL persistence
- Structured logging and health checks
- Easy to add new agents and tools

## 🧑‍💻 Contributing

Contributions are welcome! Please open issues or pull requests. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Built with ❤️ for the AI developer community.