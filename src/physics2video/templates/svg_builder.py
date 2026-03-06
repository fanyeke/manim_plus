"""
SVG 构建器

提供 SVG 元素的创建和组装功能。
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SVGElement:
    """SVG 元素定义"""

    tag: str
    attributes: dict[str, str] = field(default_factory=dict)
    children: list["SVGElement"] = field(default_factory=list)
    text: str = ""
    element_id: str = ""  # 语义化 ID

    def to_xml(self) -> ET.Element:
        """转换为 XML 元素"""
        elem = ET.Element(self.tag, self.attributes)
        if self.element_id:
            elem.set("id", self.element_id)
        if self.text:
            elem.text = self.text
        for child in self.children:
            elem.append(child.to_xml())
        return elem


class SVGBuilder:
    """
    SVG 构建器

    用于构建结构化、分层的 SVG 图形。
    遵循设计文档 4.3 节的分层 SVG 约定：
    - 背景/坐标层
    - 主体图形层（物体、元件、轨迹）
    - 标注层（矢量、符号、单位）
    - 图例层
    """

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        viewbox: str | None = None,
    ):
        self.width = width
        self.height = height
        self.viewbox = viewbox or f"0 0 {width} {height}"

        # 分层管理
        self.layers: dict[str, list[SVGElement]] = {
            "background": [],
            "main": [],
            "annotation": [],
            "legend": [],
        }

        # 元素 ID 到层的映射
        self.element_map: dict[str, str] = {}

        # 样式定义
        self.styles: list[str] = []

        # 标记定义（如箭头）
        self.defs: list[SVGElement] = []

        self._init_default_defs()

    def _init_default_defs(self) -> None:
        """初始化默认的 SVG 定义（箭头等）"""
        # 箭头标记
        arrow_marker = SVGElement(
            tag="marker",
            attributes={
                "id": "arrowhead",
                "markerWidth": "10",
                "markerHeight": "7",
                "refX": "9",
                "refY": "3.5",
                "orient": "auto",
            },
            children=[
                SVGElement(
                    tag="polygon",
                    attributes={
                        "points": "0 0, 10 3.5, 0 7",
                        "fill": "currentColor",
                    },
                )
            ],
        )
        self.defs.append(arrow_marker)

    def add_style(self, css: str) -> None:
        """添加 CSS 样式"""
        self.styles.append(css)

    def add_to_layer(
        self,
        layer: str,
        element: SVGElement,
    ) -> None:
        """
        添加元素到指定层

        Args:
            layer: 层名称 (background, main, annotation, legend)
            element: SVG 元素
        """
        if layer not in self.layers:
            self.layers[layer] = []
        self.layers[layer].append(element)
        if element.element_id:
            self.element_map[element.element_id] = layer

    def create_rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        element_id: str = "",
        fill: str = "none",
        stroke: str = "black",
        stroke_width: float = 1,
        **kwargs: Any,
    ) -> SVGElement:
        """创建矩形"""
        attrs = {
            "x": str(x),
            "y": str(y),
            "width": str(width),
            "height": str(height),
            "fill": fill,
            "stroke": stroke,
            "stroke-width": str(stroke_width),
        }
        attrs.update({k.replace("_", "-"): str(v) for k, v in kwargs.items()})
        return SVGElement(tag="rect", attributes=attrs, element_id=element_id)

    def create_circle(
        self,
        cx: float,
        cy: float,
        r: float,
        element_id: str = "",
        fill: str = "none",
        stroke: str = "black",
        stroke_width: float = 1,
        **kwargs: Any,
    ) -> SVGElement:
        """创建圆"""
        attrs = {
            "cx": str(cx),
            "cy": str(cy),
            "r": str(r),
            "fill": fill,
            "stroke": stroke,
            "stroke-width": str(stroke_width),
        }
        attrs.update({k.replace("_", "-"): str(v) for k, v in kwargs.items()})
        return SVGElement(tag="circle", attributes=attrs, element_id=element_id)

    def create_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        element_id: str = "",
        stroke: str = "black",
        stroke_width: float = 1,
        marker_end: str = "",
        **kwargs: Any,
    ) -> SVGElement:
        """创建线段"""
        attrs = {
            "x1": str(x1),
            "y1": str(y1),
            "x2": str(x2),
            "y2": str(y2),
            "stroke": stroke,
            "stroke-width": str(stroke_width),
        }
        if marker_end:
            attrs["marker-end"] = f"url(#{marker_end})"
        attrs.update({k.replace("_", "-"): str(v) for k, v in kwargs.items()})
        return SVGElement(tag="line", attributes=attrs, element_id=element_id)

    def create_arrow(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        element_id: str = "",
        stroke: str = "black",
        stroke_width: float = 2,
        **kwargs: Any,
    ) -> SVGElement:
        """创建箭头（带箭头的线段）"""
        return self.create_line(
            x1, y1, x2, y2,
            element_id=element_id,
            stroke=stroke,
            stroke_width=stroke_width,
            marker_end="arrowhead",
            **kwargs,
        )

    def create_text(
        self,
        x: float,
        y: float,
        text: str,
        element_id: str = "",
        font_size: int = 14,
        font_family: str = "Arial",
        fill: str = "black",
        text_anchor: str = "middle",
        **kwargs: Any,
    ) -> SVGElement:
        """创建文本"""
        attrs = {
            "x": str(x),
            "y": str(y),
            "font-size": str(font_size),
            "font-family": font_family,
            "fill": fill,
            "text-anchor": text_anchor,
        }
        attrs.update({k.replace("_", "-"): str(v) for k, v in kwargs.items()})
        return SVGElement(tag="text", attributes=attrs, text=text, element_id=element_id)

    def create_path(
        self,
        d: str,
        element_id: str = "",
        fill: str = "none",
        stroke: str = "black",
        stroke_width: float = 1,
        **kwargs: Any,
    ) -> SVGElement:
        """创建路径"""
        attrs = {
            "d": d,
            "fill": fill,
            "stroke": stroke,
            "stroke-width": str(stroke_width),
        }
        attrs.update({k.replace("_", "-"): str(v) for k, v in kwargs.items()})
        return SVGElement(tag="path", attributes=attrs, element_id=element_id)

    def create_group(
        self,
        children: list[SVGElement],
        element_id: str = "",
        transform: str = "",
        **kwargs: Any,
    ) -> SVGElement:
        """创建组"""
        attrs: dict[str, str] = {}
        if transform:
            attrs["transform"] = transform
        attrs.update({k.replace("_", "-"): str(v) for k, v in kwargs.items()})
        return SVGElement(
            tag="g",
            attributes=attrs,
            children=children,
            element_id=element_id,
        )

    def build(self) -> str:
        """
        构建完整的 SVG 字符串

        Returns:
            SVG XML 字符串
        """
        # 创建根元素
        root = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(self.width),
            "height": str(self.height),
            "viewBox": self.viewbox,
        })

        # 添加样式
        if self.styles:
            style = ET.SubElement(root, "style")
            style.text = "\n".join(self.styles)

        # 添加 defs
        if self.defs:
            defs = ET.SubElement(root, "defs")
            for def_elem in self.defs:
                defs.append(def_elem.to_xml())

        # 按层顺序添加元素
        for layer_name in ["background", "main", "annotation", "legend"]:
            if self.layers[layer_name]:
                layer_group = ET.SubElement(root, "g", {"id": f"layer-{layer_name}"})
                for elem in self.layers[layer_name]:
                    layer_group.append(elem.to_xml())

        return ET.tostring(root, encoding="unicode")

    def save(self, filepath: str) -> None:
        """保存 SVG 到文件"""
        svg_content = self.build()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_content)

    def to_html(self, title: str = "Physics Diagram") -> str:
        """
        生成包含 SVG 的 HTML 文件内容

        Returns:
            HTML 字符串
        """
        svg_content = self.build()
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background-color: #f5f5f5;
        }}
        .svg-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="svg-container">
        {svg_content}
    </div>
</body>
</html>"""

    def save_html(self, filepath: str, title: str = "Physics Diagram") -> None:
        """保存为 HTML 文件"""
        html_content = self.to_html(title)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
