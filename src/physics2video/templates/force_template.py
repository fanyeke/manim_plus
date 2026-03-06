"""
受力图模板

基于要素列表生成受力分析 SVG 图。
"""

import math
from dataclasses import dataclass
from typing import Any

from .svg_builder import SVGBuilder


@dataclass
class ForceElement:
    """力要素数据"""

    name: str  # 力的名称（如 "重力"）
    symbol: str  # 符号（如 "G"）
    magnitude: str  # 大小（如 "mg", "10N"）
    direction: str  # 方向（如 "竖直向下", "水平向右", "斜向上30°"）
    color: str = "#FFD700"  # 显示颜色


@dataclass
class ObjectElement:
    """物体要素数据"""

    name: str  # 物体名称
    shape: str = "rect"  # 形状: rect, circle, triangle
    width: float = 60
    height: float = 40


# 方向到角度的映射（以向右为0°，逆时针为正）
DIRECTION_ANGLES: dict[str, float] = {
    "向右": 0,
    "水平向右": 0,
    "向上": 90,
    "竖直向上": 90,
    "向左": 180,
    "水平向左": 180,
    "向下": 270,
    "竖直向下": 270,
    "斜向右上": 45,
    "斜向左上": 135,
    "斜向左下": 225,
    "斜向右下": 315,
}


def parse_direction(direction: str) -> float:
    """
    解析方向字符串为角度

    支持格式：
    - 预定义方向：向上、向下、向左、向右、竖直向上、水平向右等
    - 角度方向：斜向上30°、与水平成45°等

    Returns:
        角度（度数），以向右为0°，逆时针为正
    """
    # 检查预定义方向
    if direction in DIRECTION_ANGLES:
        return DIRECTION_ANGLES[direction]

    # 尝试解析角度
    import re
    angle_match = re.search(r"(\d+)[°度]", direction)
    if angle_match:
        angle = float(angle_match.group(1))
        if "向上" in direction or "上" in direction:
            return angle if "向右" in direction or "右" in direction else 180 - angle
        elif "向下" in direction or "下" in direction:
            return -angle if "向右" in direction or "右" in direction else 180 + angle
        return angle

    # 默认向下
    return 270


class ForceDiagramTemplate:
    """
    受力图模板

    根据物体和力的要素列表生成规范的受力分析 SVG。
    """

    def __init__(
        self,
        width: int = 400,
        height: int = 400,
        arrow_length: float = 80,
        center_x: float | None = None,
        center_y: float | None = None,
    ):
        self.width = width
        self.height = height
        self.arrow_length = arrow_length
        self.center_x = center_x or width / 2
        self.center_y = center_y or height / 2

    def generate(
        self,
        object_elem: ObjectElement,
        forces: list[ForceElement],
    ) -> SVGBuilder:
        """
        生成受力图

        Args:
            object_elem: 物体要素
            forces: 力要素列表

        Returns:
            SVGBuilder 对象
        """
        builder = SVGBuilder(self.width, self.height)

        # 添加默认样式
        builder.add_style("""
            .force-arrow { stroke-linecap: round; }
            .force-label { font-weight: bold; }
            .object-shape { fill: rgba(200, 200, 200, 0.3); }
        """)

        # 绘制物体
        self._draw_object(builder, object_elem)

        # 绘制力
        for force in forces:
            self._draw_force(builder, force)

        return builder

    def _draw_object(self, builder: SVGBuilder, obj: ObjectElement) -> None:
        """绘制物体"""
        if obj.shape == "rect":
            rect = builder.create_rect(
                self.center_x - obj.width / 2,
                self.center_y - obj.height / 2,
                obj.width,
                obj.height,
                element_id=f"object-{obj.name}",
                fill="rgba(200, 200, 200, 0.3)",
                stroke="#333",
                stroke_width=2,
            )
            builder.add_to_layer("main", rect)

        elif obj.shape == "circle":
            circle = builder.create_circle(
                self.center_x,
                self.center_y,
                min(obj.width, obj.height) / 2,
                element_id=f"object-{obj.name}",
                fill="rgba(200, 200, 200, 0.3)",
                stroke="#333",
                stroke_width=2,
            )
            builder.add_to_layer("main", circle)

        # 物体标签
        label = builder.create_text(
            self.center_x,
            self.center_y + 5,
            obj.name,
            element_id=f"label-{obj.name}",
            font_size=14,
        )
        builder.add_to_layer("annotation", label)

    def _draw_force(self, builder: SVGBuilder, force: ForceElement) -> None:
        """绘制力矢量"""
        # 解析方向
        angle_deg = parse_direction(force.direction)
        angle_rad = math.radians(angle_deg)

        # 计算箭头端点
        # SVG 坐标系 y 轴向下，需要取负
        dx = self.arrow_length * math.cos(angle_rad)
        dy = -self.arrow_length * math.sin(angle_rad)

        x1 = self.center_x
        y1 = self.center_y
        x2 = x1 + dx
        y2 = y1 + dy

        # 创建箭头
        arrow = builder.create_arrow(
            x1, y1, x2, y2,
            element_id=f"force-{force.symbol}",
            stroke=force.color,
            stroke_width=3,
        )
        builder.add_to_layer("main", arrow)

        # 标签位置（在箭头末端外侧）
        label_offset = 15
        label_x = x2 + label_offset * math.cos(angle_rad)
        label_y = y2 - label_offset * math.sin(angle_rad)

        # 力的标签
        label_text = f"{force.symbol}"
        if force.magnitude and force.magnitude != force.symbol:
            label_text = f"{force.symbol}={force.magnitude}"

        label = builder.create_text(
            label_x, label_y,
            label_text,
            element_id=f"label-{force.symbol}",
            font_size=16,
            fill=force.color,
        )
        builder.add_to_layer("annotation", label)

    def generate_from_dict(self, data: dict[str, Any]) -> SVGBuilder:
        """
        从字典数据生成受力图

        数据格式（与设计文档 4.2 节一致）：
        {
            "物体": "木块",
            "力": [
                {"名": "重力", "符号": "G", "大小": "mg", "方向": "竖直向下"},
                {"名": "支持力", "符号": "N", "大小": "N", "方向": "竖直向上"},
            ]
        }
        """
        # 解析物体
        obj_name = data.get("物体", "物体")
        obj_shape = data.get("形状", "rect")
        object_elem = ObjectElement(name=obj_name, shape=obj_shape)

        # 解析力
        forces = []
        for f in data.get("力", []):
            force = ForceElement(
                name=f.get("名", ""),
                symbol=f.get("符号", "F"),
                magnitude=f.get("大小", ""),
                direction=f.get("方向", "向下"),
                color=f.get("颜色", "#FFD700"),
            )
            forces.append(force)

        return self.generate(object_elem, forces)


def create_standard_force_diagram(
    object_name: str = "物体",
    gravity: bool = True,
    normal: bool = False,
    friction: bool = False,
    applied: bool = False,
    friction_direction: str = "水平向左",
    applied_direction: str = "水平向右",
) -> SVGBuilder:
    """
    创建标准受力图

    Args:
        object_name: 物体名称
        gravity: 是否有重力
        normal: 是否有支持力
        friction: 是否有摩擦力
        applied: 是否有外力

    Returns:
        SVGBuilder 对象
    """
    template = ForceDiagramTemplate()

    obj = ObjectElement(name=object_name)
    forces = []

    if gravity:
        forces.append(ForceElement(
            name="重力",
            symbol="G",
            magnitude="mg",
            direction="竖直向下",
            color="#FFD700",
        ))

    if normal:
        forces.append(ForceElement(
            name="支持力",
            symbol="N",
            magnitude="N",
            direction="竖直向上",
            color="#00FF00",
        ))

    if friction:
        forces.append(ForceElement(
            name="摩擦力",
            symbol="f",
            magnitude="f",
            direction=friction_direction,
            color="#FF6B6B",
        ))

    if applied:
        forces.append(ForceElement(
            name="外力",
            symbol="F",
            magnitude="F",
            direction=applied_direction,
            color="#4ECDC4",
        ))

    return template.generate(obj, forces)
