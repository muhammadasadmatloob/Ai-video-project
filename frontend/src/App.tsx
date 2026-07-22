import { useState, useEffect } from 'react';
import { auth } from './auth/firebase';
import { onAuthStateChanged, signOut, type User } from 'firebase/auth';
import { User as UserIcon, LogOut, Video } from 'lucide-react';

import HeroCanvas from './components/HeroCanvas';
import SplashScreen from './components/SplashScreen';
import LandingPage from './components/LandingPage';
import GenerationScreen from './components/GenerationScreen';
import AuthModal from './components/AuthModal';

// Clean trailing slash directly in execution to prevent network routing errors
const rawUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const BACKEND_URL = rawUrl.replace(/\/$/, "");

export interface Video {
  url: string;
  name: string;
}

export default function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [gallery, setGallery] = useState<Video[]>([]);

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

    if (!auth) {
      console.error("Firebase auth not initialized.");
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, (u: User | null) => {
      setUser(u);
      if (u) {
        fetchGallery(u.uid);
      }
    });

    return () => {
      clearTimeout(timer);
      unsubscribe();
    };
  }, []);

  if (showSplash) return <SplashScreen />;

  return (
    <div className="min-h-screen bg-slate-950 text-white font-sans overflow-x-hidden relative">
      {/* Decorative gradient backdrops */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-purple-500/10 rounded-full blur-[150px] pointer-events-none" />
      
      <HeroCanvas />
      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} />

      {/* Floating Glassmorphic Header */}
      <header className="sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center px-6 py-4 bg-slate-900/40 border border-white/10 backdrop-blur-xl rounded-3xl shadow-xl shadow-black/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-600/30">
              <Video className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                LUMINA
              </h1>
              <span className="text-[9px] uppercase tracking-widest text-indigo-400 font-bold block -mt-1">
                STUDIO LAB
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {user ? (
              <div className="flex items-center gap-3 bg-white/5 border border-white/10 px-4 py-2 rounded-2xl">
                <div className="w-8 h-8 rounded-xl bg-slate-800 flex items-center justify-center text-indigo-400 border border-white/10">
                  <UserIcon className="w-4 h-4" />
                </div>
                <div className="flex flex-col text-left">
                  <span className="text-[10px] text-gray-400 font-semibold truncate max-w-[150px] sm:max-w-[200px]">
                    {user.email}
                  </span>
                  <button
                    onClick={() => signOut(auth)}
                    className="text-[9px] uppercase font-bold text-gray-500 hover:text-red-400 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <LogOut className="w-2.5 h-2.5" />
                    Logout
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setIsAuthOpen(true)}
                className="text-[10px] uppercase font-black tracking-widest bg-gradient-to-r from-indigo-600 to-indigo-700 px-6 py-2.5 rounded-2xl hover:from-indigo-500 hover:to-indigo-600 transition-all shadow-lg shadow-indigo-500/20 active:scale-95"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>

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