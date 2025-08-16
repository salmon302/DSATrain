import axios from 'axios';

// Under test
import { practiceAPI, aiAPI, srsAPI, interviewAPI, cognitiveAPI } from './api';

jest.mock('axios');

describe('service wrappers', () => {
  const mockedAxios = axios as jest.Mocked<typeof axios> & {
    __instance?: any;
  };

  beforeEach(() => {
    const instance = {
      get: jest.fn(),
      post: jest.fn(),
      delete: jest.fn(),
      interceptors: { request: { use: jest.fn() }, response: { use: jest.fn() } },
    } as any;
    mockedAxios.create = jest.fn(() => instance) as any;
    (mockedAxios as any).__instance = instance;
  });

  test('practiceAPI.startSession posts to /practice/session and returns data', async () => {
    const payload = { user_id: 'user_1', size: 3 };
    const responseData = { problems: [{ id: 'p1' }] };
    (mockedAxios as any).__instance.post.mockResolvedValue({ data: responseData });

    const result = await practiceAPI.startSession(payload as any);

    expect((mockedAxios as any).__instance.post).toHaveBeenCalledWith('/practice/session', payload);
    expect(result).toEqual(responseData);
  });

  test('aiAPI.getStatus calls GET /ai/status with params when session provided', async () => {
    const responseData = { enabled: true };
    (mockedAxios as any).__instance.get.mockResolvedValue({ data: responseData });

    const result = await aiAPI.getStatus('session_123');

    expect((mockedAxios as any).__instance.get).toHaveBeenCalledWith('/ai/status', { params: { session_id: 'session_123' } });
    expect(result).toEqual(responseData);
  });

  test('srsAPI.getNextDue calls GET /srs/next', async () => {
    const responseData = { items: [] };
    (mockedAxios as any).__instance.get.mockResolvedValue({ data: responseData });
    const result = await srsAPI.getNextDue({ user_id: 'u1', limit: 5 });
    expect((mockedAxios as any).__instance.get).toHaveBeenCalledWith('/srs/next', { params: { user_id: 'u1', limit: 5 } });
    expect(result).toEqual(responseData);
  });

  test('interviewAPI.start posts to /interview/start and returns data', async () => {
    const payload = { problem_id: 'p1', duration_minutes: 45 } as any;
    const responseData = { interview_id: 'i123', duration_minutes: 45 };
    (mockedAxios as any).__instance.post.mockResolvedValue({ data: responseData });
    const result = await interviewAPI.start(payload);
    expect((mockedAxios as any).__instance.post).toHaveBeenCalledWith('/interview/start', payload);
    expect(result).toEqual(responseData);
  });

  test('interviewAPI.complete posts to /interview/complete', async () => {
    const payload = { interview_id: 'i1', code: 'print(1)' } as any;
    const responseData = { status: 'ok' };
    (mockedAxios as any).__instance.post.mockResolvedValue({ data: responseData });
    const result = await interviewAPI.complete(payload);
    expect((mockedAxios as any).__instance.post).toHaveBeenCalledWith('/interview/complete', payload);
    expect(result).toEqual(responseData);
  });

  test('cognitiveAPI.assess posts to /cognitive/assess', async () => {
    const payload = { working_memory: 3 } as any;
    const responseData = { profile: { working_memory: 3 } };
    (mockedAxios as any).__instance.post.mockResolvedValue({ data: responseData });
    const result = await cognitiveAPI.assess(payload);
    expect((mockedAxios as any).__instance.post).toHaveBeenCalledWith('/cognitive/assess', payload);
    expect(result).toEqual(responseData);
  });

  test('srsAPI.submitReview posts to /srs/review', async () => {
    const payload = { item_id: 'p1', rating: 4 } as any;
    const responseData = { ok: true };
    (mockedAxios as any).__instance.post.mockResolvedValue({ data: responseData });
    const result = await srsAPI.submitReview(payload);
    expect((mockedAxios as any).__instance.post).toHaveBeenCalledWith('/srs/review', payload);
    expect(result).toEqual(responseData);
  });

  test('srsAPI.getStats calls GET /srs/stats', async () => {
    const responseData = { due_today: 0 };
    (mockedAxios as any).__instance.get.mockResolvedValue({ data: responseData });
    const result = await srsAPI.getStats({ user_id: 'u1' });
    expect((mockedAxios as any).__instance.get).toHaveBeenCalledWith('/srs/stats', { params: { user_id: 'u1' } });
    expect(result).toEqual(responseData);
  });

  test('practiceAPI.gates endpoint wrappers call correct URLs', async () => {
    (mockedAxios as any).__instance.post.mockResolvedValue({ data: { session_id: 's1' } });
    (mockedAxios as any).__instance.get.mockResolvedValue({ data: { ok: true } });
    (mockedAxios as any).__instance.delete.mockResolvedValue({ data: { ok: true } });

    await practiceAPI.gates.start({ problem_id: 'p1' } as any);
    expect((mockedAxios as any).__instance.post).toHaveBeenCalledWith('/practice/gates/start', { problem_id: 'p1' });

    await practiceAPI.gates.progress({ session_id: 's1', gate_key: 'read', value: true } as any);
    expect((mockedAxios as any).__instance.post).toHaveBeenCalledWith('/practice/gates/progress', { session_id: 's1', gate_key: 'read', value: true });

    await practiceAPI.gates.status('s1');
    expect((mockedAxios as any).__instance.get).toHaveBeenCalledWith('/practice/gates/status', { params: { session_id: 's1' } });

    await practiceAPI.gates.list('p1');
    expect((mockedAxios as any).__instance.get).toHaveBeenCalledWith('/practice/gates', { params: { problem_id: 'p1' } });

    await practiceAPI.gates.get('s1');
    expect((mockedAxios as any).__instance.get).toHaveBeenCalledWith('/practice/gates/s1');

    await practiceAPI.gates.delete('s1');
    expect((mockedAxios as any).__instance.delete).toHaveBeenCalledWith('/practice/gates/s1');
  });

  test('practiceAPI.elaborative posts to /practice/elaborative', async () => {
    const payload = { question: 'why?' } as any;
    const responseData = { answer: 'because' };
    (mockedAxios as any).__instance.post.mockResolvedValue({ data: responseData });
    const result = await practiceAPI.elaborative(payload);
    expect((mockedAxios as any).__instance.post).toHaveBeenCalledWith('/practice/elaborative', payload);
    expect(result).toEqual(responseData);
  });

  test('practiceAPI.workingMemoryCheck posts to /practice/working-memory-check', async () => {
    const payload = { metrics: { span: 5 } } as any;
    const responseData = { ok: true };
    (mockedAxios as any).__instance.post.mockResolvedValue({ data: responseData });
    const result = await practiceAPI.workingMemoryCheck(payload);
    expect((mockedAxios as any).__instance.post).toHaveBeenCalledWith('/practice/working-memory-check', payload);
    expect(result).toEqual(responseData);
  });
});


