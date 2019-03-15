from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
from adapters.issue_utils import get_domain
import math
from plotly import tools


class DomainBurndownDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth, dashboard_type = True, None, None, None
    all_spent, all_remain = {'flagged': {}, 'all': {}}, {'flagged': {}, 'all': {}}

    def multi_prepare(self, data_spent, data_original):
        all_original, spent, original = {}, {}, {}
        fl_all_original, fl_spent, fl_original = {}, {}, {}
        for i in range(len(data_spent['key'])):
            data_spent['component'][i] = get_domain(data_spent['component'][i])
            if data_spent['created'][i] < datetime.date(2019, 2, 18):
                if data_spent['component'][i] not in spent.keys():
                    spent[data_spent['component'][i]] = 0
                spent[data_spent['component'][i]] += float(data_spent['spent'][i])
                if data_spent['flagged'][i] is not None:
                    if data_spent['component'][i] not in fl_spent.keys():
                        fl_spent[data_spent['component'][i]] = 0
                    fl_spent[data_spent['component'][i]] += float(data_spent['spent'][i])
            else:
                if data_spent['component'][i] not in spent.keys():
                    spent[data_spent['component'][i]] = 0
                if data_spent['flagged'][i] is not None:
                    if data_spent['component'][i] not in fl_spent.keys():
                        fl_spent[data_spent['component'][i]] = 0
        for i in range(len(data_original['key'])):
            data_original['component'][i] = get_domain(data_original['component'][i])
            if data_original['status'][i] not in ('Closed', 'Resolved'):
                if data_original['component'][i] not in original.keys():
                    original[data_original['component'][i]] = 0
                original[data_original['component'][i]] += float(data_original['timeoriginalestimate'][i])
                if data_original['flagged'][i] is not None:
                    if data_original['component'][i] not in fl_original.keys():
                        fl_original[data_original['component'][i]] = 0
                    fl_original[data_original['component'][i]] += float(data_original['timeoriginalestimate'][i])
            else:
                if data_original['component'][i] not in original.keys():
                    original[data_original['component'][i]] = 0
                if data_original['flagged'][i] is not None:
                    if data_original['component'][i] not in fl_original.keys():
                        fl_original[data_original['component'][i]] = 0
        for i in range(len(data_spent['key'])):
            if data_spent['created'][i] > datetime.date(2019, 2, 17):
                if data_spent['flagged'][i] is not None:
                    if data_spent['component'][i] not in self.all_spent['flagged'].keys():
                        self.all_spent['flagged'][data_spent['component'][i]] = {}
                    fl_spent[data_spent['component'][i]] += float(data_spent['spent'][i])
                    self.all_spent['flagged'][data_spent['component'][i]][data_spent['created'][i]] = fl_spent[data_spent['component'][i]]
                if data_spent['component'][i] not in self.all_spent['all'].keys():
                    self.all_spent['all'][data_spent['component'][i]] = {}
                spent[data_spent['component'][i]] += float(data_spent['spent'][i])
                self.all_spent['all'][data_spent['component'][i]][data_spent['created'][i]] = spent[data_spent['component'][i]]
        for i in range(len(data_original['key'])):
            if data_original['resolutiondate'][i] is not None:
                if data_original['flagged'][i] is not None:
                    if data_original['component'][i] not in fl_all_original.keys():
                        fl_all_original[data_original['component'][i]] = {}
                    fl_original[data_original['component'][i]] += float(data_original['timeoriginalestimate'][i])
                    fl_all_original[data_original['component'][i]][data_original['resolutiondate'][i]] = fl_original[data_original['component'][i]]
                if data_original['component'][i] not in all_original.keys():
                    all_original[data_original['component'][i]] = {}
                original[data_original['component'][i]] += float(data_original['timeoriginalestimate'][i])
                all_original[data_original['component'][i]][data_original['resolutiondate'][i]] = original[data_original['component'][i]]
        for dt in self.all_spent['all']['BA'].keys():
            print('{}: {}'.format(dt, self.all_spent['all']['BA'][dt]))
        print('----------------------------')
        for dt in all_original['BA'].keys():
            print('{}: {}'.format(dt, all_original['BA'][dt]))
        for dmn, spents in self.all_spent['flagged'].items():
            if dmn not in fl_all_original.keys():
                fl_all_original[dmn] = {dt: 0 for dt in spents.keys()}
            for dt in spents.keys():
                if dt not in fl_all_original[dmn].keys():
                    try:
                        fl_all_original[dmn][dt] = fl_all_original[dmn][max([date for date in fl_all_original[dmn].keys() if date < dt])]
                    except ValueError:
                        fl_all_original[dmn][dt] = fl_all_original[dmn][list(fl_all_original[dmn].keys())[-1]]
        for dmn, spents in self.all_spent['all'].items():
            if dmn not in all_original.keys():
                all_original[dmn] = {dt: 0 for dt in spents.keys()}
            for dt in spents.keys():
                if dt not in all_original[dmn].keys():
                    try:
                        all_original[dmn][dt] = all_original[dmn][max([date for date in all_original[dmn].keys() if date < dt])]
                    except ValueError:
                        all_original[dmn][dt] = all_original[dmn][list(all_original[dmn].keys())[-1]]
        print('----------------------------')
        for dt in self.all_spent['all']['BA'].keys():
            print('{}: {}'.format(dt, self.all_spent['all']['BA'][dt]))
        print('----------------------------')
        for dt in all_original['BA'].keys():
            print('{}: {}'.format(dt, all_original['BA'][dt]))
        for dmn in self.all_spent['flagged'].keys():
            self.all_remain['flagged'][dmn] = {dt: fl_all_original[dmn][dt] - self.all_spent['flagged'][dmn][dt]
                                               + float(sum([sp for sp, rd, domain, fl in zip(data_spent['spent'], data_spent['resolutiondate'], data_spent['component'], data_spent['flagged'])
                                                            if fl is not None and domain == dmn and rd is not None and rd < dt])) for dt in self.all_spent['flagged'][dmn].keys()}
        for dmn in self.all_spent['all'].keys():
            if dmn == 'BA':
                print([all_original[dmn][dt] for dt in self.all_spent['all'][dmn].keys()])
                print([self.all_spent['all'][dmn][dt] for dt in self.all_spent['all'][dmn].keys()])
                print([float(sum([sp for sp, rd, domain in zip(data_spent['spent'], data_spent['resolutiondate'], data_spent['component']) if domain == dmn and rd is not None and rd < dt])) for dt in self.all_spent['all'][dmn].keys()])
            self.all_remain['all'][dmn] = {dt: all_original[dmn][dt] - self.all_spent['all'][dmn][dt]
                                           + float(sum([sp for sp, rd, domain in zip(data_spent['spent'], data_spent['resolutiondate'], data_spent['component'])
                                                        if domain == dmn and rd is not None and rd < dt])) for dt in self.all_spent['all'][dmn].keys()}
        # for fl, data_spent, data_remain in zip(self.all_spent.keys(), self.all_spent.values(), self.all_remain.values()):
        #     print(fl)
        #     for dmn, spents, remains in zip(data_spent.keys(), data_spent.values(), data_remain.values()):
        #         print('    {}'.format(dmn))
        #         for dt, sp, rm in zip(spents.keys(), spents.values(), remains.values()):
        #             print('        {}: {} (spent), {} (remain)'.format(dt, sp, rm))

    def export_to_plotly(self):
        for fl, spents, remains in zip(self.all_spent.keys(), self.all_spent.values(), self.all_remain.values()):
            end = datetime.date(2019, 3, 18) if fl == 'flagged' else datetime.date(2019, 3, 29)
            trace_dict = {dmn: [] for dmn in spents.keys()}
            for dmn in spents.keys():
                trace_dict[dmn].append(go.Scatter(
                    x=list(spents[dmn].keys()),
                    y=list(spents[dmn].values()),
                    name='Spent',
                    mode='lines+markers',
                    line=dict(
                        width=2,
                        color='rgb(31,119,180)',
                    ),
                    marker=dict(
                        size=3,
                        color='rgb(31,119,180)',
                    ),
                    showlegend=True if dmn == list(spents.keys())[0] else False
                ))
                trace_dict[dmn].append(go.Scatter(
                    x=list(remains[dmn].keys()),
                    y=list(remains[dmn].values()),
                    name='Remain',
                    mode='lines+markers',
                    line=dict(
                        width=2,
                        color='rgb(255,127,14)',
                    ),
                    marker=dict(
                        size=3,
                        color='rgb(255,127,14)',
                    ),
                    showlegend=True if dmn == list(spents.keys())[0] else False
                ))
                trace_dict[dmn].append(go.Scatter(
                    x=[min(remains[dmn].keys()), end],
                    y=[max([math.fabs(rmn) for rmn in remains[dmn].values()]), 0],
                    name='',
                    mode='lines',
                    line=dict(
                        color='rgb(200,200,200)',
                        width=2,
                        dash='dash'),
                    showlegend=False
                ))
            cols = math.ceil(len(spents.keys()) / 2)
            fig = tools.make_subplots(rows=2, cols=cols, subplot_titles=list(spents.keys()))
            for traces, i, dmn in zip(trace_dict.values(), range(len(trace_dict.keys())), trace_dict.keys()):
                row, col = int(i // cols + 1), int(i % cols + 1)
                for trace in traces:
                    fig.append_trace(trace, row, col)
                xaxis, yaxis = 'xaxis{}'.format(i + 1), 'yaxis{}'.format(i + 1)
                fig["layout"][xaxis].update(
                    type='date',
                    dtick=86400000,
                    showline=True,
                    showticklabels=False
                )
                fig["layout"][yaxis].update(
                    showline=True,
                    # range=[0, max([math.fabs(rmn) for rmn in remains[dmn].values()]) + 10]
                )

            title = '{} for domains ({})'.format(self.dashboard_name, fl)
            # html_file = self.png_dir + "{0}.html".format(title)
            html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

            fig["layout"].update(title='<b>{0} as of {1}</b>'.format(title, datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
                                       + (' <sup>in cloud</sup>' if self.repository == 'online' else ''))
            if self.repository == 'offline':
                plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
            elif self.repository == 'online':
                plotly.tools.set_credentials_file(username=self.plotly_auth[0], api_key=self.plotly_auth[1])
                plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)


    def export_to_plot(self):
        self.export_to_plotly()
