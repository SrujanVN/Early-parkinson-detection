import React, { createContext, useContext, useState, ReactNode } from 'react';

interface UploadedImage {
  file: File | null;
  previewUrl: string | null;
  originalUrl: string | null; // Original uploaded image as base64 or URL
  gradcamUrl: string | null; // GradCAM overlay image
}

interface ImageContextType {
  uploadedImage: UploadedImage;
  setUploadedImage: (image: UploadedImage) => void;
  clearImage: () => void;
}

const ImageContext = createContext<ImageContextType | undefined>(undefined);

export const ImageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [uploadedImage, setUploadedImageState] = useState<UploadedImage>({
    file: null,
    previewUrl: null,
    originalUrl: null,
    gradcamUrl: null,
  });

  const setUploadedImage = (image: UploadedImage) => {
    setUploadedImageState(image);
    // Also store in sessionStorage for persistence
    if (image.originalUrl) {
      sessionStorage.setItem('uploadedImageUrl', image.originalUrl);
    }
    if (image.gradcamUrl) {
      sessionStorage.setItem('gradcamImageUrl', image.gradcamUrl);
    }
  };

  const clearImage = () => {
    setUploadedImageState({
      file: null,
      previewUrl: null,
      originalUrl: null,
      gradcamUrl: null,
    });
    sessionStorage.removeItem('uploadedImageUrl');
    sessionStorage.removeItem('gradcamImageUrl');
  };

  // Load from sessionStorage on mount
  React.useEffect(() => {
    const savedOriginal = sessionStorage.getItem('uploadedImageUrl');
    const savedGradcam = sessionStorage.getItem('gradcamImageUrl');
    if (savedOriginal || savedGradcam) {
      setUploadedImageState(prev => ({
        ...prev,
        originalUrl: savedOriginal,
        gradcamUrl: savedGradcam,
      }));
    }
  }, []);

  const value: ImageContextType = {
    uploadedImage,
    setUploadedImage,
    clearImage,
  };

  return <ImageContext.Provider value={value}>{children}</ImageContext.Provider>;
};

export const useImage = () => {
  const context = useContext(ImageContext);
  if (context === undefined) {
    throw new Error('useImage must be used within an ImageProvider');
  }
  return context;
};
