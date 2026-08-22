/**
 * What: Multi-isolate computation pipeline for Tower registry analysis.
 * Where: CLI tools or Flutter apps performing heavy data verification.
 * When: Processing large batches of Tower floor records that would normally block the main event loop.
 * Why: Dart isolates provide true memory isolation and parallelism, scaling horizontally across CPU cores.
 * How: Uses Isolate.spawn, SendPort/ReceivePort for structured envelopes, and Future composition.
 */

import 'dart:async';
import 'dart:isolate';
import 'dart:convert';
import 'package:crypto/crypto.dart';

// Structured Message Protocol Envelopes
abstract class WorkerMessage {}

class VerifyRequest extends WorkerMessage {
  final String floorId;
  final String technology;
  final String payload;
  final SendPort replyTo;

  VerifyRequest(this.floorId, this.technology, this.payload, this.replyTo);
}

class VerifyResult extends WorkerMessage {
  final String floorId;
  final bool success;
  final String? receipt;
  final String? error;

  VerifyResult({required this.floorId, required this.success, this.receipt, this.error});
}

class ShutdownRequest extends WorkerMessage {}

// Entry point for the isolate
void _verificationWorker(SendPort mainSendPort) {
  final port = ReceivePort();
  mainSendPort.send(port.sendPort);

  port.listen((message) {
    if (message is ShutdownRequest) {
      port.close();
      return;
    }

    if (message is VerifyRequest) {
      try {
        if (message.payload.isEmpty) {
          throw Exception("Payload is empty");
        }
        
        final raw = "${message.floorId}:${message.technology}:${message.payload}";
        final bytes = utf8.encode(raw);
        final digest = sha256.convert(bytes);
        
        message.replyTo.send(VerifyResult(
          floorId: message.floorId,
          success: true,
          receipt: digest.toString()
        ));
      } catch (e) {
        message.replyTo.send(VerifyResult(
          floorId: message.floorId,
          success: false,
          error: e.toString()
        ));
      }
    }
  });
}

class AdvancedWorkerPool {
  final int poolSize;
  final List<SendPort> _workerPorts = [];
  int _roundRobinIndex = 0;
  
  AdvancedWorkerPool(this.poolSize);

  Future<void> init() async {
    for (int i = 0; i < poolSize; i++) {
      final port = ReceivePort();
      await Isolate.spawn(_verificationWorker, port.sendPort);
      final sendPort = await port.first as SendPort;
      _workerPorts.add(sendPort);
    }
  }

  Future<VerifyResult> verifyFloor(String floorId, String technology, String payload) {
    final workerPort = _workerPorts[_roundRobinIndex];
    _roundRobinIndex = (_roundRobinIndex + 1) % poolSize;

    final resultPort = ReceivePort();
    workerPort.send(VerifyRequest(floorId, technology, payload, resultPort.sendPort));
    
    return resultPort.first.then((msg) => msg as VerifyResult);
  }

  void shutdown() {
    for (var port in _workerPorts) {
      port.send(ShutdownRequest());
    }
  }
}
