from typing import List, Dict, Any, Tuple, Optional, Callable
from parse import Mentor, Mentee

import random
import numpy as np
from scipy.optimize import linear_sum_assignment
from ortools.sat.python import cp_model
import networkx as nx

# shared compute score
# [CUSTOMIZE BASED ON WHAT YOU PRIORITIZE]
def compute_score(mentor: Any, mentee: Any) -> float:
    """
    Calculate a match score between a mentor and mentee. Higher score = better match
    Args:
        mentor: Mentor object or dictionary
        mentee: Mentee object or dictionary
        
    Returns:
        Float score representing match quality
    """
    score = 0.0
    
    m_dict = mentor if isinstance(mentor, dict) else mentor.__dict__
    e_dict = mentee if isinstance(mentee, dict) else mentee.__dict__
    
    # Meeting preference matching
    mentor_pref = m_dict.get('meeting_preference', 'no preference')
    mentee_pref = e_dict.get('meeting_preference', 'no preference')
    mentor_location = m_dict.get('location', 'Unknown')
    mentee_location = e_dict.get('location', 'Unknown')
    
    # If both prefer in-person and are in the same location
    if (mentor_pref == "in-person" and mentee_pref == "in-person" and 
        mentor_location == mentee_location and mentor_location != "Unknown"):
        score += 10.0
    # If both prefer online meetings
    elif mentor_pref == "online" and mentee_pref == "online":
        score += 8.0
    # If one has no preference and the other has a preference, somewhat match that preference
    elif (mentor_pref == "no preference" and mentee_pref != "no preference") or (mentee_pref == "no preference" and mentor_pref != "no preference"):
        score += 5.0
    # If both have no preference
    elif mentor_pref == "no preference" and mentee_pref == "no preference":
        score += 5.0
    
    # Topic matches (mentorship areas)
    mentor_topics = m_dict.get('topics', [])
    mentee_topics = e_dict.get('topics', [])
    
    for topic in mentee_topics:
        if topic in mentor_topics:
            score += 5.0
    
    # Career topic matches (weighted higher)
    mentor_career = m_dict.get('career_topics', [])
    mentee_career = e_dict.get('career_topics', [])
    
    for topic in mentee_career:
        if topic in mentor_career:
            score += 4.0
    
    # Program matches
    if m_dict.get('program', '') == e_dict.get('program', ''):
        score += 5.0
    
    # Mentor's term is higher than mentee's (if both are numeric terms)
    try:
        mentor_term = m_dict.get('term', '')
        mentee_term = e_dict.get('term', '')
        
        mentor_term_num = int(mentor_term[0]) if mentor_term and mentor_term[0].isdigit() else 0
        mentee_term_num = int(mentee_term[0]) if mentee_term and mentee_term[0].isdigit() else 0
        
        if mentor_term_num > mentee_term_num:
            score += 20.0
        elif "graduate" in mentor_term.lower():
            score += 20.0
    except (IndexError, ValueError):
        pass  # Skip if terms aren't in expected format
    
    return score


def greedy_matching(mentors: List[Any], mentees: List[Any]) -> List[Tuple[Any, Any]]:
    """
    Simple greedy matching algorithm. Sorts mentees by some criteria and assigns them to mentors one by one.
    Pretty bad btw 
    """
    matches = []
    available_mentees = mentees.copy()
    
    # Sort mentors by available slots (prioritize mentors with fewer slots)
    sorted_mentors = sorted(
        mentors, 
        key=lambda m: getattr(m, 'available_slots', 1) if not isinstance(m, dict) else 1
    )
    
    for mentor in sorted_mentors:
        # Skip mentors with no available slots
        available_slots = getattr(mentor, 'available_slots', 1) if not isinstance(mentor, dict) else 1
        if available_slots <= 0:
            continue
        
        # Calculate scores for all available mentees with this mentor
        mentee_scores = [
            (mentee, compute_score(mentor, mentee)) 
            for mentee in available_mentees
        ]
        
        # Sort by score (highest first)
        mentee_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Match top mentees up to available slots
        slots_to_fill = min(available_slots, len(mentee_scores))
        
        for i in range(slots_to_fill):
            if i < len(mentee_scores):
                mentee = mentee_scores[i][0]
                
                # Add match
                matches.append((mentor, mentee))
                available_mentees.remove(mentee)
                
                # Update mentor if it's an object
                if not isinstance(mentor, dict) and hasattr(mentor, 'add_mentee'):
                    mentor.add_mentee(mentee)
    
    return matches

# weighted bipartite matching (hungarian algorithm)
def match_mentors_and_mentees_weighted(mentors: List[Mentor], mentees: List[Mentee]) -> List[Tuple[Mentor, Mentee]]:
    G = nx.Graph()
    for i, mentor in enumerate(mentors):
        for j, mentee in enumerate(mentees):
            score = compute_score(mentor, mentee)
            if score > 0:
                for k in range(mentor.max_mentees):
                    # Give each mentor multiple virtual nodes
                    mentor_node = f"mentor_{i}_{k}"
                    mentee_node = f"mentee_{j}"
                    G.add_edge(mentor_node, mentee_node, weight=score)

    # Get max weight matching
    matching = nx.algorithms.matching.max_weight_matching(G, maxcardinality=True)

    matches = []
    used_mentees_emails = set()  # Track emails instead of objects

    for u, v in matching:
        if "mentor" in u:
            mentor_label, mentee_label = u, v
        else:
            mentor_label, mentee_label = v, u

        mentor_idx = int(mentor_label.split('_')[1])
        mentee_idx = int(mentee_label.split('_')[1])

        mentor = mentors[mentor_idx]
        mentee = mentees[mentee_idx]

        if mentee.email in used_mentees_emails:
            continue

        mentor.add_mentee(mentee)
        matches.append((mentor, mentee))
        used_mentees_emails.add(mentee.email)

    return matches

# stable matching algorithm (gale-shapley w/ capacities since 1-to-many mentor to mentee matches)
def match_mentors_and_mentees_stable(mentors: List[Mentor], mentees: List[Mentee]) -> List[Tuple[Mentor, Mentee]]:
    mentor_prefs = {mentor: sorted(mentees, key=lambda m: -compute_score(mentor, m)) for mentor in mentors}
    mentee_prefs = {mentee: sorted(mentors, key=lambda m: -compute_score(m, mentee)) for mentee in mentees}

    mentee_free = set(mentees)
    proposals = defaultdict(set)

    while mentee_free:
        mentee = mentee_free.pop()

        for mentor in mentee_prefs[mentee]:
            if mentor in proposals[mentee]:
                continue
            proposals[mentee].add(mentor)

            if mentor.available_slots > 0:
                mentor.add_mentee(mentee)
                break
            else:
                # Replace weakest mentee if new one is better
                worst = min(mentor.current_mentees, key=lambda m: compute_score(mentor, m))
                if compute_score(mentor, mentee) > compute_score(mentor, worst):
                    mentor.current_mentees.remove(worst)
                    worst.matched = False
                    worst.mentor = None
                    mentor.add_mentee(mentee)
                    mentee_free.add(worst)
                    break

    return [(mentor, mentee) for mentor in mentors for mentee in mentor.current_mentees]

# based on this: https://www.sciencedirect.com/science/article/pii/S2405844017336769#se0090
def match_mentors_and_mentees_gata_mixed(mentors: List[Mentor], mentees: List[Mentee]) -> List[Tuple[Mentor, Mentee]]:
    # Run max-weight bipartite matching to get optimal utility
    weighted_matches = match_mentors_and_mentees_weighted(mentors, mentees)

    # Convert list to lookup
    mentee_dict = {mentee.email: mentee for _, mentee in weighted_matches}
    mentor_dict = {mentor.email: mentor for mentor, _ in weighted_matches}

    # Stability enforcement pass
    for mentee in mentees:
        for mentor in mentors:
            if mentee.mentor and compute_score(mentor, mentee) > compute_score(mentee.mentor, mentee):
                # Stability violation: mentee prefers another mentor who has space or lower ranked mentee
                if mentor.available_slots > 0:
                    mentee.mentor.current_mentees.remove(mentee)
                    mentor.add_mentee(mentee)
                else:
                    worst = min(mentor.current_mentees, key=lambda m: compute_score(mentor, m))
                    if compute_score(mentor, mentee) > compute_score(mentor, worst):
                        mentor.current_mentees.remove(worst)
                        worst.matched = False
                        worst.mentor = None
                        mentee.mentor.current_mentees.remove(mentee)
                        mentor.add_mentee(mentee)

    return [(mentor, mentee) for mentor in mentors for mentee in mentor.current_mentees]

# wanted to try google or tools
def match_mentors_and_mentees_ortools(mentors: List[Mentor], mentees: List[Mentee]) -> List[Tuple[Mentor, Mentee]]:
    """
    Match using Google OR-Tools with mentor capacity constraints.
    """
    model = cp_model.CpModel()
    n_mentors = len(mentors)
    n_mentees = len(mentees)

    # Binary decision variables: match[i][j] = 1 if mentee j assigned to mentor i
    match = {}
    for i in range(n_mentors):
        for j in range(n_mentees):
            match[i, j] = model.NewBoolVar(f"match_m{i}_me{j}")

    # Each mentee is assigned to at most one mentor
    for j in range(n_mentees):
        model.Add(sum(match[i, j] for i in range(n_mentors)) <= 1)

    # Each mentor can take up to max_mentees[i]
    for i, mentor in enumerate(mentors):
        model.Add(sum(match[i, j] for j in range(n_mentees)) <= mentor.max_mentees)

    # Objective: maximize total compatibility score
    objective_terms = []
    for i in range(n_mentors):
        for j in range(n_mentees):
            score = compute_score(mentors[i], mentees[j])
            objective_terms.append(match[i, j] * score)

    model.Maximize(sum(objective_terms))

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    matches = []
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for i in range(n_mentors):
            for j in range(n_mentees):
                if solver.BooleanValue(match[i, j]):
                    mentors[i].add_mentee(mentees[j])
                    matches.append((mentors[i], mentees[j]))
    else:
        print("No feasible matching found.")

    return matches

def match_mentors_and_mentees(mentors, mentees, algorithm="weighted"):
    if algorithm == "ortools":
        return match_mentors_and_mentees_ortools(mentors, mentees)
    elif algorithm == "greedy":
        return greedy_matching(mentors, mentees)
    elif algorithm == "stable":
        return match_mentors_and_mentees_stable(mentors, mentees)
    elif algorithm == "gata-mixed":
        return match_mentors_and_mentees_gata_mixed(mentors, mentees)
    elif algorithm == "weighted":
        return match_mentors_and_mentees_weighted(mentors, mentees)
    else:
        # Default to greedy
        return greedy_matching(mentors, mentees)


def evaluate_matches(matches: List[Tuple[Any, Any]]) -> Dict[str, float]:
    if not matches:
        return {"avg_score": 0.0, "min_score": 0.0, "max_score": 0.0}
    
    scores = [compute_score(mentor, mentee) for mentor, mentee in matches]
    
    return {
        "avg_score": sum(scores) / len(scores),
        "min_score": min(scores),
        "max_score": max(scores)
    }
