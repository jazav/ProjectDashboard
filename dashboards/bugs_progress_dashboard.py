from dashboards.dashboard import AbstractDashboard
import csv
import os.path
import datetime
import plotly
import plotly.graph_objs as go
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time


def color_for_status(status):
    return {
        'Open': 'rgb(217,98,89)',
        'In Fix': 'rgb(254,210,92)',
        'Resolved': 'rgb(75,103,132)',
        'Closed': 'rgb(29,137,49)'
    }[status]


class BugsProgressDashboard(AbstractDashboard):
    status_list = []
    auto_open, repository, plotly_auth, citrix_token = True, None, None, None
    bugs_statuses = {'Open': 0, 'In Fix': 0, 'Resolved': 0, 'Closed': 0}

    def prepare(self, data):
        self.status_list = data.get_bugs_progress()
        for status in self.status_list:
            self.bugs_statuses[status] += 1
        with open(os.path.abspath('//billing.ru/dfs/incoming/ABryntsev/bugs_progress.csv'), 'a', newline='\n') as csvfile:
            data = csv.writer(csvfile, delimiter=';')
            data.writerow([str(datetime.datetime.now().date())] + list(map(str, self.bugs_statuses.values())))

    def export_to_plotly(self):
        if len(self.status_list) == 0:
            raise ValueError('There is no issues to show')

        bugs_statuses_progress = {'Open': [], 'In Fix': [], 'Resolved': [], 'Closed': []}
        dates = []
        with open(os.path.abspath('//billing.ru/dfs/incoming/ABryntsev/bugs_progress.csv'), 'r', newline='\n') as csvfile:
            data = csv.reader(csvfile, delimiter=';')
            next(data)
            for row in data:
                dates.append(row[0])
                bugs_statuses_progress['Open'].append(row[1])
                bugs_statuses_progress['In Fix'].append(row[2])
                bugs_statuses_progress['Resolved'].append(row[3])
                bugs_statuses_progress['Closed'].append(row[4])
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
                ),
                xaxis='x1',
                yaxis='y1',
                legendgroup='group1'
            ))
            data.append(go.Scatter(
                x=dates,
                y=bugs_statuses_progress[status],
                name=status,
                text=bugs_statuses_progress[status],
                textposition='top center',
                mode='lines+markers+text',
                line=dict(
                    color=color_for_status(status),
                    width=2
                ),
                marker=dict(
                    color=color_for_status(status),
                    size=6
                ),
                xaxis='x2',
                yaxis='y2',
                legendgroup='group2'
            ))

        title = self.dashboard_name
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        layout = go.Layout(
            hovermode='closest',
            xaxis1=dict(
                domain=[0, 1],
                type='date',
                dtick=86400000,
                title='Date',
                titlefont=dict(
                    size=12,
                    color='black'
                ),
                # title=dict(
                #     text='Date',
                #     font=dict(
                #         size=12,
                #         color='black'
                #     )
                # ),
                tickfont=dict(
                    size=16,
                    color='black'
                ),
                anchor='y1'
            ),
            yaxis1=dict(
                domain=[0.57, 1],
                anchor='x1',
                showline=True,
                title='Number of bugs',
                titlefont=dict(
                    size=12,
                    color='black'
                ),
                # title=dict(
                #     text='Number of bugs',
                #     font=dict(
                #         size=12,
                #         color='black'
                #     )
                # ),
                tickfont=dict(
                    size=16,
                    color='black'
                )
            ),
            xaxis2=dict(
                domain=[0, 1],
                type='date',
                dtick=86400000,
                title='Date',
                titlefont=dict(
                    size=12,
                    color='black'
                ),
                # title=dict(
                #     text='Date',
                #     font=dict(
                #         size=12,
                #         color='black'
                #     )
                # ),
                tickfont=dict(
                    size=16,
                    color='black'
                ),
                anchor='y2',
                # range=[dates[0], dates[-1]]
                autorange=True
            ),
            yaxis2=dict(
                domain=[0, 0.43],
                anchor='x2',
                showline=True,
                title='Number of bugs',
                titlefont=dict(
                    size=12,
                    color='black'
                ),
                # title=dict(
                #     text='Number of bugs',
                #     font=dict(
                #         size=12,
                #         color='black'
                #     )
                # ),
                tickfont=dict(
                    size=16,
                    color='black'
                )
            ),
            legend=dict(
                y=0.5,
                font=dict(
                    size=16
                )
            ),
            barmode='stack',
            title=title + (' <sup>in cloud</sup>' if self.repository == 'online' else '')
        )

        fig = go.Figure(data=data, layout=layout)
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.tools.set_credentials_file(username=self.plotly_auth[0], api_key=self.plotly_auth[1])
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)
        elif self.repository == 'citrix':
            plotly.offline.plot(fig, image_filename=title, image='png', image_height=1080, image_width=1920)
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
            time.sleep(5)
            shutil.move('C:/Users/Aleksey.Bryntsev/Downloads/{}.png'.format(title), './files/{}.png'.format(title))
            citrix = CitrixShareFile(hostname=self.citrix_token['hostname'], client_id=self.citrix_token['client_id'],
                                     client_secret=self.citrix_token['client_secret'],
                                     username=self.citrix_token['username'], password=self.citrix_token['password'])
            citrix.upload_file(folder_id='fofd8511-6564-44f3-94cb-338688544aac',
                               local_path='./files/{}.png'.format(title))
            citrix.upload_file(folder_id='fofd8511-6564-44f3-94cb-338688544aac',
                               local_path=html_file)

    def export_to_plot(self):
        self.export_to_plotly()
