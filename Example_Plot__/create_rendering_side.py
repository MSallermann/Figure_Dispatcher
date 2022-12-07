from spirit_extras import calculation_folder
from spirit_extras import data
from spirit_extras.pyvista_plotting import Spin_Plotter
import numpy as np
import os

__OUTPUT_FILES__ = None


def main():
    print("Creating files", __OUTPUT_FILES__)

    spin_system = data.Spin_System(
        np.array([[i, 0, 0] for i in range(10)]),
        np.array([[1, -1, 1] for i in range(10)]),
    )
    plotter = Spin_Plotter(spin_system)
    plotter.background_color = "black"
    plotter.arrows()
    plotter.set_camera_focus(distance=50, direction="y")

    if not os.path.exists(os.path.dirname(__OUTPUT_FILES__[0])):
        os.makedirs(os.path.dirname(__OUTPUT_FILES__[0]))

    # plotter.show()
    plotter.render_to_png(__OUTPUT_FILES__[0])
