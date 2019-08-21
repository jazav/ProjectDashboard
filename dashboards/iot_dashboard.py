from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time


def color_for_est(est):
    return {'Plan estimate': 'rgb(44,160,44)', 'Fact estimate': 'rgb(255,127,14)', 'Spent time': 'rgb(31,119,180)'}[est]


class IotDashboard(AbstractDashboard):
    auto_open, repository, citrix_token, local_user = True, None, None, None
    iot_dict, ticktext, nis, jql_nis = {'AEP': {}, 'CMP': {}}, {'AEP': [], 'CMP': []}, [], {'AEP': {}, 'CMP': {}}
    jql_empty = {'AEP': 'https://jira.billing.ru/issues/?jql=key in (',
                 'CMP': 'https://jira.billing.ru/issues/?jql=key in ('}

    def prepare(self, data):
        for i in range(len(data['Key'])):
            if data['Issue type'][i] != 'Epic':
                epic = data['Epic key'][i] if data['Epic key'][i] is not None else 'Empty'
                prj = data['Key'][i][3:6]
                if data['Epic name'][i] is None:
                    data['Epic name'][i] = ''
                    self.jql_empty[prj] += '{}, '.format(data['Key'][i])
                if epic not in self.iot_dict[prj].keys():
                    self.iot_dict[prj][epic] = {'Plan estimate': 0, 'Fact estimate': 0, 'Spent time': 0}
                    self.ticktext[prj].append(data['Epic name'][i])
                if not data['In sprint'][i] and epic != 'Empty':
                    self.nis.append(data['Epic key'][i])
                    if epic not in self.jql_nis[prj]:
                        self.jql_nis[prj][epic] = 'https://jira.billing.ru/issues/?jql=key in ('
                    self.jql_nis[prj][epic] += '{}, '.format(data['Key'][i])
                self.iot_dict[prj][epic]['Fact estimate'] += float(data['Original estimate'][i])
                self.iot_dict[prj][epic]['Spent time'] += float(data['Spent time'][i])
            else:
                epic = data['Key'][i]
                prj = data['Key'][i][3:6]
                if epic not in self.iot_dict[prj].keys():
                    self.iot_dict[prj][epic] = {'Plan estimate': 0, 'Fact estimate': 0, 'Spent time': 0}
                    self.ticktext[prj].append(data['Summary'][i])
                if not data['In sprint'][i]:
                    self.nis.append(data['Key'][i])
                self.iot_dict[prj][epic]['Plan estimate'] += float(data['Original estimate'][i])
        self.jql_empty = {prj: '{})'.format(jql[:-2]) for prj, jql in self.jql_empty.items()}
        self.jql_nis = {prj: {epic: '{})'.format(jql[:-2]) for epic, jql in self.jql_nis[prj].items()}
                        for prj in self.jql_nis.keys()}

    def export_to_plotly(self):
        if len(self.iot_dict[list(self.iot_dict.keys())[0]].keys()) == 0:
            raise ValueError('There is no issues to show')

        data, xtitle = [], {'AEP': None, 'CMP': None}
        for prj, i in zip(self.iot_dict.keys(), range(len(self.iot_dict.keys()))):
            xtitle[prj] = '<b><i>IOT{} Project:</i></b><br>Plan estimate: {}, Fact estimate: {}, Spent time: {}'.\
                format(prj, round(sum([e['Plan estimate'] for epic, e in self.iot_dict[prj].items()
                                       if epic not in set(self.nis)])),
                       round(sum([e['Fact estimate'] for epic, e in self.iot_dict[prj].items()
                                  if epic not in set(self.nis)]), 1),
                       round(sum([e['Spent time'] for e in self.iot_dict[prj].values()])), 1)
            for est in self.iot_dict[prj][list(self.iot_dict[prj].keys())[0]].keys():
                data.append(go.Bar(
                    y=[epic for epic in self.iot_dict[prj].keys() if self.iot_dict[prj][epic]['Spent time'] >= 0],
                    x=[e[est] for epic, e in self.iot_dict[prj].items() if self.iot_dict[prj][epic]['Spent time'] >= 0],
                    xaxis='x{}'.format(i+1),
                    yaxis='y{}'.format(i+1),
                    orientation='h',
                    name=est,
                    showlegend=True if i == 1 else False,
                    text=[round(e[est], 1) for epic, e in self.iot_dict[prj].items()
                          if self.iot_dict[prj][epic]['Spent time'] >= 0],
                    textposition='auto',
                    marker=dict(
                        color=color_for_est(est),
                        line=dict(
                            width=1
                        )
                    )
                ))

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        axis = dict()
        layout = dict(
            hovermode='closest',
            title='<b>{0} as of {1}</b>'.format(self.dashboard_name, datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
                  + (' <sup>in cloud</sup>' if self.repository == 'online' else ''),
            xaxis1=dict(axis, **dict(domain=[0, 0.49], anchor='y1', showgrid=True, title=xtitle['AEP'])),
            yaxis1=dict(axis, **dict(domain=[0, 1], anchor='x1', showline=True, showgrid=True, automargin=True,
                                     tickvals=list(self.iot_dict['AEP'].keys()),
                                     ticktext=[
                                         '<a href="https://jira.billing.ru/browse/{0}">{0}<br></a>'.format(epic) + (
                                             '<a href="{}">{}</a>'.format(self.jql_nis['AEP'][epic], (
                                                 '{}...'.format(text[:25]) if len(text) > 25 else text)) if epic in set(
                                                 self.nis) else ('{}...'.format(text[:25]) if len(
                                                 text) > 25 else text)) if epic != 'Empty' else '<a href="{}">{}</a>'.format(
                                             self.jql_empty['AEP'], epic) for epic, text in
                                         zip(list(self.iot_dict['AEP'].keys()), self.ticktext['AEP'])]),
                        ticks='outside', ticklen=10, tickcolor='rgba(0,0,0,0)'),
            xaxis2=dict(axis, **dict(domain=[0.51, 1], anchor='y2', showgrid=True, title=xtitle['CMP'],
                                     range=[max([max(e.values()) for e in self.iot_dict['CMP'].values()]), 0])),
            yaxis2=dict(axis, **dict(domain=[0, 1], anchor='x2', showline=True, showgrid=True, automargin=True,
                                     tickvals=list(self.iot_dict['CMP'].keys()),
                                     ticktext=[
                                         '<a href="https://jira.billing.ru/browse/{0}">{0}<br></a>'.format(epic) + ((
                                             '<a href="{}">{}</a>'.format(self.jql_nis['CMP'][epic], (
                                                 '{}...'.format(text[:25]) if len(text) > 25 else text)) if epic in set(
                                                 self.nis) else ('{}...'.format(text[:25]) if len(
                                                 text) > 25 else text))) if epic != 'Empty' else '<a href="{}">{}</a>'.format(
                                             self.jql_empty['CMP'], epic) for epic, text in
                                         zip(list(self.iot_dict['CMP'].keys()), self.ticktext['CMP'])], side='right'),
                        ticks='outside', ticklen=10, tickcolor='rgba(0,0,0,0)'),
            legend=dict(orientation='h', x=0.38, y=1.04)
        )

        fig = go.Figure(data=data, layout=layout)
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
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
