from manim import *

from config import BG, C_EDGE, C_MUTED, C_PATH, C_SKIP, C_TEXT
from graph_data import arrow_str, best_first_trace, bfs_trace, dfs_trace, path_cost, popped_order


class ComparisonScene(Scene):
    def construct(self):
        self.camera.background_color = BG
        runs = [
            ("BFS", "oldest (FIFO)", bfs_trace()),
            ("DFS", "newest (LIFO)", dfs_trace()),
            ("UCS", "lowest g", best_first_trace(False)),
            ("A*", "lowest g + h", best_first_trace(True)),
        ]
        results = []
        for name, rule, tr in runs:
            path = next(s["path"] for s in tr if s["path"])
            results.append((name, rule, popped_order(tr), path))
        best = min(path_cost(r[3]) for r in results)

        title = Text("Same graph, four strategies", font_size=40, weight=BOLD)
        title.move_to([0, 3.4, 0])
        self.play(FadeIn(title, shift=DOWN * 0.2))

        cols = [(-6.6, "Algorithm"), (-4.9, "Picks next"), (-2.0, "Pop order"),
                (1.0, "Final path"), (4.0, "Cost"), (5.4, "Pops")]
        header = VGroup(*[
            Text(t, font_size=24, color=C_MUTED).move_to([x, 2.2, 0], aligned_edge=LEFT)
            for x, t in cols])
        rule_line = Line([-6.8, 1.85, 0], [6.8, 1.85, 0], color=C_EDGE)
        self.play(FadeIn(header), Create(rule_line))

        for i, (name, rule, order, path) in enumerate(results):
            y = 1.2 - 0.95 * i
            cost = path_cost(path)
            ok = cost == best
            cells = [
                Text(name, font_size=30, weight=BOLD),
                Text(rule, font_size=24, color=C_MUTED),
                Text(" ".join(order), font_size=26),
                Text(arrow_str(path), font_size=26),
                Text(str(cost), font_size=30, weight=BOLD, color=C_PATH if ok else C_SKIP),
                Text(str(len(order)), font_size=28),
            ]
            row = VGroup()
            for (x, _), c in zip(cols, cells):
                c.move_to([x, y, 0], aligned_edge=LEFT)
                row.add(c)
            self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.9)
            self.wait(0.4)

        notes = VGroup(
            Text("BFS minimizes the number of edges, not the cost.", font_size=24, color=C_TEXT),
            Text("UCS and A* both find the cheapest path; A* gets there with fewer pops "
                 "because h(n) points toward the goal.", font_size=24, color=C_TEXT),
        ).arrange(DOWN, buff=0.2)
        for t in notes:
            if t.width > 13:
                t.scale_to_fit_width(13)
        notes.move_to([0, -3.0, 0])
        self.play(FadeIn(notes, shift=UP * 0.2))
        self.wait(3)