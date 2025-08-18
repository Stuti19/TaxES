const API_BASE_URL = 'http://localhost:8000';

export interface DocumentStatus {
  exists: boolean;
  s3_key?: string;
  s3_url?: string;
}

export interface UserDocuments {
  user_id: string;
  documents: {
    aadhar: DocumentStatus;
    pan: DocumentStatus;
    form16: DocumentStatus;
  };
}

export const documentService = {
  async getUserDocuments(userId: string): Promise<UserDocuments> {
    const response = await fetch(`${API_BASE_URL}/user-documents/${userId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch user documents');
    }
    return response.json();
  },

  async uploadDocuments(
    userId: string,
    files: {
      aadhar: File;
      pan: File;
      form16: File;
    }
  ) {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('aadhar', files.aadhar);
    formData.append('pan', files.pan);
    formData.append('form16', files.form16);

    const response = await fetch(`${API_BASE_URL}/upload-documents`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  },
};