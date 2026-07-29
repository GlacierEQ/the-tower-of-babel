#include <cuda_runtime.h>
__global__ void flash_attn(const float* q, const float* k, float* out) { int id = blockIdx.x * blockDim.x + threadIdx.x; out[id] = q[id] * k[id]; }
