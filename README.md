
# cis6930fa24-project1

Name: Vijay Kumar Reddy Gade

Redactor is a tool to automatically find and hide sensitive information in text files. It identifies names, dates, phone numbers, addresses, and email usernames, and can also censor sentences related to specified concepts using NLP with SpaCy.

---

## Installation

1. **Install Pipenv**:
    ```bash
    pip install pipenv
    ```

2. **Install dependencies**:
    ```bash
    pipenv install
    ```

3. **Download the SpaCy model**:
    ```bash
    pipenv run python -m spacy download en_core_web_trf
    ```

---

## Usage

Run the redactor using this command:

```bash
pipenv run python redactor.py --input '*.txt' --names --dates --phones --address --concept 'concept_keyword' --output 'output_directory/' --stats stderr
```

---

## Arguments

- `--input`: Specifies input file(s) using patterns like `docs/*.txt`.
- `--output`: Directory to save redacted files.
- `--names`: Redacts names and lists identified names in the console.
- `--dates`: Redacts dates.
- `--phones`: Redacts phone numbers.
- `--address`: Redacts addresses.
- `--email`: Redacts usernames in email addresses.
- `--concept`: Accepts one or more words/phrases to censor sentences/paragraphs around these concepts.
- `--stats`: Outputs summary statistics to `stderr`, `stdout`, or a specified file.

### Censored Characters
The tool uses the Unicode full block character `█` (U+2588) to redact text, including whitespace when necessary, to enhance privacy (e.g., masking first and last names as a single entity).

---

## Concept Redaction

The `--concept` flag allows redacting sentences or paragraphs related to specific themes. A "concept" is defined as a word or phrase representing a theme (e.g., "prison" or "kids"). The tool uses WordNet to find synonyms and hypernyms, capturing related terms. Any sentence or paragraph containing these terms is fully censored.

**Example**: 
Using `--concept prison`, sentences with terms like "jail" or "incarcerated" are redacted.

---

## Examples

1. **Redact names, dates, phones, and addresses**:
    ```bash
    pipenv run python redactor.py --input 'docs/*.txt' --names --dates --phones --address --output 'censored/'
    ```

2. **Redact sentences related to a specific concept**:
    ```bash
    pipenv run python redactor.py --input '*.txt' --concept 'kids' --output 'censored/' --stats stdout
    ```

3. **Redact multiple concepts with custom output**:
    ```bash
    pipenv run python redactor.py --input '*.txt' --names --dates --phones --address --concept 'sensitive' --concept 'prison' --output 'censored_files/' --stats stderr
    ```

---

## Stats

The `--stats` flag generates a summary of redaction processes for each file, showing:

- **Types and Counts**: Number of each type of redacted item.
- **File Summary**: Total (tokens)redactions per file.

#### Example Stats Output:
```plaintext
Redacted File: docs/sample.txt
- Names: 5
- Dates: 2
- Phones: 3
- Addresses: 1
- Concept (kids): 4
- Total tokens: 15

...
```

---

## Challenges and issues

1. **Identifying Last Names in Emails**: Detecting complex names within email usernames can be inconsistent.
2. **Flat/Suite Address Redaction**: Limited handling of unit numbers in addresses.
3. **Over-Redacting Dates**: Days (e.g., "Monday") are also redacted as dates, which may cause excessive censorship.
4. **Synonym Detection for Concepts**: Some related terms may be missed, as WordNet may not always cover less direct synonyms.
5. **Cross-Line Redaction**: Multi-line dates or phrases are difficult to redact in line-by-line processing.
6. **Phone Number Formats**: The tool may miss non-standard or international phone numbers.

---

## Testing

To verify functionality, run:

```bash
pipenv run python -m pytest
```

Place tests in a `tests` folder (e.g., `tests/test_redactor.py`) to check redaction functions for accuracy and consistency.

---
