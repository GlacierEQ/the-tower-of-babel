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

function requireNonEmptyString(value: unknown, field: string): string {
  if (typeof value !== "string" || value.trim().length === 0) {
    throw new Error(`${field} must be a non-empty string`);
  }
  return value;
}

function requireStringArray(value: unknown, field: string): string[] {
  if (!Array.isArray(value) || value.some((item) => typeof item !== "string" || item.trim().length === 0)) {
    throw new Error(`${field} must be an array of non-empty strings`);
  }
  return value as string[];
}

function validate(value: unknown): MissionEnvelope {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error("mission must be an object");
  }
  const row = value as Partial<MissionEnvelope>;
  const mission_id = requireNonEmptyString(row.mission_id, "mission_id");
  const objective = requireNonEmptyString(row.objective, "objective");
  const required_capabilities = requireStringArray(row.required_capabilities, "required_capabilities");
  const preferred_interfaces = requireStringArray(row.preferred_interfaces, "preferred_interfaces");
  if (!row.maximum_action || !["read", "plan", "write_internal", "external"].includes(row.maximum_action)) {
    throw new Error("unsupported maximum_action");
  }
  return {
    mission_id,
    objective,
    required_capabilities,
    preferred_interfaces,
    maximum_action: row.maximum_action,
  };
}

function canonicalMission(mission: MissionEnvelope): string {
  const entries = Object.entries(mission).sort(([left], [right]) => left.localeCompare(right));
  return JSON.stringify(Object.fromEntries(entries));
}

const inputPath = process.argv[2];
const outputPath = process.argv[3];
if (!inputPath || !outputPath) throw new Error("usage: ingress <input.json> <output.json>");
const mission = validate(JSON.parse(readFileSync(inputPath, "utf8")));
mission.input_sha256 = createHash("sha256").update(canonicalMission(mission)).digest("hex");
writeFileSync(outputPath, JSON.stringify(mission, null, 2) + "\n");
console.log(JSON.stringify({ stage: "ingress", mission_id: mission.mission_id, input_sha256: mission.input_sha256 }));
