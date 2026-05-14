import { useState, useEffect } from 'react';
import { auth } from './auth/firebase';
import { onAuthStateChanged, signOut, type User } from 'firebase/auth';
import HeroCanvas from './components/HeroCanvas';
import SplashScreen from './components/SplashScreen';
import LandingPage from './components/LandingPage';
import GenerationScreen from './components/GenerationScreen';
import AuthModal from './components/AuthModal';

// 🔥 ACTION REQUIRED: Replace with your actual Hugging Face Direct URL
const BACKEND_URL = "https://your-huggingface-url.hf.space";

export default function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [gallery, setGallery] = useState([]);

  const fetchGallery = async (uid: string) => {
    try {
      const res = await fetch(`${BACKEND_URL}/user-videos/${uid}`);
      if (!res.ok) throw new Error("Failed to fetch gallery");
      const data = await res.json();
      setGallery(data.videos || []);
    } catch (e) { 
      console.error("Backend Error:", e); 
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), 2000);
    
    // Check if auth exists before using it to prevent white screen
    if (!auth) {
      console.error("Firebase auth not initialized. Check your firebase.ts and Netlify Env Vars.");
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, (u: User | null) => {
      setUser(u);
      if (u) fetchGallery(u.uid);
    });

    return () => { 
      clearTimeout(timer); 
      unsubscribe(); 
    };
  }, []);

  if (showSplash) return <SplashScreen />;

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans overflow-x-hidden">
      <HeroCanvas />
      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />
      
      <nav className="relative z-50 flex justify-between p-6 border-b border-white/5 backdrop-blur-md">
        <h1 className="text-xl font-black tracking-tighter">LUMINA</h1>
        {user ? (
          <div className="flex items-center gap-4">
            <span className="text-[10px] text-gray-400 hidden sm:block">{user.email}</span>
            <button 
              onClick={() => signOut(auth)} 
              className="text-[10px] uppercase font-bold text-gray-500 hover:text-red-400 transition-colors"
            >
              Logout
            </button>
          </div>
        ) : (
          <button 
            onClick={() => setIsAuthOpen(true)} 
            className="text-[10px] uppercase font-bold bg-indigo-600 px-6 py-2 rounded-full hover:bg-indigo-500 transition-all shadow-lg shadow-indigo-500/20"
          >
            Login
          </button>
        )}
      </nav>

      <main className="relative z-10">
        {!user ? (
          <LandingPage onLogin={() => setIsAuthOpen(true)} />
        ) : (
          <GenerationScreen user={user} gallery={gallery} onRefresh={fetchGallery} />
        )}
      </main>
    </div>
  );
}