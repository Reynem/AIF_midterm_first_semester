from graph_data import best_first_trace, bfs_trace, dfs_trace
from animations.search_base import SearchScene


class BFSScene(SearchScene):
    title_text = "Breadth-First Search (BFS)"
    panel_title = "FRONTIER: queue (FIFO)"
    panel_hint = "top = next to be popped"

    def make_trace(self):
        return bfs_trace()


class DFSScene(SearchScene):
    title_text = "Depth-First Search (DFS)"
    panel_title = "FRONTIER: stack (LIFO)"
    panel_hint = "top = next to be popped"

    def make_trace(self):
        return dfs_trace()


class UCSScene(SearchScene):
    title_text = "Uniform-Cost Search (UCS)"
    panel_title = "FRONTIER: priority queue"
    panel_hint = "sorted by g(n) = cost so far"

    def make_trace(self):
        return best_first_trace(use_h=False)


class AStarScene(SearchScene):
    title_text = "A* Search:  f(n) = g(n) + h(n)"
    panel_title = "FRONTIER: priority queue"
    panel_hint = "sorted by f(n); ties → smaller h"
    show_h = True

    def make_trace(self):
        return best_first_trace(use_h=True)