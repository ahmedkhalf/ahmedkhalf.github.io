# SPDX-FileCopyrightText: 2023-present ahmedkhalf <ahmedkhalf567@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


CWD = Path.cwd().resolve()
TEMPLATE_FOLDER = CWD / "templates"
POSTS_FOLDER = CWD / "posts"
OUT_FOLDER = CWD / "out"


@dataclass
class Post:
    file: str


def main():
    # load template
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FOLDER),
        autoescape=select_autoescape()
    )
    main_template = env.get_template("main.html")

    # load posts
    posts: list[Post] = []
    for post_path in POSTS_FOLDER.glob("*.md"):
        posts.append(Post(file=post_path.name))

    # create an output directory if it does not exist
    OUT_FOLDER.mkdir(exist_ok=True)

    # render
    main_page = main_template.render(posts=posts)
    with open(OUT_FOLDER / "main.html", "w") as f:
        f.write(main_page)


if __name__ == "__main__":
    main()
