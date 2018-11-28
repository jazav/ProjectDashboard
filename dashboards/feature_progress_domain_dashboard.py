import datetime
import pandas as pd
import plotly
import plotly.graph_objs as go
from plotly import tools

import dashboards.prepare_feature_data as pfd
from config_controller import cc_klass
from dashboards.dashboard import AbstractDashboard

from enum import Enum, auto
class DashboardType(Enum):
     PROJECT = auto()
     FEATURE = auto()


PLAN_PREFIX = '<b>Plan</b>'
FACT_PREFIX = '<b>Closed</b>'
OPEN_PREFIX = '<b>Open</b>'
DEV_PREFIX = '<b>Dev</b>'


def stringDivider(strval, width, spaceReplacer):
    if (len(strval) > width):
        p = width
        while ((p > 0) and (strval[p] != ' ')):
            p = p - 1
        if (p == 0):
            while (p < len(strval) and (strval[p] != ' ')):
                p = p + 1
        if (p > 0):
            left = strval[0:p]
            right = strval[p + 1:]
            return left + spaceReplacer + stringDivider(right, width, spaceReplacer)
    return strval

class FeatureProgressDomainDashboard(AbstractDashboard):
    '''Plotly Bar Stacked Chart'''
    open_list = []
    dev_list = []
    close_list = []
    name_list = []
    auto_open = True
    fixversion = None
    project = None
    dashboard_type = DashboardType.PROJECT
    def prepare(self, data):
        if self.fixversion is None:
            raise ValueError('fixversion is undefined')
        self.open_list, self.dev_list, self.close_list, self.name_list, self.prj_list = \
            data.get_sum_by_projects(self.project, "", self.fixversion)

    def export_to_plotly(self):
        if len(self.name_list) == 0:
            return
        cc = cc_klass()
        brnamelist = []
        colors = []
        for vl in self.name_list:
            brnamelist.append(stringDivider(vl, int(cc.read_display_width()/10/len(self.name_list)), "<br>"))
            #colors.append()

        traces = []
        # was: brnamelist
        trace1 = go.Bar(
            x=self.prj_list if self.dashboard_type == DashboardType.PROJECT else brnamelist,
            y=self.close_list,
            text=self.close_list,
            name=FACT_PREFIX,
            textposition='auto',
            marker=dict(
                color='rgb(29,137,49)',#'palegreen',
                line=dict(
                    color='black',
                    width=1.5),
            ),
            insidetextfont=dict(family='Arial', size=12,
                      color='white')
        )
        # was: brnamelist
        trace2 = go.Bar(
            x=self.prj_list if self.dashboard_type == DashboardType.PROJECT else brnamelist,
            y=self.dev_list,
            text=self.dev_list,
            name=DEV_PREFIX,
            textposition='auto',
            marker=dict(
                color='rgb(254,210,92)',#'lightgoldenrodyellow',
                line=dict(
                    color='black',
                    width=1.5),
            ),
            insidetextfont=dict(family='Arial', size=12,
                      color='black')
        )
        # was: brnamelist
        trace3 = go.Bar(
            x=self.prj_list if self.dashboard_type == DashboardType.PROJECT else brnamelist,
            y=self.open_list,
            text=self.open_list,
            name=OPEN_PREFIX,
            textposition='auto',
            marker=dict(
                color='rgb(75,103,132)',#'powderblue',
                line=dict(
                    color='black',
                    width=1.5),
            ),
            insidetextfont=dict(family='Arial', size=12,
                      color='white')
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

        length_ss = cc.read_supersprint_length(self.fixversion)

        if length_ss != 0:
            will_be_done = 100*(now_dt - cc.read_supersprint_start(self.fixversion)).days / length_ss
        else:
            will_be_done = 0
        title = "{0} <br>{1} <br> Must be closed today ({4}) in {2}: {3:.2f}%".format(self.dashboard_name,  title_sum, self.fixversion, will_be_done, now_dt.strftime("%d.%m.%y %H:%M"))
        tools.make_subplots

        file_name = self.dashboard_name + ' ' + plan_fact_str
        html_file = self.png_dir + "{0}_{1}.html".format(file_name, self.project)
        layout = go.Layout(
            annotations=[
                dict(
                    x=1.05,
                    y=1.03,
                    xref='paper',
                    yref='paper',
                    text='Status',
                    showarrow=False,
                    font=dict(
                        family='sans-serif',
                        size=14,
                        color='black'
                    )
                )
            ],
            legend=dict(
                x=1,
                y=1,
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=14,
                    color='#000'
                )
            ),
            showlegend=True,
            margin=dict(t=50, b=50, r=100, l=6 * 6),
            autosize=True,
            font=dict(size=12, color='black'),
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
                title='Estimates (man-days)',
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
                tickangle=0,
                showticklabels=self.dashboard_type == DashboardType.PROJECT or (len(self.dev_list) < 30),
                tickfont=dict(
                    size=10,
                    color='black'

                ),
                title='Features (L3) ' if self.dashboard_type == DashboardType.FEATURE else "Projects",
                titlefont=dict(
                    size=12,
                    color='black'
                )
            )
        )

        fig = go.Figure(data=traces, layout=layout)
        plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)


    def export_to_plot(self):
        self.export_to_plotly()

    def export_to_json(self):
        raise NotImplementedError('export_to_json')
