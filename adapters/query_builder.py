import logging

AGE_FORMAT = "{0:%Y-%m-%d %H:%m}"


class AbstractQueryBuilder():

    def build(self, type):
        query_str = self.get_query_str(type)
        if query_str is None:
            query_str = ''
        return query_str

    def build_all(self, jira_name):
        query_str =''
        if jira_name != '':
            query_str = self.get_all_queries(jira_name)
        if query_str is None:
            query_str = ''
        return query_str

    def get_query_str(self, x):
        return None

    def build_bss_box(self, jira_name):
        query_str = self.build_all(jira_name)

        logging.debug(query_str)
        return query_str

    def build_updated_bss_box(self, age, jira_name):
        query_str = self.build_bss_box(jira_name)

        if age is None:
            raise ValueError('age is None')

        age_str = AGE_FORMAT.format(age)
        # Valid formats include: 'yyyy/MM/dd HH:mm', 'yyyy-MM-dd HH:mm', 'yyyy/MM/dd', 'yyyy-MM-dd', or a period format e.g. '-5d', '4w 2d'

        query_str = '(' + query_str + ') and updatedDate >= "' + age_str + '"'

        logging.debug(query_str)
        return query_str
