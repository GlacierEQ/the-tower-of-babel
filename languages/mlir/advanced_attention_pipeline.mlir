// Multi-level lowering sketch: tensor semantics to vectorizable loops.
module {
  func.func @scaled_scores(%q: tensor<?x?xf32>, %k: tensor<?x?xf32>, %scale: f32)
      -> tensor<?x?xf32> {
    %kt = "tensor.transpose"(%k) {permutation = array<i64: 1, 0>}
      : (tensor<?x?xf32>) -> tensor<?x?xf32>
    %scores = "linalg.matmul"(%q, %kt)
      : (tensor<?x?xf32>, tensor<?x?xf32>) -> tensor<?x?xf32>
    %scaled = "linalg.map"(%scores, %scale) ({
      ^bb0(%value: f32, %s: f32):
        %out = arith.mulf %value, %s : f32
        linalg.yield %out : f32
    }) : (tensor<?x?xf32>, f32) -> tensor<?x?xf32>
    return %scaled : tensor<?x?xf32>
  }
}
