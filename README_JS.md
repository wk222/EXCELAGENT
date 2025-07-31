# Excel智能体 - JavaScript前端版本

现代化的React前端 + Python MCP后端混合架构，提供优秀的用户体验和强大的数据分析能力。

## 🏗️ 架构设计

### 前端 (JavaScript/React)
- **React 18** + TypeScript - 现代化的用户界面
- **Tailwind CSS** - 响应式设计和主题支持
- **Plotly.js** - 交互式数据可视化
- **SheetJS** - Excel文件解析
- **Zustand** - 状态管理

### 后端 (Python MCP，可选)
- **Model Context Protocol** - 标准化的AI服务接口
- **Python数据科学栈** - Pandas, Plotly, NumPy
- **LLM集成** - 智能代码生成和分析
- **HTTP API** - RESTful接口供前端调用

## 🚀 快速开始

### 方式一：仅前端模式（轻量级）

```bash
# 1. 安装依赖
npm install

# 2. 启动前端
npm run dev

# 访问 http://localhost:3000
```

**功能特性（本地模式）：**
- ✅ Excel文件解析和预览
- ✅ 基础数据统计和摘要
- ✅ 简单图表生成
- ✅ 数据质量检查
- ❌ AI代码生成
- ❌ 深度数据分析

### 方式二：前后端完整模式（推荐）

```bash
# 1. 启动Python MCP后端
python excel_mcp_server_http.py --host 0.0.0.0 --port 8080

# 2. 启动前端（新终端）
npm install
npm run dev

# 3. 在设置页面启用MCP模式
# 访问 http://localhost:3000/settings
```

**功能特性（MCP模式）：**
- ✅ 所有本地模式功能
- ✅ AI驱动的代码生成
- ✅ 专业级数据分析
- ✅ 高质量Plotly图表
- ✅ 深度洞察和业务建议
- ✅ 自定义Python代码执行

## 📊 功能对比

| 功能特性 | 本地模式 | MCP模式 |
|----------|----------|---------|
| Excel文件解析 | ✅ JavaScript | ✅ JavaScript |
| 数据预览 | ✅ 基础预览 | ✅ 增强预览 |
| 数据摘要 | ✅ 简单统计 | ✅ 详细分析 |
| 图表生成 | ✅ 基础图表 | ✅ AI智能图表 |
| 代码生成 | ❌ | ✅ Python代码 |
| 深度分析 | ❌ | ✅ AI洞察 |
| 自定义代码 | ❌ | ✅ Python执行 |
| 部署复杂度 | 🟢 简单 | 🟡 中等 |
| 分析质量 | 🟡 基础 | 🟢 专业 |

## 🔧 配置说明

### MCP后端配置

```bash
# 默认配置
python excel_mcp_server_http.py

# 自定义配置
python excel_mcp_server_http.py --host 0.0.0.0 --port 8080 --debug
```

### 前端配置

在前端设置页面配置：

1. **MCP连接**
   - MCP服务器地址：`http://localhost:8080`
   - 启用MCP模式切换

2. **LLM设置**
   - API密钥和基础URL
   - 模型参数（温度、令牌数等）

## 💡 使用指南

### 基础使用流程

1. **上传文件** - 拖拽或点击上传Excel文件
2. **选择工作表** - 如果有多个工作表，选择要分析的工作表
3. **数据预览** - 查看数据结构和基本信息
4. **分阶段分析**：
   - 阶段一：数据摘要和质量检查
   - 阶段二：AI智能分析和可视化
   - 阶段三：深度洞察和业务建议

### 高级功能

#### MCP模式特有功能
- **AI代码生成** - 根据问题自动生成Python分析代码
- **智能可视化** - 根据数据特征选择最佳图表类型
- **深度分析** - 基于前序分析的深入洞察
- **自定义代码** - 直接执行Python数据分析代码

#### 通用功能
- **多工作表支持** - 快速切换和比较不同工作表
- **响应式设计** - 支持桌面和移动设备
- **主题切换** - 浅色/深色主题
- **数据导出** - CSV格式导出

## 🌐 部署指南

### 开发环境

```bash
# 克隆项目
git clone <repository-url>
cd excel-ai-agent

# 安装前端依赖
npm install

# 安装后端依赖（如果使用MCP模式）
pip install -r requirements_mcp.txt

# 启动开发服务器
npm run dev  # 前端
python excel_mcp_server_http.py  # 后端（可选）
```

### 生产环境

#### 仅前端部署
```bash
# 构建前端
npm run build

# 部署到静态文件服务器
# dist/ 目录包含所有静态文件
```

#### 完整部署
```bash
# 前端构建
npm run build

# 后端部署（使用gunicorn等WSGI服务器）
pip install gunicorn flask flask-cors
gunicorn -w 4 -b 0.0.0.0:8080 excel_mcp_server_http:app

# 前端部署到CDN/静态服务器
# 配置MCP服务器地址为后端地址
```

## 🔍 故障排除

### 常见问题

**Q: MCP连接失败？**
A: 
1. 确保Python后端正在运行：`python excel_mcp_server_http.py`
2. 检查防火墙设置
3. 验证MCP服务器地址配置

**Q: 前端显示空白？**
A:
1. 检查浏览器控制台错误
2. 确保Node.js版本 >= 16
3. 清除浏览器缓存

**Q: Excel文件上传失败？**
A:
1. 检查文件格式（仅支持.xlsx/.xls）
2. 确认文件大小 < 50MB
3. 验证文件未损坏

**Q: 图表不显示？**
A:
1. 检查Plotly.js是否正确加载
2. 确保数据格式正确
3. 查看浏览器控制台错误

### 调试模式

```bash
# 前端调试
npm run dev

# 后端调试
python excel_mcp_server_http.py --debug

# 查看详细日志
tail -f logs/app.log
```

## 📈 性能优化

### 前端优化
- 使用React.memo减少不必要的重渲染
- 图表懒加载和虚拟化
- 文件分块上传（大文件）
- 缓存分析结果

### 后端优化
- 数据分块处理
- LRU缓存分析结果
- 异步处理长时间任务
- 连接池管理

## 🛠️ 开发指南

### 添加新功能

1. **新增分析类型**
```typescript
// src/services/mcpService.ts
async newAnalysisType(fileData: any, params: any): Promise<AnalysisResult> {
  // 实现新的分析类型
}
```

2. **新增图表类型**
```typescript
// src/components/charts/ChartViewer.tsx
// 扩展支持的图表类型
```

3. **新增页面**
```typescript
// src/pages/NewPage.tsx
// 添加新的功能页面
```

### 代码规范
- 使用TypeScript严格模式
- 遵循React Hooks最佳实践
- 使用Prettier格式化代码
- ESLint检查代码质量

## 🔄 版本计划

### v2.1 (规划中)
- [ ] 实时协作分析
- [ ] 更多图表类型支持
- [ ] 数据源连接器（API/数据库）
- [ ] 分析模板库

### v2.2 (规划中)
- [ ] 机器学习模型集成
- [ ] 自动报告生成
- [ ] 数据管道构建
- [ ] 企业级权限管理

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 🔗 相关链接

- [Python版本文档](README.md)
- [MCP协议文档](README_MCP.md)
- [技术设计文档](TECHNICAL_DESIGN.md)