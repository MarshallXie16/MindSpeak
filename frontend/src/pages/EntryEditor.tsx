import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, Save, ArrowLeft, RefreshCw, Trash2 } from 'lucide-react';
import { entriesAPI } from '../services/api';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { ConfirmationModal } from '../components/ui/ConfirmationModal';

interface JournalEntry {
  id: number;
  title: string;
  raw_transcript: string;
  formatted_content: string;
  mood_score: number;
  emotions: string; // JSON string
  insights: string; // JSON string
  created_at: string;
  updated_at: string;
  processing_status: string;
}

interface ParsedEntry extends Omit<JournalEntry, 'emotions' | 'insights'> {
  emotions: Array<{ name: string; confidence: number }>;
  insights: string[];
}

export function EntryEditor() {
  const { entryId } = useParams<{ entryId: string }>();
  const navigate = useNavigate();
  const [entry, setEntry] = useState<ParsedEntry | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isEdited, setIsEdited] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteConfirmation, setDeleteConfirmation] = useState({
    isOpen: false,
    isDeleting: false
  });

  useEffect(() => {
    if (!entryId) {
      navigate('/dashboard');
      return;
    }
    
    loadEntry();
  }, [entryId, navigate]);

  const loadEntry = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await entriesAPI.getEntry(parseInt(entryId!));
      const rawEntry = response.data.entry;
      
      // Parse JSON strings
      const parsedEntry: ParsedEntry = {
        ...rawEntry,
        emotions: typeof rawEntry.emotions === 'string' 
          ? JSON.parse(rawEntry.emotions || '[]')
          : rawEntry.emotions || [],
        insights: typeof rawEntry.insights === 'string'
          ? JSON.parse(rawEntry.insights || '[]')
          : rawEntry.insights || []
      };
      
      setEntry(parsedEntry);
    } catch (err: any) {
      console.error('Error loading entry:', err);
      setError(err.response?.data?.message || 'Failed to load entry');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!entry || !isEdited) return;
    
    try {
      setIsSaving(true);
      
      const updateData = {
        title: entry.title,
        formatted_content: entry.formatted_content,
        mood_score: entry.mood_score,
        emotions: JSON.stringify(entry.emotions),
        insights: JSON.stringify(entry.insights)
      };
      
      await entriesAPI.updateEntry(entry.id, updateData);
      setIsEdited(false);
      
      // Show success feedback (could add toast notification)
      console.log('Entry saved successfully');
      
    } catch (err: any) {
      console.error('Error saving entry:', err);
      setError(err.response?.data?.message || 'Failed to save entry');
    } finally {
      setIsSaving(false);
    }
  };

  const handleFieldChange = (field: keyof ParsedEntry, value: any) => {
    if (!entry) return;
    
    setEntry({ ...entry, [field]: value });
    setIsEdited(true);
  };

  const handleDeleteEntry = () => {
    setDeleteConfirmation({ isOpen: true, isDeleting: false });
  };

  const confirmDeleteEntry = async () => {
    if (!entry) return;

    setDeleteConfirmation(prev => ({ ...prev, isDeleting: true }));

    try {
      await entriesAPI.deleteEntry(entry.id);
      navigate('/entries');
    } catch (err: any) {
      console.error('Error deleting entry:', err);
      setError(err.response?.data?.message || 'Failed to delete entry');
      setDeleteConfirmation(prev => ({ ...prev, isDeleting: false }));
    }
  };

  const closeDeleteConfirmation = () => {
    if (!deleteConfirmation.isDeleting) {
      setDeleteConfirmation({ isOpen: false, isDeleting: false });
    }
  };

  const renderMoodSelector = () => {
    if (!entry) return null;
    
    return (
      <div className="space-y-2">
        <label className="text-sm font-medium">Mood Score</label>
        <div className="flex items-center space-x-4">
          <input
            type="range"
            min="1"
            max="10"
            value={entry.mood_score || 5}
            onChange={(e) => handleFieldChange('mood_score', parseInt(e.target.value))}
            className="flex-1"
          />
          <span className="text-lg font-semibold w-8 text-center">
            {entry.mood_score || 5}
          </span>
        </div>
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>1 - Very Negative</span>
          <span>10 - Very Positive</span>
        </div>
      </div>
    );
  };

  const renderEmotions = () => {
    if (!entry || !entry.emotions?.length) return null;
    
    return (
      <div className="space-y-2">
        <label className="text-sm font-medium">Emotions Detected</label>
        <div className="flex flex-wrap gap-2">
          {entry.emotions.map((emotion, index) => (
            <div
              key={index}
              className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-secondary"
            >
              <span className="font-medium">{emotion.name}</span>
              <span className="ml-2 text-muted-foreground">
                {Math.round(emotion.confidence * 100)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderInsights = () => {
    if (!entry || !entry.insights?.length) return null;
    
    return (
      <div className="space-y-2">
        <label className="text-sm font-medium">AI Insights</label>
        <div className="space-y-3">
          {entry.insights.map((insight, index) => (
            <div
              key={index}
              className="p-3 bg-secondary/50 rounded-lg border-l-4 border-primary"
            >
              <p className="text-sm">{insight}</p>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading entry...</span>
        </div>
      </div>
    );
  }

  if (error || !entry) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-card p-8 rounded-lg border text-center">
          <p className="text-destructive mb-4">{error || 'Entry not found'}</p>
          <Button onClick={() => navigate('/dashboard')} variant="outline">
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button
            onClick={() => navigate('/dashboard')}
            variant="ghost"
            size="sm"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Edit Entry</h1>
            <p className="text-muted-foreground">
              Created {new Date(entry.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            onClick={handleDeleteEntry}
            variant="outline"
            size="sm"
            className="text-destructive hover:bg-destructive hover:text-destructive-foreground"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </Button>
          <Button
            onClick={handleSave}
            disabled={!isEdited || isSaving}
            size="sm"
          >
            {isSaving ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Save Changes
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Entry Content - Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Title */}
          <div className="space-y-2">
            <label htmlFor="title" className="text-sm font-medium">Title</label>
            <Input
              id="title"
              value={entry.title}
              onChange={(e) => handleFieldChange('title', e.target.value)}
              placeholder="Entry title"
            />
          </div>

          {/* Content */}
          <div className="space-y-2">
            <label htmlFor="content" className="text-sm font-medium">Content</label>
            <Textarea
              id="content"
              value={entry.formatted_content || ''}
              onChange={(e) => handleFieldChange('formatted_content', e.target.value)}
              placeholder="Write your journal entry here..."
              rows={12}
              className="resize-none"
            />
          </div>

          {/* Original Transcript */}
          {entry.raw_transcript && (
            <div className="space-y-2">
              <label className="text-sm font-medium">Original Transcript</label>
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm text-muted-foreground italic">
                  "{entry.raw_transcript}"
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar - Right Column */}
        <div className="space-y-6">
          {/* Mood Score */}
          <div className="bg-card p-4 rounded-lg border">
            {renderMoodSelector()}
          </div>

          {/* Emotions */}
          {entry.emotions?.length > 0 && (
            <div className="bg-card p-4 rounded-lg border">
              {renderEmotions()}
            </div>
          )}

          {/* Insights */}
          {entry.insights?.length > 0 && (
            <div className="bg-card p-4 rounded-lg border">
              {renderInsights()}
            </div>
          )}

          {/* Entry Stats */}
          <div className="bg-card p-4 rounded-lg border space-y-2">
            <h3 className="text-sm font-medium">Entry Details</h3>
            <div className="text-xs text-muted-foreground space-y-1">
              <p>Created: {new Date(entry.created_at).toLocaleString()}</p>
              <p>Last updated: {new Date(entry.updated_at).toLocaleString()}</p>
              <p>Status: {entry.processing_status}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Unsaved Changes Warning */}
      {isEdited && (
        <div className="fixed bottom-4 right-4 bg-card border rounded-lg p-4 shadow-lg">
          <p className="text-sm text-muted-foreground mb-2">You have unsaved changes</p>
          <div className="flex space-x-2">
            <Button onClick={handleSave} size="sm" disabled={isSaving}>
              Save
            </Button>
            <Button 
              onClick={() => {
                setIsEdited(false);
                loadEntry();
              }}
              variant="outline" 
              size="sm"
            >
              Discard
            </Button>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={deleteConfirmation.isOpen}
        onClose={closeDeleteConfirmation}
        onConfirm={confirmDeleteEntry}
        title="Delete Journal Entry"
        message={`Are you sure you want to delete "${entry?.title || 'this entry'}"? This entry will be moved to trash and can be permanently deleted later.`}
        confirmText="Delete Entry"
        confirmVariant="destructive"
        isLoading={deleteConfirmation.isDeleting}
        type="danger"
      />
    </div>
  );
}