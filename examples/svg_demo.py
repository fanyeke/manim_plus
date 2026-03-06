"""
SVG 模板演示

展示如何使用 SVG 模板生成物理示意图。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from physics2video.templates.circuit_template import (
    CircuitComponentElement,
    CircuitDiagramTemplate,
    ConnectionElement,
)
from physics2video.templates.force_template import (
    ForceDiagramTemplate,
    ForceElement,
    ObjectElement,
    create_standard_force_diagram,
)


def demo_force_diagram():
    """演示受力图生成"""
    print("=== 受力图演示 ===")

    # 方式1：直接创建
    template = ForceDiagramTemplate(width=400, height=400)
    obj = ObjectElement(name="木块", shape="rect", width=60, height=40)
    forces = [
        ForceElement("重力", "G", "mg", "竖直向下", "#FFD700"),
        ForceElement("支持力", "N", "N", "竖直向上", "#00FF00"),
        ForceElement("摩擦力", "f", "μN", "水平向左", "#FF6B6B"),
        ForceElement("拉力", "F", "F", "斜向右上", "#4ECDC4"),
    ]

    builder = template.generate(obj, forces)
    builder.save_html("output/force_diagram_1.html", "木块受力分析")
    print("生成: output/force_diagram_1.html")

    # 方式2：从字典生成（与设计文档格式一致）
    data = {
        "物体": "小车",
        "形状": "rect",
        "力": [
            {"名": "重力", "符号": "G", "大小": "Mg", "方向": "竖直向下"},
            {"名": "支持力", "符号": "N", "大小": "N", "方向": "竖直向上"},
            {"名": "牵引力", "符号": "F", "大小": "F", "方向": "水平向右", "颜色": "#4ECDC4"},
        ],
    }

    builder2 = template.generate_from_dict(data)
    builder2.save_html("output/force_diagram_2.html", "小车受力分析")
    print("生成: output/force_diagram_2.html")

    # 方式3：使用便捷函数
    builder3 = create_standard_force_diagram(
        object_name="滑块",
        gravity=True,
        normal=True,
        friction=True,
        applied=True,
        friction_direction="水平向左",
        applied_direction="水平向右",
    )
    builder3.save_html("output/force_diagram_3.html", "滑块受力分析")
    print("生成: output/force_diagram_3.html")


def demo_circuit_diagram():
    """演示电路图生成"""
    print("\n=== 电路图演示 ===")

    template = CircuitDiagramTemplate(width=600, height=400)

    # 串联电路
    components = [
        CircuitComponentElement("battery", "E", "6V", position=(50, 200)),
        CircuitComponentElement("resistor", "R1", "10Ω", position=(200, 200)),
        CircuitComponentElement("resistor", "R2", "20Ω", position=(350, 200)),
        CircuitComponentElement("ammeter", "A", "", position=(500, 200)),
    ]

    connections = [
        ConnectionElement("E", "R1"),
        ConnectionElement("R1", "R2"),
        ConnectionElement("R2", "A"),
    ]

    builder = template.generate(components, connections)
    builder.save_html("output/circuit_diagram_1.html", "串联电路")
    print("生成: output/circuit_diagram_1.html")

    # 从字典生成
    data = {
        "元件": [
            {"类型": "电源", "标号": "E", "电压": "12V"},
            {"类型": "电阻", "标号": "R1", "阻值": "10Ω"},
            {"类型": "电阻", "标号": "R2", "阻值": "20Ω"},
            {"类型": "灯泡", "标号": "L", "值": ""},
            {"类型": "开关", "标号": "S", "值": ""},
        ],
        "连接": [
            ("E", "S"),
            ("S", "R1"),
            ("R1", "R2"),
            ("R2", "L"),
        ],
    }

    builder2 = template.generate_from_dict(data)
    builder2.save_html("output/circuit_diagram_2.html", "混合电路")
    print("生成: output/circuit_diagram_2.html")


def main():
    """主函数"""
    # 创建输出目录
    os.makedirs("output", exist_ok=True)

    demo_force_diagram()
    demo_circuit_diagram()

    print("\n所有示意图已生成到 output/ 目录")
    print("可以用浏览器打开 HTML 文件查看效果")


if __name__ == "__main__":
    main()
