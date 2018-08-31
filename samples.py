import logging
from dashboard_controller import DashboardController

if __name__ == '__main__':
    # logging.basicConfig( level=logging.DEBUG, format='%(asctime)s %(message)s', filemode='w')
    # logging.config.fileConfig("logging.ini")

    logger = logging.getLogger()
    logger.info('*** STARTED ***')

    # dc = DataController()
    # issue = dc.get_issue('RDQC-89')
    # logging.info(issue)
    #
    c = DashboardController()
    # pd.options.display.max_columns = 5

    # data = c.initialize_cache()
    # data = c.update()
    ##data = c.dashboard_feature_progress()
    data = c.dashboard_feature_group_progress()

    # logging.info(data.head(2))
    # print(data[['key', 'project', 'components']])
    # logging.info(list(data.columns.values))

    # print(data)

    # print(data[['key', 'project', 'components', 'timeoriginalestimate', 'timespent', 'labels']])
    # , 'project', 'components', 'timeoriginalestimate', 'timespent'

    # [data['key'].str.contains("BSSBFAM-562")]
    # [['labels', 'key', 'timespent', 'assignee']]

    # logging.info(data[data['labels'].str.contains(pat="NewDevPlan")].groupby(['issuetype'])['issuetype'].count())

    ##logging.info(data[data['labels'].str.contains(pat="NewDevPlan")]['labels'])

    # logging.info(data[data['issuetype'].str.contains(pat="Improvement")]
    #              [data['labels'].str.contains(pat="SuperSprint4")][['key', 'epiclink']])

    # piv = data.pivot_table(index=['labels'], values=['project'], aggfunc='count')

    # .sort_values(by=('timespent'), ascending=False)

    # logging.info(piv)

    # piv.to_excel(sheet_name="Sheet1")
    # logging.info('(rows, cols) -> ' + str(piv.shape))

    # [data['project'].str.contains(pat="NWM")]
    # piv = data[data['labels'].str.contains(pat="DevPlan")].\
    #    pivot_table(index=['issuetype'], values=['epiclink'], aggfunc='sum')
    # .sort_values(by=('timespent'), ascending=False)

    ###piv.to_excel('foo.xlsx', sheet_name='Sheet1')
    # piv.to_csv('foo.csv')
    #
    # logging.info(piv)
    # p2 = piv['components'].apply(pd.Series)

    logging.info('*** FINISHED ***')
