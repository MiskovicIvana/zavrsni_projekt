# file za uređivanje grafova
# NetworkX: https://networkx.org/documentation/stable/reference/algorithms/index.html
# Mathplotlib: https://matplotlib.org/stable/api/axes_api.html
# simboli: https://www.piliapp.com/symbol/triangle/

import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, TextBox
import networkx as nx


class GraphEditor:
    def __init__(self, _examples=None):
        self.G = nx.DiGraph()
        self.pos = {}
        self.selected_node = None
        self.node_counter = 1
        self.undo_stack = [] # povijest akcija za undo
        self.node_labels = {}

        self.mode = "editing"
        self._examples = _examples or []
        self.current_example_idx = None

        self.dropdown_open = False

        self.fig, self.ax = plt.subplots(figsize=(9.5, 6.5)) # glavni prozor
        plt.subplots_adjust(left=0.18, right=0.95, bottom=0.18, top=0.88) # prozor za crtanje grafova

        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)

        self._setup_editor_widgets()

    def _setup_editor_widgets(self): # metode za izradu interaktivnih elemenata
        self.ax_capacity = plt.axes([0.18, 0.08, 0.05, 0.04]) # left, bottom, width, height (0.0-1.0)
        self.txt_capacity = TextBox(self.ax_capacity, "Kapacitet: ", initial="10")

        self.ax_source = plt.axes([0.33, 0.08, 0.05, 0.04])
        self.txt_source = TextBox(self.ax_source, "Izvor: ", initial="s")

        self.ax_sink = plt.axes([0.47, 0.08, 0.05, 0.04])
        self.txt_sink = TextBox(self.ax_sink, "Ponor: ", initial="t")

        self.ax_btn_ff = plt.axes([0.57, 0.08, 0.14, 0.04])
        self.btn_ff = Button(self.ax_btn_ff, "Ford-Fulkerson")
        self.btn_ff.on_clicked(lambda e: self.run_algorithm("Ford-Fulkerson"))

        self.ax_btn_ek = plt.axes([0.76, 0.08, 0.14, 0.04])
        self.btn_ek = Button(self.ax_btn_ek, "Edmonds-Karp")
        self.btn_ek.on_clicked(lambda e: self.run_algorithm("Edmonds-Karp"))

        self.ax_btn_fp = plt.axes([0.02, 0.08, 0.14, 0.04])
        self.btn_fp = Button(self.ax_btn_fp, "Početna stranica")
        self.btn_fp.on_clicked(lambda e: self.back_to_editor())
        self.ax_btn_fp.set_visible(False)

        self.ax_dropdown_btn = plt.axes([0.02, 0.84, 0.15, 0.045])
        self.btn_dropdown = Button(self.ax_dropdown_btn, "Primjeri grafova ▽")
        self.btn_dropdown.on_clicked(self.toggle_dropdown)

        example_names = [
            ex.get("name", f"Primjer {i+1}")
            for i, ex in enumerate(self._examples)
        ]
        
        # dinamički izračun visine okvira otvorenog padajućeg izbornika
        # ograničeno na maksimalno 35% visine ekrana
        menu_height = min(0.045 * len(example_names), 0.35) if example_names else 0.045
        self.ax_dropdown_menu = plt.axes([0.02, 0.84 - menu_height, 0.14, menu_height])

        if example_names:
            self.radio_menu = RadioButtons(
                self.ax_dropdown_menu, example_names, active=0, activecolor="lightsalmon"
            )
            self.radio_menu.on_clicked(self._on_example_selected)

        self._set_dropdown_visible(False)

        self.info_text = self.fig.text(
            0.55, 0.02, "", ha="center", fontsize=9, color="darkred"
        )

    def _set_dropdown_visible(self, visible):
        self.ax_dropdown_menu.set_visible(visible)
        self.dropdown_open = visible
        for child in self.ax_dropdown_menu.get_children():
            child.set_visible(visible)
        if visible:
            self.ax_dropdown_menu.set_frame_on(True)

    def toggle_dropdown(self, event):
        if self.mode != "editing":
            return
        new_state = not self.dropdown_open
        self._set_dropdown_visible(new_state)
        self.btn_dropdown.label.set_text(
            "Primjeri grafova △" if self.dropdown_open else "Primjeri grafova ▽"
        )
        self.fig.canvas.draw_idle()

    def _on_example_selected(self, label):
        if self.mode != "editing":
            return
        for idx, ex in enumerate(self._examples):
            if ex.get("name", f"Primjer {idx+1}") == label:
                self.load_example(idx)
                break
        self.draw_editor()

    def set_editor_widgets_visible(self, visible):
        self.ax_capacity.set_visible(visible)
        self.ax_source.set_visible(visible)
        self.ax_sink.set_visible(visible)
        self.ax_btn_ff.set_visible(visible)
        self.ax_btn_ek.set_visible(visible)
        self.ax_dropdown_btn.set_visible(visible)
        self._set_dropdown_visible(False)

    def load_example(self, idx):
        self.current_example_idx = idx
        ex = self._examples[idx]
        capacity = ex["capacity"]
        names = ex.get("names", {})
        source = ex.get("source", 0)
        sink = ex.get("sink", len(capacity) - 1)

        self.G.clear()
        self.pos.clear()
        self.node_labels.clear()
        self.undo_stack.clear()
        self.selected_node = None

        n = len(capacity)
        for i in range(n):
            self.G.add_node(i)
            self.node_labels[i] = names.get(i, str(i))
            self.node_counter = (max(self.G.nodes) + 2) if (n > 0 and 0 in self.G.nodes) else (max(self.G.nodes) + 1 if n > 0 else 1)
        for i in range(n):
            self.G.add_node(i)
            self.node_labels[i] = names.get(i, str(i))

        for u in range(n):
            for v in range(n):
                if capacity[u][v] > 0:
                    self.G.add_edge(u, v, capacity=capacity[u][v])

        if "pos" in ex:
            self.pos = ex["pos"].copy()
        else:
            temp_pos = nx.spring_layout(self.G, seed=42)
            self.pos = {node: (coords[0], coords[1]) for node, coords in temp_pos.items()}

        src_label = str(names.get(source, source))
        snk_label = str(names.get(sink, sink))
        self.txt_source.set_val(src_label)
        self.txt_sink.set_val(snk_label)
        self.info_text.set_text(f"Učitan {ex.get('name', f'Primjer {idx+1}')}.")

    def draw_editor(self):
        self.mode = "editing"
        was_open = getattr(self, "dropdown_open", False)

        self.set_editor_widgets_visible(True)
        self._set_dropdown_visible(was_open)
        self.btn_dropdown.label.set_text(
            "Primjeri grafova △" if was_open else "Primjeri grafova ▽"
        )

        self.ax_btn_fp.set_visible(False)
        self.ax.clear()

        self.ax.set_title(
            "Lijevi klik - dodaj čvor ili brid | Desni klik - obriši čvor ili brid | Z - Undo | X - Delete all",
            fontsize=11,
        )

        if len(self.G.nodes) > 0:
            node_colors = [
                "peachpuff" if node == self.selected_node else "darksalmon"
                for node in self.G.nodes()
            ]
            nx.draw_networkx_nodes(
                self.G, self.pos, ax=self.ax, node_size=700, node_color=node_colors
            )
            labels = {node: self.node_labels.get(node, str(node)) for node in self.G.nodes()}
            nx.draw_networkx_labels(self.G, self.pos, labels=labels, ax=self.ax, font_size=11)

        if len(self.G.edges) > 0:
            nx.draw_networkx_edges(
                self.G,
                self.pos,
                ax=self.ax,
                arrows=True,
                arrowsize=18,
                node_size=700,
                connectionstyle="arc3,rad=0.08", # usmjereni bridovi s blagom zakrivljenošću
            )
            edge_labels = {
                (u, v): str(data["capacity"]) for u, v, data in self.G.edges(data=True)
            }
            seen_positions = {}

            for (u, v), text in edge_labels.items():
                mid_x = round((self.pos[u][0] + self.pos[v][0]) / 2, 2)
                mid_y = round((self.pos[u][1] + self.pos[v][1]) / 2, 2)
                pos_key = (mid_x, mid_y)

                current_label_pos = 0.35 if pos_key in seen_positions else 0.5
                seen_positions[pos_key] = True

                nx.draw_networkx_edge_labels(
                    self.G,
                    self.pos,
                    edge_labels={(u, v): text},
                    ax=self.ax,
                    font_size=9,
                    label_pos=current_label_pos,
                    rotate=False,
                )

        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)
        self.ax.axis("off")
        self.fig.canvas.draw_idle() # osvježavanje prikaza

    def _get_node_at_pos(self, x, y):
        for node, (nx_x, nx_y) in self.pos.items():
            if (x - nx_x) ** 2 + (y - nx_y) ** 2 < 0.02:
                return node
        return None

    def _get_edge_at_pos(self, x, y):
        threshold = 0.06 # maksimalna dozvoljena udaljenost miša od linije da bi se smatralo da je kliknuto na taj brid
        for u, v in self.G.edges():
            x1, y1 = self.pos[u]
            x2, y2 = self.pos[v]

            dx, dy = x2 - x1, y2 - y1 # vektor smjera brida od čvora u do čvora v
            if dx == 0 and dy == 0:
                continue

            # projkecija točke klika na pravac brida, te(0.0, 1.0)
            t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
            proj_x, proj_y = x1 + t * dx, y1 + t * dy

            if ((x - proj_x) ** 2 + (y - proj_y) ** 2) ** 0.5 < threshold:
                return (u, v)
        return None

    def on_click(self, event):
        if self.mode != "editing" or event.inaxes != self.ax:
            return

        x, y = event.xdata, event.ydata
        clicked_node = self._get_node_at_pos(x, y)

        if event.button == 1:
            if clicked_node is None:
                if len(self.G.nodes) > 0:
                    max_node = max(self.G.nodes)
                    if 0 in self.G.nodes and max_node < len(self.G.nodes):
                        node_id = max_node + 2
                    else:
                        node_id = max_node + 1
                else:
                    node_id = 1
                self.node_counter = node_id + 1
                self.G.add_node(node_id)
                node_name = str(node_id)
                self.node_labels[node_id] = node_name
                self.pos[node_id] = (x, y)
                self.undo_stack.append(("add_node", node_id, (x, y), node_name))
                self.selected_node = None
                self.info_text.set_text(f"Dodan čvor '{node_name}'.")
            else:
                if self.selected_node is None:
                    self.selected_node = clicked_node
                    name = self.node_labels.get(clicked_node, str(clicked_node))
                    self.info_text.set_text(
                        f"Odabran čvor '{name}'. Kliknite na drugi čvor za dodavanje brida."
                    )
                elif self.selected_node == clicked_node:
                    self.selected_node = None
                    self.info_text.set_text("")
                else:
                    u, v = self.selected_node, clicked_node
                    self.add_edge_with_capacity(u, v, self.txt_capacity.text)
                    self.selected_node = None

        elif event.button == 3:
            if clicked_node is not None:
                edges = list(self.G.edges(clicked_node, data=True)) + [
                    (u, v, d) for u, v, d in self.G.edges(data=True) if v == clicked_node
                ]
                pos = self.pos[clicked_node]
                lbl = self.node_labels.get(clicked_node, str(clicked_node))

                self.G.remove_node(clicked_node)
                self.pos.pop(clicked_node, None)
                self.node_labels.pop(clicked_node, None)

                if self.selected_node == clicked_node:
                    self.selected_node = None

                self.undo_stack.append(("remove_node", clicked_node, pos, lbl, edges))
                self.info_text.set_text(f"Obrisan čvor '{lbl}'.")
            else:
                clicked_edge = self._get_edge_at_pos(x, y)
                if clicked_edge is not None:
                    u, v = clicked_edge
                    cap = self.G[u][v]["capacity"]
                    self.G.remove_edge(u, v)
                    self.undo_stack.append(("remove_edge", u, v, cap))

                    u_name = self.node_labels.get(u, str(u))
                    v_name = self.node_labels.get(v, str(v))
                    self.info_text.set_text(f"Obrisan brid {u_name} -> {v_name}.")

        self.draw_editor()

    def add_edge_with_capacity(self, u, v, text):
        try:
            cap = int(text)
            if cap > 0:
                old_cap = self.G[u][v]["capacity"] if self.G.has_edge(u, v) else None
                self.G.add_edge(u, v, capacity=cap)
                self.undo_stack.append(("add_edge", u, v, cap, old_cap))
                u_name = self.node_labels.get(u, str(u))
                v_name = self.node_labels.get(v, str(v))
                self.info_text.set_text(
                    f"Dodan brid '{u_name} -> {v_name}' s kapacitetom {cap}."
                )
            else:
                self.info_text.set_text("Kapacitet mora biti veći od 0!")
        except ValueError:
            self.info_text.set_text("Neispravan unos kapaciteta!")

    def on_key(self, event):
        if self.mode == "editing":
            if event.key == "z":
                if self.undo_stack:
                    action = self.undo_stack.pop()
                    act_type = action[0]

                    if act_type == "add_node":
                        node_id = action[1]
                        if node_id in self.G:
                            self.G.remove_node(node_id)
                            self.pos.pop(node_id, None)
                            self.node_labels.pop(node_id, None)

                    elif act_type == "add_edge":
                        u, v, cap, old_cap = action[1], action[2], action[3], action[4]
                        if old_cap is None:
                            if self.G.has_edge(u, v):
                                self.G.remove_edge(u, v)
                        else:
                            self.G.add_edge(u, v, capacity=old_cap)

                    elif act_type == "remove_node":
                        node_id, pos, lbl, edges = action[1], action[2], action[3], action[4]
                        self.G.add_node(node_id)
                        self.pos[node_id] = pos
                        self.node_labels[node_id] = lbl
                        for u, v, data in edges:
                            if u in self.G and v in self.G:
                                self.G.add_edge(u, v, **data)

                    elif act_type == "remove_edge":
                        u, v, cap = action[1], action[2], action[3]
                        if u in self.G and v in self.G:
                            self.G.add_edge(u, v, capacity=cap)

                    self.selected_node = None
                    self.draw_editor()

            elif event.key == "x":
                self.G.clear()
                self.pos.clear()
                self.node_labels.clear()
                self.selected_node = None
                self.node_counter = 1
                self.undo_stack.clear()
                self.info_text.set_text("Graf je obrisan. Kliknite za dodavanje novog čvora.")
                self.draw_editor()

    def run_algorithm(self, alg_type):
        pass

    def back_to_editor(self):
        self.draw_editor()
