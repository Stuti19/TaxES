const API_BASE_URL = 'http://localhost:8000';

export interface UploadDocumentsResponse {
  success: boolean;
  message: string;
  uploaded_files: Array<{
    document_type: string;
    filename: string;
    s3_key: string;
    s3_url: string;
  }>;
}

export const uploadDocumentsToAPI = async (
  userId: string,
  aadharFile: File,
  panFile: File,
  form16File: File
): Promise<UploadDocumentsResponse> => {
  const formData = new FormData();
  formData.append('user_id', userId);
  formData.append('aadhar', aadharFile);
  formData.append('pan', panFile);
  formData.append('form16', form16File);

  const response = await fetch(`${API_BASE_URL}/upload-documents`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }

  return response.json();
};