/**
 * VIDEO BATCH PROCESSOR - Web UI Component Library
 * React components for video upload, processing, transcription, and sync
 *
 * Architecture: Component-based, state managed, real-time WebSocket
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import io from 'socket.io-client';

// ======================== DESIGN TOKENS (From Memory System) ========================

const COLORS = {
  primary: '#0b73d2',
  accent: '#e07a5f',
  neutral: '#f6f7f9',
  dark: '#1a1a1a',
  success: '#4caf50',
  warning: '#ff9800',
  error: '#f44336',
};

const SPACING = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
};

const FONTS = {
  family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  sizes: {
    body: '14px',
    heading: '20px',
    large: '24px',
  },
};

// ======================== STYLED COMPONENTS ========================

const containerStyles = {
  maxWidth: '1200px',
  margin: '0 auto',
  padding: SPACING.lg,
  fontFamily: FONTS.family,
};

const buttonStyles = {
  base: {
    padding: `${SPACING.sm} ${SPACING.md}`,
    border: 'none',
    borderRadius: '4px',
    fontSize: FONTS.sizes.body,
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontFamily: FONTS.family,
  },
  primary: {
    background: COLORS.primary,
    color: 'white',
    '&:hover': { opacity: 0.9 },
  },
  secondary: {
    background: COLORS.neutral,
    color: COLORS.dark,
    border: `1px solid ${COLORS.primary}`,
  },
};

const progressBarStyles = {
  container: {
    width: '100%',
    height: '24px',
    background: COLORS.neutral,
    borderRadius: '4px',
    overflow: 'hidden',
  },
  fill: {
    height: '100%',
    background: COLORS.primary,
    transition: 'width 0.3s ease',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontSize: '12px',
    fontWeight: 'bold',
  },
};

// ======================== PROGRESS BAR COMPONENT ========================

export const ProgressBar = ({ progress = 0, label = '' }) => {
  return (
    <div style={progressBarStyles.container}>
      <div
        style={{
          ...progressBarStyles.fill,
          width: `${progress}%`,
        }}
      >
        {progress > 10 && `${Math.round(progress)}%`}
      </div>
    </div>
  );
};

// ======================== FILE UPLOAD COMPONENT ========================

export const FileUploadArea = ({
  onFilesSelected,
  multiple = true,
  accept = 'video/*',
  maxFiles = 50,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState([]);
  const inputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files).slice(0, maxFiles);
    setFiles(droppedFiles);
    onFilesSelected(droppedFiles);
  };

  const handleInputChange = (e) => {
    const selectedFiles = Array.from(e.target.files || []);
    setFiles(selectedFiles);
    onFilesSelected(selectedFiles);
  };

  return (
    <div
      style={{
        border: isDragging ? `2px dashed ${COLORS.primary}` : `2px dashed ${COLORS.neutral}`,
        borderRadius: '8px',
        padding: SPACING.lg,
        textAlign: 'center',
        cursor: 'pointer',
        background: isDragging ? `${COLORS.primary}10` : 'transparent',
        transition: 'all 0.2s ease',
      }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        multiple={multiple}
        accept={accept}
        onChange={handleInputChange}
        style={{ display: 'none' }}
      />

      <div style={{ fontSize: '32px', marginBottom: SPACING.md }}>📹</div>
      <h3 style={{ color: COLORS.primary, margin: 0 }}>
        {files.length > 0 ? `${files.length} file(s) selected` : 'Drag & drop videos here'}
      </h3>
      <p style={{ color: COLORS.dark, fontSize: '12px', margin: SPACING.sm }}>
        or click to browse (up to {maxFiles} files, .mp4, .mov, .avi)
      </p>

      {files.length > 0 && (
        <div style={{ marginTop: SPACING.md, textAlign: 'left' }}>
          {files.map((file, idx) => (
            <div key={idx} style={{ fontSize: '12px', padding: SPACING.xs }}>
              ✓ {file.name} ({(file.size / 1024 / 1024).toFixed(1)} MB)
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// ======================== BATCH UPLOAD FORM ========================

export const BatchUploadForm = ({ onSubmit }) => {
  const [files, setFiles] = useState([]);
  const [caseId, setCaseId] = useState('');
  const [quality, setQuality] = useState('high');
  const [syncBwc, setSyncBwc] = useState(true);
  const [transcription, setTranscription] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await onSubmit({
        files,
        caseId,
        quality,
        syncBwc,
        transcription,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        ...containerStyles,
        background: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      }}
    >
      <h2 style={{ color: COLORS.primary, marginTop: 0 }}>🎬 Batch Video Upload</h2>

      {/* File Upload */}
      <div style={{ marginBottom: SPACING.lg }}>
        <FileUploadArea onFilesSelected={setFiles} multiple={true} maxFiles={50} />
      </div>

      {/* Case ID */}
      <div style={{ marginBottom: SPACING.lg }}>
        <label style={{ display: 'block', marginBottom: SPACING.sm, fontWeight: '600' }}>
          📋 Case ID
        </label>
        <input
          type="text"
          value={caseId}
          onChange={(e) => setCaseId(e.target.value)}
          placeholder="e.g., case_2026_001"
          required
          style={{
            width: '100%',
            padding: SPACING.md,
            border: `1px solid ${COLORS.neutral}`,
            borderRadius: '4px',
            fontSize: FONTS.sizes.body,
            fontFamily: FONTS.family,
            boxSizing: 'border-box',
          }}
        />
      </div>

      {/* Quality Preset */}
      <div style={{ marginBottom: SPACING.lg }}>
        <label style={{ display: 'block', marginBottom: SPACING.sm, fontWeight: '600' }}>
          ⚙️ Quality
        </label>
        <select
          value={quality}
          onChange={(e) => setQuality(e.target.value)}
          style={{
            width: '100%',
            padding: SPACING.md,
            border: `1px solid ${COLORS.neutral}`,
            borderRadius: '4px',
            fontSize: FONTS.sizes.body,
            fontFamily: FONTS.family,
          }}
        >
          <option value="ultra_low">Ultra Low (240p) - Fastest</option>
          <option value="low">Low (480p) - Mobile</option>
          <option value="medium">Medium (720p) - Balanced</option>
          <option value="high">High (1080p) - HD Evidence</option>
          <option value="ultra_high">Ultra High (4K) - Archive</option>
        </select>
      </div>

      {/* Options */}
      <div
        style={{
          marginBottom: SPACING.lg,
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: SPACING.md,
        }}
      >
        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={transcription}
            onChange={(e) => setTranscription(e.target.checked)}
            style={{ marginRight: SPACING.sm }}
          />
          <span>🎤 Extract Transcription (Whisper)</span>
        </label>

        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={syncBwc}
            onChange={(e) => setSyncBwc(e.target.checked)}
            style={{ marginRight: SPACING.sm }}
          />
          <span>📹 Auto-Sync Multiple Cameras</span>
        </label>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={!files.length || !caseId || loading}
        style={{
          ...buttonStyles.base,
          ...buttonStyles.primary,
          width: '100%',
          padding: SPACING.md,
          fontSize: FONTS.sizes.heading,
          opacity: !files.length || !caseId || loading ? 0.5 : 1,
          cursor: !files.length || !caseId || loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? '⏳ Submitting...' : `✓ Upload ${files.length} Video(s)`}
      </button>
    </form>
  );
};

// ======================== BATCH PROGRESS MONITOR ========================

export const BatchProgressMonitor = ({ batchId, onClose }) => {
  const [status, setStatus] = useState(null);
  const [files, setFiles] = useState([]);
  const [syncStatus, setSyncStatus] = useState(null);
  const socketRef = useRef(null);

  useEffect(() => {
    // Connect WebSocket
    socketRef.current = io(process.env.REACT_APP_API_URL || 'http://localhost:5000', {
      auth: {
        token: localStorage.getItem('jwt_token'),
      },
    });

    // Subscribe to batch updates
    socketRef.current.emit('subscribe_batch', { batch_id: batchId });

    // Listen for events
    socketRef.current.on('batch_status', (data) => {
      setStatus(data);
    });

    socketRef.current.on('batch_progress', (data) => {
      setStatus(data);
    });

    socketRef.current.on('file_processed', (data) => {
      setFiles((prev) => [...prev, { id: data.file_id, status: 'complete', ...data }]);
    });

    socketRef.current.on('sync_progress', (data) => {
      setSyncStatus(data);
    });

    socketRef.current.on('batch_complete', (data) => {
      setStatus({ ...status, status: 'complete' });
    });

    return () => {
      socketRef.current?.disconnect();
    };
  }, [batchId]);

  const progress = status?.progress
    ? (parseInt(status.progress.split(' ')[0]) / parseInt(status.progress.split(' ')[2])) * 100
    : 0;

  return (
    <div
      style={{
        ...containerStyles,
        background: 'white',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ color: COLORS.primary, margin: 0 }}>
          📊 Processing: {batchId.substring(0, 8)}...
        </h2>
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            fontSize: '24px',
            cursor: 'pointer',
          }}
        >
          ✕
        </button>
      </div>

      {/* Overall Progress */}
      <div style={{ marginBottom: SPACING.lg }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: SPACING.sm }}>
          <span style={{ fontWeight: '600' }}>Overall Progress</span>
          <span style={{ color: COLORS.primary, fontWeight: '600' }}>
            {status?.progress || '0 / 0'}
          </span>
        </div>
        <ProgressBar progress={progress} />
      </div>

      {/* Sync Status */}
      {syncStatus && (
        <div
          style={{
            background: COLORS.neutral,
            padding: SPACING.md,
            borderRadius: '4px',
            marginBottom: SPACING.lg,
          }}
        >
          <h4 style={{ margin: `0 0 ${SPACING.sm} 0` }}>📹 Multi-Camera Synchronization</h4>
          <div style={{ fontSize: '12px', color: COLORS.dark }}>
            <div>✓ Total Videos: {syncStatus.total_videos}</div>
            <div>
              ✓ Synced: {syncStatus.synced_videos}/{syncStatus.total_videos}
            </div>
            <div>✓ Confidence: {syncStatus.progress_percent || 0}%</div>
          </div>
        </div>
      )}

      {/* File List */}
      <div style={{ marginTop: SPACING.lg }}>
        <h4 style={{ marginTop: 0 }}>📁 Files ({files.length})</h4>
        {files.map((file, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: SPACING.sm,
              borderBottom: `1px solid ${COLORS.neutral}`,
              fontSize: '12px',
            }}
          >
            <span>{file.id.substring(0, 12)}...</span>
            <span
              style={{
                background: file.status === 'complete' ? COLORS.success : COLORS.warning,
                color: 'white',
                padding: `${SPACING.xs} ${SPACING.sm}`,
                borderRadius: '4px',
              }}
            >
              {file.status === 'complete' ? '✓ Done' : '⏳ Processing'}
            </span>
          </div>
        ))}
      </div>

      {/* Status */}
      <div
        style={{
          marginTop: SPACING.lg,
          padding: SPACING.md,
          background: COLORS.neutral,
          borderRadius: '4px',
        }}
      >
        <span style={{ fontWeight: '600' }}>Status: </span>
        <span style={{ color: COLORS.primary }}>
          {status?.status === 'complete' ? '✓ Complete' : '⏳ In Progress'}
        </span>
      </div>
    </div>
  );
};

// ======================== TRANSCRIPTION VIEWER ========================

export const TranscriptionViewer = ({ fileId, onClose }) => {
  const [transcription, setTranscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTranscription = async () => {
      try {
        const response = await fetch(
          `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/upload/file/${fileId}/transcription`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('jwt_token')}`,
            },
          }
        );
        const data = await response.json();
        setTranscription(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTranscription();
  }, [fileId]);

  if (loading) return <div>⏳ Loading transcription...</div>;
  if (error) return <div style={{ color: COLORS.error }}>❌ Error: {error}</div>;
  if (!transcription) return <div>No transcription available</div>;

  return (
    <div
      style={{
        ...containerStyles,
        background: 'white',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        maxHeight: '600px',
        overflowY: 'auto',
      }}
    >
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: SPACING.lg,
        }}
      >
        <h3 style={{ color: COLORS.primary, margin: 0 }}>🎤 Transcription</h3>
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            fontSize: '24px',
            cursor: 'pointer',
          }}
        >
          ✕
        </button>
      </div>

      {/* Metadata */}
      <div
        style={{
          background: COLORS.neutral,
          padding: SPACING.md,
          borderRadius: '4px',
          marginBottom: SPACING.lg,
          fontSize: '12px',
        }}
      >
        <div>📊 Word Count: {transcription.full_text?.split(' ').length || 0}</div>
        <div>📌 Segments: {transcription.segments?.length || 0}</div>
        <div>🌐 Language: {transcription.language}</div>
      </div>

      {/* Full Text */}
      <div style={{ marginBottom: SPACING.lg }}>
        <h4>Full Text</h4>
        <p
          style={{
            lineHeight: '1.6',
            padding: SPACING.md,
            background: COLORS.neutral,
            borderRadius: '4px',
          }}
        >
          {transcription.full_text}
        </p>
      </div>

      {/* Segments Timeline */}
      <div>
        <h4>Segments (Time-Aligned)</h4>
        {transcription.segments?.map((segment, idx) => (
          <div
            key={idx}
            style={{
              padding: SPACING.md,
              marginBottom: SPACING.sm,
              background: COLORS.neutral,
              borderRadius: '4px',
              borderLeft: `4px solid ${COLORS.primary}`,
            }}
          >
            <div style={{ fontSize: '12px', color: COLORS.dark, marginBottom: SPACING.xs }}>
              ⏱️ {segment.start?.toFixed(1)}s - {segment.end?.toFixed(1)}s
              {segment.confidence && (
                <span style={{ marginLeft: SPACING.md, color: COLORS.success }}>
                  ✓ {(segment.confidence * 100).toFixed(0)}% confidence
                </span>
              )}
            </div>
            <div>{segment.text}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ======================== MAIN APP COMPONENT ========================

export const VideoBatchProcessor = () => {
  const [currentBatch, setCurrentBatch] = useState(null);
  const [viewingTranscription, setViewingTranscription] = useState(null);
  const [batches, setBatches] = useState([]);

  const handleUpload = async (uploadData) => {
    const formData = new FormData();
    for (let file of uploadData.files) {
      formData.append('files', file);
    }
    formData.append('case_id', uploadData.caseId);
    formData.append('quality', uploadData.quality);
    formData.append('transcription', uploadData.transcription);
    formData.append('sync_bwc', uploadData.syncBwc);

    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/upload/batch`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('jwt_token')}`,
          },
          body: formData,
        }
      );

      const data = await response.json();
      setCurrentBatch(data.batch_id);
      setBatches([...batches, data]);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  return (
    <div style={{ background: COLORS.neutral, minHeight: '100vh', padding: SPACING.lg }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: SPACING.xl }}>
          <h1 style={{ color: COLORS.primary, margin: 0, fontSize: '32px' }}>
            🎥 Video Batch Processing
          </h1>
          <p style={{ color: COLORS.dark, marginTop: SPACING.sm }}>
            Upload, transcribe, and synchronize multiple videos in parallel
          </p>
        </div>

        {/* Main Content */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: SPACING.lg }}>
          {/* Upload Form */}
          <div>
            <BatchUploadForm onSubmit={handleUpload} />
          </div>

          {/* Current Progress */}
          {currentBatch && (
            <div>
              <BatchProgressMonitor batchId={currentBatch} onClose={() => setCurrentBatch(null)} />
            </div>
          )}
        </div>

        {/* Transcription Viewer */}
        {viewingTranscription && (
          <div style={{ marginTop: SPACING.xl }}>
            <TranscriptionViewer
              fileId={viewingTranscription}
              onClose={() => setViewingTranscription(null)}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoBatchProcessor;
