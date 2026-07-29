import triton
import triton.language as tl
@triton.jit
def fused_attn_kernel(Q, K, V, Out, BLOCK_M: tl.constexpr):
    pass
