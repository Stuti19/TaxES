import { Button } from "@/components/ui/button";
import { ArrowRight, CheckCircle, FileText, Shield, Zap } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { useNavigate } from "react-router-dom";

export const Hero = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const handleStartFiling = () => {
    if (user) {
      navigate('/dashboard');
    } else {
      // This will be handled by the Header component's auth dialog
      document.getElementById('auth-button')?.click();
    }
  };

  return (
    <section className="relative py-20 md:py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5 animate-gradient-x bg-[length:400%_400%]" />
      
      <div className="container relative">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="space-y-4">
              <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
                <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                  AI-Powered
                </span>
                <br />
                Tax Filing Made
                <br />
                <span className="text-foreground">Simple</span>
              </h1>
              
              <p className="text-xl text-muted-foreground max-w-lg">
                Upload your documents, let our AI handle the rest. Get your ITR filed in minutes, not hours.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button 
                size="lg" 
                className="bg-gradient-to-r from-primary to-accent hover:shadow-lg transition-all duration-300"
                onClick={handleStartFiling}
              >
                {user ? 'Go to Dashboard' : 'Start Filing Now'}
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button variant="outline" size="lg">
                Watch Demo
              </Button>
            </div>

            <div className="flex items-center space-x-6 text-sm text-muted-foreground">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span>E-Filing Ready</span>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-4">
                <div className="bg-card p-6 rounded-xl border shadow-sm hover:shadow-lg transition-all duration-300 hover:scale-105 group">
                  <FileText className="h-8 w-8 text-primary mb-3 group-hover:scale-110 transition-transform" />
                  <h3 className="font-semibold mb-2">Upload Documents</h3>
                  <p className="text-sm text-muted-foreground">
                    Aadhar, Form 16 & Bank Statements
                  </p>
                </div>
                
                <div className="bg-card p-6 rounded-xl border shadow-sm hover:shadow-lg transition-all duration-300 hover:scale-105 group animate-pulse">
                  <Zap className="h-8 w-8 text-accent mb-3 group-hover:scale-110 transition-transform" />
                  <h3 className="font-semibold mb-2">AI Processing</h3>
                  <p className="text-sm text-muted-foreground">
                    Automatic data extraction & validation
                  </p>
                </div>
              </div>
              
              <div className="space-y-4 mt-8">
                <div className="bg-card p-6 rounded-xl border shadow-sm hover:shadow-lg transition-all duration-300 hover:scale-105 group">
                  <Shield className="h-8 w-8 text-green-500 mb-3 group-hover:scale-110 transition-transform" />
                  <h3 className="font-semibold mb-2">Secure & Compliant</h3>
                  <p className="text-sm text-muted-foreground">
                    Advanced security & compliance
                  </p>
                </div>
                
                <div className="bg-primary p-6 rounded-xl text-white hover:shadow-glow transition-all duration-300 hover:scale-105 cursor-pointer group">
                  <div className="text-2xl font-bold mb-1 group-hover:scale-110 transition-transform">Fast</div>
                  <p className="text-primary-foreground/80">Quick processing</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};