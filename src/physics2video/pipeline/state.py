"""
Pipeline 状态定义

定义 LangGraph 状态图的共享状态 schema，包含输入、各步输出、评分与错误信息。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StepStatus(Enum):
    """步骤状态"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    HUMAN_REVIEW = "human_review"


@dataclass
class StepScore:
    """单步评分结果"""

    step_name: str
    total_score: float  # 0-100
    dimensions: dict[str, float] = field(default_factory=dict)  # 维度 -> 得分
    comments: str = ""  # 评语与扣分原因
    passed: bool = False  # 是否通过阈值


@dataclass
class AudioInfo:
    """音频信息"""

    file_path: str
    duration: float  # 秒
    text: str  # 原始文本


@dataclass
class StoryboardScene:
    """分镜场景"""

    scene_id: int
    narration: str  # 读白
    subtitle: str  # 字幕
    visual_description: str  # 画面描述
    duration: float | None = None  # 预估时长


@dataclass
class PhysicsAnalysis:
    """物理分析结果"""

    topic: str  # 考查点
    known_quantities: list[dict[str, Any]]  # 已知量 [{name, value, unit}]
    unknown_quantities: list[dict[str, Any]]  # 未知量 [{name, unit}]
    formulas: list[str]  # 核心公式列表
    diagram_elements: dict[str, Any]  # 示意图要素
    solution_steps: list[str]  # 求解步骤
    answer: str  # 最终答案


@dataclass
class PipelineState:
    """
    Pipeline 共享状态

    遵循设计文档 3.2 节的 schema 约定，每步输出写入对应字段。
    """

    # 输入
    task_id: str
    image_path: str | None = None  # 题目图片路径
    image_url: str | None = None  # 题目图片 URL
    ocr_text: str | None = None  # 可选 OCR 文本

    # 步骤 1: 物理分析
    analysis: PhysicsAnalysis | None = None

    # 步骤 2: HTML 示意图
    html_path: str | None = None
    svg_elements: dict[str, Any] | None = None  # SVG 元素数据

    # 步骤 3: 分镜
    storyboard: list[StoryboardScene] | None = None
    storyboard_md: str | None = None  # 分镜全文 Markdown

    # 步骤 4-5: TTS 与时长验证
    audio_info: list[AudioInfo] | None = None
    total_duration: float | None = None

    # 步骤 6-7: 脚手架与 Manim 代码
    scaffold_config: dict[str, Any] | None = None
    script_path: str | None = None

    # 步骤 8: 渲染输出
    video_path: str | None = None

    # 评分与状态
    scores: dict[str, StepScore] = field(default_factory=dict)  # step_name -> score
    step_status: dict[str, StepStatus] = field(default_factory=dict)
    retry_count: dict[str, int] = field(default_factory=dict)  # step_name -> count
    errors: list[str] = field(default_factory=list)

    # 配置
    max_retries: int = 2  # 每步最大重试次数
    score_threshold: float = 60.0  # 通过阈值

    def is_step_passed(self, step_name: str) -> bool:
        """检查某步是否已通过"""
        return self.step_status.get(step_name) == StepStatus.PASSED

    def can_proceed_to(self, step_name: str) -> bool:
        """检查是否可以进入某步（前置步骤都已通过）"""
        step_order = [
            "analysis",
            "diagram",
            "storyboard",
            "tts",
            "duration_check",
            "scaffold",
            "manim_code",
            "render",
        ]
        try:
            idx = step_order.index(step_name)
        except ValueError:
            return False

        for prev_step in step_order[:idx]:
            if not self.is_step_passed(prev_step):
                return False
        return True

    def record_error(self, step_name: str, error: str) -> None:
        """记录错误"""
        self.errors.append(f"[{step_name}] {error}")

    def increment_retry(self, step_name: str) -> bool:
        """增加重试计数，返回是否还可以重试"""
        current = self.retry_count.get(step_name, 0)
        self.retry_count[step_name] = current + 1
        return current + 1 <= self.max_retries

    def set_score(self, step_name: str, score: StepScore) -> None:
        """设置评分"""
        self.scores[step_name] = score
        if score.passed:
            self.step_status[step_name] = StepStatus.PASSED
        else:
            self.step_status[step_name] = StepStatus.FAILED
