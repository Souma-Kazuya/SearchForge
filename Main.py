# ─────────────────────────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────────────────────────
import tkinter as tk   # tkinter: Python's built-in GUI library used
                        # to create windows, canvases, buttons, labels, etc.
import time             # time.sleep() is used to introduce a delay between
                        # animation frames so the user can see each step.

# ─────────────────────────────────────────────────────────────────
#  GRAPH  (Weighted Directed Adjacency Dictionary)
#  Used in Experiments 3, 4, 5 & 6
# ─────────────────────────────────────────────────────────────────
# Each KEY  → a campus building (node/state)
# Each VALUE → a dict of {neighbor: edge_cost}
#              representing direct connections and their travel cost.
# Edges are ONE-WAY (directed): e.g. Main_Gate → Admin_Block exists,
# but Admin_Block → Main_Gate does NOT.
# AI_DS_Lab has no outgoing edges {} because it is the GOAL node.
graph = {
    'Main_Gate':   {'Admin_Block': 2, 'Canteen': 1},  # From gate: Admin costs 2, Canteen costs 1
    'Admin_Block': {'Hostel': 3, 'Library': 2},        # From Admin: Hostel costs 3, Library costs 2
    'Canteen':     {'Auditorium': 2},                  # From Canteen: Auditorium costs 2
    'Hostel':      {'AI_DS_Lab': 5},                   # From Hostel: Lab costs 5 (expensive!)
    'Library':     {'AI_DS_Lab': 1},                   # From Library: Lab costs only 1 (cheapest route)
    'Auditorium':  {'AI_DS_Lab': 3},                   # From Auditorium: Lab costs 3
    'AI_DS_Lab':   {}                                  # GOAL node — no outgoing edges
}

# ─────────────────────────────────────────────────────────────────
#  HEURISTIC  h(n)  — Estimated cost from node n to the GOAL
#  Used by Informed Search algorithms: Greedy & A*
# ─────────────────────────────────────────────────────────────────
# h(n) is a hand-crafted estimate (not the real cost).
# Rule: h(GOAL) must always be 0 — the goal is 0 steps from itself.
# Lower h(n) means the node is "closer" to the goal in the algorithm's view.
# Library has h=1 (very close to goal), Main_Gate has h=5 (far away).
heuristic = {
    'Main_Gate': 5,    # Far from goal — 5 estimated units away
    'Admin_Block': 3,  # Moderately far
    'Canteen': 5,      # Also far (detour route)
    'Hostel': 5,       # Far — expensive path ahead
    'Library': 1,      # Very close to goal — cheapest path
    'Auditorium': 3,   # Moderate distance
    'AI_DS_Lab': 0     # This IS the goal → h = 0
}

# ─────────────────────────────────────────────────────────────────
#  POSITIONS  — Pixel (X, Y) coordinates for drawing each node
#               on the tkinter Canvas (820 × 360 px)
# ─────────────────────────────────────────────────────────────────
# These control where each building's oval is drawn on screen.
# Laid out left-to-right to mimic a real campus map flow:
#   Main_Gate (left) → middle buildings → AI_DS_Lab (right/center)
POSITIONS = {
    'Main_Gate':   (100, 200),   # Leftmost — entry point
    'Admin_Block': (280, 100),   # Upper-middle
    'Canteen':     (280, 300),   # Lower-middle
    'Hostel':      (500, 70),    # Upper-right cluster
    'Library':     (500, 190),   # Middle-right cluster
    'Auditorium':  (500, 310),   # Lower-right cluster
    'AI_DS_Lab':   (720, 200)    # Rightmost — the GOAL
}

# ─────────────────────────────────────────────────────────────────
#  CONSTANTS — Start and Goal nodes for every algorithm
# ─────────────────────────────────────────────────────────────────
# All 4 algorithms will search from START → GOAL.
# Having them as constants makes it easy to change the scenario later.
START = 'Main_Gate'   # Entry point of the campus (source node)
GOAL  = 'AI_DS_Lab'  # Destination we want to reach (goal node)


# ─────────────────────────────────────────────────────────────────
#  MAIN GUI CLASS
#  Wraps the entire application: window, canvas, buttons, algorithms
# ─────────────────────────────────────────────────────────────────
class CampusSearchGUI:

    # ── Constructor ───────────────────────────────────────────────
    # Called once when the app starts. Sets up the window layout:
    #   Title label → Canvas (graph area) → Status bar → Buttons
    def __init__(self, root):
        self.root = root  # root is the main tkinter window object

        # Set window title, size, and dark background color
        self.root.title("Campus Route Analyzer: DFS, BFS, Greedy & A*")
        self.root.geometry("860x540")        # Width x Height in pixels
        self.root.configure(bg="#1e1e2e")    # Dark purple-ish background

        # ── Top Title Label ───────────────────────────────────────
        # Displayed at the very top of the window as a heading
        tk.Label(
            root, text="Campus Navigation Search Visualizer (Uninformed vs Informed)",
            font=("Arial", 15, "bold"), bg="#1e1e2e", fg="#cdd6f4"
        ).pack(pady=8)   # pack() adds it to the window; pady=8 adds vertical spacing

        # ── Canvas ────────────────────────────────────────────────
        # The drawing area where the campus graph (nodes + edges) is rendered.
        # All ovals, lines, and text are drawn on this canvas.
        self.canvas = tk.Canvas(root, width=820, height=360, bg="#181825", highlightthickness=1)
        self.canvas.pack(pady=5)

        # ── Status / Info Label ───────────────────────────────────
        # Acts like a status bar — updated live during animation
        # to show which node is being explored and final results.
        self.info_label = tk.Label(
            root, text="Click an algorithm below to animate node exploration and final path.",
            font=("Consolas", 11, "bold"), bg="#313244", fg="#a6e3a1", width=90, pady=6
        )
        self.info_label.pack(pady=6)

        # ── Button Row ────────────────────────────────────────────
        # A horizontal frame holding 5 buttons, one per algorithm + Reset.
        # Each button calls the corresponding animate_* method when clicked.
        btn_frame = tk.Frame(root, bg="#1e1e2e")
        btn_frame.pack(pady=6)

        # Button 1 – DFS (Uninformed, uses a Stack)
        tk.Button(btn_frame, text="1. Run DFS (Exp 3)", command=self.animate_dfs,
                  bg="#f38ba8", fg="#11111b", font=("Arial", 10, "bold"),
                  width=18, pady=5).grid(row=0, column=0, padx=5)

        # Button 2 – BFS (Uninformed, uses a Queue)
        tk.Button(btn_frame, text="2. Run BFS (Exp 4)", command=self.animate_bfs,
                  bg="#fab387", fg="#11111b", font=("Arial", 10, "bold"),
                  width=18, pady=5).grid(row=0, column=1, padx=5)

        # Button 3 – Greedy Best-First (Informed, uses only h(n))
        tk.Button(btn_frame, text="3. Run Greedy (Exp 5)", command=self.animate_greedy,
                  bg="#89b4fa", fg="#11111b", font=("Arial", 10, "bold"),
                  width=19, pady=5).grid(row=0, column=2, padx=5)

        # Button 4 – A* Search (Informed, uses g(n) + h(n) — most optimal)
        tk.Button(btn_frame, text="4. Run A* Search (Exp 6)", command=self.animate_astar,
                  bg="#a6e3a1", fg="#11111b", font=("Arial", 10, "bold"),
                  width=20, pady=5).grid(row=0, column=3, padx=5)

        # Button 5 – Reset: clears highlights and redraws the plain graph
        tk.Button(btn_frame, text="Reset Map", command=lambda: self.draw_graph(),
                  bg="#cba6f7", fg="#11111b", font=("Arial", 10, "bold"),
                  width=12, pady=5).grid(row=0, column=4, padx=5)

        # Draw the initial (un-highlighted) campus graph on startup
        self.draw_graph()

    # ── draw_graph() ──────────────────────────────────────────────
    # PURPOSE: Renders (or re-renders) the entire graph on the canvas.
    # Called on startup, on Reset, and after every animation step.
    #
    # PARAMETERS:
    #   explored   – list of nodes already visited (shown in Blue)
    #   final_path – list of nodes on the best path (shown in Green)
    #   active     – the node currently being expanded (shown in Yellow)
    def draw_graph(self, explored=None, final_path=None, active=None):
        self.canvas.delete("all")   # Clear everything from previous frame

        # Default to empty lists if no arguments passed (initial draw)
        explored   = explored   or []
        final_path = final_path or []

        # ── Draw Directed Edges & Edge Weight Labels ───────────────
        for u in graph:
            x1, y1 = POSITIONS[u]                   # Canvas (x,y) of source node
            for v, weight in graph[u].items():
                x2, y2 = POSITIONS[v]               # Canvas (x,y) of target node

                # Check if this edge is part of the final solution path.
                # An edge (u→v) is a path edge if both u and v are in final_path
                # AND they are adjacent in the path (index difference == 1).
                is_path_edge = (u in final_path and v in final_path and
                                abs(final_path.index(u) - final_path.index(v)) == 1)

                # Highlight path edges green; all others stay grey
                color = "#a6e3a1" if is_path_edge else "#585b70"
                width = 4         if is_path_edge else 2

                # Draw the directed arrow line between the two nodes
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, arrow=tk.LAST)

                # Draw the edge weight label at the midpoint of the edge
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 10
                self.canvas.create_text(mx, my, text=f"cost={weight}", fill="#f9e2af", font=("Arial", 9, "bold"))

        # ── Draw Nodes (Ovals + Labels) ────────────────────────────
        # Color-coding:
        #   🟡 Yellow (#f9e2af) → Node currently being expanded
        #   🟢 Green  (#a6e3a1) → Node is on the final solution path
        #   🔵 Blue   (#89b4fa) → Node has already been explored
        #   ⬛ Dark   (#313244) → Node not yet visited
        for node, (x, y) in POSITIONS.items():
            if node == active:
                fill_color = "#f9e2af"  # Yellow = Currently expanding
            elif node in final_path:
                fill_color = "#a6e3a1"  # Green = Final Optimal Path
            elif node in explored:
                fill_color = "#89b4fa"  # Blue = Visited/Explored
            else:
                fill_color = "#313244"  # Default Dark = Unvisited

            # Use dark text on light nodes, light text on dark nodes
            text_color = "#11111b" if fill_color != "#313244" else "#cdd6f4"

            # Draw the oval shape representing the campus building
            self.canvas.create_oval(x - 48, y - 28, x + 48, y + 28,
                                    fill=fill_color, outline="#cdd6f4", width=2)
            # Draw the node name (building name) inside the oval
            self.canvas.create_text(x, y - 6, text=node, fill=text_color, font=("Arial", 9, "bold"))
            # Draw the heuristic value h(n) below the name for reference
            self.canvas.create_text(x, y + 11, text=f"h={heuristic[node]}", fill=text_color, font=("Arial", 8))

        # Force tkinter to refresh/redraw the window immediately
        # (needed because we're inside a loop, not the main event loop)
        self.root.update()

    # ── reconstruct() ─────────────────────────────────────────────
    # PURPOSE: Traces the solution path backward from GOAL → START
    #          using the `parent` dictionary built during search,
    #          then computes and returns the total travel cost.
    #
    # HOW IT WORKS:
    #   Every time a node is discovered during search, we record
    #   parent[node] = the node we came from.
    #   Starting from GOAL, we follow parent pointers back to START,
    #   building the path in reverse, then flip it.
    def reconstruct(self, parent):
        path, cost, curr = [], 0, GOAL   # Start tracing from the GOAL node

        # Walk backwards: GOAL → ... → START (parent[START] = None stops the loop)
        while curr is not None:
            path.append(curr)
            curr = parent[curr]          # Move to the node we came from

        path.reverse()                   # Flip so it reads START → ... → GOAL

        # Sum up the edge weights along the final path to get total cost
        for i in range(len(path) - 1):
            cost += graph[path[i]][path[i + 1]]

        return path, cost

    # ── run_animation() ───────────────────────────────────────────
    # PURPOSE: Generic animation engine shared by all 4 algorithms.
    #          Plays back the node exploration sequence step-by-step,
    #          then reveals the final highlighted path.
    #
    # PARAMETERS:
    #   algo_name – string label shown in the status bar (e.g. "DFS")
    #   traversal – ordered list of nodes explored by the algorithm
    #   path      – the final solution path from reconstruct()
    #   cost      – total cost of the solution path
    def run_animation(self, algo_name, traversal, path, cost):
        explored_so_far = []   # Accumulates nodes explored so far (for blue coloring)

        # Step through each explored node one at a time
        for node in traversal:
            explored_so_far.append(node)

            # Update the status bar to show which node is being expanded
            self.info_label.config(text=f"[{algo_name}] Exploring Node: {node} (h={heuristic[node]})...")

            # Redraw the graph: all previously explored nodes blue, current one yellow
            self.draw_graph(explored=explored_so_far, active=node)

            # Wait 0.55 seconds before moving to the next step (visible animation)
            time.sleep(0.55)

        # After all nodes explored, highlight the final solution path in green
        self.draw_graph(explored=explored_so_far, final_path=path)

        # Show final summary in the status bar
        self.info_label.config(
            text=f"{algo_name} Done! | Explored: {len(traversal)} nodes | Total Cost: {cost} | Path: {' -> '.join(path)}"
        )

    # ─────────────────────────────────────────────────────────────
    #  ALGORITHM 1 — DFS  (Depth-First Search)  [Experiment 3]
    #  Type: Uninformed (Blind) Search
    #  Data Structure: STACK (Last-In, First-Out)
    #  Strategy: Always explore the DEEPEST (most recently added) node first.
    #  Guarantee: Finds A path — NOT necessarily the optimal/cheapest one.
    # ─────────────────────────────────────────────────────────────
    def animate_dfs(self):
        # stack    – LIFO list; we use .pop() which removes from the END
        # traversal– records the order in which nodes were fully expanded
        # parent   – tracks how each node was reached (for path reconstruction)
        stack, traversal, parent = [START], [], {START: None}

        while stack:
            node = stack.pop()              # Pop from END = LIFO = Depth-First

            if node not in traversal:       # Only process unvisited nodes
                traversal.append(node)      # Mark as visited/explored

                if node == GOAL:            # Stop as soon as GOAL is found
                    break

                # Add children in REVERSED order so the first neighbor
                # in the graph is processed first (leftmost path priority)
                for child in reversed(list(graph[node].keys())):
                    if child not in traversal:
                        if child not in parent:         # Only record first discovery
                            parent[child] = node        # child was reached from node
                        stack.append(child)             # Push to stack for later

        path, cost = self.reconstruct(parent)
        self.run_animation("DFS (Exp 3)", traversal, path, cost)

    # ─────────────────────────────────────────────────────────────
    #  ALGORITHM 2 — BFS  (Breadth-First Search)  [Experiment 4]
    #  Type: Uninformed (Blind) Search
    #  Data Structure: QUEUE (First-In, First-Out)
    #  Strategy: Explore all nodes at current depth before going deeper.
    #  Guarantee: Finds the path with the FEWEST HOPS (not lowest cost).
    # ─────────────────────────────────────────────────────────────
    def animate_bfs(self):
        # queue    – FIFO list; we use .pop(0) which removes from the FRONT
        # traversal– records the order nodes were expanded (level by level)
        # parent   – tracks how each node was reached (for path reconstruction)
        queue, traversal, parent = [START], [], {START: None}

        while queue:
            node = queue.pop(0)             # Dequeue from FRONT = FIFO = Breadth-First

            if node not in traversal:       # Skip already-visited nodes
                traversal.append(node)      # Mark as explored

                if node == GOAL:            # Stop when goal is found
                    break

                # Add all unvisited, un-queued neighbors to the back of the queue
                for child in graph[node]:
                    if child not in traversal and child not in queue:
                        parent[child] = node    # Record how child was discovered
                        queue.append(child)     # Enqueue for future processing

        path, cost = self.reconstruct(parent)
        self.run_animation("BFS (Exp 4)", traversal, path, cost)

    # ─────────────────────────────────────────────────────────────
    #  ALGORITHM 3 — Greedy Best-First Search  [Experiment 5]
    #  Type: Informed Search (uses heuristic h(n))
    #  Strategy: Always expand the node with the LOWEST h(n) first.
    #            Ignores actual cost g(n) — purely heuristic-driven.
    #  Guarantee: Fast, but NOT always optimal (can get misled by h(n)).
    # ─────────────────────────────────────────────────────────────
    def animate_greedy(self):
        # open_list   – nodes discovered but not yet expanded (frontier)
        # closed_list – nodes already fully expanded (visited)
        # parent      – tracks how each node was reached
        open_list, closed_list, parent = [START], [], {START: None}

        while open_list:
            # Pick the node from open_list with the SMALLEST heuristic value h(n)
            # This is the "greedy" choice — always go toward what looks closest to goal
            best = min(open_list, key=lambda n: heuristic[n])

            open_list.remove(best)      # Remove from frontier
            closed_list.append(best)    # Move to expanded/closed set

            if best == GOAL:            # Stop if goal reached
                break

            # Add unvisited neighbors to the frontier
            for nb in graph[best]:
                if nb not in closed_list and nb not in open_list:
                    parent[nb] = best       # Record how nb was discovered
                    open_list.append(nb)    # Add to frontier for future expansion

        path, cost = self.reconstruct(parent)
        # closed_list is passed as traversal (the exploration order)
        self.run_animation("Greedy Best-First (Exp 5)", closed_list, path, cost)

    # ─────────────────────────────────────────────────────────────
    #  ALGORITHM 4 — A* Search  [Experiment 6]
    #  Type: Informed Search (uses both actual cost AND heuristic)
    #  Strategy: Expand the node with the lowest f(n) = g(n) + h(n)
    #    where:
    #      g(n) = actual cost from START to node n (known/exact)
    #      h(n) = estimated cost from n to GOAL (heuristic/guess)
    #      f(n) = total estimated cost of cheapest path through n
    #  Guarantee: OPTIMAL and COMPLETE (given admissible heuristic h(n) ≤ true cost)
    #             A* is the gold standard — finds the truly cheapest path.
    # ─────────────────────────────────────────────────────────────
    def animate_astar(self):
        # open_list   – frontier nodes to be expanded
        # closed_list – fully expanded nodes (won't be revisited)
        # g           – dict of actual costs: g[n] = cost from START to n
        # parent      – tracks how each node was reached (for reconstruction)
        open_list, closed_list, g, parent = [START], [], {START: 0}, {START: None}

        while open_list:
            # Pick node with lowest f(n) = g(n) + h(n) — the A* selection rule
            curr = min(open_list, key=lambda n: g[n] + heuristic[n])

            open_list.remove(curr)      # Remove from frontier
            closed_list.append(curr)    # Move to expanded set

            if curr == GOAL:            # Stop if goal found
                break

            # Examine each neighbor and its edge cost
            for nb, weight in graph[curr].items():
                new_g = g[curr] + weight    # Compute tentative g cost to reach nb via curr

                # Only update if this is a cheaper way to reach nb than any found before
                if nb not in g or new_g < g[nb]:
                    g[nb] = new_g           # Update g cost for nb
                    parent[nb] = curr       # Record best path to nb
                    if nb not in open_list:
                        open_list.append(nb)  # Add to frontier if not already there

        path, cost = self.reconstruct(parent)
        self.run_animation("A* Search (Exp 6)", closed_list, path, cost)


# ─────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────
# Standard Python idiom: only run the app if this file is executed
# directly (not when it's imported as a module by another script).
if __name__ == "__main__":
    root = tk.Tk()              # Create the main tkinter window
    app = CampusSearchGUI(root) # Instantiate our GUI class, builds the UI
    root.mainloop()             # Start the tkinter event loop — keeps window open
                                # and waits for user interactions (button clicks, etc.)
