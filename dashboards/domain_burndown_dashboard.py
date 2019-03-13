from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
from adapters.issue_utils import get_domain


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
        for i in range(len(data_original)):
            data_original['component'][i] = get_domain(data_original['component'][i])
            print(data_original['component'][i])
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
        for dmn, spents in self.all_spent['flagged'].items():
            for dt in spents.keys():
                if dt not in fl_all_original[dmn].keys():
                    fl_all_original[dmn][dt] = fl_all_original[dmn][max([date for date in fl_all_original[dmn].keys() if date < dt])]
        for dmn, spents in self.all_spent['all'].items():
            for dt in spents.keys():
                if dt not in all_original[dmn].keys():
                    all_original[dmn][dt] = all_original[dmn][max([date for date in all_original[dmn].keys() if date < dt])]
        for dmn in self.all_spent['flagged'].keys():
            self.all_remain['flagged'][dmn] = {dt: fl_all_original[dmn][dt] - self.all_spent['flagged'][dmn][dt]
                                               + float(sum([sp for sp, rd, domain in zip(data_spent['spent'], data_spent['resolutiondate'], data_spent['component'])
                                                            if domain == dmn and rd is not None and rd < dt])) for dt in self.all_spent['flagged'][dmn].keys()}
        for dmn in self.all_spent['all'].keys():
            self.all_remain['all'][dmn] = {dt: all_original[dmn][dt] - self.all_spent['all']
                                           + float(sum([sp for sp, rd, domain, fl in zip(data_spent['spent'], data_spent['resolutiondate'], data_spent['component'], data_spent['flagged'])
                                                        if fl is not None and domain == dmn and rd is not None and rd < dt])) for dt in self.all_spent['all'][dmn].keys()}
        for fl, data_spent, data_remain in zip(self.all_spent.keys(), self.all_spent.values(), self.all_remain.values()):
            print(fl)
            for dmn, spents, remains in zip(data_spent.keys(), data_spent.values(), data_remain.values()):
                print('    {}'.format(dmn))
                for dt, sp, rm in zip(spents.keys(), spents.values(), remains.values()):
                    print('        {}: {} (spent), {} (remain)'.format(dt, sp, rm))

    def export_to_plotly(self):
        pass

    def export_to_plot(self):
        self.export_to_plotly()
