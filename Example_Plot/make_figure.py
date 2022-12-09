from spirit_extras.plotting import Paper_Plot
import numpy as np


def main():
    data = np.loadtxt(__DATA_FILE__[0])

    pplot = Paper_Plot(10 * Paper_Plot.cm)
    pplot.nrows = 1
    pplot.ncols = 2
    pplot.wspace = 0.1
    pplot.width_ratios = [2, 1]

    fig = pplot.fig()
    gs = pplot.gs()

    ax = fig.add_subplot(gs[0, 0])
    ax.plot(data[:, 0], data[:, 1])

    ax = fig.add_subplot(gs[0, 1])
    img_path = RENDERING_[0]
    pplot.image_to_ax(ax, img_path)

    print(META_KEY1_)

    ax.set_title(TITLE_)
    fig.savefig(OUTPUT_FILE_)
