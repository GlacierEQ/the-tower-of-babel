package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
)

type Decision struct {
	MissionID  string `json:"mission_id"`
	Allowed    bool   `json:"allowed"`
	Reason     string `json:"reason"`
	PlanSHA256 string `json:"plan_sha256"`
}

type Event struct {
	MissionID       string `json:"mission_id"`
	Stage           string `json:"stage"`
	Status          string `json:"status"`
	EvidenceSHA256  string `json:"evidence_sha256"`
}

func main() {
	if len(os.Args) != 3 {
		panic("usage: telemetry <decision.json> <event.json>")
	}
	raw, err := os.ReadFile(os.Args[1])
	if err != nil { panic(err) }
	var decision Decision
	if err := json.Unmarshal(raw, &decision); err != nil { panic(err) }
	sum := sha256.Sum256(raw)
	status := "BLOCKED"
	if decision.Allowed { status = "SUCCEEDED" }
	event := Event{decision.MissionID, "authority", status, hex.EncodeToString(sum[:])}
	out, _ := json.MarshalIndent(event, "", "  ")
	if err := os.WriteFile(os.Args[2], append(out, '\n'), 0644); err != nil { panic(err) }
	fmt.Println(string(out))
}
