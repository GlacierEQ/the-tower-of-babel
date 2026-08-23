;; What: CSP channel pipeline and transducers for processing Tower registries.
;; Where: Concurrent backend data ingestion and processing systems.
;; When: Streaming large amounts of unstructured tower data requiring CPU-bound validation.
;; Why: Clojure provides zero-allocation transducers, thread-safe persistent data structures, and core.async CSP.
;; How: Spec-driven validation + core.async/pipeline for parallelism + transducers for composed stateless processing.

(ns org.glaciereq.tower.advanced-transducer
  (:require [clojure.core.async :as async :refer [go >! <! chan close! pipeline]]
            [clojure.spec.alpha :as s]
            [clojure.string :as str])
  (:import (java.security MessageDigest)))

;; 1. Spec-driven Validation
(s/def ::id string?)
(s/def ::technology string?)
(s/def ::payload (s/and string? not-empty))
(s/def ::floor (s/keys :req-un [::id ::technology ::payload]))

;; 2. Domain Logic
(defn sha256 [^String s]
  (let [md (MessageDigest/getInstance "SHA-256")]
    (.update md (.getBytes s "UTF-8"))
    (let [digest (.digest md)]
      (apply str (map #(format "%02x" (bit-and % 0xff)) digest)))))

(defn generate-receipt [{:keys [id technology payload] :as floor}]
  (let [hash (sha256 (str id ":" technology ":" payload))]
    (assoc floor :receipt hash
                 :status :verified)))

(defn process-floor [floor]
  (if (s/valid? ::floor floor)
    (generate-receipt floor)
    (assoc floor :status :invalid
                 :errors (s/explain-data ::floor floor))))

;; 3. Transducers for Zero-Intermediate-Allocation Processing
(def tower-xf
  (comp
    (filter #(not (str/blank? (:id %))))
    (map process-floor)))

;; 4. CSP Pipeline Execution
(defn process-registry-pipeline
  "Processes a collection of raw floor maps concurrently using core.async pipelines."
  [raw-floors parallelism]
  (let [in-chan (chan 100)
        out-chan (chan 100)
        done-chan (chan)]
    
    ;; Pipeline setup: read from in-chan, process via transducer with `parallelism`, write to out-chan
    (pipeline parallelism out-chan tower-xf in-chan)

    ;; Feeder go-block
    (go
      (doseq [f raw-floors]
        (>! in-chan f))
      (close! in-chan))

    ;; Consumer go-block
    (go
      (loop [acc []]
        (if-let [result (<! out-chan)]
          (recur (conj acc result))
          (do
            (>! done-chan acc)
            (close! done-chan)))))
            
    done-chan))

;; Usage Example (Concept):
;; (let [results (async/<!! (process-registry-pipeline [{:id "1" :technology "Clojure" :payload "CSP"}] 4))]
;;   (println results))
