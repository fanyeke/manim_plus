"""
LangGraph Pipeline 定义

构建物理试题转视频的状态图，实现准入、准出与严格管控。
"""

from typing import Literal

from langgraph.graph import END, StateGraph

from .state import PipelineState, StepStatus


def _should_retry_or_human(state: PipelineState, step_name: str) -> str:
    """判断失败后是重试还是转人工"""
    if state.increment_retry(step_name):
        return step_name  # 重试
    return "human_review"


def analysis_node(state: PipelineState) -> PipelineState:
    """步骤 1: 物理分析节点"""
    state.step_status["analysis"] = StepStatus.IN_PROGRESS
    # TODO: 调用多模态 LLM 进行物理分析
    # 实现时需要：
    # 1. 加载题目图片
    # 2. 调用 RAG 获取相关知识点、公式
    # 3. 调用 LLM 进行结构化分析
    # 4. 输出 PhysicsAnalysis 对象
    return state


def analysis_eval_node(state: PipelineState) -> PipelineState:
    """步骤 1 验收: 分析打分"""
    # TODO: 实现评分逻辑
    # 维度：考查点正确、公式与单位、要素列表完整、逻辑与结构
    return state


def diagram_node(state: PipelineState) -> PipelineState:
    """步骤 2: HTML 示意图生成节点"""
    state.step_status["diagram"] = StepStatus.IN_PROGRESS
    # TODO: 基于分析结果的要素列表生成 SVG
    # 使用模板引擎 + 图元库，而非让模型直接生成
    return state


def diagram_eval_node(state: PipelineState) -> PipelineState:
    """步骤 2 验收: 示意图打分"""
    # TODO: 实现评分逻辑
    # 维度：与分析一致、图元与规范、可解析与布局
    return state


def storyboard_node(state: PipelineState) -> PipelineState:
    """步骤 3: 分镜生成节点"""
    state.step_status["storyboard"] = StepStatus.IN_PROGRESS
    # TODO: 生成分镜脚本
    # 包含读白、字幕、画面描述
    return state


def storyboard_eval_node(state: PipelineState) -> PipelineState:
    """步骤 3 验收: 分镜打分"""
    # TODO: 实现评分逻辑
    # 维度：内容正确性、讲解结构、表述规范、可读性与时长、幕与音频清单
    return state


def tts_node(state: PipelineState) -> PipelineState:
    """步骤 4: TTS 语音合成节点"""
    state.step_status["tts"] = StepStatus.IN_PROGRESS
    # TODO: 调用 edge-tts 生成音频
    return state


def duration_check_node(state: PipelineState) -> PipelineState:
    """步骤 5: 验证时长节点"""
    state.step_status["duration_check"] = StepStatus.IN_PROGRESS
    # TODO: 检查音频时长，确保与分镜匹配
    return state


def scaffold_node(state: PipelineState) -> PipelineState:
    """步骤 6: 脚手架配置节点"""
    state.step_status["scaffold"] = StepStatus.IN_PROGRESS
    # TODO: 生成 PhysicsScene 配置
    return state


def manim_code_node(state: PipelineState) -> PipelineState:
    """步骤 7: Manim 代码生成节点"""
    state.step_status["manim_code"] = StepStatus.IN_PROGRESS
    # TODO: 生成 Manim 脚本
    # 必须包含 calculate_physics、assert_physics、add_sound
    return state


def manim_eval_node(state: PipelineState) -> PipelineState:
    """步骤 7 验收: 代码打分"""
    # TODO: 实现评分逻辑
    # 维度：结构与检查、物理正确性、音画同步、字幕退场
    return state


def render_node(state: PipelineState) -> PipelineState:
    """步骤 8: 视频渲染节点"""
    state.step_status["render"] = StepStatus.IN_PROGRESS
    # TODO: 调用 manim render 生成视频
    return state


def render_eval_node(state: PipelineState) -> PipelineState:
    """步骤 8 验收: 成片打分"""
    # TODO: 实现评分逻辑
    # 维度：内容与音画、画面与音质
    return state


def human_review_node(state: PipelineState) -> PipelineState:
    """人工审核节点"""
    # 将任务放入人工审核队列
    for step_name, status in state.step_status.items():
        if status == StepStatus.FAILED:
            state.step_status[step_name] = StepStatus.HUMAN_REVIEW
    return state


def route_after_analysis_eval(
    state: PipelineState,
) -> Literal["diagram", "analysis", "human_review"]:
    """分析评分后的路由"""
    if state.is_step_passed("analysis"):
        return "diagram"
    return _should_retry_or_human(state, "analysis")


def route_after_diagram_eval(
    state: PipelineState,
) -> Literal["storyboard", "diagram", "human_review"]:
    """示意图评分后的路由"""
    if state.is_step_passed("diagram"):
        return "storyboard"
    return _should_retry_or_human(state, "diagram")


def route_after_storyboard_eval(
    state: PipelineState,
) -> Literal["tts", "storyboard", "human_review"]:
    """分镜评分后的路由"""
    if state.is_step_passed("storyboard"):
        return "tts"
    return _should_retry_or_human(state, "storyboard")


def route_after_manim_eval(
    state: PipelineState,
) -> Literal["render", "manim_code", "human_review"]:
    """代码评分后的路由"""
    if state.is_step_passed("manim_code"):
        return "render"
    return _should_retry_or_human(state, "manim_code")


def route_after_render_eval(
    state: PipelineState,
) -> Literal["end", "manim_code", "human_review"]:
    """成片评分后的路由"""
    if state.is_step_passed("render"):
        return "end"
    return _should_retry_or_human(state, "manim_code")


def create_physics_pipeline() -> StateGraph:
    """
    创建物理试题转视频的 LangGraph Pipeline

    遵循设计文档 3.1 节的状态图：
    物理分析 → 分析打分 → HTML示意 → 示意打分 → 分镜 → 分镜打分
    → TTS → 验证时长 → 脚手架 → Manim实现 → 代码打分 → 渲染 → 成片打分

    验收不通过时回退重试或转人工。
    """
    workflow = StateGraph(PipelineState)

    # 添加节点
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("analysis_eval", analysis_eval_node)
    workflow.add_node("diagram", diagram_node)
    workflow.add_node("diagram_eval", diagram_eval_node)
    workflow.add_node("storyboard", storyboard_node)
    workflow.add_node("storyboard_eval", storyboard_eval_node)
    workflow.add_node("tts", tts_node)
    workflow.add_node("duration_check", duration_check_node)
    workflow.add_node("scaffold", scaffold_node)
    workflow.add_node("manim_code", manim_code_node)
    workflow.add_node("manim_eval", manim_eval_node)
    workflow.add_node("render", render_node)
    workflow.add_node("render_eval", render_eval_node)
    workflow.add_node("human_review", human_review_node)

    # 设置入口
    workflow.set_entry_point("analysis")

    # 添加边 - 生成节点到验收节点
    workflow.add_edge("analysis", "analysis_eval")
    workflow.add_edge("diagram", "diagram_eval")
    workflow.add_edge("storyboard", "storyboard_eval")
    workflow.add_edge("tts", "duration_check")
    workflow.add_edge("duration_check", "scaffold")
    workflow.add_edge("scaffold", "manim_code")
    workflow.add_edge("manim_code", "manim_eval")
    workflow.add_edge("render", "render_eval")

    # 添加条件边 - 验收后的路由
    workflow.add_conditional_edges(
        "analysis_eval",
        route_after_analysis_eval,
        {
            "diagram": "diagram",
            "analysis": "analysis",
            "human_review": "human_review",
        },
    )

    workflow.add_conditional_edges(
        "diagram_eval",
        route_after_diagram_eval,
        {
            "storyboard": "storyboard",
            "diagram": "diagram",
            "human_review": "human_review",
        },
    )

    workflow.add_conditional_edges(
        "storyboard_eval",
        route_after_storyboard_eval,
        {
            "tts": "tts",
            "storyboard": "storyboard",
            "human_review": "human_review",
        },
    )

    workflow.add_conditional_edges(
        "manim_eval",
        route_after_manim_eval,
        {
            "render": "render",
            "manim_code": "manim_code",
            "human_review": "human_review",
        },
    )

    workflow.add_conditional_edges(
        "render_eval",
        route_after_render_eval,
        {
            "end": END,
            "manim_code": "manim_code",
            "human_review": "human_review",
        },
    )

    # 人工审核是终态
    workflow.add_edge("human_review", END)

    return workflow
