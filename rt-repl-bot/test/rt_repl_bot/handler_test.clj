(ns rt-repl-bot.handler-test
  (:require [clojure.test :refer :all]
            [clojure.string :as str]
            [rt-repl-bot.handler :refer :all]))

(defn request [method resource body]
  (app {:request-method method :uri resource :body body}))

(deftest handler-test

  (testing "Test GET /info"
    (let [response (request :get "/info" nil)]
      (is (= 200 (:status response)))
      (is (str/starts-with? (:body response) "{\"author\":\"Alex 'SimY4' Simkin\",\"info\":\"Clojure REPL bot\",\"commands\":"))))

  (testing "Test GET /healthcheck"
    (let [response (request :get "/healthcheck" nil)]
      (is (= 200 (:status response)))
      (is (str/starts-with? (:body response) "{\"status\":\"OK\",\"statistics\":"))))

  (testing "Test POST /event should skip random messages with 417 code"
    (is (= 417 (:status (request :post "/event" "random body"))))
    (is (= 417 (:status (request :post "/event" {"text" "randon text"})))))

  (testing "Test POST /event should evaluate clojure commands and respond with 201 code"
    (let [response (request :post "/event" {"text" "clj> (+ 1 1)"})]
      (is (= 201 (:status response)))
      (is (= "{\"text\":\"```\\n2\\n```\",\"bot\":\"REPL-bot\"}" (:body response))))
    (let [response (request :post "/event" {"text" "clj>"})]
      (is (= 201 (:status response)))
      (is (= "{\"text\":\"```\\nEOF while reading\\n```\",\"bot\":\"REPL-bot\"}" (:body response))))
    (let [response (request :post "/event" {"text" "clj>(def var1 5)"})]
      (is (= 201 (:status response)))
      (is (re-matches #"\{\"text\":\"```\\n#'sandbox[0-9]{1,4}/var1\\n```\",\"bot\":\"REPL-bot\"\}" (:body response))))
    (let [response (request :post "/event" {"text" "clj> (while true)"})]
      (is (= 201 (:status response)))
      (is (= "{\"text\":\"```\\nEvaluation timed out in 5 seconds\\n```\",\"bot\":\"REPL-bot\"}" (:body response))))
    (let [response (request :post "/event" {"text" "clj> (+ var1 5)"})]
      (is (= 201 (:status response)))
      (is (= "{\"text\":\"```\\n10\\n```\",\"bot\":\"REPL-bot\"}" (:body response)))))

  (testing "Test 404"
    (is (= 404 (:status (request :post "/info" nil))))
    (is (= 404 (:status (request :post "/heathcheck" nil))))
    (is (= 404 (:status (request :get "/event" {"text" "clj>(+1 1)"}))))
    (is (= 404 (:status (request :get "/" nil))))
    (is (= 404 (:status (request :get "/random" nil))))))