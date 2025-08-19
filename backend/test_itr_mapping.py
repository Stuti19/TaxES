#!/usr/bin/env python3
"""Test ITR mapping with sample data"""

from itr_data_mapper import ITRDataMapper
import os

def test_mapping():
    # Sample extracted data
    sample_data = {
        'name': 'John Michael Smith',
        'aadhar_number': '123456789012',
        'dob': '1990-05-15',
        'accountNumber': '1234567890123456',
        'bankName': 'State Bank of India',
        'IFSC_Code': 'SBIN0001234'
    }
    
    template_path = input("Enter path to your ITR template Excel file: ").strip()
    
    if not os.path.exists(template_path):
        print(f"Template not found: {template_path}")
        return
    
    mapper = ITRDataMapper(template_path)
    
    # Test name splitting
    first, middle, last = mapper.split_name(sample_data['name'])
    print(f"Name split test:")
    print(f"  Full: {sample_data['name']}")
    print(f"  First: {first} -> E7")
    print(f"  Middle: {middle} -> O7") 
    print(f"  Last: {last} -> Y7")
    print()
    
    # Create test output
    output_path = "test_itr_filled.xlsx"
    success = mapper.map_data_to_template(sample_data, output_path)
    
    if success:
        print(f"✓ Test Excel created: {output_path}")
        
        # Convert to PDF
        pdf_path = mapper.convert_to_pdf(output_path)
        if pdf_path:
            print(f"✓ Test PDF created: {pdf_path}")
        else:
            print("✗ PDF conversion failed")
    else:
        print("✗ Test failed")

if __name__ == "__main__":
    test_mapping()