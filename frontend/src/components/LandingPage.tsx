import React from 'react';
import { motion } from 'framer-motion';
// FIX: Use 'import type' for Variants to satisfy verbatimModuleSyntax
import type { Variants } from 'framer-motion';
import { Sparkles, ArrowRight, Play, ShieldCheck, Zap } from 'lucide-react';

interface LandingPageProps {
  onLogin: () => void;
}

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  desc: string;
}

export default function LandingPage({ onLogin }: LandingPageProps) {
  // Variants are now correctly typed and imported
  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 30 },
    visible: { 
      opacity: 1, 
      y: 0, 
      transition: { duration: 0.8, ease: "easeOut" } 
    },
  };

  return (
    <motion.main 
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="relative z-10 flex flex-col items-center justify-center min-h-[90vh] pt-20 pb-32 px-4 overflow-hidden"
    >
      {/* Background Glow Effect */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/10 rounded-full blur-[120px] -z-10" />

      {/* Badge */}
      <motion.div 
        variants={itemVariants}
        className="flex items-center gap-2 bg-white/5 border border-white/10 px-4 py-1.5 rounded-full mb-8"
      >
        <Sparkles size={14} className="text-indigo-400" />
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-gray-400">
          Powered by Llama 3 & Three.js
        </span>
      </motion.div>

      {/* Main Hero Title */}
      <motion.h2 
        variants={itemVariants}
        className="text-6xl md:text-8xl font-black tracking-tighter mb-8 leading-[0.9] max-w-5xl text-center"
      >
        AI DOCUMENTARIES <br /> 
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400">
          IN SECONDS.
        </span>
      </motion.h2>

      {/* Subtext */}
      <motion.p 
        variants={itemVariants}
        className="text-lg md:text-xl text-gray-400 mb-12 max-w-2xl text-center font-light leading-relaxed"
      >
        Transform your research into cinematic masterpieces. Lumina Studio orchestrates 
        scripting, voiceovers, and 4K visuals into a single seamless pipeline.
      </motion.p>

      {/* CTA Buttons */}
      <motion.div 
        variants={itemVariants}
        className="flex flex-col sm:flex-row gap-4 mb-24"
      >
        <button 
          onClick={onLogin}
          className="group relative bg-indigo-600 hover:bg-indigo-500 px-10 py-5 rounded-2xl text-lg font-black transition-all flex items-center gap-3 shadow-[0_20px_50px_rgba(79,70,229,0.3)] active:scale-95"
        >
          ENTER THE STUDIO
          <ArrowRight className="group-hover:translate-x-1 transition-transform" />
        </button>
        
        <button className="bg-white/5 hover:bg-white/10 border border-white/10 px-10 py-5 rounded-2xl text-lg font-black transition-all backdrop-blur-md">
          VIEW SHOWCASE
        </button>
      </motion.div>

      {/* Features Section */}
      <motion.section 
        variants={itemVariants}
        className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl w-full"
      >
        <FeatureCard 
          icon={<Zap className="text-amber-400" />}
          title="Instant Rendering"
          desc="Proprietary FFmpeg cloud engine renders high-bitrate video in real-time."
        />
        <FeatureCard 
          icon={<Play className="text-indigo-400" />}
          title="Curated Visuals"
          desc="AI-driven keyword matching pulls the perfect 4K stock footage for every scene."
        />
        <FeatureCard 
          icon={<ShieldCheck className="text-emerald-400" />}
          title="Private Archives"
          desc="Encrypted storage ensures your documentary vault is accessible only by you."
        />
      </motion.section>
    </motion.main>
  );
}

function FeatureCard({ icon, title, desc }: FeatureCardProps) {
  return (
    <div className="bg-white/[0.02] border border-white/5 p-8 rounded-[2rem] backdrop-blur-sm hover:bg-white/[0.05] transition-all hover:border-white/10 group">
      <div className="bg-white/5 w-12 h-12 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
        {icon}
      </div>
      <h3 className="text-sm font-black uppercase tracking-widest mb-3 text-white">{title}</h3>
      <p className="text-sm text-gray-500 font-light leading-relaxed">{desc}</p>
    </div>
  );
}