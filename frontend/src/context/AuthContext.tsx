import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User, StudentProfile } from '../types';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  demoLogin: (accountType: 'student' | 'admin') => Promise<User>;
  register: (data: any) => Promise<User>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  updateProfile: (data: Partial<StudentProfile>) => Promise<StudentProfile>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const cached = localStorage.getItem('careersync_user');
      if (!cached) return null;
      const parsed = JSON.parse(cached);
      if (parsed && typeof parsed === 'object' && parsed.email) {
        return parsed;
      }
      localStorage.removeItem('careersync_user');
      return null;
    } catch {
      localStorage.removeItem('careersync_user');
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  const refreshUser = async () => {
    try {
      const currentUser = await api.getCurrentUser();
      setUser(currentUser);
      if (currentUser) {
        localStorage.setItem('careersync_user', JSON.stringify(currentUser));
      } else {
        localStorage.removeItem('careersync_user');
      }
    } catch {
      // Retain cached session if temporary network failure
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (email: string, password: string) => {
    const loggedUser = await api.login(email, password);
    setUser(loggedUser);
    localStorage.setItem('careersync_user', JSON.stringify(loggedUser));
    return loggedUser;
  };

  const demoLogin = async (accountType: 'student' | 'admin' = 'student') => {
    const loggedUser = await api.demoLogin(accountType);
    setUser(loggedUser);
    localStorage.setItem('careersync_user', JSON.stringify(loggedUser));
    return loggedUser;
  };

  const register = async (data: any) => {
    const newUser = await api.register(data);
    setUser(newUser);
    localStorage.setItem('careersync_user', JSON.stringify(newUser));
    return newUser;
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch (e) {
      console.warn('Logout request warning:', e);
    } finally {
      localStorage.removeItem('careersync_user');
      setUser(null);
    }
  };

  const updateProfile = async (data: Partial<StudentProfile>) => {
    const updatedProfile = await api.updateProfile(data);
    if (user) {
      setUser({
        ...user,
        student_profile: updatedProfile,
      });
    }
    return updatedProfile;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        demoLogin,
        register,
        logout,
        refreshUser,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
