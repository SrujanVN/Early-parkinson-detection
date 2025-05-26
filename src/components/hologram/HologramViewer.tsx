import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Maximize, Minimize, RotateCw, Eye, EyeOff } from 'lucide-react';
import Button from '../ui/Button';

interface HologramViewerProps {
  imageUrl: string;
  overlayUrl?: string;
  title: string;
}

const HologramViewer: React.FC<HologramViewerProps> = ({ 
  imageUrl, 
  overlayUrl,
  title
}) => {
  const [rotation, setRotation] = useState({ x: 0, y: 0 });
  const [isZoomed, setIsZoomed] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);
  const [autoRotate, setAutoRotate] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  // Handle mouse move for interactive rotation
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current || autoRotate) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const x = (e.clientY - rect.top) / rect.height - 0.5;
    const y = (e.clientX - rect.left) / rect.width - 0.5;
    
    setRotation({
      x: x * 20, // Limit rotation to 20 degrees
      y: y * 20,
    });
  };

  // Auto rotation effect
  useEffect(() => {
    if (!autoRotate) return;
    
    let animationFrameId: number;
    let angle = 0;
    
    const rotate = () => {
      angle += 0.005;
      setRotation({
        x: Math.sin(angle) * 5,
        y: Math.cos(angle) * 5,
      });
      animationFrameId = requestAnimationFrame(rotate);
    };
    
    rotate();
    
    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [autoRotate]);

  return (
    <div className={`${isZoomed ? 'fixed inset-0 z-50 bg-black/90 flex items-center justify-center' : 'w-full'}`}>
      {/* Hologram container */}
      <div className="relative max-w-3xl mx-auto">
        {/* Controls */}
        <div className="absolute top-4 right-4 z-10 flex space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsZoomed(!isZoomed)}
            icon={isZoomed ? <Minimize size={16} /> : <Maximize size={16} />}
          >
            {isZoomed ? 'Exit' : 'Fullscreen'}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setAutoRotate(!autoRotate)}
            icon={<RotateCw size={16} />}
          >
            {autoRotate ? 'Stop' : 'Auto Rotate'}
          </Button>
          {overlayUrl && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowOverlay(!showOverlay)}
              icon={showOverlay ? <EyeOff size={16} /> : <Eye size={16} />}
            >
              {showOverlay ? 'Hide Overlay' : 'Show Overlay'}
            </Button>
          )}
        </div>
        
        {/* Title */}
        <div className="text-center mb-6">
          <h2 className="text-xl font-semibold">{title}</h2>
          <p className="text-sm text-gray-500">
            Interactive holographic visualization
          </p>
        </div>
        
        {/* Hologram */}
        <motion.div
          ref={containerRef}
          className="hologram rounded-2xl aspect-square max-w-xl mx-auto overflow-hidden"
          onMouseMove={handleMouseMove}
          onMouseLeave={() => autoRotate || setRotation({ x: 0, y: 0 })}
          style={{
            perspective: '1000px',
          }}
        >
          <div className="hologram-glow"></div>
          <motion.div
            style={{
              rotateX: rotation.x,
              rotateY: rotation.y,
              transformStyle: 'preserve-3d',
            }}
            className="w-full h-full relative"
          >
            {/* Base image */}
            <img
              src={imageUrl}
              alt="Holographic visualization"
              className="w-full h-full object-cover rounded-2xl"
            />
            
            {/* Gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-primary/30 to-transparent rounded-2xl"></div>
            
            {/* Analysis overlay */}
            {showOverlay && overlayUrl && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.8 }}
                className="absolute inset-0"
              >
                <img
                  src={overlayUrl}
                  alt="Analysis overlay"
                  className="w-full h-full object-cover rounded-2xl"
                />
              </motion.div>
            )}
            
            {/* Holographic effects */}
            <div className="absolute inset-0 pointer-events-none">
              {/* Scanline effect */}
              <div className="absolute inset-0 overflow-hidden">
                <motion.div
                  animate={{ 
                    y: ["0%", "100%", "0%"],
                  }}
                  transition={{ 
                    duration: 8, 
                    ease: "linear", 
                    repeat: Infinity,
                  }}
                  className="w-full h-1 bg-primary/20 blur-sm"
                ></motion.div>
              </div>
              
              {/* Edge glow */}
              <div className="absolute inset-0 rounded-2xl border-2 border-primary/30"></div>
              
              {/* Corner markers */}
              {[
                'top-0 left-0', 
                'top-0 right-0',
                'bottom-0 left-0',
                'bottom-0 right-0'
              ].map((position, idx) => (
                <div key={idx} className={`absolute w-6 h-6 ${position} pointer-events-none`}>
                  <div className="w-full h-0.5 bg-primary/50"></div>
                  <div className="w-0.5 h-full bg-primary/50"></div>
                </div>
              ))}
            </div>
          </motion.div>
        </motion.div>
        
        <div className="mt-6 text-center text-sm text-gray-500">
          {autoRotate ? 'Auto-rotating' : 'Move your cursor over the image to rotate'}
        </div>
      </div>
    </div>
  );
};

export default HologramViewer;