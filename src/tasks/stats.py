#!/usr/bin/env python3
import random
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from core.task import Task
from input_parser import add_task
from utils.cwe_dictionary import top_parent, get_name
from utils.parse import cwe_from_info

plt.style.use('seaborn')


class Stats(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self):
        mapping = {}
        labels = {}
        cwes_counts = []
        lines_per_challenge = []
        vuln_lines_per_challenge = []
        patch_lines_per_challenge = []
        povs_per_challenge = []
        total = 0
        unique = set()
        for challenge in self.challenges:
            challenge_paths = self.configs.lib_paths.get_challenge_paths(challenge)
            povs_per_challenge.append(len(challenge_paths.get_povs()))
            lines_per_challenge.append(self.global_metadata[challenge]['lines'])
            vuln_lines_per_challenge.append(self.global_metadata[challenge]['vuln_lines'])
            patch_lines_per_challenge.append(self.global_metadata[challenge]['patch_lines'])
            with challenge_paths.info.open(mode="r") as ci:
                description = ci.read()
                cwes = cwe_from_info(description)
                total += len(cwes)
                cwes_counts.append(len(cwes))
                unique.add(tuple(cwes))
                for cwe in cwes:
                    cwe_id = int(cwe.split('-')[1])
                    parent = top_parent(cwe_id, None, count=3)

                    name = get_name(parent)

                    if parent not in labels:
                        labels[parent] = f"CWE-{parent} {name if name else ''}"

                    if parent in mapping:
                        mapping[parent] += 1
                    else:
                        mapping[parent] = 1
        print(len(unique))
        # Plot
        #self.pie({labels[k]: v for k, v in mapping.items()})
        #self.histogram(cwes_counts, title="Histogram of number of CWEs per Challenges", x_label='CWE count',
        #                y_label='Challenges', cmap='plasma')
        #self.histogram(lines_per_challenge, binwidth=500, title="Histogram of the number of code lines per Challenge",
        #               x_label="Lines", y_label="Challenges", cmap='RdYlGn')
        #self.histogram(vuln_lines_per_challenge, x_label="Lines", y_label="Challenges", cmap='autumn',
        #               title="Histogram of the number of vulnerable lines per Challenge")
        #self.histogram(patch_lines_per_challenge, x_label="Lines", y_label="Challenges", cmap='winter',
        #               title="Histogram of the number of patch lines per Challenge")
        self.histogram(povs_per_challenge, x_label="POVs", y_label="Challenges", cmap='Set1',
                       title="Histogram of the number of POVs across Challenges")

    def pie(self, data: dict, cmap: str = 'viridis'):
        l = list(data.items())
        random.shuffle(l)
        data = dict(l)
        values = list(data.values())
        labels = list(data.keys())

        fig, ax = plt.subplots(figsize=(20, 10), subplot_kw=dict(aspect="equal"))
        ax.set_prop_cycle(color=self.color_map(len(values), cmap))
        explode = [0.05]*len(values)

        wedges, texts, autotexts = ax.pie(values, wedgeprops=dict(width=0.4), startangle=-30, explode=explode,
                               autopct="%.1f%%", pctdistance=0.85)

        plt.setp(autotexts, size=12, weight="bold")
        bbox_props = dict(boxstyle="square,pad=0.2", fc="w", ec="k", lw=0.8)
        kw = dict(arrowprops=dict(arrowstyle="-"),
                  bbox=bbox_props, zorder=0, va="center")

        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1) / 1.5 + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = "angle,angleA=0,angleB={}".format(ang)
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            ax.annotate(labels[i], xy=(x, y), xytext=(1.15 * np.sign(x), 1.15 * y), rotation_mode="anchor",
                        horizontalalignment=horizontalalignment, **kw, fontsize=12)

        ax.set_title("Benchmark's CWEs Composition")

        plt.show()

    # source: https://medium.com/@arseniytyurin/how-to-make-your-histogram-shine-69e432be39ca
    def histogram(self, data: List[int], title: str, x_label: str, y_label: str, cmap: str = 'tab20c',
                  binwidth: float = 1):
        fig, ax = plt.subplots(figsize=(20, 10))
        bins = np.arange(min(data), max(data) + binwidth, binwidth)
        n, bins, patches = ax.hist(data, bins=bins, facecolor='#2ab0ff', edgecolor='#e0e0e0', linewidth=1, alpha=0.8)

        # Good old loop. Choose colormap of your taste
        for i, color in enumerate(self.color_map(len(patches), cmap)):
            patches[i].set_facecolor(color)
            height = patches[i].get_height()
            if height > 0:
                ax.annotate(f'{int(height)}', xy=(patches[i].get_x() + patches[i].get_width() / 2, height),
                            xytext=(0, 5), textcoords='offset points', ha='center', va='bottom')

        # Add title and labels with custom font sizes
        plt.title(title, fontsize=12)
        plt.xticks(bins)
        plt.xlabel(x_label, fontsize=10)
        plt.ylabel(y_label, fontsize=10)
        plt.show()

    def color_map(self, num, cmp: str):
        cm = plt.get_cmap(cmp)
        return [cm(1. * i / num) for i in range(num)]

    def __str__(self):
        pass


def stats_args(input_parser):
    pass


stats_parser = add_task("stats", Stats, description="Statistics about benchmark challenges.")
stats_args(stats_parser)
