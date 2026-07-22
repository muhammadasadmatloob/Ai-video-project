import React from 'react';
import { motion } from 'framer-motion';
import type { Variants } from 'framer-motion';
import { Sparkles, ArrowRight, Play, ShieldCheck, Zap, Video, Film, Cpu } from 'lucide-react';

interface LandingPageProps {
  onLogin: () => void;
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  desc: string;
  glowColor: string;
}

export default function LandingPage({ onLogin }: LandingPageProps) {
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.15 },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0, 
      transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } 
    },
  };

  return (
    <motion.div 
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="relative z-10 flex flex-col items-center justify-center min-h-[90vh] pt-12 pb-24 px-6 overflow-hidden max-w-7xl mx-auto"
    >
      {/* Dynamic background lights */}
      <div className="absolute top-12 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 rounded-full blur-[130px] -z-10" />

      {/* Intro Tag */}
      <motion.div 
        variants={itemVariants} 
        className="flex items-center gap-2 bg-slate-900/80 border border-white/10 px-4 py-2 rounded-full mb-6 backdrop-blur-md shadow-lg shadow-black/10"
      >
        <Sparkles size={14} className="text-indigo-400 animate-pulse" />
        <span className="text-[10px] font-black uppercase tracking-[0.25em] bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 to-purple-300">
          Powered by Llama 3 & FFmpeg
        </span>
      </motion.div>

      {/* Main Hero Header */}
      <motion.h2 
        variants={itemVariants} 
        className="text-5xl sm:text-7xl md:text-8xl font-black tracking-tight mb-6 leading-[1.05] text-center max-w-5xl"
      >
        AI DOCUMENTARIES <br /> 
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 drop-shadow-[0_2px_10px_rgba(129,140,248,0.2)]">
          IN SECONDS.
        </span>
      </motion.h2>

      {/* Hero Subtitle */}
      <motion.p 
        variants={itemVariants} 
        className="text-base sm:text-lg md:text-xl text-gray-400 mb-10 max-w-2xl text-center font-light leading-relaxed"
      >
        Transform your concepts into cinematic masterpieces. Lumina Studio orchestrates script generation, voice synthesis, and dynamic stock clip stitching in one seamless automated pipeline.
      </motion.p>

      {/* CTA Button */}
      <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-4 mb-20 z-20">
        <button 
          onClick={onLogin}
          className="group relative bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 px-12 py-5 rounded-2xl text-base font-black uppercase tracking-widest transition-all flex items-center justify-center gap-3 shadow-[0_15px_40px_rgba(79,70,229,0.4)] hover:shadow-[0_15px_50px_rgba(124,58,237,0.5)] active:scale-95 cursor-pointer"
        >
          <span>Enter the Studio</span>
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1.5 transition-transform" />
          {/* Subtle inside button glow */}
          <span className="absolute inset-0 rounded-2xl border border-white/20 pointer-events-none" />
        </button>
      </motion.div>

      {/* UI Mockup Container */}
      <motion.div 
        variants={itemVariants}
        className="w-full max-w-4xl bg-slate-900/60 border border-white/10 rounded-3xl p-4 sm:p-6 backdrop-blur-xl shadow-2xl mb-24 relative group"
      >
        <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-3xl blur opacity-30 group-hover:opacity-50 transition duration-1000" />
        
        {/* Mockup Windows Header */}
        <div className="relative flex items-center justify-between border-b border-white/5 pb-4 mb-6">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-500/60" />
            <span className="w-3 h-3 rounded-full bg-yellow-500/60" />
            <span className="w-3 h-3 rounded-full bg-green-500/60" />
          </div>
          <span className="text-[10px] text-gray-500 font-mono tracking-widest">LUMINA_STUDIO_V1.EXE</span>
          <div className="w-12" />
        </div>

        {/* Mockup Dashboard Content */}
        <div className="relative grid grid-cols-1 md:grid-cols-3 gap-6 text-left opacity-90 pointer-events-none select-none">
          <div className="md:col-span-2 space-y-4">
            <div className="h-10 bg-white/5 border border-white/5 rounded-xl flex items-center px-4 text-xs text-gray-400 font-light">
              Enter topic... (e.g. The Secrets of Deep Ocean Exploration)
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="h-10 bg-white/5 border border-white/5 rounded-xl flex items-center px-4 text-xs text-gray-400 font-light">
                YouTube (16:9)
              </div>
              <div className="h-10 bg-white/5 border border-white/5 rounded-xl flex items-center px-4 text-xs text-gray-400 font-light">
                30 Seconds
              </div>
            </div>
            <div className="h-12 bg-indigo-600/30 border border-indigo-500/20 rounded-xl flex items-center justify-center text-xs font-bold text-indigo-300">
              Generate Video
            </div>
          </div>
          
          <div className="bg-black/30 border border-white/5 rounded-2xl p-4 space-y-3">
            <h4 className="text-[10px] uppercase font-black tracking-widest text-indigo-400">Rendering Queue</h4>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 w-2/3" />
            </div>
            <div className="text-[10px] text-gray-400 font-light space-y-1">
              <p>⚡ Fetching media assets...</p>
              <p className="text-indigo-400">⏳ Render: 68%</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Feature Cards Grid */}
      <motion.section 
        variants={itemVariants} 
        className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full"
      >
        <FeatureCard 
          icon={<Cpu className="text-indigo-400 w-6 h-6" />}
          title="Llama 3 Brain"
          desc="Advanced large language models build deeply researched, engaging documentary-style scripts."
          glowColor="group-hover:shadow-[0_0_30px_rgba(99,102,241,0.15)] group-hover:border-indigo-500/30"
        />
        <FeatureCard 
          icon={<Film className="text-purple-400 w-6 h-6" />}
          title="Smart Visuals"
          desc="AI semantic keyword matching finds, retrieves, and processes royalty-free dynamic stock clips."
          glowColor="group-hover:shadow-[0_0_30px_rgba(168,85,247,0.15)] group-hover:border-purple-500/30"
        />
        <FeatureCard 
          icon={<ShieldCheck className="text-pink-400 w-6 h-6" />}
          title="Secure Vault"
          desc="Encrypted Firebase authentication stores and locks your video vault so it remains yours only."
          glowColor="group-hover:shadow-[0_0_30px_rgba(236,72,153,0.15)] group-hover:border-pink-500/30"
        />
      </motion.section>
    </motion.div>
  );
}

function FeatureCard({ icon, title, desc, glowColor }: FeatureCardProps) {
  return (
    <div className={`bg-slate-900/40 border border-white/5 p-8 rounded-3xl backdrop-blur-md transition-all duration-300 hover:-translate-y-1 hover:bg-slate-900/60 group relative ${glowColor}`}>
      <div className="bg-white/5 w-12 h-12 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 group-hover:bg-white/10 transition-all duration-300 shadow-inner">
        {icon}
      </div>
      <h3 className="text-xs font-black uppercase tracking-widest mb-3 text-white">{title}</h3>
      <p className="text-sm text-gray-500 font-light leading-relaxed">{desc}</p>
    </div>
  );
}