package tower

import chisel3._
import chisel3.util._

class Flit(width: Int) extends Bundle {
  val destination = UInt(4.W)
  val payload = UInt(width.W)
}

class AdvancedNoCRouter(width: Int = 64, ports: Int = 4) extends Module {
  val io = IO(new Bundle {
    val in = Flipped(Vec(ports, Decoupled(new Flit(width))))
    val out = Vec(ports, Decoupled(new Flit(width)))
  })

  val arbiters = Seq.fill(ports)(Module(new RRArbiter(new Flit(width), ports)))

  for (outPort <- 0 until ports) {
    for (inPort <- 0 until ports) {
      val selected = io.in(inPort).bits.destination === outPort.U
      arbiters(outPort).io.in(inPort).valid := io.in(inPort).valid && selected
      arbiters(outPort).io.in(inPort).bits := io.in(inPort).bits
    }
    io.out(outPort) <> arbiters(outPort).io.out
  }

  for (inPort <- 0 until ports) {
    val readyVector = VecInit((0 until ports).map { outPort =>
      arbiters(outPort).io.in(inPort).ready &&
        io.in(inPort).bits.destination === outPort.U
    })
    io.in(inPort).ready := readyVector.asUInt.orR
  }
}

object AdvancedNoCRouter extends App {
  emitVerilog(new AdvancedNoCRouter())
}
