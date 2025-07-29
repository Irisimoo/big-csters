import csv
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

# mappings [CHANGED BASED ON GOOGLE FORM CSV STRUCTURE]
COLUMN_MAPPINGS = {
    "mentor": {
        "timestamp": 0,
        "email": 1,              # Email column
        "name": 2,               # Name column
        "pronouns": 3,           # Pronouns column
        "program": 4,            # Program column
        "term": 5,               # Term column
        "in_waterloo": 6,        # Whether in Waterloo
        "prefer_in_person": 7,   # Prefers in-person meeting
        "topics": 8,             # Mentorship topics
        "career_topics": 9,      # Career topics
        "max_mentees": 10,       # Maximum mentees
        "comments": 11           # Comments field
    },
    "mentee": {
        "timestamp": 0,
        "email": 1,              # Email column
        "name": 2,               # Name column
        "pronouns": 3,           # Pronouns column
        "program": 4,            # Program column
        "term": 5,               # Term column
        "in_waterloo": 6,        # Whether in Waterloo
        "prefer_in_person": 7,   # Prefers in-person meeting
        "topics": 8,             # Mentorship topics
        "career_topics": 9,      # Career topics
        "comments": 10           # Comments field
    }
}


# Mentor and mentee classes
@dataclass
class Person:
    name: str
    email: str
    pronouns: str
    program: str
    term: str
    location: str  # Location (Waterloo, other city, or None if prefer not to say)
    meeting_preference: str  # "in-person", "online", "no preference"
    topics: List[str]
    career_topics: List[str]

    @property
    def first_name(self) -> str:
        """Get the person's first name."""
        return self.name.split()[0] if self.name else ""


@dataclass
class Mentee(Person):
    matched: bool = False
    mentor: Optional['Mentor'] = None


@dataclass
class Mentor(Person):
    max_mentees: int = 1
    current_mentees: List[Mentee] = None

    def __post_init__(self):
        if self.current_mentees is None:
            self.current_mentees = []

    @property
    def available_slots(self) -> int:
        """Get number of available mentee slots."""
        return self.max_mentees - len(self.current_mentees)

    def add_mentee(self, mentee: Mentee) -> bool:
        """Add a mentee to this mentor if space available."""
        if self.available_slots > 0:
            self.current_mentees.append(mentee)
            mentee.matched = True
            mentee.mentor = self
            return True
        return False

# PARSE CSV
def parse_csv_data(file_path: str, skip_header: bool = True) -> List[List[str]]:
    """
    Parse CSV data from file.
    Args:
        file_path: Path to the CSV file
        skip_header: Whether to skip the header row
    Returns:
        List of rows, where each row is a list of strings
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Skip header row if needed
        if skip_header:
            next(reader, None)
            
        return list(reader)


def parse_location(value: str) -> str:
    """
    Parse location from response.
    Args:
        value: String value from the location question
               "Are you based in Waterloo this term? If not, which city are you based in?"
    Returns:
        Location string: "Waterloo", city name, or "Unknown" if prefer not to say
    """
    if not value:
        return "Unknown"
    
    value = value.strip().lower()
    
    if value == "yes":
        return "Waterloo"
    elif "no (and prefer not to say)" in value:
        return "Unknown"
    elif value.startswith("no"):
        return "Not Waterloo"
    else:
        # It's likely a city name, return as is with proper capitalization
        return value.title()


def parse_meeting_preference(value: str) -> str:
    """
    Parse meeting preference from response.
    Args:
        value: String value from the preference question
               "Would you prefer to match with a mentor/mentee you can meet up with in person?"
    Returns:
        Preference string: "in-person", "online", or "no preference"
    """
    if not value:
        return "no preference"
    
    value = value.strip().lower()
    
    if "yes" in value and "in person" in value:
        return "in-person"
    elif "no" in value and "online" in value:
        return "online"
    else:
        return "no preference"


def parse_list(value: str, delimiter: str = ",") -> List[str]:
    """
    Parse a comma-separated string into a list of strings.
    Args:
        value: Comma-separated string
        delimiter: Delimiter character (default is comma)
    Returns:
        List of trimmed strings
    """
    if not value:
        return []
    
    return [item.strip() for item in value.split(delimiter)]


def create_mentees(data: List[List[str]], column_map: Dict[str, int] = None) -> List[Mentee]:
    """
    Create mentee objects from parsed CSV data.
    Args:
        data: List of rows from CSV
        column_map: Dictionary mapping field names to column indices
    Returns:
        List of Mentee objects
    """
    if column_map is None:
        column_map = COLUMN_MAPPINGS["mentee"]
        
    mentees = []
    
    for row in data:
        # Skip empty rows or rows without enough columns
        if not row or len(row) <= max(column_map.values()):
            continue
            
        try:
            # Extract data using column mappings
            email = row[column_map["email"]]
            name = row[column_map["name"]]
            pronouns = row[column_map["pronouns"]]
            program = row[column_map["program"]]
            term = row[column_map["term"]]
            location = parse_location(row[column_map["in_waterloo"]])
            meeting_preference = parse_meeting_preference(row[column_map["prefer_in_person"]])
            topics = parse_list(row[column_map["topics"]])
            career_topics = parse_list(row[column_map["career_topics"]])
            
            mentee = Mentee(
                name=name,
                email=email,
                pronouns=pronouns,
                program=program,
                term=term,
                location=location,
                meeting_preference=meeting_preference,
                topics=topics,
                career_topics=career_topics
            )
            mentees.append(mentee)
            
        except (IndexError, ValueError) as e:
            print(f"Error parsing mentee row: {e}")
            print(f"Row data: {row}")
            continue
    
    return mentees

def create_mentors(data: List[List[str]], column_map: Dict[str, int] = None) -> List[Mentor]:
    """
    Create mentor objects from parsed CSV data.
    Args:
        data: List of rows from CSV
        column_map: Dictionary mapping field names to column indices
    Returns:
        List of Mentor objects
    """
    if column_map is None:
        column_map = COLUMN_MAPPINGS["mentor"]
        
    mentors = []
    
    for row in data:
        # Skip empty rows or rows without enough columns
        if not row or len(row) <= max(column_map.values()):
            continue
            
        try:
            # Extract data using column mappings
            email = row[column_map["email"]]
            name = row[column_map["name"]]
            pronouns = row[column_map["pronouns"]] if "pronouns" in column_map and column_map["pronouns"] < len(row) else ""
            program = row[column_map["program"]]
            term = row[column_map["term"]]
            location = parse_location(row[column_map["in_waterloo"]])
            meeting_preference = parse_meeting_preference(row[column_map["prefer_in_person"]])
            topics = parse_list(row[column_map["topics"]])
            career_topics = parse_list(row[column_map["career_topics"]])
            
            # Get max mentees (default to 1 if not specified or invalid)
            try:
                max_mentees = int(row[column_map["max_mentees"]])
            except (IndexError, ValueError):
                max_mentees = 1
            
            mentor = Mentor(
                name=name,
                email=email,
                pronouns=pronouns,
                program=program,
                term=term,
                location=location,
                meeting_preference=meeting_preference,
                topics=topics,
                career_topics=career_topics,
                max_mentees=max_mentees
            )
            mentors.append(mentor)
            
        except (IndexError, ValueError) as e:
            print(f"Error parsing mentor row: {e}")
            print(f"Row data: {row}")
            continue
    
    return mentors


def parse_csv_files(mentor_file: str, mentee_file: str) -> Tuple[List[Mentor], List[Mentee]]:
    """
    Parse both mentor and mentee CSV files.
    Args:
        mentor_file: Path to the mentor CSV file
        mentee_file: Path to the mentee CSV file
    Returns:
        Tuple of (mentors, mentees) lists
    """
    print(f"Parsing mentor file: {mentor_file}")
    mentor_data = parse_csv_data(mentor_file)
    mentors = create_mentors(mentor_data)
    
    print(f"Parsing mentee file: {mentee_file}")
    mentee_data = parse_csv_data(mentee_file)
    mentees = create_mentees(mentee_data)
    
    print(f"Successfully parsed {len(mentors)} mentors and {len(mentees)} mentees")
    return mentors, mentees


# before csv implemented
def parse_raw_data(mentor_data_raw: str, mentor_emails_raw: str, 
                   mentee_data_raw: str, mentee_emails_raw: str) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """
    Parse raw string data for mentors and mentees.
    This is used for compatibility with the old script format.
    Args:
        mentor_data_raw: String with tab-separated mentor data
        mentor_emails_raw: String with mentor emails
        mentee_data_raw: String with tab-separated mentee data
        mentee_emails_raw: String with mentee emails
    Returns:
        Dictionaries of mentor and mentee data
    """
    def parse_people_data(data_string: str, email_string: str) -> Dict[str, Dict]:
        """Parses tab-separated data and email data for mentors or mentees."""
        people = {}
        data_lines = data_string.strip().split('\n')
        email_lines = email_string.strip().split('\n')

        # Use csv module to handle tab-separated values robustly
        data_reader = csv.reader([line.strip() for line in data_lines if line.strip()], delimiter='\t')

        for row, email in zip(data_reader, email_lines):
            # Handle rows with missing pronoun column
            if len(row) >= 4:
                name, pronouns, program, term = [item.strip() for item in row[:4]]
            elif len(row) == 3:
                name, program, term = [item.strip() for item in row[:3]]
                pronouns = ""  # Assign empty string if pronouns are missing
            else:
                continue

            people[name] = {
                "name": name,
                "pronouns": pronouns,
                "program": program,
                "term": term,
                "email": email.strip()
            }
        return people
    
    mentors = parse_people_data(mentor_data_raw, mentor_emails_raw)
    mentees = parse_people_data(mentee_data_raw, mentee_emails_raw)
    
    return mentors, mentees


# For testing the parser directly
if __name__ == "__main__":
    mentor_file = "Big_CSters_Mentor_Responses.csv"
    mentee_file = "Big_CSters_Mentee_Responses.csv"
    
    try:
        mentors, mentees = parse_csv_files(mentor_file, mentee_file)
        
        print("\nMentor Information:")
        for i, mentor in enumerate(mentors[:3]): 
            print(f"{i+1}. {mentor.name} - {mentor.email} - {mentor.program} {mentor.term}")
            print(f"   Topics: {', '.join(mentor.topics)}")
            print(f"   Career topics: {', '.join(mentor.career_topics)}")
            print(f"   Max mentees: {mentor.max_mentees}")
        
        print("\nMentee Information:")
        for i, mentee in enumerate(mentees[:3]): 
            print(f"{i+1}. {mentee.name} - {mentee.email} - {mentee.program} {mentee.term}")
            print(f"   Topics: {', '.join(mentee.topics)}")
            print(f"   Career topics: {', '.join(mentee.career_topics)}")
            
    except Exception as e:
        print(f"Error testing parser: {e}")
