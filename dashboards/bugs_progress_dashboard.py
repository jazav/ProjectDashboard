from dashboards.dashboard import AbstractDashboard
import csv
import os.path
import datetime
import plotly
import plotly.graph_objs as go


def color_for_status(status):
    return {
        'Open': 'rgb(217,98,89)',
        'In Fix': 'rgb(254,210,92)',
        'Closed': 'rgb(29,137,49)'
    }[status]


class BugsProgressDashboard(AbstractDashboard):
    status_list = []
    auto_open, repository = True, None
    bugs_statuses = {'Open': 0, 'In Fix': 0, 'Closed': 0}

    def prepare(self, data):
        self.status_list = data.get_bugs_progress()
        for status in self.status_list:
            self.bugs_statuses[status] += 1
        with open(os.path.abspath('//billing.ru/dfs/incoming/ABryntsev/bugs_progress.csv'), 'a', newline='\n') as csvfile:
            data = csv.writer(csvfile, delimiter=';')
            data.writerow([str(datetime.datetime.now().date())] + list(map(str, self.bugs_statuses.values())))

    def export_to_plotly(self):
        bugs_statuses_progress = {'Open': [], 'In Fix': [], 'Closed': []}
        dates = []
        with open(os.path.abspath('//billing.ru/dfs/incoming/ABryntsev/bugs_progress.csv'), 'r', newline='\n') as csvfile:
            data = csv.reader(csvfile, delimiter=';')
            next(data)
            for row in data:
                dates.append(row[0])
                bugs_statuses_progress['Open'].append(row[1])
                bugs_statuses_progress['In Fix'].append(row[2])
                bugs_statuses_progress['Closed'].append(row[3])
        print(dates, bugs_statuses_progress)
        data = []
        for status in bugs_statuses_progress.keys():
            data.append(go.Bar(
                x=dates,
                y=bugs_statuses_progress[status],
                text=bugs_statuses_progress[status],
                name=status,
                textposition='auto',
                marker=dict(
                    color=color_for_status(status),
                    line=dict(
                        color='black',
                        width=1
                    )
                )
            ))

        title = self.dashboard_name
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        layout = go.Layout(
            barmode='stack',
            title=title + (' <sup>in cloud</sup>' if self.repository == 'online' else '')
        )

        fig = go.Figure(data=dates, layout=layout)
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
