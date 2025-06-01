import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Edit } from 'lucide-react';

interface EntryCardProps {
  id: number;
  title: string;
  createdAt: string;
  moodScore?: number;
  moodEmoji?: string;
  onClick?: () => void;
  className?: string;
  compact?: boolean;
}

export function EntryCard({ 
  id, 
  title, 
  createdAt, 
  moodScore, 
  moodEmoji,
  onClick,
  className = '',
  compact = false
}: EntryCardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      navigate(`/entries/${id}/edit`);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      ...(compact ? {} : { year: 'numeric' })
    });
  };

  const getMoodEmoji = (score?: number) => {
    if (moodEmoji) return moodEmoji;
    if (!score || typeof score !== 'number') return '😐';
    if (score >= 9) return '😄';
    if (score >= 8) return '😊';
    if (score >= 7) return '🙂';
    if (score >= 6) return '😌';
    if (score >= 5) return '😐';
    if (score >= 4) return '😕';
    if (score >= 3) return '😔';
    if (score >= 2) return '😢';
    return '😞';
  };

  if (compact) {
    return (
      <div
        className={`flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors cursor-pointer ${className}`}
        onClick={handleClick}
      >
        <div className="flex items-center space-x-3">
          <span className="text-lg">{getMoodEmoji(moodScore)}</span>
          <div>
            <h3 className="font-medium text-sm">{title}</h3>
            <p className="text-xs text-muted-foreground">
              {formatDate(createdAt)}
            </p>
          </div>
        </div>
        <Edit className="h-4 w-4 text-muted-foreground" />
      </div>
    );
  }

  return (
    <div
      className={`bg-card border rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer ${className}`}
      onClick={handleClick}
    >
      <div className="flex items-start justify-between">
        <h3 className="font-semibold text-lg mb-2">{title}</h3>
        <span className="text-2xl">{getMoodEmoji(moodScore)}</span>
      </div>
      <p className="text-sm text-muted-foreground">
        {formatDate(createdAt)}
      </p>
    </div>
  );
}