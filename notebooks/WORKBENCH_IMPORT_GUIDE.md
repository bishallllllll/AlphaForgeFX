# TradingAgents Workbench Import Guide (Jupyter/Lab)

Use this to debug/fix/configure the architecture in isolated parts.

## Install/activate

```bash
source /workspaces/AlphaForgeFX/.venv/bin/activate
cd /workspaces/AlphaForgeFX
pip install -e .
```

## Part 1: Bootstrap + Config

```python
from tradingagents.workbench import load_environment, get_default_config_copy, apply_runtime_config

load_environment()
cfg = get_default_config_copy()
cfg["llm_provider"] = "openai"
apply_runtime_config(cfg)
```

## Part 2: LLM Layer

```python
from tradingagents.workbench import create_client

client = create_client("openai", "gpt-5.4-mini")
llm = client.get_llm()
```

## Part 3: Data Layer

```python
from tradingagents.workbench import list_methods, list_method_vendors, call

list_methods()
list_method_vendors()
call("get_stock_data", "AAPL", "2026-01-01", "2026-01-10")
```

## Part 4: Tool Layer

```python
from tradingagents.workbench import list_tools, invoke_tool

list_tools()
invoke_tool("get_stock_data", {
    "symbol": "AAPL",
    "start_date": "2026-01-01",
    "end_date": "2026-01-10",
})
```

## Part 5: Agent Layer

```python
from tradingagents.workbench import list_factories, get_factory

list_factories()
factory = get_factory("create_market_analyst")
```

## Part 6: Graph Layer

```python
from tradingagents.workbench import create_graph

graph = create_graph(debug=False)
state, decision = graph.propagate("NVDA", "2026-01-15")
```

## Part 7: Interface Layer

```python
from tradingagents.workbench import get_cli_app

app = get_cli_app()
app
```

## Why this split

- Fast debug cycle: test one layer without booting full pipeline.
- Lower blast radius: isolate network/provider issues from graph logic.
- Stable contracts: each part has explicit importable functions.
