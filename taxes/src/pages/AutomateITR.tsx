import { Navigation } from "@/components/Navigation";
import { Footer } from "@/components/Footer";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText, Calculator, Download, CheckCircle, Clock, Shield, Zap } from "lucide-react";
import { Link } from "react-router-dom";

const AutomateITR = () => {
  const features = [
    {
      icon: <Zap className="h-8 w-8 text-primary" />,
      title: "Automated Data Extraction",
      description: "AI-powered extraction from Form 16, bank statements, and Aadhar card"
    },
    {
      icon: <Shield className="h-8 w-8 text-green-500" />,
      title: "Error-Free Processing",
      description: "Advanced validation ensures accuracy and compliance with IT department norms"
    },
    {
      icon: <Clock className="h-8 w-8 text-blue-500" />,
      title: "Quick Turnaround",
      description: "Complete ITR processing in minutes, not hours"
    },
    {
      icon: <CheckCircle className="h-8 w-8 text-accent" />,
      title: "Expert Reviewed",
      description: "All returns are verified by certified tax professionals"
    }
  ];

  const itrForms = [
    {
      form: "ITR-1 (Sahaj)",
      description: "For individuals with salary income, one house property and other sources",
      features: ["Salary Income", "House Property", "Other Sources", "Income up to ₹50 Lakh"],
      bgColor: "bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20"
    },
    {
      form: "ITR-2",
      description: "For individuals and HUFs not having income from business or profession",
      features: ["Capital Gains", "Multiple Properties", "Foreign Income", "Director of Company"],
      bgColor: "bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20"
    },
    {
      form: "ITR-3",
      description: "For individuals and HUFs having income from business or profession",
      features: ["Business Income", "Professional Income", "Partnership Firm", "Presumptive Income"],
      bgColor: "bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20"
    },
    {
      form: "ITR-4 (Sugam)",
      description: "For presumptive income from business and profession",
      features: ["Presumptive Business", "Professional Income", "Turnover up to ₹2 Crore", "Simplified Filing"],
      bgColor: "bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20"
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main>
        {/* Hero Section */}
        <section className="py-20 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5 animate-gradient-x bg-[length:400%_400%]" />
          
          <div className="container relative">
            <div className="text-center max-w-4xl mx-auto">
              <Badge className="mb-4" variant="secondary">
                AI-Powered Tax Solution
              </Badge>
              <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                Automate ITR Data Extraction
              </h1>
              <p className="text-xl text-muted-foreground mb-8 leading-relaxed">
                Revolutionary AI technology that automatically extracts and processes your tax data from 
                documents, eliminating manual entry and ensuring 100% accuracy in ITR filing.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/dashboard">
                  <Button size="lg" className="w-full sm:w-auto">
                    <Calculator className="mr-2 h-5 w-5" />
                    Start ITR Filing
                  </Button>
                </Link>
                <Button variant="outline" size="lg" className="w-full sm:w-auto">
                  <Download className="mr-2 h-5 w-5" />
                  Download Sample
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 bg-muted/50">
          <div className="container">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Why Choose Our Automated ITR Solution?
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Experience the future of tax filing with our cutting-edge technology
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature, index) => (
                <Card key={index} className="text-center hover:shadow-lg transition-all duration-300 hover:scale-105">
                  <CardHeader>
                    <div className="flex justify-center mb-4">
                      {feature.icon}
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* ITR Forms Section */}
        <section className="py-20">
          <div className="container">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Supported ITR Forms
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                We support all major ITR forms with automated data extraction and processing
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {itrForms.map((form, index) => (
                <Card key={index} className={`${form.bgColor} border-none hover:shadow-xl transition-all duration-300 hover:scale-105`}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-xl font-bold">{form.form}</CardTitle>
                      <FileText className="h-6 w-6 text-primary" />
                    </div>
                    <CardDescription className="text-base">{form.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {form.features.map((feature, featureIndex) => (
                        <div key={featureIndex} className="flex items-center gap-2">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-sm">{feature}</span>
                        </div>
                      ))}
                    </div>
                    <Link to={`/automate-itr/${form.form.toLowerCase().split(' ')[0]}`} className="block mt-4">
                      <Button variant="outline" className="w-full">
                        Learn More
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-20 bg-muted/50">
          <div className="container">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                How Our AI Extraction Works
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Simple, secure, and accurate process in just 3 steps
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  step: "01",
                  title: "Upload Documents",
                  description: "Upload your Aadhar card, Form 16, and bank statements in PDF format",
                  icon: <FileText className="h-8 w-8" />
                },
                {
                  step: "02", 
                  title: "AI Processing",
                  description: "Our advanced AI extracts and validates all relevant tax data automatically",
                  icon: <Calculator className="h-8 w-8" />
                },
                {
                  step: "03",
                  title: "ITR Generated",
                  description: "Get your completed ITR form ready for filing with the IT department",
                  icon: <Download className="h-8 w-8" />
                }
              ].map((step, index) => (
                <div key={index} className="text-center">
                  <div className="bg-primary text-primary-foreground rounded-full w-16 h-16 flex items-center justify-center text-xl font-bold mx-auto mb-4">
                    {step.step}
                  </div>
                  <div className="flex justify-center mb-4 text-primary">
                    {step.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                  <p className="text-muted-foreground">{step.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
};

export default AutomateITR;