import numpy as np
from manim import *

from config import BG, C_CURRENT, C_EDGE, C_FRONTIER, C_PATH, C_TEXT, C_UNSEEN, PANEL_BG


class AgentPerceptsScene(Scene):
    """True state of the environment vs. what the agent actually perceives."""

    GRID = [
        ".......",
        "..##...",
        "...#...",
        "...#.#.",
        ".......",
    ]
    COLS, ROWS = 7, 5
    CELL = 0.8
    GX, GY = -3.9, -0.1           # center of the grid on screen
    AGENT_START = (1, 2)          # (col, row)
    GOAL_CELL = (6, 2)
    MOVES = [("EAST", (1, 0)), ("SOUTH", (0, 1)), ("SOUTH", (0, 1)),
             ("EAST", (1, 0)), ("EAST", (1, 0))]

    def cell_center(self, c, r):
        return np.array([self.GX + (c - 3) * self.CELL, self.GY - (r - 2) * self.CELL, 0.0])

    def look(self, c, r, dc, dr):
        nc, nr = c + dc, r + dr
        if not (0 <= nc < self.COLS and 0 <= nr < self.ROWS):
            return "edge of map"
        return "wall" if self.GRID[nr][nc] == "#" else "free"

    def percept_text(self, c, r):
        lines = [
            f"north: {self.look(c, r, 0, -1)}",
            f"east:  {self.look(c, r, 1, 0)}",
            f"south: {self.look(c, r, 0, 1)}",
            f"west:  {self.look(c, r, -1, 0)}",
            f"goal here: {'yes' if (c, r) == self.GOAL_CELL else 'no'}",
            "everything else: unknown",
        ]
        return "\n".join(lines)

    def visible(self, c, r, cc, rr):
        return max(abs(cc - c), abs(rr - r)) <= 1

    def vision_rect(self, c, r):
        cs = [(a, b) for a in range(c - 1, c + 2) for b in range(r - 1, r + 2)
              if 0 <= a < self.COLS and 0 <= b < self.ROWS]
        c0, c1 = min(a for a, _ in cs), max(a for a, _ in cs)
        r0, r1 = min(b for _, b in cs), max(b for _, b in cs)
        center = (self.cell_center(c0, r0) + self.cell_center(c1, r1)) / 2
        return Rectangle(width=(c1 - c0 + 1) * self.CELL, height=(r1 - r0 + 1) * self.CELL,
                         stroke_color=C_CURRENT, stroke_width=5, fill_opacity=0).move_to(center)

    def make_agent(self):
        body = Circle(radius=0.28, fill_color=C_FRONTIER, fill_opacity=1,
                      stroke_color=WHITE, stroke_width=3)
        eyes = VGroup(Dot(radius=0.05, color=WHITE).shift(LEFT * 0.1 + UP * 0.06),
                      Dot(radius=0.05, color=WHITE).shift(RIGHT * 0.1 + UP * 0.06))
        return VGroup(body, eyes)

    def construct(self):
        self.camera.background_color = BG

        title = Text("How does an agent see the world?", font_size=40, weight=BOLD)
        title.move_to([0, 3.5, 0])
        self.play(FadeIn(title, shift=DOWN * 0.2))

        # --- the environment (true state) ---
        cells, fog = {}, {}
        world = VGroup()
        for r in range(self.ROWS):
            for c in range(self.COLS):
                wall = self.GRID[r][c] == "#"
                sq = Square(side_length=self.CELL, stroke_color=C_EDGE, stroke_width=1.5,
                            fill_color="#475569" if wall else C_UNSEEN,
                            fill_opacity=1 if wall else 0.6)
                sq.move_to(self.cell_center(c, r))
                cells[(c, r)] = sq
                world.add(sq)
        goal = Star(n=5, outer_radius=0.28, inner_radius=0.12, color=C_CURRENT,
                    fill_opacity=1).move_to(self.cell_center(*self.GOAL_CELL))
        world.add(goal)

        env_frame = SurroundingRectangle(world, buff=0.1, color=C_FRONTIER, stroke_width=3)
        env_label = Text("ENVIRONMENT (true state)", font_size=24, color=C_FRONTIER, weight=BOLD)
        env_label.next_to(env_frame, UP, buff=0.12)

        agent = self.make_agent()
        ac, ar = self.AGENT_START
        agent.move_to(self.cell_center(ac, ar))

        self.play(FadeIn(world), Create(env_frame), FadeIn(env_label))
        self.play(FadeIn(agent, scale=0.5))
        caption = Text("The environment contains EVERYTHING: walls, free cells, the goal...",
                       font_size=26).move_to([0, -3.65, 0])
        self.play(FadeIn(caption))
        self.wait(2)

        # --- fog: the agent only gets percepts ---
        for (c, r), sq in cells.items():
            f = Square(side_length=self.CELL, stroke_width=0, fill_color=BG, fill_opacity=0)
            f.move_to(sq)
            fog[(c, r)] = f
        fog_group = VGroup(*fog.values())
        self.add(fog_group)
        self.bring_to_front(agent)

        self.play(Transform(caption, Text("But sensors give only a slice of it: the AGENT'S PERCEPT.",
                                          font_size=26).move_to([0, -3.65, 0])))
        vision = self.vision_rect(ac, ar)
        fog_anims = [fog[k].animate.set_fill(BG, opacity=0.93)
                     for k in fog if not self.visible(ac, ar, *k)]
        self.play(*fog_anims, Create(vision), run_time=1.5)
        self.bring_to_front(agent)

        # --- agent box + percept / action arrows ---
        agent_box = RoundedRectangle(corner_radius=0.15, width=3.4, height=1.2,
                                     stroke_color=C_FRONTIER, stroke_width=3,
                                     fill_color=PANEL_BG, fill_opacity=1).move_to([4.3, 0.3, 0])
        agent_txt = Text("AGENT", font_size=30, weight=BOLD).move_to(agent_box)
        percept_arrow = Arrow([-0.9, 0.75, 0], [2.55, 0.75, 0], buff=0, color=C_CURRENT, stroke_width=5)
        action_arrow = Arrow([2.55, -0.15, 0], [-0.9, -0.15, 0], buff=0, color=C_PATH, stroke_width=5)
        percept_lbl = Text("percept", font_size=22, color=C_CURRENT).next_to(percept_arrow, UP, buff=0.08)
        action_lbl = Text("action", font_size=22, color=C_PATH).next_to(action_arrow, DOWN, buff=0.08)

        card = RoundedRectangle(corner_radius=0.15, width=4.8, height=2.5,
                                stroke_color=C_EDGE, stroke_width=2,
                                fill_color=PANEL_BG, fill_opacity=1).move_to([4.3, -2.1, 0])
        card_title = Text("PERCEPT (from sensors)", font_size=20, color=C_CURRENT, weight=BOLD)
        card_title.move_to(card.get_top() + DOWN * 0.3)
        body_anchor = card.get_corner(UL) + np.array([0.3, -0.6, 0])
        body = Text(self.percept_text(ac, ar), font_size=20, line_spacing=0.9)
        body.move_to(body_anchor, aligned_edge=UL)

        self.play(FadeIn(agent_box), FadeIn(agent_txt), FadeIn(card), FadeIn(card_title))
        self.play(GrowArrow(percept_arrow), FadeIn(percept_lbl))
        self.play(FadeIn(body))
        self.wait(1.5)

        self.play(Transform(caption, Text("Loop:  percept → agent chooses → action → environment changes → new percept",
                                          font_size=24).move_to([0, -3.65, 0])))
        self.wait(1)

        # --- run the loop for a few steps ---
        c, r = ac, ar
        for name, (dc, dr) in self.MOVES:
            self.play(Indicate(agent_box, color=C_FRONTIER, scale_factor=1.05), run_time=0.8)
            new_action = Text(f"move {name}", font_size=24, color=C_PATH, weight=BOLD)
            new_action.next_to(action_arrow, DOWN, buff=0.08)
            self.play(GrowArrow(action_arrow),
                      Transform(action_lbl, new_action), run_time=0.8)

            c, r = c + dc, r + dr
            self.play(agent.animate.move_to(self.cell_center(c, r)), run_time=0.9)

            new_vision = self.vision_rect(c, r)
            fog_anims = [fog[k].animate.set_fill(BG, opacity=0 if self.visible(c, r, *k) else 0.93)
                         for k in fog]
            new_body = Text(self.percept_text(c, r), font_size=20, line_spacing=0.9)
            new_body.move_to(body_anchor, aligned_edge=UL)
            self.play(*fog_anims, Transform(vision, new_vision), Transform(body, new_body),
                      Indicate(percept_arrow, color=C_CURRENT, scale_factor=1.0), run_time=1.2)
            self.bring_to_front(agent)
            self.wait(0.4)

        final = Text("The agent never saw the goal. It decides using percepts only, "
                     "so memory and a model of the world matter.",
                     font_size=24, color=C_TEXT)
        final.scale_to_fit_width(min(final.width, 13.2)).move_to([0, -3.65, 0])
        self.play(Transform(caption, final))
        self.wait(3)