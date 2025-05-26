import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, MessagesSquare } from 'lucide-react';
import Button from '../ui/Button';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

const suggestedPrompts = [
  "What are the early symptoms of Parkinson's?",
  "How is Parkinson's diagnosed?",
  "What treatments are available?",
  "What does my diagnosis mean?",
  "How can I slow down symptom progression?",
  "What are the latest research findings?",
];

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your  assistant. I can help answer questions about Parkinson's disease, symptoms, treatments, and more. How can I assist you today?",
      sender: 'bot',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (text: string = input) => {
    if (!text.trim()) return;
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);
    
    // Simulate bot response after delay
    setTimeout(() => {
      const botResponses: { [key: string]: string } = {
        "What are the early symptoms of Parkinson's?": 
          "Early symptoms of Parkinson's disease often include tremors (especially in the hands), bradykinesia (slowness of movement), limb rigidity, and problems with balance and coordination. Some people may also notice smaller handwriting, reduced facial expressions, or a softer voice. These symptoms typically begin gradually and worsen over time.",
        
        "How is Parkinson's diagnosed?": 
          "Parkinson's disease is primarily diagnosed through clinical evaluation by a neurologist. There's no single test for it. Doctors look for cardinal symptoms like tremor, rigidity, and bradykinesia. They may order brain scans (MRI or DaTscan) to rule out other conditions. Sometimes, response to Parkinson's medication is used as a confirmation. Genetic testing may be recommended in cases with family history.",
        
        "What treatments are available?": 
          "Treatments for Parkinson's include medications like levodopa, dopamine agonists, and MAO-B inhibitors that help manage symptoms. Deep brain stimulation (DBS) surgery is an option for some patients. Physical, occupational, and speech therapy are also important. While there's no cure yet, these approaches can significantly improve quality of life.",
        
        "What does my diagnosis mean?": 
          "A Parkinson's diagnosis means your brain is producing less dopamine, affecting movement control. It's a progressive condition, but progression varies greatly between individuals. Many people live full, productive lives for many years after diagnosis. Early intervention with medication, exercise, and therapy can help manage symptoms effectively. It's important to work with a movement disorder specialist to develop a personalized treatment plan.",
        
        "How can I slow down symptom progression?": 
          "Regular exercise is one of the most effective ways to potentially slow Parkinson's progression - aim for activities that challenge balance, coordination, and flexibility. Maintain a nutritious diet rich in antioxidants. Stay mentally active with cognitive exercises. Follow your medication regimen consistently. Manage stress through meditation or other relaxation techniques. Early intervention with physical and occupational therapy can help maintain function longer.",
        
        "What are the latest research findings?": 
          "Recent Parkinson's research is exploring several promising areas: new drug therapies targeting alpha-synuclein protein aggregation, gene therapies for specific genetic forms, stem cell treatments to replace lost neurons, and advanced wearable technologies for better symptom monitoring. Researchers are also investigating gut-brain connections and the role of inflammation. Clinical trials are ongoing for several potential disease-modifying treatments."
      };
      
      // Default response for queries not in our predefined list
      let responseText = "I don't have specific information on that topic. Please ask your healthcare provider for medical advice tailored to your situation. I can answer general questions about Parkinson's symptoms, diagnosis, and treatments.";
      
      // Check if we have a predefined answer
      const lowerCaseText = text.toLowerCase();
      for (const [key, value] of Object.entries(botResponses)) {
        if (lowerCaseText.includes(key.toLowerCase()) || 
            key.toLowerCase().includes(lowerCaseText)) {
          responseText = value;
          break;
        }
      }
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        sender: 'bot',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, botMessage]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <div className="bg-white rounded-2xl shadow-neuro overflow-hidden flex flex-col h-[600px]">
      {/* Header */}
      <div className="bg-primary p-4 text-white flex items-center">
        <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center mr-3">
          <Bot size={20} />
        </div>
        <div>
          <h3 className="font-semibold">Assistant</h3>
          <p className="text-xs text-white/70">Parkinson's Medical Guide</p>
        </div>
      </div>
      
      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.map((message) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex mb-4 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`flex ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.sender === 'user' 
                  ? 'bg-primary/10 text-primary ml-2' 
                  : 'bg-gray-200 text-gray-700 mr-2'
              }`}>
                {message.sender === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>
              
              <div className={`chat-message ${
                message.sender === 'user' 
                  ? 'user-message' 
                  : 'bot-message shadow-sm'
              }`}>
                <p className="text-sm">{message.text}</p>
                <div className={`text-xs mt-1 ${
                  message.sender === 'user' ? 'text-primary/60' : 'text-gray-400'
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
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="flex mb-4"
            >
              <div className="flex flex-row">
                <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center mr-2">
                  <Bot size={16} className="text-gray-700" />
                </div>
                <div className="chat-message bot-message">
                  <div className="flex space-x-1">
                    <motion.div
                      animate={{ y: [0, -5, 0] }}
                      transition={{ repeat: Infinity, duration: 1 }}
                      className="w-2 h-2 bg-gray-400 rounded-full"
                    />
                    <motion.div
                      animate={{ y: [0, -5, 0] }}
                      transition={{ repeat: Infinity, duration: 1, delay: 0.2 }}
                      className="w-2 h-2 bg-gray-400 rounded-full"
                    />
                    <motion.div
                      animate={{ y: [0, -5, 0] }}
                      transition={{ repeat: Infinity, duration: 1, delay: 0.4 }}
                      className="w-2 h-2 bg-gray-400 rounded-full"
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Suggested prompts */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 flex overflow-x-auto">
        {suggestedPrompts.map((prompt, index) => (
          <button
            key={index}
            onClick={() => handleSendMessage(prompt)}
            className="flex-shrink-0 bg-white text-xs px-3 py-2 rounded-full border border-gray-200 mr-2 hover:border-primary hover:bg-primary/5 transition-colors whitespace-nowrap"
          >
            {prompt}
          </button>
        ))}
      </div>
      
      {/* Input area */}
      <div className="p-4 border-t border-gray-200">
        <form 
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="flex"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question here..."
            className="flex-1 rounded-l-xl px-4 py-2 border border-gray-300 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none"
          />
          <Button
            type="submit"
            className="rounded-l-none"
            icon={<Send size={16} />}
            disabled={!input.trim()}
          >
            Send
          </Button>
        </form>
        <div className="mt-2 text-xs text-gray-400 flex items-center">
          <MessagesSquare size={12} className="mr-1" />
          For medical concerns, always consult with a healthcare professional
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;