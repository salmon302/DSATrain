import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import CodePractice from './CodePractice';
import * as api from '../services/api';

jest.mock('../components/CodeEditor', () => () => <div>CodeEditor</div>);
jest.mock('../components/GoogleStyleCodeEditor', () => () => <div>GoogleStyleCodeEditor</div>);

// Mock AutoSizer and react-window to simplify DOM
jest.mock('react-virtualized-auto-sizer', () => ({ __esModule: true, default: ({ children }: any) => children({ height: 600, width: 300 }) }));
jest.mock('react-window', () => ({ FixedSizeList: ({ children, itemCount }: any) => (
  <div>{Array.from({ length: itemCount }).map((_, i) => children({ index: i, style: {} }))}</div>
)}));

// Spy on API
const problemsAPI = api.problemsAPI;
const trackingAPI = api.trackingAPI;
const practiceAPI = api.practiceAPI;

jest.spyOn(trackingAPI, 'trackInteraction').mockResolvedValue({} as any);
jest.spyOn(practiceAPI.gates, 'start').mockResolvedValue({ session_id: 'sess1' } as any);

const sampleProblem = {
  id: 'p_test',
  platform: 'leetcode',
  platform_id: '1234',
  title: 'Two Sum',
  difficulty: 'Easy',
  algorithm_tags: ['array', 'hash_table'],
  google_interview_relevance: 7,
  quality_score: 90,
} as any;

describe('CodePractice redirect & selection', () => {
  beforeEach(() => {
    jest.spyOn(problemsAPI, 'getProblems').mockResolvedValue({ problems: [sampleProblem] } as any);
    jest.spyOn(problemsAPI, 'getProblem').mockImplementation(async (id: string) => ({ ...sampleProblem, id } as any));
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('selects problem from location.state.problemId', async () => {
    // Render with state
    render(
      <MemoryRouter initialEntries={[{ pathname: '/practice', state: { problemId: 'p_state' } }] as any}>
        <Routes>
          <Route path="/practice" element={<CodePractice />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText('🚀 Code Practice Arena')).toBeInTheDocument());
    // Should fetch and select p_state; header shows selected title
    await waitFor(() => expect(problemsAPI.getProblem).toHaveBeenCalledWith('p_state'));
    expect(screen.getByText(/Code Practice Arena/)).toBeInTheDocument();
  });

  it('selects problem from ?pid= query and fetches if not preloaded', async () => {
    render(
      <MemoryRouter initialEntries={["/practice?pid=p_query"]}>
        <Routes>
          <Route path="/practice" element={<CodePractice />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText('🚀 Code Practice Arena')).toBeInTheDocument());
    await waitFor(() => expect(problemsAPI.getProblem).toHaveBeenCalledWith('p_query'));
  });
});
