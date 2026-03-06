"""
运动学图元

提供运动轨迹、坐标系和运动图像的 Manim 组件。
"""

from dataclasses import dataclass
from typing import Any, Callable

from manim import *


@dataclass
class MotionData:
    """运动数据"""

    initial_position: np.ndarray
    initial_velocity: np.ndarray
    acceleration: np.ndarray
    time_range: tuple[float, float] = (0, 5)


class CoordinateSystem(VGroup):
    """
    坐标系图元

    创建带标签和刻度的坐标系。
    """

    def __init__(
        self,
        x_range: tuple[float, float, float] = (-5, 5, 1),
        y_range: tuple[float, float, float] = (-3, 3, 1),
        x_length: float = 10,
        y_length: float = 6,
        x_label: str = "x",
        y_label: str = "y",
        show_grid: bool = False,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        # 创建坐标轴
        self.axes = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=x_length,
            y_length=y_length,
            axis_config={
                "include_tip": True,
                "include_numbers": True,
            },
        )
        self.add(self.axes)

        # 坐标轴标签
        self.x_label = self.axes.get_x_axis_label(x_label)
        self.y_label = self.axes.get_y_axis_label(y_label)
        self.add(self.x_label, self.y_label)

        # 网格
        if show_grid:
            self.grid = self.axes.get_grid()
            self.grid.set_stroke(GRAY, opacity=0.3)
            self.add(self.grid)

    def plot(
        self,
        func: Callable[[float], float],
        x_range: tuple[float, float] | None = None,
        color: str = BLUE,
    ) -> VMobject:
        """绘制函数图像"""
        if x_range is None:
            x_range = (self.axes.x_range[0], self.axes.x_range[1])
        return self.axes.plot(func, x_range=x_range, color=color)

    def plot_parametric(
        self,
        func: Callable[[float], tuple[float, float]],
        t_range: tuple[float, float] = (0, 1),
        color: str = BLUE,
    ) -> VMobject:
        """绘制参数曲线"""
        return self.axes.plot_parametric_curve(
            lambda t: self.axes.c2p(*func(t)),
            t_range=t_range,
            color=color,
        )

    def get_point(self, x: float, y: float) -> np.ndarray:
        """获取坐标系中点的实际位置"""
        return self.axes.c2p(x, y)


class MotionTrajectory(VGroup):
    """
    运动轨迹图元

    显示物体的运动轨迹和关键位置。
    """

    def __init__(
        self,
        motion: MotionData,
        dt: float = 0.1,
        show_velocity_vectors: bool = False,
        show_acceleration_vector: bool = False,
        trajectory_color: str = BLUE,
        particle_color: str = RED,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        self.motion = motion
        self.dt = dt
        self.trajectory_color = trajectory_color
        self.particle_color = particle_color

        # 计算轨迹点
        self.trajectory_points = self._calculate_trajectory()

        # 创建轨迹线
        self.trajectory = VMobject()
        self.trajectory.set_points_smoothly(self.trajectory_points)
        self.trajectory.set_stroke(trajectory_color, width=2)
        self.add(self.trajectory)

        # 创建质点
        self.particle = Dot(
            self.trajectory_points[0],
            color=particle_color,
            radius=0.1,
        )
        self.add(self.particle)

        # 速度矢量
        if show_velocity_vectors:
            self.velocity_vectors = self._create_velocity_vectors()
            self.add(*self.velocity_vectors)

        # 加速度矢量
        if show_acceleration_vector:
            self.acceleration_vector = Arrow(
                self.trajectory_points[0],
                self.trajectory_points[0] + motion.acceleration * 0.5,
                color=GREEN,
                buff=0,
            )
            self.add(self.acceleration_vector)

    def _calculate_trajectory(self) -> list[np.ndarray]:
        """计算轨迹点"""
        points = []
        t_start, t_end = self.motion.time_range
        t = t_start

        while t <= t_end:
            # 运动学公式: r = r0 + v0*t + 0.5*a*t^2
            pos = (
                self.motion.initial_position
                + self.motion.initial_velocity * t
                + 0.5 * self.motion.acceleration * t ** 2
            )
            points.append(pos)
            t += self.dt

        return points

    def _create_velocity_vectors(self) -> list[Arrow]:
        """创建速度矢量（在几个关键时刻）"""
        vectors = []
        t_start, t_end = self.motion.time_range
        num_vectors = 5

        for i in range(num_vectors):
            t = t_start + (t_end - t_start) * i / (num_vectors - 1)

            # 位置
            pos = (
                self.motion.initial_position
                + self.motion.initial_velocity * t
                + 0.5 * self.motion.acceleration * t ** 2
            )

            # 速度: v = v0 + a*t
            vel = self.motion.initial_velocity + self.motion.acceleration * t
            vel_norm = np.linalg.norm(vel)

            if vel_norm > 0.01:
                arrow = Arrow(
                    pos,
                    pos + vel / vel_norm * 0.5,
                    color=YELLOW,
                    buff=0,
                    stroke_width=2,
                )
                vectors.append(arrow)

        return vectors

    def animate_motion(
        self,
        scene: Scene,
        run_time: float | None = None,
    ) -> None:
        """
        动画展示运动过程

        Args:
            scene: Manim 场景
            run_time: 动画时长，默认为运动时间
        """
        if run_time is None:
            run_time = self.motion.time_range[1] - self.motion.time_range[0]

        # 让质点沿轨迹运动
        scene.play(
            MoveAlongPath(self.particle, self.trajectory),
            run_time=run_time,
            rate_func=linear,
        )


class VTGraph(VGroup):
    """
    v-t 图图元

    创建速度-时间图像。
    """

    def __init__(
        self,
        v_func: Callable[[float], float],
        t_range: tuple[float, float, float] = (0, 5, 1),
        v_range: tuple[float, float, float] = (-5, 5, 1),
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        # 创建坐标系
        self.coord = CoordinateSystem(
            x_range=t_range,
            y_range=v_range,
            x_label="t/s",
            y_label="v/(m/s)",
        )
        self.add(self.coord)

        # 绘制 v-t 曲线
        self.curve = self.coord.plot(v_func, color=BLUE)
        self.add(self.curve)

    def get_area(
        self,
        t_range: tuple[float, float],
        color: str = BLUE,
        opacity: float = 0.3,
    ) -> VMobject:
        """获取曲线下方的面积（位移）"""
        return self.coord.axes.get_area(
            self.curve,
            x_range=t_range,
            color=color,
            opacity=opacity,
        )


class FreeBodyDiagram(VGroup):
    """
    自由落体运动图元

    展示自由落体或竖直上抛运动。
    """

    def __init__(
        self,
        initial_height: float = 5.0,
        initial_velocity: float = 0.0,
        g: float = 10.0,
        show_height_markers: bool = True,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)

        self.h0 = initial_height
        self.v0 = initial_velocity
        self.g = g

        # 创建参考线
        ground = Line(LEFT * 3, RIGHT * 3, color=GREEN)
        ground.shift(DOWN * 3)
        self.add(ground)

        # 高度标记
        if show_height_markers:
            for i in range(int(initial_height) + 1):
                marker = Line(LEFT * 0.1, RIGHT * 0.1)
                marker.shift(DOWN * 3 + UP * i)
                label = Text(f"{i}m", font_size=16)
                label.next_to(marker, LEFT, buff=0.1)
                self.add(marker, label)

        # 创建下落物体
        self.particle = Dot(
            UP * (initial_height - 3),
            color=RED,
            radius=0.15,
        )
        self.add(self.particle)

    def get_height(self, t: float) -> float:
        """获取 t 时刻的高度"""
        h = self.h0 + self.v0 * t - 0.5 * self.g * t ** 2
        return max(0, h)

    def get_velocity(self, t: float) -> float:
        """获取 t 时刻的速度"""
        return self.v0 - self.g * t

    def animate_fall(
        self,
        scene: Scene,
        show_velocity: bool = True,
    ) -> None:
        """
        动画展示下落过程

        Args:
            scene: Manim 场景
            show_velocity: 是否显示速度信息
        """
        # 计算落地时间
        # h0 + v0*t - 0.5*g*t^2 = 0
        # 解一元二次方程
        import math
        discriminant = self.v0 ** 2 + 2 * self.g * self.h0
        if discriminant < 0:
            return
        t_fall = (self.v0 + math.sqrt(discriminant)) / self.g

        # 创建下落路径
        path = VMobject()
        points = []
        for i in range(51):
            t = t_fall * i / 50
            h = self.get_height(t)
            points.append(UP * (h - 3))
        path.set_points_smoothly(points)

        # 动画
        scene.play(
            MoveAlongPath(self.particle, path),
            run_time=t_fall,
            rate_func=linear,
        )
