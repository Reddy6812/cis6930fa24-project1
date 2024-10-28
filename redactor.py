import os
import spacy
import re
import sys
import argparse
from glob import glob
from warnings import filterwarnings
import en_core_web_trf

# Silencing warnings from SpaCy
filterwarnings('ignore')

# Load the transformer-based SpaCy model
#nlp = spacy.load('en_core_web_trf')
nlp = en_core_web_trf.load()

# Function to redact names and print identified names
def redact_names(doc):
    redacted_text = []
    identified_names = []  # List to collect identified names
    for token in doc:
        if token.ent_type_ == "PERSON":
            redacted_text.append("█" * len(token.text))  # Replace with block character
            identified_names.append(token.text)  # Collect identified names
        else:
            redacted_text.append(token.text)
    # Print all identified names
    if identified_names:
        print(f"Identified names: {', '.join(identified_names)}")
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
    phone_pattern = re.compile(r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    return phone_pattern.sub("█" * 12, text)

# Function to redact addresses
def redact_addresses(text):
    # Apply SpaCy NER for GPE, LOC, FAC (geopolitical entities, locations, facilities)
    doc = nlp(text)
    redacted_text = []
    
    # Iterate through the tokens and redact addresses
    for i, token in enumerate(doc):
        # Check for address-like patterns (numbers followed by a GPE)
        if token.ent_type_ in ["GPE", "LOC", "FAC"] and i > 0 and doc[i-1].like_num:
            redacted_text[-1] = "█" * len(doc[i-1].text)  # Redact the number part
            redacted_text.append("█" * len(token.text))    # Redact the place name
        elif token.ent_type_ in ["GPE", "LOC", "FAC"]:
            redacted_text.append("█" * len(token.text))
        else:
            redacted_text.append(token.text)

    text = " ".join(redacted_text)

    # Regex patterns to capture different parts of an address
    street_pattern = r'\d{1,5}\s+\w+(\s\w+){0,2}\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b'
    zip_code_pattern = r'\b\d{5}(?:-\d{4})?\b'  # Matches ZIP code (e.g., 62704 or 62704-1234)

    # Apply the regex patterns
    text = re.sub(street_pattern, '█' * 20, text)  # Redact street address
    text = re.sub(zip_code_pattern, '█' * 5, text)  # Redact ZIP code

    return text


# Function to redact the part before '@' in email addresses
def redact_email_usernames(text):
    # Regular expression to match email addresses
    email_pattern = re.compile(r'(\b)([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b)')
    # Replace the username part with redacted characters
    return email_pattern.sub(lambda m: m.group(1) + '█' * len(m.group(2)) + '@' + m.group(3), text)



import nltk
from nltk.corpus import wordnet

# Enhanced function to get synonyms, including hypernyms and related terms for broader coverage
def get_synonyms(keywords):
    synonyms = set()
    for keyword in keywords:
        for syn in wordnet.synsets(keyword):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name().lower().replace('_', ' '))  # Add direct synonyms
            for hypernym in syn.hypernyms():  # Add hypernyms for broader coverage
                for lemma in hypernym.lemmas():
                    synonyms.add(lemma.name().lower().replace('_', ' '))
    return synonyms

# Function to redact only sentences containing concept keywords or their synonyms
def redact_concept(text, concept_keywords):
    # Generate a list of synonyms for the concept keywords
    synonyms = get_synonyms(concept_keywords)
    keywords_set = set(map(str.lower, concept_keywords))  # Include original keywords as well
    all_keywords = keywords_set | synonyms  # Union of keywords and their synonyms

    lines = text.splitlines()  # Split text by lines
    redacted_text = []
    for line in lines:
        doc = nlp(line)  # Process each line separately with SpaCy
        redacted_line = []
        for sent in doc.sents:  # Process each sentence in the line
            # Check if any keyword or synonym is present in the sentence
            if any(keyword in sent.text.lower() for keyword in all_keywords):
                # Preserve original punctuation by conditionally adding a period
                redacted_content = "█" * len(sent.text.rstrip('.'))
                if sent.text.endswith('.'):
                    redacted_content += '.'
                redacted_line.append(redacted_content)
            else:
                redacted_line.append(sent.text)  # Keep sentences without the keyword or synonym
        redacted_text.append(" ".join(redacted_line))  # Join sentences back into the line
    return "\n".join(redacted_text)  # Rejoin lines with newline characters for paragraph breaks





# Function to process and redact file
def process_file(input_file, output_dir, redact_flags, concepts):
    with open(input_file, 'r') as f:
        text = f.read()
    
    doc = nlp(text)

    # Redact based on the specified flags, updating doc after each step
    if redact_flags['names']:
        text = redact_names(doc)
        doc = nlp(text)  # Re-parse the text to update the document object
    if redact_flags['dates']:
        text = redact_dates(doc)
        doc = nlp(text)  # Re-parse after dates redaction
    if redact_flags['phones']:
        text = redact_phones(text)  # Phone numbers work directly on the text
    if redact_flags['address']:
        text = redact_addresses(text)  # Redact addresses
    if redact_flags['email']:
        text = redact_email_usernames(text)  # Redact email usernames

    # Apply concept redaction
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
    parser.add_argument('--names', action='store_true', help="Redact names and print identified names.")
    parser.add_argument('--dates', action='store_true', help="Redact dates.")
    parser.add_argument('--phones', action='store_true', help="Redact phone numbers.")
    parser.add_argument('--address', action='store_true', help="Redact addresses.")
    parser.add_argument('--email', action='store_true', help="Redact email usernames.")  # Added email flag
    parser.add_argument('--concept', action='append', help="Redact sentences related to specified concepts.")
    parser.add_argument('--stats', help="Output statistics to a file or stderr/stdout.")

    args = parser.parse_args()

    # Create a dictionary of flags for redaction
    redact_flags = {
        'names': args.names,
        'dates': args.dates,
        'phones': args.phones,
        'address': args.address,
        'email': args.email  # Email redaction added to flags
    }

    concepts = args.concept if args.concept else []

    # Process each input file
    for input_pattern in args.input:
        for input_file in glob(input_pattern):
            if input_file.endswith('.txt'):  # Process only .txt files
                try:
                    process_file(input_file, args.output, redact_flags, concepts)
                except Exception as e:
                    print(f"Error processing file {input_file}: {e}")

    # Generate and output statistics (basic example, can be expanded)
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
