# ─────────────────────────────────────────────────────────────────
#  IMPORTS
# ─────────────────────────────────────────────────────────────────
import tkinter as tk   # tkinter: Python's built-in GUI library used
                        # to create windows, canvases, buttons, labels, etc.
from tkinter import messagebox, ttk
import time             # time.sleep() is used to introduce a delay between
                        # animation frames so the user can see each step.

# ─────────────────────────────────────────────────────────────────
#  DEFAULT GRAPH  (Weighted Directed Adjacency Dictionary)
#  Used in Experiments 3, 4, 5 & 6
# ─────────────────────────────────────────────────────────────────
# Each KEY  → a campus building (node/state)
# Each VALUE → a dict of {neighbor: edge_cost}
#              representing direct connections and their travel cost.
# Edges are ONE-WAY (directed): e.g. Main_Gate → Admin_Block exists,
# but Admin_Block → Main_Gate does NOT.
# AI_DS_Lab has no outgoing edges {} because it is the GOAL node.
DEFAULT_GRAPH = {
    'Main_Gate':   {'Admin_Block': 2, 'Canteen': 1},  # From gate: Admin costs 2, Canteen costs 1
    'Admin_Block': {'Hostel': 3, 'Library': 2},        # From Admin: Hostel costs 3, Library costs 2
    'Canteen':     {'Auditorium': 2},                  # From Canteen: Auditorium costs 2
    'Hostel':      {'AI_DS_Lab': 5},                   # From Hostel: Lab costs 5 (expensive!)
    'Library':     {'AI_DS_Lab': 1},                   # From Library: Lab costs only 1 (cheapest route)
    'Auditorium':  {'AI_DS_Lab': 3},                   # From Auditorium: Lab costs 3
    'AI_DS_Lab':   {}                                  # GOAL node — no outgoing edges
}

# ─────────────────────────────────────────────────────────────────
#  DEFAULT HEURISTIC  h(n)  — Estimated cost from node n to the GOAL
#  Used by Informed Search algorithms: Greedy & A*
# ─────────────────────────────────────────────────────────────────
# h(n) is a hand-crafted estimate (not the real cost).
# Rule: h(GOAL) must always be 0 — the goal is 0 steps from itself.
# Lower h(n) means the node is "closer" to the goal in the algorithm's view.
# Library has h=1 (very close to goal), Main_Gate has h=5 (far away).
DEFAULT_HEURISTIC = {
    'Main_Gate': 5,    # Far from goal — 5 estimated units away
    'Admin_Block': 3,  # Moderately far
    'Canteen': 5,      # Also far (detour route)
    'Hostel': 5,       # Far — expensive path ahead
    'Library': 1,      # Very close to goal — cheapest path
    'Auditorium': 3,   # Moderate distance
    'AI_DS_Lab': 0     # This IS the goal → h = 0
}

# ─────────────────────────────────────────────────────────────────
#  DEFAULT POSITIONS  — Pixel (X, Y) coordinates for drawing each node
#                       on the tkinter Canvas (820 × 360 px)
# ─────────────────────────────────────────────────────────────────
# These control where each building's oval is drawn on screen.
# Laid out left-to-right to mimic a real campus map flow:
#   Main_Gate (left) → middle buildings → AI_DS_Lab (right/center)
DEFAULT_POSITIONS = {
    'Main_Gate':   (100, 200),   # Leftmost — entry point
    'Admin_Block': (280, 100),   # Upper-middle
    'Canteen':     (280, 300),   # Lower-middle
    'Hostel':      (500, 70),    # Upper-right cluster
    'Library':     (500, 190),   # Middle-right cluster
    'Auditorium':  (500, 310),   # Lower-right cluster
    'AI_DS_Lab':   (720, 200)    # Rightmost — the GOAL
}

# Top-level aliases for backwards compatibility
graph = DEFAULT_GRAPH
heuristic = DEFAULT_HEURISTIC
POSITIONS = DEFAULT_POSITIONS

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

        # Working dynamic copies of the graph topology and layout
        self.graph = {k: dict(v) for k, v in DEFAULT_GRAPH.items()}
        self.heuristic = dict(DEFAULT_HEURISTIC)
        self.positions = dict(DEFAULT_POSITIONS)
        self.start = START
        self.goal = GOAL

        # Set window title, size, and dark background color
        self.root.title("Campus Route Analyzer: DFS, BFS, Greedy & A* (Exp 3, 4, 5, 6)")
        self.root.geometry("880x600")        # Width x Height in pixels
        self.root.configure(bg="#1e1e2e")    # Dark purple-ish background

        # ── Top Title Label ───────────────────────────────────────
        tk.Label(
            root, text="Campus Navigation Search Visualizer (Uninformed vs Informed)",
            font=("Arial", 15, "bold"), bg="#1e1e2e", fg="#cdd6f4"
        ).pack(pady=8)

        # ── Canvas ────────────────────────────────────────────────
        # The drawing area where the campus graph (nodes + edges) is rendered.
        self.canvas = tk.Canvas(root, width=840, height=360, bg="#181825", highlightthickness=1)
        self.canvas.pack(pady=4)

        # ── Status / Info Label ───────────────────────────────────
        self.info_label = tk.Label(
            root, text="Click an algorithm below to animate node exploration and final path.",
            font=("Consolas", 10, "bold"), bg="#313244", fg="#a6e3a1", width=95, pady=6
        )
        self.info_label.pack(pady=5)

        # ── Control Row 1: Algorithm Execution Buttons ─────────────
        btn_frame = tk.Frame(root, bg="#1e1e2e")
        btn_frame.pack(pady=3)

        # Button 1 – DFS (Uninformed, uses a Stack)
        tk.Button(btn_frame, text="1. Run DFS (Exp 3)", command=self.animate_dfs,
                  bg="#f38ba8", fg="#11111b", font=("Arial", 10, "bold"),
                  width=18, pady=4).grid(row=0, column=0, padx=4)

        # Button 2 – BFS (Uninformed, uses a Queue)
        tk.Button(btn_frame, text="2. Run BFS (Exp 4)", command=self.animate_bfs,
                  bg="#fab387", fg="#11111b", font=("Arial", 10, "bold"),
                  width=18, pady=4).grid(row=0, column=1, padx=4)

        # Button 3 – Greedy Best-First (Informed, uses only h(n))
        tk.Button(btn_frame, text="3. Run Greedy (Exp 5)", command=self.animate_greedy,
                  bg="#89b4fa", fg="#11111b", font=("Arial", 10, "bold"),
                  width=19, pady=4).grid(row=0, column=2, padx=4)

        # Button 4 – A* Search (Informed, uses g(n) + h(n) — most optimal)
        tk.Button(btn_frame, text="4. Run A* Search (Exp 6)", command=self.animate_astar,
                  bg="#a6e3a1", fg="#11111b", font=("Arial", 10, "bold"),
                  width=20, pady=4).grid(row=0, column=3, padx=4)

        # ── Control Row 2: Customization & Map Tools ───────────────
        tools_frame = tk.Frame(root, bg="#1e1e2e")
        tools_frame.pack(pady=4)

        # Button – Add Custom Node
        tk.Button(tools_frame, text="➕ Add Node", command=self.open_add_node_dialog,
                  bg="#cba6f7", fg="#11111b", font=("Arial", 10, "bold"),
                  width=15, pady=4).grid(row=0, column=0, padx=4)

        # Button – Add Custom Edge
        tk.Button(tools_frame, text="🔗 Add Edge", command=self.open_add_edge_dialog,
                  bg="#b4befe", fg="#11111b", font=("Arial", 10, "bold"),
                  width=15, pady=4).grid(row=0, column=1, padx=4)

        # Button – Clear Highlights
        tk.Button(tools_frame, text="🧹 Clear Highlights", command=lambda: self.draw_graph(),
                  bg="#94e2d5", fg="#11111b", font=("Arial", 10, "bold"),
                  width=16, pady=4).grid(row=0, column=2, padx=4)

        # Button – Restore Default Map
        tk.Button(tools_frame, text="↺ Default Campus", command=self.reset_to_default_map,
                  bg="#f9e2af", fg="#11111b", font=("Arial", 10, "bold"),
                  width=16, pady=4).grid(row=0, column=3, padx=4)

        # Draw the initial campus graph on startup
        self.draw_graph()

    # ── reset_to_default_map() ────────────────────────────────────
    # Restores original campus buildings, positions, heuristics, and edges.
    def reset_to_default_map(self):
        self.graph = {k: dict(v) for k, v in DEFAULT_GRAPH.items()}
        self.heuristic = dict(DEFAULT_HEURISTIC)
        self.positions = dict(DEFAULT_POSITIONS)
        self.draw_graph()
        self.info_label.config(text="Map reset to default campus topology.")

    # ── open_add_node_dialog() ────────────────────────────────────
    # Opens a modal dialog allowing users to add their own custom node.
    def open_add_node_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Custom Node")
        dialog.geometry("440x480")
        dialog.configure(bg="#1e1e2e")
        dialog.transient(self.root)
        dialog.grab_set()

        # Canvas click coordinate picker helper
        def on_canvas_click(event):
            x_entry.delete(0, tk.END)
            x_entry.insert(0, str(int(event.x)))
            y_entry.delete(0, tk.END)
            y_entry.insert(0, str(int(event.y)))
            coord_hint.config(text=f"📍 Canvas picked: ({event.x}, {event.y})")

        bind_id = self.canvas.bind("<Button-1>", on_canvas_click)

        def on_dialog_close():
            self.canvas.unbind("<Button-1>", bind_id)
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)

        tk.Label(dialog, text="➕ Add Custom Node", font=("Arial", 13, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(pady=10)

        form_frame = tk.Frame(dialog, bg="#1e1e2e")
        form_frame.pack(padx=20, pady=4, fill="x")

        # 1. Node Name
        tk.Label(form_frame, text="Node Name:", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=0, sticky="w", pady=4)
        name_entry = tk.Entry(form_frame, font=("Arial", 10), bg="#313244", fg="#ffffff", insertbackground="white")
        name_entry.grid(row=0, column=1, sticky="ew", pady=4)
        name_entry.insert(0, f"Node_{len(self.positions) + 1}")

        # 2. Heuristic h(n)
        tk.Label(form_frame, text="Heuristic h(n):", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").grid(row=1, column=0, sticky="w", pady=4)
        h_entry = tk.Entry(form_frame, font=("Arial", 10), bg="#313244", fg="#ffffff", insertbackground="white")
        h_entry.grid(row=1, column=1, sticky="ew", pady=4)
        h_entry.insert(0, "2")

        # 3. Canvas Positions X and Y
        tk.Label(form_frame, text="Canvas X (50-780):", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").grid(row=2, column=0, sticky="w", pady=4)
        x_entry = tk.Entry(form_frame, font=("Arial", 10), bg="#313244", fg="#ffffff", insertbackground="white")
        x_entry.grid(row=2, column=1, sticky="ew", pady=4)
        x_entry.insert(0, "390")

        tk.Label(form_frame, text="Canvas Y (30-330):", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").grid(row=3, column=0, sticky="w", pady=4)
        y_entry = tk.Entry(form_frame, font=("Arial", 10), bg="#313244", fg="#ffffff", insertbackground="white")
        y_entry.grid(row=3, column=1, sticky="ew", pady=4)
        y_entry.insert(0, "200")

        coord_hint = tk.Label(form_frame, text="💡 Tip: Click anywhere on the map to set (X, Y)",
                              font=("Arial", 8, "italic"), bg="#1e1e2e", fg="#89b4fa")
        coord_hint.grid(row=4, column=0, columnspan=2, pady=4)

        # 4. Incoming Connection: Connect FROM existing node
        tk.Label(form_frame, text="Connect FROM:", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").grid(row=5, column=0, sticky="w", pady=4)
        existing_nodes = ["(None)"] + list(self.positions.keys())
        from_combo = ttk.Combobox(form_frame, values=existing_nodes, state="readonly")
        from_combo.current(0)
        from_combo.grid(row=5, column=1, sticky="ew", pady=4)

        tk.Label(form_frame, text="Incoming Cost:", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").grid(row=6, column=0, sticky="w", pady=4)
        from_cost_entry = tk.Entry(form_frame, font=("Arial", 10), bg="#313244", fg="#ffffff", insertbackground="white")
        from_cost_entry.grid(row=6, column=1, sticky="ew", pady=4)
        from_cost_entry.insert(0, "2")

        # 5. Outgoing Connection: Connect TO existing node
        tk.Label(form_frame, text="Connect TO:", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").grid(row=7, column=0, sticky="w", pady=4)
        to_combo = ttk.Combobox(form_frame, values=existing_nodes, state="readonly")
        to_combo.current(0)
        to_combo.grid(row=7, column=1, sticky="ew", pady=4)

        tk.Label(form_frame, text="Outgoing Cost:", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").grid(row=8, column=0, sticky="w", pady=4)
        to_cost_entry = tk.Entry(form_frame, font=("Arial", 10), bg="#313244", fg="#ffffff", insertbackground="white")
        to_cost_entry.grid(row=8, column=1, sticky="ew", pady=4)
        to_cost_entry.insert(0, "2")

        form_frame.columnconfigure(1, weight=1)

        def save_node():
            node_name = name_entry.get().strip().replace(" ", "_")
            if not node_name:
                messagebox.showerror("Validation Error", "Node name cannot be empty.", parent=dialog)
                return
            if node_name in self.positions:
                messagebox.showerror("Validation Error", f"Node '{node_name}' already exists.", parent=dialog)
                return

            try:
                h_val = float(h_entry.get().strip())
                if h_val < 0:
                    raise ValueError
                h_val = int(h_val) if h_val.is_integer() else h_val
            except ValueError:
                messagebox.showerror("Validation Error", "Heuristic h(n) must be a non-negative number.", parent=dialog)
                return

            try:
                x_val = int(x_entry.get().strip())
                y_val = int(y_entry.get().strip())
                x_val = max(50, min(790, x_val))
                y_val = max(30, min(330, y_val))
            except ValueError:
                messagebox.showerror("Validation Error", "Coordinates X and Y must be valid integers.", parent=dialog)
                return

            # Register new node
            self.positions[node_name] = (x_val, y_val)
            self.heuristic[node_name] = h_val
            self.graph[node_name] = {}

            # Handle incoming edge
            from_node = from_combo.get()
            if from_node != "(None)" and from_node in self.graph:
                try:
                    c = int(from_cost_entry.get().strip())
                    self.graph[from_node][node_name] = max(1, c)
                except ValueError:
                    pass

            # Handle outgoing edge
            to_node = to_combo.get()
            if to_node != "(None)" and to_node in self.positions:
                try:
                    c = int(to_cost_entry.get().strip())
                    self.graph[node_name][to_node] = max(1, c)
                except ValueError:
                    pass

            on_dialog_close()
            self.draw_graph()
            self.info_label.config(text=f"✅ Added node '{node_name}' (h={h_val}) at ({x_val}, {y_val})")

        btn_box = tk.Frame(dialog, bg="#1e1e2e")
        btn_box.pack(pady=10)

        tk.Button(btn_box, text="Save Node", command=save_node,
                  bg="#a6e3a1", fg="#11111b", font=("Arial", 10, "bold"),
                  width=12, pady=4).pack(side="left", padx=6)
        tk.Button(btn_box, text="Cancel", command=on_dialog_close,
                  bg="#f38ba8", fg="#11111b", font=("Arial", 10, "bold"),
                  width=10, pady=4).pack(side="left", padx=6)

    # ── open_add_edge_dialog() ────────────────────────────────────
    # Opens a modal dialog allowing users to connect two nodes with a directed edge.
    def open_add_edge_dialog(self):
        if len(self.positions) < 2:
            messagebox.showinfo("Add Edge", "At least two nodes are required to create an edge.", parent=self.root)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Directed Edge")
        dialog.geometry("380x260")
        dialog.configure(bg="#1e1e2e")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="🔗 Add Directed Edge", font=("Arial", 13, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").pack(pady=10)

        form_frame = tk.Frame(dialog, bg="#1e1e2e")
        form_frame.pack(padx=20, pady=5, fill="x")

        nodes = list(self.positions.keys())

        tk.Label(form_frame, text="From Node:", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=0, sticky="w", pady=5)
        from_combo = ttk.Combobox(form_frame, values=nodes, state="readonly")
        from_combo.current(0)
        from_combo.grid(row=0, column=1, sticky="ew", pady=5)

        tk.Label(form_frame, text="To Node:", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").grid(row=1, column=0, sticky="w", pady=5)
        to_combo = ttk.Combobox(form_frame, values=nodes, state="readonly")
        to_combo.current(1 if len(nodes) > 1 else 0)
        to_combo.grid(row=1, column=1, sticky="ew", pady=5)

        tk.Label(form_frame, text="Edge Cost:", font=("Arial", 10, "bold"),
                 bg="#1e1e2e", fg="#cdd6f4").grid(row=2, column=0, sticky="w", pady=5)
        cost_entry = tk.Entry(form_frame, font=("Arial", 10), bg="#313244", fg="#ffffff", insertbackground="white")
        cost_entry.grid(row=2, column=1, sticky="ew", pady=5)
        cost_entry.insert(0, "2")

        form_frame.columnconfigure(1, weight=1)

        def save_edge():
            u = from_combo.get()
            v = to_combo.get()
            if u == v:
                messagebox.showerror("Error", "Self-loops are not allowed (From and To must be different).", parent=dialog)
                return
            try:
                c = int(cost_entry.get().strip())
                if c <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Edge cost must be a positive integer.", parent=dialog)
                return

            if u not in self.graph:
                self.graph[u] = {}
            self.graph[u][v] = c

            dialog.destroy()
            self.draw_graph()
            self.info_label.config(text=f"✅ Added edge: {u} ──(cost={c})──> {v}")

        btn_box = tk.Frame(dialog, bg="#1e1e2e")
        btn_box.pack(pady=12)

        tk.Button(btn_box, text="Save Edge", command=save_edge,
                  bg="#a6e3a1", fg="#11111b", font=("Arial", 10, "bold"),
                  width=12, pady=4).pack(side="left", padx=6)
        tk.Button(btn_box, text="Cancel", command=dialog.destroy,
                  bg="#f38ba8", fg="#11111b", font=("Arial", 10, "bold"),
                  width=10, pady=4).pack(side="left", padx=6)

    # ── draw_graph() ──────────────────────────────────────────────
    # PURPOSE: Renders (or re-renders) the entire graph on the canvas.
    def draw_graph(self, explored=None, final_path=None, active=None):
        self.canvas.delete("all")   # Clear everything from previous frame

        explored   = explored   or []
        final_path = final_path or []

        # ── Draw Directed Edges & Edge Weight Labels ───────────────
        for u in self.graph:
            if u not in self.positions:
                continue
            x1, y1 = self.positions[u]                   # Canvas (x,y) of source node
            for v, weight in self.graph[u].items():
                if v not in self.positions:
                    continue
                x2, y2 = self.positions[v]               # Canvas (x,y) of target node

                # Check if this edge is part of the final solution path
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
        for node, (x, y) in self.positions.items():
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
            h_val = self.heuristic.get(node, "?")
            self.canvas.create_text(x, y + 11, text=f"h={h_val}", fill=text_color, font=("Arial", 8))

        # Force tkinter to refresh/redraw the window immediately
        self.root.update()

    # ── reconstruct() ─────────────────────────────────────────────
    # Traces the solution path backward from GOAL → START using parent dict
    def reconstruct(self, parent):
        if self.goal not in parent:
            return [], 0  # Goal is unreachable in current graph

        path, cost, curr = [], 0, self.goal

        # Walk backwards: GOAL → ... → START
        while curr is not None:
            path.append(curr)
            curr = parent.get(curr)

        path.reverse()                   # Flip so it reads START → ... → GOAL

        # Sum up the edge weights along the final path to get total cost
        for i in range(len(path) - 1):
            cost += self.graph.get(path[i], {}).get(path[i + 1], 0)

        return path, cost

    # ── run_animation() ───────────────────────────────────────────
    # Generic animation engine shared by all 4 algorithms.
    def run_animation(self, algo_name, traversal, path, cost):
        explored_so_far = []

        # Step through each explored node one at a time
        for node in traversal:
            explored_so_far.append(node)
            h_val = self.heuristic.get(node, "?")
            self.info_label.config(text=f"[{algo_name}] Exploring Node: {node} (h={h_val})...")
            self.draw_graph(explored=explored_so_far, active=node)
            time.sleep(0.55)

        # After search completes:
        if path:
            self.draw_graph(explored=explored_so_far, final_path=path)
            self.info_label.config(
                text=f"{algo_name} Done! | Explored: {len(traversal)} nodes | Total Cost: {cost} | Path: {' -> '.join(path)}"
            )
        else:
            self.draw_graph(explored=explored_so_far)
            self.info_label.config(
                text=f"{algo_name} Finished | Explored: {len(traversal)} nodes | ❌ No reachable path to '{self.goal}'"
            )

    # ─────────────────────────────────────────────────────────────
    #  ALGORITHM 1 — DFS  (Depth-First Search)  [Experiment 3]
    # ─────────────────────────────────────────────────────────────
    def animate_dfs(self):
        stack, traversal, parent = [self.start], [], {self.start: None}

        while stack:
            node = stack.pop()              # Pop from END = LIFO = Depth-First

            if node not in traversal:
                traversal.append(node)

                if node == self.goal:
                    break

                for child in reversed(list(self.graph.get(node, {}).keys())):
                    if child not in traversal:
                        if child not in parent:
                            parent[child] = node
                        stack.append(child)

        path, cost = self.reconstruct(parent)
        self.run_animation("DFS (Exp 3)", traversal, path, cost)

    # ─────────────────────────────────────────────────────────────
    #  ALGORITHM 2 — BFS  (Breadth-First Search)  [Experiment 4]
    # ─────────────────────────────────────────────────────────────
    def animate_bfs(self):
        queue, traversal, parent = [self.start], [], {self.start: None}

        while queue:
            node = queue.pop(0)             # Dequeue from FRONT = FIFO = Breadth-First

            if node not in traversal:
                traversal.append(node)

                if node == self.goal:
                    break

                for child in self.graph.get(node, {}):
                    if child not in traversal and child not in queue:
                        parent[child] = node
                        queue.append(child)

        path, cost = self.reconstruct(parent)
        self.run_animation("BFS (Exp 4)", traversal, path, cost)

    # ─────────────────────────────────────────────────────────────
    #  ALGORITHM 3 — Greedy Best-First Search  [Experiment 5]
    # ─────────────────────────────────────────────────────────────
    def animate_greedy(self):
        open_list, closed_list, parent = [self.start], [], {self.start: None}

        while open_list:
            # Pick node from open_list with lowest h(n)
            best = min(open_list, key=lambda n: self.heuristic.get(n, 9999))

            open_list.remove(best)
            closed_list.append(best)

            if best == self.goal:
                break

            for nb in self.graph.get(best, {}):
                if nb not in closed_list and nb not in open_list:
                    parent[nb] = best
                    open_list.append(nb)

        path, cost = self.reconstruct(parent)
        self.run_animation("Greedy Best-First (Exp 5)", closed_list, path, cost)

    # ─────────────────────────────────────────────────────────────
    #  ALGORITHM 4 — A* Search  [Experiment 6]
    # ─────────────────────────────────────────────────────────────
    def animate_astar(self):
        open_list = [self.start]
        closed_list = []
        g = {self.start: 0}
        parent = {self.start: None}

        while open_list:
            # Pick node with lowest f(n) = g(n) + h(n)
            curr = min(open_list, key=lambda n: g[n] + self.heuristic.get(n, 9999))

            open_list.remove(curr)
            closed_list.append(curr)

            if curr == self.goal:
                break

            for nb, weight in self.graph.get(curr, {}).items():
                new_g = g[curr] + weight

                if nb not in g or new_g < g[nb]:
                    g[nb] = new_g
                    parent[nb] = curr
                    if nb not in open_list:
                        open_list.append(nb)

        path, cost = self.reconstruct(parent)
        self.run_animation("A* Search (Exp 6)", closed_list, path, cost)


# ─────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = CampusSearchGUI(root)
    root.mainloop()
