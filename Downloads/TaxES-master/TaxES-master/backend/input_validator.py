"""
Input validation module for ITR form user inputs
Handles validation for House Property, Other Income, and Deductions sections
"""
from typing import Dict, Tuple, List
import json


class InputValidator:
    """Validates user inputs for ITR form sections"""
    
    # Deduction limits per IT Act
    DEDUCTION_LIMITS = {
        "80C": 150000,      # ₹1.5 lakhs
        "80CCC": 150000,    # ₹1.5 lakhs
        "80CCD1": 50000,    # ₹50k (employee contribution to NPS)
        "80CCD1B": 50000,   # ₹50k (additional NPS)
        "80CCD2": float('inf'), # No specific limit (employer contribution)
        "80D": 25000,       # ₹25k (health insurance - individual)
        "80DD": 75000,      # ₹75k (medical treatment - dependent)
        "80DDB": 100000,    # ₹1 lakh (medical treatment - specified disease)
        "80E": 50000,       # ₹50k (education loan interest)
        "80EE": 50000,      # ₹50k (home loan interest - first-time buyer)
        "80G": float('inf'), # No limit (donations)
        "80GG": 60000,      # ₹60k (house rent paid)
        "80GGC": float('inf'), # No limit (political donations)
        "80TTA": 10000,     # ₹10k (savings account interest)
        "80U": 75000,       # ₹75k (disability)
        "80CCH": float('inf'), # No limit (annuity scheme)
    }

    @staticmethod
    def validate_house_property(data: Dict) -> Tuple[bool, str, Dict]:
        """
        Validate House Property section inputs
        
        Args:
            data: Dict with keys like gross_rent_receivable, tax_paid_local_authorities, etc.
        
        Returns:
            (is_valid, error_message, cleaned_data)
        """
        errors = []
        cleaned_data = {}

        try:
            # Gross rent receivable
            gross_rent = InputValidator._parse_float(data.get("gross_rent_receivable", 0))
            if gross_rent < 0:
                errors.append("Gross rent receivable cannot be negative")
            cleaned_data["gross_rent_receivable"] = gross_rent

            # Tax paid to local authorities
            tax_paid = InputValidator._parse_float(data.get("tax_paid_local_authorities", 0))
            if tax_paid < 0:
                errors.append("Tax paid to local authorities cannot be negative")
            if tax_paid > gross_rent:
                errors.append("Tax paid cannot exceed gross rent receivable")
            cleaned_data["tax_paid_local_authorities"] = tax_paid

            # Annual Value (i - ii)
            annual_value = gross_rent - tax_paid
            cleaned_data["annual_value"] = annual_value

            # 30% of Annual Value (auto-calculated)
            deduction_30 = annual_value * 0.30
            cleaned_data["deduction_30_percent"] = deduction_30

            # Interest on borrowed capital
            interest_borrowed = InputValidator._parse_float(data.get("interest_on_borrowed_capital", 0))
            if interest_borrowed < 0:
                errors.append("Interest on borrowed capital cannot be negative")
            cleaned_data["interest_on_borrowed_capital"] = interest_borrowed

            # Arrears/Unrealised Rent received during the year Less 30%
            arrears_unrealised = InputValidator._parse_float(data.get("arrears_unrealised_rent", 0))
            if arrears_unrealised < 0:
                errors.append("Arrears/Unrealised rent cannot be negative")
            cleaned_data["arrears_unrealised_rent"] = arrears_unrealised

            # Income chargeable under head 'House Property'
            # Formula: annual_value - 30% - interest_on_borrowed_capital + arrears_unrealised
            income_chargeable = annual_value - deduction_30 - interest_borrowed + arrears_unrealised
            
            # As per ITR-1, max loss from house property is INR 2,00,000
            if income_chargeable < -200000:
                errors.append("Loss from house property cannot exceed ₹2,00,000")
            
            cleaned_data["income_chargeable"] = max(income_chargeable, -200000)

            if errors:
                return False, " | ".join(errors), {}
            
            return True, "", cleaned_data

        except Exception as e:
            return False, f"House Property validation error: {str(e)}", {}

    @staticmethod
    def validate_other_income(data: Dict) -> Tuple[bool, str, Dict]:
        """
        Validate Income from Other Sources section
        
        Args:
            data: Dict with keys like nature_of_income_1, amount_income_1, 
                  dividend_income_1-5, etc.
        
        Returns:
            (is_valid, error_message, cleaned_data)
        """
        errors = []
        cleaned_data = {}

        try:
            # Validate other income rows (1-4)
            total_other_income = 0.0
            for i in range(1, 5):
                nature_key = f"nature_of_income_{i}"
                description_key = f"description_income_{i}"
                amount_key = f"amount_income_{i}"

                nature = data.get(nature_key, "").strip() if data.get(nature_key) else ""
                description = data.get(description_key, "").strip() if data.get(description_key) else ""
                amount = InputValidator._parse_float(data.get(amount_key, 0))

                if nature or amount > 0:
                    if not nature:
                        errors.append(f"Nature of income {i} is required if amount is provided")
                    if amount < 0:
                        errors.append(f"Income amount {i} cannot be negative")
                    if amount > 0 and not description:
                        errors.append(f"Description required for income {i}")

                cleaned_data[nature_key] = nature
                cleaned_data[description_key] = description
                cleaned_data[amount_key] = amount
                total_other_income += amount

            # Validate dividend income (quarterly breakup, 5 entries for different periods)
            total_dividend = 0.0
            for i in range(1, 6):
                dividend_key = f"dividend_income_{i}"
                dividend_amount = InputValidator._parse_float(data.get(dividend_key, 0))
                
                if dividend_amount < 0:
                    errors.append(f"Dividend income {i} cannot be negative")
                
                cleaned_data[dividend_key] = dividend_amount
                total_dividend += dividend_amount

            if errors:
                return False, " | ".join(errors), {}
            
            return True, "", cleaned_data

        except Exception as e:
            return False, f"Other Income validation error: {str(e)}", {}

    @staticmethod
    def validate_deductions(data: Dict) -> Tuple[bool, str, Dict]:
        """
        Validate Deductions section
        
        Args:
            data: Dict with deduction amounts for 80C, 80D, 80E, 80G, 80TTA, etc.
        
        Returns:
            (is_valid, error_message, cleaned_data)
        """
        errors = []
        cleaned_data = {}

        try:
            total_80C_limit = 0

            # Validate each deduction type
            for deduction_type in InputValidator.DEDUCTION_LIMITS.keys():
                amount = InputValidator._parse_float(data.get(deduction_type, 0))
                
                if amount < 0:
                    errors.append(f"{deduction_type} cannot be negative")
                
                limit = InputValidator.DEDUCTION_LIMITS[deduction_type]
                if limit != float('inf') and amount > limit:
                    errors.append(f"{deduction_type} amount ₹{amount} exceeds limit of ₹{limit}")
                
                cleaned_data[deduction_type] = amount
                
                # Track combined 80C limit (80C + 80CCC + 80CCD1 + 80CCD1B)
                if deduction_type in ["80C", "80CCC", "80CCD1", "80CCD1B"]:
                    total_80C_limit += amount

            # Combined 80C limit check
            if total_80C_limit > 150000:
                errors.append(f"Combined 80C limit (80C+80CCC+80CCD1+80CCD1B) ₹{total_80C_limit} exceeds ₹1.5 lakhs")

            # Validate other deductions
            other_deductions = InputValidator._parse_float(data.get("other_deductions", 0))
            if other_deductions < 0:
                errors.append("Other deductions cannot be negative")
            cleaned_data["other_deductions"] = other_deductions

            if errors:
                return False, " | ".join(errors), {}
            
            return True, "", cleaned_data

        except Exception as e:
            return False, f"Deductions validation error: {str(e)}", {}

    @staticmethod
    def _parse_float(value) -> float:
        """Safely parse float from various input types"""
        if value is None or value == "":
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value.strip()) if value.strip() else 0.0
        return 0.0

    @staticmethod
    def validate_all_inputs(house_property: Dict, other_income: Dict, deductions: Dict) -> Tuple[bool, str, Dict]:
        """
        Validate all three sections together
        
        Returns:
            (is_valid, error_message, all_cleaned_data)
        """
        all_valid = True
        all_errors = []
        all_cleaned = {}

        # Validate each section
        hp_valid, hp_error, hp_cleaned = InputValidator.validate_house_property(house_property or {})
        if not hp_valid:
            all_valid = False
            all_errors.append(f"House Property: {hp_error}")
        all_cleaned["house_property"] = hp_cleaned

        oi_valid, oi_error, oi_cleaned = InputValidator.validate_other_income(other_income or {})
        if not oi_valid:
            all_valid = False
            all_errors.append(f"Other Income: {oi_error}")
        all_cleaned["other_income"] = oi_cleaned

        ded_valid, ded_error, ded_cleaned = InputValidator.validate_deductions(deductions or {})
        if not ded_valid:
            all_valid = False
            all_errors.append(f"Deductions: {ded_error}")
        all_cleaned["deductions"] = ded_cleaned

        error_msg = " || ".join(all_errors) if all_errors else ""
        return all_valid, error_msg, all_cleaned if all_valid else {}
