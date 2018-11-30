from datetime import datetime
import plotly
import plotly.graph_objs as go
# from plotly import tools
from config_controller import cc_klass
from dashboards.dashboard import AbstractDashboard
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
    project_list, name_list, created_list, resolutiondate_list, domain_list = [], [], [], [], []
    auto_open, labels, priority = True, '', None
    days_dict, average_list, median_list = {}, [], []

    def prepare(self, data):
        self.average_list.clear()
        self.median_list.clear()
        self.project_list, self.name_list, self.created_list, self.resolutiondate_list, self.domain_list = \
            data.get_bugs_duration(self.labels, self.priority)
        for i in range(len(self.name_list)):
            self.created_list[i] = datetime.strptime(self.created_list[i][:11].strip(), '%Y-%m-%d').date()
            self.resolutiondate_list[i] = datetime.strptime(self.resolutiondate_list[i][:11].strip(), '%Y-%m-%d').date()
            if self.domain_list[i] not in self.days_dict.keys():
                self.days_dict[self.domain_list[i]] = []
            self.days_dict[self.domain_list[i]].append(int(numpy.busday_count(self.created_list[i],
                                                                              self.resolutiondate_list[i])) + 1)
        for domain in list(self.days_dict.keys()):
            self.average_list.append(round(statistics.mean(self.days_dict[domain]), 1))
            self.median_list.append(statistics.median(self.days_dict[domain]))

    def export_to_plotly(self):
        if len(self.name_list) == 0:
            raise ValueError('There is no issues to show')
        cc = cc_klass()

        trace1 = go.Bar(
            x=list(self.days_dict.keys()),
            y=self.average_list,
            text=self.average_list,
            name='Duration average',
            textposition='auto',
            marker=dict(
                color='rgb(29,137,49)',
                line=dict(color='black',
                          width=1.5),
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
                color='rgb(75,103,132)',
                line=dict(color='black',
                          width=1.5),
            ),
            insidetextfont=dict(family='Arial',
                                size=12,
                                color='white')
        )
        traces = [trace1, trace2]

        plan_fact_str = "pf"

        file_name = self.dashboard_name + ' ' + plan_fact_str
        html_file = self.png_dir + "{0}.html".format(file_name)

        layout = go.Layout(
            barmode='group'
        )

        fig = go.Figure(data=traces, layout=layout)
        plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)

    def export_to_plot(self):
        self.export_to_plotly()
