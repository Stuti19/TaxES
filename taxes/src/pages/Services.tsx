import { Navigation } from "@/components/Navigation";
import { Footer } from "@/components/Footer";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText, Calculator, Building, Receipt, Users, Shield, Clock, Star } from "lucide-react";

const Services = () => {
  const services = [
    {
      icon: <FileText className="h-12 w-12 text-primary" />,
      title: "Tax Filing Services",
      description: "Complete ITR filing for individuals and businesses with expert guidance",
      features: ["ITR-1 to ITR-7", "E-filing Support", "Expert Review", "Quick Processing"],
      price: "Starting ₹499",
      bgColor: "bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20"
    },
    {
      icon: <Calculator className="h-12 w-12 text-green-500" />,
      title: "Tax Planning",
      description: "Strategic tax planning to minimize your tax liability legally",
      features: ["Investment Planning", "Tax Saving Options", "Advance Tax Calculation", "Year-end Planning"],
      price: "Starting ₹999",
      bgColor: "bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20"
    },
    {
      icon: <Building className="h-12 w-12 text-purple-500" />,
      title: "Business Registration",
      description: "Complete business registration and compliance services",
      features: ["Company Incorporation", "LLP Registration", "Partnership Deed", "Trade License"],
      price: "Starting ₹2,999",
      bgColor: "bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20"
    },
    {
      icon: <Receipt className="h-12 w-12 text-orange-500" />,
      title: "GST Services",
      description: "Complete GST registration, filing, and compliance management",
      features: ["GST Registration", "Monthly Returns", "Annual Returns", "GST Planning"],
      price: "Starting ₹1,499",
      bgColor: "bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20"
    }
  ];

  const whyChooseUs = [
    {
      icon: <Users className="h-8 w-8 text-primary" />,
      title: "Expert Team",
      description: "Certified chartered accountants and tax professionals"
    },
    {
      icon: <Shield className="h-8 w-8 text-green-500" />,
      title: "100% Secure",
      description: "Bank-grade security for all your financial data"
    },
    {
      icon: <Clock className="h-8 w-8 text-blue-500" />,
      title: "Quick Service",
      description: "Fast turnaround time with quality assurance"
    },
    {
      icon: <Star className="h-8 w-8 text-accent" />,
      title: "Customer Satisfaction",
      description: "99% customer satisfaction rate with 24/7 support"
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
                Professional Tax Services
              </Badge>
              <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
                Comprehensive Tax & Business Services
              </h1>
              <p className="text-xl text-muted-foreground mb-8 leading-relaxed">
                From tax filing to business registration, we provide end-to-end financial and 
                legal services to help your business grow and stay compliant.
              </p>
            </div>
          </div>
        </section>

        {/* Services Grid */}
        <section className="py-20">
          <div className="container">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Our Services
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Professional services tailored to meet your tax and business needs
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {services.map((service, index) => (
                <Card key={index} className={`${service.bgColor} border-none hover:shadow-xl transition-all duration-300 hover:scale-105`}>
                  <CardHeader>
                    <div className="flex items-center gap-4 mb-4">
                      {service.icon}
                      <div>
                        <CardTitle className="text-xl">{service.title}</CardTitle>
                        <Badge variant="outline" className="mt-1">{service.price}</Badge>
                      </div>
                    </div>
                    <CardDescription className="text-base">{service.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 mb-6">
                      {service.features.map((feature, featureIndex) => (
                        <div key={featureIndex} className="flex items-center gap-2">
                          <div className="w-2 h-2 bg-primary rounded-full" />
                          <span className="text-sm">{feature}</span>
                        </div>
                      ))}
                    </div>
                    <Button className="w-full">
                      Get Started
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Why Choose Us */}
        <section className="py-20 bg-muted/50">
          <div className="container">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Why Choose TaxES?
              </h2>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                We're committed to providing exceptional service and results
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {whyChooseUs.map((item, index) => (
                <Card key={index} className="text-center hover:shadow-lg transition-all duration-300 hover:scale-105">
                  <CardHeader>
                    <div className="flex justify-center mb-4">
                      {item.icon}
                    </div>
                    <CardTitle className="text-lg">{item.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription>{item.description}</CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20">
          <div className="container">
            <div className="text-center max-w-2xl mx-auto">
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Ready to Get Started?
              </h2>
              <p className="text-xl text-muted-foreground mb-8">
                Let our experts handle your tax and business needs while you focus on what matters most.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button size="lg">
                  <Calculator className="mr-2 h-5 w-5" />
                  Start Tax Filing
                </Button>
                <Button variant="outline" size="lg">
                  <Users className="mr-2 h-5 w-5" />
                  Consult Expert
                </Button>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
};

export default Services;