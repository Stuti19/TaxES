#!/usr/bin/env python3
"""
ITR Automation Runner

This script combines both Aadhaar and passbook extractors to automatically
fill ITR templates with extracted data.
"""

import os
import sys
from dotenv import load_dotenv
from itr_data_mapper import ITRDataMapper, update_field_mapping
from itr_mapping_config import DEFAULT_MAPPING, create_custom_mapping

load_dotenv()

def main():
    print("=== ITR Automation System ===")
    print()
    
    # Check for ITR template file
    template_files = [f for f in os.listdir('.') if f.lower().endswith(('.xlsx', '.xls')) and 'itr' in f.lower()]
    
    if not template_files:
        print("✗ No ITR template Excel file found!")
        print("Please place your ITR template file in this directory.")
        print("The file should have 'itr' in its name (e.g., 'itr_template.xlsx')")
        return
    
    template_path = template_files[0]
    print(f"✓ Found ITR template: {template_path}")
    
    # Check S3 configuration
    bucket_name = os.getenv('S3_BUCKET_NAME')
    if not bucket_name:
        print("✗ S3_BUCKET_NAME not found in environment variables")
        print("Please check your .env file")
        return
    
    print(f"✓ Using S3 bucket: {bucket_name}")
    print()
    
    # Ask user about mapping configuration
    print("Field Mapping Configuration:")
    print("1. Use default mapping (recommended for first run)")
    print("2. Use custom mapping")
    print("3. Show mapping guide")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == '3':
        from itr_mapping_config import print_mapping_guide
        print_mapping_guide()
        return
    elif choice == '2':
        custom_mapping = create_custom_mapping()
        update_field_mapping(custom_mapping)
        print("✓ Using custom mapping")
    else:
        update_field_mapping(DEFAULT_MAPPING)
        print("✓ Using default mapping")
    
    print()
    
    # Initialize mapper and process
    mapper = ITRDataMapper(template_path)
    
    print("Processing options:")
    print("1. Process all users")
    print("2. Process specific user")
    
    process_choice = input("Enter your choice (1-2): ").strip()
    
    if process_choice == '2':
        user_id = input("Enter user ID: ").strip()
        print(f"\n--- Processing ITR for user: {user_id} ---")
        output_path = mapper.process_user_itr(user_id, bucket_name)
        if output_path:
            print(f"✓ ITR template created: {output_path}")
        else:
            print("✗ Failed to create ITR template")
    else:
        print("\n--- Processing ITR for all users ---")
        processed_files = mapper.process_all_users(bucket_name)
        print(f"\n✓ Successfully processed {len(processed_files)} ITR templates")
        for file_path in processed_files:
            print(f"  - {file_path}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)