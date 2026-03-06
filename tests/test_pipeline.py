"""
测试 Pipeline 模块
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest


class TestPipelineState:
    """测试 Pipeline 状态"""

    def test_create_state(self):
        """测试创建状态"""
        from physics2video.pipeline.state import PipelineState

        state = PipelineState(task_id="test-001")
        assert state.task_id == "test-001"
        assert state.analysis is None
        assert state.max_retries == 2

    def test_step_status(self):
        """测试步骤状态"""
        from physics2video.pipeline.state import PipelineState, StepStatus

        state = PipelineState(task_id="test-001")
        state.step_status["analysis"] = StepStatus.PASSED

        assert state.is_step_passed("analysis")
        assert not state.is_step_passed("diagram")

    def test_can_proceed_to(self):
        """测试步骤前进条件"""
        from physics2video.pipeline.state import PipelineState, StepStatus

        state = PipelineState(task_id="test-001")

        # analysis 是第一步，没有前置条件，所以可以进入
        assert state.can_proceed_to("analysis") is True

        # 但 diagram 需要 analysis 先通过
        assert state.can_proceed_to("diagram") is False

        # 分析通过后可以进入 diagram
        state.step_status["analysis"] = StepStatus.PASSED
        assert state.can_proceed_to("diagram")
        assert not state.can_proceed_to("storyboard")  # diagram 还没通过

    def test_retry_count(self):
        """测试重试计数"""
        from physics2video.pipeline.state import PipelineState

        state = PipelineState(task_id="test-001", max_retries=2)

        assert state.increment_retry("analysis")  # 第1次，可以继续
        assert state.increment_retry("analysis")  # 第2次，可以继续
        assert not state.increment_retry("analysis")  # 第3次，超限

    def test_record_error(self):
        """测试记录错误"""
        from physics2video.pipeline.state import PipelineState

        state = PipelineState(task_id="test-001")
        state.record_error("analysis", "考查点识别错误")

        assert len(state.errors) == 1
        assert "[analysis]" in state.errors[0]


class TestStepScore:
    """测试步骤评分"""

    def test_create_score(self):
        """测试创建评分"""
        from physics2video.pipeline.state import StepScore

        score = StepScore(
            step_name="analysis",
            total_score=85.0,
            dimensions={"topic": 90.0, "formula": 80.0},
            comments="分析基本正确",
            passed=True,
        )

        assert score.step_name == "analysis"
        assert score.total_score == 85.0
        assert score.passed

    def test_set_score(self):
        """测试设置评分"""
        from physics2video.pipeline.state import PipelineState, StepScore, StepStatus

        state = PipelineState(task_id="test-001")
        score = StepScore("analysis", 75.0, passed=True)

        state.set_score("analysis", score)

        assert state.scores["analysis"] == score
        assert state.step_status["analysis"] == StepStatus.PASSED


class TestPhysicsAnalysis:
    """测试物理分析数据结构"""

    def test_create_analysis(self):
        """测试创建分析结果"""
        from physics2video.pipeline.state import PhysicsAnalysis

        analysis = PhysicsAnalysis(
            topic="牛顿第二定律",
            known_quantities=[
                {"name": "质量", "value": 2, "unit": "kg"},
                {"name": "加速度", "value": 5, "unit": "m/s²"},
            ],
            unknown_quantities=[
                {"name": "力", "unit": "N"},
            ],
            formulas=["F = ma"],
            diagram_elements={
                "物体": "木块",
                "力": [
                    {"名": "重力", "符号": "G", "方向": "竖直向下"},
                    {"名": "拉力", "符号": "F", "方向": "水平向右"},
                ],
            },
            solution_steps=[
                "根据牛顿第二定律 F = ma",
                "代入数据 F = 2 × 5 = 10N",
            ],
            answer="F = 10N",
        )

        assert analysis.topic == "牛顿第二定律"
        assert len(analysis.formulas) == 1
        assert analysis.answer == "F = 10N"


class TestScorer:
    """测试评分器"""

    def test_analysis_scorer(self):
        """测试分析评分器"""
        from physics2video.evaluation.scorer import AnalysisScorer
        from physics2video.pipeline.state import PhysicsAnalysis

        scorer = AnalysisScorer(threshold=60.0)

        # 测试完整的分析
        analysis = PhysicsAnalysis(
            topic="牛顿第二定律",
            known_quantities=[],
            unknown_quantities=[],
            formulas=["F = ma"],
            diagram_elements={"物体": "木块"},
            solution_steps=["步骤1"],
            answer="10N",
        )

        score = scorer.score(analysis)
        assert score.total_score > 0
        assert score.passed  # 应该通过

    def test_analysis_scorer_empty(self):
        """测试空分析的评分"""
        from physics2video.evaluation.scorer import AnalysisScorer

        scorer = AnalysisScorer(threshold=60.0)
        score = scorer.score(None)

        assert score.total_score == 0
        assert not score.passed

    def test_storyboard_scorer(self):
        """测试分镜评分器"""
        from physics2video.evaluation.scorer import StoryboardScorer
        from physics2video.pipeline.state import StoryboardScene

        scorer = StoryboardScorer(threshold=60.0)

        scenes = [
            StoryboardScene(1, "这是第一幕的读白", "字幕1", "画面描述1"),
            StoryboardScene(2, "这是第二幕的读白", "字幕2", "画面描述2"),
        ]

        score = scorer.score(scenes)
        assert score.total_score > 0

    def test_manim_code_scorer(self):
        """测试 Manim 代码评分器"""
        from physics2video.evaluation.scorer import ManimCodeScorer

        scorer = ManimCodeScorer(threshold=60.0)

        # 包含所有必须函数的代码
        code = """
class PhysicsDemo(PhysicsScene):
    def construct(self):
        self.calculate_physics("F=ma", "F", m=2, a=10)
        self.assert_physics(True, "物理正确")
        self.add_sound("audio.mp3")
"""

        score = scorer.score(code)
        assert score.dimensions["structure_check"] == 100.0
        assert score.passed

    def test_manim_code_scorer_missing_funcs(self):
        """测试缺少必须函数的代码评分"""
        from physics2video.evaluation.scorer import ManimCodeScorer

        scorer = ManimCodeScorer(threshold=60.0)

        # 缺少必须函数的代码
        code = """
class PhysicsDemo(Scene):
    def construct(self):
        pass
"""

        score = scorer.score(code)
        assert score.dimensions["structure_check"] == 0.0
        assert "缺少必须函数" in score.comments
