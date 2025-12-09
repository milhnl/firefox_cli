# firefox_cli

Manage your firefox with the terminal.

Firefox manages to be power user hostile. This small tool tries to fix that. So
if you want to deploy firefox in your enterprise and want to set the default
search engine, or want to list the history of open tabs? `firefox_cli` has your
back.

### Installation

If you put your binaries in `~/.local/bin`:

    PREFIX="$HOME/.local" make install

If you can't figure this out and want to use this tool anyway, message me.

### Usage

    firefox_cli [-P PROFILE] <COMMAND...>

### Flags

- `-P <PROFILE>`: `string`. Profile name. If no profile is passed it tries to
  use the default one.

### Commands

- `extract <FILE>`: Some files in the profile are compressed with LZ4. Pass the
  relative path. You can use this one to get the currently open tabs with

    ```sh
    firefox_cli extract sessionstore-backups/recovery.jsonlz4
    ```

- `compress <FILE>`: The reverse operation.
- `get_path [FILE]`: Get the path to the profile or a file in the profile.
- `remove_profile`: Removes a profile
