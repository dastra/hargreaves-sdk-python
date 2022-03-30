import argparse
import logging
from pathlib import Path

from requests_tracker.renderers import HAR2MarkdownRenderer

"""
Use this script to convert a browser pre-recorded HAR log file into a MD (markdown) file when analysing a certain
customer journey.
More details here: https://github.com/eladeon/requests-tracker-python/blob/main/README.md
"""

# default URL patterns to exclude to filter the "noise" - specific to the Hargreaves Lansdown website
DEFAULT_EXCLUDE_PATTERNS = '.js,googleads,facebook,youtube,chartbeat,.jpg,.ico,.css,bing.com,fonts,twitter,' \
                           'google.com,google.co.uk,.svg,appdynamics.com,.gif,.png,.omtrdc.net,demdex.net,' \
                           'cm.everesttech.net,fundslibrary.co.uk,t.co,www.googletagmanager.com,ytimg.com,' \
                           'ajax/menus,lightstreamer,loginstatus,cms_services.php'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'input',
        action='store',
        help='har input file',
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

    args = parser.parse_args()

    input_file_path = Path(args.input)

    # by default this markdown file will be created under the 'session_cache' sub-folder
    output_folder_path = Path.joinpath(Path(__file__).parent.parent.parent, 'session_cache', input_file_path.stem) \
        if args.output is None else args.output

    # configure logger
    logger = logging.getLogger()
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)

    exclude_pattern_csv = DEFAULT_EXCLUDE_PATTERNS.split(',')
    renderer = HAR2MarkdownRenderer()

    renderer.exec(
        input_file=str(input_file_path),
        output_folder=output_folder_path,
        exclude_patterns=exclude_pattern_csv)
