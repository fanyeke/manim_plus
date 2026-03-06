"""
测试 SVG 模板模块
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest


class TestSVGBuilder:
    """测试 SVG 构建器"""

    def test_create_builder(self):
        """测试创建构建器"""
        from physics2video.templates.svg_builder import SVGBuilder

        builder = SVGBuilder(width=400, height=300)
        assert builder.width == 400
        assert builder.height == 300

    def test_create_rect(self):
        """测试创建矩形"""
        from physics2video.templates.svg_builder import SVGBuilder

        builder = SVGBuilder()
        rect = builder.create_rect(10, 20, 100, 50, element_id="test-rect")

        assert rect.tag == "rect"
        assert rect.attributes["x"] == "10"
        assert rect.attributes["width"] == "100"
        assert rect.element_id == "test-rect"

    def test_create_circle(self):
        """测试创建圆"""
        from physics2video.templates.svg_builder import SVGBuilder

        builder = SVGBuilder()
        circle = builder.create_circle(100, 100, 50, element_id="test-circle")

        assert circle.tag == "circle"
        assert circle.attributes["cx"] == "100"
        assert circle.attributes["r"] == "50"

    def test_create_arrow(self):
        """测试创建箭头"""
        from physics2video.templates.svg_builder import SVGBuilder

        builder = SVGBuilder()
        arrow = builder.create_arrow(0, 0, 100, 100, element_id="test-arrow")

        assert arrow.tag == "line"
        assert "marker-end" in arrow.attributes

    def test_create_text(self):
        """测试创建文本"""
        from physics2video.templates.svg_builder import SVGBuilder

        builder = SVGBuilder()
        text = builder.create_text(50, 50, "Hello", element_id="test-text")

        assert text.tag == "text"
        assert text.text == "Hello"

    def test_add_to_layer(self):
        """测试添加到图层"""
        from physics2video.templates.svg_builder import SVGBuilder

        builder = SVGBuilder()
        rect = builder.create_rect(0, 0, 100, 100, element_id="bg-rect")
        builder.add_to_layer("background", rect)

        assert len(builder.layers["background"]) == 1
        assert builder.element_map["bg-rect"] == "background"

    def test_build_svg(self):
        """测试构建 SVG"""
        from physics2video.templates.svg_builder import SVGBuilder

        builder = SVGBuilder(width=200, height=200)
        rect = builder.create_rect(10, 10, 80, 80)
        builder.add_to_layer("main", rect)

        svg_str = builder.build()

        assert "svg" in svg_str
        assert "width=\"200\"" in svg_str
        assert "<rect" in svg_str

    def test_build_html(self):
        """测试构建 HTML"""
        from physics2video.templates.svg_builder import SVGBuilder

        builder = SVGBuilder()
        html = builder.to_html("Test Diagram")

        assert "<!DOCTYPE html>" in html
        assert "<title>Test Diagram</title>" in html
        assert "<svg" in html


class TestForceDiagramTemplate:
    """测试受力图模板"""

    def test_parse_direction(self):
        """测试方向解析"""
        from physics2video.templates.force_template import parse_direction

        assert parse_direction("向右") == 0
        assert parse_direction("向上") == 90
        assert parse_direction("竖直向上") == 90
        assert parse_direction("向左") == 180
        assert parse_direction("向下") == 270
        assert parse_direction("竖直向下") == 270

    def test_generate_force_diagram(self):
        """测试生成受力图"""
        from physics2video.templates.force_template import (
            ForceDiagramTemplate,
            ForceElement,
            ObjectElement,
        )

        template = ForceDiagramTemplate()
        obj = ObjectElement(name="木块")
        forces = [
            ForceElement("重力", "G", "mg", "竖直向下"),
            ForceElement("支持力", "N", "N", "竖直向上", color="#00FF00"),
        ]

        builder = template.generate(obj, forces)
        svg = builder.build()

        assert "force-G" in svg
        assert "force-N" in svg
        assert "object-木块" in svg

    def test_generate_from_dict(self):
        """测试从字典生成受力图"""
        from physics2video.templates.force_template import ForceDiagramTemplate

        template = ForceDiagramTemplate()
        data = {
            "物体": "小车",
            "力": [
                {"名": "重力", "符号": "G", "大小": "mg", "方向": "竖直向下"},
                {"名": "支持力", "符号": "N", "大小": "N", "方向": "竖直向上"},
                {"名": "摩擦力", "符号": "f", "大小": "μN", "方向": "水平向左"},
            ],
        }

        builder = template.generate_from_dict(data)
        svg = builder.build()

        assert "force-G" in svg
        assert "force-N" in svg
        assert "force-f" in svg

    def test_create_standard_force_diagram(self):
        """测试创建标准受力图"""
        from physics2video.templates.force_template import create_standard_force_diagram

        builder = create_standard_force_diagram(
            object_name="滑块",
            gravity=True,
            normal=True,
            friction=True,
        )

        svg = builder.build()
        assert "force-G" in svg
        assert "force-N" in svg
        assert "force-f" in svg


class TestCircuitDiagramTemplate:
    """测试电路图模板"""

    def test_generate_circuit(self):
        """测试生成电路图"""
        from physics2video.templates.circuit_template import (
            CircuitComponentElement,
            CircuitDiagramTemplate,
            ConnectionElement,
        )

        template = CircuitDiagramTemplate()
        components = [
            CircuitComponentElement("battery", "E", "6V"),
            CircuitComponentElement("resistor", "R1", "10Ω"),
        ]
        connections = [
            ConnectionElement("E", "R1"),
        ]

        builder = template.generate(components, connections)
        svg = builder.build()

        assert "component-E" in svg
        assert "component-R1" in svg

    def test_generate_from_dict(self):
        """测试从字典生成电路图"""
        from physics2video.templates.circuit_template import CircuitDiagramTemplate

        template = CircuitDiagramTemplate()
        data = {
            "元件": [
                {"类型": "电源", "标号": "E", "电压": "12V"},
                {"类型": "电阻", "标号": "R1", "阻值": "10Ω"},
                {"类型": "电阻", "标号": "R2", "阻值": "20Ω"},
            ],
            "连接": [
                ("E", "R1"),
                ("R1", "R2"),
            ],
        }

        builder = template.generate_from_dict(data)
        svg = builder.build()

        assert "component-E" in svg
        assert "component-R1" in svg
        assert "component-R2" in svg
