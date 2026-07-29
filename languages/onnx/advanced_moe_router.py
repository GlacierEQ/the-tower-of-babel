"""Build a portable ONNX top-k Mixture-of-Experts router graph."""
from pathlib import Path
import onnx
from onnx import TensorProto, checker, helper

Path("build").mkdir(exist_ok=True)
tokens = helper.make_tensor_value_info("tokens", TensorProto.FLOAT, ["batch", "hidden"])
weights = helper.make_tensor_value_info("router_weights", TensorProto.FLOAT, ["hidden", "experts"])
values = helper.make_tensor_value_info("top_values", TensorProto.FLOAT, ["batch", 2])
indices = helper.make_tensor_value_info("top_indices", TensorProto.INT64, ["batch", 2])
k = helper.make_tensor("k", TensorProto.INT64, [1], [2])
nodes = [
    helper.make_node("MatMul", ["tokens", "router_weights"], ["logits"]),
    helper.make_node("Softmax", ["logits"], ["probabilities"], axis=-1),
    helper.make_node("TopK", ["probabilities", "k"], ["top_values", "top_indices"], axis=-1, largest=1, sorted=1),
]
graph = helper.make_graph(nodes, "portable-moe-router", [tokens, weights], [values, indices], [k])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
model.metadata_props.add(key="tower.evidence_state", value="tested")
model.metadata_props.add(key="tower.purpose", value="portable top-k expert routing")
checker.check_model(model)
onnx.save(model, "build/advanced_moe_router.onnx")
print("wrote build/advanced_moe_router.onnx")
