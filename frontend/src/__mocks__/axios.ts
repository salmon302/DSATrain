// Manual mock for axios to avoid ESM parsing in Jest and provide a controllable instance
// CRA/Jest will use this when `jest.mock('axios')` is called in tests.

// Current underlying instance that test code can replace.
let currentInstance: any = {
  get: jest.fn().mockResolvedValue({ data: {} }),
  post: jest.fn().mockResolvedValue({ data: {} }),
  delete: jest.fn().mockResolvedValue({ data: {} }),
  put: jest.fn().mockResolvedValue({ data: {} }),
  patch: jest.fn().mockResolvedValue({ data: {} }),
  interceptors: {
    request: { use: jest.fn(), eject: jest.fn() },
    response: { use: jest.fn(), eject: jest.fn() },
  },
};

// Create a proxy/wrapper instance whose methods forward to the current instance.
const makeProxyInstance = () => ({
  get: (...args: any[]) => currentInstance.get(...args),
  post: (...args: any[]) => currentInstance.post(...args),
  delete: (...args: any[]) => currentInstance.delete(...args),
  put: (...args: any[]) => currentInstance.put(...args),
  patch: (...args: any[]) => currentInstance.patch(...args),
  interceptors: {
    request: {
      use: (...args: any[]) => currentInstance.interceptors.request.use(...args),
      eject: (...args: any[]) => currentInstance.interceptors.request.eject(...args),
    },
    response: {
      use: (...args: any[]) => currentInstance.interceptors.response.use(...args),
      eject: (...args: any[]) => currentInstance.interceptors.response.eject(...args),
    },
  },
});

const axiosMock: any = {
  // When api code calls axios.create, return a proxy instance bound to currentInstance
  create: jest.fn(() => makeProxyInstance()),
  // Also allow direct calls in rare cases
  get: (...args: any[]) => currentInstance.get(...args),
  post: (...args: any[]) => currentInstance.post(...args),
  delete: (...args: any[]) => currentInstance.delete(...args),
  put: (...args: any[]) => currentInstance.put(...args),
  patch: (...args: any[]) => currentInstance.patch(...args),
};

// Expose a mutable __instance so tests can swap it
Object.defineProperty(axiosMock, '__instance', {
  get: () => currentInstance,
  set: (v) => { currentInstance = v; },
  configurable: true,
});

export default axiosMock;
