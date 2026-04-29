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

export interface WizardSectionResponse {
  success: boolean;
  message: string;
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
      signal: AbortSignal.timeout(600000), // 10 minutes timeout
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

// ────────────── WIZARD API ENDPOINTS ──────────────

export const saveHousePropertyInput = async (
  data: Record<string, any>
): Promise<WizardSectionResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/user-inputs/house-property`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || 'Failed to save house property data');
    }

    return result;
  } catch (error) {
    console.error('House property API error:', error);
    throw error;
  }
};

export const saveOtherIncomeInput = async (
  data: Record<string, any>
): Promise<WizardSectionResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/user-inputs/other-income`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || 'Failed to save other income data');
    }

    return result;
  } catch (error) {
    console.error('Other income API error:', error);
    throw error;
  }
};

export const saveDeductionsInput = async (
  data: Record<string, any>
): Promise<WizardSectionResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/user-inputs/deductions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || 'Failed to save deductions data');
    }

    return result;
  } catch (error) {
    console.error('Deductions API error:', error);
    throw error;
  }
};

export const fillExcelWithInputs = async (): Promise<WizardSectionResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/fill-excel-with-inputs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({}),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.message || 'Failed to fill Excel with user inputs');
    }

    return result;
  } catch (error) {
    console.error('Fill Excel API error:', error);
    throw error;
  }
};