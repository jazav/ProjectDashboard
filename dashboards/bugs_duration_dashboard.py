from datetime import datetime
import plotly
import plotly.graph_objs as go
# from plotly import tools
# from config_controller import cc_klass
from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain, get_domain_by_project
import numpy
import statistics


def string_divider(strval, width, space_replacer):
    if len(strval) > width:
        p = width
        while (p > 0) and (strval[p] != ' '):
            p = p - 1
        if p == 0:
            while (p < len(strval)) and (strval[p] != ' '):
                p = p + 1
        if p > 0:
            left = strval[0:p]
            right = strval[p + 1:]
            return left + space_replacer + string_divider(right, width, space_replacer)
    return strval


class BugsDurationDashboard(AbstractDashboard):
    project_list, name_list, created_list, resolutiondate_list, components_list = [], [], [], [], []
    auto_open, labels, priority, creators = True, None, None, None
    days_dict, average_list, median_list = {}, [], []

    def prepare(self, data):
        self.average_list.clear()
        self.median_list.clear()
        self.project_list, self.name_list, self.created_list, self.resolutiondate_list, self.components_list = \
            data.get_bugs_duration(self.labels, self.priority, self.creators)

        for i in range(len(self.name_list)):
            self.created_list[i] = datetime.strptime(self.created_list[i][:11].strip(), '%Y-%m-%d').date()
            self.resolutiondate_list[i] = datetime.strptime(self.resolutiondate_list[i][:11].strip(), '%Y-%m-%d').date()
            self.components_list[i] = self.components_list[i].split(',')
            if len(self.components_list[i]) != 1:
                for _ in range(1, len(self.components_list[i])):
                    self.components_list.append([self.components_list[i].pop()])
                    self.created_list.append(self.created_list[i])
                    self.resolutiondate_list.append(self.resolutiondate_list[i])
                    self.project_list.append(self.project_list[i])

        for i in range(len(self.components_list)):
            if self.components_list[i] != ['']:
                self.components_list[i] = get_domain(*self.components_list[i])
            else:
                self.components_list[i] = get_domain_by_project(self.project_list[i])
            if self.components_list[i] not in self.days_dict.keys():
                self.days_dict[self.components_list[i]] = []
            self.days_dict[self.components_list[i]].append(int(numpy.busday_count(self.created_list[i],
                                                                                  self.resolutiondate_list[i])) + 1)
        try:
            del self.days_dict["OTHERS"]
        except KeyError:
            print('Key not in domains')

        for domain in list(self.days_dict.keys()):
            self.average_list.append(round(statistics.mean(self.days_dict[domain]), 1))
            self.median_list.append(statistics.median(self.days_dict[domain]))

    def export_to_plotly(self):
        if len(self.name_list) == 0:
            raise ValueError('There is no issues to show')

        trace1 = go.Bar(
            x=list(self.days_dict.keys()),
            y=self.average_list,
            text=self.average_list,
            name='Duration average',
            textposition='auto',
            marker=dict(
                color='rgb(49,130,189)',
                line=dict(color='black',
                          width=1),
            ),
            insidetextfont=dict(family='Arial',
                                size=12,
                                color='white')
        )
        trace2 = go.Bar(
            x=list(self.days_dict.keys()),
            y=self.median_list,
            text=self.median_list,
            name='Duration median',
            textposition='auto',
            marker=dict(
                color='rgb(254,210,92)',
                line=dict(color='black',
                          width=1),
            ),
            insidetextfont=dict(family='Arial',
                                size=12,
                                color='black')
        )
        traces = [trace1, trace2]

        plan_fact_str = "pf"

        file_name = self.dashboard_name + ' ' + plan_fact_str
        html_file = self.png_dir + "{0}.html".format(file_name)
        title = self.dashboard_name + (' in ' + self.labels
                                       if self.labels != '' else '') + (' created by QC' if self.creators != '' else '')

        layout = go.Layout(
            annotations=[
                dict(
                    x=1.05,
                    y=1.03,
                    xref='paper',
                    yref='paper',
                    text='Operation',
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
            barmode='group',
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
                title='Days between creation date and resolution date',
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
                showticklabels=True,
                tickfont=dict(
                    size=16,
                    color='black'

                ),
                title='Domains',
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
