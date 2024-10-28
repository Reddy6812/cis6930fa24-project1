from redactor import redact_concept

def test_redact_concept():
    # Input text containing sentences, some of which relate to the concept keyword
    text = (
        '''
           Signing In To enhance security, you will have to sign in for each transaction session to
reserve and purchase flights. This means you will have to use your password each
time. To have your password e-mailed to you visit link
You are strongly encouraged to sign in at the beginning of the travel arranging
process.
        '''
    )
    
    # Define a single concept keyword to redact sentences containing this keyword
    concept_keywords = ["transaction"]
    
    # Adjusted Expected output with the sentence containing the concept keyword redacted
    expected_output = (
        '''
           ███████████████████████████████████████████████████████████████████████████████████████████████████
reserve and purchase flights. This means you will have to use your password each
time. To have your password e-mailed to you visit link
You are strongly encouraged to sign in at the beginning of the travel arranging
process.
        '''
    )
    
    # Run the redact_concept function
    output = redact_concept(text, concept_keywords)
    
    # Normalize whitespace by stripping leading/trailing spaces from each line
    output_lines = [line.strip() for line in output.splitlines()]
    expected_output_lines = [line.strip() for line in expected_output.splitlines()]
    
    # Print outputs for debugging
    #print("Output:\n", "\n".join(output_lines))
    #print("Expected Output:\n", "\n".join(expected_output_lines))
    
    # Assert if the normalized output matches the normalized expected output
    assert output_lines == expected_output_lines, f"Expected: {expected_output}, but got: {output}"

# Run the test
test_redact_concept()
