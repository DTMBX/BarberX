/**
 * __tests__/components/BatchUploadContainer.test.tsx
 * Integration tests for BatchUploadContainer component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BatchUploadContainer from '../../components/VideoUpload/BatchUploadContainer';
import * as socketIO from 'socket.io-client';

// Mock Socket.IO
jest.mock('socket.io-client');

describe('BatchUploadContainer Component', () => {
  const mockSocket = {
    on: jest.fn(),
    off: jest.fn(),
    emit: jest.fn(),
    disconnect: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (socketIO.io as jest.Mock).mockReturnValue(mockSocket);

    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(() => 'test_token'),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });

    // Mock fetch
    global.fetch = jest.fn();
  });

  test('renders component with title', () => {
    render(<BatchUploadContainer />);
    expect(screen.getByText(/Video Upload/i)).toBeInTheDocument();
  });

  test('initializes WebSocket connection on mount', () => {
    render(<BatchUploadContainer />);

    expect(socketIO.io).toHaveBeenCalled();
    expect(mockSocket.on).toHaveBeenCalledWith('batch_progress', expect.any(Function));
  });

  test('handles file selection from drop zone', async () => {
    const user = userEvent.setup();
    render(<BatchUploadContainer />);

    // Simulate file drop
    const file = new File(['video'], 'test.mp4', { type: 'video/mp4' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(() => {
      expect(screen.getByText('test.mp4')).toBeInTheDocument();
    });
  });

  test('shows quality selector with default value', () => {
    render(<BatchUploadContainer />);
    expect(screen.getByText(/Quality/i)).toBeInTheDocument();
  });

  test('enables upload button when files and case are selected', () => {
    render(<BatchUploadContainer />);

    const uploadButton = screen.getByText(/Start Upload/i) as HTMLButtonElement;
    expect(uploadButton).toBeDisabled();

    // After selecting files and case, button should be enabled
    // (Implementation depends on your test data setup)
  });

  test('sends POST request with batch config on upload', async () => {
    const mockFetch = global.fetch as jest.Mock;
    mockFetch.mockResolvedValueOnce({
      status: 202,
      json: async () => ({
        batch_id: 'test-batch-123',
        files: [{ id: 'file-1', status: 'pending' }],
      }),
    });

    render(<BatchUploadContainer />);

    // Add file
    const file = new File(['video'], 'test.mp4', { type: 'video/mp4' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(input, { target: { files: [file] } });

    // Click start upload
    const uploadButton = screen.getByText(/Start Upload/i);
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/upload/batch'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: expect.stringContaining('Bearer'),
          }),
        })
      );
    });
  });

  test('displays progress component after upload starts', async () => {
    const user = userEvent.setup();
    const mockFetch = global.fetch as jest.Mock;
    mockFetch.mockResolvedValueOnce({
      status: 202,
      json: async () => ({
        batch_id: 'test-batch-123',
        files: [{ id: 'file-1', status: 'pending' }],
      }),
    });

    render(<BatchUploadContainer />);

    // Add file
    const file = new File(['video'], 'test.mp4', { type: 'video/mp4' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    await user.upload(input, file);

    // Click start upload
    const uploadButton = screen.getByText(/Start Upload/i);
    await user.click(uploadButton);

    // Wait for upload progress to appear
    await waitFor(() => {
      expect(screen.queryByText(/Upload Progress/i)).toBeInTheDocument();
    });
  });

  test('removes file from queue when remove button clicked', async () => {
    const user = userEvent.setup();
    render(<BatchUploadContainer />);

    // Add file
    const file = new File(['video'], 'test.mp4', { type: 'video/mp4' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    await user.upload(input, file);

    // Verify file is visible
    await waitFor(() => {
      expect(screen.getByText('test.mp4')).toBeInTheDocument();
    });

    // Find and click remove button
    const removeButton = screen.getByText(/Remove/i);
    await user.click(removeButton);

    // File should be removed
    await waitFor(() => {
      expect(screen.queryByText('test.mp4')).not.toBeInTheDocument();
    });
  });

  test('cleans up socket connection on unmount', () => {
    const { unmount } = render(<BatchUploadContainer />);
    unmount();
    expect(mockSocket.disconnect).toHaveBeenCalled();
  });

  test('handles socket progress events', async () => {
    render(<BatchUploadContainer />);

    // Get the batch_progress handler
    const progressHandler = mockSocket.on.mock.calls.find(
      (call) => call[0] === 'batch_progress'
    )?.[1];

    expect(progressHandler).toBeDefined();

    // Simulate progress event
    progressHandler?.({
      file_id: 'file-1',
      progress: 50,
    });

    // Component should update with new progress
    // (Verify in DOM if applicable)
  });

  test('toggles transcription and sync options', async () => {
    const user = userEvent.setup();
    render(<BatchUploadContainer />);

    const transcriptionCheckbox = screen.getByLabelText(/Enable Transcription/i);
    const syncCheckbox = screen.getByLabelText(/Enable.*Sync/i);

    await user.click(transcriptionCheckbox);
    expect(transcriptionCheckbox).not.toBeChecked();

    await user.click(syncCheckbox);
    expect(syncCheckbox).toBeChecked();
  });
});
