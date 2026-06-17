// Auth helpers — uses localStorage for real JWT tokens.
// The backend still auto-injects a mock admin user for every request,
// so both real login and the demo "skip" path work identically.

const TOKEN_KEY = "recruiter_token";
const DEMO_TOKEN = "bypass-token"; // accepted by the backend bypass middleware

export const setToken = (token: string) => {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token);
  }
};

export const getToken = (): string | null => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
};

export const clearToken = () => {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
  }
};

export const isAuthenticated = (): boolean => {
  return !!getToken();
};

/** Called by the "Skip / Enter as Demo" button */
export const enterDemoMode = () => {
  setToken(DEMO_TOKEN);
};
