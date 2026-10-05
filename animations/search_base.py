import numpy as np
from manim import *

from config import (
    BG,
    C_CURRENT,
    C_EDGE,
    C_EXPANDED,
    C_FRONTIER,
    C_MUTED,
    C_PATH,
    C_SKIP,
    C_TEXT,
    C_UNSEEN,
    PANEL_BG,
)
from graph_data import EDGES, GOAL, H, POS, START, arrow_str, path_cost


class SearchScene(Scene):
    title_text = ""
    panel_title = ""
    panel_hint = ""
    show_h = False

    PANEL_X = 4.6

    def make_trace(self):
        raise NotImplementedError

    def _p(self, n):
        return np.array([POS[n][0], POS[n][1], 0.0])

    def build_graph(self):
        self.nodes, self.edges, self.tags = {}, {}, {}
        edge_group, label_group, node_group = VGroup(), VGroup(), VGroup()

        for u, v, w in EDGES:
            arr = Arrow(self._p(u), self._p(v), buff=0.4, stroke_width=3,
                        tip_length=0.2, color=C_EDGE)
            self.edges[(u, v)] = arr
            edge_group.add(arr)
            lab = Text(str(w), font_size=24, color=C_TEXT)
            lab.move_to((self._p(u) + self._p(v)) / 2)
            lab.add_background_rectangle(color=BG, opacity=0.9, buff=0.06)
            label_group.add(lab)

        for n in POS:
            circ = Circle(radius=0.38, stroke_color=C_TEXT, stroke_width=3,
                          fill_color=C_UNSEEN, fill_opacity=1)
            txt = Text(n, font_size=30, color=WHITE, weight=BOLD)
            grp = VGroup(circ, txt).move_to(self._p(n))
            self.nodes[n] = grp
            node_group.add(grp)

        start_lbl = Text("START", font_size=20, color=C_MUTED).next_to(self.nodes[START], UP, buff=0.12)
        goal_lbl = Text("GOAL", font_size=20, color=C_MUTED).next_to(self.nodes[GOAL], UP, buff=0.12)
        self.nodes[GOAL][0].set_stroke(C_CURRENT, width=5)

        self.graph_group = VGroup(edge_group, label_group, node_group, start_lbl, goal_lbl)
        return self.graph_group

    def build_legend(self):
        items = [("frontier", C_FRONTIER), ("current", C_CURRENT),
                 ("expanded", C_EXPANDED), ("final path", C_PATH)]
        legend = VGroup()
        for text, col in items:
            dot = Circle(radius=0.1, fill_color=col, fill_opacity=1, stroke_width=0)
            lab = Text(text, font_size=18, color=C_MUTED)
            legend.add(VGroup(dot, lab.next_to(dot, RIGHT, buff=0.12)))
        legend.arrange(RIGHT, buff=0.45)
        legend.move_to([-6.9, 3.0, 0], aligned_edge=LEFT)
        return legend

    def build_panel(self):
        bg = RoundedRectangle(corner_radius=0.2, width=4.5, height=5.7,
                              stroke_color=C_EDGE, stroke_width=2,
                              fill_color=PANEL_BG, fill_opacity=1)
        bg.move_to([self.PANEL_X, 0.4, 0])
        t1 = Text(self.panel_title, font_size=24, color=WHITE, weight=BOLD)
        t1.move_to([self.PANEL_X, 2.85, 0])
        t2 = Text(self.panel_hint, font_size=18, color=C_MUTED)
        t2.move_to([self.PANEL_X, 2.4, 0])
        return VGroup(bg, t1, t2)

    def make_rows(self, items):
        rows = VGroup()
        if not items:
            t = Text("(empty)", font_size=22, color=C_MUTED)
            t.move_to([self.PANEL_X, 1.85, 0])
            rows.add(t)
            return rows
        for i, (_n, label) in enumerate(items):
            box = RoundedRectangle(corner_radius=0.12, width=3.9, height=0.5,
                                   stroke_color=C_CURRENT if i == 0 else C_FRONTIER,
                                   stroke_width=3 if i == 0 else 2,
                                   fill_color=C_UNSEEN, fill_opacity=1)
            txt = Text(label, font_size=22, color=WHITE)
            if txt.width > 3.6:
                txt.scale_to_fit_width(3.6)
            txt.move_to(box)
            row = VGroup(box, txt)
            row.move_to([self.PANEL_X, 1.85 - 0.62 * i, 0])
            rows.add(row)
        return rows

    def make_tag(self, n, text):
        from graph_data import TAG_DIR
        muted = text.startswith("h=") and "g=" not in text
        tag = Text(text, font_size=18, color=C_MUTED if muted else C_TEXT)
        tag.next_to(self.nodes[n], np.array(TAG_DIR[n]), buff=0.1)
        return tag

    def tag_anim(self, n, text):
        new = self.make_tag(n, text)
        if n in self.tags:
            old = self.tags[n]
            self.tags[n] = new
            return ReplacementTransform(old, new)
        self.tags[n] = new
        return FadeIn(new)

    def make_caption(self, text, y=-3.1, size=26, color=WHITE):
        cap = Text(text, font_size=size, color=color)
        if cap.width > 13:
            cap.scale_to_fit_width(13)
        cap.move_to([0, y, 0])
        return cap

    def set_caption(self, text):
        new = self.make_caption(text)
        return Transform(self.caption, new)

    def set_order(self, popped):
        text = "Pop order:  " + (" → ".join(popped) if popped else "-")
        new = self.make_caption(text, y=-3.7, size=22, color=C_MUTED)
        return Transform(self.order, new)

    def set_node(self, n, color):
        return self.nodes[n][0].animate.set_fill(color, opacity=1)

    def construct(self):
        self.camera.background_color = BG
        trace = self.make_trace()

        title = Text(self.title_text, font_size=38, color=WHITE, weight=BOLD)
        title.move_to([-6.9, 3.6, 0], aligned_edge=LEFT)
        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=0.8)
        self.play(FadeIn(self.build_legend()), FadeIn(self.build_graph()),
                  FadeIn(self.build_panel()), run_time=1.2)

        # initial state
        init = trace[0]
        self.caption = self.make_caption(init["cap"])
        self.order = self.make_caption("Pop order:  -", y=-3.7, size=22, color=C_MUTED)
        self.rows = self.make_rows(init["frontier"])

        anims = [FadeIn(self.caption), FadeIn(self.order), FadeIn(self.rows),
                 self.set_node(START, C_FRONTIER)]
        if self.show_h:
            for n in POS:
                anims.append(self.tag_anim(n, f"h={H[n]}"))
        self.play(*anims, run_time=1.0)
        for child, tag, _ in init["gen"]:
            if tag:
                self.play(self.tag_anim(child, tag), run_time=0.5)
        self.wait(1.0)

        popped = []
        for step in trace[1:]:
            node = step["pop"]

            # 1) pop the next node from the frontier
            self.play(self.set_node(node, C_CURRENT),
                      Indicate(self.nodes[node], color=C_CURRENT, scale_factor=1.15),
                      self.set_caption(step["pop_cap"]), run_time=1.0)
            popped.append(node)
            self.wait(0.4)

            # 2a) goal reached: draw the final path
            if step["path"]:
                path = step["path"]
                self.play(FadeTransform(self.rows, self.make_rows(step["frontier"])),
                          self.set_order(popped), run_time=0.6)
                seq = []
                for u, v in zip(path, path[1:]):
                    seq.append(self.edges[(u, v)].animate.set_color(C_PATH).set_stroke(width=6))
                for n in path:
                    seq.append(self.set_node(n, C_PATH))
                self.play(LaggedStart(*seq, lag_ratio=0.25), run_time=2.0)
                never = [n for n in POS if n not in popped]
                summary = (f"Path {arrow_str(path)}   |   cost = {path_cost(path)}   |   "
                           f"edges = {len(path) - 1}   |   popped {len(popped)} nodes")
                if never:
                    summary += f"   |   never popped: {', '.join(never)}"
                self.play(Transform(self.caption, self.make_caption(summary, size=24, color=C_PATH)),
                          run_time=0.8)
                self.wait(2.5)
                break

            # 2b) expand: the node becomes "expanded", children enter the frontier
            new_rows = self.make_rows(step["frontier"])
            anims = [self.set_node(node, C_EXPANDED),
                     self.set_caption(step["cap"]),
                     self.set_order(popped)]
            for child, tag, improved in step["gen"]:
                edge = self.edges[(node, child)]
                anims.append(edge.animate.set_color(C_FRONTIER))
                anims.append(self.set_node(child, C_FRONTIER))
                if tag:
                    anims.append(self.tag_anim(child, tag))
            for child in step["skip"]:
                anims.append(Indicate(self.edges[(node, child)], color=C_SKIP, scale_factor=1.0))
            self.play(*anims, FadeTransform(self.rows, new_rows), run_time=1.4)
            self.rows = new_rows
            self.wait(0.8)