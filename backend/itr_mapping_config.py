"""
ITR Template Mapping Configuration Helper

This file helps you configure where each extracted field should be placed in your ITR Excel template.
You can specify the exact cell addresses where each piece of data should go.
"""

# Default mapping configuration
DEFAULT_MAPPING = {
    # Personal Information from Aadhaar
    'name': 'B8',           # Full Name
    'aadhar_number': 'B10', # Aadhaar Number
    'dob': 'B12',           # Date of Birth (YYYY-MM-DD format)
    'gender': 'B16',        # Gender (Male/Female)
    'address': 'B14',       # Complete Address
    
    # Bank Information from Passbook
    'accountNumber': 'B20', # Bank Account Number
    'bankName': 'B22',      # Bank Name
    'IFSC_Code': 'B24',     # IFSC Code
}

def create_custom_mapping():
    """
    Create a custom mapping based on your ITR template structure.
    
    Instructions:
    1. Open your ITR template Excel file
    2. Note down the cell addresses where each field should go
    3. Update the mapping below
    
    Example cell addresses:
    - 'A1' = Column A, Row 1
    - 'C15' = Column C, Row 15
    - 'AB25' = Column AB, Row 25
    """
    
    custom_mapping = {
        # Update these cell addresses according to your ITR template
        
        # Section 1: Personal Information (usually at the top)
        'name': 'B8',           # Where should the full name go?
        'aadhar_number': 'B10', # Where should Aadhaar number go?
        'dob': 'B12',           # Where should date of birth go?
        'gender': 'B16',        # Where should gender go?
        'address': 'B14',       # Where should address go?
        
        # Section 2: Bank Details (usually in bank information section)
        'accountNumber': 'B20', # Where should account number go?
        'bankName': 'B22',      # Where should bank name go?
        'IFSC_Code': 'B24',     # Where should IFSC code go?
        
        # Add more fields as needed:
        # 'pan_number': 'B26',  # If you extract PAN from documents
        # 'mobile': 'B28',      # If you extract mobile number
        # 'email': 'B30',       # If you extract email
    }
    
    return custom_mapping

def get_mapping_by_section():
    """
    Alternative way to organize mapping by ITR sections
    """
    return {
        'personal_info': {
            'name': 'B8',
            'aadhar_number': 'B10',
            'dob': 'B12',
            'gender': 'B16',
            'address': 'B14',
        },
        'bank_details': {
            'accountNumber': 'B20',
            'bankName': 'B22',
            'IFSC_Code': 'B24',
        }
    }

def print_mapping_guide():
    """Print a guide for setting up the mapping"""
    print("=== ITR Template Mapping Guide ===")
    print()
    print("To set up your mapping:")
    print("1. Open your ITR template Excel file")
    print("2. Find where each field should be placed")
    print("3. Note the cell address (e.g., B8, C15, etc.)")
    print("4. Update the mapping in this file")
    print()
    print("Available fields to map:")
    print("- name: Full name from Aadhaar")
    print("- aadhar_number: 12-digit Aadhaar number")
    print("- dob: Date of birth (YYYY-MM-DD)")
    print("- gender: Male/Female")
    print("- address: Complete address from Aadhaar")
    print("- accountNumber: Bank account number")
    print("- bankName: Bank name")
    print("- IFSC_Code: Bank IFSC code")
    print()
    print("Example mapping:")
    print("'name': 'B8'  # Places name in cell B8")
    print("'dob': 'C15'  # Places date of birth in cell C15")

if __name__ == "__main__":
    print_mapping_guide()