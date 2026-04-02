# MCP Server for SC4S — Implementation Plan

## Overview

The MCP server will expose SC4S knowledge and capabilities to AI assistants (Claude, Cursor, etc.), enabling them to help developers create parsers, understand existing ones, run/validate tests, and navigate the SC4S codebase.

---

## Phase 1: Project Setup

### 1.1 Create `mcp/` directory in repo root

```
mcp/
  server.py          # MCP server entry point
  tools/             # Tool implementations
  resources/         # Resource handlers
  README.md
```

## Phase 2: Resources (read-only context)

These expose SC4S knowledge to the LLM as context:

| Resource URI | Description |
|---|---|
| `sc4s://docs/creating_parsers` | Full parser creation guide including filters and unit tests (from `docs/creating_parsers/`) |

---

## Phase 3: Tools (actions the LLM can take)

### 3.1 Parser discovery tools

| Tool | Description |
|---|---|
| `list_vendors` | List all vendor addons |
| `list_parsers(vendor)` | List `.conf` files for a vendor |
| `get_parser(vendor, parser_name)` | Return parser file content |
| `search_parsers(query)` | Grep for a pattern across all parser files (sourcetype, filter pattern, etc.) |

### 3.2 Test tools

| Tool | Description |
|---|---|
| `list_tests` | List all test files in `tests/` |
| `get_test(vendor_product)` | Return test file content |
| `run_tests(test_file, sc4s_host, splunk_host, ...)` | Execute `poetry run pytest` for a specific test (requires running SC4S + Splunk) |

### 3.3 Documentation tools

| Tool | Description |
|---|---|
| `get_doc(page)` | Return markdown content of any docs page |
| `search_docs(query)` | Text search across all documentation |

---

## Phase 4 (Optional): Semantic Search with RAG

The docs corpus is currently small (~10 markdown files). The tools above are sufficient for now. If the corpus grows significantly (e.g. per-vendor docs for all 92 vendors), the following options can be added.

### Option A: Local embeddings (no external API)

- Embed all docs into vectors at startup using `sentence-transformers`
- Store vectors in a `faiss` index
- `search_docs(query)` becomes a semantic vector search instead of text grep
- Runs fully locally, no API key required
- Adds ~500MB of model weight dependencies

Additional dependencies:
```toml
sentence-transformers = "*"
faiss-cpu = "*"
```

### Option B: Embeddings via API

- Same as Option A but embeddings are computed via an external API (e.g. Anthropic, OpenAI)
- Lighter local dependencies, requires API key and internet access
- Suitable if model weight dependencies are undesirable

Additional dependencies:
```toml
openai = "*"  # or anthropic = "*"
faiss-cpu = "*"
```

---

## Phase 5: Prompts (pre-built LLM workflows)

| Prompt | Description |
|---|---|
| `create_parser` | Guided flow: asks for vendor, product, log example, filter type — produces `.conf` + test file |
| `debug_parser` | Takes parser content + raw log — suggests filter fixes |
| `review_parser` | Reviews a `.conf` against SC4S conventions |

---