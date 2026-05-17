import axios from 'axios';
import type { AnalysisResult, AgentEvent } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// Derive WebSocket URL from API URL: https → wss, http → ws
const WS_URL = import.meta.env.VITE_WS_URL ||
  API_URL.replace(/^https:\/\//, 'wss://').replace(/^http:\/\//, 'ws://');

export const api = axios.create({ baseURL: API_URL });

export async function uploadContract(file: File): Promise<{ analysis_id: string }> {
  const form = new FormData();
  form.append('file', file);
  const res = await api.post('/api/analyze', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function getAnalysis(analysisId: string): Promise<AnalysisResult> {
  const res = await api.get(`/api/analysis/${analysisId}`);
  return res.data;
}

export function createWebSocket(
  analysisId: string,
  onMessage: (event: AgentEvent) => void,
  onComplete: (analysisId: string) => void,
  onError: (msg: string) => void
): WebSocket {
  const ws = new WebSocket(`${WS_URL}/ws/analysis/${analysisId}`);
  ws.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      if (data.status === 'complete') {
        onComplete(data.analysis_id || analysisId);
      } else if (data.status === 'error') {
        onError(data.message || 'Unknown error');
      } else {
        onMessage(data as AgentEvent);
      }
    } catch {
      /* ignore parse errors */
    }
  };
  ws.onerror = () => onError('WebSocket connection failed');
  return ws;
}
