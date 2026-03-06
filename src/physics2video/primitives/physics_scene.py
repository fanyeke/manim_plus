"""
PhysicsScene - 物理场景脚手架

提供物理讲解视频的基础场景类，包含：
- calculate_physics: 物理量计算与验证
- assert_physics: 物理约束断言
- add_sound: 音频同步
- 字幕管理
"""

from dataclasses import dataclass
from typing import Any, Callable

from manim import *


@dataclass
class PhysicsQuantity:
    """物理量定义"""

    name: str
    symbol: str
    value: float | None = None
    unit: str = ""
    vector: bool = False  # 是否为矢量
    direction: np.ndarray | None = None  # 矢量方向


@dataclass
class PhysicsConstraint:
    """物理约束定义"""

    name: str
    check_fn: Callable[[], bool]
    error_message: str


@dataclass
class AudioSegment:
    """音频片段"""

    file_path: str
    start_time: float
    duration: float
    text: str  # 对应文本


class PhysicsScene(Scene):
    """
    物理场景基类

    扩展 Manim Scene，提供物理讲解视频所需的标准化功能：
    1. 物理量管理与计算
    2. 物理约束验证
    3. 音频同步
    4. 字幕管理
    """

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

        # 物理量存储
        self.quantities: dict[str, PhysicsQuantity] = {}

        # 物理约束
        self.constraints: list[PhysicsConstraint] = []

        # 音频信息
        self.audio_segments: list[AudioSegment] = []
        self.current_audio_index: int = 0

        # 字幕管理
        self.current_subtitle: Text | None = None
        self.subtitle_position: np.ndarray = DOWN * 3

        # 场景配置
        self.scene_duration: float = 0.0

    def define_quantity(
        self,
        name: str,
        symbol: str,
        value: float | None = None,
        unit: str = "",
        vector: bool = False,
        direction: np.ndarray | None = None,
    ) -> PhysicsQuantity:
        """
        定义物理量

        Args:
            name: 物理量名称（如 "重力"）
            symbol: 符号（如 "G"）
            value: 数值
            unit: 单位（如 "N"）
            vector: 是否为矢量
            direction: 矢量方向

        Returns:
            定义的物理量对象
        """
        quantity = PhysicsQuantity(
            name=name,
            symbol=symbol,
            value=value,
            unit=unit,
            vector=vector,
            direction=direction,
        )
        self.quantities[symbol] = quantity
        return quantity

    def calculate_physics(
        self,
        formula: str,
        result_symbol: str,
        **kwargs: float,
    ) -> float:
        """
        执行物理计算

        根据公式和已知量计算结果，并存储到物理量表中。

        Args:
            formula: 计算公式（作为标识符）
            result_symbol: 结果存储的符号
            **kwargs: 已知量 {symbol: value}

        Returns:
            计算结果

        Example:
            # F = ma
            result = self.calculate_physics(
                "F=ma",
                "F",
                m=2.0,  # kg
                a=9.8,  # m/s²
            )
        """
        # 更新已知量的值
        for symbol, value in kwargs.items():
            if symbol in self.quantities:
                self.quantities[symbol].value = value
            else:
                self.define_quantity(symbol, symbol, value)

        # TODO: 实现公式解析和计算
        # 这里仅作示例，实际应解析 formula 并计算
        result = 0.0

        # 常见公式的简单实现
        if formula == "F=ma" and "m" in kwargs and "a" in kwargs:
            result = kwargs["m"] * kwargs["a"]
        elif formula == "v=v0+at" and all(k in kwargs for k in ["v0", "a", "t"]):
            result = kwargs["v0"] + kwargs["a"] * kwargs["t"]
        elif formula == "s=v0t+0.5at^2" and all(k in kwargs for k in ["v0", "a", "t"]):
            result = kwargs["v0"] * kwargs["t"] + 0.5 * kwargs["a"] * kwargs["t"] ** 2
        elif formula == "E=0.5mv^2" and "m" in kwargs and "v" in kwargs:
            result = 0.5 * kwargs["m"] * kwargs["v"] ** 2
        elif formula == "U=IR" and "I" in kwargs and "R" in kwargs:
            result = kwargs["I"] * kwargs["R"]
        elif formula == "P=UI" and "U" in kwargs and "I" in kwargs:
            result = kwargs["U"] * kwargs["I"]

        # 存储结果
        if result_symbol in self.quantities:
            self.quantities[result_symbol].value = result
        else:
            self.define_quantity(result_symbol, result_symbol, result)

        return result

    def assert_physics(
        self,
        condition: bool,
        message: str = "物理约束不满足",
    ) -> None:
        """
        断言物理约束

        用于验证动画中的物理量是否符合预期。

        Args:
            condition: 约束条件
            message: 失败时的错误信息

        Raises:
            AssertionError: 当约束不满足时
        """
        if not condition:
            raise AssertionError(f"PhysicsScene 断言失败: {message}")

    def add_constraint(
        self,
        name: str,
        check_fn: Callable[[], bool],
        error_message: str,
    ) -> None:
        """
        添加物理约束

        Args:
            name: 约束名称
            check_fn: 检查函数，返回 True 表示满足
            error_message: 不满足时的错误信息
        """
        self.constraints.append(
            PhysicsConstraint(name, check_fn, error_message)
        )

    def verify_constraints(self) -> list[str]:
        """
        验证所有物理约束

        Returns:
            失败的约束错误信息列表
        """
        errors = []
        for constraint in self.constraints:
            if not constraint.check_fn():
                errors.append(f"{constraint.name}: {constraint.error_message}")
        return errors

    def add_sound(
        self,
        file_path: str,
        text: str = "",
        gain: float = 0.0,
    ) -> float:
        """
        添加音频并获取时长

        Args:
            file_path: 音频文件路径
            text: 对应的文本（用于字幕）
            gain: 音量增益 (dB)

        Returns:
            音频时长（秒）
        """
        # 使用 Manim 的 add_sound 方法
        super().add_sound(file_path, gain=gain)

        # 获取音频时长
        try:
            from pydub import AudioSegment as PydubSegment
            audio = PydubSegment.from_file(file_path)
            duration = len(audio) / 1000.0  # 毫秒转秒
        except Exception:
            duration = 3.0  # 默认时长

        # 记录音频信息
        segment = AudioSegment(
            file_path=file_path,
            start_time=self.scene_duration,
            duration=duration,
            text=text,
        )
        self.audio_segments.append(segment)
        self.scene_duration += duration

        return duration

    def show_subtitle(
        self,
        text: str,
        duration: float | None = None,
        font_size: int = 32,
        color: str = WHITE,
        position: np.ndarray | None = None,
    ) -> None:
        """
        显示字幕

        Args:
            text: 字幕文本
            duration: 显示时长（秒），None 表示持续到下一个字幕
            font_size: 字体大小
            color: 颜色
            position: 位置，默认为底部
        """
        # 移除旧字幕
        if self.current_subtitle is not None:
            self.play(FadeOut(self.current_subtitle), run_time=0.3)

        # 创建新字幕
        pos = position if position is not None else self.subtitle_position
        subtitle = Text(text, font_size=font_size, color=color)
        subtitle.move_to(pos)

        self.current_subtitle = subtitle
        self.play(FadeIn(subtitle), run_time=0.3)

        if duration is not None:
            self.wait(duration - 0.6)  # 减去淡入淡出时间
            self.play(FadeOut(subtitle), run_time=0.3)
            self.current_subtitle = None

    def clear_subtitle(self) -> None:
        """清除当前字幕"""
        if self.current_subtitle is not None:
            self.play(FadeOut(self.current_subtitle), run_time=0.3)
            self.current_subtitle = None

    def create_formula(
        self,
        formula: str,
        use_latex: bool = True,
    ) -> MathTex | Text:
        """
        创建公式显示对象

        Args:
            formula: 公式文本或 LaTeX
            use_latex: 是否使用 LaTeX 渲染

        Returns:
            Manim 文本对象
        """
        if use_latex:
            return MathTex(formula)
        else:
            return Text(formula)

    def animate_calculation(
        self,
        formula: str,
        steps: list[str],
        position: np.ndarray = ORIGIN,
        step_duration: float = 2.0,
    ) -> None:
        """
        动画展示计算过程

        Args:
            formula: 初始公式
            steps: 计算步骤列表
            position: 显示位置
            step_duration: 每步时长
        """
        current = self.create_formula(formula)
        current.move_to(position)
        self.play(Write(current))

        for step in steps:
            next_formula = self.create_formula(step)
            next_formula.move_to(position)
            self.play(Transform(current, next_formula), run_time=step_duration)
            self.wait(0.5)

    def setup_coordinate_system(
        self,
        x_range: tuple[float, float, float] = (-5, 5, 1),
        y_range: tuple[float, float, float] = (-3, 3, 1),
        x_label: str = "x",
        y_label: str = "y",
    ) -> Axes:
        """
        设置坐标系

        Args:
            x_range: x 轴范围 (min, max, step)
            y_range: y 轴范围 (min, max, step)
            x_label: x 轴标签
            y_label: y 轴标签

        Returns:
            Manim Axes 对象
        """
        axes = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=10,
            y_length=6,
            axis_config={"include_tip": True},
        )

        x_lab = axes.get_x_axis_label(x_label)
        y_lab = axes.get_y_axis_label(y_label)

        self.play(Create(axes), Write(x_lab), Write(y_lab))

        return axes
