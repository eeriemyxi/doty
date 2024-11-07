# Doty
A simple ebook manager for Linux.

## Dependencies
- [`fzf`](https://github.com/junegunn/fzf)
- [`zathura`](https://github.com/pwmt/zathura)

## How to Install
> [!CAUTION]
> Doty only works on Linux.

> [!WARNING]
> Please first install the [dependencies](#dependencies).

### Method I
```
git clone --depth 1 --branch main <REPO URL> doty
pip install ./doty
```

### Method II
```
pip install git+<REPO URL>@main
```
## How to Use
Calling `doty` will open an `fzf` interface to select a book to open.

> [!TIP]
> Doty will detect the current page you are reading and save it for you (on exit).

Calling `doty add <file_path>` will add a file to the database.

Calling `doty rem` will open an `fzf` interface to remove a book from the database. The
actual files are of course unaffected.

## Command-Line Arguments
```
usage: doty [-h] [--reset-db] {add,rem} ...

Doty - A simple ebook manager, dependent on Zathura.

positional arguments:
  {add,rem}
    add       Add a book to the database.
    rem       Remove a book from the database.

options:
  -h, --help  show this help message and exit
  --reset-db  Reset book database. Caution: no backups are done.
```
