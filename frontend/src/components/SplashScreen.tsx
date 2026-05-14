import { motion } from 'framer-motion';

export default function SplashScreen() {
  return (
    <div className="fixed inset-0 z-[100] bg-slate-950 flex flex-col items-center justify-center">
      <motion.h1 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-5xl font-black tracking-tighter text-white"
      >
        LUMINA <span className="text-indigo-500">FILMS</span>
      </motion.h1>
      <motion.div 
        initial={{ width: 0 }}
        animate={{ width: 200 }}
        className="h-1 bg-indigo-500 mt-4 rounded-full"
      />
    </div>
  );
}