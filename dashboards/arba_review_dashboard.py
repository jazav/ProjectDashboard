from dashboards.dashboard import AbstractDashboard
import plotly
from plotly import tools
import plotly.figure_factory as ff
import plotly.graph_objs as go
from datetime import datetime, timedelta
from dashboards.arba_issues_dashboard import split_on, group_on
import math


class ArbaReviewDashboard(AbstractDashboard):
    key_list, assignee_list, issuetype_list, status_list, duedate_list = [], [], [], [], []
    auto_open, assignees = True, None

    def prepare(self, data):
        self.key_list, self.assignee_list, self.issuetype_list, self.status_list, self.duedate_list =\
            data.get_arba_review(self.assignees)
        self.assignee_list = split_on(self.assignee_list)
        self.key_list = group_on(self.key_list, self.assignee_list)
        self.issuetype_list = group_on(self.issuetype_list, self.assignee_list)
        self.status_list = group_on(self.status_list, self.assignee_list)
        self.duedate_list = group_on(self.duedate_list, self.assignee_list)

    def export_to_plotly(self):
        if len(self.key_list) == 0:
            raise ValueError('There is no issues to show')

        table_dict = {assignee[0]: None for assignee in self.assignee_list}
        for assignee in table_dict.keys():
            data_US = [['The quick brown fox', 'jumps over the lazy dog'] for _ in range(8)]
            table_dict[assignee] = ff.create_table(data_US)
        cols = math.ceil(len(table_dict.keys())/2)
        fig = tools.make_subplots(rows=2, cols=cols, subplot_titles=list(table_dict.keys()))
        for table, i in zip(table_dict.values(), range(len(table_dict.keys()))):
            row, col = int(i // cols + 1), int(i % cols + 1)
            fig.append_trace(table['data'][0], row, col)
            xaxis, yaxis = 'xaxis' + str(i+1), 'yaxis' + str(i+1)
            xref, yref = 'x' + str(i+1), 'y' + str(i+1)
            fig['layout'][xaxis].update(table['layout']['xaxis'])
            fig['layout'][yaxis].update(table['layout']['yaxis'])
            for j in range(len(table['layout']['annotations'])):
                table['layout']['annotations'][j].update(xref=xref, yref=yref)
            fig['layout']['annotations'] += table['layout']['annotations']

        title = self.dashboard_name
        html_file = self.png_dir + "{0}.html".format(title)

        plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)

    def export_to_plot(self):
        self.export_to_plotly()
