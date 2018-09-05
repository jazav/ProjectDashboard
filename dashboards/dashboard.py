import config_controller as cc


class AbstractDashboard():
    data = None
    colors = None
    png_dir = './files/'
    dashboard_name = None
    filter_list = None

    items_on_chart = 0
    #if we have tail less then its param the system adds their to the last chart
    min_item_tail = 4

    plan = None
    fact = None
    details = None

    def __init__(self):
        config = cc.ConfigController()
        self.png_dir = config.read_dashboards_config()[cc.FILE_DIR]

    def prepare(self, data):
        self.data = data
        raise NotImplementedError('prepare')
        return data

    def export_to_plot(self):
        raise NotImplementedError('export_to_plot')

    def export_to_json(self):
        raise NotImplementedError('export_to_json')
