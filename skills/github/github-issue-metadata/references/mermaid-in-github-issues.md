# Mermaid in GitHub Issues

GitHub renders Mermaid natively in Issues, PRs, Discussions, wikis, and `.md`
files (since 2022-02-14). No plugins, no static images — just a ` ```mermaid `
fenced block.

## Authoritative sources
- GitHub Docs — Creating diagrams: https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams
- Mermaid live editor: https://mermaid.live/edit
- Community example gist (ChristopherA): https://gist.github.com/ChristopherA/bffddfdf7b1502215e44cec9fb766dfd

## Diagram types that fit issues
- `flowchart` — logic / control flow / component interaction. Real example (triage):
  ```mermaid
  flowchart TD
      A(Coffee machine <br>not working) --> B{Machine has power?}
      B -->|No| H(Plug in and turn on)
      B -->|Yes| C{Out of beans or water?} -->|Yes| G(Refill beans and water)
  ```
- `sequenceDiagram` — request/response, multi-actor flows.
- `gitGraph` — branch/merge, parent-child relationship visuals:
  ```mermaid
  gitGraph
      commit
      branch develop
      checkout develop
      commit
      checkout main
      merge develop
  ```

## GitHub engine limitations (verified)
- Emoji (😀) and some extended-ASCII chars (†, ¶) break rendering. `²` is
  oddly fine. Use HTML entities (`&dagger;`) if unavoidable.
- `<br>` works in labels; markdown (`*italic*`) and mathjax do not render in
  labels but don't break it.
- `click` / hyperlinks / tooltips do NOT work on GitHub — describe links as
  plain text.
- Quote labels with `()` / `[]` / special chars: `A["Text (note)"]`.
- `fa:fa-ban` style icons and some Mermaid symbols are unsupported.
