import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Camera, X, Activity, ScanFace, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../../services/api';

interface VitalsScannerProps {
  onClose: () => void;
  onScanComplete: (data: { heartRate: number; emotion: string }) => void;
}

export function VitalsScanner({ onClose, onScanComplete }: VitalsScannerProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 640, height: 480 },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      setError("Camera access denied or unavailable.");
      console.error(err);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
  };

  const startScan = () => {
    if (!streamRef.current) return;
    
    setError(null);
    chunksRef.current = [];
    const mediaRecorder = new MediaRecorder(streamRef.current, { mimeType: 'video/webm' });
    mediaRecorderRef.current = mediaRecorder;
    
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        chunksRef.current.push(e.data);
      }
    };
    
    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
      await processVideo(blob);
    };
    
    // Simulate recording progress for 10 seconds
    setIsRecording(true);
    let p = 0;
    const interval = setInterval(() => {
      p += 10;
      setProgress(p);
      if (p >= 100) {
        clearInterval(interval);
        mediaRecorder.stop();
        setIsRecording(false);
        setIsProcessing(true);
      }
    }, 1000); // 10 ticks (10s total)
    
    mediaRecorder.start();
  };

  const processVideo = async (videoBlob: Blob) => {
    try {
      const result = await api.analyzeVitals(videoBlob);
      if (result.error) {
         setError(result.error);
         setIsProcessing(false);
         return;
      }
      
      // Allow user to see "success" for a second before closing
      setTimeout(() => {
        onScanComplete({
          heartRate: result.heart_rate,
          emotion: result.emotion
        });
      }, 1500);
      
    } catch (err) {
      setError("Analysis failed. Please try again.");
      setIsProcessing(false);
      console.error(err);
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md"
      >
        <motion.div
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          className="bg-[#0a0a0f] border border-white/10 rounded-2xl w-full max-w-lg overflow-hidden relative shadow-2xl"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/5 bg-white/5">
            <h3 className="flex items-center gap-2 text-white font-semibold">
              <ScanFace className="w-5 h-5 text-[#00ffc8]" />
              Vitals & Emotion Scan
            </h3>
            <button onClick={onClose} className="p-1 hover:bg-white/10 rounded-lg text-white/50 hover:text-white transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Camera View */}
          <div className="relative aspect-video bg-black flex items-center justify-center overflow-hidden">
             
            <video
               ref={videoRef}
               autoPlay
               playsInline
               muted
               className={`w-full h-full object-cover ${(isRecording || isProcessing) ? 'opacity-50' : 'opacity-100'} transition-opacity`}
               style={{ transform: 'scaleX(-1)' }}
            />
            
            {/* UI Overlays */}
            {error && (
              <div className="absolute inset-x-4 top-4 bg-red-500/20 border border-red-500/50 p-3 rounded-lg flex items-start gap-2 text-red-200 text-sm">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <p>{error}</p>
              </div>
            )}

            {isRecording && (
              <>
                {/* Face Scanning Brackets */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                   <div className="w-48 h-64 border-2 border-[#00ffc8]/50 rounded-3xl relative">
                      <div className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-[#00ffc8] rounded-tl-3xl"></div>
                      <div className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-[#00ffc8] rounded-tr-3xl"></div>
                      <div className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-[#00ffc8] rounded-bl-3xl"></div>
                      <div className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-[#00ffc8] rounded-br-3xl"></div>
                   </div>
                </div>

                <div className="absolute top-4 right-4 flex items-center gap-2 bg-red-500/20 text-red-400 px-3 py-1 rounded-full text-xs font-bold font-mono border border-red-500/30">
                  <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                  RECORDING ({10 - (progress/10)}s)
                </div>
              </>
            )}

            {isProcessing && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/60 backdrop-blur-sm z-10">
                 {!error && (
                   <>
                      <div className="w-16 h-16 rounded-full border-4 border-[#00ffc8]/20 border-t-[#00ffc8] animate-spin mb-4" />
                      <p className="text-[#00ffc8] font-mono tracking-widest text-sm uppercase">Analyzing Vitals...</p>
                      <p className="text-white/40 text-xs mt-2 text-center px-8">Extracting rPPG heartbeat and dominant emotion signatures via neural processing.</p>
                   </>
                 )}
              </div>
            )}
            
            {/* Progress Bar (Bottom) */}
            {isRecording && (
                <div className="absolute bottom-0 left-0 w-full h-1 bg-white/10">
                   <div 
                      className="h-full bg-gradient-to-r from-[#6464ff] to-[#00ffc8] transition-all duration-1000 ease-linear"
                      style={{ width: `${progress}%` }}
                   />
                </div>
            )}

          </div>

          {/* Guidelines & Controls */}
          <div className="p-6 bg-white/5 relative z-20">
             <div className="flex flex-col gap-4">
                 
                <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-sm text-white/70">
                   <ul className="space-y-2">
                     <li className="flex items-center gap-2">
                       <CheckCircle2 className="w-4 h-4 text-[#00ffc8]" />
                       Ensure your face is well-lit and centered.
                     </li>
                     <li className="flex items-center gap-2">
                       <CheckCircle2 className="w-4 h-4 text-[#00ffc8]" />
                       Hold still for 10 seconds.
                     </li>
                     <li className="flex items-center gap-2">
                       <CheckCircle2 className="w-4 h-4 text-[#00ffc8]" />
                       Keep a natural expression during the scan.
                     </li>
                   </ul>
                </div>

                <button
                  onClick={startScan}
                  disabled={isRecording || isProcessing || !!error}
                  className={`w-full py-4 rounded-xl flex items-center justify-center gap-2 font-bold tracking-widest uppercase transition-all
                    ${(isRecording || isProcessing || !!error) 
                      ? 'bg-white/10 text-white/30 cursor-not-allowed' 
                      : 'bg-[#6464ff] hover:bg-[#5252ff] text-white shadow-[0_0_20px_rgba(100,100,255,0.3)]'}
                  `}
                >
                  {isRecording ? (
                     <>Scanning...</>
                  ) : isProcessing ? (
                     <>Analyzing...</>
                  ) : (
                     <><Camera className="w-5 h-5" /> Start 10s Scan</>
                  )}
                </button>
             </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
