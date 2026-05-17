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

  // Spread getRootProps onto a plain <div> to avoid Framer Motion's onDrag type conflict
  const rootProps = getRootProps();

  return (
    <div style={{ width: '100%' }}>
      <div
        {...rootProps}
        style={{
          border: `2px dashed ${isDragActive ? 'var(--gold)' : 'var(--border-strong)'}`,
          borderRadius: 'var(--radius)',
          padding: '2.5rem 1.5rem',
          textAlign: 'center',
          cursor: isUploading ? 'not-allowed' : 'pointer',
          background: isDragActive ? 'var(--gold-pale)' : 'var(--bg-primary)',
          transition: 'all 0.25s ease',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <input {...getInputProps()} />

        <AnimatePresence mode="wait">
          {isUploading ? (
            <motion.div key="uploading" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div style={{ marginBottom: '1rem' }}>
                <div className="spinner" style={{ width: 36, height: 36, margin: '0 auto', borderTopColor: 'var(--navy)' }} />
              </div>
              <p style={{ color: 'var(--navy)', fontWeight: 700, fontSize: '1rem' }}>
                Uploading &amp; starting analysis...
              </p>
              <p style={{ color: 'var(--text-secondary)', marginTop: 6, fontSize: '0.85rem' }}>
                AI agents are being deployed
              </p>
            </motion.div>
          ) : isDragActive ? (
            <motion.div key="drag" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
              <CheckCircle size={44} color="var(--gold)" style={{ margin: '0 auto 1rem' }} />
              <p style={{ color: 'var(--gold)', fontWeight: 700, fontSize: '1.1rem' }}>
                Drop to analyze!
              </p>
            </motion.div>
          ) : (
            <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div style={{
                width: 64, height: 64, margin: '0 auto 1.25rem',
                borderRadius: 16,
                background: 'var(--navy-pale)',
                border: '1px solid #c8d5e8',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <Upload size={28} color="var(--navy)" />
              </div>
              <p style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 6, color: 'var(--text-primary)' }}>
                Drop your contract here
              </p>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.25rem', fontSize: '0.85rem' }}>
                or click to browse — up to 20MB
              </p>
              <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
                {['PDF', 'DOCX', 'PNG', 'JPG', 'TIFF'].map(type => (
                  <span key={type} style={{
                    padding: '3px 10px', borderRadius: 99,
                    background: 'white',
                    border: '1px solid var(--border-strong)',
                    fontSize: '0.72rem',
                    color: 'var(--text-secondary)',
                    display: 'flex', alignItems: 'center', gap: 4,
                    fontWeight: 600,
                  }}>
                    <FileText size={10} />
                    {type}
                  </span>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -6 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            display: 'flex', alignItems: 'center', gap: 8,
            color: 'var(--critical)', marginTop: 10,
            fontSize: '0.82rem',
          }}
        >
          <AlertCircle size={14} /> {error}
        </motion.div>
      )}
    </div>
  );
}
