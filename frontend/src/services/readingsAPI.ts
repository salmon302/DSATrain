import { apiService, getCurrentUserId } from './api';

export interface ReadingMaterial {
  id: string;
  title: string;
  subtitle?: string;
  author?: string;
  content_type: string;
  difficulty_level: string;
  estimated_read_time: number;
  tags?: string[];
  summary?: string;
  thumbnail_url?: string;
  user_ratings?: number;
  total_ratings?: number;
  view_count?: number;
  status?: string;
  published_at?: string | null;
  created_at?: string | null;
  // optional content fields
  content_markdown?: string;
  content_sections?: Array<{ title: string }>;
  prerequisite_materials?: string[];
  follow_up_materials?: string[];
  user_progress?: any;
}

export const readingsAPI = {
  search: async (params: {
    query: string;
    content_type?: string;
    difficulty_level?: string;
    concept_ids?: string[];
    limit?: number;
  }) => {
    const user_id = getCurrentUserId();
    const response = await apiService.get('/reading-materials/search', {
      params: {
        query: params.query,
        content_type: params.content_type,
        difficulty_level: params.difficulty_level,
        concept_ids: params.concept_ids?.join(','),
        user_id,
        limit: params.limit ?? 20,
      },
    });
    return response.data as { materials: ReadingMaterial[]; total_found: number; query: string };
  },

  getMaterial: async (materialId: string, includeContent = true) => {
    const user_id = getCurrentUserId();
    const response = await apiService.get(`/reading-materials/material/${materialId}`, {
      params: { user_id, include_content: includeContent },
    });
    return response.data as ReadingMaterial;
  },

  updateProgress: async (
    materialId: string,
    payload: { progress_percentage: number; reading_time_seconds: number; sections_read?: string[]; notes?: string; bookmarked_sections?: string[] }
  ) => {
    const user_id = getCurrentUserId();
    const response = await apiService.post(`/reading-materials/material/${materialId}/progress`, payload, {
      params: { user_id },
    });
    return response.data;
  },

  rate: async (
    materialId: string,
    payload: { user_rating: number; difficulty_rating?: number; usefulness_rating?: number; feedback_text?: string; would_recommend?: boolean }
  ) => {
    const user_id = getCurrentUserId();
    const response = await apiService.post(`/reading-materials/material/${materialId}/rating`, payload, {
      params: { user_id },
    });
    return response.data;
  },

  getCollections: async (params?: { collection_type?: string; difficulty_level?: string; target_persona?: string; limit?: number }) => {
    const response = await apiService.get('/reading-materials/collections', { params });
    return response.data as { collections: any[] };
  },

  getCollection: async (collectionId: string) => {
    const user_id = getCurrentUserId();
    const response = await apiService.get(`/reading-materials/collection/${collectionId}`, { params: { user_id } });
    return response.data as any;
  },
};
