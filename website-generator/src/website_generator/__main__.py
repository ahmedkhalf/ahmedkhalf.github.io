# SPDX-FileCopyrightText: 2023-present ahmedkhalf <ahmedkhalf567@gmail.com>
#
# SPDX-License-Identifier: MIT

import argparse
from dataclasses import dataclass
from datetime import date
import datetime
import os
from pathlib import Path
import shutil
import time
from typing import Optional

import frontmatter
import mistune
from jinja2 import Environment, FileSystemLoader, select_autoescape


CWD = Path.cwd().resolve()
TEMPLATE_FOLDER = CWD / "templates"
PAGES_FOLDER = CWD / "pages"
POSTS_FOLDER = PAGES_FOLDER / "posts"
PUBLIC_FOLDER = CWD / "public"
OUT_FOLDER = CWD / "out"


@dataclass
class Page:
    file: str
    title: str
    content: str
    href: str
    date_published: Optional[date] = None


def date_filter(value: date):
    if value.day == 1:
        return f"{value:%B} {value.day}<sup>st</sup>, {value:%Y}"
    elif value.day == 2:
        return f"{value:%B} {value.day}<sup>nd</sup>, {value:%Y}"
    elif value.day == 3:
        return f"{value:%B} {value.day}<sup>rd</sup>, {value:%Y}"
    else:
        return f"{value:%B} {value.day}<sup>th</sup>, {value:%Y}"


def main(commit_hash: str):
    # load template
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_FOLDER),
        autoescape=select_autoescape()
    )
    env.globals["commit_hash"] = commit_hash
    env.filters["date"] = date_filter
    main_template = env.get_template("main.html")
    post_template = env.get_template("post.html")

    # load pages
    pages: list[Page] = []
    posts: list[Page] = []
    for page_path in PAGES_FOLDER.rglob("*.md"):
        with open(page_path) as f:
            page_file = str(Path(page_path).relative_to(PAGES_FOLDER).with_suffix('').as_posix())
            page_metadata = frontmatter.load(f)
            new_page = Page(
                file=f"{page_file}/index.html",
                title=page_metadata["title"],
                date_published=page_metadata.get("date-published"),
                content=str(mistune.html(page_metadata.content)),
                href=f"/{page_file}"
            )

            if Path(page_path).is_relative_to(POSTS_FOLDER):
                posts.append(new_page)
            pages.append(new_page)

    # empty the output directory or create it if it does not exist
    if OUT_FOLDER.exists():
        for entry in os.scandir(OUT_FOLDER):
            if entry.is_file():
                os.remove(entry.path)
            elif entry.is_dir():
                shutil.rmtree(entry.path)
    else:
        OUT_FOLDER.mkdir()

    # copy public folder to output folder
    if PUBLIC_FOLDER.exists():
        shutil.copytree(PUBLIC_FOLDER, OUT_FOLDER, dirs_exist_ok=True)

    # render
    posts.sort(key=lambda post: (post.date_published, post.file), reverse=True)
    main_page = main_template.render(posts=posts)
    with open(OUT_FOLDER / "index.html", "w") as f:
        f.write(main_page)

    for page in pages:
        page_html = post_template.render(post=page)
        output_file = OUT_FOLDER / f"{page.file}"
        output_file.resolve().parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(page_html)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="website-generator")
    parser.add_argument('--hash', type=str, default="na", help="Hash of the commit being built")
    args = parser.parse_args()

    start = time.perf_counter()
    main(args.hash)
    print(f"{datetime.datetime.now()} :: Built in {(time.perf_counter() - start) * 1000:.0f}ms")
