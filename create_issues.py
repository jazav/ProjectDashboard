import openpyxl
import pandas as pnd

EXCEL_NAME = 'Copy of Backlog BOX v1(006) (002).xlsx'
# 'Test_newPlan.xlsx'
# Copy of Backlog BOX v1(006) (002).xlsx'
EXCEL_PATH = '../excel/'


def get_start(sheet):
    # for i in range(0, 100, 1):
    #     if sheet[1][i].value == 'Estimation':
    #         start_col = i
    start_col = 37
    return start_col


def get_project_list(sheet, project_row, start_col):
    projects = list()
    capacities = dict()

    # capacities = dict({'project':'capacity'})

    for cell in sheet[project_row]:
        if cell.col_idx >= start_col:
            if cell.value is not None:
                prj = list([cell.value, sheet[cell.row + 1][cell.col_idx - 1].value, cell.col_idx])

                capacity = sheet[cell.row - 5][cell.col_idx - 1].value
                if capacity is not None and capacity > 0:
                    capacities[prj[0]] = round(float(sheet[cell.row - 5][cell.col_idx - 1].value), 0)

                projects.append(prj)
                if prj[0] == 'RMSDOC':
                    break
            else:
                if len(projects) > 0:
                    break
    print('components: ' + str(len(projects)))
    return projects, capacities


def get_issues(sheet, items):
    jira_issues = []
    pandas_issues = []

    for item in items:
        # print('*** ' + str(item[0]) + ' - '+ str(item[1]) + ' ***')

        project = item[0]
        component = item[1]
        column = item[2]
        start_item_row = 10

        for row in range(start_item_row, 10000, 1):

            f_group = sheet[row][4].value

            if f_group == None:
                break

            epic_name = sheet[row][5].value

            if epic_name == None:
                epic_name = ''
            # print(str(sheet[row][0].value) + ' - ' + f_group + ' - ' + epic_name)

            descr = sheet[row][10].value
            if descr == None:
                descr = ''

            estimate = sheet[row][column - 1].value
            if estimate == None or estimate == 0 or estimate == '':
                continue

            if estimate == '?':
                est_str = None
            else:
                est_str = str(estimate)

            if project == 'RNDDOC':
                issuetype = 'Documentation'
            else:
                issuetype = 'Epic'

            priority = sheet[row][7].value

            label1 = f_group
            label2 = 'NewDevplan'
            label3 = 'AutoCreated'

            num_str = str(sheet[row][1].value).zfill(2) + '.' + str(sheet[row][2].value).zfill(2)
            label4 = 'num' + num_str

            label5 = None

            stage = sheet[row][8].value
            if stage == 1 or stage == '1?':
                label5 = 'alpha'
            if stage == 2 or stage == '2?':
                label5 = 'MVP'
            if stage == 3 or stage == '3?':
                label5 = 'Release2'
            if stage == '?':
                label5 == 'Release2'

            srs = sheet[row][9].value

            if srs is None:
                srs = '?'
            else:
                if srs.lower() in ('да', 'yes', 'y'):
                    srs = 'Y'
                if srs.lower() in ('нет', 'no', 'n'):
                    srs = 'N'

            jira_issue = {
                'project': {'key': project},
                'summary': epic_name,
                'description': descr,
                'issuetype': {'name': issuetype},
                'components': [{'name': component}],
                'customfield_10204': epic_name,
                'customfield_11100': [label1, label2, label3, label4]
            }

            pandas_issue = {
                'num': num_str,
                'project': project,
                'component': component,
                'group': f_group,
                'epic': epic_name,
                'stage': stage,
                'srs': srs,
                'summary': epic_name,
                'description': descr,
                'priority': priority
            }

            if label5 is not None:
                jira_issue['customfield_11100'].append(label5)

            if est_str is not None:
                jira_issue['timetracking'] = {
                    "originalEstimate": est_str + 'd'}
                try:
                    if est_str != '':
                        pandas_issue['estimate'] = float(est_str)
                    else:
                        pandas_issue['estimate'] = float(0.00)
                except:
                    print(
                        'estimate error: row:' + str(row) + ' - ' + ' - ' + project + ' - ' + component + ' - ' +
                        sheet[row][
                            column - 1].value)

            jira_issues.append(jira_issue)
            pandas_issues.append(pandas_issue)

            # if row > 11:
            #     break
    return jira_issues, pandas_issues


def load_file():
    wb = openpyxl.load_workbook(filename=EXCEL_PATH + EXCEL_NAME, data_only=True)

    # try:
    sheet = wb['Sheet1']
    #     sheet = wb['Лист1']
    # except:
    #     sheet = wb['Sheet1']

    start_col = get_start(sheet)

    items, capacities = get_project_list(sheet, project_row=8, start_col=start_col)
    jira_issues, pandas_issues = get_issues(sheet=sheet, items=items)

    return jira_issues, pandas_issues, capacities


if __name__ == '__main__':
    # logging.basicConfig(filename='devplan.log', level=logging.DEBUG, format='%(asctime)s %(message)s', filemode='w')

    jira_issues, pandas_issues, capacities = load_file()
    df = pnd.DataFrame(pandas_issues)
    cap = pnd.Series(capacities)
    df.to_csv('new_devplan.csv')
    cap.to_csv('capacities.csv')

    df = pnd.read_csv('new_devplan.csv')
    cap = pnd.read_csv('capacities.csv', names=['project', 'capacity'])

    prj_piv = df.pivot_table(index='project', values=['estimate'], aggfunc='sum').sort_values(by=('estimate'),
                                                                                              ascending=False)

    epic_piv = df[df['estimate'] > 99.99].pivot_table(index=['epic', 'project'], values=['estimate'], aggfunc='sum')
    # .sort_values(by=(['estimate']), ascending=False)

    srs_piv = df.pivot_table(index='srs', values=['estimate', 'epic'], aggfunc={'estimate': [sum], 'epic': ['count']})
    priority_piv = df.pivot_table(index='priority', values=['estimate', 'epic'],
                                  aggfunc={'estimate': [sum], 'epic': ['count']})

    writer = pnd.ExcelWriter('excel_new_devplan.xlsx', engine='openpyxl')
    try:
        df.to_excel(writer, sheet_name='Data', index=False)
        cap.to_excel(writer, sheet_name='Capacity', index=False)
        prj_piv.to_excel(writer, sheet_name='prj_pivot')
        epic_piv.to_excel(writer, sheet_name='featue_pivot > 99')
        srs_piv.to_excel(writer, sheet_name='srs_pivot')
        priority_piv.to_excel(writer, sheet_name='priority_piv')
        writer.save()
    except:
        writer.close()

    #
    # piv = df.pivot_table(index=['component', 'epic'],  values=['estimate'], aggfunc='sum').sort_values(by=('estimate'), ascending=False)
    # print(piv)

    # issue_list = [
    #     {
    #         'project': {'key': 'BSSARBA'},
    #         'summary': 'summary2',
    #         'description': 'Description1',
    #         'issuetype': {'name': 'Epic'},
    #         'components': [{'name': 'Analytics'}],
    #         'customfield_10204': 'Epic name',
    #         'customfield_11100': ['Label1, Label2', 'AUTO'],
    #         'timetracking': {
    #             "originalEstimate": "1d"
    #         },
    #     },
    #     {
    #         'project': {'id': 20607},
    #         'summary': 'summary3',
    #         'description': 'Description1',
    #         'issuetype': {'name': 'Epic'},
    #         'components': [{'name': 'Analytics'}],
    #         'customfield_10204': 'Epic',
    #         'customfield_11100': ['Label1, Label2'],
    #         'timetracking': {
    #             "originalEstimate": "5.1d"
    #         }
    #
    #     },
    # ]

    ##issues = dc.create_issues(issue_list)

    # issue = dc.get_issue(key='BSSARBA-1268')
    # issue.update(timetracking= {"originalEstimate": "1d 2h"})

    # print(issues)
