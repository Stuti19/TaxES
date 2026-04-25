import { useState, createContext, useContext } from 'react';

interface User {
  id: string;
  email: string;
  full_name?: string;
}

interface AuthContextType {
  user: User | null;
  session: any;
  loading: boolean;
  signUp: (email: string, password: string, fullName: string) => Promise<{ error: any }>;
  signIn: (email: string, password: string) => Promise<{ error: any }>;
  signInWithGoogle: () => Promise<{ error: any }>;
  signOut: () => Promise<{ error: any }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  // Mock user for development
  const [user] = useState<User>({
    id: 'mock-user-id',
    email: 'user@example.com',
    full_name: 'Test User'
  });
  const [loading] = useState(false);

  const signUp = async (email: string, password: string, fullName: string) => {
    return { error: null };
  };

  const signIn = async (email: string, password: string) => {
    return { error: null };
  };

  const signInWithGoogle = async () => {
    return { error: null };
  };

  const signOut = async () => {
    return { error: null };
  };

  return (
    <AuthContext.Provider value={{
      user,
      session: { user },
      loading,
      signUp,
      signIn,
      signInWithGoogle,
      signOut
    }}>
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