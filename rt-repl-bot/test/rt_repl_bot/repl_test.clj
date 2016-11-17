(ns rt-repl-bot.repl-test
  (:require [clojure.test :refer :all]
            [rt-repl-bot.repl :refer :all]))

(deftest repl-test

  (testing "Should evaluate valid forms"
    (is (= "2" (eval-command "(+ 1 1)")))
    (is (re-matches #"#'sandbox[0-9]{1,4}/var1" (eval-command "(def var1 5)")))
    (is (re-matches #"#'sandbox[0-9]{1,4}/fun1" (eval-command "(defn fun1 [x y] (+ x y))")))
    (is (= "10" (eval-command "(fun1 var1 5)"))))

  (testing "Should return evaluation error for invalid forms"
    (not (= "2" (eval-command "(+ 1 1")))
    (not (= "text" (eval-command "text")))
    (not (re-matches #"#'sandbox[0-9]{1,4}/.+" (eval-command "(def 5)")))
    (not (re-matches #"#'sandbox[0-9]{1,4}/.+" (eval-command "(def fun1 [x y] (+ x y))")))
    (not (re-matches #"#'sandbox[0-9]{1,4}/.+" (eval-command "(defn fun1 x y (+ x y))"))))

  (testing "Should fail on infinite loop scripts"
    (is (= "Evaluation timed out in 5 seconds" (eval-command "(while true)")))))