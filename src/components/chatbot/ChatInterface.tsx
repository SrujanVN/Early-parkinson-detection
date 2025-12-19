import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, MessagesSquare, Sparkles, Trash2 } from 'lucide-react';
import { sendChatMessage } from '../../utils/api';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const MessageFormatter: React.FC<{ text: string }> = ({ text }) => {
  // Pattern to match text inside double asterisks or specific key phrases
  const parts = text.split(/(\*\*.*?\*\*|Care and Treatment Options:|Clinical Insights:|Diagnosis:|Recommendation:)/g);

  return (
    <>
      {parts.map((part, i) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <span key={i} className="message-highlight">{part.slice(2, -2)}</span>;
        }
        if (['Care and Treatment Options:', 'Clinical Insights:', 'Diagnosis:', 'Recommendation:'].includes(part)) {
          return <span key={i} className="message-highlight !bg-primary/10 !border-primary/30 mb-2">{part}</span>;
        }
        return <span key={i}>{part}</span>;
      })}
    </>
  );
};

const TypewriterText: React.FC<{ text: string; onUpdate?: () => void; onComplete?: () => void }> = ({ text, onUpdate, onComplete }) => {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    setDisplayedText('');
    const words = text.split(/(\s+)/);
    let currentWordIndex = 0;
    let accumulated = '';

    const stream = setInterval(() => {
      if (currentWordIndex < words.length) {
        accumulated += words[currentWordIndex];
        setDisplayedText(accumulated);
        currentWordIndex++;
      } else {
        clearInterval(stream);
        if (onComplete) onComplete();
      }
    }, 20);

    return () => clearInterval(stream);
  }, [text, onComplete]);

  // Handle scrolling when text updates
  useEffect(() => {
    if (onUpdate) onUpdate();
  }, [displayedText, onUpdate]);

  return <MessageFormatter text={displayedText} />;
};

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Good day. I am Assistant. I am here to provide you with support and information regarding Parkinson's disease research and care. How may I be of assistance to you today?",
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Improved scroll handling: Continuous scroll to bottom during generation
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({
        top: scrollContainerRef.current.scrollHeight,
        behavior: messages.length > 2 ? 'smooth' : 'auto'
      });
    }
  }, [messages]);

  const handleSendMessage = async (text: string = input) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const data = await sendChatMessage(text, [userMessage]);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        sender: 'bot',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Assistant: I apologize, but I am currently experiencing a connection difficulty. Please check your network or try again shortly.",
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const clearChat = () => {
    setMessages([{
      id: Date.now().toString(),
      text: "Hello. I am Assistant. How may I help you today?",
      sender: 'bot',
      timestamp: new Date(),
    }]);
  };

  return (
    <div className="flex flex-col h-[650px] w-full transition-all relative glassmorphism overflow-hidden">
      {/* Header */}
      <div className="bg-card/80 backdrop-blur-md border-b border-divider p-6 flex items-center justify-between shadow-sm z-10">
        <div className="flex items-center">
          <div className="relative">
            <div className="w-12 h-12 rounded-2xl bg-primary/5 flex items-center justify-center mr-4 border border-divider shadow-inner">
              <Bot size={24} className="text-primary" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-green-500 rounded-full border-2 border-card shadow-sm" />
          </div>
          <div>
            <div className="flex items-center">
              <h3 className="text-lg font-bold text-text tracking-tight">Assistant</h3>
              <Sparkles size={14} className="ml-2 text-primary opacity-60" />
            </div>
            <p className="text-[10px] text-text/40 font-bold uppercase tracking-[0.2em]">Neural Intelligence Node</p>
          </div>
        </div>
        <button
          onClick={clearChat}
          className="p-2.5 hover:bg-primary/10 rounded-xl transition-all text-text/40 hover:text-red-500 hover:shadow-sm"
          title="Clear Conversation"
        >
          <Trash2 size={18} />
        </button>
      </div>

      {/* Chat messages */}
      <div
        ref={scrollContainerRef}
        className="flex-1 overflow-y-auto p-6 space-y-8 bg-gray-50/5 scroll-smooth"
      >
        {messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} w-full`}
          >
            <div className={`flex max-w-[88%] ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm transition-transform hover:scale-105 ${message.sender === 'user'
                ? 'bg-primary text-white ml-3'
                : 'bg-card border border-divider text-primary mr-3'
                }`}>
                {message.sender === 'user' ? <User size={18} /> : <Bot size={18} />}
              </div>

              <div className={`relative px-6 py-4 rounded-3xl ${message.sender === 'user'
                ? 'bg-primary text-primary-foreground shadow-lg rounded-tr-none'
                : 'bg-card text-text shadow-xl border border-divider rounded-tl-none'
                }`}>
                <div className="text-[15px] leading-relaxed whitespace-pre-wrap font-medium">
                  {message.sender === 'bot' && index === messages.length - 1 && index !== 0 ? (
                    <TypewriterText
                      text={message.text}
                      onUpdate={() => {
                        if (scrollContainerRef.current) {
                          scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
                        }
                      }}
                    />
                  ) : message.sender === 'bot' ? (
                    <MessageFormatter text={message.text} />
                  ) : (
                    message.text
                  )}
                </div>
                <div className={`text-[9px] mt-3 font-bold uppercase tracking-widest ${message.sender === 'user' ? 'text-white/50' : 'text-text/40'
                  }`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          </motion.div>
        ))}

        {/* Typing indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="flex items-center space-x-3"
            >
              <div className="w-9 h-9 rounded-xl bg-card border border-divider flex items-center justify-center text-primary shadow-sm">
                <Bot size={18} />
              </div>
              <div className="bg-card/80 border border-divider px-5 py-4 rounded-3xl rounded-tl-none shadow-md flex items-center space-x-1.5">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 1 }}
                  className="w-1.5 h-1.5 bg-primary/40 rounded-full"
                />
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 1, delay: 0.2 }}
                  className="w-1.5 h-1.5 bg-primary/60 rounded-full"
                />
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ repeat: Infinity, duration: 1, delay: 0.4 }}
                  className="w-1.5 h-1.5 bg-primary/80 rounded-full"
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Input area */}
      <div className="p-6 bg-card/80 backdrop-blur-md border-t border-divider">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="relative flex items-center group"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Talk to Assistant..."
            className="w-full bg-background/50 border border-divider rounded-2xl px-6 py-4 pr-16 focus:ring-4 focus:ring-primary/10 focus:border-primary focus:bg-card outline-none transition-all text-text placeholder:text-text/40 font-medium shadow-inner"
          />
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className={`absolute right-2 p-3.5 rounded-xl transition-all ${!input.trim() || isTyping
              ? 'bg-gray-100 text-gray-400'
              : 'bg-primary text-white hover:bg-primary/90 shadow-lg hover:scale-105 active:scale-95'
              }`}
          >
            <Send size={18} />
          </button>
        </form>
        <div className="mt-4 flex items-center justify-center space-x-6 text-[9px] text-text/40 font-bold uppercase tracking-[0.2em]">
          <div className="flex items-center">
            <Sparkles size={11} className="mr-1.5 text-primary/40" />
            Active Node
          </div>
          <div className="flex items-center">
            <MessagesSquare size={11} className="mr-1.5 text-primary/40" />
            Neural Comms
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;