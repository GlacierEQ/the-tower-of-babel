/**
 * Advanced TypeScript exhibit: bounded JSON-RPC/MCP gateway.
 * Evidence class: tested through the executable self-test below.
 */
type JsonRpcId = string | number | null;
interface JsonRpcRequest {
  jsonrpc: "2.0";
  id: JsonRpcId;
  method: string;
  params?: unknown;
}
interface JsonRpcSuccess {
  jsonrpc: "2.0";
  id: JsonRpcId;
  result: unknown;
}
interface JsonRpcFailure {
  jsonrpc: "2.0";
  id: JsonRpcId;
  error: { code: number; message: string };
}
type JsonRpcResponse = JsonRpcSuccess | JsonRpcFailure;
type Handler = (params: unknown) => Promise<unknown>;

class Gateway {
  private readonly handlers = new Map<string, Handler>();

  constructor(private readonly timeoutMs = 1_000) {}

  register(method: string, handler: Handler): void {
    if (!method || this.handlers.has(method)) {
      throw new Error(`invalid or duplicate method: ${method}`);
    }
    this.handlers.set(method, handler);
  }

  private validate(value: unknown): JsonRpcRequest {
    if (typeof value !== "object" || value === null) throw new Error("request must be an object");
    const row = value as Partial<JsonRpcRequest>;
    if (row.jsonrpc !== "2.0") throw new Error("jsonrpc must be 2.0");
    if (typeof row.method !== "string" || row.method.length === 0) throw new Error("method is required");
    if (!("id" in row)) throw new Error("id is required");
    return row as JsonRpcRequest;
  }

  async handle(input: unknown): Promise<JsonRpcResponse> {
    let request: JsonRpcRequest;
    try {
      request = this.validate(input);
    } catch (error) {
      return { jsonrpc: "2.0", id: null, error: { code: -32600, message: String(error) } };
    }
    const handler = this.handlers.get(request.method);
    if (!handler) {
      return { jsonrpc: "2.0", id: request.id, error: { code: -32601, message: "method not found" } };
    }
    try {
      const result = await Promise.race([
        handler(request.params),
        new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error("handler timeout")), this.timeoutMs),
        ),
      ]);
      return { jsonrpc: "2.0", id: request.id, result };
    } catch (error) {
      return { jsonrpc: "2.0", id: request.id, error: { code: -32000, message: String(error) } };
    }
  }
}

async function selfTest(): Promise<void> {
  const gateway = new Gateway(100);
  gateway.register("tower.spec", async (params) => ({ ok: true, params }));
  const success = await gateway.handle({ jsonrpc: "2.0", id: 1, method: "tower.spec", params: { id: "rust" } });
  if (!("result" in success)) throw new Error("expected success");
  const missing = await gateway.handle({ jsonrpc: "2.0", id: 2, method: "missing" });
  if (!("error" in missing) || missing.error.code !== -32601) throw new Error("expected method error");
  console.log(JSON.stringify({ success, missing }));
}

void selfTest();
