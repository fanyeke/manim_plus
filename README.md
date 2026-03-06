# manim_plus

manim+ 是一个基于 [Manim Community](https://www.manim.community/) 的 Python 项目，用于将高中物理试题自动转换为讲解视频。

## 项目概述

本项目旨在构建一个完整的 Pipeline，实现从物理试题图片输入到讲解视频输出的自动化流程：

1. **物理分析** - 多模态模型理解题目，提取考查点、公式、示意图要素
2. **HTML 示意图** - 基于分析结果生成结构化示意图
3. **分镜** - 生成讲解文案与分镜脚本
4. **TTS** - 文字转语音
5. **验证时长** - 校验音画时长
6. **脚手架** - 生成 Manim 代码框架
7. **Manim 实现** - 完成动画代码
8. **渲染** - 输出最终视频

## 技术栈

- **Python 3.12+**
- **Manim Community v0.20.1** - 数学动画引擎
- **LangGraph** - Pipeline 编排
- **FastAPI** - 业务 API
- **Celery + Redis** - 任务队列
- **多模态 LLM** - GPT-4o / Claude 3.5 / Gemini 等
- **RAG** - 知识库检索增强

## 快速开始

### 环境准备

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 运行示例场景

```bash
# 低画质预览（480p，快速）
manim render -ql example_scene.py ExampleScene

# 中画质（720p）
manim render -qm example_scene.py ExampleScene

# 高画质（1080p）
manim render -qh example_scene.py ExampleScene
```

输出视频位于 `media/videos/` 目录。

## 文档

- [详细设计文档](docs/design/physics2video-design.md) - 技术栈、领域特点、Pipeline 编排、验收标准

## 开发

### 代码检查

```bash
ruff check .
```

### 运行测试

```bash
python -m pytest
```

## 目录结构

```
manim_plus/
├── docs/
│   ├── design/          # 设计文档
│   ├── scoring/         # 评分标准
│   └── evolution/       # 需求演进记录
├── media/               # 渲染输出（.gitignore）
├── .venv/               # Python 虚拟环境
├── example_scene.py     # Manim 示例场景
├── requirements.txt     # Python 依赖
└── AGENTS.md           # Cursor Agent 配置
```

## 许可证

[待定]
