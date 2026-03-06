"""
PhysicsScene 演示示例

展示如何使用 PhysicsScene 脚手架创建物理讲解动画。
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from manim import *

from physics2video.primitives.force_diagram import (
    ForceAnalysisDiagram,
    ForceData,
    ForceVector,
    create_standard_forces,
)
from physics2video.primitives.physics_scene import PhysicsScene


class NewtonSecondLawDemo(PhysicsScene):
    """
    牛顿第二定律演示

    演示 F = ma 的计算和受力分析。
    """

    def construct(self):
        # 标题
        title = Text("牛顿第二定律演示", font_size=48, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # 定义物理量
        self.define_quantity("质量", "m", 2.0, "kg")
        self.define_quantity("加速度", "a", 5.0, "m/s²")

        # 计算合外力
        F = self.calculate_physics("F=ma", "F", m=2.0, a=5.0)

        # 物理断言
        self.assert_physics(F == 10.0, "F = ma = 2 × 5 = 10N")

        # 显示公式
        formula = MathTex(r"F = ma", font_size=48)
        formula.next_to(title, DOWN, buff=1)
        self.play(Write(formula))
        self.wait(0.5)

        # 显示计算过程
        calc = MathTex(r"F = 2 \times 5 = 10 \, \text{N}", font_size=36)
        calc.next_to(formula, DOWN, buff=0.5)
        self.play(Write(calc))
        self.wait(0.5)

        # 创建受力分析图
        forces = create_standard_forces(
            gravity=True,
            normal=True,
            applied=True,
            gravity_value="G",
            normal_value="N",
            applied_value="F",
            applied_direction=RIGHT,
        )

        diagram = ForceAnalysisDiagram(
            object_name="物体",
            forces=forces,
            scale=0.8,
        )
        diagram.shift(DOWN * 1.5)

        # 动画展示受力分析
        diagram.animate_all_forces(self)

        self.wait(1)

        # 清理
        self.play(FadeOut(title), FadeOut(formula), FadeOut(calc), FadeOut(diagram))


class KinematicsDemo(PhysicsScene):
    """
    运动学演示

    演示匀变速直线运动公式。
    """

    def construct(self):
        # 标题
        title = Text("匀变速直线运动", font_size=48, color=GREEN)
        title.to_edge(UP)
        self.play(Write(title))

        # 定义初始条件
        self.define_quantity("初速度", "v0", 0, "m/s")
        self.define_quantity("加速度", "a", 10, "m/s²")
        self.define_quantity("时间", "t", 2, "s")

        # 计算末速度
        v = self.calculate_physics("v=v0+at", "v", v0=0, a=10, t=2)

        # 显示公式
        formula1 = MathTex(r"v = v_0 + at", font_size=40)
        formula1.next_to(title, DOWN, buff=0.8)

        calc1 = MathTex(r"v = 0 + 10 \times 2 = 20 \, \text{m/s}", font_size=32)
        calc1.next_to(formula1, DOWN, buff=0.3)

        self.play(Write(formula1))
        self.play(Write(calc1))
        self.wait(0.5)

        # 计算位移
        s = self.calculate_physics("s=v0t+0.5at^2", "s", v0=0, a=10, t=2)

        formula2 = MathTex(r"s = v_0 t + \frac{1}{2}at^2", font_size=40)
        formula2.next_to(calc1, DOWN, buff=0.5)

        calc2 = MathTex(r"s = 0 + \frac{1}{2} \times 10 \times 2^2 = 20 \, \text{m}", font_size=32)
        calc2.next_to(formula2, DOWN, buff=0.3)

        self.play(Write(formula2))
        self.play(Write(calc2))

        # 验证结果
        self.assert_physics(v == 20.0, "末速度计算正确")
        self.assert_physics(s == 20.0, "位移计算正确")

        self.wait(1)


class CircuitDemo(PhysicsScene):
    """
    简单电路演示

    演示欧姆定律。
    """

    def construct(self):
        # 标题
        title = Text("欧姆定律", font_size=48, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))

        # 定义物理量
        self.define_quantity("电流", "I", 2.0, "A")
        self.define_quantity("电阻", "R", 5.0, "Ω")

        # 计算电压
        U = self.calculate_physics("U=IR", "U", I=2.0, R=5.0)

        # 显示公式
        formula = MathTex(r"U = IR", font_size=48)
        formula.next_to(title, DOWN, buff=1)

        calc = MathTex(r"U = 2 \times 5 = 10 \, \text{V}", font_size=36)
        calc.next_to(formula, DOWN, buff=0.5)

        self.play(Write(formula))
        self.play(Write(calc))

        # 计算功率
        P = self.calculate_physics("P=UI", "P", U=10.0, I=2.0)

        formula2 = MathTex(r"P = UI", font_size=48)
        formula2.next_to(calc, DOWN, buff=0.8)

        calc2 = MathTex(r"P = 10 \times 2 = 20 \, \text{W}", font_size=36)
        calc2.next_to(formula2, DOWN, buff=0.5)

        self.play(Write(formula2))
        self.play(Write(calc2))

        # 验证
        self.assert_physics(U == 10.0, "电压计算正确")
        self.assert_physics(P == 20.0, "功率计算正确")

        self.wait(1)


if __name__ == "__main__":
    # 可以直接运行测试
    print("请使用 manim 命令渲染场景：")
    print("  manim render -ql examples/physics_demo.py NewtonSecondLawDemo")
    print("  manim render -ql examples/physics_demo.py KinematicsDemo")
    print("  manim render -ql examples/physics_demo.py CircuitDemo")
