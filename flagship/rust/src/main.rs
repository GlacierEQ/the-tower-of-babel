use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{env, fs, process};

#[derive(Deserialize)]
struct Plan {
    mission_id: String,
    technology_ids: Vec<String>,
    tower_registry_sha256: String,
}

#[derive(Serialize)]
struct Decision {
    mission_id: String,
    allowed: bool,
    reason: String,
    plan_sha256: String,
    expected_registry_sha256: String,
    observed_registry_sha256: String,
}

fn is_sha256(value: &str) -> bool {
    value.len() == 64 && value.bytes().all(|byte| byte.is_ascii_hexdigit())
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 4 {
        eprintln!("usage: tower-governor <plan.json> <decision.json> <expected-registry-sha256>");
        process::exit(2);
    }
    let bytes = fs::read(&args[1]).expect("read plan");
    let plan: Plan = serde_json::from_slice(&bytes).expect("parse plan");
    let expected_registry_sha256 = args[3].trim().to_ascii_lowercase();
    let observed_registry_sha256 = plan.tower_registry_sha256.trim().to_ascii_lowercase();
    let digest = hex::encode(Sha256::digest(&bytes));
    let registry_matches = is_sha256(&expected_registry_sha256)
        && is_sha256(&observed_registry_sha256)
        && expected_registry_sha256 == observed_registry_sha256;
    let allowed = !plan.mission_id.trim().is_empty()
        && !plan.technology_ids.is_empty()
        && registry_matches;
    let decision = Decision {
        mission_id: plan.mission_id,
        allowed,
        reason: if allowed {
            "non-empty Tower plan bound to the independently supplied canonical registry hash".into()
        } else if !registry_matches {
            "plan registry hash does not match the canonical Tower registry".into()
        } else {
            "plan failed Tower authority preconditions".into()
        },
        plan_sha256: digest,
        expected_registry_sha256,
        observed_registry_sha256,
    };
    fs::write(&args[2], serde_json::to_vec_pretty(&decision).unwrap()).expect("write decision");
    println!("{}", serde_json::to_string(&decision).unwrap());
    if !allowed {
        process::exit(3);
    }
}
