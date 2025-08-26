;; Example MeTTa script for Nimo project
;; This demonstrates basic identity concepts and contributions

;; Define identity atoms
(= (Identity $name $attributes) (Person $name $attributes))

;; Define contribution types
(= (Contribution $type $content $author) (Record $type $content $author))

;; Sample identities
(Identity "Alice" (Attributes (Age 17) (Skills "Coding" "Music")))
(Identity "Bob" (Attributes (Age 16) (Skills "Art" "Writing")))

;; Sample contributions
(Contribution "CodeProject" "Built a calculator app" "Alice")
(Contribution "Blog" "How to learn programming" "Bob")

;; Query to find all identities
!(match &self (Identity $name $attrs) (println $name ":" $attrs))

;; Query to find all contributions
!(match &self (Contribution $type $content $author) 
  (println "Contribution by" $author ":" $type "-" $content))

;; Query to find specific contributions by author
!(match &self (Contribution $type $content "Alice") 
  (println "Alice contributed:" $type "-" $content))