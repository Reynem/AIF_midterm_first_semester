from collections import deque

# The shared graph (Lecture 2, slide "A* Python Example")
START, GOAL = "A", "G"

POS = {
    "A": (-6.0, 0.0),
    "B": (-3.5, 1.8),
    "C": (-3.5, -1.8),
    "D": (-0.8, 1.8),
    "E": (-0.8, -1.5),
    "G": (1.8, 0.0),
}

EDGES = [
    ("A", "B", 1),
    ("A", "C", 4),
    ("B", "D", 2),
    ("B", "E", 5),
    ("C", "E", 1),
    ("D", "G", 5),
    ("E", "G", 2),
]

H = {"A": 6, "B": 5, "C": 3, "D": 4, "E": 2, "G": 0}

ADJ = {n: [] for n in POS}
W = {}
for _u, _v, _w in EDGES:
    ADJ[_u].append((_v, _w))
    W[(_u, _v)] = _w

# where to draw the g/h/f tag of each node (so it never sits on an edge)
TAG_DIR = {"A": (-1, -1, 0), "B": (0, 1, 0), "C": (0, -1, 0), "D": (0, 1, 0), "E": (0, -1, 0), "G": (0, -1, 0)}


def path_cost(path):
    return sum(W[(u, v)] for u, v in zip(path, path[1:]))


def arrow_str(path):
    return "→".join(path)


def _step(pop, pop_cap, cap, gen, skip, frontier, path=None):
    return dict(pop=pop, pop_cap=pop_cap, cap=cap, gen=gen, skip=skip,
                frontier=frontier, path=path)


def _expand_caption(node, gen_parts, skip, skip_reason):
    parts = ", ".join(gen_parts) if gen_parts else "nothing new"
    text = f"Expand {node}: {parts}"
    if skip:
        text += f"    (skip {', '.join(skip)}: {skip_reason})"
    return text


def bfs_trace():
    rule = "the OLDEST plan (FIFO queue)"
    fr = lambda q: [(n, arrow_str(p)) for n, p in q]
    q = deque([(START, [START])])
    seen = {START}
    steps = [_step(None, "", "Start: the frontier holds one plan, [A]",
                   [(START, None, False)], [], fr(q))]
    while q:
        node, path = q.popleft()
        pop_cap = f"Pop {node} - {rule}"
        if node == GOAL:
            steps.append(_step(node, pop_cap, f"Goal test passed at {node}!",
                               [], [], fr(q), path))
            break
        gen, skip = [], []
        for nxt, _w in ADJ[node]:
            if nxt in seen:
                skip.append(nxt)
            else:
                seen.add(nxt)
                q.append((nxt, path + [nxt]))
                gen.append((nxt, None, False))
        cap = _expand_caption(node, [f"add {c}" for c, _, _ in gen], skip, "already seen")
        steps.append(_step(node, pop_cap, cap, gen, skip, fr(q)))
    return steps


def dfs_trace():
    rule = "the NEWEST plan (LIFO stack)"
    fr = lambda s: [(n, arrow_str(p)) for n, p in reversed(s)]  # top of stack first
    stack = [(START, [START])]
    visited = set()
    steps = [_step(None, "", "Start: the stack holds one plan, [A]",
                   [(START, None, False)], [], fr(stack))]
    while stack:
        node, path = stack.pop()
        pop_cap = f"Pop {node} - {rule}"
        if node == GOAL:
            steps.append(_step(node, pop_cap, f"Goal test passed at {node}!",
                               [], [], fr(stack), path))
            break
        if node in visited:
            steps.append(_step(node, pop_cap, f"{node} was already expanded - ignore it",
                               [], [], fr(stack)))
            continue
        visited.add(node)
        gen, skip = [], []
        # push in reverse so the FIRST neighbour is explored first
        for nxt, _w in reversed(ADJ[node]):
            if nxt in visited:
                skip.append(nxt)
            else:
                stack.append((nxt, path + [nxt]))
                gen.append((nxt, None, False))
        gen.reverse()
        cap = _expand_caption(node, [f"push {c}" for c, _, _ in gen], skip, "already visited")
        steps.append(_step(node, pop_cap, cap, gen, skip, fr(stack)))
    return steps


def best_first_trace(use_h):
    """UCS (use_h=False, priority g) and A* (use_h=True, priority f = g + h).
    Ties are broken by smaller h, then alphabetically."""
    rule = "the LOWEST f = g + h" if use_h else "the LOWEST g (cheapest so far)"
    h = (lambda n: H[n]) if use_h else (lambda n: 0)

    g = {START: 0}
    parent = {START: None}
    frontier = {START}
    closed = set()

    def tag(n):
        return f"g={g[n]} h={H[n]} f={g[n] + H[n]}" if use_h else f"g={g[n]}"

    def label(n):
        return f"{n}    f = {g[n]} + {H[n]} = {g[n] + H[n]}" if use_h else f"{n}    g = {g[n]}"

    def ordered():
        return sorted(frontier, key=lambda n: (g[n] + h(n), h(n), n))

    def fr():
        return [(n, label(n)) for n in ordered()]

    steps = [_step(None, "", "Start: the frontier holds one plan, [A]",
                   [(START, tag(START), False)], [], fr())]
    while frontier:
        node = ordered()[0]
        frontier.remove(node)
        pop_cap = f"Pop {node} - {rule}"
        if node == GOAL:
            path, cur = [], node
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            steps.append(_step(node, pop_cap, f"Goal test passed at {node}!  Cost = {g[node]}",
                               [], [], fr(), path))
            break
        closed.add(node)
        gen, skip, parts = [], [], []
        for nxt, w in ADJ[node]:
            new_g = g[node] + w
            if nxt in closed:
                skip.append(nxt)
            elif nxt not in g:
                g[nxt], parent[nxt] = new_g, node
                frontier.add(nxt)
                gen.append((nxt, tag(nxt), False))
                parts.append(f"add {nxt}")
            elif new_g < g[nxt]:
                old = g[nxt]
                g[nxt], parent[nxt] = new_g, node
                gen.append((nxt, tag(nxt), True))
                parts.append(f"improve {nxt} (g {old}→{new_g})")
            else:
                skip.append(nxt)
        cap = _expand_caption(node, parts, skip, "no better route")
        steps.append(_step(node, pop_cap, cap, gen, skip, fr()))
    return steps


def popped_order(trace):
    return [s["pop"] for s in trace if s["pop"] is not None]