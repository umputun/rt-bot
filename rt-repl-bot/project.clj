(defproject rt-repl-bot "0.1.0"
  :description "Clojure REPL bot for Radio-T chat"
  :dependencies [[org.clojure/clojure "1.8.0"]
                 [org.clojure/tools.logging "0.3.1"]
                 [compojure "1.5.1"]
                 [ring-server "0.4.0"]
                 [ring/ring-json "0.4.0"]
                 [clojail "1.0.6"]
                 [amalloy/ring-buffer "1.2.1" :exclusions [org.clojure/clojurescript]]]
  :jvm-opts ["-Djava.security.policy=.java.policy"]
  :plugins [[lein-ring "0.9.7"]]
  :ring {:handler rt-repl-bot.handler/app :port 8080})
