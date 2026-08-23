/**
 * What: Concurrent floor verification gateway utilizing structured concurrency.
 * Where: JVM service layer of the Tower of Babel.
 * When: Parallel validation of heterogeneous technology registries requires non-blocking execution.
 * Why: Kotlin coroutines provide built-in cancellation propagation, supervisor scopes for fault tolerance, and cold stream backpressure.
 * How: Combines supervisorScope for batch resilience, Channels for M:N fan-out/fan-in, and Flow for cold reactive processing.
 */

package org.glaciereq.tower

import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.flow.*
import java.security.MessageDigest

data class TowerFloor(val id: String, val technology: String, val payload: String)
data class VerificationResult(val floorId: String, val valid: Boolean, val receipt: String, val error: String? = null)

class AdvancedCoroutineGateway {

    private val exceptionHandler = CoroutineExceptionHandler { _, exception ->
        println("Gateway caught global error: ${exception.message}")
    }

    /**
     * Verifies a stream of floors concurrently, guaranteeing that one failure does not abort the whole batch.
     */
    suspend fun verifyFloors(floors: List<TowerFloor>, parallelism: Int = 4): Flow<VerificationResult> = flow {
        supervisorScope {
            val floorChannel = produce(capacity = parallelism * 2) {
                for (floor in floors) send(floor)
            }

            val resultChannel = Channel<VerificationResult>(Channel.BUFFERED)

            // Fan-out: start multiple workers
            val workers = (1..parallelism).map {
                launch(exceptionHandler) {
                    for (floor in floorChannel) {
                        try {
                            val result = verifyFloor(floor)
                            resultChannel.send(result)
                        } catch (e: Exception) {
                            // supervisorScope allows other coroutines to continue
                            resultChannel.send(
                                VerificationResult(floor.id, false, "", e.message)
                            )
                        }
                    }
                }
            }

            // Fan-in: close result channel when all workers complete
            launch {
                workers.joinAll()
                resultChannel.close()
            }

            // Emit to flow
            for (result in resultChannel) {
                emit(result)
            }
        }
    }.buffer(Channel.BUFFERED).flowOn(Dispatchers.Default)

    private suspend fun verifyFloor(floor: TowerFloor): VerificationResult {
        // Simulate IO or CPU bound work
        delay(50)
        if (floor.payload.isEmpty()) {
            throw IllegalArgumentException("Empty payload for floor ${floor.id}")
        }
        val rawReceipt = "${floor.id}:${floor.technology}:${floor.payload}:${System.currentTimeMillis()}"
        val md = MessageDigest.getInstance("SHA-256")
        val hash = md.digest(rawReceipt.toByteArray()).joinToString("") { "%02x".format(it) }
        return VerificationResult(floor.id, true, hash)
    }
}
