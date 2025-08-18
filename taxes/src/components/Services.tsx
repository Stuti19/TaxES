import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, Calculator, Shield, Users, Clock, TrendingUp } from "lucide-react";
import taxAutomation from "@/assets/tax-automation.jpg";
import taxServices from "@/assets/tax-services.jpg";
import taxSecurity from "@/assets/tax-security.jpg";

export const Services = () => {
  const services = [
    {
      title: "Automate ITR Data Extract",
      description: "Advanced AI-powered technology automatically extracts and processes your financial data from multiple sources, ensuring accurate ITR filing with minimal manual intervention.",
      features: ["Auto Bank Statement Analysis", "Digital Receipt Processing", "Smart Tax Calculation", "Error Detection & Correction"],
      icon: Calculator,
      image: taxAutomation,
      badge: "Popular"
    },
    {
      title: "Professional Tax Consultation",
      description: "Get expert guidance from certified tax professionals who understand the complexities of Indian tax law and can help optimize your tax planning strategies.",
      features: ["One-on-One Consultation", "Tax Planning Strategy", "Investment Advisory", "Compliance Review"],
      icon: Users,
      image: taxServices,
      badge: "Expert"
    },
    {
      title: "Automate Data Extraction Based Services",
      description: "Advanced automation technology extracts data from multiple sources with enterprise-grade security measures while ensuring full compliance with Indian tax regulations and IT department guidelines.",
      features: ["256-bit Encryption", "IT Department Approved", "Data Privacy Guarantee", "Audit Trail"],
      icon: Shield,
      image: taxSecurity,
      badge: "Automated"
    }
  ];

  const additionalServices = [
    {
      title: "Document Management",
      description: "Centralized storage and organization of all your tax documents",
      icon: FileText
    },
    {
      title: "Real-time Processing",
      description: "Get instant updates on your tax filing status and processing",
      icon: Clock
    },
    {
      title: "Tax Analytics",
      description: "Detailed insights and analytics on your tax patterns and savings",
      icon: TrendingUp
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-secondary/20 to-accent/10">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Our Services
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Comprehensive tax solutions designed to simplify your ITR filing process and maximize your tax savings
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {services.map((service, index) => (
            <Card 
              key={index} 
              className="group hover:shadow-[var(--shadow-hover)] transition-all duration-500 transform hover:-translate-y-2 border-0 bg-card/50 backdrop-blur-sm"
            >
              <div className="relative overflow-hidden rounded-t-lg">
                <img 
                  src={service.image} 
                  alt={service.title}
                  className="w-full h-48 object-cover transition-transform duration-500 group-hover:scale-110"
                />
                <div className="absolute top-4 right-4">
                  <Badge variant="secondary" className="bg-primary text-primary-foreground">
                    {service.badge}
                  </Badge>
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              </div>
              
              <CardHeader className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                    <service.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl group-hover:text-primary transition-colors">
                    {service.title}
                  </CardTitle>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <p className="text-muted-foreground leading-relaxed">
                  {service.description}
                </p>
                <ul className="space-y-2">
                  {service.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-sm">
                      <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {additionalServices.map((service, index) => (
            <Card 
              key={index}
              className="group hover:shadow-[var(--shadow-elegant)] transition-all duration-300 transform hover:-translate-y-1 bg-card/30 backdrop-blur-sm border border-border/50"
            >
              <CardContent className="p-6 text-center">
                <div className="inline-flex p-3 rounded-full bg-gradient-to-br from-primary/10 to-accent/10 mb-4 group-hover:from-primary/20 group-hover:to-accent/20 transition-all duration-300">
                  <service.icon className="h-8 w-8 text-primary group-hover:scale-110 transition-transform duration-300" />
                </div>
                <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">
                  {service.title}
                </h3>
                <p className="text-muted-foreground text-sm">
                  {service.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};