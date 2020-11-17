#!/usr/bin/env python3
import yaml

from typing import List, AnyStr
from collections import Counter

from core.task import Task
from input_parser import add_task
from utils.plotter import Plotter, color_map


class Stats(Task):
    def __init__(self, plots: List[AnyStr] = None, **kwargs):
        super().__init__(**kwargs)
        self.plots = plots
        self.stats = {}

    def __call__(self):
        all_cwes = []

        for cn in self.challenges:
            challenge = self.get_challenge(cn)
            stats = challenge.stats()
            self.stats[cn] = stats
            all_cwes.extend(stats['cwes'])

        self.cwes_counts = Counter(all_cwes)

        data = {
            'Number of': {
                'Challenges': len(self.stats),
                'Unique CWEs': len(self.cwes_counts),
            },
            'CWEs Counts': dict(self.cwes_counts.items())
        }
        print(yaml.dump(data, default_flow_style=False))
        self.plot()

    def plot(self):
        if self.plots:
            plotter = Plotter(out_path=self.configs.plots)
            if 'cwes' in self.plots:
                print(self.cwes_counts.values())
                plotter.pie(data=list(self.cwes_counts.values()), labels=list(self.cwes_counts.keys()), cmap='viridis',
                            filename='cwes_pie')
                plotter.histogram([len(s['cwes']) for s in self.stats.values()], x_label='CWE count', cmap='plasma',
                                  y_label='Challenges', title="Histogram of number of CWEs per Challenges")
            if 'lines' in self.plots:
                plotter.histogram([s['lines'] for s in self.stats.values()], binwidth=500, filename='lines_hist',
                                  title="Histogram of the number of code lines per Challenge",
                                  x_label="Lines", y_label="Challenges", cmap='RdYlGn')
                plotter.histogram([s['vuln_lines'] for s in self.stats.values()], x_label="Lines", y_label="Challenges",
                                  cmap='autumn', filename='vuln_lines_hist',
                                  title="Histogram of the number of vulnerable lines per Challenge")
                plotter.histogram([s['patch_lines'] for s in self.stats.values()], x_label="Lines",
                                  y_label="Challenges", cmap='winter', filename='patch_lines_hist',
                                  title="Histogram of the number of patch lines per Challenge")
            if 'povs' in self.plots:
                plotter.histogram([s['povs'] for s in self.stats.values()], x_label="POVs", y_label="Challenges",
                                  cmap='Set1', filename='povs_hist',
                                  title="Histogram of the number of POVs across Challenges")

    def __str__(self):
        return super().__str__()


def stats_args(input_parser):
    input_parser.add_argument('--plots', choices=['cwes', 'lines', 'povs'], nargs="+", default=None,
                              help='Specific plots for the stats')


stats_parser = add_task("stats", Stats, description="Statistics about benchmark challenges.")
stats_args(stats_parser)
