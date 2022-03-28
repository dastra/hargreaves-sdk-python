import json
import logging
import pathlib
from typing import List

import jinja2

from .requests import HttpRequestEntry

logger = logging.getLogger(__name__)


class HARHttpRequestEntryRenderer:

    def __init__(self):
        pass

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
        logger.debug(f'render HAR with template "{template.name}"')

        py = template.render(
            http_entries=http_entries
        )

        return py


class HAR2MarkdownRenderer:

    def __init__(self):
        pass

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
        logger.debug(f'render HAR with template "{template.name}"')

        output_txt = template.render(
            http_entries=http_entries
        )

        return output_txt
