import re

def zimbabwe( text ):
    data = {}
    
    id_number_match = re.search(r'Number\w*\s*(\d{2}-\s*\d+)', text, re.IGNORECASE)
    first_name_match = re.search(r'First NAME\s*([A-Z]+)', text, re.IGNORECASE)
    surname_match = re.search(r'SuRNAME\s*([A-Z]+)', text, re.IGNORECASE)
    dob_match = re.search(r'Date O[FP] BIRTH\s*(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    
    if id_number_match:
        data['ID Number'] = id_number_match.group(1).strip().replace(" ", "")

    if first_name_match:
        data['First Name'] = first_name_match.group(1).capitalize().strip()
    if surname_match:
        data['Surname'] = surname_match.group(1).capitalize().strip()
    if dob_match:
        data['Date of Birth'] = dob_match.group(1)
    
    return data