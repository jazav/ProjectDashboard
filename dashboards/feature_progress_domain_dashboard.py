import pandas as pd
import plotly
import plotly.graph_objs as go
from plotly import tools

import dashboards.prepare_feature_data as pfd
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
    def prepare(self, data):
        self.open_list, self.dev_list, self.close_list, self.name_list = data.get_sum_by_projects(self.project, "", "SuperSprint7")

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
        plan_fact_str = 'plan '+ 'fact'

        title = "{0} <br>{1}".format(self.dashboard_name, plan_fact_str)
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
