# Coming from Bash (Nushell)

Source: `book/coming_from_bash.html`. Direct command equivalents.

## File / shell ops

| Bash | Nu |
| --- | --- |
| `ls -la` | `ls --long --all` (or `ls -la`) |
| `ls -d */` | `ls \| where type == dir` |
| `find . -name *.rs` | `ls **/*.rs` |
| `find . -name M \| xargs vim` | `ls **/M \| get name \| vim ...$in` |
| `cat <path>` | `open --raw <path>` (or `open` for structured) |
| `cat <(c1) <(c2)` | `[(c1) (c2)] \| str join` |
| `> p` | `out> p` / `\| save p` |
| `>> p` | `out>> p` / `\| save --append p` |
| `> /dev/null` | `\| ignore` |
| `> /dev/null 2>&1` | `out+err>\| ignore` |
| `cmd 2>&1 \| less` | `cmd out+err>\| less` |
| `cmd1 \| tee log \| cmd2` | `cmd1 \| tee { save log.txt } \| cmd2` |
| `command \| head -5` | `command \| first 5` |
| `for f in *.md; do echo $f; done` | `ls *.md \| each { $in.name }` |
| `for i in $(seq 1 10); do ...` | `for i in 1..10 { print $i }` |
| `sed` | `str replace` |
| `grep pat` | `where $it =~ pat` or `find pat` |
| `man c` | `help c`; `help commands`; `help --find s` |
| `command1 && command2` | `command1; command2` |
| `bash -c "..."` | `nu -c "..."`; `bash f` => `nu f` |
| `\` (line cont.) | `( <command> )` |

## Env / vars

| Bash | Nu |
| --- | --- |
| `echo $PATH` | `$env.PATH` (or `$env.Path` on Win) |
| `echo $?` | `$env.LAST_EXIT_CODE` |
| `export PATH=$PATH:/x` | `$env.PATH = ($env.PATH \| append /x)` |
| `export FOO=BAR` | `$env.FOO = BAR` |
| `echo ${FOO:-fb}` | `$env.FOO? \| default "ABC"` |
| `unset FOO` | `hide-env FOO` |
| `alias s="git st -sb"` | `alias s = git status -sb` |
| `type FOO` | `which FOO` |
| `FOO=BAR ./bin` | `FOO=BAR ./bin` (same one-shot syntax) |
| `read var` | `let var = input`; `read -s` => `input -s` |
| `stat $(which git)` | `stat ...(which git).path` |
| `echo /tmp/$RANDOM` | `$"/tmp/(random int)"` |

## History / keybindings

- `!!`, `!$`, `!<n>`, `!<-n>`, `!<str>` history substitution (inserted, not auto-run — review first).
- `Ctrl/⌘+R` reverse search; `Ctrl/⌘+O` edit line in `$env.EDITOR` (inserted, not auto-run).
- Windows Git Bash externals (`ln`,`grep`,`vi`): add `$env.Path = ($env.Path | prepend 'C:\Program Files\Git\usr\bin')`.
