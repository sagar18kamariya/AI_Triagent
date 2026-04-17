import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Send, Bot, User, AlertTriangle, Stethoscope, Activity, AlertCircle, Camera } from 'lucide-react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { VitalsScanner } from './VitalsScanner';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: any;
}

// ================== SEVERITY ==================
const SeverityBanner = ({ severity }: { severity: string }) => {
  const colors = {
    critical: 'bg-gradient-to-r from-red-600 to-red-800',
    high: 'bg-gradient-to-r from-orange-500 to-red-600',
    medium: 'bg-gradient-to-r from-yellow-500 to-orange-500',
    low: 'bg-gradient-to-r from-green-500 to-emerald-600',
    normal: 'bg-gradient-to-r from-blue-500 to-cyan-500',
  };

  const colorClass = colors[severity?.toLowerCase() as keyof typeof colors] || colors.normal;

  return (
    <div className={`${colorClass} p-3 rounded-lg mb-3 flex items-center justify-center gap-2`}>
      <AlertTriangle className="w-5 h-5 text-white animate-pulse" />
      <span className="text-white font-bold uppercase text-sm">
        Severity Level: {severity || 'UNKNOWN'}
      </span>
    </div>
  );
};

// ================== RESPONSE CARD ==================
const MedicalResponseCard = ({ metadata, content }: { metadata: any, content: string }) => {
  if (!metadata || metadata.mode !== 'medical') {
    return <p className="text-white/90 text-sm whitespace-pre-wrap">{content}</p>;
  }

  return (
    <div className="w-full">
      <SeverityBanner severity={metadata.risk} />

      <div className="bg-white/5 border border-white/10 rounded-xl p-4 space-y-4">
        <div className="flex items-center gap-2 border-b border-white/10 pb-2">
          <Stethoscope className="w-5 h-5 text-[#6464ff]" />
          <h3 className="text-white font-semibold">Doctor Recommendation</h3>
        </div>

        <div>
          <span className="text-white/60 text-xs">Detected Symptoms</span>
          <div className="flex flex-wrap gap-2 mt-1">
            {metadata.symptoms?.map((s: string, i: number) => (
              <span key={i} className="px-2 py-1 text-xs bg-white/10 rounded">
                {s}
              </span>
            ))}
          </div>
        </div>

        <div>
          <span className="text-white/60 text-xs">Predicted Disease</span>
          <div className="flex items-center gap-2 text-[#ff6464] mt-1">
            <AlertTriangle className="w-4 h-4" />
            <span className="font-semibold">{metadata.disease || 'Unknown'}</span>
          </div>
        </div>

        <div>
          <span className="text-white/60 text-xs">Specialist</span>
          <div className="flex items-center gap-2 text-[#00ffc8] mt-1">
            <Activity className="w-4 h-4" />
            {metadata.doctor}
          </div>
        </div>

        <div>
          <span className="text-white/60 text-xs">Advice</span>
          <p className="text-white/90 text-sm mt-1">{content}</p>
        </div>

        {['high', 'critical'].includes(metadata.risk?.toLowerCase()) && (
          <div className="flex gap-2 bg-red-500/10 p-2 rounded">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <p className="text-red-200 text-xs">Seek medical help immediately.</p>
          </div>
        )}
      </div>
    </div>
  );
};

// ================== MAIN ==================
export function AIChat() {
  const { user } = useAuth();

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hello! I'm your AI medical assistant. How can I help?",
      timestamp: new Date(),
    },
  ]);

  const [input, setInput] = useState('');
  const [allSymptoms, setAllSymptoms] = useState<string[]>([]);
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [showScanner, setShowScanner] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // ================== VITALS HANDLER ==================
  const handleVitalsScanned = (vitalsData: { heartRate: number; emotion: string }) => {
    setShowScanner(false);
    const scanMsg = `System log: Patient vitals scanned via camera. Heart Rate: ${vitalsData.heartRate} BPM. Detected emotion: ${vitalsData.emotion}.`;
    
    // Briefly delay to let the UI settle before sending
    setTimeout(() => {
       handleSend(scanMsg);
    }, 500);
  };

  // ================== SCROLL ==================
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // ================== LOAD SYMPTOMS ==================
  useEffect(() => {
    api.getSymptoms()
      .then((data) => {
        console.log("API DATA:", data);
        setAllSymptoms(data);
      })
      .catch((err) => console.error(err));
  }, []);

  // ================== FILTER ==================
  useEffect(() => {
    if (!input.trim()) {
      setFilteredSuggestions([]);
      return;
    }

    const inputLower = input.toLowerCase().trim();
    const inputWords = inputLower.split(/\s+/).filter(w => w.length > 0);
    
    const filtered = allSymptoms
      .map(s => s.replace(/_/g, ' '))
      .filter(symptom => {
        const symptomLower = symptom.toLowerCase();
        
        // If input is multi-word, check if symptom contains all input words
        if (inputWords.length > 1) {
          return inputWords.every(word => symptomLower.includes(word));
        }
        
        // For single word input, check if symptom contains the word
        // or if any word in symptom starts with the input
        return symptomLower.includes(inputLower) ||
               symptomLower.split(/\s+/).some(word => word.startsWith(inputLower));
      })
      .slice(0, 8); // Show more suggestions

    setFilteredSuggestions(filtered);
  }, [input, allSymptoms]);

  // ================== SEND ==================
  const handleSend = async (text?: string) => {
    const messageText = text || input;
    if (!messageText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setFilteredSuggestions([]);
    setIsTyping(true);

    const aiMessageId = (Date.now() + 1).toString();

    setMessages(prev => [
      ...prev,
      {
        id: aiMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      }
    ]);

    try {
      await api.triageStream(
        messageText,
        (data) => {
          if (data.type === 'result') {
            const finalData = data.data;

            setMessages(prev =>
              prev.map(msg =>
                msg.id === aiMessageId
                  ? {
                      ...msg,
                      metadata: finalData,
                      content: finalData.advice
                    }
                  : msg
              )
            );
          }
        },
        user?.id
      );
    } catch (err) {
      console.error(err);
    } finally {
      setIsTyping(false);
    }
  };

  // ================== UI ==================
  return (
    <div className="flex flex-col h-full rounded-xl overflow-hidden bg-black/40 backdrop-blur-md border border-white/10">

      {/* HEADER */}
      <div className="p-4 border-b border-white/10 flex items-center gap-2">
        <Bot className="text-[#00ffc8]" />
        <span className="text-white">AI Medical Assistant</span>
      </div>

      {/* MESSAGES */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className="max-w-[80%]">

                {/* USER */}
                {msg.role === 'user' && (
                  <div className="bg-[#6464ff]/20 border border-[#6464ff]/30 p-3 rounded-xl text-white text-sm">
                    {msg.content}
                  </div>
                )}

                {/* ASSISTANT */}
                {msg.role === 'assistant' && (
                  <>
                    {msg.metadata ? (
                      <MedicalResponseCard metadata={msg.metadata} content={msg.content} />
                    ) : (
                      <div className="bg-white/5 border border-white/10 p-3 rounded-xl text-white text-sm">
                        {msg.content || (
                          <span className="flex items-center gap-2">
                            <Activity className="w-4 h-4 animate-pulse text-[#00ffc8]" />
                            Analyzing symptoms...
                          </span>
                        )}
                      </div>
                    )}
                  </>
                )}

              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* ECG STYLE TYPING */}
        {isTyping && (
          <div className="flex items-center gap-2 text-[#00ffc8] text-sm">
            <Activity className="w-5 h-5 animate-pulse" />
            <span className="animate-pulse">Analyzing (ECG)...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* SCANNER MODAL */}
      {showScanner && (
        <VitalsScanner 
          onClose={() => setShowScanner(false)} 
          onScanComplete={handleVitalsScanned} 
        />
      )}

      {/* INPUT */}
      <div className="p-4 border-t border-white/10">
        <div className="flex gap-2">
          <button 
            onClick={() => setShowScanner(true)}
            className="p-3 bg-white/5 hover:bg-white/10 text-[#00ffc8] rounded transition-colors shadow-lg"
            title="Scan Vitals (Camera)"
          >
            <Camera className="w-5 h-5 flex-shrink-0" />
          </button>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            className="flex-1 p-2 bg-white/5 text-white rounded outline-none"
            placeholder="Type symptoms or scan vitals..."
          />
          <button onClick={() => handleSend()} className="px-4 bg-[#00ffc8] text-black rounded hover:bg-[#00cca0] transition-colors">
            <Send className="w-5 h-5" />
          </button>
        </div>

        {/* SUGGESTIONS */}
        {filteredSuggestions.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {filteredSuggestions.map((item, index) => (
              <button
                key={index}
                onClick={() => handleSend(item)}
                className="text-xs px-3 py-1 bg-white/10 rounded text-white hover:bg-[#00ffc8]/20"
              >
                {item}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}