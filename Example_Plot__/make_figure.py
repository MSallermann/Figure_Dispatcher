from spirit_extras.plotting import Paper_Plot
import numpy as np


def main():
    print(__OUTPUT_FILE__)
    print(__RENDERINGS_TOP__)
    print(__RENDERING_SIDE__)
    print(__DATA_FILE__)

    data = np.loadtxt(__DATA_FILE__[0])

    pplot = Paper_Plot(10 * Paper_Plot.cm)
    pplot.nrows = 3
    pplot.ncols = 2
    pplot.wspace = 0.1
    pplot.width_ratios = [2, 1]

    fig = pplot.fig()
    gs = pplot.gs()

    ax = fig.add_subplot(gs[:, 0])

    ax.plot(data[:, 0], data[:, 1])

    for i, ax in enumerate(pplot.col(-1, slice(0, 2))):
        img_path = __RENDERINGS_TOP__[i]
        pplot.image_to_ax(ax, img_path)

    img_path = __RENDERING_SIDE__[0]
    ax = fig.add_subplot(gs[-1, -1])
    pplot.image_to_ax(ax, img_path)

    fig.savefig(__OUTPUT_FILE__, dpi=__DPI__)
    # pplot.image_to_ax(img_path)
