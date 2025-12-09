:- encoding(utf8).

% --------------------- Symptoms facts ---------------------
symptom(anterograde, cannot_remember_after_onset).
symptom(anterograde, remembers_before_onset).

symptom(retrograde, cannot_remember_before_onset).
symptom(retrograde, remembers_after_onset).
symptom(retrograde, often_after_head_injury).

symptom(fixation, cannot_fix_current_events).
symptom(fixation, confabulations).
symptom(fixation, short_term_memory_impairment).

symptom(dissociative_fugue, loss_of_personal_identity).
symptom(dissociative_fugue, forgot_who_he_is).
symptom(dissociative_fugue, may_start_new_life).
symptom(dissociative_fugue, after_severe_stress).

% --------------------- Diagnosis rules ---------------------
diagnosis(Type) :-
    symptom(Type, Main1), ask(Main1, yes),
    symptom(Type, Main2), ask(Main2, yes),
    \+ (other_type(Type, Other), enough_for(Other)),
    write('Most likely diagnosis: '), write(Type), nl.

other_type(anterograde, retrograde).
other_type(retrograde, anterograde).
other_type(fixation, _).
other_type(dissociative_fugue, _).
other_type(_, fixation).
other_type(_, dissociative_fugue).

% Another type has enough symptoms — it takes priority
enough_for(Type) :-
    symptom(Type, S1), ask(S1, yes),
    symptom(Type, S2), ask(S2, yes).

% --------------------- Interactive questions ---------------------
ask(Question, Answer) :-
    known(Question, Answer), !.

ask(cannot_remember_after_onset, Answer) :-
    ask_q("Patient cannot remember events that occurred AFTER the onset of the disorder? (yes/no)", Answer).
ask(remembers_before_onset, Answer) :-
    ask_q("Patient clearly remembers everything that happened BEFORE the onset? (yes/no)", Answer).

ask(cannot_remember_before_onset, Answer) :-
    ask_q("Patient cannot recall events that happened BEFORE the onset? (yes/no)", Answer).
ask(remembers_after_onset, Answer) :-
    ask_q("Patient normally remembers everything that happened AFTER the onset? (yes/no)", Answer).
ask(often_after_head_injury, Answer) :-
    ask_q("Did the amnesia appear after a head injury or concussion? (yes/no)", Answer).

ask(cannot_fix_current_events, Answer) :-
    ask_q("Patient cannot retain current events even for a few minutes? (yes/no)", Answer).
ask(confabulations, Answer) :-
    ask_q("Does the patient make up false memories (confabulation)? (yes/no)", Answer).

ask(loss_of_personal_identity, Answer) :-
    ask_q("Patient does not know who he is, forgot name and biography? (yes/no)", Answer).
ask(forgot_who_he_is, Answer) :- ask(loss_of_personal_identity, Answer).

ask(may_start_new_life, Answer) :-
    ask_q("Has the patient left home and started (or could start) a new life elsewhere? (yes/no)", Answer).
ask(after_severe_stress, Answer) :-
    ask_q("Did the amnesia occur after severe emotional shock or stress? (yes/no)", Answer).

% --------------------- Helper predicates ---------------------
ask_q(Question, Answer) :-
    format("~w~nAnswer (yes/no): ", [Question]),
    read(Input),
    (   Input = yes  -> Answer = yes
    ;   Input = no   -> Answer = no
    ;   write("Please answer 'yes' or 'no'.\n"), ask_q(Question, Answer)
    ),
    assert(known(Question, Answer)).

% Clear memory and start diagnosis
start :-
    retractall(known(_,_)),
    nl, write("=== Amnesia Type Diagnosis ===\n\n"),
    (   diagnosis(Type)
    ->  true
    ;   write("Could not determine the exact type of amnesia with the given data.\n")
    ),
    nl.

% --------------------- Auto start ---------------------
:- start.