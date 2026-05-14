import { useState } from 'react';
import type { User } from 'firebase/auth';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, Sparkles, Download, Loader2, X, Trash2
} from 'lucide-react';

interface Video { url: string; name: string; }

export default function GenerationScreen({
  user,
  gallery,
  onRefresh
}: {
  user: User,
  gallery: Video[],
  onRefresh: (uid: string) => void
}) {

  const [topic, setTopic] = useState("");
  const [ratio, setRatio] = useState("16:9");
  const [duration, setDuration] = useState(30);
  const [status, setStatus] = useState<"idle" | "processing">("idle");
  const [progress, setProgress] = useState(0);
  const [activeVideo, setActiveVideo] = useState<Video | null>(null);

  const startProduction = async () => {
    if (!topic) return;

    setStatus("processing");
    setProgress(5);

    const formData = new FormData();
    formData.append("topic", topic);
    formData.append("ratio", ratio);
    formData.append("duration", duration.toString());
    formData.append("user_id", user.uid);

    try {
      const res = await fetch("http://127.0.0.1:8000/generate-video", {
        method: "POST",
        body: formData
      });

      const { job_id } = await res.json();

      const interval = setInterval(async () => {
        const sRes = await fetch(`http://127.0.0.1:8000/job-status/${job_id}`);
        const sData = await sRes.json();

        setProgress(prev => sData.progress || prev + 2);

        if (sData.status === "completed") {
          clearInterval(interval);
          setStatus("idle");
          onRefresh(user.uid);
        } else if (sData.status === "failed") {
          clearInterval(interval);
          setStatus("idle");
          alert("Generation failed. Check server logs.");
        }
      }, 3000);

    } catch (e) {
      console.error(e);
      setStatus("idle");
    }
  };

  const handleDownload = async (video: Video) => {
    try {
      const response = await fetch(video.url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = video.name || "video.mp4";
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      console.error("Download failed", err);
    }
  };

  // 🔥 DELETE FUNCTIONALITY
  const handleDelete = async (video: Video) => {
    if (!confirm("Are you sure you want to delete this video?")) return;
    
    try {
      const res = await fetch(`http://127.0.0.1:8000/delete-video/${user.uid}/${video.name}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        onRefresh(user.uid);
        if (activeVideo?.name === video.name) setActiveVideo(null);
      }
    } catch (err) {
      console.error("Failed to delete video", err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 relative z-10">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

        {/* LEFT SIDE */}
        <div className="lg:col-span-8 space-y-6">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/[0.03] backdrop-blur-3xl p-8 rounded-[2.5rem] border border-white/10 shadow-2xl"
          >
            <div className="flex items-center gap-3 mb-8">
              <div className="p-2 bg-indigo-500/20 rounded-lg">
                <Sparkles className="w-5 h-5 text-indigo-400" />
              </div>
              <h3 className="text-sm font-black uppercase tracking-widest text-indigo-400">
                AI Production Lab
              </h3>
            </div>

            <div className="space-y-6">
              <input 
                placeholder="e.g. The Hidden Secrets of the Amazon Rainforest..." 
                className="w-full bg-black/40 border border-white/5 p-5 rounded-2xl outline-none"
                onChange={e => setTopic(e.target.value)}
              />

              <div className="grid grid-cols-2 gap-4">
                <select 
                  className="bg-black/40 p-5 rounded-2xl outline-none"
                  onChange={e => setRatio(e.target.value)}
                >
                  <option value="16:9">16:9 (Landscape)</option>
                  <option value="9:16">9:16 (Portrait)</option>
                </select>

                <input 
                  type="number"
                  value={duration}
                  onChange={e => setDuration(Number(e.target.value))}
                  className="bg-black/40 p-5 rounded-2xl outline-none"
                />
              </div>

              <button 
                onClick={startProduction}
                disabled={status === "processing"}
                className="w-full bg-indigo-600 hover:bg-indigo-700 transition-colors py-5 rounded-2xl font-bold flex justify-center gap-3 disabled:opacity-50"
              >
                {status === "processing" ? (
                  <>
                    <Loader2 className="animate-spin" />
                    Producing Cinematic Video...
                  </>
                ) : (
                  <>
                    <Play /> Generate Video
                  </>
                )}
              </button>

              {status === "processing" && (
                <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-indigo-500 transition-all"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* RIGHT SIDE */}
        <div className="lg:col-span-4">
          <div className="bg-white/[0.02] border border-white/5 p-6 rounded-[2rem] h-[80vh] overflow-y-auto">
            <h4 className="text-sm font-bold text-gray-400 mb-4">Your Gallery</h4>
            {gallery.length === 0 ? (
              <p className="text-center text-gray-600 text-sm mt-10">
                No videos generated yet
              </p>
            ) : (
              gallery.map((vid, i) => (
                <div key={i} className="mb-6 bg-black/30 p-3 rounded-2xl">
                  <div 
                    className="cursor-pointer relative group rounded-xl overflow-hidden"
                    onClick={() => setActiveVideo(vid)}
                  >
                    <video 
                      src={vid.url}
                      className="w-full rounded-xl opacity-70 group-hover:opacity-100 transition-opacity"
                    />
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="bg-black/50 p-3 rounded-full backdrop-blur-md">
                        <Play size={24} className="text-white fill-white" />
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-between items-center mt-3 px-1">
                    <p className="text-xs text-gray-300 truncate w-3/5">{vid.name}</p>
                    <div className="flex gap-3">
                      <button 
                        onClick={() => handleDownload(vid)} 
                        className="text-gray-400 hover:text-white transition-colors"
                        title="Download"
                      >
                        <Download size={18} />
                      </button>
                      <button 
                        onClick={() => handleDelete(vid)} 
                        className="text-red-400 hover:text-red-300 transition-colors"
                        title="Delete"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

      {/* MODAL */}
      <AnimatePresence>
        {activeVideo && (
          <motion.div 
            className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div 
              className="relative w-full max-w-4xl rounded-2xl overflow-hidden bg-black shadow-2xl border border-white/10"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: "spring", stiffness: 150, damping: 20 }}
            >
              <button 
                onClick={() => setActiveVideo(null)}
                className="absolute top-4 right-4 bg-white/10 hover:bg-white/20 p-2 rounded-full text-white z-10 transition-colors backdrop-blur-md"
              >
                <X size={20} />
              </button>

              <div className="w-full h-[80vh] flex items-center justify-center bg-black">
                <video 
                  src={activeVideo.url}
                  controls
                  autoPlay
                  className="max-w-full max-h-full object-contain"
                />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}