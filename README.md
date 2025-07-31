# Excel智能数据分析助手

一个基于Dash和LLM的智能Excel文件分析工具，支持多工作表切换、自动可视化和智能洞察生成。

## 📋 项目特色

### 🚀 核心功能
- **多工作表支持** - 自动检测和切换Excel文件中的所有工作表
- **智能数据分析** - 基于LLM的自动数据分析和代码生成
- **交互式可视化** - 自动生成多种类型的Plotly交互式图表
- **实时预览** - 工作表切换时实时更新数据预览和摘要
- **自定义图表** - 支持用户自定义创建各种类型的数据可视化
- **智能摘要** - 生成包含洞察和建议的专业分析报告

### 🎯 技术亮点
- **无数据库依赖** - 简化架构，无需复杂的数据库配置
- **响应式设计** - 基于Bootstrap的现代化UI界面
- **错误处理完善** - 完整的异常处理和用户友好的错误提示
- **代码安全执行** - 沙箱环境下安全执行生成的Python代码
- **多格式支持** - 支持.xlsx和.xls格式的Excel文件

## 🛠️ 技术栈

### 后端框架
- **Dash** - 基于Flask的Python Web框架
- **Pandas** - 数据处理和分析
- **Plotly** - 交互式数据可视化

### AI集成
- **LangChain** - LLM应用开发框架
- **OpenAI API** - GPT模型调用（支持自定义endpoint）

### 前端UI
- **Dash Bootstrap Components** - 响应式UI组件
- **Bootstrap Icons** - 图标库
- **Plotly.js** - 客户端图表渲染

## 📦 安装说明

### 环境要求
- Python 3.8+
- pip包管理器

### 快速安装
```bash
# 克隆项目
git clone https://github.com/your-username/excel-analysis-assistant.git
cd excel-analysis-assistant

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="your-api-endpoint"  # 可选
export MODEL_NAME="gpt-3.5-turbo"  # 可选

# 启动应用
python dash_app.py
```

### 依赖包列表
```txt
dash>=2.14.0
dash-bootstrap-components>=1.5.0
pandas>=1.5.0
plotly>=5.15.0
langchain-openai>=0.1.0
langchain-core>=0.2.0
openpyxl>=3.1.0
xlrd>=2.0.0
numpy>=1.24.0
```

## 🚀 使用指南

### 基本使用流程

1. **启动应用**
   ```bash
   python dash_app.py
   ```
   应用将在 http://localhost:5000 启动

2. **上传Excel文件**
   - 点击上传区域或拖拽Excel文件
   - 支持.xlsx和.xls格式
   - 自动检测所有工作表

3. **选择工作表**（多工作表文件）
   - 在下拉菜单中选择要分析的工作表
   - 实时预览数据内容和结构

4. **输入分析问题**
   ```
   示例问题：
   - "分析各地区的销售情况并创建可视化图表"
   - "找出销售额最高的产品类别"
   - "分析客户流失的主要原因"
   ```

5. **查看分析结果**
   - 自动生成的交互式图表
   - 详细的数据分析摘要
   - 专业的洞察和建议

### 高级功能

#### 自定义图表创建
1. 点击"数据操作"按钮
2. 选择数据源和坐标轴
3. 选择图表类型（柱状图、折线图、散点图等）
4. 应用筛选条件（可选）
5. 生成自定义图表

#### 数据详情查看
- 点击"查看数据详情"查看完整的数据信息
- 包含所有工作表概览
- 数据质量和结构分析

#### 结果导出
- 下载分析详情和生成的代码
- 保存图表为高清图片
- 导出分析报告

## 📁 项目结构

```
excel-analysis-assistant/
│
├── dash_app.py              # 主应用入口
├── cn.py                    # 核心分析引擎
├── prompts.json             # LLM提示词模板
├── README.md               # 项目说明文档
├── requirements.txt        # 依赖包列表
│
├── assets/                 # 静态资源目录
│   ├── plots/             # 生成的图表存储
│   └── uploads/           # 上传文件临时存储
│
└── callback_cache/        # 应用缓存（自动生成）
```

## 🔧 配置说明

### 环境变量配置
```bash
# 必需配置
OPENAI_API_KEY=your-openai-api-key

# 可选配置
OPENAI_BASE_URL=https://api.openai.com/v1  # API基础URL
MODEL_NAME=gpt-3.5-turbo                   # 使用的模型名称
```

### 自定义LLM配置
在`cn.py`文件中修改LLM参数：
```python
llm_params = {
    "model": "your-model-name",
    "temperature": 0.8,
    "api_key": "your-api-key",
    "base_url": "your-api-endpoint",
    "request_timeout": 300
}
```

## 🎨 界面预览

### 主界面
- 清洁现代的上传界面
- 实时文件预览和验证
- 直观的分析问题输入区

### 分析结果
- 多样化的交互式图表展示
- 结构化的数据分析摘要
- 专业的商业洞察和建议

### 数据操作
- 灵活的自定义图表创建
- 多维度数据筛选和分组
- 实时图表生成和预览

## 🔍 功能详解

### 多工作表支持
- **自动检测**：上传Excel文件时自动识别所有工作表
- **智能切换**：下拉菜单显示每个工作表的行列数信息
- **实时更新**：切换工作表时实时更新预览和摘要信息
- **错误处理**：优雅处理损坏或空白的工作表

### 智能分析引擎
- **数据预处理**：自动处理缺失值和数据类型转换
- **智能图表选择**：根据数据特征自动选择最佳图表类型
- **多角度分析**：从分布、关联、趋势等多个角度分析数据
- **代码生成**：生成可读性强的Python分析代码

### 安全机制
- **沙箱执行**：在受控环境中执行生成的代码
- **权限限制**：限制文件系统和网络访问
- **异常捕获**：完善的错误处理和用户提示

## 🐛 常见问题

### Q: 应用启动失败？
A: 请检查：
1. Python版本是否为3.8+
2. 是否正确安装了所有依赖包
3. API密钥是否正确配置

### Q: 上传文件失败？
A: 请确认：
1. 文件格式是否为.xlsx或.xls
2. 文件是否损坏或受保护
3. 文件大小是否超过限制

### Q: 分析结果不准确？
A: 建议：
1. 检查数据质量和完整性
2. 调整分析问题的描述
3. 手动清理数据后重新分析

### Q: 图表显示异常？
A: 可能原因：
1. 浏览器兼容性问题，建议使用Chrome
2. 网络连接不稳定
3. 数据中包含特殊字符

## 🤝 贡献指南

### 开发环境设置
```bash
# 克隆开发分支
git clone -b develop https://github.com/your-username/excel-analysis-assistant.git

# 安装开发依赖
pip install -r requirements-dev.txt

# 启动开发模式
python dash_app.py
```

### 代码规范
- 遵循PEP 8编码规范
- 添加适当的注释和文档字符串
- 保持函数功能单一和模块化
- 完善的错误处理和日志记录

### 提交流程
1. Fork项目到个人仓库
2. 创建功能分支
3. 提交代码并推送
4. 创建Pull Request

## 📄 开源协议

本项目采用 MIT 开源协议，详情请参阅 [LICENSE](LICENSE) 文件。

## 📞 联系方式

- **项目主页**：https://github.com/wk222

## 🙏 致谢

感谢以下开源项目的支持：
- [Dash](https://dash.plotly.com/) - Web应用框架
- [Plotly](https://plotly.com/) - 数据可视化库
- [LangChain](https://langchain.com/) - LLM应用开发框架
- [Pandas](https://pandas.pydata.org/) - 数据分析库

---

