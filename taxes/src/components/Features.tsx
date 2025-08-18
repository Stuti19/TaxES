import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  FileText, 
  Brain, 
  Download, 
  Shield, 
  Clock, 
  CheckCircle2 
} from "lucide-react";

export const Features = () => {
  const features = [
    {
      icon: FileText,
      title: "Document Upload",
      description: "Upload Aadhar Card, Bank Statements, and Form 16 with drag-and-drop simplicity.",
      color: "text-blue-500"
    },
    {
      icon: Brain,
      title: "AI Data Extraction",
      description: "Our AI automatically extracts and validates data from your documents with 99.9% accuracy.",
      color: "text-purple-500"
    },
    {
      icon: CheckCircle2,
      title: "ITR Form Selection",
      description: "Choose from ITR-1, ITR-2, ITR-3, and ITR-4 forms based on your income profile.",
      color: "text-green-500"
    },
    {
      icon: Download,
      title: "Instant Download",
      description: "Get your completed ITR form ready for e-filing in PDF format within minutes.",
      color: "text-orange-500"
    },
    {
      icon: Shield,
      title: "Advanced Security",
      description: "Your data is protected with military-grade encryption and secure cloud storage.",
      color: "text-red-500"
    },
    {
      icon: Clock,
      title: "24/7 Support",
      description: "Get expert assistance anytime with our round-the-clock customer support team.",
      color: "text-indigo-500"
    }
  ];

  return (
    <section id="features" className="py-20 bg-muted/30">
      <div className="container">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Why Choose <span className="text-primary">TaxES</span>?
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Experience the future of tax filing with our AI-powered platform designed for modern taxpayers.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card key={index} className="relative overflow-hidden group hover:shadow-lg transition-all duration-300">
              <CardHeader>
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center mb-4`}>
                  <feature.icon className={`h-6 w-6 ${feature.color}`} />
                </div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {feature.description}
                </CardDescription>
              </CardContent>
              <div className="absolute inset-0 bg-gradient-to-r from-primary/5 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};