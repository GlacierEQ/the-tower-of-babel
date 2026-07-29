declare const require: (name: string) => any;
declare const process: { argv: string[] };
const { createHash } = require("node:crypto");
const { readFileSync, writeFileSync } = require("node:fs");

interface MissionEnvelope {
  mission_id: string;
  objective: string;
  required_capabilities: string[];
  preferred_interfaces: string[];
  maximum_action: "read" | "plan" | "write_internal" | "external";
  input_sha256?: string;
}

function validate(value: unknown): MissionEnvelope {
  if (typeof value !== "object" || value === null) throw new Error("mission must be an object");
  const row = value as Partial<MissionEnvelope>;
  if (!row.mission_id || !row.objective) throw new Error("mission_id and objective are required");
  if (!Array.isArray(row.required_capabilities) || !Array.isArray(row.preferred_interfaces)) {
    throw new Error("capabilities and interfaces must be arrays");
  }
  if (!["read", "plan", "write_internal", "external"].includes(String(row.maximum_action))) {
    throw new Error("unsupported maximum_action");
  }
  return row as MissionEnvelope;
}

const inputPath = process.argv[2];
const outputPath = process.argv[3];
if (!inputPath || !outputPath) throw new Error("usage: ingress <input.json> <output.json>");
const mission = validate(JSON.parse(readFileSync(inputPath, "utf8")));
const canonical = JSON.stringify(mission, Object.keys(mission).sort());
mission.input_sha256 = createHash("sha256").update(canonical).digest("hex");
writeFileSync(outputPath, JSON.stringify(mission, null, 2) + "\n");
console.log(JSON.stringify({ stage: "ingress", mission_id: mission.mission_id, input_sha256: mission.input_sha256 }));
