 lisp laba 2

;; Lab 2

(defstruct node
  question
  yes
  no
  diagnosis)

(defparameter *tree*
  (make-node 
    :question "Organic brain damage present?"
    :yes (make-node 
           :question "Cannot form new memories?"
           :yes (make-node :diagnosis "Anterograde Amnesia")
           :no  (make-node :diagnosis "Retrograde Amnesia"))
    :no  (make-node 
           :question "Sudden complete loss of identity?"
           :yes (make-node :diagnosis "Psychogenic Fugue")
           :no  (make-node 
                  :question "Invents false memories and believes them?"
                  :yes (make-node :diagnosis "Confabulation")
                  :no  (make-node :diagnosis "Other type")))))

(defun diagnose (node)
  (if (node-diagnosis node)
      (progn
        (format t "~%")
        (format t "----------~%")
        (format t "DIAGNOSIS:~%")
        (format t "~A~%" (node-diagnosis node))
        (format t "----------~%~%"))
      (progn
        (format t "~A~%" (node-question node))
        (format t "(yes/no): ")
        (force-output)
        (let ((ans (string-trim " " (read-line))))
          (cond ((or (string-equal ans "yes")
                     (string-equal ans "y"))
                 (diagnose (node-yes node)))
                ((or (string-equal ans "no")
                     (string-equal ans "n"))
                 (diagnose (node-no node)))
                (t 
                 (format t "~%Answer yes or no only~%~%")
                 (diagnose node)))))))

(format t "answerr yes or no ~%")
(format t "~%~%")
(force-output)
(diagnose *tree*)