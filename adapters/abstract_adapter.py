class AbstractAdapter:
    """Common class for all issue adapters. Do not use to implement objects."""

    def get_builder(self):
        raise NotImplementedError()
        return None

    def load_by_query(self, query_str, expand, url):
        raise NotImplementedError()
        return None

    def load_by_key(self, key, expand, url):
        raise NotImplementedError()
        return None

    def load_all(self, query, expand, url, jira_name):
        """Loading all issues by batch query"""
        if query is None:
            builder = self.get_builder()
            query_str = builder.build_bss_box(jira_name)
        else:
            query_str = query

        return self.load_by_query(query_str=query_str, expand=expand, url=url)

    def load_updated(self, query, age, expand, url, jira_name):
        """Loading all issues by batch query"""
        if query is None:
            builder = self.get_builder()
            query_str = builder.build_updated_bss_box(age, jira_name)
        else:
            query_str = query

        return self.load_by_query(query_str, expand, url=url)

    def save_all(self, data):
        raise NotImplementedError()

    def create_issue(self, issues):
        raise NotImplementedError()
        return None
