const API_BASE_URL = 'http://localhost:8000/api/v1';

export const startWebScan = async (targetUrl: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/scanners/web`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ target_url: targetUrl }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error starting web scan:', error);
    throw error;
  }
};

export const getScanStatus = async (scanId: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/scanners/web/${scanId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error getting scan status:', error);
    throw error;
  }
};
