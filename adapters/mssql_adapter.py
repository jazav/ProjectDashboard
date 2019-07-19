import pyodbc
import os


class MssqlAdapter:
    @staticmethod
    def get_issues_mssql(mssql_query_file):
        mssql_database = pyodbc.connect("Driver={ODBC Driver 13 for SQL Server};"
                                        "Server=SRV-SQL-MIRROR\\JIRAREPORT;"
                                        "Database=srv-jira-prod-report;"
                                        "uid=rndview;pwd=V2f6A8Uf")

        path = os.path.abspath('./SQL_queries/{}.txt'.format(mssql_query_file))
        with open(path, 'r') as query:
            sql_str = query.read()
            cursor = mssql_database.cursor()
            cursor.execute(sql_str)

        data = {}
        for column in cursor.description:
            data[column[0]] = []
        for row in cursor:
            for el, key in zip(row, data.keys()):
                data[key].append(el)
        return data
