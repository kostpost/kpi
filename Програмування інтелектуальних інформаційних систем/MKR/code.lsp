(defparameter *data*
  '((30 2 60000)
    (35 5 75000)
    (28 1 55000)
    (45 10 95000)
    (40 8 85000)
    (50 15 110000)
    (32 3 68000)
    (38 6 78000)
    (42 9 90000)
    (55 20 120000)))

(defparameter *a* 1500)   
(defparameter *b* 20000)  

(defun g (experience)
  "Returns the average salary of the 3 closest employees by experience"
  (let* ((distances (mapcar (lambda (row)
                              (cons (abs (- experience (second row))) (third row)))
                            *data*))
         (sorted (sort distances #'< :key #'car))           
         (nearest (subseq sorted 0 (min 3 (length sorted)))) 
         (salaries (mapcar #'cdr nearest)))
    (if (zerop (length salaries))
        0
        (/ (reduce #'+ salaries) (length salaries)))))

(defun predict (age experience)
  "Returns salary prediction"
  (+ (* *a* age) *b* (g experience)))

(format t "Prediction for age 36, experience 4: ~A~%" (predict 36 4))
(format t "Prediction for age 48, experience 12: ~A~%" (predict 48 12))
(format t "Prediction for age 29, experience 1: ~A~%" (predict 29 1))