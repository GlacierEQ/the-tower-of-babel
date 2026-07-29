use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{env, fs};

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
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 {
        panic!("usage: tower-governor <plan.json> <decision.json>");
    }
    let bytes = fs::read(&args[1]).expect("read plan");
    let plan: Plan = serde_json::from_slice(&bytes).expect("parse plan");
    let digest = hex::encode(Sha256::digest(&bytes));
    let allowed = !plan.technology_ids.is_empty() && plan.tower_registry_sha256.len() == 64;
    let decision = Decision {
        mission_id: plan.mission_id,
        allowed,
        reason: if allowed {
            "non-empty Tower plan with bound registry hash".into()
        } else {
            "plan failed Tower authority preconditions".into()
        },
        plan_sha256: digest,
    };
    fs::write(&args[2], serde_json::to_vec_pretty(&decision).unwrap()).expect("write decision");
    println!("{}", serde_json::to_string(&decision).unwrap());
}
