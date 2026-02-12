# SnliteYao

**SnliteYao 1.1.0** 是从原 Snlite fork 出来的独立版本（基于 Snlite 7.1.1），定位为更炫酷、更顺手的本地化 GenAI 聊天框架。  
依然坚持：**本地优先、轻量可改、无云锁定**。

> Local only · Streaming · Thinking trace · Multimodal · Cooler UI

---

## 1.1.0 版本亮点

- 项目名称统一升级为 **SnliteYao**
- 安装后的项目名更新为 **snliteyao**
- 启动命令更新为：`SNLYao`
- UI 全面视觉升级（Aurora 背景、玻璃拟态卡片、渐变高亮按钮）
- 保留原有核心能力：
  - Ollama 模型加载 / 卸载
  - 流式输出
  - Thinking trace 工作区
  - 图片输入
  - 文档注入（PDF/DOCX/TXT/MD）
  - 会话与归档管理
  - 中英双语与 locale 插件

---

## 环境要求

- Python **3.10+**
- 已安装并运行 **Ollama**

检查：

```bash
ollama --version
ollama list
```

---

## 安装

```bash
git clone (https://github.com/Yaoaoin/snlite-)
cd snlite-
pip install -e .
```

安装后命令：

```bash
SNLYao
```

浏览器打开：

```text
127.0.0.1:8000
```

可选环境变量：

```bash
SNLITE_HOST=127.0.0.1
SNLITE_PORT=8000
OLLAMA_BASE_URL=http://127.0.0.1:11434
```

---

## 快速说明

- **模型**：左侧选择 Provider 与 Model 后点击 Load
- **Thinking**：可选择 auto/on/off/low/medium/high
- **附件**：支持最多 3 个文件，每个不超过 6MB
- **导出**：支持导出单会话 `.md/.json` 与全量备份 `.json`

---

## 版本记录

### v1.1.0

#### Changed

- Rename: SNLite → SnliteYao（项目名、页面名、CLI 文案统一）
- CLI command: `snlite` → `SNLYao`
- Package version: `7.1.1` → `1.1.0`

#### Improved

- UI 视觉升级：
  - 更强的多层渐变背景
  - 动态 Aurora 光晕效果
  - 更明显的玻璃卡片层次
  - 更具冲击力的主按钮发光反馈

### Base

- Forked from Snlite 7.1.1
