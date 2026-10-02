"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { auth, clearToken, getToken, setToken } from "@/lib/api";

interface AuthUser {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  date_joined?: string;
}

interface AuthSession {
  access_token: string;
  user: AuthUser;
}

interface AuthContextValue {
  user: AuthUser | null;
  session: AuthSession | null;
  loading: boolean;
  error: string | null;
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signUp: (email: string, password: string) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [session, setSession] = useState<AuthSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }

    auth.getProfile()
      .then((profile) => {
        const authenticatedUser = (profile as { user: AuthUser }).user;
        setUser(authenticatedUser);
        setSession({ access_token: token, user: authenticatedUser });
      })
      .catch(() => clearToken())
      .finally(() => setLoading(false));
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    setError(null);
    try {
      const response = await auth.login({ username: email, password });
      setToken(response.token);
      setUser(response.user);
      setSession({ access_token: response.token, user: response.user });
      return { error: null };
    } catch (error) {
      const message = error instanceof Error ? error.message : "Sign in failed.";
      setError(message);
      return { error: message };
    }
  }, []);

  const signUp = useCallback(async (email: string, password: string) => {
    setError(null);
    try {
      const response = await auth.register({
        username: email,
        email,
        password,
      });
      setToken(response.token);
      setUser(response.user);
      setSession({ access_token: response.token, user: response.user });
      return { error: null };
    } catch (error) {
      const message = error instanceof Error ? error.message : "Account creation failed.";
      setError(message);
      return { error: message };
    }
  }, []);

  const signOut = useCallback(async () => {
    clearToken();
    setUser(null);
    setSession(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, session, loading, error, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
