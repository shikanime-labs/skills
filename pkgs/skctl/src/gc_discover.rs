/// GC discovery: dangling bookmarks (not trunk, no open PR) and skill
/// workspaces (<repo>.<unit> or <repo>-fix), with a dirty working-copy guard.
/// Dry-run only — never forgets or removes.
pub struct GcReport {
    pub dangling_bookmarks: Vec<String>,
    pub workspaces: Vec<Workspace>,
}

pub struct Workspace {
    pub name: String,
    pub path: String,
    pub clean: bool,
}

pub fn discover(repo_dir: &str) -> Result<GcReport, String> {
    if !std::path::Path::new(repo_dir).join(".jj").is_dir() {
        return Err(format!("{repo_dir} has no .jj/ — run from a jj repo root."));
    }

    let trunk: Vec<&str> = vec!["main", "trunk", "master"];

    let open_prs = crate::cmd::run_in(
        repo_dir,
        "gh",
        &[
            "pr",
            "list",
            "--state",
            "open",
            "--limit",
            "200",
            "--json",
            "headRefName",
            "--jq",
            ".[].headRefName",
        ],
    )?;
    let open_prs: Vec<&str> = open_prs.lines().map(str::trim).collect();

    let bm_out = crate::cmd::run_in(
        repo_dir,
        "jj",
        &[
            "bookmark",
            "list",
            "-r",
            "bookmarks() & ~::trunk()",
            "--color",
            "never",
            "-T",
            "name ++ \"\\n\"",
        ],
    )?;
    let mut dangling: Vec<String> = Vec::new();
    let mut seen: Vec<String> = Vec::new();
    for bm in bm_out.lines().map(str::trim) {
        if bm.is_empty() || seen.contains(&bm.to_string()) {
            continue;
        }
        seen.push(bm.to_string());
        if trunk.contains(&bm) || open_prs.contains(&bm) {
            continue;
        }
        dangling.push(bm.to_string());
    }
    dangling.sort();

    let repo_name = std::path::Path::new(repo_dir)
        .file_name()
        .map(|s| s.to_string_lossy().into_owned())
        .unwrap_or_default();

    let ws_out = crate::cmd::run_in(
        repo_dir,
        "jj",
        &[
            "workspace",
            "list",
            "--color",
            "never",
            "-T",
            "name ++ \"\\t\" ++ root ++ \"\\n\"",
        ],
    )?;
    let mut workspaces = Vec::new();
    for line in ws_out.lines() {
        let mut it = line.splitn(2, '\t');
        let (name, path) = match (it.next(), it.next()) {
            (Some(n), Some(p)) => (n.trim(), p.trim()),
            _ => continue,
        };
        let is_skill_ws =
            name.starts_with(&format!("{repo_name}.")) || name == format!("{repo_name}-fix");
        if !is_skill_ws {
            continue;
        }
        let status =
            crate::cmd::run_in(path, "jj", &["status", "--color", "never"]).unwrap_or_default();
        let clean = status.contains("has no changes");
        workspaces.push(Workspace {
            name: name.to_string(),
            path: path.to_string(),
            clean,
        });
    }

    Ok(GcReport {
        dangling_bookmarks: dangling,
        workspaces,
    })
}
