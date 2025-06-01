import React from 'react';
import { AlertTriangle, X } from 'lucide-react';
import { Modal } from './Modal';
import { Button } from './Button';

interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  confirmVariant?: 'default' | 'destructive';
  isLoading?: boolean;
  type?: 'warning' | 'danger';
}

export function ConfirmationModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  confirmVariant = 'default',
  isLoading = false,
  type = 'warning'
}: ConfirmationModalProps) {
  const handleConfirm = () => {
    onConfirm();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title=""
      className="max-w-md"
    >
      <div className="space-y-4">
        {/* Icon and Title */}
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-full ${
            type === 'danger' ? 'bg-destructive/10' : 'bg-yellow-100'
          }`}>
            <AlertTriangle className={`h-6 w-6 ${
              type === 'danger' ? 'text-destructive' : 'text-yellow-600'
            }`} />
          </div>
          <div>
            <h3 className="text-lg font-semibold">{title}</h3>
          </div>
        </div>

        {/* Message */}
        <p className="text-muted-foreground">{message}</p>

        {/* Actions */}
        <div className="flex justify-end space-x-3 pt-4">
          <Button
            variant="ghost"
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            variant={confirmVariant}
            onClick={handleConfirm}
            disabled={isLoading}
            className="flex items-center space-x-2"
          >
            {isLoading && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
            )}
            <span>{isLoading ? 'Processing...' : confirmText}</span>
          </Button>
        </div>
      </div>
    </Modal>
  );
}