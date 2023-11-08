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

    firefox_cli [-P PROFILE] extract FILE

Extracts the LZ4 compressed (json) file in your profile (pass the name with
`-P`, otherwise it tries to find a `.default-release` profile) to stdout.
