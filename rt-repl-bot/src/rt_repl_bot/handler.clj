(ns rt-repl-bot.handler
  (:use compojure.core ring.middleware.json)
  (:require [clojure.string :as str]
            [clojure.tools.logging :as log]
            [compojure.handler :as handler]
            [compojure.route :as route]
            [rt-repl-bot.repl :as repl]
            [amalloy.ring-buffer :refer [ring-buffer]]))

(def most-recent-calls
  "Simlple finite buffer to store latest REST API calls for simple statistics"
  (atom (ring-buffer 50)))

(defn handle-command [command]
  "Handles REST POST /event call and returns constructed response"
  (let [eval-result (repl/eval-command command)]
    (log/info "clj>" command "~" eval-result)
    {:status  201
     :body    {:text (str "```\n" eval-result "\n```")
               :bot  "REPL-bot"}
     }))

(defn wrap-statistics [handler]
  "Ring framework middleware that will collect the latest API calls meta for simple statistics"
  (wrap-routes
    handler
    (fn [route-handler]
      (fn [request]
        (let [start (. System (nanoTime))
              response (route-handler request)
              exec-time (/ (double (- (. System (nanoTime)) start)) 1000000.0)]
          (swap! most-recent-calls conj (str (:compojure/route request) "[" exec-time "] ~" (:status response)))
          response
          )))))

(defroutes
  app-routes
  "REST API routes"
  (GET "/healthcheck" []
    {:status 200
     :body   {:status     "OK"
              :statistics (sequence (deref most-recent-calls))}
     })
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
        :else {:status 417})))
  (route/not-found {:status 404}))

(def app
  "REPL bot application"
  (->
    (handler/site app-routes)
    (wrap-json-body)
    (wrap-statistics)
    (wrap-json-response)))