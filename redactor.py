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
namecount=0
conceptcount=0
datecount=0
addresscount=0
phonecount=0



# Function to redact names, including names in email addresses

def redact_names(doc):
    redacted_text = []
    identified_names = []  # List to collect identified names
    global namecount
    email_pattern = re.compile(r'(\b)([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b)', re.IGNORECASE)

    for token in doc:
        # Check for regular names
        if token.ent_type_ == "PERSON":
            redacted_text.append("█" * len(token.text))  # Replace with block characters
            namecount +=1
            identified_names.append(token.text)  # Collect identified names
        else:
            # Check for email pattern
            match = email_pattern.search(token.text)
            if match:
                username, domain = match.group(2), match.group(3)

                # Check if username contains identifiable names
                redacted_username = username
                for name_token in doc.ents:
                    if name_token.label_ == "PERSON" and name_token.text.lower() in username.lower():
                        # Redact the name portion within the email
                        redacted_username = redacted_username.replace(name_token.text, "█" * len(name_token.text))
                        namecount +=1
                        identified_names.append(name_token.text)

                # Construct the redacted email with the (possibly) modified username
                redacted_email = f"{redacted_username}@{domain}"
                redacted_text.append(redacted_email)
            else:
                # If no email match, keep the token as-is
                redacted_text.append(token.text)

    # Print all identified names
    if identified_names:
        print(f"Identified names: {', '.join(identified_names)}")

    return " ".join(redacted_text)


# Function to redact dates
def redact_dates(doc):
    redacted_text = []
    global datecount
    for token in doc:
        if token.ent_type_ == "DATE":
            #print(count(token.text))
            redacted_text.append("█" * len(token.text))
            datecount +=1
        else:
            redacted_text.append(token.text)
    return " ".join(redacted_text)


# Function to redact phone numbers
def redact_phones(text):
    global phonecount
    phone_pattern = re.compile(r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    phonecount +=1
    return phone_pattern.sub("█" * 12, text)




# Function to redact addresses
def redact_addresses(text):
    # Apply SpaCy NER for GPE, LOC, FAC (geopolitical entities, locations, facilities)
    global addresscount
    doc = nlp(text)
    redacted_text = []

    # Iterate through the tokens and redact addresses
    for i, token in enumerate(doc):
        # Check for address-like patterns (numbers followed by a GPE, LOC, or FAC entity)
        if token.ent_type_ in ["GPE", "LOC", "FAC"] and i > 0 and doc[i-1].like_num:
            # Redact the number and place name for address components
            redacted_text[-1] = "█" * len(doc[i-1].text)  # Redact the number part
            addresscount +=1
            redacted_text.append("█" * len(token.text))    # Redact the place name
        elif token.ent_type_ in ["GPE", "LOC", "FAC"]:
            redacted_text.append("█" * len(token.text))
            addresscount +=1
        else:
            redacted_text.append(token.text)

    # Join the tokenized text after initial redaction
    text = " ".join(redacted_text)

    # Extended regex patterns for address parts
    street_pattern = r'\d{1,5}\s+\w+(\s\w+){0,2}\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Plaza|Pl)\b'
    unit_pattern = r'\b(Apt|Apartment|Suite|Ste|Floor|Unit|Fl|Rm)\s*\d*[A-Za-z]?\b'
    zip_code_pattern = r'\b\d{5}(?:-\d{4})?\b'  # Matches ZIP code (e.g., 62704 or 62704-1234)

    # Apply the regex patterns for street, unit, and ZIP code redactions
    text = re.sub(street_pattern, '█' * 20, text)     # Redact street address
    text = re.sub(unit_pattern, '█' * 10, text)       # Redact apartment/unit details
    text = re.sub(zip_code_pattern, '█' * 5, text)    # Redact ZIP code

    return text

# Function to redact the part before '@' in email addresses
def redact_email_usernames(text):
    # Regular expression to match email addresses
    email_pattern = re.compile(r'(\b)([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b)')
    # Replace the username part with redacted characters
    return email_pattern.sub(lambda m: m.group(1) + '█' * len(m.group(2)) + '@' + m.group(3), text)



import nltk
from nltk.corpus import wordnet

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('wordnet')

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
    global conceptcount

    lines = text.splitlines()  # Split text by lines
    redacted_text = []
    for line in lines:
        doc = nlp(line)  # Process each line separately with SpaCy
        redacted_line = []
        for sent in doc.sents:  # Process each sentence in the line
            # Check if any keyword or synonym is present in the sentence
            if any(keyword in sent.text.lower() for keyword in all_keywords):
                # Preserve original punctuation by conditionally adding a period
                conceptcount +=1
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
    print(relative_path)
    output_file = os.path.join(output_dir, relative_path[relative_path.rfind('/')+1:] + '.censored')

    # Ensure output directory structure exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(text)

# Argument parser for command-line flags

def main():
    parser = argparse.ArgumentParser(description="Redact sensitive information from text files.")
    parser.add_argument('--input', required=True, action='append', help="Input text files (glob pattern allowed).")
    parser.add_argument('--output', help="Directory to store censored files.")
    parser.add_argument('--names', action='store_true', help="Redact names and print identified names.")
    parser.add_argument('--dates', action='store_true', help="Redact dates.")
    parser.add_argument('--phones', action='store_true', help="Redact phone numbers.")
    parser.add_argument('--address', action='store_true', help="Redact addresses.")
    parser.add_argument('--email', action='store_true', help="Redact email usernames.")
    parser.add_argument('--concept', action='append', help="Redact sentences related to specified concepts.")
    parser.add_argument('--stats', help="Output statistics to a file or stderr/stdout.")

    args = parser.parse_args()

    # Create a dictionary of flags for redaction
    redact_flags = {
        'names': args.names,
        'dates': args.dates,
        'phones': args.phones,
        'address': args.address,
        'email': args.email
    }

    concepts = args.concept if args.concept else []

    # Process each input file
    for input_pattern in args.input:
        for input_file in glob(input_pattern):
            if input_file.endswith('.txt'):  # Process only .txt files
                try:
                    process_file(input_file, args.output, redact_flags, concepts)
                except Exception as e:
                    print(f"Error processing file {input_file}: {e}", file=sys.stderr)

    # Generate statistics data
    total_redacted = namecount + conceptcount + datecount + addresscount + phonecount
    stats_data = (
        f"Name count: {namecount}\n"
        f"Concept count: {conceptcount}\n"
        f"Date count: {datecount}\n"
        f"Address count: {addresscount}\n"
        f"Phone count: {phonecount}\n"
        f"Total tokens redacted: {total_redacted}\n"
        f"Files processed: {len(args.input)}"
    )

    # Output statistics based on the --stats argument
    if args.stats:
        if args.stats == 'stderr':
            print(stats_data, file=sys.stderr)
        elif args.stats == 'stdout':
            print(stats_data)
        else:
            # Write to a file if a path is provided in --stats
            with open(args.stats, 'w') as f:
                f.write(stats_data)

if __name__ == "__main__":
    main()
