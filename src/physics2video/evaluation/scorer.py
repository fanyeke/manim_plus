"""
评分器实现

根据设计文档第七节的打分标准实现各步骤的评分逻辑。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ..pipeline.state import PhysicsAnalysis, StepScore, StoryboardScene


@dataclass
class ScoringDimension:
    """评分维度定义"""

    name: str
    weight: float  # 权重 (0-1)
    description: str


class BaseScorer(ABC):
    """评分器基类"""

    def __init__(self, threshold: float = 60.0):
        self.threshold = threshold
        self.dimensions: list[ScoringDimension] = []

    @abstractmethod
    def score(self, data: Any, context: dict[str, Any] | None = None) -> StepScore:
        """执行评分"""
        pass

    def _create_score(
        self,
        step_name: str,
        dimension_scores: dict[str, float],
        comments: str = "",
    ) -> StepScore:
        """创建评分结果"""
        total = 0.0
        for dim in self.dimensions:
            score = dimension_scores.get(dim.name, 0.0)
            total += score * dim.weight

        return StepScore(
            step_name=step_name,
            total_score=total,
            dimensions=dimension_scores,
            comments=comments,
            passed=total >= self.threshold,
        )


class AnalysisScorer(BaseScorer):
    """
    物理分析评分器

    评分维度（设计文档 7.2 节）：
    - 考查点正确 (高权重)
    - 公式与单位 (高权重)
    - 要素列表完整 (中权重)
    - 逻辑与结构 (中权重)
    """

    def __init__(self, threshold: float = 60.0):
        super().__init__(threshold)
        self.dimensions = [
            ScoringDimension(
                "topic_correct", 0.3, "考查点与题目设问一致，知识点属于高中范围"
            ),
            ScoringDimension(
                "formula_unit", 0.3, "公式正确、单位一致、无漏写"
            ),
            ScoringDimension(
                "elements_complete", 0.2, "示意图所需要素齐全（力、元件、轨迹等）"
            ),
            ScoringDimension(
                "logic_structure", 0.2, "已知→求→推导链清晰"
            ),
        ]

    def score(
        self,
        data: PhysicsAnalysis | None,
        context: dict[str, Any] | None = None,
    ) -> StepScore:
        """评分物理分析结果"""
        if data is None:
            return self._create_score(
                "analysis",
                {d.name: 0.0 for d in self.dimensions},
                "分析结果为空",
            )

        comments = []
        dimension_scores: dict[str, float] = {}

        # 考查点检查
        if data.topic and len(data.topic) > 0:
            dimension_scores["topic_correct"] = 80.0
        else:
            dimension_scores["topic_correct"] = 0.0
            comments.append("考查点未明确")

        # 公式检查
        if data.formulas and len(data.formulas) > 0:
            dimension_scores["formula_unit"] = 80.0
        else:
            dimension_scores["formula_unit"] = 0.0
            comments.append("缺少核心公式")

        # 要素检查
        if data.diagram_elements:
            dimension_scores["elements_complete"] = 80.0
        else:
            dimension_scores["elements_complete"] = 0.0
            comments.append("缺少示意图要素")

        # 逻辑检查
        if data.solution_steps and len(data.solution_steps) > 0:
            dimension_scores["logic_structure"] = 80.0
        else:
            dimension_scores["logic_structure"] = 0.0
            comments.append("缺少推导步骤")

        return self._create_score(
            "analysis",
            dimension_scores,
            "; ".join(comments) if comments else "分析完整",
        )


class DiagramScorer(BaseScorer):
    """
    示意图评分器

    评分维度（设计文档 7.3 节）：
    - 与分析一致 (高权重)
    - 图元与规范 (中权重)
    - 可解析与布局 (低权重)
    """

    def __init__(self, threshold: float = 60.0):
        super().__init__(threshold)
        self.dimensions = [
            ScoringDimension(
                "consistency", 0.5, "图示要素与步骤 1 要素列表一致"
            ),
            ScoringDimension(
                "primitives_standard", 0.3, "符合约定图元库与符号规范"
            ),
            ScoringDimension(
                "parsable_layout", 0.2, "SVG 合法、无重叠遮挡严重"
            ),
        ]

    def score(
        self,
        data: dict[str, Any] | None,
        context: dict[str, Any] | None = None,
    ) -> StepScore:
        """评分示意图"""
        if data is None:
            return self._create_score(
                "diagram",
                {d.name: 0.0 for d in self.dimensions},
                "示意图数据为空",
            )

        # TODO: 实现详细的示意图评分逻辑
        # 1. 检查要素是否与分析一致
        # 2. 检查图元是否来自图元库
        # 3. 验证 SVG 是否可解析

        dimension_scores = {
            "consistency": 80.0,
            "primitives_standard": 80.0,
            "parsable_layout": 80.0,
        }

        return self._create_score("diagram", dimension_scores, "")


class StoryboardScorer(BaseScorer):
    """
    分镜与讲解文案评分器

    评分维度（设计文档 7.4 节）：
    - 内容正确性 (高权重)
    - 讲解结构 (中权重)
    - 表述规范 (中权重)
    - 可读性与时长 (低权重)
    - 幕与音频清单 (必须)
    """

    def __init__(self, threshold: float = 60.0):
        super().__init__(threshold)
        self.dimensions = [
            ScoringDimension(
                "content_correct", 0.3, "与物理分析一致，无科学错误"
            ),
            ScoringDimension(
                "structure", 0.25, "先现象/题意再公式再结论；层次清晰"
            ),
            ScoringDimension(
                "expression", 0.25, "符合高中课标用语、关键量有单位"
            ),
            ScoringDimension(
                "readability", 0.1, "单幕读白长度适中，字幕与读白对应"
            ),
            ScoringDimension(
                "scene_audio_list", 0.1, "幕号连续、音频文件名规范"
            ),
        ]

    def score(
        self,
        data: list[StoryboardScene] | None,
        context: dict[str, Any] | None = None,
    ) -> StepScore:
        """评分分镜"""
        if data is None or len(data) == 0:
            return self._create_score(
                "storyboard",
                {d.name: 0.0 for d in self.dimensions},
                "分镜为空",
            )

        comments = []
        dimension_scores: dict[str, float] = {}

        # 检查场景连续性
        scene_ids = [s.scene_id for s in data]
        expected_ids = list(range(1, len(data) + 1))
        if scene_ids == expected_ids:
            dimension_scores["scene_audio_list"] = 100.0
        else:
            dimension_scores["scene_audio_list"] = 50.0
            comments.append("幕号不连续")

        # 检查读白长度
        for scene in data:
            if len(scene.narration) > 500:
                dimension_scores["readability"] = 50.0
                comments.append(f"场景 {scene.scene_id} 读白过长")
                break
        else:
            dimension_scores["readability"] = 80.0

        # TODO: 实现更详细的内容正确性、结构、表述检查
        dimension_scores["content_correct"] = 80.0
        dimension_scores["structure"] = 80.0
        dimension_scores["expression"] = 80.0

        return self._create_score(
            "storyboard",
            dimension_scores,
            "; ".join(comments) if comments else "分镜结构完整",
        )


class ManimCodeScorer(BaseScorer):
    """
    Manim 代码评分器

    评分维度（设计文档 7.5 节）：
    - 结构与检查 (高权重)
    - 物理正确性 (高权重)
    - 音画同步 (中权重)
    - 字幕退场 (中权重)
    """

    def __init__(self, threshold: float = 60.0):
        super().__init__(threshold)
        self.dimensions = [
            ScoringDimension(
                "structure_check", 0.3,
                "含 calculate_physics、assert_physics、add_sound；check 通过"
            ),
            ScoringDimension(
                "physics_correct", 0.3, "动画方向/大小与分析一致"
            ),
            ScoringDimension(
                "audio_sync", 0.2, "每幕 add_sound、画面时长 ≥ 音频时长"
            ),
            ScoringDimension(
                "subtitle_exit", 0.2, "字幕有退场、无残留"
            ),
        ]

    def score(
        self,
        data: str | None,  # 代码内容
        context: dict[str, Any] | None = None,
    ) -> StepScore:
        """评分 Manim 代码"""
        if data is None:
            return self._create_score(
                "manim_code",
                {d.name: 0.0 for d in self.dimensions},
                "代码为空",
            )

        comments = []
        dimension_scores: dict[str, float] = {}

        # 检查必须的函数
        required_funcs = ["calculate_physics", "assert_physics", "add_sound"]
        missing_funcs = [f for f in required_funcs if f not in data]

        if missing_funcs:
            dimension_scores["structure_check"] = 0.0
            comments.append(f"缺少必须函数: {', '.join(missing_funcs)}")
        else:
            dimension_scores["structure_check"] = 100.0

        # TODO: 实现更详细的检查
        # 1. 语法检查
        # 2. 物理方向/大小检查
        # 3. 音频同步检查
        # 4. 字幕退场检查

        dimension_scores["physics_correct"] = 80.0
        dimension_scores["audio_sync"] = 80.0
        dimension_scores["subtitle_exit"] = 80.0

        return self._create_score(
            "manim_code",
            dimension_scores,
            "; ".join(comments) if comments else "代码结构完整",
        )


class VideoScorer(BaseScorer):
    """
    成片评分器

    评分维度（设计文档 7.6 节）：
    - 内容与音画 (高权重)
    - 画面与音质 (低权重)
    """

    def __init__(self, threshold: float = 60.0):
        super().__init__(threshold)
        self.dimensions = [
            ScoringDimension(
                "content_audio", 0.7, "与分镜一致、无静音幕、字幕与读白一致"
            ),
            ScoringDimension(
                "quality", 0.3, "清晰可读、无爆音断音"
            ),
        ]

    def score(
        self,
        data: str | None,  # 视频路径
        context: dict[str, Any] | None = None,
    ) -> StepScore:
        """评分成片"""
        if data is None:
            return self._create_score(
                "render",
                {d.name: 0.0 for d in self.dimensions},
                "视频文件不存在",
            )

        # TODO: 实现视频评分
        # 1. 检查视频是否存在且可播放
        # 2. 检查是否有静音段
        # 3. 对比分镜检查内容一致性

        import os
        if not os.path.exists(data):
            return self._create_score(
                "render",
                {d.name: 0.0 for d in self.dimensions},
                f"视频文件不存在: {data}",
            )

        dimension_scores = {
            "content_audio": 80.0,
            "quality": 80.0,
        }

        return self._create_score("render", dimension_scores, "视频生成完成")
