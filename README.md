### 配置环境

```bash
uv venv -p 3.12
uv sync
```
**初次开发前执行（一定要执行）**
`uv run pre-commit install`

### 启动

```bash
fastmcp run bilibili_mcp_server.py:mcp
```
或
```bash
uv run bilibili_mcp_server.py
```
### 配置MCP
请参照mcp_config.json.sample
