import { useState } from "react";
import { AlertCircle, Plus, Trash2 } from "lucide-react";

interface OtherIncomeFormProps {
  onSave: (data: Record<string, any>) => Promise<boolean>;
  isLoading?: boolean;
}

const INCOME_TYPES = [
  "Interest Income",
  "Dividend Income",
  "Rental Income",
  "Capital Gains",
  "Retirement Benefit",
  "Other",
];

const DIVIDEND_PERIODS = [
  "Upto 15-Jun-2024",
  "From 16-Jun-2024 to 15-Sep-2024",
  "From 16-Sep-2024 to 15-Dec-2024",
  "From 16-Dec-2024 to 15-Mar-2025",
  "From 16-Mar-2025 to 31-Mar-2025",
];

export const OtherIncomeForm = ({
  onSave,
  isLoading = false,
}: OtherIncomeFormProps) => {
  const [formData, setFormData] = useState({
    nature_of_income_1: "",
    description_income_1: "",
    amount_income_1: "",
    nature_of_income_2: "",
    description_income_2: "",
    amount_income_2: "",
    nature_of_income_3: "",
    description_income_3: "",
    amount_income_3: "",
    nature_of_income_4: "",
    description_income_4: "",
    amount_income_4: "",
    dividend_income_1: "",
    dividend_income_2: "",
    dividend_income_3: "",
    dividend_income_4: "",
    dividend_income_5: "",
  });

  const [error, setError] = useState("");

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
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
    // Check if any income source is provided with incomplete data
    for (let i = 1; i <= 4; i++) {
      const amount = parseFloat(formData[`amount_income_${i}` as keyof typeof formData] as string || "0");
      if (amount > 0) {
        const nature = formData[`nature_of_income_${i}` as keyof typeof formData];
        const description = formData[`description_income_${i}` as keyof typeof formData];

        if (!nature) {
          setError(`Nature of income ${i} is required if amount is provided`);
          return;
        }
        if (!description) {
          setError(`Description is required for income ${i}`);
          return;
        }
      }
    }

    const success = await onSave(formData);
    if (!success) {
      setError("Failed to save other income data");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-md flex gap-2">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Other Income Sources Table */}
      <div className="space-y-4">
        <h3 className="font-semibold text-sm">Income from Other Sources</h3>
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-100 border-b">
                <th className="px-3 py-2 text-left font-medium">S.No.</th>
                <th className="px-3 py-2 text-left font-medium">Nature of Income</th>
                <th className="px-3 py-2 text-left font-medium">Description</th>
                <th className="px-3 py-2 text-left font-medium">Amount</th>
              </tr>
            </thead>
            <tbody>
              {[1, 2, 3, 4].map((rowNum) => (
                <tr key={rowNum} className="border-b hover:bg-gray-50">
                  <td className="px-3 py-2">{rowNum}</td>
                  <td className="px-3 py-2">
                    <select
                      name={`nature_of_income_${rowNum}`}
                      value={formData[`nature_of_income_${rowNum}` as keyof typeof formData]}
                      onChange={handleChange}
                      disabled={isLoading}
                      className="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-primary"
                    >
                      <option value="">Select...</option>
                      {INCOME_TYPES.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-3 py-2">
                    <input
                      type="text"
                      name={`description_income_${rowNum}`}
                      value={formData[`description_income_${rowNum}` as keyof typeof formData]}
                      onChange={handleChange}
                      disabled={isLoading}
                      placeholder="Enter description"
                      className="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-primary"
                    />
                  </td>
                  <td className="px-3 py-2">
                    <input
                      type="number"
                      name={`amount_income_${rowNum}`}
                      value={formData[`amount_income_${rowNum}` as keyof typeof formData]}
                      onChange={handleChange}
                      disabled={isLoading}
                      placeholder="0"
                      className="w-full px-2 py-1 border border-gray-300 rounded text-xs focus:outline-none focus:ring-1 focus:ring-primary"
                      step="0.01"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dividend Income - Quarterly Breakup */}
      <div className="space-y-4">
        <h3 className="font-semibold text-sm">Dividend Income (Quarterly Breakup)</h3>
        <div className="space-y-2">
          {DIVIDEND_PERIODS.map((period, index) => (
            <div key={index} className="flex items-end gap-2">
              <div className="flex-1 space-y-1">
                <label className="text-xs font-medium text-gray-700">{period}</label>
                <input
                  type="number"
                  name={`dividend_income_${index + 1}`}
                  value={formData[`dividend_income_${index + 1}` as keyof typeof formData]}
                  onChange={handleChange}
                  disabled={isLoading}
                  placeholder="0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
                  step="0.01"
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
        <p className="text-sm text-blue-900">
          💡 <strong>Tip:</strong> (Optional) Enter sources of income from interest, dividends,
          retirement benefits, etc. You can skip this section if you don't have other income sources.
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
