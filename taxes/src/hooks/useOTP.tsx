import { useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";

export const useOTP = () => {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const sendOTP = async (mobileNumber: string) => {
    setLoading(true);
    try {
      // Generate a random 6-digit OTP
      const otp = Math.floor(100000 + Math.random() * 900000).toString();
      const expiresAt = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes from now

      // In a real application, you would integrate with an SMS service like Twilio
      // For now, we'll store the OTP in the database and show it in the toast
      const { data: { user } } = await supabase.auth.getUser();
      
      if (user) {
        const { error } = await supabase
          .from('profiles')
          .update({
            otp_code: otp,
            otp_expires_at: expiresAt.toISOString(),
            mobile_number: mobileNumber
          })
          .eq('id', user.id);

        if (error) throw error;

        // In production, send SMS here
        toast({
          title: "OTP Sent",
          description: `OTP: ${otp} (Demo mode - check console)`,
        });
        
        console.log(`Demo OTP for ${mobileNumber}: ${otp}`);
        return { success: true };
      }
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  const verifyOTP = async (otp: string) => {
    setLoading(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (user) {
        const { data: profile, error } = await supabase
          .from('profiles')
          .select('otp_code, otp_expires_at')
          .eq('id', user.id)
          .single();

        if (error) throw error;

        if (!profile.otp_code) {
          throw new Error("No OTP found. Please request a new one.");
        }

        if (new Date() > new Date(profile.otp_expires_at)) {
          throw new Error("OTP has expired. Please request a new one.");
        }

        if (profile.otp_code !== otp) {
          throw new Error("Invalid OTP. Please try again.");
        }

        // Mark mobile as verified
        const { error: updateError } = await supabase
          .from('profiles')
          .update({
            mobile_verified: true,
            otp_code: null,
            otp_expires_at: null
          })
          .eq('id', user.id);

        if (updateError) throw updateError;

        toast({
          title: "Success!",
          description: "Mobile number verified successfully.",
        });
        
        return { success: true };
      }
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message,
      });
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  };

  return { sendOTP, verifyOTP, loading };
};