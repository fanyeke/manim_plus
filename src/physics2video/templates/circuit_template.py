"""
电路图模板

基于要素列表生成电路 SVG 图。
"""

from dataclasses import dataclass
from typing import Any

from .svg_builder import SVGBuilder


@dataclass
class CircuitComponentElement:
    """电路元件要素"""

    component_type: str  # resistor, capacitor, battery, switch, ammeter, voltmeter, bulb
    label: str  # 标号（如 R1）
    value: str = ""  # 值（如 10Ω）
    position: tuple[float, float] | None = None
    rotation: float = 0  # 旋转角度（度）


@dataclass
class ConnectionElement:
    """连接要素"""

    from_component: str  # 起始元件标号
    to_component: str  # 目标元件标号
    from_terminal: str = "right"  # left 或 right
    to_terminal: str = "left"


# 元件符号的路径定义
COMPONENT_PATHS: dict[str, dict[str, Any]] = {
    "resistor": {
        "type": "path",
        "d": "M0,0 L10,0 L15,-10 L25,10 L35,-10 L45,10 L55,-10 L60,0 L70,0",
        "width": 70,
        "height": 20,
    },
    "capacitor": {
        "type": "lines",
        "lines": [
            (0, 0, 25, 0),
            (25, -15, 25, 15),
            (35, -15, 35, 15),
            (35, 0, 60, 0),
        ],
        "width": 60,
        "height": 30,
    },
    "battery": {
        "type": "lines",
        "lines": [
            (0, 0, 20, 0),
            (20, -15, 20, 15),
            (30, -8, 30, 8),
            (30, 0, 50, 0),
        ],
        "width": 50,
        "height": 30,
        "extra": {"text": "+", "pos": (10, -10)},
    },
    "switch": {
        "type": "compound",
        "parts": [
            {"type": "line", "coords": (0, 0, 20, 0)},
            {"type": "circle", "cx": 20, "cy": 0, "r": 3},
            {"type": "line", "coords": (20, 0, 45, -15)},
            {"type": "circle", "cx": 50, "cy": 0, "r": 3},
            {"type": "line", "coords": (50, 0, 70, 0)},
        ],
        "width": 70,
        "height": 20,
    },
    "ammeter": {
        "type": "meter",
        "symbol": "A",
        "width": 60,
        "height": 40,
    },
    "voltmeter": {
        "type": "meter",
        "symbol": "V",
        "width": 60,
        "height": 40,
    },
    "bulb": {
        "type": "compound",
        "parts": [
            {"type": "line", "coords": (0, 0, 15, 0)},
            {"type": "circle", "cx": 30, "cy": 0, "r": 15},
            {"type": "line", "coords": (20, -10, 40, 10)},
            {"type": "line", "coords": (20, 10, 40, -10)},
            {"type": "line", "coords": (45, 0, 60, 0)},
        ],
        "width": 60,
        "height": 40,
    },
}


class CircuitDiagramTemplate:
    """
    电路图模板

    根据元件和连接要素列表生成规范的电路 SVG。
    """

    def __init__(
        self,
        width: int = 600,
        height: int = 400,
        grid_size: float = 100,
    ):
        self.width = width
        self.height = height
        self.grid_size = grid_size

        # 元件位置映射
        self.component_positions: dict[str, tuple[float, float]] = {}
        self.component_sizes: dict[str, tuple[float, float]] = {}

    def generate(
        self,
        components: list[CircuitComponentElement],
        connections: list[ConnectionElement],
    ) -> SVGBuilder:
        """
        生成电路图

        Args:
            components: 元件要素列表
            connections: 连接要素列表

        Returns:
            SVGBuilder 对象
        """
        builder = SVGBuilder(self.width, self.height)

        # 添加样式
        builder.add_style("""
            .circuit-element { stroke: #333; stroke-width: 2; fill: none; }
            .circuit-label { font-size: 14px; fill: #333; }
            .circuit-value { font-size: 12px; fill: #666; }
            .circuit-wire { stroke: #333; stroke-width: 2; fill: none; }
        """)

        # 自动布局（如果没有指定位置）
        self._auto_layout(components)

        # 绘制元件
        for comp in components:
            self._draw_component(builder, comp)

        # 绘制连接线
        for conn in connections:
            self._draw_connection(builder, conn)

        return builder

    def _auto_layout(self, components: list[CircuitComponentElement]) -> None:
        """自动布局元件"""
        # 简单的网格布局
        cols = max(1, int((len(components) ** 0.5) + 0.5))
        row = 0
        col = 0

        for i, comp in enumerate(components):
            if comp.position is None:
                x = 100 + col * self.grid_size
                y = 100 + row * self.grid_size

                comp.position = (x, y)

                col += 1
                if col >= cols:
                    col = 0
                    row += 1

            self.component_positions[comp.label] = comp.position

            # 获取元件尺寸
            comp_info = COMPONENT_PATHS.get(comp.component_type, {})
            width = comp_info.get("width", 60)
            height = comp_info.get("height", 30)
            self.component_sizes[comp.label] = (width, height)

    def _draw_component(
        self,
        builder: SVGBuilder,
        comp: CircuitComponentElement,
    ) -> None:
        """绘制单个元件"""
        if comp.position is None:
            return

        x, y = comp.position
        comp_info = COMPONENT_PATHS.get(comp.component_type)

        if comp_info is None:
            # 未知元件，绘制矩形
            rect = builder.create_rect(
                x, y - 10, 60, 20,
                element_id=f"component-{comp.label}",
                stroke="#333",
                fill="none",
            )
            builder.add_to_layer("main", rect)
        elif comp_info["type"] == "path":
            # 路径类型元件
            path = builder.create_path(
                self._translate_path(comp_info["d"], x, y),
                element_id=f"component-{comp.label}",
                stroke="#333",
            )
            builder.add_to_layer("main", path)
        elif comp_info["type"] == "lines":
            # 线段组合元件
            group_children = []
            for line_coords in comp_info["lines"]:
                x1, y1, x2, y2 = line_coords
                line = builder.create_line(
                    x + x1, y + y1, x + x2, y + y2,
                    stroke="#333",
                )
                group_children.append(line)

            group = builder.create_group(
                group_children,
                element_id=f"component-{comp.label}",
            )
            builder.add_to_layer("main", group)

            # 额外元素（如电池的+号）
            if "extra" in comp_info:
                extra = comp_info["extra"]
                if "text" in extra:
                    px, py = extra["pos"]
                    text = builder.create_text(
                        x + px, y + py,
                        extra["text"],
                        font_size=12,
                    )
                    builder.add_to_layer("annotation", text)

        elif comp_info["type"] == "meter":
            # 电表类型
            r = 15
            circle = builder.create_circle(
                x + 30, y, r,
                element_id=f"component-{comp.label}",
                stroke="#333",
            )
            builder.add_to_layer("main", circle)

            # 连接线
            left_line = builder.create_line(x, y, x + 15, y, stroke="#333")
            right_line = builder.create_line(x + 45, y, x + 60, y, stroke="#333")
            builder.add_to_layer("main", left_line)
            builder.add_to_layer("main", right_line)

            # 符号
            symbol = builder.create_text(
                x + 30, y + 5,
                comp_info["symbol"],
                font_size=14,
            )
            builder.add_to_layer("annotation", symbol)

        elif comp_info["type"] == "compound":
            # 复合元件
            group_children = []
            for part in comp_info["parts"]:
                if part["type"] == "line":
                    x1, y1, x2, y2 = part["coords"]
                    line = builder.create_line(
                        x + x1, y + y1, x + x2, y + y2,
                        stroke="#333",
                    )
                    group_children.append(line)
                elif part["type"] == "circle":
                    circle = builder.create_circle(
                        x + part["cx"], y + part["cy"], part["r"],
                        stroke="#333",
                        fill="#333",
                    )
                    group_children.append(circle)

            group = builder.create_group(
                group_children,
                element_id=f"component-{comp.label}",
            )
            builder.add_to_layer("main", group)

        # 标签
        label = builder.create_text(
            x + 30, y - 20,
            comp.label,
            element_id=f"label-{comp.label}",
            font_size=14,
        )
        builder.add_to_layer("annotation", label)

        # 值
        if comp.value:
            value = builder.create_text(
                x + 30, y + 25,
                comp.value,
                font_size=12,
                fill="#666",
            )
            builder.add_to_layer("annotation", value)

    def _translate_path(self, d: str, dx: float, dy: float) -> str:
        """平移路径"""
        # 简单实现：在路径前添加 M 命令
        return f"M{dx},{dy} " + d.replace("M0,0 ", "")

    def _draw_connection(
        self,
        builder: SVGBuilder,
        conn: ConnectionElement,
    ) -> None:
        """绘制连接线"""
        from_pos = self.component_positions.get(conn.from_component)
        to_pos = self.component_positions.get(conn.to_component)

        if from_pos is None or to_pos is None:
            return

        from_size = self.component_sizes.get(conn.from_component, (60, 30))
        to_size = self.component_sizes.get(conn.to_component, (60, 30))

        # 计算端点
        if conn.from_terminal == "right":
            x1 = from_pos[0] + from_size[0]
        else:
            x1 = from_pos[0]
        y1 = from_pos[1]

        if conn.to_terminal == "left":
            x2 = to_pos[0]
        else:
            x2 = to_pos[0] + to_size[0]
        y2 = to_pos[1]

        # 绘制直角连接线
        mid_x = (x1 + x2) / 2

        path_d = f"M{x1},{y1} L{mid_x},{y1} L{mid_x},{y2} L{x2},{y2}"
        path = builder.create_path(
            path_d,
            element_id=f"wire-{conn.from_component}-{conn.to_component}",
            stroke="#333",
        )
        builder.add_to_layer("main", path)

    def generate_from_dict(self, data: dict[str, Any]) -> SVGBuilder:
        """
        从字典数据生成电路图

        数据格式（与设计文档 4.2 节一致）：
        {
            "元件": [
                {"类型": "电阻", "标号": "R1", "值": "10Ω"},
                {"类型": "电源", "标号": "E", "值": "6V"},
            ],
            "连接": [
                ("R1", "E"),
                ...
            ]
        }
        """
        # 类型映射
        type_mapping = {
            "电阻": "resistor",
            "电容": "capacitor",
            "电源": "battery",
            "电池": "battery",
            "开关": "switch",
            "安培表": "ammeter",
            "电流表": "ammeter",
            "伏特表": "voltmeter",
            "电压表": "voltmeter",
            "灯泡": "bulb",
        }

        # 解析元件
        components = []
        for c in data.get("元件", []):
            comp_type = type_mapping.get(c.get("类型", ""), "resistor")
            comp = CircuitComponentElement(
                component_type=comp_type,
                label=c.get("标号", ""),
                value=c.get("值", c.get("阻值", c.get("电压", ""))),
            )
            components.append(comp)

        # 解析连接
        connections = []
        for conn in data.get("连接", []):
            if isinstance(conn, (list, tuple)) and len(conn) >= 2:
                connections.append(ConnectionElement(
                    from_component=conn[0],
                    to_component=conn[1],
                ))

        return self.generate(components, connections)
