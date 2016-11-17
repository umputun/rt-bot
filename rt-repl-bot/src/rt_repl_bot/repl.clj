(ns rt-repl-bot.repl
  (:import (java.util.concurrent TimeoutException)
           (java.io StringWriter))
  (:require [clojail.core :refer [sandbox]]
            [clojail.testers :refer [secure-tester-without-def]]))

(def ^:private repl-sandbox
  "Clojure jailed sandbox instance"
  (sandbox
    secure-tester-without-def
    :timeout 5000
    :init '(require '[clojure.repl :refer [doc source]])
    ))

(defn eval-command [command]
  "Evaluates given command in jailed snadbox and returns the evaluated result couped with the output
  that was generated during the command execution"
  (with-open [out (StringWriter.)]
    (try
      (let [form (binding [*read-eval* false] (read-string command))
            eval-result (repl-sandbox form {#'*out* out})
            out-string (.toString out)]
        (if (.isEmpty out-string)
          eval-result
          (str out-string "\n" eval-result)))
      (catch TimeoutException _
        "Evaluation timed out in 5 seconds")
      (catch Exception e
        (.getMessage e)))))
