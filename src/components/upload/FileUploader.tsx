import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, X, Image, FileAudio, FileSpreadsheet, FileText } from 'lucide-react';
import Button from '../ui/Button';

type FileType = 'MRI' | 'Handwriting' | 'Audio' | 'CSV';

interface FileUploaderProps {
  onFileUpload: (file: File, type: FileType) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFileUpload }) => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [fileType, setFileType] = useState<FileType>('MRI');
  const [error, setError] = useState<string | null>(null);

  // File type configurations
  const fileTypeConfig = {
    MRI: {
      accept: { 'image/*': ['.png', '.jpg', '.jpeg'] },
      icon: <Image size={24} />,
      color: 'text-primary',
    },
    Handwriting: {
      accept: { 'image/*': ['.png', '.jpg', '.jpeg'] },
      icon: <FileText size={24} />,
      color: 'text-secondary',
    },
    Audio: {
      accept: { 'audio/*': ['.mp3', '.wav', '.ogg'] },
      icon: <FileAudio size={24} />,
      color: 'text-accent',
    },
    CSV: {
      accept: { 'text/csv': ['.csv'] },
      icon: <FileSpreadsheet size={24} />,
      color: 'text-success',
    },
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    
    const selectedFile = acceptedFiles[0];
    setFile(selectedFile);
    setError(null);

    // Create preview for images
    if (selectedFile.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    } else {
      setPreview(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: fileTypeConfig[fileType].accept,
    maxFiles: 1,
    onDropRejected: () => {
      setError(`Please upload a valid ${fileType} file.`);
    },
  });

  const resetUpload = () => {
    setFile(null);
    setPreview(null);
    setError(null);
  };

  const handleUpload = () => {
    if (file) {
      onFileUpload(file, fileType);
    }
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">File Type</label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(fileTypeConfig).map(([type, config]) => (
            <button
              key={type}
              onClick={() => {
                setFileType(type as FileType);
                resetUpload();
              }}
              className={`flex items-center justify-center p-3 rounded-xl border transition-all ${
                fileType === type
                  ? `bg-${config.color.split('-')[1]}/10 border-${
                      config.color.split('-')[1]
                    }/30 ${config.color}`
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex flex-col items-center">
                {config.icon}
                <span className="mt-2 text-sm">{type}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
          isDragActive
            ? 'border-primary bg-primary/5'
            : 'border-gray-300 hover:border-primary/50 hover:bg-gray-50'
        }`}
      >
        <input {...getInputProps()} />

        {file ? (
          <div className="space-y-4">
            <div className="relative mx-auto">
              {preview ? (
                <img
                  src={preview}
                  alt="Preview"
                  className="max-h-48 mx-auto rounded-lg object-contain"
                />
              ) : (
                <div className="flex items-center justify-center h-32 w-full">
                  {fileTypeConfig[fileType].icon}
                  <span className="ml-2 text-gray-600">{file.name}</span>
                </div>
              )}
            </div>
            <div className="flex justify-center space-x-3">
              <Button
                variant="outline"
                size="sm"
                icon={<X size={16} />}
                onClick={(e) => {
                  e.stopPropagation();
                  resetUpload();
                }}
              >
                Remove
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-center">
              <motion.div
                animate={{ y: [0, -5, 0] }}
                transition={{ repeat: Infinity, duration: 2 }}
                className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center"
              >
                <Upload className="h-8 w-8 text-primary" />
              </motion.div>
            </div>
            <div>
              <p className="text-lg font-medium">
                Drag & drop your {fileType} file here
              </p>
              <p className="text-sm text-gray-500 mt-1">
                or click to browse from your device
              </p>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-3 text-error text-sm">
          {error}
        </div>
      )}

      <div className="mt-6">
        <Button
          fullWidth
          disabled={!file}
          onClick={handleUpload}
        >
          Submit for  Analysis
        </Button>
      </div>
    </div>
  );
};

export default FileUploader;