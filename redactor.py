import os
import spacy
import re
import sys
import argparse
from glob import glob
from warnings import filterwarnings

# Silencing warnings from SpaCy
filterwarnings('ignore')

# Load the transformer-based SpaCy model
nlp = spacy.load('en_core_web_trf')

# Function to redact names
def redact_names(doc):
    redacted_text = []
    for token in doc:
        if token.ent_type_ == "PERSON":
            redacted_text.append("█" * len(token.text))  # Replace with block character
        else:
            redacted_text.append(token.text)
    return " ".join(redacted_text)

# Function to redact dates
def redact_dates(doc):
    redacted_text = []
    for token in doc:
        if token.ent_type_ == "DATE":
            redacted_text.append("█" * len(token.text))
        else:
            redacted_text.append(token.text)
    return " ".join(redacted_text)

# Function to redact phone numbers
def redact_phones(text):
    phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    return phone_pattern.sub("█" * 12, text)

# Function to redact addresses
def redact_addresses(doc):
    redacted_text = []
    for token in doc:
        if token.ent_type_ in ["GPE", "LOC", "FAC"]:
            redacted_text.append("█" * len(token.text))
        else:
            redacted_text.append(token.text)
    return " ".join(redacted_text)

# Function to redact concepts based on keywords
def redact_concept(text, concept_keywords):
    for keyword in concept_keywords:
        text = re.sub(rf'\b{keyword}\b', '█' * len(keyword), text, flags=re.IGNORECASE)
    return text

# Function to process and redact file
def process_file(input_file, output_dir, redact_flags, concepts):
    with open(input_file, 'r') as f:
        text = f.read()
    
    doc = nlp(text)

    # Redact based on the specified flags
    if redact_flags['names']:
        text = redact_names(doc)
    if redact_flags['dates']:
        text = redact_dates(nlp(text))
    if redact_flags['phones']:
        text = redact_phones(text)
    if redact_flags['address']:
        text = redact_addresses(nlp(text))
    
    if concepts:
        text = redact_concept(text, concepts)

    # Save redacted file with '.censored' extension
    relative_path = os.path.relpath(input_file, 'docs/')  # Assuming 'docs/' is the base folder for input files
    output_file = os.path.join(output_dir, relative_path + '.censored')

    # Ensure output directory structure exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(text)

# Argument parser for command-line flags
def main():
    parser = argparse.ArgumentParser(description="Redact sensitive information from text files.")
    parser.add_argument('--input', required=True, action='append', help="Input text files (glob pattern allowed).")
    parser.add_argument('--output', required=True, help="Directory to store censored files.")
    parser.add_argument('--names', action='store_true', help="Redact names.")
    parser.add_argument('--dates', action='store_true', help="Redact dates.")
    parser.add_argument('--phones', action='store_true', help="Redact phone numbers.")
    parser.add_argument('--address', action='store_true', help="Redact addresses.")
    parser.add_argument('--concept', action='append', help="Redact sentences related to specified concepts.")
    parser.add_argument('--stats', help="Output statistics to a file or stderr/stdout.")

    args = parser.parse_args()

    # Create a dictionary of flags for redaction
    redact_flags = {
        'names': args.names,
        'dates': args.dates,
        'phones': args.phones,
        'address': args.address
    }

    concepts = args.concept if args.concept else []

    # Process each input file
    for input_pattern in args.input:
        for input_file in glob(input_pattern):
            try:
                process_file(input_file, args.output, redact_flags, concepts)
            except Exception as e:
                print(f"Error processing file {input_file}: {e}")

    # Generate and output statistics (you can expand this with more detailed stats)
    if args.stats:
        stats_output = f"Files processed: {len(args.input)}"
        if args.stats == 'stderr':
            print(stats_output, file=sys.stderr)
        elif args.stats == 'stdout':
            print(stats_output)
        else:
            with open(args.stats, 'w') as f:
                f.write(stats_output)

if __name__ == "__main__":
    main()
