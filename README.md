# cis6930fa24-project1
# The Redactor Project by Vijay Kumar Reddy Gade

## Installation
1. Install Pipenv:
    ```bash
    pip install pipenv
    ```
2. Install dependencies:
    ```bash
    pipenv install
    ```

3. Download the SpaCy model:
    ```bash
    pipenv run python -m spacy download en_core_web_sm
    ```

## Usage
To run the redactor:
```bash
pipenv run python redactor.py --input '*.txt' --names --dates --phones --address --concept 'kids' --output 'censored/' --stats stderr
