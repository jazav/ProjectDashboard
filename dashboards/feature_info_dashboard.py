from dashboards.dashboard import AbstractDashboard
# import json
import plotly
import plotly.graph_objs as go
from datetime import datetime
from adapters.issue_utils import get_domain
from collections import OrderedDict


bulk_convert = {
        'Common': 'Common', 'Infra': 'Infra', 'Billing': 'Billing', 'Business Analysis': 'BA',
        'CRM (Customer Relationship Management)': 'CRM', 'Charge Events Storage': 'Billing',
        'Order Management': 'Ordering', 'Design': 'Design', 'DevOps': 'DevOps', 'DFE (Digital Frontend)': 'DFE',
        'Digital API': 'DFE', 'Documentation': 'Doc', 'Dunning and Collection': 'Billing',
        'Logical Resource Inventory': 'PSC', 'Network Monetization': 'NWM', 'Partner Management': 'PRM',
        'Payment Management': 'Billing', 'Performance Testing': 'Common', 'Product Management': 'PSC', 'QC': 'Common',
        'System Architecture': 'Arch'
    }


class FeatureInfoDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth = True, None, None
    feature_dict, spent_dict, info, commited, wrong_estimates, due_dates, readiness_dict = {}, {}, [], [], {}, {}, {}

    def prepare(self, data):
        for i in range(len(data['Key'])):
            if data['Issue type'][i] == 'User Story (L3)':
                if data['Flagged'][i]:
                    self.commited.append(data['Key'][i])
                if data['Key'][i] not in self.feature_dict.keys():
                    self.feature_dict[data['Key'][i]] = {domain: 0 for domain in bulk_convert.values()
                                                         if domain != 'Common'}
                    self.spent_dict[data['Key'][i]] = {domain: 0 for domain in bulk_convert.values()
                                                       if domain != 'Common'}
                    self.info.append(' ({})<br>{}<br>Due date: {}<br>Status: {}, '
                                     .format(data['FL'][i], data['Feature name'][i],
                                             data['Due date'][i], data['Status'][i]))
                    self.due_dates[data['Key'][i]] = {domain: [] for domain in bulk_convert.values() if domain != 'Common'}
                    self.readiness_dict[data['Key'][i]] = {domain: None for domain in bulk_convert.values() if domain != 'Common'}
                # d = json.loads(data['Estimate'][i]) if data['Estimate'][i] is not None else {}
                # for domain in [key for key in d.keys() if not key.isdigit() and key != 'Total']:
                #     if bulk_convert[domain] != 'Common':
                #         self.feature_dict[data['Key'][i]][bulk_convert[domain]] += float(d[domain]['v'])
            else:
                if get_domain(data['Component'][i]) not in ('Empty', 'Common'):
                    self.spent_dict[data['Feature'][i]][get_domain(data['Component'][i])] += float(data['Spent time'][i]) / 28800
                    self.feature_dict[data['Feature'][i]][get_domain(data['Component'][i])] += float(data['Original estimate'][i]) / 28800
                    if data['Due date'][i] is not None:
                        self.due_dates[data['Feature'][i]][get_domain(data['Component'][i])].append(datetime.strptime(data['Due date'][i], '%d.%m.%Y'))
        for ft, bulk in self.feature_dict.items():
            self.wrong_estimates[ft] = []
            for dmn in bulk.keys():
                if bulk[dmn] < self.spent_dict[ft][dmn]:
                    self.feature_dict[ft][dmn] = self.spent_dict[ft][dmn]
                    self.wrong_estimates[ft].append(dmn)
        for ft, est, sp, i, st in zip(self.feature_dict.keys(), self.feature_dict.values(), self.spent_dict.values(), range(len(self.info)),
                                      [st for st, it in zip(data['Status'], data['Issue type']) if it == 'User Story (L3)']):
            if st != 'Closed':
                try:
                    self.info[i] += 'Readiness: {}%'.format(round(sum(sp.values()) / sum(est.values()) * 100))
                except ZeroDivisionError:
                    self.info[i] += 'Readiness: 0%'
            else:
                self.info[i] += 'Readiness: 100%'
            for dmn, e, s in zip(est.keys(), est.values(), sp.values()):
                try:
                    self.readiness_dict[ft][dmn] = round((s / e), 1)
                except ZeroDivisionError:
                    self.readiness_dict[ft][dmn] = 0
        fd, pt, sd, info, dd, rd = {}, 1, {}, {}, {}, {}
        for ft, est, spent, inf, d, ready in zip(self.feature_dict.keys(), self.feature_dict.values(), self.spent_dict.values(),
                                                 self.info, self.due_dates.values(), self.readiness_dict.values()):
            part = 'part{}'.format(pt)
            if part not in fd.keys():
                fd[part], sd[part], info[part], dd[part], rd[part] = {}, {}, [], {}, {}
            fd[part][ft], sd[part][ft], dd[part][ft], rd[part][ft] = est, spent, d, ready
            info[part].append(inf)
            if len(fd[part].keys()) > 8:
                pt += 1
        self.feature_dict, self.spent_dict, self.info, self.due_dates, self.readiness_dict = fd, sd, info, dd, rd

    def export_to_plotly(self):
        if len(self.feature_dict.keys()) == 0:
            raise ValueError('There is no issues to show')

        for pt, estimates, spents, info, dd, readiness in zip(self.feature_dict.keys(), self.feature_dict.values(),
                                                              self.spent_dict.values(), self.info.values(),
                                                              self.due_dates.values(), self.readiness_dict.values()):
            estimates = {key: value for key, value in zip(reversed(list(estimates.keys())), reversed(list(estimates.values())))}
            spents = {key: value for key, value in zip(reversed(list(spents.keys())), reversed(list(spents.values())))}
            info = list(reversed(info))
            dd = {key: value for key, value in zip(reversed(list(dd.keys())), reversed(list(dd.values())))}
            readiness = {key: value for key, value in zip(reversed(list(readiness.keys())), reversed(list(readiness.values())))}
            print(info)
            data, base = [], [0]*len(spents.keys())
            for dmn in estimates[list(estimates.keys())[0]].keys():
                spent_color, due_color = [], []
                for ft in list(spents.keys()):
                    if ft in self.commited and dmn not in self.wrong_estimates[ft]:
                        spent_color.append('rgba(153,222,153,0.6)')
                    elif dmn in self.wrong_estimates[ft]:
                        spent_color.append('rgba(222,110,110,0.6)')
                    else:
                        spent_color.append('rgba(200,200,200,0.6)')
                for d, ft in zip(dd.values(), readiness.keys()):
                    if len(d[dmn]) == 0:
                        if readiness[ft][dmn] < 1:
                            due_color.append('rgb(230,0,0)')
                        else:
                            due_color.append('rgb(0,0,0)')
                    else:
                        if max(d[dmn]) < datetime.now():
                            if readiness[ft][dmn] < 1:
                                due_color.append('rgb(230,0,0)')
                            else:
                                due_color.append('rgb(0,0,0)')
                        else:
                            due_color.append('rgb(0,0,0)')
                data.append(go.Bar(
                    orientation='h',
                    y=list(estimates.keys()),
                    x=[est[dmn] for est in estimates.values()],
                    name=dmn,
                    showlegend=False,
                    # text=[dmn]*len(estimates.keys()),
                    text=[dmn + ': {}'.format(max(d[dmn]).strftime('%d.%m')) if len(d[dmn]) > 0 else dmn + ': empty' for d in dd.values()],
                    textposition='inside',
                    insidetextfont=dict(
                        color=due_color
                    ),
                    marker=dict(
                        color=['rgb(245,255,245)' if ft in self.commited else 'rgb(250,250,250)' for ft in list(estimates.keys())],
                        opacity=0.5,
                        line=dict(
                            color=['rgb(0,150,0)' if ft in self.commited else 'rgb(0,0,0)' for ft in list(estimates.keys())],
                            width=2
                        )
                    ),
                    base=base,
                    offset=-0.4,
                    width=0.8
                ))
                data.append(go.Bar(
                    orientation='h',
                    y=list(spents.keys()),
                    x=[spent[dmn] for spent in spents.values()],
                    name=dmn,
                    showlegend=False,
                    text='',
                    textposition='inside',
                    marker=dict(
                        color=spent_color
                    ),
                    base=base,
                    offset=-0.39,
                    width=0.78
                ))
                base = [bs + cnt for bs, cnt in zip(base, [est[dmn] for est in estimates.values()])]

            title = '{} Features ({})'.format(self.dashboard_name, pt)
            # html_file = self.png_dir + "{0}.html".format(title)
            html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

            for el in ['<a href="https://jira.billing.ru/browse/{0}">{0}</a>{1}'.format(key, inf) for key, inf in zip(list(estimates.keys()), info)]:
                print(el)
            layout = dict(
                title='<b>{0} as of {1}</b>'.format(title, datetime.now().strftime("%d.%m.%y %H:%M"))
                      + (' <sup>in cloud</sup>' if self.repository == 'online' else ''),
                yaxis=dict(
                    automargin=True,
                    tickvals=list(estimates.keys()),
                    ticktext=['<a href="https://jira.billing.ru/browse/{0}">{0}</a>{1}'.format(key, inf) for key, inf in zip(list(estimates.keys()), info)],
                    ticks='outside',
                    ticklen=10,
                    tickcolor='rgba(0,0,0,0)',
                    tickfont=dict(size=10)
                )
            )

            fig = go.Figure(data=data, layout=layout)
            if self.repository == 'offline':
                plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
            elif self.repository == 'online':
                plotly.tools.set_credentials_file(username=self.plotly_auth[0], api_key=self.plotly_auth[1])
                plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
