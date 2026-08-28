/// Verify a rebuilt hotfix chain: exact commit count, zero conflict markers,
/// and a tree that reconstructs main's source (release-please files may
/// differ). Returns the list of failures; empty means clean.
pub fn verify_backport(base_tag: &str, tip: &str, expected: usize) -> Result<Vec<String>, String> {
    let range = format!("{base_tag}..{tip}");
    let mut failures = Vec::new();

    let count_out = crate::cmd::run(
        "jj",
        &["log", "-r", &range, "--no-graph", "-T", "commit_id"],
    )?;
    let count = count_out.lines().filter(|l| !l.trim().is_empty()).count();
    if count != expected {
        failures.push(format!(
            "FAIL: chain has {count} commits, expected {expected}"
        ));
    }

    let conflicts_out = crate::cmd::run(
        "jj",
        &[
            "log",
            "-r",
            &range,
            "--no-graph",
            "-T",
            "if(conflict, description.first_line(), \"\")",
        ],
    )?;
    let conflicts = conflicts_out
        .lines()
        .filter(|l| !l.trim().is_empty())
        .count();
    if conflicts != 0 {
        failures.push(format!("FAIL: {conflicts} conflict markers in {range}"));
    }

    let diff_out = crate::cmd::run("git", &["diff", "--name-only", tip, "main"])?;
    let stray: Vec<&str> = diff_out
        .lines()
        .filter(|l| !l.trim().is_empty())
        .filter(|l| {
            !l.starts_with("package.json")
                && !l.starts_with("CHANGELOG.md")
                && !l.starts_with(".release-please-manifest.json")
        })
        .collect();
    if !stray.is_empty() {
        failures.push(format!("FAIL: tree differs from main: {}", stray.join(" ")));
    }

    Ok(failures)
}

#[cfg(test)]
mod tests {
    #[test]
    fn filters_release_please_files() {
        let lines = [
            "package.json",
            "CHANGELOG.md",
            ".release-please-manifest.json",
            "src/main.rs",
        ];
        let stray: Vec<&str> = lines
            .iter()
            .copied()
            .filter(|l| {
                !l.starts_with("package.json")
                    && !l.starts_with("CHANGELOG.md")
                    && !l.starts_with(".release-please-manifest.json")
            })
            .collect();
        assert_eq!(stray, vec!["src/main.rs"]);
    }

    #[test]
    fn counts_non_empty_lines() {
        let out = "abc\n\ndef\n\n\n";
        let n = out.lines().filter(|l| !l.trim().is_empty()).count();
        assert_eq!(n, 2);
    }
}
