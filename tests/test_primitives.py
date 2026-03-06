"""
测试物理图元模块
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import pytest


class TestPhysicsScene:
    """测试 PhysicsScene 脚手架"""

    def test_define_quantity(self):
        """测试物理量定义"""
        from physics2video.primitives.physics_scene import PhysicsScene

        scene = PhysicsScene()
        direction = np.array([0, -1, 0])
        q = scene.define_quantity("重力", "G", 10.0, "N", vector=True, direction=direction)

        assert q.name == "重力"
        assert q.symbol == "G"
        assert q.value == 10.0
        assert q.unit == "N"
        assert q.vector is True
        assert scene.quantities["G"] == q

    def test_calculate_physics_newton2(self):
        """测试牛顿第二定律计算"""
        from physics2video.primitives.physics_scene import PhysicsScene

        scene = PhysicsScene()
        result = scene.calculate_physics("F=ma", "F", m=2.0, a=10.0)

        assert result == 20.0
        assert scene.quantities["F"].value == 20.0

    def test_calculate_physics_kinematics(self):
        """测试运动学公式计算"""
        from physics2video.primitives.physics_scene import PhysicsScene

        scene = PhysicsScene()

        # v = v0 + at
        v = scene.calculate_physics("v=v0+at", "v", v0=0, a=10, t=2)
        assert v == 20.0

        # s = v0t + 0.5at^2
        s = scene.calculate_physics("s=v0t+0.5at^2", "s", v0=0, a=10, t=2)
        assert s == 20.0

    def test_calculate_physics_ohm(self):
        """测试欧姆定律计算"""
        from physics2video.primitives.physics_scene import PhysicsScene

        scene = PhysicsScene()
        U = scene.calculate_physics("U=IR", "U", I=2.0, R=5.0)

        assert U == 10.0

    def test_assert_physics_pass(self):
        """测试物理断言 - 通过"""
        from physics2video.primitives.physics_scene import PhysicsScene

        scene = PhysicsScene()
        scene.assert_physics(True, "测试通过")  # 不应抛出异常

    def test_assert_physics_fail(self):
        """测试物理断言 - 失败"""
        from physics2video.primitives.physics_scene import PhysicsScene

        scene = PhysicsScene()
        with pytest.raises(AssertionError) as excinfo:
            scene.assert_physics(False, "条件不满足")

        assert "条件不满足" in str(excinfo.value)

    def test_add_constraint(self):
        """测试添加物理约束"""
        from physics2video.primitives.physics_scene import PhysicsScene

        scene = PhysicsScene()
        scene.define_quantity("力", "F", 10.0, "N")
        scene.define_quantity("质量", "m", 2.0, "kg")
        scene.define_quantity("加速度", "a", 5.0, "m/s²")

        # 添加约束: F = ma
        def check_newton():
            F = scene.quantities["F"].value
            m = scene.quantities["m"].value
            a = scene.quantities["a"].value
            return F == m * a

        scene.add_constraint("牛顿第二定律", check_newton, "F ≠ ma")

        errors = scene.verify_constraints()
        assert len(errors) == 0  # 约束满足


class TestForceVector:
    """测试力矢量图元"""

    def test_create_force_vector(self):
        """测试创建力矢量"""
        from physics2video.primitives.force_diagram import ForceData, ForceVector

        force = ForceData(
            name="重力",
            symbol="G",
            magnitude=10,
            direction=np.array([0, -1, 0]),
            color="#FFD700",
        )

        vec = ForceVector(force, scale=1.0)
        assert vec.force == force
        assert vec.arrow is not None

    def test_create_standard_forces(self):
        """测试创建标准力集合"""
        from physics2video.primitives.force_diagram import create_standard_forces

        forces = create_standard_forces(
            gravity=True,
            normal=True,
            friction=True,
        )

        assert len(forces) == 3
        symbols = [f.symbol for f in forces]
        assert "G" in symbols
        assert "N" in symbols
        assert "f" in symbols


class TestCircuitElement:
    """测试电路元件图元"""

    def test_create_resistor(self):
        """测试创建电阻"""
        from physics2video.primitives.circuit import (
            CircuitComponentData,
            CircuitElement,
            ComponentType,
        )

        comp = CircuitComponentData(
            component_type=ComponentType.RESISTOR,
            label="R1",
            value="10Ω",
        )

        elem = CircuitElement(comp)
        assert elem.component == comp

    def test_create_circuit_diagram(self):
        """测试创建电路图"""
        from physics2video.primitives.circuit import (
            CircuitComponentData,
            CircuitDiagram,
            ComponentType,
        )

        components = [
            CircuitComponentData(ComponentType.BATTERY, "E", "6V"),
            CircuitComponentData(ComponentType.RESISTOR, "R1", "10Ω"),
        ]

        diagram = CircuitDiagram(components)
        assert len(diagram.elements) == 2
        assert "E" in diagram.elements
        assert "R1" in diagram.elements


class TestMotionTrajectory:
    """测试运动轨迹图元"""

    def test_create_motion_data(self):
        """测试创建运动数据"""
        from physics2video.primitives.motion import MotionData

        motion = MotionData(
            initial_position=np.array([0, 0, 0]),
            initial_velocity=np.array([10, 0, 0]),
            acceleration=np.array([0, -10, 0]),
            time_range=(0, 2),
        )

        assert np.allclose(motion.initial_velocity, [10, 0, 0])
        assert motion.time_range == (0, 2)
