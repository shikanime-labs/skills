/// Derive the next patch milestone from a base tag (v9.24.4 -> 9.24.5).
/// Pure derivation, no network.
pub fn next_milestone(base_tag: &str) -> Result<String, String> {
    let base = base_tag
        .strip_prefix('v')
        .ok_or_else(|| format!("'{base_tag}' is not a vMAJOR.MINOR.PATCH tag (e.g. v9.24.4)"))?;
    let parts: Vec<&str> = base.split('.').collect();
    if parts.len() != 3
        || parts
            .iter()
            .any(|p| p.is_empty() || !p.chars().all(|c| c.is_ascii_digit()))
    {
        return Err(format!(
            "'{base_tag}' is not a vMAJOR.MINOR.PATCH tag (e.g. v9.24.4)"
        ));
    }
    let patch: u64 = parts[2]
        .parse()
        .map_err(|_| format!("'{base_tag}' has a non-numeric patch"))?;
    let next = patch
        .checked_add(1)
        .ok_or_else(|| format!("'{base_tag}' patch overflows"))?;
    Ok(format!("{}.{}.{}", parts[0], parts[1], next))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bumps_patch() {
        assert_eq!(next_milestone("v9.24.4").unwrap(), "9.24.5");
    }

    #[test]
    fn handles_single_digit_components() {
        assert_eq!(next_milestone("v1.0.0").unwrap(), "1.0.1");
    }

    #[test]
    fn rejects_missing_v_prefix() {
        assert!(next_milestone("9.24.4").is_err());
    }

    #[test]
    fn rejects_four_part_versions() {
        assert!(next_milestone("v9.24.4.1").is_err());
    }

    #[test]
    fn rejects_non_numeric_components() {
        assert!(next_milestone("v9.24.x").is_err());
    }

    #[test]
    fn rejects_empty_input() {
        assert!(next_milestone("").is_err());
    }

    #[test]
    fn rejects_patch_overflow() {
        assert!(next_milestone("v1.0.18446744073709551615").is_err());
    }
}
