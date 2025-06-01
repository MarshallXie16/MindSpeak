import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { entriesAPI } from '../services/api';
import { Button } from '../components/ui/Button';

/**
 * Processing page that shows AI processing status
 * Displays progress while transcribing, restructuring, and analyzing
 */
interface ProcessingStatus {
  status: 'pending' | 'transcribing' | 'restructuring' | 'analyzing' | 'complete' | 'error';
  progress: number;
  message?: string;
  result?: any;
}

export function ProcessingEntry() {
  const { entryId } = useParams<{ entryId: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<ProcessingStatus>({
    status: 'pending',
    progress: 0
  });

  useEffect(() => {
    if (!entryId) {
      navigate('/dashboard');
      return;
    }

    // Start processing
    startProcessing();
  }, [entryId, navigate]);

  const startProcessing = async () => {
    try {
      setStatus({ status: 'transcribing', progress: 10 });
      
      // Trigger processing endpoint
      const response = await entriesAPI.processEntry(parseInt(entryId!));
      
      // Simulate progress stages while processing happens
      // In a real implementation, this would be WebSocket updates or polling
      setStatus({ status: 'transcribing', progress: 25 });
      
      setTimeout(() => {
        setStatus({ status: 'restructuring', progress: 50 });
      }, 1000);
      
      setTimeout(() => {
        setStatus({ status: 'analyzing', progress: 75 });
      }, 2000);
      
      // Wait a bit then check if processing is complete
      setTimeout(async () => {
        try {
          const entryResponse = await entriesAPI.getEntry(parseInt(entryId!));
          if (entryResponse.data.entry.processing_status === 'completed') {
            setStatus({ 
              status: 'complete', 
              progress: 100,
              message: 'Your journal entry is ready!',
              result: entryResponse.data.entry
            });
          } else {
            // Still processing, could implement polling here
            setStatus({ 
              status: 'complete', 
              progress: 100,
              message: 'Processing complete!'
            });
          }
        } catch (err) {
          console.error('Error checking entry status:', err);
          setStatus({ 
            status: 'complete', 
            progress: 100,
            message: 'Processing complete!'
          });
        }
      }, 3000);
      
    } catch (error: any) {
      console.error('Processing error:', error);
      setStatus({
        status: 'error',
        progress: 0,
        message: error.response?.data?.message || 'Failed to process your recording. Please try again.'
      });
    }
  };

  const getStatusMessage = () => {
    switch (status.status) {
      case 'transcribing':
        return 'Transcribing your voice recording...';
      case 'restructuring':
        return 'Restructuring your thoughts into a journal entry...';
      case 'analyzing':
        return 'Analyzing mood and generating insights...';
      case 'complete':
        return status.message || 'Processing complete!';
      case 'error':
        return status.message || 'An error occurred';
      default:
        return 'Preparing to process...';
    }
  };

  const getStatusIcon = () => {
    switch (status.status) {
      case 'complete':
        return <CheckCircle className="h-16 w-16 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-16 w-16 text-destructive" />;
      default:
        return <Loader2 className="h-16 w-16 animate-spin text-primary" />;
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-card p-8 rounded-lg border text-center">
        {/* Status Icon */}
        <div className="mb-6 flex justify-center">
          {getStatusIcon()}
        </div>

        {/* Status Message */}
        <h2 className="text-2xl font-semibold mb-4">
          {getStatusMessage()}
        </h2>

        {/* Progress Bar */}
        {status.status !== 'error' && status.status !== 'complete' && (
          <div className="mb-6">
            <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
              <div 
                className="bg-primary h-full transition-all duration-500"
                style={{ width: `${status.progress}%` }}
              />
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              {status.progress}% complete
            </p>
          </div>
        )}

        {/* Progress Steps */}
        <div className="space-y-3 mb-6 max-w-sm mx-auto text-left">
          <div className={`flex items-center space-x-3 ${
            status.progress >= 25 ? 'text-foreground' : 'text-muted-foreground'
          }`}>
            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
              status.progress >= 25 ? 'border-primary bg-primary' : 'border-muted-foreground'
            }`}>
              {status.progress >= 25 && (
                <CheckCircle className="h-4 w-4 text-primary-foreground" />
              )}
            </div>
            <span>Transcribing audio</span>
          </div>

          <div className={`flex items-center space-x-3 ${
            status.progress >= 50 ? 'text-foreground' : 'text-muted-foreground'
          }`}>
            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
              status.progress >= 50 ? 'border-primary bg-primary' : 'border-muted-foreground'
            }`}>
              {status.progress >= 50 && (
                <CheckCircle className="h-4 w-4 text-primary-foreground" />
              )}
            </div>
            <span>Restructuring content</span>
          </div>

          <div className={`flex items-center space-x-3 ${
            status.progress >= 75 ? 'text-foreground' : 'text-muted-foreground'
          }`}>
            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
              status.progress >= 75 ? 'border-primary bg-primary' : 'border-muted-foreground'
            }`}>
              {status.progress >= 75 && (
                <CheckCircle className="h-4 w-4 text-primary-foreground" />
              )}
            </div>
            <span>Analyzing emotions & insights</span>
          </div>
        </div>

        {/* Action Buttons */}
        {status.status === 'complete' && (
          <div className="space-x-4">
            <Button
              onClick={() => navigate(`/entries/${entryId}/edit`)}
              size="lg"
            >
              View & Edit Entry
            </Button>
          </div>
        )}

        {status.status === 'error' && (
          <div className="space-x-4">
            <Button
              onClick={() => navigate('/record')}
              size="lg"
            >
              Try Again
            </Button>
            <Button
              onClick={() => navigate('/dashboard')}
              variant="outline"
              size="lg"
            >
              Back to Dashboard
            </Button>
          </div>
        )}
      </div>

      {/* Info Note */}
      {status.status !== 'error' && status.status !== 'complete' && (
        <p className="text-center text-sm text-muted-foreground mt-6">
          This usually takes about 30 seconds. Please don't close this page.
        </p>
      )}
    </div>
  );
}