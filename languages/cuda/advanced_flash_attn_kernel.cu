// Advanced CUDA exhibit: reference scaled dot-product attention kernel.
// This is an auditable correctness reference, not a claim to implement the
// production FlashAttention algorithm. Evidence class: hardware_gated.

#include <cuda_runtime.h>
#include <cmath>
#include <cstdio>
#include <vector>

__global__ void reference_attention(
    const float* q, const float* k, const float* v, float* out,
    int sequence, int dimension) {
    const int query_index = blockIdx.x;
    if (query_index >= sequence || threadIdx.x != 0) return;

    extern __shared__ float scores[];
    const float scale = rsqrtf(static_cast<float>(dimension));
    float max_score = -INFINITY;
    for (int key_index = 0; key_index < sequence; ++key_index) {
        float dot = 0.0f;
        for (int d = 0; d < dimension; ++d) {
            dot += q[query_index * dimension + d] * k[key_index * dimension + d];
        }
        scores[key_index] = dot * scale;
        max_score = fmaxf(max_score, scores[key_index]);
    }

    float denominator = 0.0f;
    for (int key_index = 0; key_index < sequence; ++key_index) {
        scores[key_index] = expf(scores[key_index] - max_score);
        denominator += scores[key_index];
    }

    for (int d = 0; d < dimension; ++d) {
        float value = 0.0f;
        for (int key_index = 0; key_index < sequence; ++key_index) {
            value += (scores[key_index] / denominator) * v[key_index * dimension + d];
        }
        out[query_index * dimension + d] = value;
    }
}

int main() {
    constexpr int sequence = 4;
    constexpr int dimension = 4;
    std::vector<float> host(sequence * dimension, 0.25f);
    float *q, *k, *v, *out;
    const size_t bytes = host.size() * sizeof(float);
    cudaMalloc(&q, bytes); cudaMalloc(&k, bytes); cudaMalloc(&v, bytes); cudaMalloc(&out, bytes);
    cudaMemcpy(q, host.data(), bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(k, host.data(), bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(v, host.data(), bytes, cudaMemcpyHostToDevice);
    reference_attention<<<sequence, 1, sequence * sizeof(float)>>>(q, k, v, out, sequence, dimension);
    cudaDeviceSynchronize();
    cudaMemcpy(host.data(), out, bytes, cudaMemcpyDeviceToHost);
    printf("attention[0]=%.6f\n", host[0]);
    cudaFree(q); cudaFree(k); cudaFree(v); cudaFree(out);
    return 0;
}
