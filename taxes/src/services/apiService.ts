const API_BASE_URL = 'http://localhost:8000';

export interface UploadDocumentsResponse {
  success: boolean;
  message: string;
  session_id?: string;
  extraction_results?: any;
  parsing_results?: any;
  excel_result?: any;
  output_files?: any;
  redirect_to?: string;
}

export const uploadDocumentsToAPI = async (
  userId: string,
  aadharFile: File,
  passbookFile: File,
  form16File: File,
  email?: string,
  mobileNo?: string
): Promise<UploadDocumentsResponse> => {
  try {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('aadhar', aadharFile);
    formData.append('passbook', passbookFile);
    formData.append('form16', form16File);
    if (email) formData.append('email', email);
    if (mobileNo) formData.append('mobile_no', mobileNo);

    console.log('Sending request to:', `${API_BASE_URL}/process-documents`);
    
    const response = await fetch(`${API_BASE_URL}/process-documents`, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
      },
      signal: AbortSignal.timeout(300000), // 5 minutes timeout
    });

    console.log('Response status:', response.status);
    
    const responseText = await response.text();
    console.log('Raw response:', responseText);
    
    if (!response.ok) {
      console.error('Response error:', responseText);
      throw new Error(`Processing failed: ${response.statusText}`);
    }

    let result;
    try {
      result = JSON.parse(responseText);
    } catch (parseError) {
      console.error('JSON parse error:', parseError);
      throw new Error('Invalid response format from server');
    }
    
    console.log('Parsed response data:', result);
    return result;
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};