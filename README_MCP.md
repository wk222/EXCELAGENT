# Excel智能体 MCP 服务器

将原有的Excel智能体转换为基于Model Context Protocol (MCP)的标准化服务器，提供Excel数据分析、可视化和智能问答功能。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装MCP Python SDK和相关依赖
pip install -r requirements_mcp.txt

# 或者使用uv（推荐）
uv add -r requirements_mcp.txt
```

### 2. 启动MCP服务器

#### 方法1: 使用启动脚本（推荐新手）

```bash
# 交互式启动，选择不同模式
python start_server.py
```

#### 方法2: 直接启动（推荐）

```bash
# HTTP服务器模式（推荐）
python excel_mcp_server.py --transport http

# STDIO模式（适合Claude Desktop）
python excel_mcp_server.py --transport stdio

# 开发模式（如果安装了fastmcp CLI）
fastmcp dev excel_mcp_server.py
```

#### 方法3: 自定义配置

```bash
# 自定义端口和主机
python excel_mcp_server.py --transport http --host 0.0.0.0 --port 9000

# 查看所有选项
python excel_mcp_server.py --help
```

### ⚠️ 重要提示

**如果服务器启动后卡住不动：**

1. **HTTP模式**：正常现象，服务器在等待客户端连接
   - 浏览器访问：`http://127.0.0.1:8080/mcp`
   - 使用MCP客户端连接到该地址

2. **STDIO模式**：需要MCP客户端（如Claude Desktop）连接
   - 不应该直接运行，而是配置在客户端中

3. **开发模式**：会自动打开MCP Inspector界面

### 3. 测试MCP服务器

```bash
# 自动测试模式
python test_mcp_client.py

# 交互式测试模式
python test_mcp_client.py --interactive
```

### 4. 测试功能 - Web前端（推荐新手）

#### 方法1: 一键启动Web界面

```bash
# 启动Web测试前端
python run_web_frontend.py
```

浏览器会自动打开 `http://localhost:8501`，你可以：
- 上传Excel文件或使用示例数据
- 输入分析问题（支持中文）
- 查看AI分析结果和图表
- 实时测试所有功能

#### 方法2: 手动启动

```bash
# 安装依赖（如果还没安装）
pip install streamlit openpyxl

# 启动Streamlit应用
streamlit run web_frontend.py
```

### 5. 测试功能 - 命令行客户端

```bash
# 自动测试模式
python test_mcp_client.py

# 交互式测试模式
python test_mcp_client.py --interactive
```

## 🏗️ MCP架构概览

### 核心组件

1. **Tools (工具)** - 执行具体的数据分析任务
   - `analyze_excel_data`: 分析Excel数据并回答问题
   - `get_data_summary`: 获取数据基本摘要
   - `validate_excel_data`: 验证Excel数据有效性

2. **Resources (资源)** - 提供配置和元数据
   - `excel://config`: 服务器配置信息
   - `excel://prompts`: 可用的prompt模板

3. **Prompts (提示)** - 预定义的分析模板
   - `analyze_data_prompt`: 数据分析提示模板
   - `data_visualization_prompt`: 可视化提示模板

### MCP vs 原始版本的优势

| 特性 | 原始版本 | MCP版本 |
|------|----------|---------|
| **标准化** | 自定义API | 遵循MCP标准协议 |
| **互操作性** | 独立服务 | 可与任何MCP客户端集成 |
| **开发工具** | 无 | 支持MCP Inspector等调试工具 |
| **传输方式** | HTTP | stdio/SSE/Streamable HTTP |
| **类型安全** | 基本 | Pydantic模型验证 |
| **可扩展性** | 有限 | 可轻松添加新的Tools/Resources |

## 🛠️ 使用方式

### 方式1: 使用MCP Inspector（推荐开发调试）

```bash
# 安装MCP Inspector
npm install -g @modelcontextprotocol/inspector

# 启动Inspector并连接到服务器
mcp-inspector python excel_mcp_server.py
```

### 方式2: 集成到Claude Desktop

在Claude Desktop配置文件中添加：

```json
{
  "mcpServers": {
    "excel-analyzer": {
      "command": "python",
      "args": ["path/to/excel_mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "your-api-key"
      }
    }
  }
}
```

### 方式3: 编程集成

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 连接到MCP服务器
server_params = StdioServerParameters(
    command="python",
    args=["excel_mcp_server.py"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # 调用分析工具
        result = await session.call_tool(
            "analyze_excel_data",
            arguments={
                "file_data": your_excel_data,
                "question": "分析销售趋势"
            }
        )
```

## 📊 数据格式

Excel数据需要按以下格式传递：

```python
excel_data = {
    'filename': 'data.xlsx',
    'dataframe': [
        {'列1': '值1', '列2': 100, '列3': 'A'},
        {'列1': '值2', '列2': 200, '列3': 'B'},
        # ... 更多行
    ],
    'columns': ['列1', '列2', '列3'],
    'shape': (行数, 列数),
    'dtypes': {'列1': 'object', '列2': 'int64', '列3': 'object'},
    'current_sheet': 'Sheet1',
    'sheet_names': ['Sheet1', 'Sheet2']
}
```

## 🔧 配置选项

### 环境变量

```bash
# LLM配置
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4"

# MCP配置
export MCP_LOG_LEVEL="INFO"
```

### 自定义Prompts

创建`prompts.json`文件来自定义分析提示：

```json
{
  "analysis_code_generation": "你的自定义代码生成提示...",
  "summary_generation": "你的自定义摘要生成提示..."
}
```

## 🚀 部署选项

### 1. 本地开发

```bash
# 开发模式（支持热重载）
uv run mcp dev excel_mcp_server.py
```

### 2. 生产部署

```bash
# 使用SSE传输
python excel_mcp_server.py --transport sse --port 8080

# 使用Streamable HTTP传输（推荐）
python excel_mcp_server.py --transport streamable-http --port 8080
```

### 3. Docker部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_mcp.txt .
RUN pip install -r requirements_mcp.txt

COPY excel_mcp_server.py .
COPY prompts.json .

EXPOSE 8080
CMD ["python", "excel_mcp_server.py", "--transport", "streamable-http", "--port", "8080"]
```

## 🔍 调试和监控

### 使用MCP Inspector

```bash
# 启动带调试的服务器
mcp-inspector python excel_mcp_server.py
```

### 日志配置

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 性能监控

```python
# 在工具函数中添加监控
@mcp.tool()
async def analyze_excel_data(file_data, question, ctx: Context):
    start_time = time.time()
    try:
        # 分析逻辑
        result = perform_analysis()
        await ctx.info(f"分析完成，耗时: {time.time() - start_time:.2f}秒")
        return result
    except Exception as e:
        await ctx.error(f"分析失败: {str(e)}")
        raise
```

## 🧪 测试

### 单元测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_excel_analysis.py
```

### 集成测试

```bash
# 测试MCP服务器
python test_mcp_client.py

# 交互式测试
python test_mcp_client.py --interactive
```

## 📈 扩展功能

### 添加新工具

```python
@mcp.tool()
def new_analysis_tool(data: Dict[str, Any]) -> str:
    """新的分析工具"""
    # 实现新功能
    return "分析结果"
```

### 添加新资源

```python
@mcp.resource("excel://new-resource")
def get_new_resource() -> str:
    """新资源"""
    return json.dumps({"data": "新资源数据"})
```

### 添加新提示

```python
@mcp.prompt()
def new_prompt(parameter: str) -> str:
    """新提示模板"""
    return f"基于{parameter}的新提示"
```

## 🆚 与其他方案对比

### MCP vs REST API

| 特性 | MCP | REST API |
|------|-----|----------|
| 协议标准化 | ✅ 标准化 | ❌ 自定义 |
| 类型安全 | ✅ Pydantic | ⚠️ 取决于实现 |
| 调试工具 | ✅ MCP Inspector | ⚠️ 需要自己构建 |
| AI集成 | ✅ 原生支持 | ❌ 需要额外适配 |
| 开发复杂度 | ✅ 简单 | ⚠️ 中等 |

### MCP vs gRPC

| 特性 | MCP | gRPC |
|------|-----|------|
| 学习曲线 | ✅ 平缓 | ❌ 陡峭 |
| AI生态 | ✅ 专门设计 | ❌ 通用协议 |
| 工具生态 | ✅ 丰富 | ✅ 丰富 |
| 性能 | ⚠️ 中等 | ✅ 高 |

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个MCP服务器！

## 📄 许可证

MIT License

---

## 📞 支持

如果遇到问题或需要帮助：

1. 查看[MCP官方文档](https://modelcontextprotocol.io/)
2. 提交[GitHub Issue](https://github.com/modelcontextprotocol/python-sdk/issues)
3. 加入[MCP社区讨论](https://github.com/modelcontextprotocol/python-sdk/discussions) 