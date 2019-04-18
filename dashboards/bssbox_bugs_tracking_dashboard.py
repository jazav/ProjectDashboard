from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain_bssbox
import datetime
import textwrap
import plotly
import plotly.graph_objs as go
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time


def alert_action(keys, days, priorities, olds):
    color = [[]]
    for key, day, priority in zip(keys, days, priorities):
        if priority == 'Blocker' and key not in olds:
            if day > 0:
                color[0].append('rgb(255,204,204)')
            elif day > 2:
                color[0].append('rgb(255,102,102)')
            else:
                color[0].append('rgb(255,255,255)')
        elif priority == 'Critical' and key not in olds:
            if day > 1:
                color[0].append('rgb(255,204,204)')
            elif day > 3:
                color[0].append('rgb(255,102,102)')
            else:
                color[0].append('rgb(255,255,255)')
        else:
            color[0].append('rgb(255,255,255)')
    return color


def workdays(fromdate, todate):
    return sum(1 for day in (fromdate + datetime.timedelta(x + 1)
                             for x in range((todate - fromdate).days)) if day.weekday() < 5)


def deadline(fromdate, days):
    dl = fromdate
    while days > 0:
        dl += datetime.timedelta(days=1)
        if dl.weekday() >= 5:
            continue
        days -= 1
    return dl.strftime('%d.%m.%y %H:%M')


class BssboxBugsTrackingDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth, citrix_token, local_user = True, None, None, None, None
    tracking_data, pivot_data, all_bugs, overdue_data, created_dict, old_list = {}, {}, {}, {}, [], []
    jql_all = 'https://jira.billing.ru/issues/?jql=key in ('

    def prepare(self, data):
        self.tracking_data = {key: [] for key in list(data.keys()) if key != 'Resolved'}
        self.all_bugs['BSSBox'] = {'On track': 0, 'Overdue': 0}
        preparing_data = {key: [] for key in data.keys()}
        for i in range(len(data['Key'])):
            if get_domain_bssbox(data['Domain'][i]) != 'Common':  # exclude specific components
                for key in data.keys():
                    preparing_data[key].append(data[key][i])
        data = preparing_data
        created = [cr for cr, st in zip(data['Days in progress'], data['Status']) if st not in ('Closed', 'Resolved')]
        self.created_dict = created
        for i in range(len(data['Key'])):
            data['Domain'][i] = get_domain_bssbox(data['Domain'][i])
            if data['Days in progress'][i] < datetime.datetime(2019, 1, 28):
                self.old_list.append(data['Key'][i])
            data['Days in progress'][i] =\
                workdays(data['Days in progress'][i], datetime.datetime.now())\
                if data['Status'][i] not in ('Closed', 'Resolved')\
                else workdays(data['Days in progress'][i], data['Resolved'][i])
            if data['Key'][i] == data['Key'][i-1] and data['Domain'][i] == data['Domain'][i-1]:
                continue
            if data['Status'][i] not in ('Closed', 'Resolved'):
                for key in self.tracking_data.keys():
                    self.tracking_data[key].append(data[key][i])
            if data['Domain'][i] not in self.pivot_data.keys():
                self.pivot_data[data['Domain'][i]] = {'On track': 0, 'Overdue': 0}
                self.overdue_data[data['Domain'][i]] = 'https://jira.billing.ru/issues/?jql=key in ('
            if data['Priority'][i] == 'Blocker':
                if data['Days in progress'][i] > 0 and data['Key'][i] not in self.old_list:
                    self.pivot_data[data['Domain'][i]]['Overdue'] += 1
                    self.all_bugs['BSSBox']['Overdue'] += 1
                    self.overdue_data[data['Domain'][i]] += '{}, '.format(data['Key'][i])
                    self.jql_all += '{}, '.format(data['Key'][i])
                else:
                    self.pivot_data[data['Domain'][i]]['On track'] += 1
                    self.all_bugs['BSSBox']['On track'] += 1
            elif data['Priority'][i] == 'Critical':
                if data['Days in progress'][i] > 1 and data['Key'][i] not in self.old_list:
                    self.pivot_data[data['Domain'][i]]['Overdue'] += 1
                    self.all_bugs['BSSBox']['Overdue'] += 1
                    self.overdue_data[data['Domain'][i]] += '{}, '.format(data['Key'][i])
                    self.jql_all += '{}, '.format(data['Key'][i])
                else:
                    self.pivot_data[data['Domain'][i]]['On track'] += 1
                    self.all_bugs['BSSBox']['On track'] += 1
        self.overdue_data = {domain: '{})'.format(jql[:-2]) for domain, jql in self.overdue_data.items()}
        self.jql_all = '{})'.format(self.jql_all[:-2])

    def export_to_plotly(self):
        if len(self.tracking_data['Key']) == 0:
            raise ValueError('There is no issues to show')

        header_values = [['<b>{}</b>'.format(head)] for head in self.tracking_data.keys()] + [['<b>Deadline</b>']]
        cells_values = [value if key != 'Key' else
                        list(map(lambda el:'<a href="https://jira.billing.ru/browse/{0}">{0}</a>'.format(el), value))
                        for key, value in self.tracking_data.items()] + [[deadline(cr, 2) if pr == 'Critical' else
                        deadline(cr, 1) for cr, pr in zip(self.created_dict, self.tracking_data['Priority'])]]
        data = [go.Table(
            domain=dict(
                x=[0, 0.72],
                y=[0, 1]
            ),
            columnorder=[1, 2, 3, 4, 5, 6, 7, 8, 9],
            columnwidth=[3, 10, 3, 2, 2, 2, 2, 2, 2.5],
            header=dict(
                values=header_values,
                fill=dict(color=['grey']),
                font=dict(color='white'),
                line=dict(width=2),
                align='center'
            ),
            cells=dict(
                values=cells_values,
                align=['center', 'left', 'center', 'center', 'center', 'center', 'center'],
                fill=dict(color=alert_action(keys=self.tracking_data['Key'], days=self.tracking_data['Days in progress'],
                                             priorities=self.tracking_data['Priority'], olds=self.old_list)),
                height=25,
                line=dict(width=2)
            )
        ), go.Bar(
            orientation='h',
            y=list(self.pivot_data.keys()),
            x=[value['On track'] for value in self.pivot_data.values()],
            xaxis='x1',
            yaxis='y1',
            name='On track',
            showlegend=False,
            text=list(map(lambda el: 'On track: <b>{}</b> '.format(el),
                          [value['On track'] for value in self.pivot_data.values()])),
            textposition='inside',
            marker=dict(
                color='rgb(163,204,163)',
                line=dict(
                    color='grey',
                    width=1
                )
            )
        ), go.Bar(
            orientation='h',
            y=list(self.pivot_data.keys()),
            x=[value['Overdue'] for value in self.pivot_data.values()],
            xaxis='x1',
            yaxis='y1',
            name='Overdue',
            showlegend=False,
            text=list(map(lambda el, link: '<a href = "{}">Overdue: <b>{}</b> </a>'.format(link, el),
                          [value['Overdue'] for value in self.pivot_data.values()], self.overdue_data.values())),
            textposition='inside',
            marker=dict(
                color='rgb(255,204,204)',
                line=dict(
                    color='grey',
                    width=1
                )
            )
        ), go.Bar(
            orientation='h',
            y=list(self.all_bugs.keys()),
            x=[value['On track'] for value in self.all_bugs.values()],
            xaxis='x2',
            yaxis='y2',
            name='On track',
            showlegend=False,
            text=list(map(lambda el: 'On track: <b>{}</b> '.format(el),
                          [value['On track'] for value in self.all_bugs.values()])),
            textposition='inside',
            marker=dict(
                color='rgb(163,204,163)',
                line=dict(
                    color='grey',
                    width=1
                )
            )
        ), go.Bar(
            orientation='h',
            y=list(self.all_bugs.keys()),
            x=[value['Overdue'] for value in self.all_bugs.values()],
            xaxis='x2',
            yaxis='y2',
            name='Overdue',
            showlegend=False,
            text=list(map(lambda el: '<a href = "{}">Overdue: <b>{}</b> </a>'.format(self.jql_all, el),
                          [value['Overdue'] for value in self.all_bugs.values()])),
            textposition='inside',
            marker=dict(
                color='rgb(255,204,204)',
                line=dict(
                    color='grey',
                    width=1
                )
            )
        )]

        title = self.dashboard_name
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        axis = dict()
        layout = go.Layout(
            hovermode='closest',
            title='<b>{} ({})</b>'.format(title, datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
                  + ('<sup> in cloud</sup>' if self.repository == 'online' else '')
                  + '<br><i>SLA: Blockers - 1 day, Criticals - 2 days</i>',
            font=dict(family='Oswald, sans-serif', size=12),
            shapes=[dict(
                type='rect',
                xref='paper',
                yref='paper',
                x0=0.73,
                y0=0.15,
                x1=1,
                y1=1,
                line=dict(
                    color='rgb(0,0,0)',
                    width=1
                )
            ), dict(
                type='rect',
                xref='paper',
                yref='paper',
                x0=0.73,
                y0=0,
                x1=1,
                y1=0.13,
                line=dict(
                    color='rgb(0,0,0)',
                    width=1
                )
            )],
            xaxis1=dict(axis, **dict(domain=[0.77, 0.99], anchor='y1')),
            yaxis1=dict(axis, **dict(domain=[0.18, 0.99], anchor='x1', tickvals=list(self.pivot_data.keys()),
                                     ticktext=[text if len(text) < 11 else '<br>'.join(textwrap.wrap(text, 10))
                                               for text in list(self.pivot_data.keys())],
                                     ticks='outside', ticklen=5, tickcolor='rgba(0,0,0,0)')),
            xaxis2=dict(axis, **dict(domain=[0.77, 0.99], anchor='y2')),
            yaxis2=dict(axis, **dict(domain=[0.03, 0.12], anchor='x2',
                                     ticks='outside', ticklen=5, tickcolor='rgba(0,0,0,0)')),
            barmode='stack'
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
            shutil.move('C:/Users/{}/Downloads/{}.png'.format(self.local_user, title), './files/{}.png'.format(title))
            citrix = CitrixShareFile(hostname=self.citrix_token['hostname'], client_id=self.citrix_token['client_id'],
                                     client_secret=self.citrix_token['client_secret'],
                                     username=self.citrix_token['username'], password=self.citrix_token['password'])
            citrix.upload_file(folder_id='fofd8511-6564-44f3-94cb-338688544aac',
                               local_path='./files/{}.png'.format(title))
            citrix.upload_file(folder_id='fofd8511-6564-44f3-94cb-338688544aac',
                               local_path=html_file)

    def export_to_plot(self):
        self.export_to_plotly()
