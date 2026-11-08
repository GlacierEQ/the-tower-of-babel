// =============================================================================
// WHAT: Multi-Level Intermediate Representation (MLIR) affine & linalg attention
// WHERE: Tensor compiler optimization pipeline for high-performance GPU execution
// WHEN: Lowering high-level Transformer attention graphs to hardware vector units
// WHY: Bridges high-level math with LLVM machine code via polyhedral loop tiling
// HOW: linalg.generic, affine.for, vector.transfer_read/write dialect composition
// =============================================================================

module @advanced_attention_kernel {
  func.func @flash_attention_tile_2d(
    %query: memref<128x64xf32>,
    %key: memref<128x64xf32>,
    %output: memref<128x128xf32>
  ) {
    %c0 = arith.constant 0 : index
    %c128 = arith.constant 128 : index
    %c32 = arith.constant 32 : index
    %f0 = arith.constant 0.0 : f32

    // Outer Polyhedral Loop Tiling over Query Blocks (Tile Size = 32)
    affine.for %i = 0 to 128 step 32 {
      // Inner Polyhedral Loop Tiling over Key Blocks (Tile Size = 32)
      affine.for %j = 0 to 128 step 32 {
        // Initialize accumulator tile
        affine.for %ii = 0 to 32 {
          affine.for %jj = 0 to 32 {
            affine.store %f0, %output[%i + %ii, %j + %jj] : memref<128x128xf32>
          }
        }

        // Fused Matrix Multiply Dot Product with Affine bounds
        affine.for %k = 0 to 64 {
          affine.for %ii = 0 to 32 {
            %q_val = affine.load %query[%i + %ii, %k] : memref<128x64xf32>
            affine.for %jj = 0 to 32 {
              %k_val = affine.load %key[%j + %jj, %k] : memref<128x64xf32>
              %old_acc = affine.load %output[%i + %ii, %j + %jj] : memref<128x128xf32>
              %prod = arith.mulf %q_val, %k_val : f32
              %new_acc = arith.addf %old_acc, %prod : f32
              affine.store %new_acc, %output[%i + %ii, %j + %jj] : memref<128x128xf32>
            }
          }
        }
      }
    }
    return
  }
}
