import { useState } from "react";
import type { User } from "firebase/auth";

import { motion, AnimatePresence } from "framer-motion";

import {
  Play,
  Sparkles,
  Loader2,
  X
} from "lucide-react";

// =========================
// BACKEND URL
// =========================
const BACKEND_URL = import.meta.env.VITE_API_URL;

interface Video {
  url: string;
  name: string;
}

interface Props {
  user: User;
  gallery: Video[];
  onRefresh: (uid: string) => void;
}

export default function GenerationScreen({
  user,
  gallery,
  onRefresh
}: Props) {

  const [topic, setTopic] = useState("");
  const [ratio, setRatio] = useState("16:9");
  const [duration, setDuration] = useState(30);

  const [status, setStatus] =
    useState<"idle" | "processing">("idle");

  const [progress, setProgress] = useState(0);

  const [activeVideo, setActiveVideo] =
    useState<Video | null>(null);

  // =========================
  // START VIDEO GENERATION
  // =========================
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

      const res = await fetch(
        `${BACKEND_URL}/generate-video`,
        {
          method: "POST",
          body: formData
        }
      );

      if (!res.ok) throw new Error("Request failed");

      const data = await res.json();
      const job_id = data.job_id;

      const interval = setInterval(async () => {

        const sRes = await fetch(
          `${BACKEND_URL}/job-status/${job_id}`
        );

        const sData = await sRes.json();

        setProgress(sData.progress || 0);

        if (sData.status === "completed") {
          clearInterval(interval);
          setStatus("idle");
          setProgress(100);
          onRefresh(user.uid);
        }

        if (sData.status === "failed") {
          clearInterval(interval);
          setStatus("idle");
          alert("Video generation failed");
        }

      }, 3000);

    } catch (err) {
      console.error(err);
      setStatus("idle");
      alert("Backend not reachable");
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
            className="bg-white/3 backdrop-blur-3xl p-8 rounded-[2.5rem] border border-white/10 shadow-2xl"
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
                placeholder="Enter topic..."
                className="w-full bg-black/40 border border-white/5 p-5 rounded-2xl outline-none"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />

              <div className="grid grid-cols-2 gap-4">

                <select
                  value={ratio}
                  className="bg-black/40 p-5 rounded-2xl outline-none"
                  onChange={(e) => setRatio(e.target.value)}
                >
                  <option value="16:9">16:9</option>
                  <option value="9:16">9:16</option>
                </select>

                <input
                  type="number"
                  value={duration}
                  min={10}
                  max={120}
                  className="bg-black/40 p-5 rounded-2xl outline-none"
                  onChange={(e) =>
                    setDuration(Number(e.target.value))
                  }
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
                    Generating...
                  </>
                ) : (
                  <>
                    <Play />
                    Generate Video
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

          {/* =========================
              GALLERY (FIXED WARNING)
          ========================= */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">

            {gallery.length === 0 ? (
              <p className="text-gray-500">No videos yet</p>
            ) : (
              gallery.map((vid, i) => (
                <div
                  key={i}
                  className="bg-black/40 p-3 rounded-xl cursor-pointer"
                  onClick={() => setActiveVideo(vid)}
                >
                  <video
                    src={vid.url}
                    className="rounded-lg w-full"
                  />
                  <p className="text-xs text-gray-300 mt-2 truncate">
                    {vid.name}
                  </p>
                </div>
              ))
            )}

          </div>

        </div>
      </div>

      {/* VIDEO MODAL */}
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
            >

              <button
                onClick={() => setActiveVideo(null)}
                className="absolute top-4 right-4 bg-white/10 hover:bg-white/20 p-2 rounded-full text-white z-10"
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