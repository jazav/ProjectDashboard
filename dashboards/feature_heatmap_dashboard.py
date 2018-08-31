import seaborn as sns
import matplotlib.pyplot as plt
from dashboards.dashboard import AbstractDashboard
import dashboards.prepare_feature_data as pfd

FEATURE_COUNT_ON_CHART = 40


class FeatureHeatmapDashboard(AbstractDashboard):
    '''Heatmap feature-component'''

    def prepare(self, data):
        self.data = pfd.prepare(epic_data=data, or_filter_list=self.dashboard_name, with_total=True)
        return self.data

    def export_seaborn(self):

        if len(self.data) == 0:
            return

        # for index, row in self.data.itertuples():
        #      bar.text(row.index, row['timeoriginalestimate'], round(row['timeoriginalestimate'], 2), color='black', ha="center")

        ind = 1

        for i in range(0, self.data.columns.size, FEATURE_COUNT_ON_CHART):
            sns.set(font_scale=0.8)

            # Initialize the matplotlib figue
            f, ax = plt.subplots(figsize=(18, 10))

            sns.despine(left=True, bottom=True)
            ax.figure.axes[-1].yaxis.label.set_size(10)

            # title
            title = "Feature group {0} \nPart #{1}".format(self.dashboard_name, str(ind))
            plt.title(title, fontsize=12)
            ttl = ax.title
            ttl.set_position([0.5, 1.02])

            sns.heatmap(self.data.iloc[:, i:i + FEATURE_COUNT_ON_CHART], annot=True, linewidths=.2, ax=ax,
                        cmap='RdYlGn_r', vmin=1,
                        vmax=200,
                        fmt='1.0f', square=True, annot_kws={'size': 10, 'weight': 'normal', 'color': 'black'},
                        cbar_kws={"label": "Efforts (man-days)", "orientation": "vertical"})

            # labels
            plt.xlabel("Features")
            # plt.ylabel("Components")

            plt.savefig(self.png_dir + 'heatmap{0}_{1}.files'.format(self.dashboard_name, str(ind)),
                        bbox_inches='tight',
                        dpi=300)

            ind = ind + 1
            plt.clf()

        # plt.show()

    def export_to_plot(self):
        self.export_seaborn()

    def export_to_json(self):
        raise NotImplementedError('export_to_json')
