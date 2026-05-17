import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';

interface Props {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

export default function UploadZone({ onUpload, isUploading }: Props) {
  const [error, setError] = useState('');

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: unknown[]) => {
      setError('');
      if (rejectedFiles.length > 0) {
        setError('Invalid file type. Please upload PDF, DOCX, or image files.');
        return;
      }
      if (acceptedFiles[0]) onUpload(acceptedFiles[0]);
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/tiff': ['.tiff'],
    },
    maxFiles: 1,
    maxSize: 20 * 1024 * 1024,
    disabled: isUploading,
  });

  const rootProps = getRootProps();

  return (
    <div style={{ width: '100%' }}>
      <div
        {...rootProps}
        style={{
          border: `2px dashed ${isDragActive ? '#1d4ed8' : '#d1d5db'}`,
          borderRadius: 10,
          padding: '2rem 1.5rem',
          textAlign: 'center',
          cursor: isUploading ? 'not-allowed' : 'pointer',
          background: isDragActive ? '#eff6ff' : '#fafafa',
          transition: 'all 0.2s ease',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <input {...getInputProps()} />
        <AnimatePresence mode="wait">
          {isUploading ? (
            <motion.div key="uploading" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div style={{ marginBottom: '1rem' }}>
                <div className="spinner" style={{ width: 34, height: 34, margin: '0 auto', borderTopColor: '#1d4ed8' }} />
              </div>
              <p style={{ color: '#1a2e4a', fontWeight: 700, fontSize: '0.95rem' }}>
                Uploading &amp; starting analysis...
              </p>
              <p style={{ color: '#6b7280', marginTop: 6, fontSize: '0.82rem' }}>
                AI agents are being deployed
              </p>
            </motion.div>
          ) : isDragActive ? (
            <motion.div key="drag" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
              <CheckCircle size={40} color="#1d4ed8" style={{ margin: '0 auto 0.75rem' }} />
              <p style={{ color: '#1d4ed8', fontWeight: 700, fontSize: '1rem' }}>
                Drop to analyze!
              </p>
            </motion.div>
          ) : (
            <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div style={{
                width: 52, height: 52, margin: '0 auto 1rem',
                borderRadius: 12, background: '#eff6ff',
                border: '1px solid #bfdbfe',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Upload size={24} color="#1d4ed8" />
              </div>
              <p style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: 4, color: '#111827' }}>
                Drop your contract here
              </p>
              <p style={{ color: '#9ca3af', marginBottom: '1rem', fontSize: '0.82rem' }}>
                or click to browse — PDF, DOCX, PNG, JPG, TIFF up to 20 MB
              </p>
              <div style={{ display: 'flex', gap: 6, justifyContent: 'center', flexWrap: 'wrap' }}>
                {['PDF', 'DOCX', 'PNG', 'JPG', 'TIFF'].map(type => (
                  <span key={type} style={{
                    padding: '2px 10px', borderRadius: 99,
                    background: 'white', border: '1px solid #e5e7eb',
                    fontSize: '0.7rem', color: '#6b7280',
                    display: 'flex', alignItems: 'center', gap: 3, fontWeight: 600,
                  }}>
                    <FileText size={9} />{type}
                  </span>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }}
          style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#dc2626', marginTop: 8, fontSize: '0.82rem' }}
        >
          <AlertCircle size={13} /> {error}
        </motion.div>
      )}
    </div>
  );
}
