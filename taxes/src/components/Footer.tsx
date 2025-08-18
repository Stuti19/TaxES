import { Facebook, Twitter, Linkedin, Mail, Phone, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";

export const Footer = () => {
  return (
    <footer className="bg-gradient-to-br from-primary/5 via-secondary/5 to-accent/5 border-t border-border/50">
      <div className="container mx-auto px-4 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Section */}
          <div className="space-y-4">
            <h3 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              TaxES
            </h3>
            <p className="text-muted-foreground text-sm leading-relaxed">
              Revolutionizing tax filing with intelligent automation and expert guidance. 
              Your trusted partner for accurate, secure, and efficient ITR processing.
            </p>
            <div className="flex space-x-3">
              <Button 
                variant="outline" 
                size="icon" 
                className="hover:bg-primary hover:text-primary-foreground hover:border-primary transition-all duration-300 hover:scale-110"
              >
                <Facebook className="h-4 w-4" />
              </Button>
              <Button 
                variant="outline" 
                size="icon" 
                className="hover:bg-primary hover:text-primary-foreground hover:border-primary transition-all duration-300 hover:scale-110"
              >
                <Twitter className="h-4 w-4" />
              </Button>
              <Button 
                variant="outline" 
                size="icon" 
                className="hover:bg-primary hover:text-primary-foreground hover:border-primary transition-all duration-300 hover:scale-110"
              >
                <Linkedin className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* ITR Forms */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-foreground">ITR Forms</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="hover:text-primary transition-colors cursor-pointer">ITR-1 Salary Income</li>
              <li className="hover:text-primary transition-colors cursor-pointer">ITR-2 Capital Gains</li>
              <li className="hover:text-primary transition-colors cursor-pointer">ITR-3 Business Income</li>
              <li className="hover:text-primary transition-colors cursor-pointer">ITR-4 Presumptive</li>
              <li className="hover:text-primary transition-colors cursor-pointer">GST Calculator</li>
            </ul>
          </div>

          {/* Professional Services */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-foreground">Professional Services</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="hover:text-primary transition-colors cursor-pointer">Tax Planning</li>
              <li className="hover:text-primary transition-colors cursor-pointer">Business Registration</li>
              <li className="hover:text-primary transition-colors cursor-pointer">Expert Consultation</li>
              <li className="hover:text-primary transition-colors cursor-pointer">Compliance Review</li>
              <li className="hover:text-primary transition-colors cursor-pointer">Document Management</li>
            </ul>
          </div>

          {/* Contact Info */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold text-foreground">Contact Info</h4>
            <div className="space-y-3 text-sm text-muted-foreground">
              <div className="flex items-center gap-3 group">
                <Mail className="h-4 w-4 text-primary group-hover:scale-110 transition-transform" />
                <span className="group-hover:text-primary transition-colors cursor-pointer">
                  ysahu0582@gmail.com
                </span>
              </div>
              <div className="flex items-center gap-3 group">
                <Phone className="h-4 w-4 text-primary group-hover:scale-110 transition-transform" />
                <span className="group-hover:text-primary transition-colors cursor-pointer">
                  +918349670829
                </span>
              </div>
              <div className="flex items-center gap-3 group">
                <MapPin className="h-4 w-4 text-primary group-hover:scale-110 transition-transform" />
                <span className="group-hover:text-primary transition-colors">
                  23 Sir M. Visvesvaraya Marg, Indore, Madhya Pradesh 452003, India
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-border/50 pt-8 mt-8">
          <div className="flex flex-col md:flex-row justify-center items-center gap-4">
            <div className="flex gap-6 text-sm text-muted-foreground">
              <span className="hover:text-primary transition-colors cursor-pointer">Privacy</span>
              <span className="hover:text-primary transition-colors cursor-pointer">Terms</span>
              <span className="hover:text-primary transition-colors cursor-pointer">Cookies</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};