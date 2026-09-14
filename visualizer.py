# file za vizualizaciju

import matplotlib.pyplot as plt
import networkx as nx
from ford_fulkerson import ford_fulkerson
from edmonds_karp import edmonds_karp
from editor import GraphEditor


class MaxFlowVisualizer(GraphEditor):
    def __init__(self, _examples=None):
        super().__init__(_examples)

        self.states = []
        self.current_state_idx = 0
        self.final_state = False
        self.alg_name = ""
        self.max_flow = 0
        self.capacity_matrix = []
        self.names_map = {}
        self.pos_map = {}

        if self._examples:
            self.load_example(0)
            self.draw_editor()
        else:
            self.draw_editor()

    def on_key(self, event):
        super().on_key(event)

        if self.mode == "visualizing":
            if event.key == "right":
                if not self.final_state:
                    if self.current_state_idx == len(self.states) - 1:
                        self.final_state = True
                    else:
                        self.current_state_idx += 1
                    self.draw_iteration()
            elif event.key == "left":
                if self.final_state:
                    self.final_state = False
                elif self.current_state_idx > 0:
                    self.current_state_idx -= 1
                self.draw_iteration()

    def run_algorithm(self, alg_type):
        if self.mode != "editing":
            return

        nodes = list(self.G.nodes)
        if len(nodes) < 2:
            self.info_text.set_text("Potrebna su barem dva čvora za pokretanje!")
            return

        source_input = self.txt_source.text.strip()
        sink_input = self.txt_sink.text.strip()

        s_node, t_node = None, None

        # pronalazak čvora (izvora) po imenu (label)
        for node in nodes:
            label = str(self.node_labels.get(node, str(node)))
            if label == source_input:
                s_node = node
                break

        # ako nije pronađen, čvor tražimo prema internom ID-u
        if s_node is None:
            for node in nodes:
                if str(node) == source_input:
                    s_node = node
                    break

        for node in nodes:
            label = str(self.node_labels.get(node, str(node)))
            if label == sink_input:
                t_node = node
                break

        if t_node is None:
            for node in nodes:
                if str(node) == sink_input:
                    t_node = node
                    break

        if s_node is None or t_node is None:
            self.info_text.set_text("Uneseni izvor ili ponor ne postoji u grafu!")
            return

        if s_node == t_node:
            self.info_text.set_text("Izvor i ponor moraju biti različiti!")
            return

        # povezuje ID čvora s indeksom u matrici
        node_map = {node: i for i, node in enumerate(nodes)}
        # povezuje indeks čvora u matrici s nazivom čvora u vizualnom prikazu
        self.names_map = {
            i: str(self.node_labels.get(node, str(node))) for node, i in node_map.items()
        }

        n = len(nodes)
        self.capacity_matrix = [[0] * n for _ in range(n)]
        for u, v, data in self.G.edges(data=True):
            self.capacity_matrix[node_map[u]][node_map[v]] = data["capacity"]

        self.pos_map = {node_map[node]: self.pos[node] for node in nodes}
        source = node_map[s_node]
        sink = node_map[t_node]

        if alg_type == "Ford-Fulkerson":
            self.max_flow, self.states = ford_fulkerson(
                self.capacity_matrix, source, sink
            )
        else:
            self.max_flow, self.states = edmonds_karp(
                self.capacity_matrix, source, sink
            )

        self.alg_name = alg_type
        self.current_state_idx = 0
        self.final_state = False
        self.mode = "visualizing"

        self.set_editor_widgets_visible(False)
        self.ax_btn_fp.set_visible(True)
        self.info_text.set_text("")

        self.draw_iteration()

    def draw_iteration(self):
        self.ax.clear()
        state = (
            self.states[-1] if self.final_state else self.states[self.current_state_idx]
        )
        iteration = state["iteration"]
        flows = state["flows"]
        path = state["path"]
        c_min = state["c_min"]

        if "Edmonds-Karp" in self.alg_name:
            node_color = "plum"
            path_color = "darkblue"
            title_color = "indigo"
            reverse_path_color = "dodgerblue"
        else:
            node_color = "lightpink"
            path_color = "red"
            title_color = "firebrick"
            reverse_path_color = "orange"

        display_G = nx.DiGraph()
        n = len(self.capacity_matrix)
        for i in range(n):
            display_G.add_node(i)

        for u in range(n):
            for v in range(n):
                if self.capacity_matrix[u][v] > 0:
                    display_G.add_edge(u, v)

        edge_labels = {
            (u, v): f"{flows[u][v]}/{self.capacity_matrix[u][v]}"
            for u, v in display_G.edges()
        }
        path_edges = (
            list(zip(path[:-1], path[1:])) if (path and not self.final_state) else []
        )

        if path and not self.final_state:
            for u, v in path_edges:
                if not display_G.has_edge(u, v):
                    if display_G.has_edge(v, u):
                        display_G.remove_edge(v, u)
                        if (v, u) in edge_labels:
                            del edge_labels[(v, u)]

                    display_G.add_edge(u, v)
                    edge_labels[(u, v)] = f"{flows[v][u]}"

        edge_colors, edge_widths, edge_styles = [], [], []

        for u, v in display_G.edges():
            if (u, v) in path_edges:
                if self.capacity_matrix[u][v] == 0:
                    edge_colors.append(reverse_path_color)
                    edge_styles.append("dashed")
                else:
                    edge_colors.append(path_color)
                    edge_styles.append("solid")
                edge_widths.append(3.5)
            else:
                edge_colors.append("black")
                edge_styles.append("solid")
                edge_widths.append(1.5)

        if self.final_state:
            self.ax.set_title(
                f"{self.alg_name} - Konačno stanje | Maksimalni tok = {self.max_flow}",
                fontsize=13,
                color="darkgreen",
            )
        else:
            if iteration == 0:
                main_title = f"{self.alg_name} - Inicijalno stanje | Tok = 0"
                current_title_color = "black"
            else:
                path_names = [self.names_map[node] for node in path]
                path_text = " - ".join(path_names)
                main_title = f"{self.alg_name} - Iteracija {iteration}: Put {path_text} (+{c_min})"
                current_title_color = title_color

            self.ax.set_title(
                main_title, fontsize=13, color=current_title_color, pad=25
            )

            self.ax.text(
                0.5, # x (50% širine platna)
                1.02, # y (102% visine platna)
                "<-- prethodni korak     sljedeći korak -->",
                transform=self.ax.transAxes, # gornje koordinate su relativni postotci osi
                ha="center", # horizontalno poravnanje
                va="bottom", # vertikalno poravnanje
                fontsize=10,
                color="black",
            )

        nx.draw_networkx_nodes(
            display_G,
            self.pos_map,
            ax=self.ax,
            node_size=700,
            node_color=node_color,
        )
        labels = {node: self.names_map[node] for node in display_G.nodes()}
        nx.draw_networkx_labels(
            display_G, self.pos_map, labels=labels, ax=self.ax, font_size=11
        )

        nx.draw_networkx_edges(
            display_G,
            self.pos_map,
            ax=self.ax,
            edge_color=edge_colors,
            width=edge_widths,
            style=edge_styles,
            arrows=True,
            arrowsize=18,
            node_size=700,
            connectionstyle="arc3,rad=0.08",
        )

        seen_positions = {}
        for (u, v), text in edge_labels.items():
            if not display_G.has_edge(u, v):
                continue
            mid_x = round((self.pos_map[u][0] + self.pos_map[v][0]) / 2, 2)
            mid_y = round((self.pos_map[u][1] + self.pos_map[v][1]) / 2, 2)
            pos_key = (mid_x, mid_y)

            current_label_pos = 0.35 if pos_key in seen_positions else 0.5
            seen_positions[pos_key] = True

            nx.draw_networkx_edge_labels(
                display_G,
                self.pos_map,
                edge_labels={(u, v): text},
                ax=self.ax,
                font_size=9,
                label_pos=current_label_pos,
                rotate=False,
            )

        self.ax.axis("off")
        self.fig.canvas.draw_idle()