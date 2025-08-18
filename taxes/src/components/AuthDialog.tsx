import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/useAuth";
import { MobileVerification } from "./MobileVerification";
import { Mail, AlertCircle, User, Lock, Phone } from "lucide-react";

interface AuthDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: 'login' | 'signup';
  onModeChange: (mode: 'login' | 'signup') => void;
}

export const AuthDialog = ({ open, onOpenChange, mode, onModeChange }: AuthDialogProps) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [showMobileVerification, setShowMobileVerification] = useState(false);
  const { toast } = useToast();
  const { signUp, signIn, signInWithGoogle } = useAuth();

  const handleGoogleSignIn = async () => {
    setLoading(true);
    try {
      const { error } = await signInWithGoogle();
      if (error) throw error;
      
      toast({
        title: "Redirecting...",
        description: "You'll be redirected to Google for authentication.",
      });
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (mode === 'signup') {
        const { error } = await signUp(email, password, name);
        
        if (error) throw error;
        
        toast({
          title: "Account Created!",
          description: "Please check your email to verify your account.",
        });
        setShowMobileVerification(true);
      } else {
        const { error } = await signIn(email, password);
        
        if (error) throw error;
        
        toast({
          title: "Welcome back!",
          description: "You have successfully logged in.",
        });
        onOpenChange(false);
      }
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
    } finally {
      setLoading(false);
    }
  };

  if (showMobileVerification) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-center text-2xl font-bold">
              Complete Setup
            </DialogTitle>
          </DialogHeader>
          <MobileVerification 
            onVerified={() => {
              setShowMobileVerification(false);
              onOpenChange(false);
            }}
            onSkip={() => {
              setShowMobileVerification(false);
              onOpenChange(false);
            }}
          />
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-center text-2xl font-bold flex items-center justify-center gap-2">
            <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center">
              {mode === 'login' ? <Lock className="w-4 h-4 text-primary" /> : <User className="w-4 h-4 text-primary" />}
            </div>
            {mode === 'login' ? 'Welcome Back' : 'Create Account'}
          </DialogTitle>
        </DialogHeader>
        
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-primary/5 to-accent/5 border border-primary/20 rounded-lg p-4">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                <Mail className="w-6 h-6 text-primary" />
              </div>
              <p className="text-sm font-medium">Secure & Professional Platform</p>
              <p className="text-xs text-muted-foreground">Your data is protected with enterprise-grade security</p>
            </div>
          </div>

          <Button 
            onClick={handleGoogleSignIn}
            variant="outline" 
            className="w-full h-12 text-base border-2 hover:bg-primary/5 transition-all duration-300"
            disabled={loading}
          >
            <Mail className="mr-2 h-5 w-5" />
            Continue with Google
          </Button>
          
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                Or continue with email
              </span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'signup' && (
              <div>
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="mt-1"
                />
              </div>
            )}
            
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="mt-1"
              />
            </div>
            
            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="mt-1"
              />
            </div>
            
            <Button 
              type="submit" 
              className="w-full h-12 bg-gradient-to-r from-primary to-accent hover:shadow-glow transition-all duration-300"
              disabled={loading}
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Processing...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  {mode === 'login' ? <Lock className="w-4 h-4" /> : <User className="w-4 h-4" />}
                  {mode === 'login' ? 'Sign In to Continue' : 'Create Professional Account'}
                </div>
              )}
            </Button>
          </form>
          
          <div className="text-center space-y-2">
            <Button
              variant="link"
              onClick={() => onModeChange(mode === 'login' ? 'signup' : 'login')}
              className="text-sm hover:text-primary transition-colors"
            >
              {mode === 'login' 
                ? "New user? Create professional account →" 
                : "Already registered? Sign in to continue →"
              }
            </Button>
            
            <p className="text-xs text-muted-foreground">
              {mode === 'login' 
                ? "Join thousands of professionals using our platform" 
                : "Secure, fast, and reliable tax solutions"
              }
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};