"""
Big CSters matching script

This automates the matching and email generation for the Big CSters mentorship program: 
- creates matches between mentors and mentees 
- let's you experiment with generating matches from different algorithms, you can customize weightings in match.py
- optionally: sends emails to the participants.

Usage:
  python big_csters.py [options]
  
Options:
  --mentor-csv FILE       Path to mentor CSV file (default: Big_CSters_Mentor_Responses.csv)
  --mentee-csv FILE       Path to mentee CSV file (default: Big_CSters_Mentee_Responses.csv)
  --algorithm ALGORITHM   Matching algorithm to use (default: weighted), options: greedy, weighted, stable, gata-mixed, ortools
  --send-emails           Actually send emails (default: doesn't send)
  --evaluate-all          Compare all matching algorithms

Example: python big_csters.py --algorithm weighted
"""

import argparse
import sys

from parse import parse_csv_files, Mentor, Mentee
from match import match_mentors_and_mentees, evaluate_matches
from email_sender import send_match_emails


def run_matching(mentor_csv: str, mentee_csv: str, algorithm: str = "weighted", send_emails: bool = False) -> None:
    """
    Args:
        mentor_csv: Path to the mentor CSV file
        mentee_csv: Path to the mentee CSV file
        algorithm: Matching algorithm to use
        send_emails: Whether to actually send emails
    """
    print(f"Processing mentor data from: {mentor_csv}")
    print(f"Processing mentee data from: {mentee_csv}")
    
    # Parse CSV data into lists of mentor and mentee objects
    mentors, mentees = parse_csv_files(mentor_csv, mentee_csv)
    
    print(f"Num mentors: {len(mentors)}, num mentees: {len(mentees)}")
    
    # Match mentors and mentees
    matches = match_mentors_and_mentees(mentors, mentees, algorithm=algorithm)
    print(f"Created {len(matches)} matches")
    
    # Evaluate match quality
    metrics = evaluate_matches(matches)
    print(f"Match quality metrics:")
    print(f"Average score: {metrics['avg_score']:.2f}")
    print(f"Minimum score: {metrics['min_score']:.2f}")
    print(f"Maximum score: {metrics['max_score']:.2f}")
    
    # Find unmatched mentees
    unmatched_mentees = [m for m in mentees if not m.matched]
    if unmatched_mentees:
        print("WARNING:", len(unmatched_mentees), "mentees could not be matched:")
        for mentee in unmatched_mentees:
            print({mentee.name},({mentee.email}))
    
    # Print matches
    print("Matches:")
    for mentor, mentee in matches:
        print("Mentor:", {mentor.name}, {mentor.email}," - ", {mentee.name},{mentee.email})
    
    # Send emails
    if matches:
        print("send emails")
        # send_match_emails(matches, send_emails=send_emails)


def compare_algorithms(mentor_csv: str, mentee_csv: str) -> None:
    """
    Compare all matching algorithms.
    
    Args:
        mentor_csv: Path to the mentor CSV file
        mentee_csv: Path to the mentee CSV file
    """
    print(f"Processing mentor data from: {mentor_csv}")
    print(f"Processing mentee data from: {mentee_csv}")
    
    # Parse CSV data
    original_mentors, original_mentees = parse_csv_files(mentor_csv, mentee_csv)
    
    algorithms = ["greedy", "weighted", "stable", "random"]
    results = {}
    
    print("\nComparing matching algorithms:")
    for algo in algorithms:
        print(f"\n{algo.upper()} MATCHING:")
        
        # Create copies of the data to avoid state interference
        mentors = [Mentor(
            name=m.name,
            email=m.email,
            pronouns=m.pronouns,
            program=m.program,
            term=m.term,
            location=m.location,
            meeting_preference=m.meeting_preference,
            topics=m.topics.copy(),
            career_topics=m.career_topics.copy(),
            max_mentees=m.max_mentees
        ) for m in original_mentors]
        
        mentees = [Mentee(
            name=m.name,
            email=m.email,
            pronouns=m.pronouns,
            program=m.program,
            term=m.term,
            location=m.location,
            meeting_preference=m.meeting_preference,
            topics=m.topics.copy(),
            career_topics=m.career_topics.copy()
        ) for m in original_mentees]
        
        # Match and evaluate
        matches = match_mentors_and_mentees(mentors, mentees, algorithm=algo)
        metrics = evaluate_matches(matches)
        
        # Store results
        results[algo] = {
            "matches": len(matches),
            "metrics": metrics,
            "unmatched": sum(1 for m in mentees if not m.matched)
        }
        
        # Print results
        print(f"Created {len(matches)} matches")
        print(f"Avg score: {metrics['avg_score']:.2f}, Min: {metrics['min_score']:.2f}, Max: {metrics['max_score']:.2f}")
        print(f"Unmatched mentees: {sum(1 for m in mentees if not m.matched)}")
    
    # Print comparison table
    print("\nALGORITHM COMPARISON:")
    print(f"{'Algorithm':<10} {'Matches':<10} {'Avg Score':<12} {'Min Score':<12} {'Max Score':<12} {'Unmatched':<10}")
    print("-" * 70)
    
    for algo, data in results.items():
        print(f"{algo:<10} {data['matches']:<10} {data['metrics']['avg_score']:.2f}{' ' * 8} "
              f"{data['metrics']['min_score']:.2f}{' ' * 8} {data['metrics']['max_score']:.2f}{' ' * 8} "
              f"{data['unmatched']:<10}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Big CSters Matching and Email Automation")
    parser.add_argument("--mentor-csv", default="Big_CSters_Mentor_Responses.csv")
    parser.add_argument("--mentee-csv", default="Big_CSters_Mentee_Responses.csv")
    parser.add_argument("--algorithm", default="weighted",
                        choices=["greedy", "weighted", "stable", "random"])
    parser.add_argument("--send-emails", action="store_true")
    parser.add_argument("--evaluate-all", action="store_true")
    
    args = parser.parse_args()
    
    if args.evaluate_all:
        compare_algorithms(args.mentor_csv, args.mentee_csv)
    else:
        run_matching(args.mentor_csv, args.mentee_csv, args.algorithm, args.send_emails)
