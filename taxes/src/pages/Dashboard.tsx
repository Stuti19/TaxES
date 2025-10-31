import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

import { 
  Upload, 
  FileText, 
  CreditCard, 
  BookOpen, 
  Eye,
  CheckCircle,
  Clock,
  Sparkles,
  Loader2
} from "lucide-react";
import { toast } from "sonner";
import { uploadDocumentsToAPI } from "@/services/apiService";

interface UploadedFile {
  id: string;
  name: string;
  type: string;
  file: File;
  uploadDate: Date;
}

export const Dashboard = () => {
  const { user, signOut } = useAuth();
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const documentTypes = [
    {
      id: "aadhar",
      name: "Aadhar Card",
      icon: CreditCard,
      description: "Upload your Aadhar Card PDF",
      color: "text-blue-500"
    },
    {
      id: "passbook",
      name: "Bank Passbook",
      icon: BookOpen,
      description: "Upload your Bank Passbook PDF",
      color: "text-green-500"
    },
    {
      id: "form16",
      name: "Form-16",
      icon: FileText,
      description: "Upload your Form-16 PDF",
      color: "text-orange-500"
    }
  ];

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>, docType: string) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
      toast.error("Please upload only PDF files");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error("File size should be less than 10MB");
      return;
    }

    const newFile: UploadedFile = {
      id: Date.now().toString(),
      name: file.name,
      type: docType,
      file,
      uploadDate: new Date()
    };

    setUploadedFiles(prev => [...prev, newFile]);
    toast.success("File uploaded successfully!");
  };

  const handlePreview = (file: UploadedFile) => {
    const url = URL.createObjectURL(file.file);
    setPreviewUrl(url);
    setSelectedFile(file);
  };



  const handleProcessDocuments = async () => {
    if (uploadedFiles.length < 3) {
      toast.error("Please upload all three documents (Aadhar, Bank Passbook, Form 16)");
      return;
    }

    if (!user?.id) {
      toast.error("User not authenticated");
      return;
    }

    const aadharFile = uploadedFiles.find(f => f.type === 'aadhar')?.file;
    const passbookFile = uploadedFiles.find(f => f.type === 'passbook')?.file;
    const form16File = uploadedFiles.find(f => f.type === 'form16')?.file;

    if (!aadharFile || !passbookFile || !form16File) {
      toast.error("Missing required documents");
      return;
    }

    setIsProcessing(true);
    
    // Test server connectivity first
    try {
      const testResponse = await fetch('http://localhost:8000/health');
      if (!testResponse.ok) {
        throw new Error('Server not reachable');
      }
      console.log('Server connectivity test passed');
    } catch (error) {
      toast.error('Cannot connect to server. Please check if the backend is running.');
      setIsProcessing(false);
      return;
    }
    
    try {
      toast.info("Uploading documents to secure cloud storage...");
      console.log('Starting document processing...');
      
      const result = await uploadDocumentsToAPI(
        user.id,
        aadharFile,
        passbookFile,
        form16File
      );
      
      console.log('Processing result:', result);
      
      if (result.success) {
        toast.success("Documents processed successfully! Redirecting to download page...");
        
        // Redirect to output page with session ID
        if (result.redirect_to) {
          setTimeout(() => {
            window.location.href = result.redirect_to;
          }, 2000);
        }
      } else {
        toast.error(result.message || "Processing failed. Please try again.");
      }
      
    } catch (error) {
      console.error('Error processing documents:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      toast.error(`Failed to process documents: ${errorMessage}`);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/3">
      {/* Professional Header */}
      <header className="border-b bg-card/95 backdrop-blur-sm sticky top-0 z-50 shadow-sm">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-primary to-accent rounded-lg flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                TaxES Pro
              </h1>
            </div>
            <Badge variant="secondary" className="bg-primary/10 text-primary">
              Professional Dashboard
            </Badge>
          </div>
          

        </div>
      </header>

      <div className="container py-8">


        <div className="grid lg:grid-cols-3 gap-8">
          {/* Upload Section */}
          <div className="lg:col-span-2 space-y-6">
            <div className="text-center lg:text-left">
              <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Document Management Center
              </h2>
              <p className="text-muted-foreground">
                Upload your tax documents to our secure, enterprise-grade platform for automated ITR processing
              </p>
            </div>

            <div className="grid gap-6">
              {documentTypes.map((docType) => {
                const uploadedFile = uploadedFiles.find(f => f.type === docType.id);
                
                return (
                  <Card key={docType.id} className="professional-card group">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="p-3 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 group-hover:from-primary/20 group-hover:to-accent/20 transition-all duration-300">
                            <docType.icon className={`h-6 w-6 ${docType.color} group-hover:scale-110 transition-transform duration-300`} />
                          </div>
                          <div>
                            <CardTitle className="text-lg font-semibold">{docType.name}</CardTitle>
                            <CardDescription className="text-sm">{docType.description}</CardDescription>
                          </div>
                        </div>
                        
                        {uploadedFile ? (
                          <div className="flex items-center space-x-2">
                            <CheckCircle className="h-5 w-5 text-green-500" />
                            <Badge variant="secondary" className="bg-green-100 text-green-700">
                              Uploaded
                            </Badge>
                          </div>
                        ) : (
                          <Badge variant="outline" className="border-amber-200 text-amber-700 bg-amber-50">
                            <Clock className="h-3 w-3 mr-1" />
                            Pending Upload
                          </Badge>
                        )}
                      </div>
                    </CardHeader>
                    
                    <CardContent>
                      {uploadedFile ? (
                        <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
                          <div>
                            <p className="font-medium text-sm">{uploadedFile.name}</p>
                            <p className="text-xs text-muted-foreground">
                              Uploaded on {uploadedFile.uploadDate.toLocaleDateString()}
                            </p>
                          </div>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handlePreview(uploadedFile)}
                            className="flex items-center space-x-2"
                          >
                            <Eye className="h-4 w-4" />
                            <span>Preview</span>
                          </Button>
                        </div>
                      ) : (
                        <div className="border-2 border-dashed border-muted-foreground/25 rounded-xl p-8 text-center group-hover:border-primary/50 group-hover:bg-primary/5 transition-all duration-300">
                          <div className="w-16 h-16 bg-gradient-to-br from-primary/10 to-accent/10 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                            <Upload className="h-8 w-8 text-primary" />
                          </div>
                          <p className="text-sm font-semibold mb-2">Upload Secure PDF Document</p>
                          <p className="text-xs text-muted-foreground mb-6">
                            Enterprise-grade security • Max 10MB • Encrypted storage
                          </p>
                          <label htmlFor={`upload-${docType.id}`} className="cursor-pointer">
                            <Button variant="outline" size="sm" className="hover:bg-primary hover:text-primary-foreground transition-all duration-300" asChild>
                              <span>Choose Professional File</span>
                            </Button>
                          </label>
                          <input
                            id={`upload-${docType.id}`}
                            type="file"
                            accept=".pdf"
                            className="hidden"
                            onChange={(e) => handleFileUpload(e, docType.id)}
                          />
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {uploadedFiles.length > 0 && (
              <Card className="mt-8 professional-card border-green-200 bg-gradient-to-r from-green-50 to-emerald-50">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center">
                      <CheckCircle className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <CardTitle className="text-green-800">Professional Processing Ready</CardTitle>
                      <CardDescription className="text-green-600">
                        All documents uploaded securely. Enterprise AI processing available.
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <Button 
                    size="lg" 
                    className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-lg hover:shadow-xl transition-all duration-300"
                    onClick={handleProcessDocuments}
                    disabled={isProcessing || uploadedFiles.length < 3}
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        Processing Documents...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-5 h-5 mr-2" />
                        Start Professional ITR Processing
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Preview Section */}
          <div className="space-y-6">
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Eye className="h-5 w-5" />
                  <span>Document Preview</span>
                </CardTitle>
                <CardDescription>
                  {selectedFile ? `Viewing: ${selectedFile.name}` : "Select a document to preview"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {previewUrl ? (
                  <div className="space-y-4">
                    <iframe
                      src={previewUrl}
                      className="w-full h-96 border rounded-lg"
                      title="Document Preview"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={() => {
                        setPreviewUrl(null);
                        setSelectedFile(null);
                      }}
                    >
                      Close Preview
                    </Button>
                  </div>
                ) : (
                  <div className="h-96 flex items-center justify-center border-2 border-dashed border-muted-foreground/25 rounded-lg">
                    <div className="text-center">
                      <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-sm text-muted-foreground">
                        Upload and select a document to preview
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};