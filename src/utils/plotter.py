from pathlib import Path

import textwrap
import numpy as np
import random
import matplotlib.pyplot as plt
from typing import List, AnyStr, Tuple

plt.style.use('seaborn')

medium_font = {'family': 'serif',
              'name': 'Helvetica',
              'size': 16}

large_font = {'family': 'serif',
              'name': 'Helvetica',
              'weight': 'bold',
              'size': 18}


def color_map(num: int, cmap: str):
    cm = plt.get_cmap(cmap)
    return [cm(1. * i / num) for i in range(num)]


class Plotter:
    def __init__(self, out_path: str, fig_width: int = 20, fig_height: int = 10):
        self.out_path = Path(out_path)
        self.fig_size = (fig_width, fig_height)

        if not self.out_path.exists():
            self.out_path.mkdir()

        plt.figure(figsize=self.fig_size)

    def save(self, file_name: str):
        plt.savefig(f"{self.out_path / Path(file_name)}", bbox_inches='tight')
        plt.clf()

    def pie(self, data: List[int], labels: List[AnyStr], cmap: str, filename: str = 'pie'):
        labels = ['\n'.join(textwrap.wrap(cn, width=25)) if len(cn) > 25 else cn for cn in labels]
        pairs = list(zip(data, labels))
        random.shuffle(pairs)
        data, labels = zip(*pairs)

        fig, ax = plt.subplots(figsize=(20, 10), subplot_kw=dict(aspect="equal"))
        colors = color_map(len(data), cmap)
        ax.set_prop_cycle(color=colors)
        explode = [0.05] * len(labels)

        wedges, texts, autotexts = ax.pie(data, wedgeprops=dict(width=0.4), startangle=-30, explode=explode,
                                          autopct="%.1f%%", pctdistance=0.85)

        plt.setp(autotexts, size=20, weight="bold")
        bbox_props = dict(boxstyle="square,pad=0.2", fc="w", ec="k", lw=0.8)
        kw = dict(arrowprops=dict(arrowstyle="-"),
                  bbox=bbox_props, zorder=0, va="center")

        for i, p in enumerate(wedges):
            if data[i] < 2:
                continue
            ang = (p.theta2 - p.theta1) / 1.5 + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = "angle,angleA=0,angleB={}".format(ang)
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            ax.annotate(labels[i], xy=(x, y), xytext=(1.15 * np.sign(x), 1.15 * y), rotation_mode="anchor",
                        horizontalalignment=horizontalalignment, **kw, fontsize=22)

        #ax.set_title("Benchmark's CWEs Composition", fontsize=20, weight="bold")
        self.save(filename)

    # source: https://medium.com/@arseniytyurin/how-to-make-your-histogram-shine-69e432be39ca
    def histogram(self, data: List[int], title: str, x_label: str, y_label: str, cmap: str, filename: str = 'hist',
                  binwidth: float = 1):
        fig, ax = plt.subplots(figsize=(20, 10))
        bins = np.arange(min(data), max(data) + binwidth, binwidth)
        n, bins, patches = ax.hist(data, bins=bins, facecolor='#2ab0ff', edgecolor='#e0e0e0', rwidth=1, linewidth=1, alpha=0.8, align='left')
        colors = color_map(len(patches), cmap)
        # Good old loop. Choose colormap of your taste
        for i, color in enumerate(colors):
            patches[i].set_facecolor(color)
            height = patches[i].get_height()
            if height > 0:
                ax.annotate(f'{int(height)}', xy=(patches[i].get_x() + patches[i].get_width() / 2, height),
                            xytext=(0, 5), textcoords='offset points', ha='center', va='bottom', **medium_font)

        # Add title and labels with custom font sizes
        plt.title(title, **large_font)
        if bins[-1] > 1000:
            plt.xticks(bins, **medium_font, rotation=-30, ha="right")
        else:
            plt.xticks(bins, **medium_font)
        plt.yticks(**medium_font)
        plt.xlabel(x_label, fontsize=10, **large_font)
        plt.ylabel(y_label, fontsize=10, **large_font)

        self.save(filename)
