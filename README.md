# Big CSters Mentorship Matching

The big_csters script automates the matching and email generation for the Big CSters mentorship program. Features: 
- Parse mentor and mentee information from CSV files (download directly from google form)
- Experiment with generating matches from different matching algorithms, you can customize weightings in match.py (greedy, weighted bipartite matching, stable matching, gata-mixed (optimal + stability + priority), integer linear programming)
- Compare different matching algorithms
- Generate email templates for mentors and mentees
- Optional email sending functionality

## Setup

### 1. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Add the CSV response files `Big_CSters_Mentor_Responses.csv` and `Big_CSters_Mentee_Responses.csv`. Then run:

```bash
python big_csters.py
```

### Command-Line Options

```bash
python big_csters.py --mentor-csv [MENTOR_FILE] --mentee-csv [MENTEE_FILE] --algorithm [ALGORITHM]
```

- `--mentor-csv`: Path to the mentor CSV file (default: Big_CSters_Mentor_Responses.csv)
- `--mentee-csv`: Path to the mentee CSV file (default: Big_CSters_Mentee_Responses.csv)
- `--algorithm`: Matching algorithm to use (options: greedy, weighted, stable, random)
- `--send-emails`: Include this flag to actually send emails (by default, it will only print them)
- `--evaluate-all`: Compare all matching algorithms

### Example

```bash
# Run with weighted algorithm (default)
python big_csters.py

# Compare all algorithms
python big_csters.py --evaluate-all

# Use stable matching algorithm
python big_csters.py --algorithm stable

# Use custom CSV files
python big_csters.py --mentor-csv my_mentors.csv --mentee-csv my_mentees.csv
```

## CSV File Format

The program expects CSV files with the following columns (based on S25 google form):

### Mentor CSV
- Email
- Name
- Pronouns
- Program
- Term
- Location (Are you based in Waterloo this term? If not, which city are you based in?)
- Meeting Preference (Would you prefer to meet in person or online?)
- Topics (Mentorship topics)
- Career topics
- Max mentees (Maximum number of mentees to be assigned)

### Mentee CSV
- Email
- Name
- Pronouns
- Program
- Term
- Location (Are you based in Waterloo this term? If not, which city are you based in?)
- Meeting Preference (Would you prefer to meet in person or online?)
- Topics (Mentorship topics)
- Career topics

## Customization

- Matching weights can be adjusted in the `calculate_match_score` function in `match.py`
- Email templates can be modified in `email_sender.py`
