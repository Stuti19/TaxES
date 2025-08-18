import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Upload, FileText, CheckCircle } from 'lucide-react';
import { useToast } from './ui/use-toast';
import { supabase } from '@/integrations/supabase/client';

interface DocumentUploadProps {
  onUploadComplete?: (uploadedFiles: any[]) => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUploadComplete }) => {
  const [files, setFiles] = useState<{
    aadhar: File | null;
    pan: File | null;
    form16: File | null;
  }>({
    aadhar: null,
    pan: null,
    form16: null,
  });
  
  const [uploading, setUploading] = useState(false);
  const { toast } = useToast();

  const handleFileChange = (docType: 'aadhar' | 'pan' | 'form16', file: File | null) => {
    if (file && !file.name.toLowerCase().endsWith('.pdf')) {
      toast({
        title: "Invalid file type",
        description: "Please upload only PDF files",
        variant: "destructive",
      });
      return;
    }
    
    setFiles(prev => ({ ...prev, [docType]: file }));
  };

  const handleUpload = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      toast({
        title: "Authentication required",
        description: "Please log in to upload documents",
        variant: "destructive",
      });
      return;
    }

    if (!files.aadhar || !files.pan || !files.form16) {
      toast({
        title: "Missing documents",
        description: "Please select all three PDF documents",
        variant: "destructive",
      });
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('user_id', user.id);
      formData.append('aadhar', files.aadhar);
      formData.append('pan', files.pan);
      formData.append('form16', files.form16);

      const response = await fetch('http://localhost:8000/upload-documents', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok) {
        toast({
          title: "Upload successful",
          description: "All documents uploaded successfully",
        });
        
        onUploadComplete?.(result.uploaded_files);
        
        // Reset files
        setFiles({ aadhar: null, pan: null, form16: null });
      } else {
        throw new Error(result.detail || 'Upload failed');
      }
    } catch (error) {
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : "An error occurred",
        variant: "destructive",
      });
    } finally {
      setUploading(false);
    }
  };

  const DocumentInput = ({ 
    docType, 
    label, 
    description 
  }: { 
    docType: 'aadhar' | 'pan' | 'form16'; 
    label: string; 
    description: string;
  }) => (
    <div className="space-y-2">
      <Label htmlFor={docType} className="text-sm font-medium">
        {label}
      </Label>
      <div className="flex items-center space-x-2">
        <Input
          id={docType}
          type="file"
          accept=".pdf"
          onChange={(e) => handleFileChange(docType, e.target.files?.[0] || null)}
          className="flex-1"
        />
        {files[docType] && (
          <CheckCircle className="h-5 w-5 text-green-500" />
        )}
      </div>
      <p className="text-xs text-gray-500">{description}</p>
    </div>
  );

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <FileText className="h-6 w-6" />
          <span>Upload Tax Documents</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <DocumentInput
          docType="aadhar"
          label="Aadhar Card"
          description="Upload your Aadhar card PDF"
        />
        
        <DocumentInput
          docType="pan"
          label="PAN Card"
          description="Upload your PAN card PDF"
        />
        
        <DocumentInput
          docType="form16"
          label="Form 16"
          description="Upload your Form 16 PDF"
        />

        <Button
          onClick={handleUpload}
          disabled={uploading || !files.aadhar || !files.pan || !files.form16}
          className="w-full"
        >
          {uploading ? (
            <>
              <Upload className="mr-2 h-4 w-4 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="mr-2 h-4 w-4" />
              Upload Documents
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};