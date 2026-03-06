"""
电路图元

提供电路元件和电路图的 Manim 组件。
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from manim import *


class ComponentType(Enum):
    """电路元件类型"""

    RESISTOR = "resistor"
    CAPACITOR = "capacitor"
    INDUCTOR = "inductor"
    BATTERY = "battery"
    SWITCH = "switch"
    AMMETER = "ammeter"
    VOLTMETER = "voltmeter"
    BULB = "bulb"
    WIRE = "wire"


@dataclass
class CircuitComponentData:
    """电路元件数据"""

    component_type: ComponentType
    label: str  # 标号（如 R1）
    value: str = ""  # 值（如 10Ω）
    position: np.ndarray | None = None
    rotation: float = 0.0  # 旋转角度（弧度）


class CircuitElement(VGroup):
    """
    电路元件图元

    根据元件类型创建标准化的电路符号。
    """

    def __init__(
        self,
        component: CircuitComponentData,
        scale: float = 1.0,
        show_label: bool = True,
        show_value: bool = True,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        self.component = component
        self.scale = scale

        # 创建元件符号
        symbol = self._create_symbol(component.component_type)
        symbol.scale(scale)

        if component.rotation != 0:
            symbol.rotate(component.rotation)

        if component.position is not None:
            symbol.move_to(component.position)

        self.symbol = symbol
        self.add(symbol)

        # 标签
        if show_label and component.label:
            self.label = Text(component.label, font_size=20)
            self.label.next_to(symbol, UP, buff=0.1)
            self.add(self.label)

        # 值
        if show_value and component.value:
            self.value_text = Text(component.value, font_size=16)
            self.value_text.next_to(symbol, DOWN, buff=0.1)
            self.add(self.value_text)

    def _create_symbol(self, component_type: ComponentType) -> VMobject:
        """创建元件符号"""
        if component_type == ComponentType.RESISTOR:
            return self._create_resistor()
        elif component_type == ComponentType.CAPACITOR:
            return self._create_capacitor()
        elif component_type == ComponentType.BATTERY:
            return self._create_battery()
        elif component_type == ComponentType.SWITCH:
            return self._create_switch()
        elif component_type == ComponentType.AMMETER:
            return self._create_meter("A")
        elif component_type == ComponentType.VOLTMETER:
            return self._create_meter("V")
        elif component_type == ComponentType.BULB:
            return self._create_bulb()
        else:
            return Line(LEFT * 0.5, RIGHT * 0.5)

    def _create_resistor(self) -> VGroup:
        """创建电阻符号（锯齿形）"""
        group = VGroup()

        # 锯齿形电阻
        points = [
            LEFT * 0.6,
            LEFT * 0.4,
            LEFT * 0.3 + UP * 0.15,
            LEFT * 0.1 + DOWN * 0.15,
            RIGHT * 0.1 + UP * 0.15,
            RIGHT * 0.3 + DOWN * 0.15,
            RIGHT * 0.4,
            RIGHT * 0.6,
        ]
        resistor = VMobject()
        resistor.set_points_as_corners(points)
        resistor.set_stroke(WHITE, width=2)

        group.add(resistor)
        return group

    def _create_capacitor(self) -> VGroup:
        """创建电容符号"""
        group = VGroup()

        # 左边线
        left_wire = Line(LEFT * 0.5, LEFT * 0.1)
        # 左极板
        left_plate = Line(LEFT * 0.1 + UP * 0.2, LEFT * 0.1 + DOWN * 0.2)
        # 右极板
        right_plate = Line(RIGHT * 0.1 + UP * 0.2, RIGHT * 0.1 + DOWN * 0.2)
        # 右边线
        right_wire = Line(RIGHT * 0.1, RIGHT * 0.5)

        for item in [left_wire, left_plate, right_plate, right_wire]:
            item.set_stroke(WHITE, width=2)

        group.add(left_wire, left_plate, right_plate, right_wire)
        return group

    def _create_battery(self) -> VGroup:
        """创建电池/电源符号"""
        group = VGroup()

        # 左边线
        left_wire = Line(LEFT * 0.5, LEFT * 0.15)
        # 长线（正极）
        long_line = Line(LEFT * 0.15 + UP * 0.25, LEFT * 0.15 + DOWN * 0.25)
        # 短线（负极）
        short_line = Line(RIGHT * 0.05 + UP * 0.15, RIGHT * 0.05 + DOWN * 0.15)
        # 右边线
        right_wire = Line(RIGHT * 0.05, RIGHT * 0.5)

        for item in [left_wire, long_line, short_line, right_wire]:
            item.set_stroke(WHITE, width=2)

        # + 号
        plus = Text("+", font_size=16)
        plus.next_to(long_line, LEFT, buff=0.05)

        group.add(left_wire, long_line, short_line, right_wire, plus)
        return group

    def _create_switch(self) -> VGroup:
        """创建开关符号"""
        group = VGroup()

        # 左边线和触点
        left_wire = Line(LEFT * 0.5, LEFT * 0.2)
        left_point = Dot(LEFT * 0.2, radius=0.05)

        # 右边线和触点
        right_wire = Line(RIGHT * 0.2, RIGHT * 0.5)
        right_point = Dot(RIGHT * 0.2, radius=0.05)

        # 开关杆（斜线表示断开）
        switch_arm = Line(LEFT * 0.2, RIGHT * 0.15 + UP * 0.2)

        for item in [left_wire, right_wire, switch_arm]:
            item.set_stroke(WHITE, width=2)

        group.add(left_wire, left_point, right_wire, right_point, switch_arm)
        return group

    def _create_meter(self, symbol: str) -> VGroup:
        """创建电表符号（A: 安培表, V: 伏特表）"""
        group = VGroup()

        # 圆圈
        circle = Circle(radius=0.25, color=WHITE)

        # 符号
        label = Text(symbol, font_size=20)

        # 连接线
        left_wire = Line(LEFT * 0.5, LEFT * 0.25)
        right_wire = Line(RIGHT * 0.25, RIGHT * 0.5)

        for item in [circle, left_wire, right_wire]:
            item.set_stroke(WHITE, width=2)

        group.add(circle, label, left_wire, right_wire)
        return group

    def _create_bulb(self) -> VGroup:
        """创建灯泡符号"""
        group = VGroup()

        # 圆圈
        circle = Circle(radius=0.2, color=WHITE)

        # 交叉线
        cross1 = Line(UL * 0.14, DR * 0.14)
        cross2 = Line(UR * 0.14, DL * 0.14)

        # 连接线
        left_wire = Line(LEFT * 0.5, LEFT * 0.2)
        right_wire = Line(RIGHT * 0.2, RIGHT * 0.5)

        for item in [circle, cross1, cross2, left_wire, right_wire]:
            item.set_stroke(WHITE, width=2)

        group.add(circle, cross1, cross2, left_wire, right_wire)
        return group

    def get_left_terminal(self) -> np.ndarray:
        """获取左端点位置"""
        return self.symbol.get_left()

    def get_right_terminal(self) -> np.ndarray:
        """获取右端点位置"""
        return self.symbol.get_right()


class CircuitDiagram(VGroup):
    """
    电路图

    管理多个电路元件和连接线。
    """

    def __init__(
        self,
        components: list[CircuitComponentData] | None = None,
        connections: list[tuple[str, str]] | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        self.components_data = components or []
        self.connections_data = connections or []

        self.elements: dict[str, CircuitElement] = {}
        self.wires: list[VMobject] = []

        # 创建元件
        for comp in self.components_data:
            element = CircuitElement(comp)
            self.elements[comp.label] = element
            self.add(element)

    def add_component(
        self,
        component: CircuitComponentData,
    ) -> CircuitElement:
        """添加电路元件"""
        element = CircuitElement(component)
        self.elements[component.label] = element
        self.components_data.append(component)
        self.add(element)
        return element

    def connect(
        self,
        from_label: str,
        to_label: str,
        from_terminal: str = "right",
        to_terminal: str = "left",
    ) -> VMobject:
        """
        连接两个元件

        Args:
            from_label: 起始元件标号
            to_label: 目标元件标号
            from_terminal: 起始端点 ("left" 或 "right")
            to_terminal: 目标端点 ("left" 或 "right")

        Returns:
            连接线对象
        """
        from_elem = self.elements.get(from_label)
        to_elem = self.elements.get(to_label)

        if from_elem is None or to_elem is None:
            raise ValueError(f"元件不存在: {from_label} 或 {to_label}")

        # 获取端点
        if from_terminal == "right":
            start = from_elem.get_right_terminal()
        else:
            start = from_elem.get_left_terminal()

        if to_terminal == "left":
            end = to_elem.get_left_terminal()
        else:
            end = to_elem.get_right_terminal()

        # 创建连接线（直角连接）
        mid_x = (start[0] + end[0]) / 2
        wire = VMobject()
        wire.set_points_as_corners([
            start,
            np.array([mid_x, start[1], 0]),
            np.array([mid_x, end[1], 0]),
            end,
        ])
        wire.set_stroke(WHITE, width=2)

        self.wires.append(wire)
        self.add(wire)
        return wire

    def animate_build(
        self,
        scene: Scene,
        component_time: float = 0.5,
        wire_time: float = 0.3,
    ) -> None:
        """
        动画构建电路图

        Args:
            scene: Manim 场景
            component_time: 每个元件的动画时间
            wire_time: 每条连接线的动画时间
        """
        # 先显示元件
        for element in self.elements.values():
            scene.play(Create(element), run_time=component_time)

        # 再显示连接线
        for wire in self.wires:
            scene.play(Create(wire), run_time=wire_time)
