from news_ebook.lib.news_source import Issue


class Output:
    def get_output_path(self, issue: Issue) -> str:
        raise NotImplementedError()
