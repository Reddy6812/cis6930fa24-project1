from redactor import redact_addresses
import spacy

nlp = spacy.load('en_core_web_trf')

def test_redact_address():
    text = '''John Doe, a longtime resident of New York City, recently moved to a new house located at 1234 Elm Street, Apt 56, Brooklyn, NY 11201. 
    He has lived in various parts of the city over the years, but this new location, 
    just a few blocks away from Central Park, has become his favorite. For any official correspondence, you can send mail to his previous address: 789 Maple Avenue, Unit 23, Manhattan, NY 10001. John's new phone number is (555) 123-4567, and he's planning to update all his contacts about the change soon.'''
    doc = nlp(text)
    redacted = redact_addresses(doc)
    assert "I live in ███ ████ ████ ." in redacted  # Updated expected result
