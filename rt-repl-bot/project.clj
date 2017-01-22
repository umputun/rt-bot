(defproject rt-repl-bot "1.0.0"
  :description "Clojure REPL bot for Radio-T chat"
  :dependencies [[org.clojure/clojure "1.8.0"]
                 [org.clojure/tools.logging "0.3.1"]
                 [ch.qos.logback/logback-classic "1.1.8"]
                 [compojure "1.5.2"]
                 [ring-server "0.4.0"]
                 [ring/ring-json "0.4.0"]
                 [ring/ring-defaults "0.2.1"]
                 [clojail "1.0.6"]
                 [metrics-clojure "2.8.0"]
                 [metrics-clojure-ring "2.8.0"]]
  :jvm-opts ["-Djava.security.policy=.java.policy"]
  :plugins [[lein-ring "0.10.0"]]
  :ring {:handler rt-repl-bot.handler/app :port 8080})
