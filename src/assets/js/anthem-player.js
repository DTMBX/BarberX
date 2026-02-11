/**
 * ============================================================================
 * National Anthem Audio Player — Evident Technologies
 * ============================================================================
 * 
 * Respectful playback of The Star-Spangled Banner on homepage landing.
 * 
 * Features:
 * - Gentle 3-second fade-in (not startling)
 * - Graceful fade-out when song ends
 * - Remembers user's mute preference
 * - Graceful degradation if audio unavailable
 * - Respects browser autoplay policies
 * 
 * Version: 1.0.0
 * Last updated: 2026-02-11
 */
(function () {
  'use strict';

  // Configuration
  const CONFIG = {
    fadeInDuration: 3000,     // 3 seconds fade-in
    fadeOutDuration: 2000,    // 2 seconds fade-out
    initialVolume: 0.4,       // 40% volume (respectful level)
    maxVolume: 0.5,           // Maximum 50% volume
    fadeSteps: 50,            // Smoothness of fade
    autoplayDelay: 1500,      // Wait 1.5s after page load
    storageKey: 'evident_anthem_muted'
  };

  // DOM elements
  let player, audio, toggleBtn, muteBtn, replayBtn, status;

  /**
   * Initialize the anthem player
   */
  function init() {
    console.log('[Anthem] Initializing player...');
    
    player = document.getElementById('anthem-player');
    audio = document.getElementById('anthem-audio');
    toggleBtn = document.getElementById('anthem-toggle');
    muteBtn = document.getElementById('anthem-mute');
    replayBtn = document.getElementById('anthem-replay');
    status = document.getElementById('anthem-status');

    if (!player || !audio) {
      console.error('[Anthem] Player elements not found', {
        player: !!player,
        audio: !!audio
      });
      return;
    }

    console.log('[Anthem] Player elements found, setting up listeners...');

    // Check if audio source is available
    audio.addEventListener('error', handleAudioError);
    audio.addEventListener('canplaythrough', handleAudioReady);
    audio.addEventListener('ended', handleAudioEnded);
    audio.addEventListener('play', handleAudioPlay);
    audio.addEventListener('pause', handleAudioPause);

    // Button event listeners
    if (toggleBtn) {
      toggleBtn.addEventListener('click', togglePlayPause);
      console.log('[Anthem] Toggle button listener attached');
    }
    if (muteBtn) {
      muteBtn.addEventListener('click', toggleMute);
    }
    if (replayBtn) {
      replayBtn.addEventListener('click', replayAnthem);
    }

    // Restore mute preference
    restoreMutePreference();

    // Load the audio
    console.log('[Anthem] Loading audio...');
    audio.load();
  }

  /**
   * Handle audio ready to play
   */
  function handleAudioReady() {
    console.log('[Anthem] Audio ready');
    player.classList.add('is-ready');
    
    // Attempt autoplay after delay
    setTimeout(function () {
      attemptAutoplay();
    }, CONFIG.autoplayDelay);
  }

  /**
   * Handle audio load error
   */
  function handleAudioError(e) {
    console.log('[Anthem] Audio unavailable:', e);
    player.classList.add('is-unavailable');
  }

  /**
   * Attempt autoplay with fade-in
   * Respects browser autoplay policies
   */
  function attemptAutoplay() {
    // Check if user has previously muted
    if (localStorage.getItem(CONFIG.storageKey) === 'true') {
      console.log('[Anthem] User previously muted, not autoplaying');
      player.classList.add('is-paused');
      return;
    }

    // Check for reduced motion preference
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      console.log('[Anthem] Reduced motion preference, not autoplaying');
      player.classList.add('is-paused');
      return;
    }

    // Start muted with volume at 0 to satisfy browser autoplay policies
    audio.muted = true;
    audio.volume = 0;
    
    // Attempt to play
    const playPromise = audio.play();

    if (playPromise !== undefined) {
      playPromise
        .then(function () {
          console.log('[Anthem] Autoplay started, unmuting and fading in...');
          player.classList.add('is-fading-in');
          // Unmute immediately, then fade in from 0
          audio.muted = false;
          fadeIn();
        })
        .catch(function (error) {
          console.log('[Anthem] Autoplay blocked:', error.message);
          player.classList.add('is-paused');
          // Show play button for manual start
        });
    }
  }

  /**
   * Fade audio volume in
   */
  function fadeIn() {
    const targetVolume = CONFIG.initialVolume;
    const stepTime = CONFIG.fadeInDuration / CONFIG.fadeSteps;
    const volumeStep = targetVolume / CONFIG.fadeSteps;
    let currentStep = 0;

    const fadeInterval = setInterval(function () {
      currentStep++;
      const newVolume = Math.min(volumeStep * currentStep, targetVolume);
      audio.volume = newVolume;

      if (currentStep >= CONFIG.fadeSteps) {
        clearInterval(fadeInterval);
        audio.volume = targetVolume;
        player.classList.remove('is-fading-in');
        console.log('[Anthem] Fade-in complete');
      }
    }, stepTime);
  }

  /**
   * Fade audio volume out
   */
  function fadeOut(callback) {
    const startVolume = audio.volume;
    const stepTime = CONFIG.fadeOutDuration / CONFIG.fadeSteps;
    const volumeStep = startVolume / CONFIG.fadeSteps;
    let currentStep = 0;

    player.classList.add('is-fading-out');

    const fadeInterval = setInterval(function () {
      currentStep++;
      const newVolume = Math.max(startVolume - (volumeStep * currentStep), 0);
      audio.volume = newVolume;

      if (currentStep >= CONFIG.fadeSteps) {
        clearInterval(fadeInterval);
        audio.volume = 0;
        player.classList.remove('is-fading-out');
        if (callback) callback();
        console.log('[Anthem] Fade-out complete');
      }
    }, stepTime);
  }

  /**
   * Handle audio ended
   */
  function handleAudioEnded() {
    console.log('[Anthem] Song ended');
    player.classList.remove('is-paused');
    player.classList.add('is-ended');
    updateToggleLabel('Play The Star-Spangled Banner');
  }

  /**
   * Handle audio play
   */
  function handleAudioPlay() {
    player.classList.remove('is-paused');
    player.classList.remove('is-ended');
    updateToggleLabel('Pause National Anthem');
  }

  /**
   * Handle audio pause
   */
  function handleAudioPause() {
    if (!audio.ended) {
      player.classList.add('is-paused');
      updateToggleLabel('Play National Anthem');
    }
  }

  /**
   * Toggle play/pause
   */
  function togglePlayPause() {
    if (audio.paused) {
      // If starting from beginning, fade in
      if (audio.currentTime === 0 || audio.currentTime < 0.5) {
        audio.volume = 0;
        audio.play().then(function () {
          fadeIn();
        }).catch(function (e) {
          console.log('[Anthem] Play failed:', e);
        });
      } else {
        audio.play();
      }
    } else {
      audio.pause();
    }
  }

  /**
   * Toggle mute
   */
  function toggleMute() {
    audio.muted = !audio.muted;
    
    if (audio.muted) {
      player.classList.add('is-muted');
      updateMuteLabel('Unmute');
      localStorage.setItem(CONFIG.storageKey, 'true');
    } else {
      player.classList.remove('is-muted');
      updateMuteLabel('Mute');
      localStorage.setItem(CONFIG.storageKey, 'false');
    }
  }

  /**
   * Replay the anthem
   */
  function replayAnthem() {
    audio.currentTime = 0;
    audio.volume = 0;
    
    audio.play().then(function () {
      player.classList.remove('is-ended');
      fadeIn();
    }).catch(function (e) {
      console.log('[Anthem] Replay failed:', e);
    });
  }

  /**
   * Restore user's mute preference
   */
  function restoreMutePreference() {
    const wasMuted = localStorage.getItem(CONFIG.storageKey) === 'true';
    if (wasMuted) {
      audio.muted = true;
      player.classList.add('is-muted');
      updateMuteLabel('Unmute');
    }
  }

  /**
   * Update toggle button label
   */
  function updateToggleLabel(label) {
    if (toggleBtn) {
      toggleBtn.setAttribute('aria-label', label);
      toggleBtn.setAttribute('title', label);
    }
  }

  /**
   * Update mute button label
   */
  function updateMuteLabel(label) {
    if (muteBtn) {
      muteBtn.setAttribute('aria-label', label);
      muteBtn.setAttribute('title', label);
    }
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
