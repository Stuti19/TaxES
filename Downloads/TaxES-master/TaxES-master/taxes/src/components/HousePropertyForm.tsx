import { useState } from "react";
import { AlertCircle } from "lucide-react";

interface HousePropertyFormProps {
  onSave: (data: Record<string, any>) => Promise<boolean>;
  isLoading?: boolean;
}

export const HousePropertyForm = ({
  onSave,
  isLoading = false,
}: HousePropertyFormProps) => {
  const [formData, setFormData] = useState({
    gross_rent_receivable: "",
    tax_paid_local_authorities: "",
    interest_on_borrowed_capital: "",
    arrears_unrealised_rent: "",
  });

  const [calculatedValues, setCalculatedValues] = useState({
    annual_value: 0,
    deduction_30_percent: 0,
    income_chargeable: 0,
  });

  const [error, setError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    const newValue = value;
    setFormData((prev) => ({
      ...prev,
      [name]: newValue,
    }));
    setError("");

    // Auto-calculate derived fields
    if (name === "gross_rent_receivable" || name === "tax_paid_local_authorities") {
      const grossRent = parseFloat(
        name === "gross_rent_receivable" ? newValue : formData.gross_rent_receivable
      ) || 0;
      const taxPaid = parseFloat(
        name === "tax_paid_local_authorities" ? newValue : formData.tax_paid_local_authorities
      ) || 0;

      const annualValue = grossRent - taxPaid;
      const deduction30 = annualValue * 0.3;
      const interestBorrowed = parseFloat(formData.interest_on_borrowed_capital) || 0;
      const arrearsUnrealised = parseFloat(formData.arrears_unrealised_rent) || 0;

      const incomeChargeable = annualValue - deduction30 - interestBorrowed + arrearsUnrealised;

      setCalculatedValues({
        annual_value: annualValue,
        deduction_30_percent: deduction30,
        income_chargeable: incomeChargeable,
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Client-side validation
    const grossRent = parseFloat(formData.gross_rent_receivable || "0");
    const taxPaid = parseFloat(formData.tax_paid_local_authorities || "0");

    if (!formData.gross_rent_receivable) {
      setError("Gross rent receivable is required");
      return;
    }

    if (grossRent < 0) {
      setError("Gross rent receivable cannot be negative");
      return;
    }

    if (taxPaid < 0) {
      setError("Tax paid cannot be negative");
      return;
    }

    if (taxPaid > grossRent) {
      setError("Tax paid cannot exceed gross rent receivable");
      return;
    }

    const interestBorrowed = parseFloat(formData.interest_on_borrowed_capital || "0");
    if (interestBorrowed < 0) {
      setError("Interest on borrowed capital cannot be negative");
      return;
    }

    const arrearsUnrealised = parseFloat(formData.arrears_unrealised_rent || "0");
    if (arrearsUnrealised < 0) {
      setError("Arrears/Unrealised rent cannot be negative");
      return;
    }

    // Prepare data with calculated fields
    const dataToSend = {
      ...formData,
      annual_value: calculatedValues.annual_value,
      deduction_30_percent: calculatedValues.deduction_30_percent,
      income_chargeable: calculatedValues.income_chargeable,
    };

    const success = await onSave(dataToSend);
    if (!success) {
      setError("Failed to save house property data");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md flex gap-2">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="space-y-2">
        <label className="text-sm font-medium">
          Gross Rent Received/Receivable/Lettable Value *
        </label>
        <input
          type="number"
          name="gross_rent_receivable"
          value={formData.gross_rent_receivable}
          onChange={handleChange}
          disabled={isLoading}
          placeholder="e.g., 2,00,000"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          step="0.01"
        />
        <p className="text-xs text-muted-foreground">
          Total annual rent/income during the financial year
        </p>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Tax Paid to Local Authorities *</label>
        <input
          type="number"
          name="tax_paid_local_authorities"
          value={formData.tax_paid_local_authorities}
          onChange={handleChange}
          disabled={isLoading}
          placeholder="e.g., 20,000"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          step="0.01"
        />
        <p className="text-xs text-muted-foreground">
          Property tax paid to municipal authorities
        </p>
      </div>

      {/* Auto-calculated field: Annual Value */}
      <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
        <p className="text-sm text-blue-900 font-medium">
          Annual Value (i - ii): ₹
          {calculatedValues.annual_value.toLocaleString("en-IN", {
            maximumFractionDigits: 2,
          })}
        </p>
      </div>

      {/* Auto-calculated field: 30% of Annual Value */}
      <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
        <p className="text-sm text-blue-900 font-medium">
          30% of Annual Value (30% × iii): ₹
          {calculatedValues.deduction_30_percent.toLocaleString("en-IN", {
            maximumFractionDigits: 2,
          })}
        </p>
        <p className="text-xs text-blue-800 mt-1">
          Deduction under Section 23(1)(a)
        </p>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">Interest on Borrowed Capital</label>
        <input
          type="number"
          name="interest_on_borrowed_capital"
          value={formData.interest_on_borrowed_capital}
          onChange={handleChange}
          disabled={isLoading}
          placeholder="e.g., 50,000"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          step="0.01"
        />
        <p className="text-xs text-muted-foreground">
          Interest paid on home loan or borrowed capital for property
        </p>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium">
          Arrears/Unrealised Rent Received During the Year
        </label>
        <input
          type="number"
          name="arrears_unrealised_rent"
          value={formData.arrears_unrealised_rent}
          onChange={handleChange}
          disabled={isLoading}
          placeholder="e.g., 0"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          step="0.01"
        />
        <p className="text-xs text-muted-foreground">
          Any arrears or unrealised rent less 30%
        </p>
      </div>

      {/* Auto-calculated: Income chargeable under head 'House Property' */}
      <div className="p-3 bg-green-50 border border-green-200 rounded-md">
        <p className="text-sm text-green-900 font-medium">
          Income Chargeable Under 'House Property' (vii): ₹
          {calculatedValues.income_chargeable.toLocaleString("en-IN", {
            maximumFractionDigits: 2,
          })}
        </p>
        <p className="text-xs text-green-800 mt-1">
          Formula: iii – iv – v + vi (Max loss: ₹2,00,000)
        </p>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-md p-3">
        <p className="text-sm text-amber-900">
          💡 <strong>Note:</strong> For self-occupied properties, only interest on
          borrowed capital can be deducted. For rented properties, you can deduct
          30% of annual value as deemed deduction for repairs and maintenance.
        </p>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white font-medium py-2 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        {isLoading ? "Saving..." : "Save & Continue"}
      </button>
    </form>
  );
};
