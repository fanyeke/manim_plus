from manim import *


class HelloManimPlus(Scene):
    def construct(self):
        title = Text("manim+", font_size=72, color=BLUE)
        subtitle = Text("Development Environment Ready!", font_size=36, color=GREEN)
        subtitle.next_to(title, DOWN, buff=0.5)

        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP))

        circle = Circle(radius=1.5, color=YELLOW)
        circle.next_to(subtitle, DOWN, buff=1.0)
        self.play(Create(circle))

        square = Square(side_length=2, color=RED)
        square.move_to(circle.get_center())
        self.play(Transform(circle, square))

        self.wait(1)
