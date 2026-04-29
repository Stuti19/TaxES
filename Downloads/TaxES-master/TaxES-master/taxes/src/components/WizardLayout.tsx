import { ReactNode } from "react";
import { ChevronLeft, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface WizardLayoutProps {
  currentStep: number;
  totalSteps: number;
  stepTitles: string[];
  children: ReactNode;
  onBack?: () => void;
  onNext?: () => void;
  onFinish?: () => void;
  isLoading?: boolean;
  canProceed?: boolean;
}

export const WizardLayout = ({
  currentStep,
  totalSteps,
  stepTitles,
  children,
  onBack,
  onNext,
  onFinish,
  isLoading = false,
  canProceed = true,
}: WizardLayoutProps) => {
  const isLastStep = currentStep === totalSteps;
  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/3">
      {/* Header */}
      <header className="border-b bg-card/95 backdrop-blur-sm sticky top-0 z-50 shadow-sm">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              TaxES - Form Completion
            </h1>
          </div>
          <div className="text-sm text-muted-foreground">
            Step {currentStep} of {totalSteps}
          </div>
        </div>
      </header>

      <div className="container py-8">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between mb-3">
            {stepTitles.map((title, index) => (
              <div key={index} className="flex flex-col items-center flex-1">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold mb-2 transition-all ${
                    index + 1 < currentStep
                      ? "bg-green-500 text-white"
                      : index + 1 === currentStep
                      ? "bg-primary text-white ring-2 ring-primary ring-offset-2"
                      : "bg-muted text-muted-foreground"
                  }`}
                >
                  {index + 1 < currentStep ? (
                    <CheckCircle className="w-6 h-6" />
                  ) : (
                    index + 1
                  )}
                </div>
                <p className="text-xs text-center text-muted-foreground max-w-20 line-clamp-2">
                  {title}
                </p>
              </div>
            ))}
          </div>

          {/* Progress bar */}
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Content */}
        <div className="max-w-2xl mx-auto">
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="text-2xl">
                {stepTitles[currentStep - 1]}
              </CardTitle>
            </CardHeader>
            <CardContent className="min-h-96">
              {children}
            </CardContent>
          </Card>

          {/* Navigation Buttons */}
          <div className="flex justify-between gap-4 mt-8">
            {currentStep > 1 && (
              <Button
                variant="outline"
                onClick={onBack}
                disabled={isLoading}
                className="gap-2"
              >
                <ChevronLeft className="w-4 h-4" />
                Back
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
