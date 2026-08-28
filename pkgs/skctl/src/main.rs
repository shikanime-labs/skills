mod cmd;
mod discover_metadata;
mod fetch_backport_set;
mod gc_discover;
mod milestone_number;
mod next_milestone;
mod verify_backport;

use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(
    name = "skctl",
    version,
    about = "Wrap common shikanime/cloud-pi-native operations"
)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Print the next patch milestone for a base tag (v9.24.4 -> 9.24.5)
    NextMilestone {
        #[arg(value_name = "BASE_TAG")]
        base_tag: String,
    },
    /// Print the milestone number for a title on REPO (OWNER/REPO)
    MilestoneNumber {
        #[arg(value_name = "REPO")]
        repo: String,
        #[arg(value_name = "MILESTONE_TITLE")]
        title: String,
    },
    /// Print (and optionally write) the ordered merge-commit SHAs of a
    /// milestone's merged PRs
    FetchBackportSet {
        #[arg(value_name = "REPO")]
        repo: String,
        #[arg(value_name = "MILE_NUM")]
        mile_num: u32,
        #[arg(value_name = "OUTFILE", default_value = "/tmp/cpn_ms_ids.txt")]
        outfile: String,
    },
    /// Verify a rebuilt hotfix chain: count / conflict / tree-parity check
    VerifyBackport {
        #[arg(value_name = "BASE_TAG")]
        base_tag: String,
        #[arg(value_name = "TIP")]
        tip: String,
        // `wc -l < file` right-pads its output; accept surrounding whitespace.
        #[arg(value_name = "EXPECTED_COUNT", value_parser = parse_usize)]
        expected: usize,
    },
    /// Discover GC candidates in a shikanime jj repo (dry-run only)
    GcDiscover {
        #[arg(value_name = "REPO_DIR", default_value = ".")]
        repo_dir: String,
    },
    /// Discover every triage-relevant metadata value a repo offers
    DiscoverMetadata {
        #[arg(value_name = "REPO")]
        repo: String,
    },
}

fn main() {
    let cli = Cli::parse();
    let code = match run(cli.command) {
        Ok(()) => 0,
        Err(e) => {
            eprintln!("Error: {e}");
            1
        }
    };
    std::process::exit(code);
}

fn parse_usize(s: &str) -> Result<usize, String> {
    s.trim()
        .parse::<usize>()
        .map_err(|_| format!("'{s}' is not a valid count"))
}

fn run(command: Command) -> Result<(), String> {
    match command {
        Command::NextMilestone { base_tag } => {
            println!("{}", next_milestone::next_milestone(&base_tag)?);
            Ok(())
        }
        Command::MilestoneNumber { repo, title } => {
            match milestone_number::milestone_number(&repo, &title)? {
                Some(n) => {
                    println!("{n}");
                    Ok(())
                }
                None => Err(format!("milestone '{title}' is absent or closed on {repo}")),
            }
        }
        Command::FetchBackportSet {
            repo,
            mile_num,
            outfile,
        } => {
            let shas = fetch_backport_set::fetch_backport_set(&repo, mile_num, &outfile)?;
            println!("wrote {} commits to {outfile}", shas.len());
            Ok(())
        }
        Command::VerifyBackport {
            base_tag,
            tip,
            expected,
        } => {
            let failures = verify_backport::verify_backport(&base_tag, &tip, expected)?;
            if failures.is_empty() {
                println!("OK: chain verified against {base_tag}..{tip}");
                Ok(())
            } else {
                Err(failures.join("\n"))
            }
        }
        Command::GcDiscover { repo_dir } => {
            let report = gc_discover::discover(&repo_dir)?;
            println!("== dangling bookmarks (not trunk, no open PR) ==");
            for bm in &report.dangling_bookmarks {
                println!("{bm}");
            }
            println!("== skill workspaces (<repo>.<unit> or <repo>-fix) ==");
            for ws in &report.workspaces {
                if ws.clean {
                    println!("CLEAN {} {}", ws.name, ws.path);
                } else {
                    println!(
                        "DIRTY {} {}   # skip: uncommitted changes (data loss)",
                        ws.name, ws.path
                    );
                }
            }
            Ok(())
        }
        Command::DiscoverMetadata { repo } => {
            print!("{}", discover_metadata::discover_metadata(&repo)?);
            Ok(())
        }
    }
}
