import logging

AGE_FORMAT = "{0:%Y-%m-%d %H:%m}"


class AbstractQueryBuilder():

    def build(self, type):
        query_str = self.get_query_str(type)
        if query_str is None:
            query_str = ''
        return query_str

    def get_query_str(self, x):
        return None

    def build_bss_box(self):
        query_str = self.build('CRM') + ' or ' + self.build('ORDERING') + ' or ' + self.build(
            'PRM') + ' or ' + self.build('BILLING') + ' or ' + self.build('DFE') + ' or ' + self.build(
            'NWM') + ' or ' + self.build('INFRA') + ' or ' + self.build('PSC') + ' or ' + self.build(
            'QC') + ' or ' + self.build('ARCH') + ' or ' + self.build('BA') + ' or ' + self.build('DOC')

        logging.debug(query_str)
        return query_str

    def build_updated_bss_box(self, age):
        query_str = self.build_bss_box()

        if age is None:
            raise ValueError('age is None')

        age_str = AGE_FORMAT.format(age)
        # Valid formats include: 'yyyy/MM/dd HH:mm', 'yyyy-MM-dd HH:mm', 'yyyy/MM/dd', 'yyyy-MM-dd', or a period format e.g. '-5d', '4w 2d'

        query_str = '(' + query_str + ') and updatedDate >= "' + age_str + '"'

        logging.debug(query_str)
        return query_str
