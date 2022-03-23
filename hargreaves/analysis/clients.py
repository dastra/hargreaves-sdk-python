import json
import pathlib
from typing import List

import jinja2
from logging import Logger

from hargreaves.web.session import HttpRequestEntry


class HARHttpRequestEntryRenderer:
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    def safe_text_filter(self, txt_input: str):
        """Custom filter"""
        return json.dumps(txt_input, ensure_ascii=False)

    def rendering(
            self,
            http_entries: List[HttpRequestEntry],
            template_dir: str = pathlib.Path(__file__).parent,
            template_name: str = 'har.jinja2',
    ):
        """Generate HTTP Archive (HAR) using jinja2 template.
        :param template_dir:
        :param http_entries:
        :param template_name:
        """
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
        env.filters['safe_text'] = self.safe_text_filter
        template = env.get_template(template_name)
        self._logger.debug(f'render HAR with template "{template.name}"')

        py = template.render(
            http_entries=http_entries
        )

        return py


class HAR2MarkdownRenderer:
    _logger: Logger

    def __init__(self, logger: Logger):
        self._logger = logger

    def safe_text_filter(self, txt_input: str):
        """Custom filter"""
        return json.dumps(txt_input, ensure_ascii=False)

    def rendering(
            self,
            http_entries: list,
            template_dir: str = pathlib.Path(__file__).parent,
            template_name: str = 'md.jinja2'
    ):
        """Generate HTTP Archive (HAR) using jinja2 template.
        :param template_dir:
        :param http_entries:
        :param template_name:
        """
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
        env.filters['safe_text'] = self.safe_text_filter
        template = env.get_template(template_name)
        self._logger.debug(f'render HAR with template "{template.name}"')

        output_txt = template.render(
            http_entries=http_entries
        )

        return output_txt
