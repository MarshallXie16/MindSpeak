import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { AudioVisualizer } from '../components/AudioVisualizer';
import { AudioRecorder } from '../utils/audioRecorder';
import { entriesAPI } from '../services/api';
import { Mic, Square, AlertCircle, Loader2 } from 'lucide-react';

/**
 * Recording page component
 * Handles voice recording with 2-minute limit and audio visualization
 */
type RecordingStatus = 'idle' | 'recording' | 'uploading' | 'processing' | 'error' | 'success';

export function Recording() {
  const navigate = useNavigate();
  const [status, setStatus] = useState<RecordingStatus>('idle');
  const [duration, setDuration] = useState(0);
  const [error, setError] = useState<string>('');
  const [stream, setStream] = useState<MediaStream | null>(null);
  
  const recorderRef = useRef<AudioRecorder | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  const MAX_DURATION = 120; // 2 minutes in seconds

  useEffect(() => {
    // Initialize recorder
    recorderRef.current = new AudioRecorder(MAX_DURATION);
    
    return () => {
      // Cleanup on unmount
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (recorderRef.current?.isRecording()) {
        recorderRef.current.stopRecording();
      }
    };
  }, []);

  /**
   * Start recording audio
   */
  const startRecording = async () => {
    try {
      setError('');
      setStatus('recording');
      
      await recorderRef.current!.startRecording();
      setStream(recorderRef.current!.getStream());
      
      // Start duration timer
      timerRef.current = setInterval(() => {
        const currentDuration = recorderRef.current!.getCurrentDuration();
        setDuration(Math.floor(currentDuration));
        
        // Auto-stop at max duration
        if (currentDuration >= MAX_DURATION) {
          stopRecording();
        }
      }, 100);
    } catch (err) {
      setError('Failed to access microphone. Please check your permissions.');
      setStatus('error');
    }
  };

  /**
   * Stop recording and upload audio
   */
  const stopRecording = async () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    try {
      setStatus('uploading');
      const { audioBlob, duration } = await recorderRef.current!.stopRecording();
      setStream(null);
      
      // Minimum duration check
      if (duration < 5) {
        setError('Recording too short. Please record at least 5 seconds.');
        setStatus('error');
        return;
      }

      // Upload audio file
      const formData = new FormData();
      formData.append('audio', audioBlob, `recording-${Date.now()}.webm`);
      formData.append('duration', duration.toString());

      const response = await entriesAPI.uploadAudio(formData);
      
      // Navigate to processing page with entry ID
      navigate(`/entries/${response.data.entry_id}/process`);
    } catch (err) {
      setError('Failed to upload recording. Please try again.');
      setStatus('error');
    }
  };

  /**
   * Cancel recording
   */
  const cancelRecording = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
    if (recorderRef.current?.isRecording()) {
      recorderRef.current.stopRecording();
    }
    navigate('/dashboard');
  };

  /**
   * Format duration as MM:SS
   */
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Record Your Thoughts</h1>
        <p className="text-muted-foreground">
          Speak naturally about your day. You have up to 2 minutes.
        </p>
      </div>

      {/* Recording Interface */}
      <div className="bg-card p-8 rounded-lg border">
        {/* Audio Visualizer */}
        <div className="mb-8">
          <AudioVisualizer 
            stream={stream} 
            isRecording={status === 'recording'} 
          />
        </div>

        {/* Duration Display */}
        <div className="text-center mb-8">
          <div className="text-4xl font-mono font-bold">
            {formatDuration(duration)} / {formatDuration(MAX_DURATION)}
          </div>
          {status === 'recording' && (
            <p className="text-sm text-muted-foreground mt-2">
              Recording in progress...
            </p>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-destructive/10 text-destructive rounded-lg flex items-center space-x-2">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Control Buttons */}
        <div className="flex justify-center space-x-4">
          {status === 'idle' && (
            <>
              <Button
                size="lg"
                onClick={startRecording}
                className="flex items-center space-x-2"
              >
                <Mic className="h-5 w-5" />
                <span>Start Recording</span>
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={cancelRecording}
              >
                Cancel
              </Button>
            </>
          )}

          {status === 'recording' && (
            <Button
              size="lg"
              onClick={stopRecording}
              variant="destructive"
              className="flex items-center space-x-2"
            >
              <Square className="h-5 w-5" />
              <span>Stop Recording</span>
            </Button>
          )}

          {status === 'uploading' && (
            <Button size="lg" disabled>
              <Loader2 className="h-5 w-5 animate-spin mr-2" />
              Uploading...
            </Button>
          )}

          {status === 'error' && (
            <>
              <Button
                size="lg"
                onClick={() => {
                  setStatus('idle');
                  setDuration(0);
                  setError('');
                }}
              >
                Try Again
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={cancelRecording}
              >
                Cancel
              </Button>
            </>
          )}
        </div>

        {/* Tips */}
        {status === 'idle' && (
          <div className="mt-8 p-4 bg-muted/50 rounded-lg">
            <h3 className="font-semibold mb-2">Tips for a great entry:</h3>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Find a quiet place to record</li>
              <li>• Speak naturally, as if talking to a friend</li>
              <li>• Don't worry about perfect grammar</li>
              <li>• Share what's on your mind - feelings, events, thoughts</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}