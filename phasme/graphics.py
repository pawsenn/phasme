"""Module containing general routines for graphics generation using pandas/matplotlib.

Used by routines to produce loads of visualizations.

"""
import inspect
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os


def make_all(graph, outdir: str, params: dict = None):
    """
    Make all the graphs, yield the outfiles name and their description.
    params = {arg: value}
    """
    get_description = lambda f: f.__doc__.splitlines(False)[0]
    get_args = lambda f: inspect.getfullargspec(f)[0]

    # list containing the graphics functions
    func_list = [v for k, v in globals().items() if k.startswith("make_graphics")]

    for func in func_list:
        func_params = get_args(func)
        outfile = func(graph, outdir, **{p: v for p, v in params.items() if p in func_params})
        yield outfile, get_description(func)

    ...  # more functions to call


def make_graphics_degree(graph, outdir: str, bins: int = 50, no_one: bool = False,
                         log: bool = False, degree_color: str = 'green'):
    """degree distribution histogram"""
    degrees = list(graph.degree().values())

    title = "Degree distribution"
    data_list = degrees[:]
    # remove the values equal to 1
    if no_one:
        data_list = [x for x in data_list if x != 1]
        title += " - without degree = 1"
    # number of bars
    num_bins = bins
    x = data_list
    plt.hist(x, num_bins, edgecolor='black', facecolor=degree_color, alpha=0.8)

    # log scale
    if log:
        plt.yscale('log')
        title += " - log scale"
    plt.xlabel("Degree")
    plt.ylabel("Count")
    plt.title(title)
    plt.grid(True)

    # choose file name
    i = 1
    file_name = "{}/degree_distrib.png".format(outdir)
    while os.path.exists(file_name):
        file_name = "{}/degree_distrib_{}.png".format(outdir, i)
        i += 1

    plt.savefig(file_name)
    # clear the current figure
    plt.clf()
    file_name = os.path.basename(file_name)
    return file_name


def make_graphics_coef(graph, outdir: str, bins: int = 50, no_zero: bool = False,
                       log: bool = False, coef_color: str = 'blue'):
    """clustering coefficient distribution histogram"""
    coefs = list(nx.clustering(graph).values())

    title = "Coef distribution"
    data_list = coefs[:]
    # remove the values equal to 1
    if no_zero:
        data_list = [x for x in data_list if x != 0]
        title += " - without zero"
    # number of bars
    num_bins = bins
    x = data_list
    plt.hist(x, num_bins, edgecolor='black', facecolor=coef_color, alpha=0.8)

    # log scale
    if log:
        plt.yscale('log')
        title += " - log scale"
    plt.xlabel("Coef")
    plt.ylabel("Count")
    plt.title(title)
    plt.grid(True)

    # choose file name
    i = 1
    file_name = "{}/coef_distrib.png".format(outdir)
    while os.path.exists(file_name):
        file_name = "{}/coef_distrib_{}.png".format(outdir, i)
        i += 1

    plt.savefig(file_name)
    # clear the current figure
    plt.clf()
    file_name = os.path.basename(file_name)
    return file_name


def make_graphics_coef_stacked(graph, outdir: str, bins: int = 50, no_zero: bool = False,
                               log: bool = False, stacked_limits: list = None,
                               stacked_colors: list = None):
    """clustering coefficient distribution histogram with different degree categories
    Create a distribution histogram of the local clustering coefficients.
    By default, 4 colors for each bar:
        - green: degree <= 4
        - yellow/green: 4 < degree <= 10
        - yellow: 10 < degree <= 30
        - red: degree > 30
    """
    # default colors and the different thresholds
    if stacked_limits is None:
        stacked_limits = [4, 10, 30]
    if stacked_colors is None:
        stacked_colors = ['mediumseagreen', 'greenyellow', 'gold', 'orangered']
    # TODO define a default color list depending on the threshold list length, ex: default gradient
    assert len(stacked_colors) == len(stacked_limits) + 1, "Colors length must be equal to Limits" \
                                                           " length + 1"

    degrees = graph.degree()
    coefs = nx.clustering(graph)

    title = "Local clustering coefficient distribution with degree"

    x = []
    for i in range(len(stacked_limits) + 1):
        # retrieve the nodes for each degree category
        # first value
        if i == 0:
            node_degree = {k: v for (k, v) in degrees.items() if v <= stacked_limits[i]}
        # last value
        elif i == len(stacked_limits):
            node_degree = {k: v for (k, v) in degrees.items() if v > stacked_limits[i - 1]}
        else:
            node_degree = {k: v for (k, v) in degrees.items() if stacked_limits[i - 1] <= v <=
                           stacked_limits[i]}
        # retrieve the coef for the selected nodes
        node_coef = {k: v for (k, v) in coefs.items() if k in node_degree}
        # retrieve the list of values from node_coef
        values = list(node_coef.values())
        if no_zero:
            values[:] = [x for x in values if x != 0]
        # array w/ 1 column
        values = np.transpose(np.array([values]))
        x.append(values)
    if no_zero:
        title += " - without zero"

    # set the legend
    labels = []
    for i in range(len(stacked_limits)):
        labels.append("degree <= {}".format(stacked_limits[i]))
    # add last legend item
    labels.append("degree > {}".format(stacked_limits[-1]))

    num_bins = bins
    plt.hist(x, num_bins, edgecolor='black', histtype='bar', stacked=True, color=stacked_colors,
             label=labels, alpha=0.8)

    # change axis length
    ymax = plt.gca().get_ybound()
    ymax = ymax[1] * 1.1
    xmax = plt.gca().get_xbound()[1]
    plt.axis([0, xmax, 0, ymax])

    # log scale
    if log:
        plt.yscale('log')
        title += " - log scale"

    # axis labels and title
    plt.xlabel("Coef")
    plt.ylabel("Count")
    plt.title(title)
    plt.legend(prop={'size': 10})
    plt.grid(True)

    # choose file name
    i = 1
    file_name = "{}/coef_distrib_stacked.png".format(outdir)
    while os.path.exists(file_name):
        file_name = "{}/coef_distrib_stacked_{}.png".format(outdir, i)
        i += 1

    plt.savefig(file_name)
    # clear the current figure
    plt.clf()
    file_name = os.path.basename(file_name)
    return file_name
