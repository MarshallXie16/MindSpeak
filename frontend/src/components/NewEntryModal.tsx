import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Modal } from './ui/Modal';
import { Mic, PenTool } from 'lucide-react';

/**
 * Modal for selecting new entry type
 * Allows user to choose between voice recording or written entry
 */
interface NewEntryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function NewEntryModal({ isOpen, onClose }: NewEntryModalProps) {
  const navigate = useNavigate();

  const handleVoiceEntry = () => {
    onClose();
    navigate('/record');
  };

  const handleWrittenEntry = () => {
    onClose();
    // TODO: Navigate to written entry page
    navigate('/write');
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create New Entry"
      className="max-w-sm"
    >
      <div className="space-y-4">
        <p className="text-muted-foreground text-center">
          How would you like to create your journal entry?
        </p>
        
        <div className="grid gap-3">
          {/* Voice Recording Option */}
          <button
            onClick={handleVoiceEntry}
            className="group p-6 rounded-lg border-2 border-border hover:border-primary transition-all duration-200 text-left"
          >
            <div className="flex items-center space-x-4">
              <div className="p-3 rounded-full bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                <Mic className="h-6 w-6" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-1">Voice Recording</h3>
                <p className="text-sm text-muted-foreground">
                  Speak your thoughts naturally, up to 2 minutes
                </p>
              </div>
            </div>
          </button>

          {/* Written Entry Option */}
          <button
            onClick={handleWrittenEntry}
            className="group p-6 rounded-lg border-2 border-border hover:border-primary transition-all duration-200 text-left"
          >
            <div className="flex items-center space-x-4">
              <div className="p-3 rounded-full bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                <PenTool className="h-6 w-6" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-1">Written Entry</h3>
                <p className="text-sm text-muted-foreground">
                  Type your thoughts at your own pace
                </p>
              </div>
            </div>
          </button>
        </div>
      </div>
    </Modal>
  );
}