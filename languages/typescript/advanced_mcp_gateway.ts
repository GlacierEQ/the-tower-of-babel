export interface MCPRequest { jsonrpc: "2.0"; method: string; }
export class Gateway { handle(r: MCPRequest) { return { status: "DISPATCHED", method: r.method }; } }
