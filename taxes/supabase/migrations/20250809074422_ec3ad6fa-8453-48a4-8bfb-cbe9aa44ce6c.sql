-- Create table for ITR processing steps
CREATE TABLE public.itr_processes (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  itr_type TEXT NOT NULL CHECK (itr_type IN ('ITR-1', 'ITR-2', 'ITR-3', 'ITR-4')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  uploaded_documents JSONB DEFAULT '{}',
  extracted_data JSONB DEFAULT '{}',
  form_data JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.itr_processes ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view their own ITR processes" 
ON public.itr_processes 
FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own ITR processes" 
ON public.itr_processes 
FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own ITR processes" 
ON public.itr_processes 
FOR UPDATE 
USING (auth.uid() = user_id);

-- Update profiles table to include mobile number and verification
ALTER TABLE public.profiles 
ADD COLUMN mobile_number TEXT,
ADD COLUMN mobile_verified BOOLEAN DEFAULT false,
ADD COLUMN email_verified BOOLEAN DEFAULT false,
ADD COLUMN otp_code TEXT,
ADD COLUMN otp_expires_at TIMESTAMP WITH TIME ZONE;

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic timestamp updates on ITR processes
CREATE TRIGGER update_itr_processes_updated_at
BEFORE UPDATE ON public.itr_processes
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Create storage bucket for ITR documents
INSERT INTO storage.buckets (id, name, public) 
VALUES ('itr-documents', 'itr-documents', false);

-- Create storage policies for ITR documents
CREATE POLICY "Users can view their own ITR documents" 
ON storage.objects 
FOR SELECT 
USING (bucket_id = 'itr-documents' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can upload their own ITR documents" 
ON storage.objects 
FOR INSERT 
WITH CHECK (bucket_id = 'itr-documents' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can update their own ITR documents" 
ON storage.objects 
FOR UPDATE 
USING (bucket_id = 'itr-documents' AND auth.uid()::text = (storage.foldername(name))[1]);