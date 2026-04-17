export const API_BASE_URL = 'http://127.0.0.1:5000';

export interface TriageResponse {
  mode: 'medical' | 'chat';
  reply?: string;
  symptoms?: string[];
  risk?: string;
  doctor?: string;
  advice?: string;
  severity?: number;
  recommended_doctors?: any[];
}

export const api = {

  // ================= NORMAL TRIAGE =================
  async triage(message: string, userId?: number): Promise<TriageResponse> {
    try {
      console.warn("Using fallback triage (non-stream)");

      const response = await fetch(`${API_BASE_URL}/triage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, user_id: userId }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      return await response.json();

    } catch (error) {
      console.error('Error calling triage API:', error);
      throw error;
    }
  },

  // ================= STREAM TRIAGE =================
  async triageStream(
    message: string,
    onChunk: (data: any) => void,
    userId?: number
  ): Promise<void> {

    try {
      const response = await fetch(`${API_BASE_URL}/triage`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message, user_id: userId }),
      });

      if (!response.ok) {
        throw new Error('Network error');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Stream reader not available');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode chunk
        buffer += decoder.decode(value, { stream: true });

        // Split lines
        let lines = buffer.split('\n');

        // Keep last incomplete line
        buffer = lines.pop() || '';

        for (let line of lines) {
          line = line.trim();
          if (!line) continue;

          try {
            const parsed = JSON.parse(line);

            // 🔍 Debug log (you can remove later)
            console.log("STREAM DATA:", parsed);

            onChunk(parsed);

          } catch (err) {
            console.error('JSON parse error:', line);
          }
        }
      }

    } catch (error) {
      console.error('Error in triageStream:', error);
      throw error;
    }
  },  // ✅ IMPORTANT COMMA FIXED HERE


  // ================= LOGIN =================
  async login(data: any): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.message || 'Login failed');
    }

    return response.json();
  },


  // ================= SIGNUP =================
  async signup(data: any): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.message || 'Signup failed');
    }

    return response.json();
  },


  // ================= QUEUE =================
  async getQueue(): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/queue`);

    if (!response.ok) {
      throw new Error('Failed to fetch queue');
    }

    return response.json();
  },
  //=====Suggestion=======
  async getSymptoms(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/symptoms`);
  if (!response.ok) throw new Error('Failed to fetch symptoms');
  return response.json();
},


  // ================= DOCTOR RECOMMEND =================
  async getRecommendations(symptoms: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }

      return await response.json();

    } catch (error) {
      console.error('Error fetching recommendations:', error);
      return [];
    }
  },

  // ================= VITALS ANALYSIS =================
  async analyzeVitals(videoBlob: Blob): Promise<any> {
    try {
      const formData = new FormData();
      formData.append('video', videoBlob, 'video.webm');

      const response = await fetch(`${API_BASE_URL}/analyze_vitals`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error((errorData && errorData.error) || 'Network error during vitals analysis');
      }

      return await response.json();
    } catch (error: any) {
      console.error('Error analyzing vitals:', error);
      return { error: error.message || 'Failed to analyze vitals' };
    }
  },
};