import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calculator, Receipt, TrendingUp } from "lucide-react";

const gstRates = [
  { value: "0", label: "0% - Exempt" },
  { value: "5", label: "5% - Essential goods" },
  { value: "12", label: "12% - Standard rate" },
  { value: "18", label: "18% - Standard rate" },
  { value: "28", label: "28% - Luxury items" },
];

export const GSTCalculator = () => {
  const [amount, setAmount] = useState("");
  const [gstRate, setGstRate] = useState("");
  const [calculationType, setCalculationType] = useState("exclusive");
  const [results, setResults] = useState<{
    baseAmount: number;
    cgst: number;
    sgst: number;
    igst: number;
    totalGst: number;
    finalAmount: number;
  } | null>(null);

  const calculateGST = () => {
    if (!amount || !gstRate) return;

    const inputAmount = parseFloat(amount);
    const rate = parseFloat(gstRate);

    let baseAmount: number;
    let gstAmount: number;

    if (calculationType === "inclusive") {
      // Amount includes GST
      baseAmount = inputAmount / (1 + rate / 100);
      gstAmount = inputAmount - baseAmount;
    } else {
      // Amount excludes GST
      baseAmount = inputAmount;
      gstAmount = baseAmount * (rate / 100);
    }

    const cgst = gstAmount / 2;
    const sgst = gstAmount / 2;
    const igst = gstAmount; // For inter-state transactions
    const finalAmount = calculationType === "inclusive" ? inputAmount : baseAmount + gstAmount;

    setResults({
      baseAmount: Math.round(baseAmount * 100) / 100,
      cgst: Math.round(cgst * 100) / 100,
      sgst: Math.round(sgst * 100) / 100,
      igst: Math.round(igst * 100) / 100,
      totalGst: Math.round(gstAmount * 100) / 100,
      finalAmount: Math.round(finalAmount * 100) / 100,
    });
  };

  const resetCalculator = () => {
    setAmount("");
    setGstRate("");
    setResults(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mb-4">
            GST Calculator
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Calculate GST (CGST, SGST, IGST) with accurate breakdowns for your business transactions
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {/* Calculator Input */}
          <Card className="shadow-xl border-0 bg-white/90 backdrop-blur">
            <CardHeader className="bg-gradient-to-r from-primary to-accent text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-2 text-white">
                <Calculator className="h-6 w-6" />
                GST Calculator
              </CardTitle>
              <CardDescription className="text-white/90">
                Enter amount and GST rate to calculate taxes
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              <div className="space-y-2">
                <Label htmlFor="amount">Amount (₹)</Label>
                <Input
                  id="amount"
                  type="number"
                  placeholder="Enter amount"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="text-lg"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="calculation-type">Calculation Type</Label>
                <Select value={calculationType} onValueChange={setCalculationType}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="exclusive">Amount Excluding GST</SelectItem>
                    <SelectItem value="inclusive">Amount Including GST</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="gst-rate">GST Rate</Label>
                <Select value={gstRate} onValueChange={setGstRate}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select GST rate" />
                  </SelectTrigger>
                  <SelectContent>
                    {gstRates.map((rate) => (
                      <SelectItem key={rate.value} value={rate.value}>
                        {rate.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex gap-4">
                <Button onClick={calculateGST} className="flex-1">
                  Calculate GST
                </Button>
                <Button onClick={resetCalculator} variant="outline">
                  Reset
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          {results && (
            <Card className="shadow-xl border-0 bg-white/90 backdrop-blur">
              <CardHeader className="bg-gradient-to-r from-accent to-primary text-white rounded-t-lg">
                <CardTitle className="flex items-center gap-2 text-white">
                  <Receipt className="h-6 w-6" />
                  GST Breakdown
                </CardTitle>
                <CardDescription className="text-white/90">
                  Detailed tax calculation results
                </CardDescription>
              </CardHeader>
              <CardContent className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-muted-foreground">Base Amount</Label>
                    <div className="text-2xl font-bold text-primary">₹{results.baseAmount}</div>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-muted-foreground">Final Amount</Label>
                    <div className="text-2xl font-bold text-accent">₹{results.finalAmount}</div>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    Tax Breakdown
                  </h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                      <span className="font-medium">CGST ({parseFloat(gstRate) / 2}%)</span>
                      <span className="font-bold text-blue-600">₹{results.cgst}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                      <span className="font-medium">SGST ({parseFloat(gstRate) / 2}%)</span>
                      <span className="font-bold text-green-600">₹{results.sgst}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                      <span className="font-medium">IGST ({gstRate}%)</span>
                      <span className="font-bold text-purple-600">₹{results.igst}</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-primary/10 rounded-lg border-2 border-primary/20">
                      <span className="font-bold">Total GST</span>
                      <span className="font-bold text-primary text-lg">₹{results.totalGst}</span>
                    </div>
                  </div>
                </div>

                <div className="bg-muted p-4 rounded-lg">
                  <p className="text-sm text-muted-foreground">
                    <strong>Note:</strong> CGST and SGST apply for intra-state transactions. 
                    IGST applies for inter-state transactions.
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};