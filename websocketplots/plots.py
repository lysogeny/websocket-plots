"""Helpers for plots"""

import io
import random
import matplotlib as mpl
import matplotlib.pyplot as plt

def random_plot():
    """Plots random numbers"""
    #size_actual = [s/dpi for s in size]
    indexes = list(range(0, 100))
    rand = [random.random() for i in indexes]
    fig = plt.figure()
    plt.plot(indexes, rand)
    return fig

def save_plot(fig, dpi, size):
    """Save the plot `fig` as SVG string with `dpi` and `size`"""
    data = io.StringIO()
    fig.set_size_inches(*size)
    fig.savefig(data, format='svg', dpi=dpi)
    data.seek(0)
    return data.read()

