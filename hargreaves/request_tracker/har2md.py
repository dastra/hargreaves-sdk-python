import argparse
import json
import logging
import os
import shutil
from os import path
from pathlib import Path

from urllib3.util import parse_url

from .renderers import HAR2MarkdownRenderer
from hargreaves.utils.files import FileHelper
from hargreaves.utils.logging import LogHelper

DEFAULT_EXCLUDE = '.js,googleads,facebook,youtube,chartbeat,.jpg,.ico,.css,bing.com,fonts,twitter,google.com,' \
                  'google.co.uk,.svg,appdynamics.com,.gif,.png,.omtrdc.net,demdex.net,cm.everesttech.net,' \
                  'fundslibrary.co.uk,t.co,www.googletagmanager.com,ytimg.com,ajax/menus,lightstreamer,' \
                  'loginstatus,cms_services.php'

logger = logging.getLogger(__name__)


class Har2MdController:

    def load_entries(self, file_path: str):
        har_txt = FileHelper.read_file_contents(file_path)
        har_json = json.loads(har_txt)
        return har_json['log']['entries']

    def filter_entries(self, all_entries: list, exclude_patterns: list) -> list:
        filtered_entries = []
        if len(exclude_patterns) == 0:
            filtered_entries = all_entries
        else:
            for entry in all_entries:
                request_url = str(entry['request']['url'])
                if any(ext in request_url for ext in exclude_patterns):
                    continue
                filtered_entries.append(entry)
        return filtered_entries

    def prepare(self, http_entries: list):
        request_groups = {}

        for entry in http_entries:
            request_url = str(entry['request']['url'])
            entry['request']['clean_url'] = request_url.split('?')[0]
            parsed_url = parse_url(request_url)
            request_group = str(parsed_url.path)

            if request_group not in request_groups:
                request_groups[request_group] = 0

            request_groups[request_group] = request_groups[request_group] + 1
            request_id = f"{request_group}[{request_groups[request_group]}]"

            request_group_name_clean = str(parsed_url.path).replace('/', '_').replace('.', '_')
            content_file_name = f"{request_group_name_clean}_{request_groups[request_group]}.html"

            entry['request']['request_id'] = request_id
            entry['response']['content_file_name'] = content_file_name
            entry['response']['content_file_link'] = f"content/{content_file_name}"

    def create_content_files(self, content_folder: str, http_entries: list):
        for entry in http_entries:
            content_file_path = Path.joinpath(Path(content_folder), entry['response']['content_file_name'])
            response_content = entry['response']['content'].get('text')
            if response_content is not None:
                FileHelper.write_file(str(content_file_path), response_content)
            elif entry['response']['content'].get('size') > 0:
                logger.warning(f"response content is missing for '{content_file_path}'")

    def exec(self, input_file: str, output_folder: str, exclude_patterns: list):

        if not path.exists(input_file):
            raise Exception(f"Invalid Input File Path '{input_file}' ")

        content_folder = str(Path.joinpath(Path(output_folder), 'content'))

        if Path(output_folder).exists():
            logger.debug(f"Deleting folder ({output_folder}) ...")
            shutil.rmtree(output_folder)

        logger.debug(f"Creating folder ({output_folder} ...")
        os.makedirs(output_folder)

        logger.debug(f"Creating folder ({content_folder} ...")
        os.makedirs(content_folder)

        all_entries = self.load_entries(input_file)
        filtered_entries = self.filter_entries(all_entries, exclude_patterns)
        self.prepare(filtered_entries)

        logger.debug(f"Filtered {len(all_entries)} entries down to {len(filtered_entries)} ...")

        logger.debug(f"Creating content files ...")
        self.create_content_files(content_folder, filtered_entries)

        renderer = HAR2MarkdownRenderer()
        rendered_txt = renderer.rendering(http_entries=filtered_entries)

        md_output_file = Path.joinpath(Path(output_folder), 'output.md')
        FileHelper.write_file(str(md_output_file), rendered_txt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'input',
        action='store',
        help='har input file',
    )

    parser.add_argument(
        '-e',
        '--exclude',
        action='store',
        default=DEFAULT_EXCLUDE,
        type=str,
        help=(
            'CSV list of URL patterns to exclude'
        ),
    )

    parser.add_argument(
        '-o',
        '--output',
        action='store',
        default=None,
        type=str,
        help=(
            'output folder name'
        ),
    )

    parser.add_argument("--v", action="store_true",
                        help="Verbose (Log Level = DEBUG)")

    args = parser.parse_args()

    input_file_path = Path(args.input)

    exclude_pattern_csv = str(args.exclude).split(',')
    output_folder_path = Path.joinpath(input_file_path.parent, input_file_path.stem) \
        if args.output is None else args.output
    is_verbose = args.v

    LogHelper.configure(logging.DEBUG if is_verbose else logging.INFO)

    controller = Har2MdController()
    controller.exec(str(input_file_path), output_folder_path, exclude_pattern_csv)
