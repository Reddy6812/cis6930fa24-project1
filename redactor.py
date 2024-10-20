import spacy
import re
import argparse
import os
import glob

# Load SpaCy model
nlp = spacy.load('en_core_web_sm')


# Redact Names (PERSON and ORG labels)
# Redact Names (PERSON and ORG labels)
def redact_names(doc):
    redacted_text = doc.text
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            redacted_text = redacted_text.replace(ent.text, '█' * len(ent.text))
    return redacted_text

#hardcode common names found in the body that may not be detected by SpaCy.
def redact_known_names(text):
    known_names = ['Laura Luce', 'Frank Vickers', 'Brian Redmond', 'Fred Lagrasta', 'Barry Tycholiz', 'Hunter Shively', 'John Arnold']
    for name in known_names:
        text = text.replace(name, '█' * len(name))
    return text



# Redact Dates
def redact_dates(doc):
    redacted_text = doc.text
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            redacted_text = redacted_text.replace(ent.text, '█' * len(ent.text))
    return redacted_text

# Redact Phone Numbers using Regex
def redact_phones(text):
    # Updated phone number pattern to catch multiple formats
    phone_pattern = r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4}|\d{4}[-.\s]?\d{3}[-.\s]?\d{4})'
    return re.sub(phone_pattern, '██████████', text)


# Redact Addresses (GPE: Geo-political entities)
def redact_address(doc):
    redacted_text = doc.text
    for ent in doc.ents:
        if ent.label_ == 'GPE':
            redacted_text = redacted_text.replace(ent.text, '█' * len(ent.text))
    return redacted_text
# Redact Email Addresses using Regex
def redact_emails(text):
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    return re.sub(email_pattern, '████████████████', text)

# Redact concepts based on keyword matching
def redact_concept(text, concept):
    concept_pattern = re.compile(r'\b{}\b'.format(concept), re.IGNORECASE)
    return re.sub(concept_pattern, '██████', text)

import os

def process_file(input_file, output_dir, redact_flags, concepts=None):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Processing file: {input_file}")
    
    with open(input_file, 'r') as file:
        text = file.read()
        doc = nlp(text)

        if redact_flags.get('names'):
            text = redact_names(doc)  # Use SpaCy's NER
            text = redact_known_names(text)  # Apply known names redaction
        if redact_flags.get('dates'):
            text = redact_dates(doc)
        if redact_flags.get('phones'):
            text = redact_phones(text)
        if redact_flags.get('address'):
            text = redact_address(doc)
        if redact_flags.get('emails'):   # Add redaction for emails
            text = redact_emails(text)
        if concepts:
            for concept in concepts:
                text = redact_concept(text, concept)

        # Save redacted file
        relative_path = os.path.relpath(input_file, 'docs/maildir/')
        output_file = os.path.join(output_dir, relative_path + '.censored')
        
        # Create necessary subdirectories in the output path
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w') as out_file:
            out_file.write(text)

    print(f"Processed and saved redacted file: {output_file}")







# Main function
def main():
    parser = argparse.ArgumentParser(description="Redactor tool")
    parser.add_argument('--input', required=True, help="Input file pattern")
    parser.add_argument('--output', required=True, help="Directory to save redacted files")
    parser.add_argument('--names', action='store_true', help="Redact names")
    parser.add_argument('--dates', action='store_true', help="Redact dates")
    parser.add_argument('--phones', action='store_true', help="Redact phone numbers")
    parser.add_argument('--address', action='store_true', help="Redact addresses")
    parser.add_argument('--emails', action='store_true', help="Redact email addresses")  # Add this line
    parser.add_argument('--concept', action='append', help="Redact specific concepts")
    parser.add_argument('--stats', help="Output redaction statistics", default="stderr")
    
    args = parser.parse_args()

    files = glob.glob(args.input)
    for file in files:
        process_file(file, args.output, {
            'names': args.names,
            'dates': args.dates,
            'phones': args.phones,
            'address': args.address,
            'emails': args.emails  # Add this line
        }, args.concept)

if __name__ == "__main__":
    main()
