/// Find the milestone number for a title on REPO (OWNER/REPO), or None when
/// the milestone is absent or closed.
pub fn milestone_number(repo: &str, title: &str) -> Result<Option<u32>, String> {
    let out = crate::cmd::run(
        "gh",
        &[
            "api",
            "--paginate",
            &format!("repos/{repo}/milestones?state=open"),
            "--jq",
            ".[] | \"\\(.number)\\t\\(.title)\"",
        ],
    )?;
    for line in out.lines() {
        let mut it = line.splitn(2, '\t');
        let (num, t) = match (it.next(), it.next()) {
            (Some(n), Some(t)) => (n, t),
            _ => continue,
        };
        if t == title {
            return num
                .parse::<u32>()
                .map(Some)
                .map_err(|_| format!("milestone number '{num}' is not numeric"));
        }
    }
    Ok(None)
}
