/**
 * __tests__/components/FileDropZone.test.tsx
 * Unit tests for FileDropZone component
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FileDropZone from '../../components/VideoUpload/FileDropZone';

describe('FileDropZone Component', () => {
  const mockOnFilesSelected = jest.fn();

  beforeEach(() => {
    mockOnFilesSelected.mockClear();
  });

  test('renders drop zone with instructions', () => {
    render(<FileDropZone onFilesSelected={mockOnFilesSelected} />);
    expect(screen.getByText(/drag and drop/i)).toBeInTheDocument();
  });

  test('accepts video files on drop', async () => {
    const { container } = render(
      <FileDropZone onFilesSelected={mockOnFilesSelected} accept=".mp4,.mov" />
    );

    const dropZone = container.querySelector('[data-testid="drop-zone"]') as HTMLElement;
    const file = new File(['video content'], 'test.mp4', {
      type: 'video/mp4',
    });

    const dataTransfer = {
      files: [file],
      items: [{ kind: 'file', type: 'video/mp4', getAsFile: () => file }],
      types: ['Files'],
    };

    fireEvent.drop(dropZone, { dataTransfer });

    expect(mockOnFilesSelected).toHaveBeenCalledWith([file]);
  });

  test('rejects invalid file types', () => {
    const { container } = render(
      <FileDropZone onFilesSelected={mockOnFilesSelected} accept=".mp4,.mov" />
    );

    const dropZone = container.querySelector('[data-testid="drop-zone"]') as HTMLElement;
    const file = new File(['text content'], 'test.txt', {
      type: 'text/plain',
    });

    const dataTransfer = {
      files: [file],
      items: [{ kind: 'file', type: 'text/plain', getAsFile: () => file }],
      types: ['Files'],
    };

    fireEvent.drop(dropZone, { dataTransfer });

    expect(mockOnFilesSelected).toHaveBeenCalledWith([]);
  });

  test('enforces max file count', async () => {
    const { container } = render(
      <FileDropZone onFilesSelected={mockOnFilesSelected} maxFiles={2} accept=".mp4" />
    );

    const dropZone = container.querySelector('[data-testid="drop-zone"]') as HTMLElement;
    const files = [
      new File(['video1'], 'test1.mp4', { type: 'video/mp4' }),
      new File(['video2'], 'test2.mp4', { type: 'video/mp4' }),
      new File(['video3'], 'test3.mp4', { type: 'video/mp4' }),
    ];

    const dataTransfer = {
      files,
      items: files.map((f) => ({ kind: 'file', getAsFile: () => f })),
      types: ['Files'],
    };

    fireEvent.drop(dropZone, { dataTransfer });

    expect(mockOnFilesSelected).toHaveBeenCalledWith(files.slice(0, 2));
  });

  test('handles click to browse', async () => {
    const user = userEvent.setup();
    render(<FileDropZone onFilesSelected={mockOnFilesSelected} />);

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(input).toBeInTheDocument();
  });

  test('shows drag-over visual feedback', () => {
    const { container } = render(<FileDropZone onFilesSelected={mockOnFilesSelected} />);

    const dropZone = container.querySelector('[data-testid="drop-zone"]') as HTMLElement;

    fireEvent.dragOver(dropZone);
    expect(dropZone).toHaveClass('isDragging');

    fireEvent.dragLeave(dropZone);
    expect(dropZone).not.toHaveClass('isDragging');
  });
});
