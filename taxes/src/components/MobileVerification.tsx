import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@/components/ui/input-otp";
import { useOTP } from "@/hooks/useOTP";
import { Phone, Shield } from "lucide-react";

interface MobileVerificationProps {
  onVerified: () => void;
  onSkip?: () => void;
}

export const MobileVerification = ({ onVerified, onSkip }: MobileVerificationProps) => {
  const [mobileNumber, setMobileNumber] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState<'mobile' | 'otp'>('mobile');
  const { sendOTP, verifyOTP, loading } = useOTP();

  const handleSendOTP = async () => {
    if (mobileNumber.length !== 10) {
      return;
    }
    
    const result = await sendOTP(mobileNumber);
    if (result.success) {
      setStep('otp');
    }
  };

  const handleVerifyOTP = async () => {
    if (otp.length !== 6) {
      return;
    }
    
    const result = await verifyOTP(otp);
    if (result.success) {
      onVerified();
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
          {step === 'mobile' ? (
            <Phone className="w-8 h-8 text-primary" />
          ) : (
            <Shield className="w-8 h-8 text-primary" />
          )}
        </div>
        <h3 className="text-xl font-semibold">
          {step === 'mobile' ? 'Verify Mobile Number' : 'Enter OTP'}
        </h3>
        <p className="text-muted-foreground text-sm">
          {step === 'mobile' 
            ? 'We need to verify your mobile number for secure access'
            : `Enter the 6-digit code sent to +91 ${mobileNumber}`
          }
        </p>
      </div>

      {step === 'mobile' ? (
        <div className="space-y-4">
          <div>
            <Label htmlFor="mobile">Mobile Number</Label>
            <div className="flex mt-1">
              <div className="flex items-center px-3 border border-r-0 rounded-l-md bg-muted text-muted-foreground">
                +91
              </div>
              <Input
                id="mobile"
                type="tel"
                placeholder="Enter 10-digit mobile number"
                value={mobileNumber}
                onChange={(e) => setMobileNumber(e.target.value.replace(/\D/g, '').slice(0, 10))}
                className="rounded-l-none"
                maxLength={10}
              />
            </div>
          </div>
          
          <Button 
            onClick={handleSendOTP}
            disabled={mobileNumber.length !== 10 || loading}
            className="w-full"
          >
            {loading ? 'Sending...' : 'Send OTP'}
          </Button>
          
          {onSkip && (
            <Button 
              variant="ghost" 
              onClick={onSkip}
              className="w-full text-muted-foreground"
            >
              Skip for now
            </Button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Enter OTP</Label>
            <div className="flex justify-center">
              <InputOTP maxLength={6} value={otp} onChange={setOtp}>
                <InputOTPGroup>
                  <InputOTPSlot index={0} />
                  <InputOTPSlot index={1} />
                  <InputOTPSlot index={2} />
                  <InputOTPSlot index={3} />
                  <InputOTPSlot index={4} />
                  <InputOTPSlot index={5} />
                </InputOTPGroup>
              </InputOTP>
            </div>
          </div>
          
          <Button 
            onClick={handleVerifyOTP}
            disabled={otp.length !== 6 || loading}
            className="w-full"
          >
            {loading ? 'Verifying...' : 'Verify OTP'}
          </Button>
          
          <div className="text-center">
            <Button 
              variant="link" 
              onClick={() => setStep('mobile')}
              className="text-sm text-muted-foreground"
            >
              Change mobile number
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};