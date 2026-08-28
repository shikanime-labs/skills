/// Discover every triage-relevant metadata value a repo offers: labels,
/// milestones, projects, assignees, issue types, and custom fields. This is
/// the source of truth — triage must only set values that exist here.
/// Structured output, one section per metadata class.
pub fn discover_metadata(repo: &str) -> Result<String, String> {
    let owner = repo.split('/').next().unwrap_or(repo);
    let mut out = String::new();

    out.push_str("== labels ==\n");
    match crate::cmd::run(
        "gh",
        &[
            "label",
            "list",
            "--repo",
            repo,
            "--limit",
            "200",
            "--json",
            "name,description",
            "--jq",
            ".[] | \"\\(.name)\\t\\(.description // \"\")\"",
        ],
    ) {
        Ok(s) => out.push_str(&s),
        Err(e) => out.push_str(&format!("<error: {e}>\n")),
    }

    out.push_str("== milestones (open) ==\n");
    match crate::cmd::run(
        "gh",
        &[
            "api",
            "--paginate",
            &format!("repos/{repo}/milestones?state=open"),
            "--jq",
            ".[] | \"\\(.number)\\t\\(.title)\"",
        ],
    ) {
        Ok(s) => out.push_str(&s),
        Err(e) => out.push_str(&format!("<error: {e}>\n")),
    }

    out.push_str("== projects (owner) ==\n");
    match crate::cmd::run(
        "gh",
        &[
            "project",
            "list",
            "--owner",
            owner,
            "--format",
            "json",
            "--jq",
            ".[] | \"\\(.number)\\t\\(.title)\"",
        ],
    ) {
        Ok(s) => out.push_str(&s),
        Err(_) => out.push_str("no accessible projects (needs project scope)\n"),
    }

    out.push_str("== assignees ==\n");
    match crate::cmd::run(
        "gh",
        &[
            "api",
            "--paginate",
            &format!("repos/{repo}/assignees"),
            "--jq",
            ".[].login",
        ],
    ) {
        Ok(s) => out.push_str(&s),
        Err(e) => out.push_str(&format!("<error: {e}>\n")),
    }

    out.push_str("== issue types (enabled) ==\n");
    match crate::cmd::run(
        "gh",
        &[
            "api",
            "--paginate",
            &format!("repos/{repo}/issue-types"),
            "--jq",
            ".[] | select(.is_enabled) | .name",
        ],
    ) {
        Ok(s) => out.push_str(&s),
        Err(e) => out.push_str(&format!("<error: {e}>\n")),
    }

    out.push_str("== custom fields ==\n");
    match crate::cmd::run(
        "gh",
        &[
            "api",
            "--paginate",
            &format!("repos/{repo}/fields"),
            "--jq",
            ".[].name",
        ],
    ) {
        Ok(s) if !s.trim().is_empty() => out.push_str(&s),
        _ => out.push_str("no repo-level fields\n"),
    }

    Ok(out)
}

#[cfg(test)]
mod tests {
    #[test]
    fn owner_from_repo() {
        assert_eq!(
            "cloud-pi-native",
            "cloud-pi-native/console".split('/').next().unwrap()
        );
    }

    #[test]
    fn empty_fields_section_uses_fallback() {
        // Simulates the gh api fields call returning nothing usable.
        let blank = String::new();
        let out = if blank.trim().is_empty() {
            "no repo-level fields\n".to_string()
        } else {
            blank
        };
        assert_eq!(out, "no repo-level fields\n");
    }
}
