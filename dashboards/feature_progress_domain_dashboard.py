import pandas as pd
import plotly
import plotly.graph_objs as go

import dashboards.prepare_feature_data as pfd
from dashboards.dashboard import AbstractDashboard

PLAN_PREFIX = '<b>Plan: </b>'
FACT_PREFIX = '<b>Fact: </b>'


class FeatureProgressDomainDashboard(AbstractDashboard):
    '''Plotly Bar Stacked Chart'''

    def prepare(self, data):

        columns_size = 0
        epic_df = data[(data.issuetype == "Epic")]
        epic_df = epic_df[epic_df["labels"].str.contains(pat="num34.01")]
        #epic_df = epic_df[epic_df["labels"].str.contains(pat="num")]
        plan_df, fact_df = pfd.prepare_domain(epic_data=epic_df, issue_data=data, or_filter_list=self.filter_list,
                                       and_filter_list=["SuperSprint6"],
                                       plan_prefix=PLAN_PREFIX, fact_prefix=FACT_PREFIX, with_total=False,
                                       details=self.details,project_fiter_list=self.project_list)
        columns_size = plan_df.columns.size

        self.data = pd.DataFrame()

        for idx in range(0, columns_size):
            if self.fact:
                self.data[fact_df.columns[idx]] = fact_df[fact_df.columns[idx]]
            if self.plan:
                self.data[plan_df.columns[idx]] = plan_df[plan_df.columns[idx]]

        self.data = self.data.reindex(sorted(self.data.columns, key=lambda x: x[len(PLAN_PREFIX):], reverse=False),
                                      axis=1)

        #self.data = self.data.assign(tmp=self.data.sum(axis=1)).sort_values('tmp', ascending=False)
        #self.data = self.data.sort_values(by=, ascending=False)

    def export_to_plotly(self):

        if len(self.data) == 0:
            return

        ind = 1

        feature_name_max_length = max(len(column) for column in self.data.columns)

        first_feature = 0
        last_feature = self.data.columns.size

        loop_exit = False

        # screen loop
        for current_feature in range(first_feature, last_feature, self.items_on_chart):

            final_feature = current_feature + self.items_on_chart
            if last_feature - final_feature <= self.min_item_tail:
                final_feature = last_feature
                loop_exit = True

                #
            # data_frame[row1:row2, column1:column2]
            #
            data_part = self.data.iloc[:, current_feature:final_feature]
            # reverse sorting due to go from top to down
            data_part = data_part.reindex(
                sorted(data_part.columns, key=lambda x: x[len(PLAN_PREFIX):], reverse=True), axis=1)

            traces = list()
            shapes = list()

            # now the colors
            # clrred = 'rgb(222,0,0)'
            # clrgrn = 'rgb(0,222,0)'

            for component_idx in range(0, len(data_part)):
                # clrs = [clrred if x%2 else clrgrn for x in range(data_part.iloc[component_idx].size)]
                total = str(data_part.iloc[component_idx].values.sum())

                bar_plan = go.Bar(
                    y=data_part.columns,
                    x=data_part.iloc[component_idx],
                    name=data_part.index[component_idx],
                    textposition='auto',
                    orientation='h',
                    legendgroup=data_part.index[component_idx],
                    hoverinfo='name + text',
                    text=data_part.iloc[component_idx],

                    # marker=[x for x in dict(color=clrred)]
                )
                traces.append(bar_plan)
            plan_fact_str = ''
            if self.plan:
                plan_fact_str = 'plan '
            if self.fact:
                plan_fact_str = plan_fact_str + 'fact'

            if last_feature > self.items_on_chart:
                title = "{0} \nPart #{1} <br>{2}".format(self.dashboard_name.replace('num', ''), str(ind),
                                                         plan_fact_str)
            else:
                title = "{0} <br>{1}".format(self.dashboard_name, plan_fact_str)

            layout = go.Layout(
                annotations=[
                    dict(
                        x=1.09,
                        y=1.03,
                        xref='paper',
                        yref='paper',
                        text='Components',
                        showarrow=False,
                        font=dict(
                            family='sans-serif',
                            size=12,
                            color='#000'
                        )
                    )
                ],
                legend=dict(
                    x=1,
                    y=1,
                    traceorder='normal',
                    font=dict(
                        family='sans-serif',
                        size=10,
                        color='#000'
                    )
                ),
                showlegend=True,
                margin=dict(t=50, b=50, r=100, l=feature_name_max_length * 6),
                autosize=True,
                font=dict(size=9, color='black'),
                barmode='stack',
                shapes=shapes,
                title=title,
                plot_bgcolor='white',
                yaxis=dict(
                    rangemode="tozero",
                    autorange=True,
                    showgrid=True,
                    zeroline=True,
                    showline=True,
                    ticks='',
                    showticklabels=True,
                    tickangle=0,
                    tickfont=dict(
                        size=10,
                        color='black'

                    ),
                ),
                xaxis=dict(
                    rangemode="tozero",
                    autorange=True,
                    showgrid=True,
                    zeroline=True,
                    showline=True,
                    ticks='',
                    showticklabels=True,
                    tickfont=dict(
                        size=10,
                        color='black'

                    ),
                    title='Estimates (man-days)',
                    titlefont=dict(
                        size=16,
                        color='black'
                    )
                )
            )
            file_name = self.dashboard_name.replace('num', '') + ' ' + plan_fact_str
            html_file = self.png_dir + "{0}_{1}.html".format(file_name, str(ind))
            fig = go.Figure(data=traces, layout=layout)
            plotly.offline.plot(fig, filename=html_file, auto_open=True)

            ind = ind + 1
            if loop_exit:
                break

    def export_to_plot(self):
        self.export_to_plotly()

    def export_to_json(self):
        raise NotImplementedError('export_to_json')
