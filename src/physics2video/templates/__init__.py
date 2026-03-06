"""
SVG 模板引擎模块

提供基于要素列表的 SVG 生成功能，支持受力图、电路图、运动轨迹等。
"""

from .circuit_template import CircuitDiagramTemplate
from .force_template import ForceDiagramTemplate
from .svg_builder import SVGBuilder, SVGElement

__all__ = [
    "SVGBuilder",
    "SVGElement",
    "ForceDiagramTemplate",
    "CircuitDiagramTemplate",
]
