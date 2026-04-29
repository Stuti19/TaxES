import json
import os
from pathlib import Path
from openpyxl import load_workbook

class ExcelFiller:
    def __init__(self, session_id=None):
        if session_id:
            self.base_dir = Path("taxes_files") / session_id
            self.parsed_dir = self.base_dir / "parsed"
            self.excel_dir = self.base_dir / "excel"
        else:
            # Fallback to old structure for backward compatibility
            self.base_dir = Path("taxes_files")
            self.parsed_dir = self.base_dir / "parsed"
            self.excel_dir = self.base_dir / "excel"
        
        # Create excel directory if it doesn't exist
        self.excel_dir.mkdir(parents=True, exist_ok=True)

    def fill_itr_excel(self, template_path=None, email='', mobile_no=''):
        """Fill ITR Excel using parsed JSON files"""
        try:
            # Set template path
            if template_path is None:
                template_path = Path("itr1_template.xlsm")
                if not template_path.exists():
                    return {'status': 'error', 'message': 'Excel template itr1_template.xlsm not found'}
            
            # Load JSON data
            form16_path = self.parsed_dir / "form16_parsed.json"
            aadhar_path = self.parsed_dir / "aadhar_parsed.json"
            passbook_path = self.parsed_dir / "passbook_parsed.json"
            
            # Check if files exist
            if not form16_path.exists():
                return {'status': 'error', 'message': 'Form16 parsed data not found'}
            if not aadhar_path.exists():
                return {'status': 'error', 'message': 'Aadhar parsed data not found'}
            if not passbook_path.exists():
                return {'status': 'error', 'message': 'Passbook parsed data not found'}
            
            with open(form16_path, 'r') as f:
                form16_data = json.load(f)
            
            with open(aadhar_path, 'r') as f:
                aadhar_data = json.load(f)
            
            with open(passbook_path, 'r') as f:
                passbook_data = json.load(f)
            
            # Load Excel workbook
            print(f"Loading template from: {template_path}")
            wb = load_workbook(str(template_path))
            ws = wb.active
            print("Template loaded successfully")
            
            # Form 16 cell mapping
            form16_mapping = {
                "pan": "AN7",
                "employee_address": "O11",
                "gross_salary": "AO35",
                "salary_section_17_1": "AO36",
                "prerequisites_section_17_2": "AO37",
                "profits_section_17_3": "AO38",
                "total_exemption_section_10": "AO45",
                "net_salary": "AO52",
                "deduction_under_sec16": "AO53",
                "standard_deduction_16_ia": "AO54",
                "entertainment_allowance_16_ii": "AO55",
                "tax_on_employment_16_iii": "AO56",
                "income_chargeable_salaries": "AO57",
                "gross_total_income": "AO93",
                "tax_on_total_income": "AO140",
                "rebate_87A": "AO141",
                "health_education_cess": "AO144",
                "relief_section_89": "AO146"
            }
            
            # Aadhar cell mapping (removed address - will parse into components instead)
            aadhar_mapping = {
                "aadhar_number": "AN8",
                "dob": "AN11"
            }
            
            # Deductions that need dual cells
            dual_cell_mapping = {
                "deduction_80C": ["AB96", "AN96"],
                "deduction_80CCC": ["AB97", "AN97"],
                "deduction_80CCD1": ["AB98", "AN98"],
                "deduction_80CCD1B": ["AB99", "AN99"],
                "deduction_80CCD2": ["AB101", "AN101"],
                "deduction_80D": ["AB102", "AN102"],
                "deduction_80E": ["AB111", "AN111"],
                "deduction_80G": ["AB115", "AN115"],
                "deduction_80TTA": ["AB122", "AN122"]
            }
            
            # Fill Form 16 data
            for json_key, cell_address in form16_mapping.items():
                if json_key in form16_data and form16_data[json_key]:
                    ws[cell_address] = form16_data[json_key]
            
            # Parse Aadhar data using Groq
            parsed_name = None
            parsed_address = None
            
            try:
                import time
                from groq_parser import GroqParser
                parser = GroqParser()
                
                if "name" in aadhar_data and aadhar_data["name"]:
                    print("Waiting 2s before name parsing...")
                    time.sleep(2)
                    parsed_name = parser.parse_name(aadhar_data["name"])
                    print(f"Parsed name: {parsed_name}")
                
                if "address" in aadhar_data and aadhar_data["address"]:
                    print("Waiting 2s before address parsing...")
                    time.sleep(2)
                    parsed_address = parser.parse_address(aadhar_data["address"])
                    print(f"Parsed address: {parsed_address}")
            except Exception as e:
                print(f"Groq parsing error: {e}")
                import traceback
                traceback.print_exc()
            
            # Fill Aadhar data
            for json_key, cell_address in aadhar_mapping.items():
                if json_key in aadhar_data and aadhar_data[json_key]:
                    ws[cell_address] = aadhar_data[json_key]
            
            # Fill parsed name (prioritize Aadhar, fallback to passbook, fallback to simple split)
            if parsed_name and parsed_name.get("first_name"):
                # Use Groq-parsed name from Aadhar
                ws["E7"] = parsed_name.get("first_name", "")
                ws["O7"] = parsed_name.get("middle_name", "")
                ws["Y7"] = parsed_name.get("last_name", "")
                print(f"Filled name fields from Groq-parsed Aadhar: {parsed_name}")
            elif "name" in aadhar_data and aadhar_data["name"]:
                # Use simple parsing from Aadhar name if Groq failed
                first_name, middle_name, last_name = self._parse_name(aadhar_data["name"])
                ws["E7"] = first_name
                ws["O7"] = middle_name
                ws["Y7"] = last_name
                print(f"Filled name fields from simple-parsed Aadhar: {first_name}, {middle_name}, {last_name}")
            elif "name" in passbook_data and passbook_data["name"]:
                # Fallback to passbook name if Aadhar name not available
                first_name, middle_name, last_name = self._parse_name(passbook_data["name"])
                ws["E7"] = first_name
                ws["O7"] = middle_name
                ws["Y7"] = last_name
                print(f"Filled name fields from passbook: {first_name}, {middle_name}, {last_name}")
            
            # Fill parsed address components
            if parsed_address and parsed_address.get("flat_door_block_no") or parsed_address.get("premises_building_village") or parsed_address.get("state"):
                ws["E11"] = parsed_address.get("flat_door_block_no", "")  # Flat/Door/Block No
                ws["O11"] = parsed_address.get("premises_building_village", "")  # Building/Village name
                ws["E13"] = parsed_address.get("road_street_post_office", "")
                ws["W13"] = parsed_address.get("area_locality", "")
                ws["AN13"] = parsed_address.get("town_city_district", "")
                ws["E15"] = parsed_address.get("state", "")
                ws["AA15"] = parsed_address.get("pin_code", "")
                print(f"Filled address fields from Groq-parsed Aadhar: {parsed_address}")
            elif "address" in aadhar_data and aadhar_data["address"]:
                # Fallback to simple address parsing if Groq failed
                fallback_address = self._parse_address(aadhar_data["address"])
                ws["E11"] = fallback_address.get("flat_door_block_no", "")
                ws["O11"] = fallback_address.get("premises_building_village", "")
                ws["E13"] = fallback_address.get("road_street_post_office", "")
                ws["W13"] = fallback_address.get("area_locality", "")
                ws["AN13"] = fallback_address.get("town_city_district", "")
                ws["E15"] = fallback_address.get("state", "")
                ws["AA15"] = fallback_address.get("pin_code", "")
                print(f"Filled address fields from simple-parsed Aadhar: {fallback_address}")
            
            # Fill dual cells for deductions
            for json_key, cell_addresses in dual_cell_mapping.items():
                if json_key in form16_data and form16_data[json_key]:
                    for cell_address in cell_addresses:
                        ws[cell_address] = form16_data[json_key]
            
            # Fill contact information
            if email:
                ws["E28"] = email
            if mobile_no:
                ws["Q28"] = mobile_no
            
            # Calculate and fill derived tax fields
            self._fill_calculated_tax_fields(ws, form16_data)
            
            # Save to excel folder
            output_path = self.excel_dir / "filled_itr.xlsx"
            print(f"Saving Excel to: {output_path}")
            
            # Remove existing file if it exists
            if output_path.exists():
                output_path.unlink()
            
            wb.save(str(output_path))
            print("Excel saved successfully")
            
            return {
                'status': 'success',
                'message': 'Excel file generated successfully',
                'file_path': str(output_path)
            }
            
        except Exception as e:
            print(f"Excel generation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': f'Error generating Excel: {str(e)}'
            }

    def _fill_calculated_tax_fields(self, ws, form16_data):
        """Calculate and fill derived tax fields"""
        try:
            # Get values with default 0 if not present or not numeric
            gross_salary = self._get_numeric_value(form16_data, "gross_salary")
            total_exemption_section_10 = self._get_numeric_value(form16_data, "total_exemption_section_10")
            standard_deduction_16_ia = self._get_numeric_value(form16_data, "standard_deduction_16_ia")
            entertainment_allowance_16_ii = self._get_numeric_value(form16_data, "entertainment_allowance_16_ii")
            tax_on_employment_16_iii = self._get_numeric_value(form16_data, "tax_on_employment_16_iii")
            tax_on_total_income = self._get_numeric_value(form16_data, "tax_on_total_income")
            rebate_87A = self._get_numeric_value(form16_data, "rebate_87A")
            health_education_cess = self._get_numeric_value(form16_data, "health_education_cess")
            relief_section_89 = self._get_numeric_value(form16_data, "relief_section_89")
            
            # Calculate net_salary = gross_salary - total_exemption_section_10
            net_salary = gross_salary - total_exemption_section_10
            ws["AO52"] = net_salary
            
            # Calculate deduction_under_sec16 = standard_deduction_16_ia + entertainment_allowance_16_ii + tax_on_employment_16_iii
            deduction_under_sec16 = standard_deduction_16_ia + entertainment_allowance_16_ii + tax_on_employment_16_iii
            ws["AO53"] = deduction_under_sec16
            
            # Calculate tax_payable_after_rebate = tax_on_total_income - rebate_87A
            tax_payable_after_rebate = tax_on_total_income - rebate_87A
            ws["AO142"] = tax_payable_after_rebate
            
            # Calculate total_tax_and_cess = tax_payable_after_rebate + health_education_cess
            total_tax_and_cess = tax_payable_after_rebate + health_education_cess
            ws["AO145"] = total_tax_and_cess
            
            # Calculate balance_tax_after_relief = total_tax_and_cess - relief_section_89
            balance_tax_after_relief = total_tax_and_cess - relief_section_89
            ws["AO148"] = balance_tax_after_relief
            
            print(f"Calculated fields:")
            print(f"  Net salary (AO52): {net_salary}")
            print(f"  Deduction under sec16 (AO53): {deduction_under_sec16}")
            print(f"  Tax payable after rebate (AO142): {tax_payable_after_rebate}")
            print(f"  Total tax and cess (AO145): {total_tax_and_cess}")
            print(f"  Balance tax after relief (AO148): {balance_tax_after_relief}")
            
        except Exception as e:
            print(f"Error calculating tax fields: {e}")
    
    def _get_numeric_value(self, data, key):
        """Get numeric value from data, return 0 if not present or not numeric"""
        try:
            value = data.get(key, 0)
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Try to convert string to float
                return float(value) if value.strip() else 0.0
            else:
                return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _parse_name(self, full_name):
        """Parse name into first, middle, last"""
        if not full_name or full_name.lower() == "no":
            return "", "", ""
        
        # Remove common prefixes and clean
        name_parts = full_name.replace("MR ", "").replace("MRS ", "").replace("MS ", "").strip().split()
        
        if len(name_parts) == 1:
            return name_parts[0], "", ""
        elif len(name_parts) == 2:
            return name_parts[0], "", name_parts[1]
        else:
            return name_parts[0], " ".join(name_parts[1:-1]), name_parts[-1]

    def _parse_address(self, address):
        """Fallback address parsing - extract components from raw address string"""
        import re
        
        result = {
            "flat_door_block_no": "",
            "premises_building_village": "",
            "road_street_post_office": "",
            "area_locality": "",
            "town_city_district": "",
            "state": "",
            "pin_code": ""
        }
        
        if not address:
            return result
        
        # Extract PIN code (6 digits)
        pin_match = re.search(r'\b(\d{6})\b', address)
        if pin_match:
            result["pin_code"] = pin_match.group(1)
        
        # Split by comma to get address parts
        parts = [part.strip() for part in address.split(',') if part.strip()]
        
        # Try to identify state from common patterns or known states
        indian_states = [
            'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
            'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
            'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya',
            'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim',
            'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand',
            'West Bengal', 'Delhi', 'Chandigarh', 'Ladakh', 'Jammu and Kashmir'
        ]
        
        # Search for state name in address
        for state in indian_states:
            if state.upper() in address.upper():
                result["state"] = state
                break
        
        # Extract flat/door number (first number followed by optional letter)
        flat_match = re.search(r'\b(\d+[A-Z]?)\b', address)
        if flat_match:
            result["flat_door_block_no"] = flat_match.group(1)
        
        # Try to fill parts based on position
        if len(parts) >= 1:
            result["premises_building_village"] = parts[0]
        if len(parts) >= 2:
            result["road_street_post_office"] = parts[1]
        if len(parts) >= 3:
            result["area_locality"] = parts[2]
        if len(parts) >= 4:
            result["town_city_district"] = parts[3]
        if len(parts) >= 5 and not result["state"]:
            result["state"] = parts[4]
        
        return result

    def fill_user_input_sections(self, excel_path, user_inputs):
        """
        Fill user-provided input sections into Excel file
        
        Args:
            excel_path: Path to the Excel file to update
            user_inputs: Dict with structure:
                {
                    "house_property": {...},
                    "other_income": {...},
                    "deductions": {...}
                }
        
        Returns:
            Dict with status and message
        """
        try:
            # Load field mappings
            import json
            from pathlib import Path
            mappings_path = Path(__file__).parent / "config_field_mappings.json"
            
            if not mappings_path.exists():
                return {'status': 'error', 'message': 'Field mappings file not found'}
            
            with open(mappings_path, 'r') as f:
                field_mappings = json.load(f)
            
            # Load the workbook
            print(f"Loading Excel file for user input filling: {excel_path}")
            wb = load_workbook(str(excel_path))
            ws = wb.active
            
            # Helper function to safely set cell value (handling merged cells)
            def set_cell_value(worksheet, cell_ref, value):
                """Set cell value, handling merged cells"""
                # Find if this cell is in any merged range
                merged_range_to_unmerge = None
                for merged_range in worksheet.merged_cells.ranges:
                    if cell_ref in merged_range:
                        merged_range_to_unmerge = merged_range
                        break
                
                if merged_range_to_unmerge:
                    # Unmerge, set value, re-merge
                    worksheet.unmerge_cells(str(merged_range_to_unmerge))
                    worksheet[cell_ref] = value
                    worksheet.merge_cells(str(merged_range_to_unmerge))
                else:
                    # Not merged, just set it
                    worksheet[cell_ref] = value
            
            # Fill House Property section
            if "house_property" in user_inputs and user_inputs["house_property"]:
                hp_data = user_inputs["house_property"]
                hp_mappings = field_mappings.get("house_property", {})
                
                for field_name, cell_ref in hp_mappings.items():
                    if field_name in hp_data and hp_data[field_name] is not None:
                        value = hp_data[field_name]
                        # Handle boolean property_type specially
                        if field_name == "property_type":
                            value = str(value)
                        try:
                            set_cell_value(ws, cell_ref, value)
                            print(f"Filled {field_name}: {cell_ref} = {value}")
                        except Exception as e:
                            print(f"Warning: Could not fill {field_name} at {cell_ref}: {str(e)}")
            
            # Fill Other Income section
            if "other_income" in user_inputs and user_inputs["other_income"]:
                oi_data = user_inputs["other_income"]
                oi_mappings = field_mappings.get("other_income", {})
                
                for field_name, cell_ref in oi_mappings.items():
                    if field_name in oi_data and oi_data[field_name] is not None:
                        value = oi_data[field_name]
                        try:
                            set_cell_value(ws, cell_ref, value)
                            print(f"Filled {field_name}: {cell_ref} = {value}")
                        except Exception as e:
                            print(f"Warning: Could not fill {field_name} at {cell_ref}: {str(e)}")
            
            # Fill Deductions section
            if "deductions" in user_inputs and user_inputs["deductions"]:
                ded_data = user_inputs["deductions"]
                ded_mappings = field_mappings.get("deductions", {})
                
                for field_name, cell_ref in ded_mappings.items():
                    if field_name in ded_data and ded_data[field_name] is not None:
                        value = ded_data[field_name]
                        try:
                            set_cell_value(ws, cell_ref, value)
                            print(f"Filled {field_name}: {cell_ref} = {value}")
                        except Exception as e:
                            print(f"Warning: Could not fill {field_name} at {cell_ref}: {str(e)}")
            
            # Save updated workbook
            print(f"Saving updated Excel file: {excel_path}")
            wb.save(str(excel_path))
            print("User input sections filled successfully")
            
            return {
                'status': 'success',
                'message': 'User input sections filled successfully'
            }
        
        except Exception as e:
            print(f"Error filling user input sections: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': f'Error filling user input sections: {str(e)}'
            }

    def fill_itr_complete(self, parsed_data_dir, user_inputs, email='', mobile_no=''):
        """
        Complete ITR filling: Merge extracted document data + user inputs into Excel
        
        Args:
            parsed_data_dir: Path to directory containing form16_parsed.json, etc.
            user_inputs: Dict with house_property, other_income, deductions
            email: User email
            mobile_no: User mobile number
        
        Returns:
            Dict with status and file path
        """
        try:
            import json
            from pathlib import Path
            
            parsed_data_dir = Path(parsed_data_dir)
            
            # Load extracted data from JSONs
            form16_path = parsed_data_dir / "form16_parsed.json"
            aadhar_path = parsed_data_dir / "aadhar_parsed.json"
            passbook_path = parsed_data_dir / "passbook_parsed.json"
            
            form16_data = {}
            aadhar_data = {}
            passbook_data = {}
            
            if form16_path.exists():
                with open(form16_path, 'r') as f:
                    form16_data = json.load(f)
            
            if aadhar_path.exists():
                with open(aadhar_path, 'r') as f:
                    aadhar_data = json.load(f)
            
            if passbook_path.exists():
                with open(passbook_path, 'r') as f:
                    passbook_data = json.load(f)
            
            # Load template
            template_path = Path(self.excel_dir) / "itr_temp.xlsx"
            if not template_path.exists():
                # Try from backend root directory
                template_path = Path(__file__).parent / "itr_temp.xlsx"
            if not template_path.exists():
                # Try alternate names
                for name in ["itr_template.xlsm", "itr_template.xlsx", "itr_temp.xlsm"]:
                    alt_path = Path(__file__).parent / name
                    if alt_path.exists():
                        template_path = alt_path
                        break
            if not template_path.exists():
                return {'status': 'error', 'message': f'Excel template not found. Searched for: itr_temp.xlsx'}
            
            print(f"Loading template: {template_path}")
            wb = load_workbook(str(template_path))
            ws = wb.active
            
            # ─── Fill Extracted Data ───────────────────────────────
            print("Filling extracted document data...")
            
            # Form 16 mappings
            form16_mapping = {
                "pan": "AN7",
                "employee_address": "O11",
                "gross_salary": "AO35",
                "salary_section_17_1": "AO36",
                "prerequisites_section_17_2": "AO37",
                "profits_section_17_3": "AO38",
                "total_exemption_section_10": "AO45",
                "net_salary": "AO52",
                "deduction_under_sec16": "AO53",
                "standard_deduction_16_ia": "AO54",
                "entertainment_allowance_16_ii": "AO55",
                "tax_on_employment_16_iii": "AO56",
                "income_chargeable_salaries": "AO57",
                "gross_total_income": "AO93",
                "tax_on_total_income": "AO140",
                "rebate_87A": "AO141",
                "health_education_cess": "AO144",
                "relief_section_89": "AO146"
            }
            
            # Aadhar mappings (removed address - will parse into components)
            aadhar_mapping = {
                "aadhar_number": "AN8",
                "dob": "AN11"
            }
            
            # Helper to safely set merged cells
            def set_cell_value(worksheet, cell_ref, value):
                """Set cell value, handling merged cells"""
                # Find if this cell is in any merged range
                merged_range_to_unmerge = None
                for merged_range in worksheet.merged_cells.ranges:
                    if cell_ref in merged_range:
                        merged_range_to_unmerge = merged_range
                        break
                
                if merged_range_to_unmerge:
                    # Unmerge, set value, re-merge
                    worksheet.unmerge_cells(str(merged_range_to_unmerge))
                    worksheet[cell_ref] = value
                    worksheet.merge_cells(str(merged_range_to_unmerge))
                else:
                    # Not merged, just set it
                    worksheet[cell_ref] = value
            
            # Fill Form16 data
            for field_name, cell_ref in form16_mapping.items():
                if field_name in form16_data and form16_data[field_name]:
                    try:
                        set_cell_value(ws, cell_ref, form16_data[field_name])
                        print(f"  Filled {field_name}: {cell_ref}")
                    except Exception as e:
                        print(f"  Warning: Could not fill {field_name}: {str(e)}")
            
            # Fill Aadhar data
            for field_name, cell_ref in aadhar_mapping.items():
                if field_name in aadhar_data and aadhar_data[field_name]:
                    try:
                        set_cell_value(ws, cell_ref, aadhar_data[field_name])
                        print(f"  Filled {field_name}: {cell_ref}")
                    except Exception as e:
                        print(f"  Warning: Could not fill {field_name}: {str(e)}")
            
            # ─── Parse and Fill Name Fields (Groq + Fallback) ───────
            parsed_name = None
            try:
                if "name" in aadhar_data and aadhar_data["name"]:
                    import time
                    from groq_parser import GroqParser
                    parser = GroqParser()
                    print("Parsing name with Groq API...")
                    time.sleep(1)  # Brief delay to avoid rate limiting
                    parsed_name = parser.parse_name(aadhar_data["name"])
                    print(f"  Groq parsed name: {parsed_name}")
            except Exception as e:
                print(f"  Groq name parsing error: {e}")
                import traceback
                traceback.print_exc()
            
            # Fill name fields with proper fallback
            if parsed_name and parsed_name.get("first_name"):
                try:
                    set_cell_value(ws, "E7", parsed_name.get("first_name", ""))
                    set_cell_value(ws, "O7", parsed_name.get("middle_name", ""))
                    set_cell_value(ws, "Y7", parsed_name.get("last_name", ""))
                    print(f"  Filled name fields from Groq-parsed Aadhar: {parsed_name}")
                except Exception as e:
                    print(f"  Warning: Could not fill parsed name fields: {str(e)}")
            elif "name" in aadhar_data and aadhar_data["name"]:
                # Fallback to simple parsing
                try:
                    first_name, middle_name, last_name = self._parse_name(aadhar_data["name"])
                    set_cell_value(ws, "E7", first_name)
                    set_cell_value(ws, "O7", middle_name)
                    set_cell_value(ws, "Y7", last_name)
                    print(f"  Filled name fields from simple-parsed Aadhar: {first_name}, {middle_name}, {last_name}")
                except Exception as e:
                    print(f"  Warning: Could not fill simple parsed name: {str(e)}")
            elif "name" in passbook_data and passbook_data["name"]:
                # Last resort: passbook name
                try:
                    first_name, middle_name, last_name = self._parse_name(passbook_data["name"])
                    set_cell_value(ws, "E7", first_name)
                    set_cell_value(ws, "O7", middle_name)
                    set_cell_value(ws, "Y7", last_name)
                    print(f"  Filled name fields from passbook: {first_name}, {middle_name}, {last_name}")
                except Exception as e:
                    print(f"  Warning: Could not fill passbook name: {str(e)}")
            
            # ─── Parse and Fill Address Fields (Groq + Fallback) ───
            parsed_address = None
            try:
                if "address" in aadhar_data and aadhar_data["address"]:
                    import time
                    from groq_parser import GroqParser
                    parser = GroqParser()
                    print("Parsing address with Groq API...")
                    time.sleep(1)  # Brief delay to avoid rate limiting
                    parsed_address = parser.parse_address(aadhar_data["address"])
                    print(f"  Groq parsed address: {parsed_address}")
            except Exception as e:
                print(f"  Groq address parsing error: {e}")
                import traceback
                traceback.print_exc()
            
            # Fill address fields with proper fallback
            if parsed_address and (parsed_address.get("flat_door_block_no") or parsed_address.get("premises_building_village") or parsed_address.get("state")):
                try:
                    set_cell_value(ws, "E11", parsed_address.get("flat_door_block_no", ""))
                    set_cell_value(ws, "O11", parsed_address.get("premises_building_village", ""))
                    set_cell_value(ws, "E13", parsed_address.get("road_street_post_office", ""))
                    set_cell_value(ws, "W13", parsed_address.get("area_locality", ""))
                    set_cell_value(ws, "AN13", parsed_address.get("town_city_district", ""))
                    set_cell_value(ws, "E15", parsed_address.get("state", ""))
                    set_cell_value(ws, "AA15", parsed_address.get("pin_code", ""))
                    print(f"  Filled address fields from Groq-parsed Aadhar: {parsed_address}")
                except Exception as e:
                    print(f"  Warning: Could not fill Groq parsed address: {str(e)}")
            elif "address" in aadhar_data and aadhar_data["address"]:
                # Fallback to simple address parsing
                try:
                    fallback_address = self._parse_address(aadhar_data["address"])
                    set_cell_value(ws, "E11", fallback_address.get("flat_door_block_no", ""))
                    set_cell_value(ws, "O11", fallback_address.get("premises_building_village", ""))
                    set_cell_value(ws, "E13", fallback_address.get("road_street_post_office", ""))
                    set_cell_value(ws, "W13", fallback_address.get("area_locality", ""))
                    set_cell_value(ws, "AN13", fallback_address.get("town_city_district", ""))
                    set_cell_value(ws, "E15", fallback_address.get("state", ""))
                    set_cell_value(ws, "AA15", fallback_address.get("pin_code", ""))
                    print(f"  Filled address fields from simple-parsed Aadhar: {fallback_address}")
                except Exception as e:
                    print(f"  Warning: Could not fill simple parsed address: {str(e)}")
            
            # Fill contact info
            try:
                set_cell_value(ws, "AN9", email)
                set_cell_value(ws, "AN10", mobile_no)
                print(f"  Filled contact: email={email}, mobile={mobile_no}")
            except Exception as e:
                print(f"  Warning: Could not fill contact: {str(e)}")
            
            # ─── Fill User Inputs ──────────────────────────────────
            print("Filling user input data...")
            
            mappings_path = Path(__file__).parent / "config_field_mappings.json"
            if mappings_path.exists():
                with open(mappings_path, 'r') as f:
                    field_mappings = json.load(f)
                
                # Fill House Property
                if "house_property" in user_inputs and user_inputs["house_property"]:
                    hp_data = user_inputs["house_property"]
                    hp_mappings = field_mappings.get("house_property", {})
                    
                    for field_name, cell_ref in hp_mappings.items():
                        if field_name in hp_data and hp_data[field_name] is not None:
                            try:
                                set_cell_value(ws, cell_ref, hp_data[field_name])
                                print(f"  Filled {field_name}: {cell_ref}")
                            except Exception as e:
                                print(f"  Warning: Could not fill {field_name}: {str(e)}")
                
                # Fill Other Income
                if "other_income" in user_inputs and user_inputs["other_income"]:
                    oi_data = user_inputs["other_income"]
                    oi_mappings = field_mappings.get("other_income", {})
                    
                    for field_name, cell_ref in oi_mappings.items():
                        if field_name in oi_data and oi_data[field_name] is not None:
                            try:
                                set_cell_value(ws, cell_ref, oi_data[field_name])
                                print(f"  Filled {field_name}: {cell_ref}")
                            except Exception as e:
                                print(f"  Warning: Could not fill {field_name}: {str(e)}")
                
                # Fill Deductions
                if "deductions" in user_inputs and user_inputs["deductions"]:
                    ded_data = user_inputs["deductions"]
                    ded_mappings = field_mappings.get("deductions", {})
                    
                    for field_name, cell_ref in ded_mappings.items():
                        if field_name in ded_data and ded_data[field_name] is not None:
                            try:
                                set_cell_value(ws, cell_ref, ded_data[field_name])
                                print(f"  Filled {field_name}: {cell_ref}")
                            except Exception as e:
                                print(f"  Warning: Could not fill {field_name}: {str(e)}")
            
            # Save completed Excel
            output_path = Path(self.excel_dir) / "filled_itr.xlsx"
            wb.save(str(output_path))
            print(f"\n✓ Complete ITR form filled and saved: {output_path}")
            
            return {
                'status': 'success',
                'message': 'Complete ITR form filled successfully',
                'file_path': str(output_path)
            }
        
        except Exception as e:
            print(f"Error in complete ITR filling: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': f'Error filling complete ITR: {str(e)}'
            }