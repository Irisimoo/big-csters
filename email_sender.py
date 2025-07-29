import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional, Tuple, Union


# Email Templates
MENTOR_EMAIL_TEMPLATE = """
Hello {mentor_first_name}!

You have both been matched for our Big CSters Mentorship Program!
Mentee: {mentee_name} ({mentee_email}), {mentee_term} {mentee_program}

We suggest introducing yourselves, swapping contact info, and setting up a time to meet either in person or virtually! To help you with your mentorship we have put together a mentor guide so feel free to take a look here: https://docs.google.com/document/d/1gmp7XHnBKb-nPnfCGqXIUzEDbStrTtDL_r9XEBclhs0/edit?usp=sharing

Thank you for signing up to be a Big CSter mentor this term!

If you have any questions feel free to reach out,
UWaterloo WiCS Undergrad Committee
"""

MENTEE_EMAIL_TEMPLATE = """
Hello {mentee_first_name}!

You have both been matched for our Big CSters Mentorship Program!
Mentor: {mentor_name} ({mentor_email}), {mentor_term} {mentor_program}

We suggest introducing yourselves, swapping contact info, and setting up a time to meet either in person or virtually! To help you with your mentorship we have put together a mentee guide so feel free to take a look here: https://docs.google.com/document/d/1FsxEdrliNDqAhB1B5ApQMuIV4bd0FmM6e6Pazlg1pnA/edit?usp=sharing

Thank you for signing up to be a Big CSter mentee this term!

If you have any questions feel free to reach out,
UWaterloo WiCS Undergrad Committee
"""


# Email Configuration 
# obviously fill out with wics undergrad email before sending
EMAIL_CONFIG = {
    "sender_email": "",
    "sender_password": "", 
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_name": "WiCS Undergraduate Committee"
}

def generate_emails(matches: List[Dict[str, Any]]) -> None:
    """
    Generates and prints emails for mentors and mentees based on templates.

    Args:
        matches: A list of dictionaries, where each dictionary contains 'mentor' and 'mentee' info
    """
    for i, match in enumerate(matches):
        mentor = match["mentor"]
        mentee = match["mentee"]

        # Generate mentor email
        mentor_email = MENTOR_EMAIL_TEMPLATE.format(
            mentor_first_name=mentor["name"].split()[0],
            mentee_name=mentee["name"],
            mentee_email=mentee["email"],
            mentee_term=mentee["term"],
            mentee_program=mentee["program"]
        )

        # Generate mentee email
        mentee_email = MENTEE_EMAIL_TEMPLATE.format(
            mentee_first_name=mentee["name"].split()[0],
            mentor_name=mentor["name"],
            mentor_email=mentor["email"],
            mentor_term=mentor["term"],
            mentor_program=mentor["program"]
        )

        print(f"Match {i+1}: {mentor['name']}, {mentee['name']}")
        print("For Mentor: " + mentor["name"] + " ---")
        print(mentor_email)
        print("For Mentee: " + mentee["name"] + " ---")
        print(mentee_email)


def generate_email_content(mentor: Dict[str, Any], mentee: Dict[str, Any]) -> Tuple[str, str, str, str]:
    """
    Generate email subject and content for both mentor and mentee.
    
    Args:
        mentor: Dictionary containing mentor information
        mentee: Dictionary containing mentee information
        
    Returns:
        Tuple of (mentor_subject, mentor_content, mentee_subject, mentee_content)
    """
    # Mentor email
    mentor_subject = "Big CSters Mentorship Match"
    mentor_content = MENTOR_EMAIL_TEMPLATE.format(
        mentor_first_name=mentor["name"].split()[0],
        mentee_name=mentee["name"],
        mentee_email=mentee["email"],
        mentee_term=mentee["term"],
        mentee_program=mentee["program"]
    )
    
    # Mentee email
    mentee_subject = "Big CSters Mentorship Match"
    mentee_content = MENTEE_EMAIL_TEMPLATE.format(
        mentee_first_name=mentee["name"].split()[0],
        mentor_name=mentor["name"],
        mentor_email=mentor["email"],
        mentor_term=mentor["term"],
        mentor_program=mentor["program"]
    )
    
    return mentor_subject, mentor_content, mentee_subject, mentee_content


def send_email(recipient_email: str, subject: str, content: str) -> bool:
    """
    Send an email to a recipient.
    
    Args:
        recipient_email: Email address of the recipient
        subject: Subject line of the email
        content: Body content of the email
        
    Returns:
        Boolean indicating whether the email was sent successfully
    """
    if not EMAIL_CONFIG["sender_email"] or not EMAIL_CONFIG["sender_password"]:
        print("Email credentials not configured. Please update EMAIL_CONFIG in email.py.")
        return False
    
    message = MIMEMultipart()
    message["From"] = f"{EMAIL_CONFIG['sender_name']} <{EMAIL_CONFIG['sender_email']}>"
    message["To"] = recipient_email
    message["Subject"] = subject
    
    message.attach(MIMEText(content, "plain"))
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
            server.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {e}")
        return False


def send_match_emails(matches: List[Dict[str, Any]], send_emails: bool = True) -> None:
    """
    Args:
        matches: List of dictionaries containing mentor and mentee matches
        send_emails: If True, emails will be sent, if not will only be printed
    """
    for mentor_obj, mentee_obj in matches:
        # Convert to dictionary format if needed (for compatibility with different object types)
        mentor = mentor_obj if isinstance(mentor_obj, dict) else mentor_obj.__dict__
        mentee = mentee_obj if isinstance(mentee_obj, dict) else mentee_obj.__dict__
        
        mentor_subject, mentor_content, mentee_subject, mentee_content = generate_email_content(mentor, mentee)
        
        if not send_emails:
            # just print           
            print("For Mentor: " + mentor["name"] + " ---")
            print("Subject", mentor_subject)
            print(mentor_content)
            print("For Mentee: " + mentee["name"] + " ---")
            print("Subject", mentee_subject)
            print(mentee_content)
        else:
            # acutally send
            print(f"Sending email to mentor: {mentor['name']} <{mentor['email']}>")
            mentor_success = send_email(mentor['email'], mentor_subject, mentor_content)
            
            print(f"Sending email to mentee: {mentee['name']} <{mentee['email']}>")
            mentee_success = send_email(mentee['email'], mentee_subject, mentee_content)
            
            if mentor_success and mentee_success:
                print(f"Successfully sent emails for match: {mentor['name']} - {mentee['name']}")
            else:
                print(f"Error sending one or more emails for match: {mentor['name']} - {mentee['name']}")
