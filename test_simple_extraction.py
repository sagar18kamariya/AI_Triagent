#!/usr/bin/env python3
"""
Simple test for extract_symptoms function
Tests multiple symptom detection
"""

def test_extract_symptoms():
    """Test the extract_symptoms logic"""
    # This is a simplified version for testing
    def extract_symptoms(user_text):
        user_text = user_text.lower()
        separators = [",", " and ", "&", " with ", ";"]
        for sep in separators:
            user_text = user_text.replace(sep, "|")
        symptoms = [s.strip() for s in user_text.split("|") if len(s.strip()) > 2]
        
        # Handle multi-word symptoms
        if len(symptoms) == 1 and " " in symptoms[0]:
            single = symptoms[0]
            multiword_symptoms = [
                "shortness of breath", "chest pain", "stomach pain", 
                "abdominal pain", "night sweats", "weight loss"
            ]
            extracted = []
            remaining = single
            for multiword in sorted(multiword_symptoms, key=len, reverse=True):
                if multiword in remaining:
                    extracted.append(multiword)
                    remaining = remaining.replace(multiword, " ").strip()
            if extracted:
                remaining_words = [w.strip() for w in remaining.split() if len(w.strip()) > 2]
                symptoms = extracted + remaining_words
            elif len(single.split()) > 2:
                words = [w.strip() for w in single.split() if len(w.strip()) > 2]
                symptoms = words
        
        return list(set(symptoms))
    
    # Test cases
    tests = [
        ("chest pain and shortness of breath", ["chest pain", "shortness of breath"]),
        ("fever, cough, fatigue", ["fever", "cough", "fatigue"]),
        ("headache with nausea", ["headache", "nausea"]),
        ("stomach pain vomiting diarrhea", ["stomach pain", "vomiting", "diarrhea"]),
        ("shortness of breath chest pain", ["shortness of breath", "chest pain"]),
        ("cold", ["cold"]),
    ]
    
    print("Testing extract_symptoms function:")
    print("=" * 50)
    
    all_pass = True
    for input_text, expected in tests:
        result = extract_symptoms(input_text)
        result_set = set(result)
        expected_set = set(expected)
        
        if result_set == expected_set:
            print(f"PASS: '{input_text}' -> {result}")
        else:
            print(f"FAIL: '{input_text}'")
            print(f"  Expected: {expected}")
            print(f"  Got: {result}")
            all_pass = False
    
    print("\n" + "=" * 50)
    if all_pass:
        print("All tests passed!")
    else:
        print("Some tests failed.")
    
    return all_pass

if __name__ == "__main__":
    test_extract_symptoms()