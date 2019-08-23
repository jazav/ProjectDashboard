from dashboards.dashboard import AbstractDashboard
import datetime
from datetime import timedelta
from jira import JIRA
import plotly
import plotly.graph_objs as go
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time


class SprintOverviewDashboard(AbstractDashboard):
    auto_open, repository, citrix_token, local_user, user, password, sprint = True, None, None, None, None, None, None

    @staticmethod
    def upload_sprint(jira, sprint, dates):
        issue_dict, done_dict, count_dict = {}, {date: set() for date in dates}, {date: 0 for date in dates}
        jql_str = 'filter = "Tasks and subtasks in {0}"'.format(sprint)
        tsts = jira.search_issues(jql_str=jql_str, maxResults=False, expand='changelog')
        jql_str = 'filter = "Epics in {0}"'.format(sprint)
        epic_dict = {
            epic.key: [cmp['name'] for cmp in epic.raw['fields']['components']] if epic.fields.components else []
            for epic in jira.search_issues(jql_str=jql_str, maxResults=False, fields='components')}
        for i, tst in enumerate(tsts, 1):
            print('{}/{} tasks and subtasks are uploaded'.format(i, len(tsts)))
            created = datetime.datetime.strptime(tst.fields.created, '%Y-%m-%dT%H:%M:%S.%f%z').date()
            for date in dates:
                if created <= date:
                    count_dict[date] += 1

            original = float(tst.fields.timeoriginalestimate) if tst.fields.timeoriginalestimate else 0
            spent = float(tst.fields.timespent) if tst.fields.timespent else 0
            original = spent if spent > original or tst.fields.status.name in ('Resolved', 'Closed', 'Done') else original
            epic = tst.fields.customfield_10201 if tst.fields.issuetype.name != 'Sub-task' \
                else [task for task in tsts if task.key == tst.fields.parent.key][0].fields.customfield_10201
            issue_dict[tst.key] = {date: {'original': original, 'spent': 0,
                                          'components': epic_dict[epic]} for date in dates}
            changelog = tst.changelog
            for history in changelog.histories:
                dt = datetime.datetime.strptime(history.created, '%Y-%m-%dT%H:%M:%S.%f%z').date()
                for item in history.items:
                    if item.field == 'status':
                        for date in dates:
                            if date - datetime.timedelta(days=6) <= dt <= date \
                                    and item.toString in ('Resolved', 'Closed', 'Done'):
                                if tst.key not in [key for keys in done_dict.values() for key in keys]:
                                    done_dict[date].add(tst.key)
                    elif item.field == 'timespent':
                        for date in dates:
                            if dt <= date:
                                issue_dict[tst.key][date]['spent'] = item.toString

        spents, originals = {date: 0 for date in dates}, {date: 0 for date in dates}
        for key, changelog in issue_dict.items():
            for date in dates:
                if not any(
                        cmp in changelog[date]['components'] for cmp in ('Documentation', 'QC Design', 'QC Testing')):
                    spents[date] += float(changelog[date]['spent'])
                    originals[date] += float(changelog[date]['original'])

        done_dict = {date: len(keys) for date, keys in done_dict.items()}
        return {date: round(spents[date] / originals[date] * 100, 2) for date in dates}, count_dict, done_dict

    @staticmethod
    def upload_bugs(jira, dates):
        bug_dict = {date: set() for date in dates}
        end, start = dates[-1].strftime('%Y/%m/%d'), (dates[0] - timedelta(days=6)).strftime('%Y/%m/%d')
        jql_str = 'project = BSSBOX AND issuetype = Bug AND status changed TO (Closed, Resolved, Done) ' \
                  'DURING ("{}", "{}")'.format(start, end)
        bugs = jira.search_issues(jql_str=jql_str, maxResults=False, expand='changelog')
        for i, bug in enumerate(bugs, 1):
            print('{}/{} bug(-s) uploaded'.format(i, len(bugs)))
            changelog = bug.changelog
            for history in changelog.histories:
                dt = datetime.datetime.strptime(history.created, '%Y-%m-%dT%H:%M:%S.%f%z').date()
                for item in history.items:
                    if item.field == 'status':
                        for date in dates:
                            if date - datetime.timedelta(days=5) <= dt <= date \
                                    and item.toString in ('Closed', 'Resolved', 'Done'):
                                if bug.key not in [key for keys in bug_dict.values() for key in keys]:
                                    bug_dict[date].add(bug.key)

        bug_dict = {date: len(keys) for date, keys in bug_dict.items()}
        return bug_dict

    def export_to_plotly(self):
        jira = JIRA(server='https://jira.billing.ru', basic_auth=(self.user, self.password))

        date, dates = datetime.date(2019, 7, 5), []
        while date <= datetime.datetime.now().date():
            dates.append(date)
            date += datetime.timedelta(days=7)

        bugs = self.upload_bugs(jira=jira, dates=dates)
        readiness, count_dict, done_dict = self.upload_sprint(jira=jira, sprint=self.sprint, dates=dates)

        data = [go.Scatter(
            x=list(readiness.keys()),
            y=list(readiness.values()),
            name='Readiness',
            xaxis='x1',
            yaxis='y1',
            text=list(readiness.values()),
            textposition='top left',
            mode='lines+markers+text',
            line=dict(
                width=2,
                color='rgb(158,244,82)'
            ),
            marker=dict(
                size=5,
                color='rgb(158,244,82)'
            ),
            showlegend=False
        ), go.Bar(
            x=list(bugs.keys()),
            y=list(bugs.values()),
            name='Bugs',
            xaxis='x2',
            yaxis='y2',
            text=list(bugs.values()),
            textposition='inside',
            marker=dict(
                color='rgba(97,100,223,0.4)',
                line=dict(
                    color='rgb(97,100,223)',
                    width=2
                )
            ),
            showlegend=False
        ), go.Bar(
            x=list(done_dict.keys()),
            y=list(done_dict.values()),
            name='Done count',
            xaxis='x3',
            yaxis='y3',
            text=list(done_dict.values()),
            textposition='inside',
            marker=dict(
                color='rgba(82,162,218,0.4)',
                line=dict(
                    color='rgb(82,162,218)',
                    width=2
                )
            ),
            showlegend=False
        ), go.Scatter(
            x=list(count_dict.keys()),
            y=list(count_dict.values()),
            name='Total count',
            xaxis='x4',
            yaxis='y4',
            text=list(count_dict.values()),
            textposition='top left',
            mode='lines+markers+text',
            line=dict(
                width=2,
                color='rgb(75,223,156)'
            ),
            marker=dict(
                size=5,
                color='rgb(75,223,156)'
            ),
            showlegend=False
        )]

        title = self.dashboard_name
        layout = go.Layout(
            hovermode='closest',
            plot_bgcolor='white',
            title=dict(
                text=title,
                x=0.5
            ),
            xaxis1=dict(
                showline=True,
                domain=[0, 0.45],
                anchor='y1',
                type='date',
                dtick=604800000,
                title='Dates',
                range=[dates[0] - timedelta(days=2), dates[-1] + timedelta(days=2)],
                tickvals=dates,
                ticktext=[datetime.datetime.strftime(tick, '%d.%m.%y') for tick in dates],
                ticks='outside', ticklen=5, tickcolor='rgba(0,0,0,0)',
                linecolor='black',
                gridcolor='rgb(232,232,232)'
            ),
            xaxis2=dict(
                showline=True,
                domain=[0.55, 1],
                anchor='y2',
                type='date',
                dtick=604800000,
                title='Dates',
                range=[dates[0] - timedelta(days=7), dates[-1] + timedelta(days=7)],
                tickvals=dates,
                ticktext=[datetime.datetime.strftime(tick, '%d.%m.%y') for tick in dates],
                ticks='outside', ticklen=5, tickcolor='rgba(0,0,0,0)',
                linecolor='black',
                gridcolor='rgb(232,232,232)'
            ),
            xaxis3=dict(
                showline=True,
                domain=[0, 0.45],
                anchor='y3',
                type='date',
                dtick=604800000,
                title='Dates',
                range=[dates[0] - timedelta(days=7), dates[-1] + timedelta(days=7)],
                tickvals=dates,
                ticktext=[datetime.datetime.strftime(tick, '%d.%m.%y') for tick in dates],
                ticks='outside', ticklen=5, tickcolor='rgba(0,0,0,0)',
                linecolor='black',
                gridcolor='rgb(232,232,232)'
            ),
            xaxis4=dict(
                showline=True,
                domain=[0.55, 1],
                anchor='y4',
                type='date',
                dtick=604800000,
                title='Dates',
                range=[dates[0] - timedelta(days=2), dates[-1] + timedelta(days=2)],
                tickvals=dates,
                ticktext=[datetime.datetime.strftime(tick, '%d.%m.%y') for tick in dates],
                ticks='outside', ticklen=5, tickcolor='rgba(0,0,0,0)',
                linecolor='black',
                gridcolor='rgb(232,232,232)'
            ),
            yaxis1=dict(
                domain=[0.55, 1],
                title='Sprint scope readiness, %',
                showline=True,
                anchor='x1',
                ticks='outside', ticklen=5, tickcolor='rgba(0,0,0,0)',
                linecolor='black',
                gridcolor='rgb(232,232,232)'
            ),
            yaxis2=dict(
                domain=[0.55, 1],
                title='Count of closed and resolved bugs',
                showline=True,
                anchor='x2',
                ticks='outside', ticklen=5, tickcolor='rgba(0,0,0,0)',
                linecolor='black',
                gridcolor='rgb(232,232,232)'
            ),
            yaxis3=dict(
                domain=[0, 0.45],
                title='Count of closed and resolved issues',
                showline=True,
                anchor='x3',
                ticks='outside', ticklen=5, tickcolor='rgba(0,0,0,0)',
                linecolor='black',
                gridcolor='rgb(232,232,232)'
            ),
            yaxis4=dict(
                domain=[0, 0.45],
                title='Count of issues in sprint scope',
                showline=True,
                anchor='x4',
                ticks='outside', ticklen=5, tickcolor='rgba(0,0,0,0)',
                linecolor='black',
                gridcolor='rgb(232,232,232)'
            )
        )

        html_file = '//billing.ru/dfs/incoming/ABryntsev/{}.html'.format(title)
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
