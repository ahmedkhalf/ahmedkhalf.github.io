# SPDX-FileCopyrightText: 2023-present ahmedkhalf <ahmedkhalf567@gmail.com>
#
# SPDX-License-Identifier: MIT

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


CWD = Path.cwd().resolve()
TEMPLATE_FOLDER = CWD / "templates"
OUT_FOLDER = CWD / "out"


def main():
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FOLDER),
        autoescape=select_autoescape()
    )

    main_template = env.get_template("main.html")

    # create an output directory if it does not exist
    OUT_FOLDER.mkdir(exist_ok=True)

    main_page = main_template.render()
    with open(OUT_FOLDER / "main.html", "w") as f:
        f.write(main_page)


if __name__ == "__main__":
    main()
