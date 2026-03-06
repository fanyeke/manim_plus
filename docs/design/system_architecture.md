# physics2video 系统架构

## 概述

physics2video 是一个将高中物理试题转化为 Manim 讲解视频的系统。系统基于 LangGraph 编排 Pipeline，实现从题目图片到视频的完整流程。

## 目录结构

```
src/physics2video/
├── __init__.py
├── pipeline/           # LangGraph Pipeline 编排
│   ├── __init__.py
│   ├── state.py       # 状态定义
│   └── graph.py       # 状态图定义
├── nodes/             # Pipeline 节点实现
│   └── __init__.py
├── evaluation/        # 验收评估模块
│   ├── __init__.py
│   └── scorer.py      # 评分器实现
├── primitives/        # 物理图元库
│   ├── __init__.py
│   ├── physics_scene.py    # PhysicsScene 脚手架
│   ├── force_diagram.py    # 受力分析图元
│   ├── circuit.py          # 电路图元
│   └── motion.py           # 运动学图元
├── templates/         # SVG 模板引擎
│   ├── __init__.py
│   ├── svg_builder.py      # SVG 构建器
│   ├── force_template.py   # 受力图模板
│   └── circuit_template.py # 电路图模板
├── knowledge/         # 知识库与 RAG
│   ├── __init__.py
│   └── rag.py         # RAG 检索系统
└── utils/             # 工具模块
    ├── __init__.py
    ├── tts.py         # TTS 语音合成
    └── config.py      # 配置管理
```

## 核心模块

### 1. Pipeline 编排 (`pipeline/`)

基于 LangGraph 实现的状态图，包含 8 个主要步骤和 5 个验收节点：

```
物理分析 → 分析打分 → HTML示意 → 示意打分 → 分镜 → 分镜打分
→ TTS → 验证时长 → 脚手架 → Manim实现 → 代码打分 → 渲染 → 成片打分
```

#### 状态 Schema (`PipelineState`)

- `task_id`: 任务标识
- `image_path/url`: 题目图片
- `analysis`: 物理分析结果
- `html_path`: HTML 示意图路径
- `storyboard`: 分镜数据
- `audio_info`: TTS 音频信息
- `script_path`: Manim 脚本路径
- `video_path`: 输出视频路径
- `scores`: 各步评分
- `step_status`: 步骤状态
- `retry_count`: 重试计数

### 2. 验收评估 (`evaluation/`)

实现设计文档第七节的打分标准：

- `AnalysisScorer`: 物理分析评分（考查点、公式、要素、逻辑）
- `DiagramScorer`: 示意图评分（一致性、规范、布局）
- `StoryboardScorer`: 分镜评分（正确性、结构、表述、时长）
- `ManimCodeScorer`: 代码评分（结构、物理正确性、音画同步）
- `VideoScorer`: 成片评分（内容、画质）

### 3. 物理图元库 (`primitives/`)

#### PhysicsScene 脚手架

扩展 Manim Scene 的物理场景基类：

```python
class PhysicsScene(Scene):
    def calculate_physics(formula, result_symbol, **kwargs)  # 物理计算
    def assert_physics(condition, message)                    # 物理断言
    def add_sound(file_path, text)                           # 音频同步
    def show_subtitle(text, duration)                        # 字幕管理
```

#### 图元组件

- `ForceVector`: 力矢量
- `ForceAnalysisDiagram`: 受力分析图
- `CircuitElement`: 电路元件
- `CircuitDiagram`: 电路图
- `MotionTrajectory`: 运动轨迹
- `CoordinateSystem`: 坐标系

### 4. SVG 模板引擎 (`templates/`)

基于要素列表的 SVG 生成，减少模型幻觉：

#### SVG 分层约定

1. `background`: 背景/坐标层
2. `main`: 主体图形层（物体、元件、轨迹）
3. `annotation`: 标注层（矢量、符号、单位）
4. `legend`: 图例层

#### 模板类

- `ForceDiagramTemplate`: 从力要素列表生成受力图
- `CircuitDiagramTemplate`: 从电路要素列表生成电路图

### 5. 知识库与 RAG (`knowledge/`)

支持物理讲义、公式集、分镜范例的检索：

```python
rag = PhysicsRAG()
rag.add_knowledge(chunks)
result = rag.retrieve(query, module="力学", knowledge_type="公式")
```

预置内容：
- 高中物理常用公式（力学、电磁学）
- 知识点分类（模块、章节、题型）

## 使用示例

### 渲染 Manim 场景

```bash
# 激活虚拟环境
source .venv/bin/activate

# 渲染示例场景
manim render -ql examples/physics_demo.py NewtonSecondLawDemo
```

### 生成 SVG 示意图

```python
from physics2video.templates.force_template import create_standard_force_diagram

builder = create_standard_force_diagram(
    object_name="滑块",
    gravity=True,
    normal=True,
    friction=True,
)
builder.save_html("output/force_diagram.html")
```

### 使用 PhysicsScene

```python
from physics2video.primitives.physics_scene import PhysicsScene

class MyPhysicsDemo(PhysicsScene):
    def construct(self):
        # 定义物理量
        self.define_quantity("质量", "m", 2.0, "kg")
        
        # 计算
        F = self.calculate_physics("F=ma", "F", m=2.0, a=10.0)
        
        # 断言
        self.assert_physics(F == 20.0, "计算正确")
        
        # 动画...
```

## 下一步

1. 实现 Pipeline 节点的具体逻辑
2. 集成多模态 LLM 进行物理分析
3. 实现 TTS 音频合成
4. 完善 RAG 知识库内容
5. 添加更多物理图元
