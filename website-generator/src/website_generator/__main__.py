# SPDX-FileCopyrightText: 2023-present ahmedkhalf <ahmedkhalf567@gmail.com>
#
# SPDX-License-Identifier: MIT

import argparse
from dataclasses import dataclass
from datetime import date
from datetime import datetime
import os
from pathlib import Path
import shutil
import time

import frontmatter
import mistune
from jinja2 import Environment, FileSystemLoader, select_autoescape
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


CWD = Path.cwd().resolve()
TEMPLATE_FOLDER = CWD / "templates"
POSTS_FOLDER = CWD / "posts"
PUBLIC_FOLDER = CWD / "public"
OUT_FOLDER = CWD / "out"


@dataclass
class Post:
    file: str
    title: str
    date_published: date
    content: str
    href: str


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
    env.filters["date"] = date_filter
    main_template = env.get_template("main.html")
    post_template = env.get_template("post.html")

    # load posts
    posts: list[Post] = []
    for post_path in POSTS_FOLDER.glob("*.md"):
        with open(post_path) as f:
            post = frontmatter.load(f)
            post_file = str(Path(post_path).relative_to(POSTS_FOLDER).with_suffix('').as_posix())
            post_title = post["title"]
            post_date_pusblished = post["date-published"]
            post_content = str(mistune.html(post.content))
            posts.append(Post(
                file=f"posts/{post_file}/index.html",
                title=post_title,
                date_published=post_date_pusblished,
                content=post_content,
                href=f"/posts/{post_file}"
            ))
    
    posts.sort(key=lambda post: (post.date_published, post.file), reverse=True)

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
    main_page = main_template.render(posts=posts, commit_hash=commit_hash)
    with open(OUT_FOLDER / "index.html", "w") as f:
        f.write(main_page)

    for post in posts:
        post_page = post_template.render(post=post, commit_hash=commit_hash)
        output_file = OUT_FOLDER / f"{post.file}"
        output_file.resolve().parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(post_page)


class MyHandler(FileSystemEventHandler):
    def __init__(self, commit_hash: str) -> None:
        super().__init__()
        self.commit_hash = commit_hash

    def on_any_event(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(".pyc"):
            print(f'{datetime.now()} :: {Path(event.src_path).relative_to(CWD)} :: Compiling website..')
            main(self.commit_hash)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="website-generator")
    parser.add_argument('--dev', action="store_true", help="Run continuously and watch for changes")
    parser.add_argument('--hash', type=str, default="na", help="Hash of the commit being built")
    args = parser.parse_args()

    commit_hash = args.hash
    if args.dev == True:
        commit_hash = "DevMode"

    main(commit_hash)

    if args.dev == False:
        exit(0)

    # Watch for changes in the template and post folders
    event_handler = MyHandler(commit_hash)
    observer = Observer()
    observer.schedule(event_handler, str(TEMPLATE_FOLDER), recursive=True)
    observer.schedule(event_handler, str(POSTS_FOLDER), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
