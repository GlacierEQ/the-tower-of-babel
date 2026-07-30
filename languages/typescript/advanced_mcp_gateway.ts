/**
 * Advanced TypeScript exhibit: bounded JSON-RPC/MCP gateway.
 * Evidence class: tested through the executable self-test below.
 */
type JsonRpcId = string | number | null;
interface JsonRpcRequest {
  jsonrpc: "2.0";
  id?: JsonRpcId;
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
type Handler = (params: unknown, signal: AbortSignal) => Promise<unknown>;

class Gateway {
  private readonly handlers = new Map<string, Handler>();

  constructor(private readonly timeoutMs = 1_000) {
    if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
      throw new Error("timeoutMs must be a positive finite number");
    }
  }

  register(method: string, handler: Handler): void {
    if (!method || this.handlers.has(method)) {
      throw new Error(`invalid or duplicate method: ${method}`);
    }
    this.handlers.set(method, handler);
  }

  private validate(value: unknown): JsonRpcRequest {
    if (typeof value !== "object" || value === null || Array.isArray(value)) {
      throw new Error("request must be an object");
    }
    const row = value as Partial<JsonRpcRequest>;
    if (row.jsonrpc !== "2.0") throw new Error("jsonrpc must be 2.0");
    if (typeof row.method !== "string" || row.method.length === 0) throw new Error("method is required");
    if ("id" in row) {
      const validId = row.id === null
        || typeof row.id === "string"
        || (typeof row.id === "number" && Number.isFinite(row.id));
      if (!validId) throw new Error("id must be a string, finite number, or null");
    }
    return row as JsonRpcRequest;
  }

  async handle(input: unknown): Promise<JsonRpcResponse | null> {
    let request: JsonRpcRequest;
    try {
      request = this.validate(input);
    } catch (error) {
      return { jsonrpc: "2.0", id: null, error: { code: -32600, message: String(error) } };
    }
    const notification = !("id" in request);
    const handler = this.handlers.get(request.method);
    if (!handler) {
      return notification
        ? null
        : { jsonrpc: "2.0", id: request.id ?? null, error: { code: -32601, message: "method not found" } };
    }

    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    try {
      const timeout = new Promise<never>((_, reject) => {
        timer = setTimeout(() => {
          controller.abort("handler timeout");
          reject(new Error("handler timeout"));
        }, this.timeoutMs);
      });
      const result = await Promise.race([
        handler(request.params, controller.signal),
        timeout,
      ]);
      return notification
        ? null
        : { jsonrpc: "2.0", id: request.id ?? null, result };
    } catch (error) {
      return notification
        ? null
        : { jsonrpc: "2.0", id: request.id ?? null, error: { code: -32000, message: String(error) } };
    } finally {
      if (timer !== undefined) clearTimeout(timer);
    }
  }
}

async function selfTest(): Promise<void> {
  const gateway = new Gateway(25);
  let notifications = 0;
  gateway.register("tower.spec", async (params) => ({ ok: true, params }));
  gateway.register("tower.notify", async () => {
    notifications += 1;
    return { accepted: true };
  });
  gateway.register("tower.slow", async (_params, signal) =>
    new Promise((_resolve, reject) => {
      signal.addEventListener("abort", () => reject(new Error(String(signal.reason))), { once: true });
    }));

  const success = await gateway.handle({ jsonrpc: "2.0", id: 1, method: "tower.spec", params: { id: "rust" } });
  if (success === null || !("result" in success)) throw new Error("expected success");
  const missing = await gateway.handle({ jsonrpc: "2.0", id: 2, method: "missing" });
  if (missing === null || !("error" in missing) || missing.error.code !== -32601) throw new Error("expected method error");
  const invalidId = await gateway.handle({ jsonrpc: "2.0", id: Number.NaN, method: "tower.spec" });
  if (invalidId === null || !("error" in invalidId) || invalidId.error.code !== -32600) throw new Error("expected invalid-request error");
  const notification = await gateway.handle({ jsonrpc: "2.0", method: "tower.notify" });
  if (notification !== null || notifications !== 1) throw new Error("expected notification execution without response");
  const timeout = await gateway.handle({ jsonrpc: "2.0", id: "slow", method: "tower.slow" });
  if (timeout === null || !("error" in timeout) || !timeout.error.message.includes("timeout")) throw new Error("expected timeout error");
  console.log(JSON.stringify({ success, missing, invalidId, notification, timeout }));
}

void selfTest();
