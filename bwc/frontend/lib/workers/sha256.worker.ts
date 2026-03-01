/**
 * SHA-256 Web Worker for off-main-thread hashing.
 *
 * Receives an ArrayBuffer, returns the hex digest.
 * Falls back to crypto.subtle in worker scope.
 */
self.onmessage = async (e: MessageEvent<ArrayBuffer>) => {
  try {
    const digest = await crypto.subtle.digest('SHA-256', e.data);
    const hex = Array.from(new Uint8Array(digest))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');
    self.postMessage({ type: 'result', hash: hex });
  } catch (err) {
    self.postMessage({
      type: 'error',
      message: err instanceof Error ? err.message : 'Hash failed',
    });
  }
};
