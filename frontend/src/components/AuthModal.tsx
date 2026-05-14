import React, { useState } from 'react';
import { auth } from '../auth/firebase'; 
import { 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword 
} from 'firebase/auth';
// FIX: FirebaseError must be imported from 'firebase/app'
import { FirebaseError } from 'firebase/app';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [isLogin, setIsLogin] = useState<boolean>(true);
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setError] = useState<string>("");

  const validatePassword = (pw: string): boolean => {
    // 8+ chars, 1 upper, 1 lower, 1 special, 1 number
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return regex.test(pw);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    setError("");
    
    if (!validatePassword(password)) {
      setError("Password must be 8+ chars, include uppercase, lowercase, number, and special char.");
      return;
    }

    try {
      if (isLogin) {
        await signInWithEmailAndPassword(auth, email, password);
      } else {
        await createUserWithEmailAndPassword(auth, email, password);
      }
      onClose();
    } catch (err: unknown) {
      // FIX: Narrow the type of 'err' to FirebaseError to solve 'unknown' type issue
      if (err instanceof FirebaseError) {
        // Now 'err' is recognized as FirebaseError, so .message is accessible
        setError(err.message);
      } else {
        setError("An unexpected authentication error occurred.");
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
      <div className="bg-slate-900 border border-white/10 p-8 rounded-[2.5rem] w-full max-w-md shadow-2xl animate-in zoom-in duration-300">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-black tracking-tighter">
            {isLogin ? 'WELCOME BACK' : 'JOIN LUMINA'}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-[10px] uppercase tracking-widest text-gray-500 ml-2 font-bold">Email Address</label>
            <input 
              type="email" 
              placeholder="name@example.com" 
              className="w-full bg-black/50 border border-white/10 p-4 rounded-2xl outline-none focus:ring-2 ring-indigo-500 transition-all" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
              required 
            />
          </div>
          
          <div className="space-y-1">
            <label className="text-[10px] uppercase tracking-widest text-gray-500 ml-2 font-bold">Password</label>
            <input 
              type="password" 
              placeholder="••••••••" 
              className="w-full bg-black/50 border border-white/10 p-4 rounded-2xl outline-none focus:ring-2 ring-indigo-500 transition-all" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
            />
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 p-3 rounded-xl">
              <p className="text-red-400 text-[10px] font-bold leading-tight">{error}</p>
            </div>
          )}

          <button 
            type="submit" 
            className="w-full bg-indigo-600 py-4 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-indigo-500 transition-all shadow-xl shadow-indigo-600/20 active:scale-95"
          >
            {isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <button 
          onClick={() => {
            setIsLogin(!isLogin);
            setError("");
          }} 
          className="w-full mt-6 text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 hover:text-indigo-400 transition-colors"
        >
          {isLogin ? "New to the Studio? Create Account" : "Have an Account? Sign In"}
        </button>
      </div>
    </div>
  );
}