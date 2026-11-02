# ─────────────────────────────────────────────────────────────────
#  SEARCHFORGE — INTERACTIVE CUSTOM NODE GRAPH SEARCH VISUALIZER
# ─────────────────────────────────────────────────────────────────
#  This standalone application allows users to build, edit, and experiment
#  with custom graphs and heuristics, then visualize 4 search strategies:
#    1. Depth-First Search (DFS)
#    2. Breadth-First Search (BFS)
#    3. Greedy Best-First Search
#    4. A* Search
# ─────────────────────────────────────────────────────────────────

import tkinter as tk
from tkinter import messagebox, ttk
import time

# ─────────────────────────────────────────────────────────────────
#  DEFAULT CAMPUS TOPOLOGY (Initial Template)
# ─────────────────────────────────────────────────────────────────
DEFAULT_GRAPH = {
    'Main_Gate':   {'Admin_Block': 2, 'Canteen': 1},
    'Admin_Block': {'Hostel': 3, 'Library': 2},
    'Canteen':     {'Auditorium': 2},
    'Hostel':      {'AI_DS_Lab': 5},
    'Library':     {'AI_DS_Lab': 1},
    'Auditorium':  {'AI_DS_Lab': 3},
    'AI_DS_Lab':   {}
}

DEFAULT_HEURISTIC = {
    'Main_Gate': 5,
    'Admin_Block': 3,
    'Canteen': 5,
    'Hostel': 5,
    'Library': 1,
    'Auditorium': 3,
    'AI_DS_Lab': 0
}

DEFAULT_POSITIONS = {
    'Main_Gate':   (110, 200),
    'Admin_Block': (290, 100),
    'Canteen':     (290, 300),
    'Hostel':      (520, 70),
    'Library':     (520, 190),
    'Auditorium':  (520, 310),
    'AI_DS_Lab':   (750, 200)
}

DEFAULT_START = 'Main_Gate'
DEFAULT_GOAL  = 'AI_DS_Lab'


# ─────────────────────────────────────────────────────────────────
#  INTERACTIVE SEARCH GUI CLASS
# ─────────────────────────────────────────────────────────────────
class InteractiveSearchGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("SearchForge — Interactive Graph & Algorithm Studio")
        self.root.geometry("980x680")
        self.root.configure(bg="#1e1e2e")

        # Active dynamic state (isolated working copies)
        self.graph = {k: dict(v) for k, v in DEFAULT_GRAPH.items()}
        self.heuristic = dict(DEFAULT_HEURISTIC)
        self.positions = dict(DEFAULT_POSITIONS)
        self.start_node = DEFAULT_START
        self.goal_node = DEFAULT_GOAL

        # Setup GUI Components
        self._build_header()
        self._build_canvas()
        self._build_status_bar()
        self._build_endpoints_bar()
        self._build_algorithm_controls()
        self._build_graph_editing_controls()

        # Initial render
        self.draw_graph()

    # ── UI Construction Helpers ───────────────────────────────────

    def _build_header(self):
        header_frame = tk.Frame(self.root, bg="#1e1e2e")
        header_frame.pack(fill="x", pady=(10, 4))

        tk.Label(
            header_frame,
            text="SearchForge: Interactive Graph & Heuristic Search Studio",
            font=("Arial", 16, "bold"),
            bg="#1e1e2e",
            fg="#cdd6f4"
        ).pack()

        tk.Label(
            header_frame,
            text="Add your own custom buildings/nodes, connect routes with weights, and trace AI search strategies in real time.",
            font=("Arial", 9),
            bg="#1e1e2e",
            fg="#a6adc8"
        ).pack(pady=(2, 0))

    def _build_canvas(self):
        # Canvas dimensions: 940 x 360 px
        self.canvas = tk.Canvas(
            self.root,
            width=940,
            height=360,
            bg="#181825",
            highlightthickness=1,
            highlightbackground="#45475a"
        )
        self.canvas.pack(pady=6)

    def _build_status_bar(self):
        self.info_label = tk.Label(
            self.root,
            text="Ready. Select Start/Goal, add custom nodes, or run an algorithm below.",
            font=("Consolas", 10, "bold"),
            bg="#313244",
            fg="#a6e3a1",
            width=110,
            pady=6,
            relief="groove"
        )
        self.info_label.pack(pady=4)

    def _build_endpoints_bar(self):
        ep_frame = tk.Frame(self.root, bg="#1e1e2e")
        ep_frame.pack(pady=4)

        tk.Label(ep_frame, text="Start Node:", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#fab387").pack(side="left", padx=(0, 4))
        self.start_combo = ttk.Combobox(ep_frame, values=list(self.positions.keys()), state="readonly", width=14)
        self.start_combo.set(self.start_node)
        self.start_combo.pack(side="left", padx=(0, 16))
        self.start_combo.bind("<<ComboboxSelected>>", self._on_endpoint_change)

        tk.Label(ep_frame, text="Goal Node:", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#a6e3a1").pack(side="left", padx=(0, 4))
        self.goal_combo = ttk.Combobox(ep_frame, values=list(self.positions.keys()), state="readonly", width=14)
        self.goal_combo.set(self.goal_node)
        self.goal_combo.pack(side="left", padx=(0, 16))
        self.goal_combo.bind("<<ComboboxSelected>>", self._on_endpoint_change)

        tk.Label(
            ep_frame,
            text="💡 Tip: Click anywhere on canvas when adding a node to set coordinates",
            font=("Arial", 8, "italic"),
            bg="#1e1e2e",
            fg="#89b4fa"
        ).pack(side="left", padx=(10, 0))

    def _build_algorithm_controls(self):
        algo_frame = tk.Frame(self.root, bg="#1e1e2e")
        algo_frame.pack(pady=4)

        # 1. DFS
        tk.Button(
            algo_frame, text="1. Run DFS (Stack)", command=self.animate_dfs,
            bg="#f38ba8", fg="#11111b", font=("Arial", 9, "bold"), width=18, pady=4
        ).grid(row=0, column=0, padx=4)

        # 2. BFS
        tk.Button(
            algo_frame, text="2. Run BFS (Queue)", command=self.animate_bfs,
            bg="#fab387", fg="#11111b", font=("Arial", 9, "bold"), width=18, pady=4
        ).grid(row=0, column=1, padx=4)

        # 3. Greedy
        tk.Button(
            algo_frame, text="3. Run Greedy Best-First", command=self.animate_greedy,
            bg="#89b4fa", fg="#11111b", font=("Arial", 9, "bold"), width=22, pady=4
        ).grid(row=0, column=2, padx=4)

        # 4. A*
        tk.Button(
            algo_frame, text="4. Run A* Search", command=self.animate_astar,
            bg="#a6e3a1", fg="#11111b", font=("Arial", 9, "bold"), width=18, pady=4
        ).grid(row=0, column=3, padx=4)

    def _build_graph_editing_controls(self):
        edit_frame = tk.Frame(self.root, bg="#1e1e2e")
        edit_frame.pack(pady=4)

        # Add Node Button
        tk.Button(
            edit_frame, text="➕ Add Node", command=self.open_add_node_dialog,
            bg="#cba6f7", fg="#11111b", font=("Arial", 9, "bold"), width=14, pady=4
        ).grid(row=0, column=0, padx=4)

        # Add Edge Button
        tk.Button(
            edit_frame, text="🔗 Add Edge", command=self.open_add_edge_dialog,
            bg="#b4befe", fg="#11111b", font=("Arial", 9, "bold"), width=14, pady=4
        ).grid(row=0, column=1, padx=4)

        # Delete Node Button
        tk.Button(
            edit_frame, text="🗑️ Delete Node", command=self.open_delete_node_dialog,
            bg="#eba0ac", fg="#11111b", font=("Arial", 9, "bold"), width=14, pady=4
        ).grid(row=0, column=2, padx=4)

        # Clear Highlights
        tk.Button(
            edit_frame, text="🧹 Clear Highlights", command=lambda: self.draw_graph(),
            bg="#94e2d5", fg="#11111b", font=("Arial", 9, "bold"), width=16, pady=4
        ).grid(row=0, column=3, padx=4)

        # Reset Map to Default
        tk.Button(
            edit_frame, text="↺ Reset to Default", command=self.reset_to_default,
            bg="#f9e2af", fg="#11111b", font=("Arial", 9, "bold"), width=16, pady=4
        ).grid(row=0, column=4, padx=4)

    # ── State & Endpoint Updates ──────────────────────────────────

    def _update_comboboxes(self):
        nodes = list(self.positions.keys())
        self.start_combo['values'] = nodes
        self.goal_combo['values'] = nodes
        if self.start_node not in nodes and nodes:
            self.start_node = nodes[0]
        if self.goal_node not in nodes and nodes:
            self.goal_node = nodes[-1]
        self.start_combo.set(self.start_node)
        self.goal_combo.set(self.goal_node)

    def _on_endpoint_change(self, event=None):
        self.start_node = self.start_combo.get()
        self.goal_node = self.goal_combo.get()
        self.draw_graph()
        self.info_label.config(text=f"Updated endpoints: Start = '{self.start_node}', Goal = '{self.goal_node}'")

    def reset_to_default(self):
        self.graph = {k: dict(v) for k, v in DEFAULT_GRAPH.items()}
        self.heuristic = dict(DEFAULT_HEURISTIC)
        self.positions = dict(DEFAULT_POSITIONS)
        self.start_node = DEFAULT_START
        self.goal_node = DEFAULT_GOAL
        self._update_comboboxes()
        self.draw_graph()
        self.info_label.config(text="Map restored to default campus topology.")

    # ── Dialogs: Add Node ─────────────────────────────────────────

    def open_add_node_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Custom Node")
        dialog.geometry("450x500")
        dialog.configure(bg="#1e1e2e")
        dialog.transient(self.root)
        dialog.grab_set()

        # Canvas click handler to capture coordinates
        def on_canvas_click(event):
            x_entry.delete(0, tk.END)
            x_entry.insert(0, str(int(event.x)))
            y_entry.delete(0, tk.END)
            y_entry.insert(0, str(int(event.y)))
            coord_hint.config(text=f"📍 Canvas picked: ({event.x}, {event.y})", fg="#a6e3a1")

        bind_id = self.canvas.bind("<Button-1>", on_canvas_click)

        def cleanup_and_close():
            self.canvas.unbind("<Button-1>", bind_id)
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", cleanup_and_close)

        tk.Label(
            dialog, text="➕ Add Custom Node", font=("Arial", 13, "bold"),
            bg="#1e1e2e", fg="#cdd6f4"
        ).pack(pady=10)

        form = tk.Frame(dialog, bg="#1e1e2e")
        form.pack(padx=22, pady=4, fill="x")

        # 1. Node Name
        tk.Label(form, text="Node Name:", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=0, sticky="w", pady=4)
        name_entry = tk.Entry(form, font=("Arial", 9), bg="#313244", fg="#ffffff", insertbackground="white")
        name_entry.grid(row=0, column=1, sticky="ew", pady=4)
        name_entry.insert(0, f"Node_{len(self.positions) + 1}")

        # 2. Heuristic Value
        tk.Label(form, text="Heuristic h(n):", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").grid(row=1, column=0, sticky="w", pady=4)
        h_entry = tk.Entry(form, font=("Arial", 9), bg="#313244", fg="#ffffff", insertbackground="white")
        h_entry.grid(row=1, column=1, sticky="ew", pady=4)
        h_entry.insert(0, "2")

        # 3. Canvas Positions
        tk.Label(form, text="Canvas X (50–900):", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").grid(row=2, column=0, sticky="w", pady=4)
        x_entry = tk.Entry(form, font=("Arial", 9), bg="#313244", fg="#ffffff", insertbackground="white")
        x_entry.grid(row=2, column=1, sticky="ew", pady=4)
        x_entry.insert(0, "400")

        tk.Label(form, text="Canvas Y (30–330):", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").grid(row=3, column=0, sticky="w", pady=4)
        y_entry = tk.Entry(form, font=("Arial", 9), bg="#313244", fg="#ffffff", insertbackground="white")
        y_entry.grid(row=3, column=1, sticky="ew", pady=4)
        y_entry.insert(0, "200")

        coord_hint = tk.Label(
            form, text="💡 Tip: Click anywhere directly on the map to pick (X, Y)",
            font=("Arial", 8, "italic"), bg="#1e1e2e", fg="#89b4fa"
        )
        coord_hint.grid(row=4, column=0, columnspan=2, pady=4)

        # 4. Optional Incoming Connection
        tk.Label(form, text="Connect FROM:", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").grid(row=5, column=0, sticky="w", pady=4)
        existing_nodes = ["(None)"] + list(self.positions.keys())
        from_combo = ttk.Combobox(form, values=existing_nodes, state="readonly")
        from_combo.current(0)
        from_combo.grid(row=5, column=1, sticky="ew", pady=4)

        tk.Label(form, text="Incoming Cost:", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").grid(row=6, column=0, sticky="w", pady=4)
        from_cost_entry = tk.Entry(form, font=("Arial", 9), bg="#313244", fg="#ffffff", insertbackground="white")
        from_cost_entry.grid(row=6, column=1, sticky="ew", pady=4)
        from_cost_entry.insert(0, "2")

        # 5. Optional Outgoing Connection
        tk.Label(form, text="Connect TO:", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").grid(row=7, column=0, sticky="w", pady=4)
        to_combo = ttk.Combobox(form, values=existing_nodes, state="readonly")
        to_combo.current(0)
        to_combo.grid(row=7, column=1, sticky="ew", pady=4)

        tk.Label(form, text="Outgoing Cost:", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").grid(row=8, column=0, sticky="w", pady=4)
        to_cost_entry = tk.Entry(form, font=("Arial", 9), bg="#313244", fg="#ffffff", insertbackground="white")
        to_cost_entry.grid(row=8, column=1, sticky="ew", pady=4)
        to_cost_entry.insert(0, "2")

        form.columnconfigure(1, weight=1)

        def save_node():
            name = name_entry.get().strip().replace(" ", "_")
            if not name:
                messagebox.showerror("Invalid Input", "Node name cannot be blank.", parent=dialog)
                return
            if name in self.positions:
                messagebox.showerror("Invalid Input", f"Node '{name}' already exists in graph.", parent=dialog)
                return

            try:
                h_val = float(h_entry.get().strip())
                if h_val < 0:
                    raise ValueError
                h_val = int(h_val) if h_val.is_integer() else h_val
            except ValueError:
                messagebox.showerror("Invalid Input", "Heuristic h(n) must be a non-negative number.", parent=dialog)
                return

            try:
                x_val = int(x_entry.get().strip())
                y_val = int(y_entry.get().strip())
                x_val = max(50, min(890, x_val))
                y_val = max(30, min(330, y_val))
            except ValueError:
                messagebox.showerror("Invalid Input", "Coordinates X and Y must be valid integers.", parent=dialog)
                return

            # Register new node
            self.positions[name] = (x_val, y_val)
            self.heuristic[name] = h_val
            self.graph[name] = {}

            # Add incoming connection if requested
            src = from_combo.get()
            if src != "(None)" and src in self.graph:
                try:
                    c = int(from_cost_entry.get().strip())
                    self.graph[src][name] = max(1, c)
                except ValueError:
                    pass

            # Add outgoing connection if requested
            dst = to_combo.get()
            if dst != "(None)" and dst in self.positions:
                try:
                    c = int(to_cost_entry.get().strip())
                    self.graph[name][dst] = max(1, c)
                except ValueError:
                    pass

            cleanup_and_close()
            self._update_comboboxes()
            self.draw_graph()
            self.info_label.config(text=f"✅ Created node '{name}' (h={h_val}) at ({x_val}, {y_val})")

        btn_box = tk.Frame(dialog, bg="#1e1e2e")
        btn_box.pack(pady=12)

        tk.Button(
            btn_box, text="Save Node", command=save_node,
            bg="#a6e3a1", fg="#11111b", font=("Arial", 9, "bold"), width=12, pady=4
        ).pack(side="left", padx=6)

        tk.Button(
            btn_box, text="Cancel", command=cleanup_and_close,
            bg="#f38ba8", fg="#11111b", font=("Arial", 9, "bold"), width=10, pady=4
        ).pack(side="left", padx=6)

    # ── Dialogs: Add Edge ─────────────────────────────────────────

    def open_add_edge_dialog(self):
        if len(self.positions) < 2:
            messagebox.showinfo("Add Edge", "At least two nodes are required to form an edge.", parent=self.root)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Directed Edge")
        dialog.geometry("380x260")
        dialog.configure(bg="#1e1e2e")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog, text="🔗 Add Directed Edge", font=("Arial", 13, "bold"),
            bg="#1e1e2e", fg="#cdd6f4"
        ).pack(pady=10)

        form = tk.Frame(dialog, bg="#1e1e2e")
        form.pack(padx=20, pady=6, fill="x")

        nodes = list(self.positions.keys())

        tk.Label(form, text="From Node:", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=0, sticky="w", pady=5)
        from_combo = ttk.Combobox(form, values=nodes, state="readonly")
        from_combo.current(0)
        from_combo.grid(row=0, column=1, sticky="ew", pady=5)

        tk.Label(form, text="To Node:", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").grid(row=1, column=0, sticky="w", pady=5)
        to_combo = ttk.Combobox(form, values=nodes, state="readonly")
        to_combo.current(1 if len(nodes) > 1 else 0)
        to_combo.grid(row=1, column=1, sticky="ew", pady=5)

        tk.Label(form, text="Edge Cost:", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").grid(row=2, column=0, sticky="w", pady=5)
        cost_entry = tk.Entry(form, font=("Arial", 9), bg="#313244", fg="#ffffff", insertbackground="white")
        cost_entry.grid(row=2, column=1, sticky="ew", pady=5)
        cost_entry.insert(0, "2")

        form.columnconfigure(1, weight=1)

        def save_edge():
            u = from_combo.get()
            v = to_combo.get()
            if u == v:
                messagebox.showerror("Invalid Edge", "Self-loops are not allowed (source and destination must differ).", parent=dialog)
                return

            try:
                c = int(cost_entry.get().strip())
                if c <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Edge", "Edge cost must be a positive integer.", parent=dialog)
                return

            if u not in self.graph:
                self.graph[u] = {}
            self.graph[u][v] = c

            dialog.destroy()
            self.draw_graph()
            self.info_label.config(text=f"✅ Added edge: {u} ──(cost={c})──> {v}")

        btn_box = tk.Frame(dialog, bg="#1e1e2e")
        btn_box.pack(pady=12)

        tk.Button(
            btn_box, text="Save Edge", command=save_edge,
            bg="#a6e3a1", fg="#11111b", font=("Arial", 9, "bold"), width=12, pady=4
        ).pack(side="left", padx=6)

        tk.Button(
            btn_box, text="Cancel", command=dialog.destroy,
            bg="#f38ba8", fg="#11111b", font=("Arial", 9, "bold"), width=10, pady=4
        ).pack(side="left", padx=6)

    # ── Dialogs: Delete Node ──────────────────────────────────────

    def open_delete_node_dialog(self):
        if not self.positions:
            messagebox.showinfo("Delete Node", "Graph is already empty.", parent=self.root)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Delete Node")
        dialog.geometry("340x200")
        dialog.configure(bg="#1e1e2e")
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog, text="🗑️ Delete Node", font=("Arial", 13, "bold"),
            bg="#1e1e2e", fg="#cdd6f4"
        ).pack(pady=10)

        form = tk.Frame(dialog, bg="#1e1e2e")
        form.pack(padx=20, pady=8, fill="x")

        tk.Label(form, text="Select Node:", font=("Arial", 9, "bold"), bg="#1e1e2e", fg="#cdd6f4").grid(row=0, column=0, sticky="w", pady=5)
        node_combo = ttk.Combobox(form, values=list(self.positions.keys()), state="readonly")
        node_combo.current(0)
        node_combo.grid(row=0, column=1, sticky="ew", pady=5)
        form.columnconfigure(1, weight=1)

        def do_delete():
            target = node_combo.get()
            if not target:
                return

            # Remove from positions & heuristics
            self.positions.pop(target, None)
            self.heuristic.pop(target, None)
            self.graph.pop(target, None)

            # Remove any incoming edges directed at target
            for u in self.graph:
                self.graph[u].pop(target, None)

            dialog.destroy()
            self._update_comboboxes()
            self.draw_graph()
            self.info_label.config(text=f"🗑️ Removed node '{target}' and its associated edges.")

        btn_box = tk.Frame(dialog, bg="#1e1e2e")
        btn_box.pack(pady=12)

        tk.Button(
            btn_box, text="Delete", command=do_delete,
            bg="#f38ba8", fg="#11111b", font=("Arial", 9, "bold"), width=10, pady=4
        ).pack(side="left", padx=6)

        tk.Button(
            btn_box, text="Cancel", command=dialog.destroy,
            bg="#6c7086", fg="#11111b", font=("Arial", 9, "bold"), width=10, pady=4
        ).pack(side="left", padx=6)

    # ── Rendering Pipeline ────────────────────────────────────────

    def draw_graph(self, explored=None, final_path=None, active=None):
        self.canvas.delete("all")

        explored = explored or []
        final_path = final_path or []

        # 1. Draw Directed Edges & Edge Cost Labels
        for u, neighbors in self.graph.items():
            if u not in self.positions:
                continue
            x1, y1 = self.positions[u]
            for v, weight in neighbors.items():
                if v not in self.positions:
                    continue
                x2, y2 = self.positions[v]

                # Determine if edge is part of the solution route
                is_path_edge = (
                    u in final_path and v in final_path and
                    abs(final_path.index(u) - final_path.index(v)) == 1
                )

                color = "#a6e3a1" if is_path_edge else "#585b70"
                width = 4 if is_path_edge else 2

                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, arrow=tk.LAST)

                mx = (x1 + x2) / 2
                my = (y1 + y2) / 2 - 10
                self.canvas.create_text(mx, my, text=f"cost={weight}", fill="#f9e2af", font=("Arial", 9, "bold"))

        # 2. Draw Nodes (Ovals & Text)
        for node, (x, y) in self.positions.items():
            is_start = (node == self.start_node)
            is_goal  = (node == self.goal_node)

            if node == active:
                fill_color = "#f9e2af"  # Yellow: expanding
            elif node in final_path:
                fill_color = "#a6e3a1"  # Green: final solution
            elif node in explored:
                fill_color = "#89b4fa"  # Blue: visited
            elif is_start:
                fill_color = "#fab387"  # Peach: start endpoint
            elif is_goal:
                fill_color = "#cba6f7"  # Mauve: goal endpoint
            else:
                fill_color = "#313244"  # Dark: unvisited

            text_color = "#11111b" if fill_color != "#313244" else "#cdd6f4"
            outline_color = "#f38ba8" if (is_start or is_goal) else "#cdd6f4"
            outline_w = 3 if (is_start or is_goal) else 2

            # Oval representation
            self.canvas.create_oval(
                x - 48, y - 28, x + 48, y + 28,
                fill=fill_color, outline=outline_color, width=outline_w
            )

            # Node label + badges
            badge = " [S]" if is_start else (" [G]" if is_goal else "")
            self.canvas.create_text(x, y - 7, text=f"{node}{badge}", fill=text_color, font=("Arial", 9, "bold"))

            # Heuristic value
            h_val = self.heuristic.get(node, "?")
            self.canvas.create_text(x, y + 11, text=f"h={h_val}", fill=text_color, font=("Arial", 8))

        self.root.update()

    # ── Path Reconstruction & Animation Sequencer ─────────────────

    def reconstruct(self, parent):
        if self.goal_node not in parent:
            return [], 0  # Goal unreachable

        path, cost, curr = [], 0, self.goal_node
        while curr is not None:
            path.append(curr)
            curr = parent.get(curr)

        path.reverse()
        for i in range(len(path) - 1):
            cost += self.graph.get(path[i], {}).get(path[i + 1], 0)

        return path, cost

    def run_animation(self, algo_name, traversal, path, cost):
        explored_so_far = []
        for node in traversal:
            explored_so_far.append(node)
            h_val = self.heuristic.get(node, "?")
            self.info_label.config(text=f"[{algo_name}] Visiting: {node} (h={h_val}) | Explored: {len(explored_so_far)}")
            self.draw_graph(explored=explored_so_far, active=node)
            time.sleep(0.45)

        if path:
            self.draw_graph(explored=explored_so_far, final_path=path)
            self.info_label.config(
                text=f"{algo_name} Completed! | Explored: {len(traversal)} nodes | Cost: {cost} | Path: {' -> '.join(path)}"
            )
        else:
            self.draw_graph(explored=explored_so_far)
            self.info_label.config(
                text=f"{algo_name} Finished | Explored: {len(traversal)} nodes | ❌ No reachable path from '{self.start_node}' to '{self.goal_node}'"
            )

    # ── Search Algorithms ─────────────────────────────────────────

    def animate_dfs(self):
        """Depth-First Search (Uninformed LIFO stack)"""
        if self.start_node not in self.positions or self.goal_node not in self.positions:
            messagebox.showwarning("Search", "Please ensure valid Start and Goal nodes exist.", parent=self.root)
            return

        stack, traversal, parent = [self.start_node], [], {self.start_node: None}

        while stack:
            node = stack.pop()
            if node not in traversal:
                traversal.append(node)
                if node == self.goal_node:
                    break

                for child in reversed(list(self.graph.get(node, {}).keys())):
                    if child not in traversal:
                        if child not in parent:
                            parent[child] = node
                        stack.append(child)

        path, cost = self.reconstruct(parent)
        self.run_animation("DFS", traversal, path, cost)

    def animate_bfs(self):
        """Breadth-First Search (Uninformed FIFO queue)"""
        if self.start_node not in self.positions or self.goal_node not in self.positions:
            messagebox.showwarning("Search", "Please ensure valid Start and Goal nodes exist.", parent=self.root)
            return

        queue, traversal, parent = [self.start_node], [], {self.start_node: None}

        while queue:
            node = queue.pop(0)
            if node not in traversal:
                traversal.append(node)
                if node == self.goal_node:
                    break

                for child in self.graph.get(node, {}):
                    if child not in traversal and child not in queue:
                        parent[child] = node
                        queue.append(child)

        path, cost = self.reconstruct(parent)
        self.run_animation("BFS", traversal, path, cost)

    def animate_greedy(self):
        """Greedy Best-First Search (Informed, priority on h(n))"""
        if self.start_node not in self.positions or self.goal_node not in self.positions:
            messagebox.showwarning("Search", "Please ensure valid Start and Goal nodes exist.", parent=self.root)
            return

        open_list, closed_list, parent = [self.start_node], [], {self.start_node: None}

        while open_list:
            best = min(open_list, key=lambda n: self.heuristic.get(n, 9999))
            open_list.remove(best)
            closed_list.append(best)

            if best == self.goal_node:
                break

            for nb in self.graph.get(best, {}):
                if nb not in closed_list and nb not in open_list:
                    parent[nb] = best
                    open_list.append(nb)

        path, cost = self.reconstruct(parent)
        self.run_animation("Greedy Best-First", closed_list, path, cost)

    def animate_astar(self):
        """A* Search (Informed, priority on f(n) = g(n) + h(n))"""
        if self.start_node not in self.positions or self.goal_node not in self.positions:
            messagebox.showwarning("Search", "Please ensure valid Start and Goal nodes exist.", parent=self.root)
            return

        open_list = [self.start_node]
        closed_list = []
        g = {self.start_node: 0}
        parent = {self.start_node: None}

        while open_list:
            curr = min(open_list, key=lambda n: g[n] + self.heuristic.get(n, 9999))
            open_list.remove(curr)
            closed_list.append(curr)

            if curr == self.goal_node:
                break

            for nb, weight in self.graph.get(curr, {}).items():
                new_g = g[curr] + weight
                if nb not in g or new_g < g[nb]:
                    g[nb] = new_g
                    parent[nb] = curr
                    if nb not in open_list:
                        open_list.append(nb)

        path, cost = self.reconstruct(parent)
        self.run_animation("A* Search", closed_list, path, cost)


# ─────────────────────────────────────────────────────────────────
#  MAIN RUNNER
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveSearchGUI(root)
    root.mainloop()

