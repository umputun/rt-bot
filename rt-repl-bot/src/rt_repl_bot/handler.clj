(ns rt-repl-bot.handler
  (:use compojure.core ring.middleware.json)
  (:require [clojure.string :as str]
            [clojure.tools.logging :as log]
            [ring.middleware.defaults :refer :all]
            [compojure.core :refer :all]
            [compojure.route :refer [not-found]]
            [rt-repl-bot.repl :as repl]
            [metrics.ring.instrument :refer [instrument]]
            [metrics.ring.expose :refer [expose-metrics-as-json]]))

(defn handle-command [command]
  "Handles REST POST /event call and returns constructed response"
  (let [eval-result (repl/eval-command command)]
    (log/info "clj>" command "~" eval-result)
    {:status  201
     :body    {:text (str "```\n" eval-result "\n```")
               :bot  "REPL-bot"}
     }))

(defroutes
  app-routes
  "REST API routes"
  (GET "/info" []
    {:status 200
     :body   {:author   "Alex 'SimY4' Simkin"
              :info     "Clojure REPL bot"
              :commands ["clj> (do\n  (prn \"Весь текст после префикса 'clj>' будет вычислен как форма Clojure. Например:)\n  (+ 5 5))\n```\n10\n```"]}
     })
  (POST "/event" {body :body}
    (let [text (or (get body "text") "")]
      (cond
        (str/starts-with? text "clj>") (handle-command (subs text 4))
        :else {:status 417 :body {:status "Expectation Failed"}})))
  (not-found
    {:status 404 :body {:status "Not Found"}}))

(def app
  "REPL bot application"
  (->
    app-routes
    (instrument)
    (wrap-json-body)
    (wrap-json-response)
    (expose-metrics-as-json)
    (wrap-defaults api-defaults)))