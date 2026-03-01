import { describe, it, expect } from 'vitest';
import { sanitizeFilename } from '@/lib/uploadManager';

describe('sanitizeFilename', () => {
  it('strips path segments', () => {
    expect(sanitizeFilename('C:\\Users\\admin\\evidence.zip')).toBe('evidence.zip');
    expect(sanitizeFilename('/home/user/photos/image.jpg')).toBe('image.jpg');
  });

  it('removes null bytes', () => {
    expect(sanitizeFilename('file\x00name.pdf')).toBe('filename.pdf');
  });

  it('replaces path traversal', () => {
    expect(sanitizeFilename('../../etc/passwd')).toBe('passwd');
    expect(sanitizeFilename('..\\..\\secret.txt')).toBe('secret.txt');
  });

  it('handles double dots in filename (traversal)', () => {
    const result = sanitizeFilename('file..name.txt');
    expect(result).not.toContain('..');
  });

  it('returns unnamed for empty input', () => {
    expect(sanitizeFilename('')).toBe('unnamed');
  });

  it('returns unnamed for whitespace-only', () => {
    expect(sanitizeFilename('   ')).toBe('unnamed');
  });

  it('preserves valid filenames', () => {
    expect(sanitizeFilename('evidence-2026-01.mp4')).toBe('evidence-2026-01.mp4');
    expect(sanitizeFilename('photo (1).jpg')).toBe('photo (1).jpg');
  });
});
