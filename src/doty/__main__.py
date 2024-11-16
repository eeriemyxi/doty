import argparse
import os
import pathlib
import re
import sqlite3
import subprocess
import sys
import uuid

PAGE_RE = re.compile(r"debug: .+: Emitting signal for page (?P<page>\d+)")
ZATHURA_EXE = "zathura"
ZATHURA_FLAGS = ("-l", "debug")
FZF_EXE = "fzf"
SCRIPT_DIR = pathlib.Path(__file__).parent


def get_sql_file_path():
    match sys.platform:
        case "linux":
            config_path = pathlib.Path(os.environ["HOME"]) / ".config/doty"
            if not config_path.exists():
                raise FileNotFoundError(f"Config dir not available at {config_path}.")
            return config_path / "db.sql"


def add_book(args, cur, conn):
    res = cur.execute("INSERT INTO books(path) VALUES(?)", [str(args.file.resolve())])
    if not res:
        print(f"ERROR: couldn't add '{args.file}' to the database. (hint: maybe it's already in there.)", file=sys.stderr)
        exit(1)
    conn.commit()
    print(f"Successfully added {args.file} to the database.")


def rem_book(args, cur, conn):
    res = cur.execute("SELECT path FROM books")

    paths_r = res.fetchall()
    paths = [x[0] for x in paths_r]

    file_index = fzf_search(
        prompt="Remove a book: ",
        items=paths,
    )

    if file_index == -1:
        print("INFO: the action was cancelled.", file=sys.stderr)
        return

    file_path = paths[file_index]

    res = cur.execute("DELETE FROM books WHERE path=?", [file_path])
    conn.commit()

    print(f"Successfully removed {file_path} from the database.")


def open_book(args, cur, conn):
    res = cur.execute("SELECT path FROM books")

    paths_r = res.fetchall()
    paths = [x[0] for x in paths_r]

    file_index = fzf_search(
        prompt="Search a book: ",
        items=paths,
    )

    if file_index == -1:
        print("INFO: the action was cancelled.", file=sys.stderr)
        return

    file_path = paths[file_index]

    res = cur.execute("SELECT current_page FROM books where path=?", [file_path])
    page = res.fetchone()[0]

    result = subprocess.run(
        [ZATHURA_EXE, *ZATHURA_FLAGS, file_path, "--page", str(page)],
        capture_output=True,
    )
    res_stderr = result.stderr.decode()

    pages = PAGE_RE.findall(res_stderr)
    if not pages:
        return

    cur.execute("UPDATE books SET current_page=? WHERE path=?", [pages[-1], file_path])
    conn.commit()
    print(f"Updated current page to {pages[-1]}.")


def fzf_search(prompt, items) -> int:
    items_string = "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))
    tmp_file = pathlib.Path(f"/tmp/{uuid.uuid4()}.doty.txt")

    with open(tmp_file, "w") as file:
        res = subprocess.run(
            [FZF_EXE, "--prompt"],
            stdout=file,
            input=items_string,
            shell=True,
            text=True,
        )

    if res.returncode != 0:
        return -1

    with open(tmp_file) as file:
        file_str = file.read()
        return int(file_str[:file_str.index(".")]) - 1

    tmp_file.unlink()


parser = argparse.ArgumentParser(
    description="Doty - A simple ebook manager, dependent on Zathura."
)
parser.add_argument(
    "--reset-db",
    help="Reset book database. Caution: no backups are done.",
    action="store_true",
    default=False,
)
parser.set_defaults(func=open_book)

subparsers = parser.add_subparsers()

parser_add = subparsers.add_parser(
    "add",
    help=f"Add a book to the database.",
)
parser_add.add_argument("file", type=pathlib.Path)
parser_add.set_defaults(func=add_book)

parser_rem = subparsers.add_parser(
    "rem",
    help=f"Remove a book from the database.",
)
parser_rem.set_defaults(func=rem_book)

with open(SCRIPT_DIR/ "schema.sql") as file:
    SQL_SCRIPT = file.read()

SQLITE_FILE_PATH = get_sql_file_path()

args = parser.parse_args()

if args.reset_db:
    SQLITE_FILE_PATH.unlink()

db_con = sqlite3.connect(SQLITE_FILE_PATH)
db_con.cursor().executescript(SQL_SCRIPT)

args.func(args, db_con.cursor(), db_con)


def main():
    pass
