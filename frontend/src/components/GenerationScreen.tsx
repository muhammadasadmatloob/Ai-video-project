import { useState, useRef, useEffect } from "react";
import type { User } from "firebase/auth";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Play, 
  Sparkles, 
  Loader2, 
  X, 
  Trash2, 
  Download, 
  Clock, 
  Monitor, 
  Smartphone, 
  Film, 
  Compass, 
  Database 
} from "lucide-react";
import type { Video } from "../App";

const rawUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const BACKEND_URL = rawUrl.replace(/\/$/, "");

interface Props {
  user: User;
  gallery: Video[];
  onRefresh: (uid: string) => void;
}

export default function GenerationScreen({
  user,
  gallery,
  onRefresh,
}: Props) {
  const [topic, setTopic] = useState("");
  const [ratio, setRatio] = useState("16:9");
  const [duration, setDuration] = useState(30);

  const [status, setStatus] = useState<"idle" | "processing">("idle");
  const [progress, setProgress] = useState(0);
  const [activeVideo, setActiveVideo] = useState<Video | null>(null);

  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (intervalRef.current !== null) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const startProduction = async () => {
    if (!topic.trim()) return;

    setStatus("processing");
    setProgress(5);

    const formData = new FormData();
    formData.append("topic", topic);
    formData.append("ratio", ratio);
    formData.append("duration", duration.toString());
    formData.append("user_id", user.uid);

    try {
      const res = await fetch(`${BACKEND_URL}/generate-video`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`Server Error (${res.status}): ${errorText}`);
      }

      const data = await res.json();
      const job_id = data.job_id;

      if (intervalRef.current !== null) {
        clearInterval(intervalRef.current);
      }

      intervalRef.current = window.setInterval(async () => {
        try {
          const sRes = await fetch(
            `${BACKEND_URL}/job-status/${job_id}`
          );

          if (!sRes.ok) {
            throw new Error("Status check failed");
          }

          const sData = await sRes.json();

          if (!sData) return;

          setProgress(sData.progress ?? 0);

          if (sData.status === "completed") {
            if (intervalRef.current !== null) {
              clearInterval(intervalRef.current);
              intervalRef.current = null;
            }

            setStatus("idle");
            setProgress(100);
            onRefresh(user.uid);
            setTopic(""); // Clear topic input on success
          }

          if (sData.status === "failed") {
            if (intervalRef.current !== null) {
              clearInterval(intervalRef.current);
              intervalRef.current = null;
            }

            setStatus("idle");

            alert(
              `Video generation failed: ${
                sData.error || "Unknown pipeline error"
              }`
            );
          }
        } catch (err: unknown) {
          console.error("Polling error:", err);
        }
      }, 3000);
    } catch (err: unknown) {
      console.error("Fetch Error:", err);

      setStatus("idle");

      if (err instanceof Error) {
        if (
          err.message === "Failed to fetch" ||
          err.name === "TypeError"
        ) {
          alert(
            `Network Error: Cannot reach backend at ${BACKEND_URL}.\n\nMake sure your server is running, the URL is correct, and CORS is configured.`
          );
        } else {
          alert(err.message);
        }
      } else {
        alert("An unexpected error occurred.");
      }
    }
  };

  const handleDelete = async (
    e: React.MouseEvent<HTMLButtonElement>,
    vid: Video
  ) => {
    e.stopPropagation();

    if (!confirm("Are you sure you want to delete this video?")) {
      return;
    }

    try {
      const res = await fetch(
        `${BACKEND_URL}/delete-video/${user.uid}/${vid.name}`,
        {
          method: "DELETE",
        }
      );

      if (!res.ok) {
        throw new Error("Failed to delete");
      }

      onRefresh(user.uid);
    } catch (err: unknown) {
      console.error("Delete Error:", err);
      alert("Could not delete the video. Check console for details.");
    }
  };

  // Determine current active pipeline phase based on progress value
  const getPipelineStep = () => {
    if (progress < 30) return 1; // Scripting
    if (progress < 70) return 2; // Asset Acquisition
    return 3; // Video rendering
  };

  const currentStep = getPipelineStep();

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 relative z-10">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Creator Control Panel */}
        <div className="lg:col-span-5 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-slate-900/60 border border-white/10 p-6 sm:p-8 rounded-[2.5rem] backdrop-blur-xl shadow-2xl relative overflow-hidden"
          >
            {/* Ambient subtle glow background inside the card */}
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl pointer-events-none" />

            <div className="flex items-center gap-3 mb-8">
              <div className="p-2.5 bg-indigo-500/10 rounded-2xl border border-indigo-500/20 shadow-inner">
                <Sparkles className="w-5 h-5 text-indigo-400" />
              </div>
              <div>
                <h3 className="text-sm font-black uppercase tracking-wider text-indigo-400">
                  Production Panel
                </h3>
                <p className="text-[10px] text-gray-500 font-medium">Configure and compile your AI video</p>
              </div>
            </div>

            <div className="space-y-6">
              {/* Topic Input */}
              <div className="space-y-2">
                <label className="text-[10px] uppercase tracking-wider text-gray-400 font-bold ml-1">
                  Video Concept / Topic
                </label>
                <input
                  placeholder="e.g. Life Cycle of a Black Hole..."
                  className="w-full bg-black/40 border border-white/5 p-4 rounded-2xl outline-none text-white focus:ring-2 focus:ring-indigo-500 transition-all placeholder:text-gray-600 text-sm font-light"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  disabled={status === "processing"}
                />
              </div>

              {/* Aspect Ratio Choices */}
              <div className="space-y-2">
                <label className="text-[10px] uppercase tracking-wider text-gray-400 font-bold ml-1">
                  Select Dimension Ratio
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setRatio("16:9")}
                    disabled={status === "processing"}
                    className={`flex items-center justify-center gap-3 p-4 rounded-2xl border transition-all cursor-pointer ${
                      ratio === "16:9"
                        ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow-md shadow-indigo-500/5 font-bold"
                        : "bg-black/30 border-white/5 text-gray-400 hover:bg-black/40 hover:border-white/10"
                    }`}
                  >
                    <Monitor className="w-4 h-4" />
                    <span className="text-xs">YouTube (16:9)</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setRatio("9:16")}
                    disabled={status === "processing"}
                    className={`flex items-center justify-center gap-3 p-4 rounded-2xl border transition-all cursor-pointer ${
                      ratio === "9:16"
                        ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 shadow-md shadow-indigo-500/5 font-bold"
                        : "bg-black/30 border-white/5 text-gray-400 hover:bg-black/40 hover:border-white/10"
                    }`}
                  >
                    <Smartphone className="w-4 h-4" />
                    <span className="text-xs">Shorts/Reels (9:16)</span>
                  </button>
                </div>
              </div>

              {/* Custom Duration Slider */}
              <div className="space-y-2">
                <div className="flex justify-between items-center ml-1">
                  <label className="text-[10px] uppercase tracking-wider text-gray-400 font-bold">
                    Target Duration
                  </label>
                  <span className="text-xs text-indigo-400 font-black">{duration} seconds</span>
                </div>
                <div className="bg-black/30 border border-white/5 p-4 rounded-2xl flex items-center gap-4">
                  <Clock className="w-4 h-4 text-gray-500 shrink-0" />
                  <input
                    type="range"
                    value={duration}
                    min={10}
                    max={120}
                    step={5}
                    disabled={status === "processing"}
                    className="w-full accent-indigo-500 bg-slate-800 h-1.5 rounded-lg appearance-none cursor-pointer"
                    onChange={(e) => setDuration(Number(e.target.value))}
                  />
                </div>
              </div>

              {/* Generate Button */}
              <button
                onClick={startProduction}
                disabled={status === "processing" || !topic.trim()}
                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 transition-all py-4.5 rounded-2xl font-black uppercase text-xs tracking-widest flex justify-center items-center gap-3 disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-indigo-600/20 active:scale-[0.98] cursor-pointer"
              >
                {status === "processing" ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin text-white" />
                    <span>Processing Pipeline...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 text-white fill-white" />
                    <span>Compile Video</span>
                  </>
                )}
              </button>

              {/* Pipeline Progress/Steps Status Panel */}
              <AnimatePresence>
                {status === "processing" && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-black/30 border border-white/5 rounded-3xl p-5 space-y-5 overflow-hidden"
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] uppercase font-black tracking-widest text-indigo-400">
                        Status Monitor
                      </span>
                      <span className="text-xs text-indigo-300 font-bold">{progress}%</span>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500 rounded-full"
                        style={{ width: `${progress}%` }}
                      />
                    </div>

                    {/* Pipeline Steps */}
                    <div className="space-y-3 font-sans text-xs">
                      {/* Step 1 */}
                      <div className="flex items-center gap-3">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                          currentStep > 1 
                            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" 
                            : currentStep === 1 
                            ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500 animate-pulse" 
                            : "bg-white/5 text-gray-500"
                        }`}>
                          {currentStep > 1 ? "✓" : "1"}
                        </div>
                        <span className={`${currentStep === 1 ? "text-white font-bold" : currentStep > 1 ? "text-gray-400" : "text-gray-600"}`}>
                          AI Scriptwriting & Conception
                        </span>
                      </div>

                      {/* Step 2 */}
                      <div className="flex items-center gap-3">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                          currentStep > 2 
                            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" 
                            : currentStep === 2 
                            ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500 animate-pulse" 
                            : "bg-white/5 text-gray-500"
                        }`}>
                          {currentStep > 2 ? "✓" : "2"}
                        </div>
                        <span className={`${currentStep === 2 ? "text-white font-bold" : currentStep > 2 ? "text-gray-400" : "text-gray-600"}`}>
                          Asset Acquisition & Audio Synthesis
                        </span>
                      </div>

                      {/* Step 3 */}
                      <div className="flex items-center gap-3">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                          currentStep === 3 
                            ? "bg-indigo-500/20 text-indigo-400 border border-indigo-500 animate-pulse" 
                            : "bg-white/5 text-gray-500"
                        }`}>
                          3
                        </div>
                        <span className={`${currentStep === 3 ? "text-white font-bold" : "text-gray-600"}`}>
                          Video Rendering & Stitching
                        </span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </div>

        {/* Right Column: Video Gallery Vault */}
        <div className="lg:col-span-7 space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="flex flex-col min-h-[550px]"
          >
            {/* Header section with count stats */}
            <div className="flex justify-between items-center mb-6 px-2">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-indigo-400" />
                <h3 className="text-sm font-black uppercase tracking-wider text-white">
                  Lumina Vault
                </h3>
              </div>
              <span className="text-[10px] uppercase bg-white/5 border border-white/10 px-3 py-1 rounded-full text-gray-400 font-bold tracking-widest">
                {gallery.length} Renders
              </span>
            </div>

            {/* Gallery Grid */}
            {gallery.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center bg-slate-900/20 border border-dashed border-white/10 rounded-[2.5rem] p-12 text-center backdrop-blur-sm">
                <div className="p-4 bg-white/5 rounded-full mb-4 border border-white/5 text-gray-500">
                  <Film className="w-8 h-8" />
                </div>
                <h4 className="text-sm font-bold uppercase tracking-widest text-gray-400 mb-1">
                  Vault is Empty
                </h4>
                <p className="text-xs text-gray-600 font-light max-w-xs">
                  Provide a concept on the production panel and compile your first documentary.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {gallery.map((vid, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.4, delay: i * 0.05 }}
                    className="relative group bg-slate-900/60 border border-white/10 p-3 rounded-3xl cursor-pointer hover:bg-slate-900/90 hover:border-white/20 transition-all shadow-xl hover:shadow-2xl overflow-hidden"
                    onClick={() => setActiveVideo(vid)}
                  >
                    {/* Thumbnail video node */}
                    <div className="relative aspect-video rounded-2xl overflow-hidden bg-black border border-white/5">
                      <video
                        src={vid.url}
                        className="w-full h-full object-cover opacity-80 group-hover:scale-105 transition-transform duration-500"
                        muted
                        playsInline
                      />
                      
                      {/* Play overlay display */}
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-all duration-300">
                        <div className="w-12 h-12 rounded-full bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/40 text-white transform scale-90 group-hover:scale-100 transition-all duration-300">
                          <Play className="w-5 h-5 fill-white ml-0.5" />
                        </div>
                      </div>

                      {/* Aspect Ratio Badge */}
                      <div className="absolute top-2.5 left-2.5 bg-black/70 border border-white/10 px-2 py-0.5 rounded-lg text-[9px] font-bold text-gray-300">
                        {vid.name.includes("portrait") || vid.name.includes("_9_16") ? "9:16" : "16:9"}
                      </div>
                    </div>

                    <div className="flex justify-between items-center mt-4 px-1.5 pb-1">
                      <div className="flex flex-col text-left max-w-[70%]">
                        <p className="text-xs font-bold text-gray-200 truncate" title={vid.name}>
                          {vid.name.replace("_final.mp4", "").replace(/_/g, " ")}
                        </p>
                        <span className="text-[9px] text-gray-500 font-mono tracking-wider truncate">
                          {vid.name}
                        </span>
                      </div>

                      <div className="flex items-center gap-1.5">
                        <a
                          href={vid.url}
                          download
                          target="_blank"
                          rel="noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="p-2 bg-white/5 hover:bg-indigo-600/20 hover:text-indigo-400 rounded-xl border border-white/5 transition-all text-gray-400"
                          title="Download Video"
                        >
                          <Download size={14} />
                        </a>
                        <button
                          onClick={(e) => handleDelete(e, vid)}
                          className="p-2 bg-white/5 hover:bg-red-600/20 hover:text-red-400 rounded-xl border border-white/5 transition-all text-gray-400 cursor-pointer"
                          title="Delete Video"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        </div>
      </div>

      {/* Cinematic Modal Player */}
      <AnimatePresence>
        {activeVideo && (
          <motion.div
            className="fixed inset-0 bg-black/90 backdrop-blur-lg flex items-center justify-center z-[100] p-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="relative w-full max-w-4xl rounded-3xl overflow-hidden bg-slate-900 border border-white/10 shadow-2xl"
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 20 }}
              transition={{ type: "spring", damping: 25, stiffness: 350 }}
            >
              {/* Close Button */}
              <button
                onClick={() => setActiveVideo(null)}
                className="absolute top-4 right-4 bg-black/60 hover:bg-white/10 p-2.5 rounded-full text-white z-10 transition-colors border border-white/10 cursor-pointer"
              >
                <X size={18} />
              </button>

              {/* Video Player Display Container */}
              <div className="w-full bg-black flex items-center justify-center relative overflow-hidden" style={{ height: "65vh" }}>
                <video
                  src={activeVideo.url}
                  controls
                  autoPlay
                  className="max-w-full max-h-full object-contain relative z-10"
                />
              </div>

              {/* Modal Details Footer */}
              <div className="p-6 bg-slate-900 border-t border-white/5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-indigo-500/10 rounded-xl border border-indigo-500/20 text-indigo-400">
                    <Compass className="w-5 h-5 animate-spin" style={{ animationDuration: '6s' }} />
                  </div>
                  <div className="text-left">
                    <h4 className="text-sm font-black text-white uppercase tracking-wide">
                      {activeVideo.name.replace("_final.mp4", "").replace(/_/g, " ")}
                    </h4>
                    <span className="text-[10px] text-gray-500 font-mono tracking-widest">{activeVideo.name}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3 w-full sm:w-auto">
                  <a
                    href={activeVideo.url}
                    download
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-widest px-6 py-3.5 rounded-2xl shadow-lg shadow-indigo-600/20 transition-all active:scale-[0.98] border border-white/10 text-center"
                  >
                    <Download size={14} />
                    <span>Download MP4</span>
                  </a>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}