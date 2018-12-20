from datetime import datetime
import plotly
import plotly.graph_objs as go
# from plotly import tools
# from config_controller import cc_klass
from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain, get_domain_by_project
import numpy
import statistics


class BugsDurationDashboard(AbstractDashboard):
    project_list, name_list, created_list, resolutiondate_list, components_list = [], [], [], [], []
    auto_open, labels, priority, creators = True, None, None, None
    days_dict, average_list, median_list, max_list, count_list = {}, [], [], [], []

    def prepare(self, data):
        self.average_list.clear()
        self.median_list.clear()
        self.max_list.clear()
        self.count_list.clear()
        self.days_dict.clear()
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

        daysdict = {}
        for domain, days in self.days_dict.items():
            if domain in ('Billing', 'CRM', 'DFE', 'Infra', 'NWM', 'Ordering', 'PRM', 'PSC'):
                daysdict[domain] = days
        self.days_dict = daysdict

        for domain in list(self.days_dict.keys()):
            self.average_list.append(round(statistics.mean(self.days_dict[domain]), 1))
            self.median_list.append(round(statistics.median(self.days_dict[domain]), 1))
            self.max_list.append(max(self.days_dict[domain]))
            self.count_list.append(len(self.days_dict[domain]))

    def export_to_plotly(self):
        if len(self.name_list) == 0:
            raise ValueError('There is no issues to show')

        trace_avg = go.Bar(
            x=list(self.days_dict.keys()),
            y=self.average_list,
            text=self.average_list,
            name='average',
            textposition='auto',
            marker=dict(
                color='rgb(126,135,215)',
                line=dict(color='black',
                          width=1),
            ),
            insidetextfont=dict(family='sans-serif',
                                size=18,
                                color='white')
        )
        trace_median = go.Bar(
            x=list(self.days_dict.keys()),
            y=self.median_list,
            text=self.median_list,
            name='median',
            textposition='auto',
            marker=dict(
                color='rgb(254,210,92)',
                line=dict(color='black',
                          width=1),
            ),
            insidetextfont=dict(family='sans-serif',
                                size=18,
                                color='black')
        )

        trace_max = go.Bar(
            x=list(self.days_dict.keys()),
            y=self.max_list,
            text=self.max_list,
            name='max',
            textposition='auto',
            marker=dict(
                color='pink',
                line=dict(color='black',
                          width=1),
            ),
            insidetextfont=dict(family='sans-serif',
                                size=18,
                                color='black')
        )
        traces = [trace_median, trace_avg]

        plan_fact_str = "pf"

        title = self.dashboard_name + (' in ' + self.labels
                                       if self.labels != '' else '') + (' created by QC' if self.creators != '' else '')
        file_name = title + ' ' + plan_fact_str
        # html_file = self.png_dir + "{0}.html".format(file_name)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        annotations = [dict(
            x=1.05,
            y=1.03,
            xref='paper',
            yref='paper',
            text='Duration',
            showarrow=False,
            font=dict(
                family='sans-serif',
                size=16,
                color='black'
            )
        )]
        for i in range(len(self.days_dict.keys())):
            annotations.append(dict(
                x=list(self.days_dict.keys())[i],
                y=self.average_list[i] + max(self.average_list)/20,
                xref='x',
                yref='y',
                text='Bugs number: <b>' + str(self.count_list[i]) + '</b><br>Max duration: <b>' + str(self.max_list[i]) + '</b>',
                showarrow=False,
                font=dict(
                    family='sans-serif',
                    size=16,
                    color='black'
                ),
                bordercolor='black',
                borderwidth=1,
                borderpad=5,
                bgcolor='white',
                opacity=1
            ))
        layout = go.Layout(
            annotations=annotations,
            legend=dict(
                x=1,
                y=1,
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=16,
                    color='#000'
                )
            ),
            showlegend=True,
            margin=dict(t=50, b=50, r=100, l=36),
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
                title='Days between creation and resolution',
                titlefont=dict(
                    family='sans-serif',
                    size=12,
                    color='black'
                ),
                tickfont=dict(
                    family='sans-serif',
                    size=16,
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
                    family='sans-serif',
                    size=16,
                    color='black'

                ),
                title='Domains',
                titlefont=dict(
                    family='sans-serif',
                    size=12,
                    color='black'
                )
            )
        )

        fig = go.Figure(data=traces, layout=layout)
        plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)

    def export_to_plot(self):
        self.export_to_plotly()
