"""Install docs."""

import os
import argparse
import shutil

from docknv.utils.prompt import prompt_yes_no
from docknv.logger import Logger

html_docs = os.path.join("_build", "html")

parser = argparse.ArgumentParser(description="install documentation to path")
parser.add_argument("output_path")

args = parser.parse_args()

if not os.path.exists(html_docs):
    Logger.error("you must build the HTML docs.")

if not os.path.exists(args.output_path):
    Logger.error("output path {0} does not exist.".format(args.output_path))
else:
    choice = prompt_yes_no(
        "/!\\ the folder {0} will be removed and recreated. "
        "are you sure you want to install?".format(args.output_path)
    )

    if choice:
        shutil.rmtree(args.output_path)
        shutil.copytree(html_docs, args.output_path)
