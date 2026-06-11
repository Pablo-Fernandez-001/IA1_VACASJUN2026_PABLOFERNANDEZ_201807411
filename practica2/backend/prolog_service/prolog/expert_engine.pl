:- use_module(library(http/json)).
:- dynamic selected/1.
:- dynamic diagnosis/6.
:- dynamic rule/5.
:- dynamic required_symptom/2.

is_selected(S) :- selected(S).

count_matched([], [], 0).
count_matched([H|T], [H|MT], Count) :-
    is_selected(H), !,
    count_matched(T, MT, Rest),
    Count is Rest + 1.
count_matched([_|T], MT, Count) :-
    count_matched(T, MT, Count).

missing_symptoms([], []).
missing_symptoms([H|T], Missing) :-
    is_selected(H), !,
    missing_symptoms(T, Missing).
missing_symptoms([H|T], [H|MT]) :-
    missing_symptoms(T, MT).

problem_level(Probability, bajo) :- Probability < 35, !.
problem_level(Probability, medio) :- Probability < 70, !.
problem_level(_, alto).

diagnostic_result(json([
    diagnosis_id=DiagnosisId,
    name=Name,
    category=Category,
    message=Message,
    rule_id=RuleId,
    rule_name=RuleName,
    explanation=Explanation,
    probability=Rounded,
    problem_level=Level,
    matched=Matched,
    total_required=Total,
    matched_symptoms=MatchedSymptoms,
    missing_symptoms=MissingSymptoms,
    solution_route=Route
])) :-
    rule(RuleId, DiagnosisId, RuleName, Weight, Explanation),
    diagnosis(DiagnosisId, Name, Category, Message, Route, Base),
    findall(S, required_symptom(RuleId, S), Required),
    length(Required, Total),
    Total > 0,
    count_matched(Required, MatchedSymptoms, Matched),
    Matched > 0,
    missing_symptoms(Required, MissingSymptoms),
    Raw is (Matched / Total) * Weight * (Base / 100),
    Rounded is round(Raw),
    problem_level(Rounded, Level).

main :-
    findall(Result, diagnostic_result(Result), Results),
    reply_json(json([diagnostics=Results])).
