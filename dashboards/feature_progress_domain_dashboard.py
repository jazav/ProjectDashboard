import datetime
import pandas as pd
import plotly
import plotly.graph_objs as go
from plotly import tools

import dashboards.prepare_feature_data as pfd
from config_controller import cc_klass
from dashboards.dashboard import AbstractDashboard

PLAN_PREFIX = '<b>Plan: </b>'
FACT_PREFIX = '<b>Closed: </b>'
OPEN_PREFIX = '<b>Open: </b>'
DEV_PREFIX = '<b>Dev: </b>'


class FeatureProgressDomainDashboard(AbstractDashboard):
    '''Plotly Bar Stacked Chart'''
    open_list= [];
    dev_list= [];
    close_list= [];
    name_list= [];

    def prepare(self, data, fixversion):
        self.fixversion = fixversion
        self.open_list, self.dev_list, self.close_list, self.name_list = data.get_sum_by_projects(self.project, "", fixversion)

    def export_to_plotly(self):

        if len(self.name_list) == 0:
            return
        traces = []
        trace1 = go.Bar(
            x=self.name_list,
            y=self.close_list,
            text=self.close_list,
            name=FACT_PREFIX,
            textposition='auto',
            marker=dict(
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
            )
        )
        trace2 = go.Bar(
            x=self.name_list,
            y=self.dev_list,
            text=self.dev_list,
            name=DEV_PREFIX,
            textposition = 'auto',
                           marker = dict(
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
            )
        )

        trace3 = go.Bar(
            x=self.name_list,
            y=self.open_list,
            text=self.open_list,
            name=OPEN_PREFIX,
            textposition = 'auto',
                           marker = dict(
                line=dict(
                    color='rgb(8,48,107)',
                    width=1.5),
            )
        )
        traces.append(trace1)
        traces.append(trace2)
        traces.append(trace3)
        all_open = 0
        for value in self.open_list:
            all_open += value
        all_dev = 0
        for value in self.dev_list:
            all_dev += value
        all_closed = 0
        for value in self.close_list:
            all_closed += value
        all_tasks= all_closed + all_dev + all_open
        if all_tasks == 0:
            all_tasks = 1
        plan_fact_str = "pf"
        title_sum = "Open: {0:.2f}%, Dev: {1:.2f}%, Closed: {2:.2f}%, All tasks: {3:.2f} md".format(100*all_open/all_tasks, 100*all_dev/all_tasks, 100*all_closed/all_tasks, all_tasks)
        now_dt = datetime.datetime.now()
        cc = cc_klass()
        length_ss = cc.read_supersprint_length(self.fixversion)
        if length_ss!=0:
            will_be_done = 100*(now_dt - cc.read_supersprint_start(self.fixversion)).days/ length_ss
        else:
            will_be_done = 0
        title = "{0} <br>{1} <br> Current position in {2}: {3:.2f}%".format(self.dashboard_name, title_sum, self.fixversion, will_be_done)
        tools.make_subplots

        file_name = self.dashboard_name.replace('num', '') + ' ' + plan_fact_str
        html_file = self.png_dir + "{0}_{1}.html".format(file_name, self.project)
        layout = go.Layout(
            annotations=[
                dict(
                    x=1.09,
                    y=1.03,
                    xref='paper',
                    yref='paper',
                    text='Components',
                    showarrow=False,
                    font=dict(
                        family='sans-serif',
                        size=12,
                        color='#000'
                    )
                )
            ],
            legend=dict(
                x=1,
                y=1,
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=10,
                    color='#000'
                )
            ),
            showlegend=True,
            margin=dict(t=50, b=50, r=100, l=6 * 6),
            autosize=True,
            font=dict(size=9, color='black'),
            barmode='stack',
            title=title,
            plot_bgcolor='white',
            yaxis=dict(
                rangemode="tozero",
                autorange=True,
                showgrid=True,
                zeroline=True,
                showline=True,
                ticks='',
                showticklabels=True,
                tickangle=0,
                tickfont=dict(
                    size=10,
                    color='black'

                ),
            ),
            xaxis=dict(
                rangemode="tozero",
                autorange=True,
                showgrid=True,
                zeroline=True,
                showline=True,
                ticks='',
                showticklabels=True,
                tickfont=dict(
                    size=10,
                    color='black'

                ),
                title='Estimates (man-days)',
                titlefont=dict(
                    size=16,
                    color='black'
                )
            )
        )

        fig = go.Figure(data=traces, layout=layout)
        plotly.offline.plot(fig, filename=html_file, auto_open=True)


    def export_to_plot(self):
        self.export_to_plotly()

    def export_to_json(self):
        raise NotImplementedError('export_to_json')
