# main file za pozivanje funkcija i prikaz rezultata
# pip install networkx matplotlib

import matplotlib.pyplot as plt
from visualizer import MaxFlowVisualizer
from examples import examples


if __name__ == "__main__":
    app = MaxFlowVisualizer(_examples=examples)
    plt.show()