/**
 * What: Type-safe functional stream processor for Tower registry entries.
 * Where: Data pipelines and distributed processing layers.
 * When: Transforming and classifying heterogeneous technology records with absolute type safety.
 * Why: Scala 3's compiler can enforce category errors, exhaustiveness checking via sealed traits, and capability-based refinements.
 * How: Uses opaque types, sealed traits for ADTs, Either for error handling, and lazy iterators for streaming.
 */

package org.glaciereq.tower

import java.security.MessageDigest

object AdvancedSparkTransform {

  // Opaque types for zero-cost domain modeling
  opaque type FloorId = String
  object FloorId:
    def apply(id: String): FloorId = id
    def unwrap(id: FloorId): String = id

  opaque type ReceiptHash = String
  object ReceiptHash:
    def apply(hash: String): ReceiptHash = hash

  // Sealed traits for exhaustive pattern matching
  sealed trait TechCategory
  case object Backend extends TechCategory
  case object Frontend extends TechCategory
  case object DataEng extends TechCategory
  case class Unknown(raw: String) extends TechCategory

  // Type refinement using Match Types
  type ClassifiedFloor[T <: TechCategory] = T match
    case Backend.type  => BackendFloor
    case Frontend.type => FrontendFloor
    case DataEng.type  => DataEngFloor
    case Unknown       => UnverifiedFloor

  case class RawEntry(id: String, tech: String, payload: String)
  
  sealed trait ProcessedFloor { def id: FloorId }
  case class BackendFloor(id: FloorId, payload: String, receipt: ReceiptHash) extends ProcessedFloor
  case class FrontendFloor(id: FloorId, payload: String, receipt: ReceiptHash) extends ProcessedFloor
  case class DataEngFloor(id: FloorId, payload: String, receipt: ReceiptHash) extends ProcessedFloor
  case class UnverifiedFloor(id: FloorId, reason: String) extends ProcessedFloor

  def classifyTech(tech: String): TechCategory = tech.toLowerCase match {
    case "kotlin" | "scala" | "clojure" | "go" | "rust" => Backend
    case "typescript" | "javascript" | "dart" => Frontend
    case "python" | "sql" => DataEng
    case other => Unknown(other)
  }

  def hash(data: String): ReceiptHash = {
    val md = MessageDigest.getInstance("SHA-256")
    ReceiptHash(md.digest(data.getBytes).map("%02x".format(_)).mkString)
  }

  def processEntry(entry: RawEntry): Either[String, ProcessedFloor] = {
    val id = FloorId(entry.id)
    if (entry.payload.isEmpty) Left(s"Floor ${entry.id} has empty payload")
    else {
      val receipt = hash(s"${entry.id}:${entry.tech}:${entry.payload}")
      Right(classifyTech(entry.tech) match {
        case Backend => BackendFloor(id, entry.payload, receipt)
        case Frontend => FrontendFloor(id, entry.payload, receipt)
        case DataEng => DataEngFloor(id, entry.payload, receipt)
        case Unknown(raw) => UnverifiedFloor(id, s"Unknown technology: $raw")
      })
    }
  }

  // Pure Scala functional stream processor
  def processRegistry(stream: Iterator[RawEntry]): Iterator[Either[String, ProcessedFloor]] = {
    stream.map { entry =>
      for {
        processed <- processEntry(entry)
      } yield processed
    }
  }
}
