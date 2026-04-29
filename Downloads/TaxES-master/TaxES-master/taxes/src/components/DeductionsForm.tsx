import { useState } from "react";
import { AlertCircle, Info } from "lucide-react";

interface DeductionsFormProps {
  onSave: (data: Record<string, any>) => Promise<boolean>;
  onFinish?: () => Promise<void>;
  isLoading?: boolean;
}

export const DeductionsForm = ({
  onSave,
  onFinish,
  isLoading = false,
}: DeductionsFormProps) => {
  const [formData, setFormData] = useState({
    "80C": "",
    "80CCC": "",
    "80CCD1": "",
    "80CCD1B": "",
    "80CCD2": "",
    "80D": "",
    "80DD": "",
    "80DDB": "",
    "80E": "",
    "80EE": "",
    "80G": "",
    "80GG": "",
    "80GGC": "",
    "80TTA": "",
    "80U": "",
    "80CCH": "",
    other_deductions: "",
  });

  const [error, setError] = useState("");

  const deductionDetails: Record<string, { limit: number; description: string; example: string }> = {
    "80C": { 
      limit: 150000, 
      description: "Life Insurance, PPF, ELSS, etc.",
      example: "Includes LIC premium, Public Provident Fund, Equity Linked Saving Scheme"
    },
    "80CCC": { 
      limit: 150000, 
      description: "Pension Plan Contributions",
      example: "Contributions to pension schemes notified by the government"
    },
    "80CCD1": { 
      limit: 50000, 
      description: "Employee NPS Contribution (10% of salary)",
      example: "Contribution to National Pension Scheme by employee"
    },
    "80CCD1B": { 
      limit: 50000, 
      description: "Additional NPS Contribution",
      example: "Additional contribution to NPS beyond salary deduction"
    },
    "80CCD2": { 
      limit: Infinity, 
      description: "Employer NPS Contribution",
      example: "Contribution to NPS made by employer"
    },
    "80D": { 
      limit: 25000, 
      description: "Health Insurance Premium (Individual)",
      example: "Premium for health insurance policies for self"
    },
    "80DD": { 
      limit: 75000, 
      description: "Medical Treatment - Dependent",
      example: "Medical expenses for dependent family members"
    },
    "80DDB": { 
      limit: 100000, 
      description: "Medical Treatment - Specified Disease",
      example: "Treatment of specific diseases like cancer, diabetes, etc."
    },
    "80E": { 
      limit: 50000, 
      description: "Education Loan Interest",
      example: "Interest paid on loan taken for higher education"
    },
    "80EE": { 
      limit: 50000, 
      description: "Home Loan Interest (First-time Buyer)",
      example: "Interest on home loan for first-time residential property"
    },
    "80G": { 
      limit: Infinity, 
      description: "Donations",
      example: "Donations to charitable institutions, temples, mosques, etc."
    },
    "80GG": { 
      limit: 60000, 
      description: "House Rent Paid",
      example: "Rent paid for residential accommodation (no own property)"
    },
    "80GGC": { 
      limit: Infinity, 
      description: "Political Donations",
      example: "Donations to recognized political parties"
    },
    "80TTA": { 
      limit: 10000, 
      description: "Savings Account Interest",
      example: "Interest on savings account with banks"
    },
    "80U": { 
      limit: 75000, 
      description: "Disability",
      example: "Deduction for person with disability"
    },
    "80CCH": { 
      limit: Infinity, 
      description: "Annuity Scheme",
      example: "Contribution to approved annuity schemes"
    },
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Client-side validation
    for (const [key, value] of Object.entries(formData)) {
      if (value === "") continue;

      const numValue = parseFloat(value);
      if (numValue < 0) {
        setError(`${key} cannot be negative`);
        return;
      }

      if (key in deductionDetails) {
        const limit = deductionDetails[key].limit;
        if (limit !== Infinity && numValue > limit) {
          setError(
            `${key} amount ₹${numValue} exceeds limit of ₹${limit.toLocaleString()}`
          );
          return;
        }
      }
    }

    // Check combined 80C limit
    const total80C = (parseFloat(formData["80C"] || "0") + 
                     parseFloat(formData["80CCC"] || "0") + 
                     parseFloat(formData["80CCD1"] || "0") + 
                     parseFloat(formData["80CCD1B"] || "0"));
    
    if (total80C > 150000) {
      setError(`Combined 80C limit (80C+80CCC+80CCD1+80CCD1B) ₹${total80C} exceeds ₹1,50,000`);
      return;
    }

    const success = await onSave(formData);
    if (success && onFinish) {
      // If this is the last step and onFinish is provided, call it after save
      await onFinish();
    } else if (!success) {
      setError("Failed to save deductions data");
    }
  };

  const formatLimit = (limit: number) => {
    if (limit === Infinity) return "No limit";
    return `₹${limit.toLocaleString()}`;
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md flex gap-2">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div className="bg-amber-50 border border-amber-200 rounded-md p-3 flex gap-2">
        <Info className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-amber-900">
          Enter amounts you're claiming under each deduction section. Values are capped at
          statutory limits per the IT Act.
        </p>
      </div>

      {/* Combined 80C Section */}
      <div className="border rounded-lg p-4 bg-blue-50">
        <h3 className="font-semibold text-sm mb-1 text-blue-900">Section 80C: Combined Limit ₹1,50,000</h3>
        <p className="text-xs text-blue-800 mb-4">
          Combined total of 80C, 80CCC, 80CCD1, and 80CCD1B cannot exceed ₹1.5 lakhs
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {["80C", "80CCC", "80CCD1", "80CCD1B"].map((section) => (
            <div key={section} className="space-y-1">
              <label className="text-xs font-medium text-blue-900">
                {section}: {deductionDetails[section].description}
              </label>
              <input
                type="number"
                name={section}
                value={formData[section as keyof typeof formData]}
                onChange={handleChange}
                disabled={isLoading}
                placeholder="0"
                className="w-full px-2 py-2 border border-gray-300 rounded text-xs focus:outline-none focus:ring-2 focus:ring-primary"
                step="0.01"
              />
              <p className="text-xs text-blue-700">Limit: {formatLimit(deductionDetails[section].limit)}</p>
              <p className="text-xs text-gray-600 italic">{deductionDetails[section].example}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Other Deductions */}
      <div className="space-y-4">
        <h3 className="font-semibold text-sm">Other Deductions</h3>

        {["80CCD2", "80D", "80DD", "80DDB", "80E", "80EE"].map((section) => (
          <div key={section} className="border-b pb-4 last:border-b-0">
            <label className="text-xs font-medium text-gray-900">
              {section}: {deductionDetails[section].description}
            </label>
            <p className="text-xs text-gray-600 mb-2">{deductionDetails[section].example}</p>
            <input
              type="number"
              name={section}
              value={formData[section as keyof typeof formData]}
              onChange={handleChange}
              disabled={isLoading}
              placeholder="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              step="0.01"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Limit: {formatLimit(deductionDetails[section].limit)}
            </p>
          </div>
        ))}

        {["80G", "80GG", "80GGC", "80TTA", "80U", "80CCH"].map((section) => (
          <div key={section} className="border-b pb-4 last:border-b-0">
            <label className="text-xs font-medium text-gray-900">
              {section}: {deductionDetails[section].description}
            </label>
            <p className="text-xs text-gray-600 mb-2">{deductionDetails[section].example}</p>
            <input
              type="number"
              name={section}
              value={formData[section as keyof typeof formData]}
              onChange={handleChange}
              disabled={isLoading}
              placeholder="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              step="0.01"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Limit: {formatLimit(deductionDetails[section].limit)}
            </p>
          </div>
        ))}
      </div>

      {/* Other Deductions */}
      <div className="border-t pt-4">
        <label className="text-sm font-medium">Any Other Deductions</label>
        <input
          type="number"
          name="other_deductions"
          value={formData.other_deductions}
          onChange={handleChange}
          disabled={isLoading}
          placeholder="Enter any other eligible deductions"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary mt-1 text-sm"
          step="0.01"
        />
        <p className="text-xs text-muted-foreground mt-1">
          Deductions not covered by the above sections
        </p>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-md p-3">
        <p className="text-sm text-green-900">
          ✅ <strong>Note:</strong> (Optional) Enter deduction amounts under applicable sections.
          You can skip this section if you don't claim any deductions.
        </p>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white font-medium py-2 px-4 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        {isLoading ? (onFinish ? "Generating..." : "Saving...") : (onFinish ? "Finish & Generate Excel" : "Save & Continue")}
      </button>
    </form>
  );
};
