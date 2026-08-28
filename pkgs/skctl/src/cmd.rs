use std::process::{Command, Output};

pub fn run(bin: &str, args: &[&str]) -> Result<String, String> {
    let out: Output = Command::new(bin)
        .args(args)
        .output()
        .map_err(|e| format!("failed to run {bin}: {e}"))?;
    if !out.status.success() {
        let err = String::from_utf8_lossy(&out.stderr);
        let tail = err.lines().rev().take(3).collect::<Vec<_>>().join("\n");
        return Err(format!("{bin} exited {:?}: {tail}", out.status.code()));
    }
    Ok(String::from_utf8_lossy(&out.stdout).into_owned())
}

/// Run a command from a working directory; used by gc-discover.
pub fn run_in(dir: &str, bin: &str, args: &[&str]) -> Result<String, String> {
    let out: Output = Command::new(bin)
        .args(args)
        .current_dir(dir)
        .output()
        .map_err(|e| format!("failed to run {bin}: {e}"))?;
    if !out.status.success() {
        let err = String::from_utf8_lossy(&out.stderr);
        let tail = err.lines().rev().take(3).collect::<Vec<_>>().join("\n");
        return Err(format!("{bin} exited {:?}: {tail}", out.status.code()));
    }
    Ok(String::from_utf8_lossy(&out.stdout).into_owned())
}
