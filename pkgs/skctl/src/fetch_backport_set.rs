use std::io::Write;

/// Fetch the ordered (oldest->newest) merge-commit SHAs of a milestone's
/// merged PRs. The milestone is the authoritative backport set — NOT a
/// BASE_TAG..main diff. Phase 1 gets PR numbers via the issues endpoint
/// (honors the milestone filter), phase 2 gets merge_commit_sha per PR via
/// the pulls endpoint (only it returns it).
pub fn fetch_backport_set(repo: &str, mile_num: u32, outfile: &str) -> Result<Vec<String>, String> {
    let issues = crate::cmd::run(
        "gh",
        &[
            "api",
            "--paginate",
            &format!("repos/{repo}/issues?milestone={mile_num}&state=closed&per_page=100"),
            "--jq",
            ".[] | select(.pull_request and .pull_request.merged_at != null) | \"\\(.pull_request.merged_at) \\(.number)\"",
        ],
    )?;

    let mut entries: Vec<(String, String)> = issues
        .lines()
        .filter_map(|l| {
            let mut it = l.splitn(2, ' ');
            match (it.next(), it.next()) {
                (Some(ts), Some(num)) => Some((ts.to_string(), num.to_string())),
                _ => None,
            }
        })
        .collect();
    entries.sort_by(|a, b| a.0.cmp(&b.0));

    let mut shas = Vec::new();
    for (_, num) in &entries {
        let sha = crate::cmd::run(
            "gh",
            &[
                "api",
                &format!("repos/{repo}/pulls/{num}"),
                "--jq",
                ".merge_commit_sha",
            ],
        )?;
        shas.push(sha.trim().to_string());
    }

    if !outfile.is_empty() {
        let mut f =
            std::fs::File::create(outfile).map_err(|e| format!("cannot write {outfile}: {e}"))?;
        for sha in &shas {
            writeln!(f, "{sha}").map_err(|e| format!("cannot write {outfile}: {e}"))?;
        }
    }
    Ok(shas)
}
