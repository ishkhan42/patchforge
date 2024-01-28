# PatchForge

A simple POC tool for diffing and backporting tool.

## Usage

1. Clone the repository:

2. Dependencies:

   If you have Pytohn 3.6+ installed, you should be good to go.

3. Run the project:

    `python backport.py --help`
    ```bash
    usage: backport.py [-h] [--log_file LOG_FILE] [--output OUTPUT] [--window WINDOW] [--ctx CTX] base_file patched_file target_file

    positional arguments:
    base_file            Base file
    patched_file         Patched file
    target_file          Target file

    options:
    -h, --help           show this help message and exit
    --log_file LOG_FILE  Hunk log file
    --output OUTPUT      Patched file name
    --window WINDOW      Offset window size for locating to apply hunks
    --ctx CTX            Edit script context size for finding shortest edit script

    ```
