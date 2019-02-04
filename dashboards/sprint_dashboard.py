from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain_by_project, get_domain
import math
import plotly.plotly
import plotly.graph_objs as go


def domain_position(row, col, cols):
    # delta = 0.05
    # length = round(((0.6-(cols-1)*delta)/cols), 2)
    # start, end, x_pos = 0.4, length, {}
    # for i in range(1, cols+1):
    #     x_pos[i] = [start, end]
    #     start = end + delta
    #     end = start + length
    x_pos = {
        1: [0, 0.16],
        2: [0.17, 0.33],
        3: [0.34, 0.5]
    }
    y_pos = {
        1: [0.68, 1],
        2: [0.34, 0.66],
        3: [0, 0.32]
    }
    return dict(
        x=x_pos[col],
        y=y_pos[row]
    )


class SprintDashboard(AbstractDashboard):
    auto_open, fixversion, repository = True, None, None
    key_list, project_list, status_list, components_list, timeoriginalestimate_list, timespent_list, issuetype_list = \
        [], [], [], [], [], [], []
    domain_list, bugs_dict, accuracy_dict = [], {}, {}

    def prepare(self, data):
        self.key_list, self.project_list, self.status_list, self.components_list, self.timeoriginalestimate_list,\
         self.timespent_list, self.issuetype_list = data.get_sprint_info(self.fixversion)
        print(len(self.key_list))
        for i in range(len(self.key_list)):
            if self.issuetype_list[i] == 'Bug':
                self.components_list[i] = self.components_list[i].split(',')
                if len(self.components_list[i]) != 1:
                    for _ in range(1, len(self.components_list[i])):
                        self.components_list.append([self.components_list[i].pop()])
                        self.key_list.append(self.key_list[i])
                        self.project_list.append(self.project_list[i])
                        self.status_list.append(self.status_list[i])
                        self.timeoriginalestimate_list.append(self.timeoriginalestimate_list[i])
                        self.timespent_list.append(self.timespent_list[i])
                        self.issuetype_list.append(self.issuetype_list[i])
        self.domain_list = [None] * len(self.key_list)
        for i in range(len(self.key_list)):
            if self.issuetype_list[i] != 'Bug':
                self.domain_list[i] = get_domain_by_project(self.project_list[i])
                if self.domain_list[i] not in self.accuracy_dict.keys():
                    self.accuracy_dict[self.domain_list[i]] = {'Plan': 0, 'Fact': 0}
                self.accuracy_dict[self.domain_list[i]]['Plan'] += self.timeoriginalestimate_list[i]
                self.accuracy_dict[self.domain_list[i]]['Fact'] += self.timespent_list[i]
            else:
                if self.components_list[i] != [''] and get_domain(*self.components_list[i]) != 'Others':
                    self.domain_list[i] = get_domain(*self.components_list[i])
                else:
                    self.domain_list[i] = get_domain_by_project(self.project_list[i])
                if self.domain_list[i] not in self.bugs_dict.keys():
                    self.bugs_dict[self.domain_list[i]] = {'Open': 0, 'In Fix': 0, 'Closed': 0}
                self.bugs_dict[self.domain_list[i]][self.status_list[i]] += 1

    def export_to_plotly(self):
        if len(self.key_list) == 0:
            raise ValueError('There is no issues to show')

        plotly.tools.set_credentials_file(username='Rnd-Rnd', api_key='GFSxsbDP8rOiakf0rs8U')

        data = []
        cols = math.ceil(len(self.bugs_dict.keys()) / 3)
        for domain, i in zip(self.bugs_dict.keys(), range(len(self.bugs_dict.keys()))):
            row, col = int((i // cols) + 1), int((i % cols) + 1)
            data.append(go.Pie(
                labels=list(self.bugs_dict[domain].keys()),
                values=list(self.bugs_dict[domain].values()),
                hoverinfo='label+percent',
                textinfo='label+value',
                hole=0.4,
                domain=domain_position(row, col, cols),
                marker=dict(
                    colors=['rgb(75,103,132)', 'rgb(254,210,92)', 'rgb(29,137,49)']
                ),
                showlegend=False,
                title=domain,
                titleposition='middle center'
            ))
        timeoriginalestimate, timespent, annotations = [], [], []
        for domain in self.accuracy_dict.keys():
            timeoriginalestimate.append(self.accuracy_dict[domain]['Plan'])
            timespent.append(self.accuracy_dict[domain]['Fact'])
        data.append(go.Bar(
            orientation='h',
            y=list(self.accuracy_dict.keys()),
            x=timeoriginalestimate,
            xaxis='x1',
            yaxis='y1',
            name='Original Estimate',
            showlegend=True,
            text=list(map(lambda x: round(x, 2), timeoriginalestimate)),
            textposition='auto'
        ))
        data.append(go.Bar(
            orientation='h',
            y=list(self.accuracy_dict.keys()),
            x=timespent,
            xaxis='x1',
            yaxis='y1',
            name='Spent Time',
            showlegend=True,
            text=list(map(lambda x: round(x, 2), timespent)),
            textposition='auto'
        ))
        for domain in self.accuracy_dict.keys():
            # est_acc = 100 - math.fabs(
            #     100 - (self.accuracy_dict[domain]['Plan'] / self.accuracy_dict[domain]['Fact'] * 100))
            acc_fac = self.accuracy_dict[domain]['Fact'] / self.accuracy_dict[domain]['Plan']
            annotations.append(dict(
                x=self.accuracy_dict[domain]['Fact'] + max(timespent)/5,
                y=domain,
                xref='x1',
                yref='y1',
                showarrow=False,
                text='Accuracy factor:<br>{0:.2f}'.format(acc_fac),
                align='center',
                bordercolor='black',
                borderwidth=2,
                borderpad=4
            ))

        axis = dict()
        layout = dict(
            legend=dict(
                orientation='h',
                x=0.695,
                y=1.05
            ),
            title=self.dashboard_name + (' <sup>in cloud</sup>' if self.repository == 'online' else ''),
            annotations=annotations,
            xaxis1=dict(axis, **dict(domain=[0.55, 1], anchor='y1')),
            yaxis1=dict(axis, **dict(domain=[0, 1]), anchor='x1', ticksuffix='  ')
        )

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        fig = go.Figure(data=data, layout=layout)
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
