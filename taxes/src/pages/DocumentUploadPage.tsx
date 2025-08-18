import React, { useEffect, useState } from 'react';
import { DocumentUpload } from '@/components/DocumentUpload';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, CheckCircle, XCircle } from 'lucide-react';
import { supabase } from '@/integrations/supabase/client';
import { documentService, UserDocuments } from '@/services/documentService';
import { useToast } from '@/components/ui/use-toast';

export const DocumentUploadPage: React.FC = () => {
  const [userDocuments, setUserDocuments] = useState<UserDocuments | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  const fetchUserDocuments = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const documents = await documentService.getUserDocuments(user.id);
      setUserDocuments(documents);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch document status",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserDocuments();
  }, []);

  const handleUploadComplete = () => {
    fetchUserDocuments();
    toast({
      title: "Success",
      description: "Documents uploaded successfully!",
    });
  };

  const DocumentStatus = ({ 
    docType, 
    label, 
    status 
  }: { 
    docType: string; 
    label: string; 
    status: { exists: boolean; s3_url?: string } 
  }) => (
    <div className="flex items-center justify-between p-3 border rounded-lg">
      <div className="flex items-center space-x-3">
        <FileText className="h-5 w-5 text-gray-500" />
        <span className="font-medium">{label}</span>
      </div>
      <div className="flex items-center space-x-2">
        {status.exists ? (
          <>
            <CheckCircle className="h-5 w-5 text-green-500" />
            <Badge variant="default" className="bg-green-100 text-green-800">
              Uploaded
            </Badge>
          </>
        ) : (
          <>
            <XCircle className="h-5 w-5 text-red-500" />
            <Badge variant="secondary" className="bg-red-100 text-red-800">
              Missing
            </Badge>
          </>
        )}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Tax Document Upload</h1>
        <p className="text-gray-600">
          Upload your Aadhar, PAN, and Form 16 documents for tax processing
        </p>
      </div>

      {userDocuments && (
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>Document Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <DocumentStatus
              docType="aadhar"
              label="Aadhar Card"
              status={userDocuments.documents.aadhar}
            />
            <DocumentStatus
              docType="pan"
              label="PAN Card"
              status={userDocuments.documents.pan}
            />
            <DocumentStatus
              docType="form16"
              label="Form 16"
              status={userDocuments.documents.form16}
            />
          </CardContent>
        </Card>
      )}

      <DocumentUpload onUploadComplete={handleUploadComplete} />
    </div>
  );
};