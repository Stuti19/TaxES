import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { 
  FileText, 
  Upload, 
  Brain, 
  Download, 
  CheckCircle, 
  Clock,
  ArrowRight,
  FileCheck,
  Sparkles
} from "lucide-react";

const itrTypes = [
  {
    type: "ITR-1",
    title: "Sahaj",
    description: "For individuals with salary income",
    features: ["Salary Income", "House Property", "Other Sources"],
    recommended: true
  },
  {
    type: "ITR-2", 
    title: "Standard",
    description: "For individuals/HUFs with capital gains",
    features: ["Capital Gains", "Multiple Sources", "Foreign Assets"]
  },
  {
    type: "ITR-3",
    title: "Business",
    description: "For individuals with business income",
    features: ["Business Income", "Professional Income", "Presumptive Taxation"]
  },
  {
    type: "ITR-4",
    title: "Sugam",
    description: "For presumptive business income",
    features: ["Presumptive Income", "Business < 2Cr", "Simple Filing"]
  }
];

const processSteps = [
  {
    id: 1,
    title: "Start Process",
    description: "Initialize your ITR filing journey",
    icon: FileText,
    status: "completed"
  },
  {
    id: 2,
    title: "Choose ITR Type",
    description: "Select the appropriate ITR form",
    icon: FileCheck,
    status: "current"
  },
  {
    id: 3,
    title: "Upload Documents",
    description: "Upload required documents",
    icon: Upload,
    status: "pending"
  },
  {
    id: 4,
    title: "AI Processing",
    description: "AI extracts and validates data",
    icon: Brain,
    status: "pending"
  },
  {
    id: 5,
    title: "Review & Submit",
    description: "Review details and submit",
    icon: CheckCircle,
    status: "pending"
  },
  {
    id: 6,
    title: "Download ITR",
    description: "Download completed ITR",
    icon: Download,
    status: "pending"
  }
];

export const ITRProcessFlow = () => {
  const [selectedITR, setSelectedITR] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(2);
  const navigate = useNavigate();
  const { user } = useAuth();

  const progressPercentage = (currentStep / processSteps.length) * 100;

  const handleITRSelection = (itrType: string) => {
    setSelectedITR(itrType);
  };

  const handleContinue = () => {
    if (selectedITR) {
      // Navigate to the document upload page
      navigate(`/automate-itr/${selectedITR.toLowerCase()}`);
    }
  };

  const handleStartProcess = () => {
    if (!user) {
      // Trigger auth dialog
      document.getElementById('auth-button')?.click();
      return;
    }
    setCurrentStep(2);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Progress Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-2">
          <Sparkles className="w-6 h-6 text-primary" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Professional ITR Filing Process
          </h1>
        </div>
        
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center justify-between text-sm text-muted-foreground mb-2">
            <span>Step {currentStep} of {processSteps.length}</span>
            <span>{Math.round(progressPercentage)}% Complete</span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </div>
      </div>

      {/* Process Steps */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {processSteps.map((step, index) => {
          const Icon = step.icon;
          const isCompleted = index + 1 < currentStep;
          const isCurrent = index + 1 === currentStep;
          
          return (
            <Card 
              key={step.id}
              className={`professional-card border-2 ${
                isCompleted 
                  ? 'border-green-200 bg-green-50' 
                  : isCurrent 
                    ? 'border-primary bg-primary/5' 
                    : 'border-muted'
              }`}
            >
              <CardContent className="p-4 text-center">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-2 ${
                  isCompleted 
                    ? 'bg-green-100 text-green-600' 
                    : isCurrent 
                      ? 'bg-primary/10 text-primary' 
                      : 'bg-muted text-muted-foreground'
                }`}>
                  {isCompleted ? (
                    <CheckCircle className="w-6 h-6" />
                  ) : (
                    <Icon className="w-6 h-6" />
                  )}
                </div>
                <h3 className="font-medium text-sm">{step.title}</h3>
                <p className="text-xs text-muted-foreground mt-1">{step.description}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Main Content */}
      {currentStep === 1 && (
        <Card className="professional-card max-w-2xl mx-auto">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Ready to Start Your ITR Filing?</CardTitle>
            <p className="text-muted-foreground">
              Our AI-powered platform makes tax filing simple and accurate
            </p>
          </CardHeader>
          <CardContent className="text-center">
            <Button 
              size="lg" 
              onClick={handleStartProcess}
              className="bg-gradient-to-r from-primary to-accent hover:shadow-glow"
            >
              Start ITR Process
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </CardContent>
        </Card>
      )}

      {currentStep === 2 && (
        <div className="space-y-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-2">Choose Your ITR Type</h2>
            <p className="text-muted-foreground">
              Select the ITR form that matches your income sources
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {itrTypes.map((itr) => (
              <Card 
                key={itr.type}
                className={`professional-card cursor-pointer transition-all duration-300 border-2 ${
                  selectedITR === itr.type 
                    ? 'border-primary bg-primary/5 scale-105' 
                    : 'border-muted hover:border-primary/50'
                } ${itr.recommended ? 'ring-2 ring-accent/20' : ''}`}
                onClick={() => handleITRSelection(itr.type)}
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{itr.type}</CardTitle>
                    {itr.recommended && (
                      <Badge variant="secondary" className="bg-accent/20 text-accent-foreground">
                        Recommended
                      </Badge>
                    )}
                  </div>
                  <h3 className="font-semibold text-primary">{itr.title}</h3>
                  <p className="text-sm text-muted-foreground">{itr.description}</p>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {itr.features.map((feature) => (
                      <li key={feature} className="flex items-center text-sm">
                        <CheckCircle className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>

          {selectedITR && (
            <div className="text-center">
              <Button 
                size="lg" 
                onClick={handleContinue}
                className="bg-gradient-to-r from-primary to-accent hover:shadow-glow"
              >
                Continue with {selectedITR}
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};