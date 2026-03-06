"""
受力分析图元

提供力矢量和受力分析图的 Manim 组件。
"""

from dataclasses import dataclass
from typing import Any

from manim import *


@dataclass
class ForceData:
    """力的数据定义"""

    name: str  # 力的名称（如 "重力"）
    symbol: str  # 符号（如 "G"）
    magnitude: float | str  # 大小（数值或符号）
    direction: np.ndarray  # 方向（单位向量）
    color: str = YELLOW  # 显示颜色
    application_point: np.ndarray | None = None  # 作用点


class ForceVector(VGroup):
    """
    力矢量图元

    显示一个带标签的力矢量箭头。
    """

    def __init__(
        self,
        force: ForceData,
        scale: float = 1.0,
        show_label: bool = True,
        label_direction: np.ndarray | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        self.force = force
        self.scale = scale

        # 确定起点
        start = force.application_point if force.application_point is not None else ORIGIN

        # 计算终点
        length = float(force.magnitude) if isinstance(force.magnitude, (int, float)) else 1.5
        end = start + force.direction * length * scale

        # 创建箭头
        self.arrow = Arrow(
            start=start,
            end=end,
            color=force.color,
            buff=0,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.2,
        )
        self.add(self.arrow)

        # 创建标签
        if show_label:
            label_text = force.symbol
            if isinstance(force.magnitude, (int, float)):
                label_text = f"{force.symbol}={force.magnitude}"

            self.label = MathTex(label_text, color=force.color, font_size=28)

            # 标签位置
            if label_direction is not None:
                self.label.next_to(self.arrow, label_direction, buff=0.1)
            else:
                # 默认放在箭头中点的垂直方向
                mid = (start + end) / 2
                perp = np.array([-force.direction[1], force.direction[0], 0])
                self.label.move_to(mid + perp * 0.3)

            self.add(self.label)

    def animate_draw(self, scene: Scene, run_time: float = 1.0) -> None:
        """动画绘制力矢量"""
        scene.play(GrowArrow(self.arrow), run_time=run_time)
        if hasattr(self, "label"):
            scene.play(Write(self.label), run_time=0.5)


class ForceAnalysisDiagram(VGroup):
    """
    受力分析图

    显示一个物体的完整受力分析图。
    """

    def __init__(
        self,
        object_shape: VMobject | None = None,
        forces: list[ForceData] | None = None,
        object_name: str = "",
        show_object_label: bool = True,
        scale: float = 1.0,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        self.forces_data = forces or []
        self.force_vectors: list[ForceVector] = []

        # 创建物体（默认为方块）
        if object_shape is not None:
            self.object = object_shape
        else:
            self.object = Square(side_length=1.0, color=WHITE, fill_opacity=0.3)
        self.add(self.object)

        # 物体标签
        if show_object_label and object_name:
            self.object_label = Text(object_name, font_size=24)
            self.object_label.move_to(self.object.get_center())
            self.add(self.object_label)

        # 创建力矢量
        center = self.object.get_center()
        for force in self.forces_data:
            if force.application_point is None:
                force.application_point = center.copy()
            force_vec = ForceVector(force, scale=scale)
            self.force_vectors.append(force_vec)
            self.add(force_vec)

    def add_force(self, force: ForceData, scale: float = 1.0) -> ForceVector:
        """添加一个力"""
        if force.application_point is None:
            force.application_point = self.object.get_center().copy()

        force_vec = ForceVector(force, scale=scale)
        self.force_vectors.append(force_vec)
        self.forces_data.append(force)
        self.add(force_vec)
        return force_vec

    def animate_all_forces(
        self,
        scene: Scene,
        object_first: bool = True,
        force_interval: float = 0.5,
    ) -> None:
        """
        动画展示完整受力分析

        Args:
            scene: Manim 场景
            object_first: 是否先显示物体
            force_interval: 力之间的间隔时间
        """
        if object_first:
            scene.play(Create(self.object))
            if hasattr(self, "object_label"):
                scene.play(Write(self.object_label))
            scene.wait(0.3)

        for force_vec in self.force_vectors:
            force_vec.animate_draw(scene)
            scene.wait(force_interval)


def create_standard_forces(
    gravity: bool = True,
    normal: bool = False,
    friction: bool = False,
    tension: bool = False,
    applied: bool = False,
    gravity_value: float | str = "G",
    normal_value: float | str = "N",
    friction_value: float | str = "f",
    tension_value: float | str = "T",
    applied_value: float | str = "F",
    applied_direction: np.ndarray = RIGHT,
) -> list[ForceData]:
    """
    创建标准力集合

    Args:
        gravity: 是否包含重力
        normal: 是否包含支持力
        friction: 是否包含摩擦力
        tension: 是否包含拉力
        applied: 是否包含外力
        *_value: 各力的大小
        applied_direction: 外力方向

    Returns:
        力数据列表
    """
    forces = []

    if gravity:
        forces.append(ForceData(
            name="重力",
            symbol="G",
            magnitude=gravity_value,
            direction=DOWN,
            color=YELLOW,
        ))

    if normal:
        forces.append(ForceData(
            name="支持力",
            symbol="N",
            magnitude=normal_value,
            direction=UP,
            color=GREEN,
        ))

    if friction:
        forces.append(ForceData(
            name="摩擦力",
            symbol="f",
            magnitude=friction_value,
            direction=LEFT,
            color=RED,
        ))

    if tension:
        forces.append(ForceData(
            name="拉力",
            symbol="T",
            magnitude=tension_value,
            direction=UP + RIGHT,
            color=BLUE,
        ))

    if applied:
        forces.append(ForceData(
            name="外力",
            symbol="F",
            magnitude=applied_value,
            direction=applied_direction,
            color=ORANGE,
        ))

    return forces
