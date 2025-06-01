import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Loader2, Search, Calendar, Edit, Trash2, Plus, List, ChevronLeft, ChevronRight } from 'lucide-react';
import { entriesAPI } from '../services/api';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { NewEntryModal } from '../components/NewEntryModal';
import { ConfirmationModal } from '../components/ui/ConfirmationModal';

interface JournalEntry {
  id: number;
  title: string;
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
  mood_emoji?: string;
}

interface CalendarData {
  [date: string]: ParsedEntry[];
}

type ViewMode = 'list' | 'calendar';

export function EntriesList() {
  const navigate = useNavigate();
  const [entries, setEntries] = useState<ParsedEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isNewEntryModalOpen, setIsNewEntryModalOpen] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState<{
    isOpen: boolean;
    entryId: number | null;
    entryTitle: string;
    isDeleting: boolean;
  }>({
    isOpen: false,
    entryId: null,
    entryTitle: '',
    isDeleting: false
  });
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [calendarDate, setCalendarDate] = useState(new Date());

  useEffect(() => {
    loadEntries();
  }, [page]);

  const loadEntries = async (isNewSearch = false) => {
    try {
      console.log('🔄 Loading entries...', { isNewSearch, page });
      setIsLoading(true);
      setError(null);
      
      const currentPage = isNewSearch ? 1 : page;
      const response = await entriesAPI.getEntries({ 
        page: currentPage, 
        limit: 20 
      });
      
      console.log('📥 API Response:', response.data);
      
      const rawEntries = response.data.entries || [];
      console.log('📋 Raw entries count:', rawEntries.length);
      
      const parsedEntries: ParsedEntry[] = rawEntries.map((entry: JournalEntry, index: number) => {
        try {
          const parsed = {
            ...entry,
            emotions: typeof entry.emotions === 'string' 
              ? JSON.parse(entry.emotions || '[]')
              : entry.emotions || [],
            insights: typeof entry.insights === 'string'
              ? JSON.parse(entry.insights || '[]')
              : entry.insights || []
          };
          console.log(`✅ Parsed entry ${index + 1}:`, { 
            id: parsed.id, 
            title: parsed.title, 
            hasContent: !!parsed.formatted_content,
            emotionsCount: parsed.emotions.length 
          });
          return parsed;
        } catch (parseErr) {
          console.error(`❌ Error parsing entry ${index + 1}:`, parseErr, entry);
          // Return entry with safe defaults
          return {
            ...entry,
            emotions: [],
            insights: [],
            formatted_content: entry.formatted_content || ''
          };
        }
      });
      
      if (isNewSearch) {
        setEntries(parsedEntries);
        setPage(1);
      } else {
        setEntries(prev => page === 1 ? parsedEntries : [...prev, ...parsedEntries]);
      }
      
      setHasMore(parsedEntries.length === 20); // If we got a full page, there might be more
      console.log('✅ Entries loaded successfully:', parsedEntries.length);
      
    } catch (err: any) {
      console.error('❌ Error loading entries:', err);
      console.error('Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      });
      setError(err.response?.data?.message || 'Failed to load entries');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearchTerm(value);
    // TODO: Implement search filtering
    // For now, just filter locally
  };

  const handleDeleteEntry = (entryId: number) => {
    const entry = entries.find(e => e.id === entryId);
    if (entry) {
      setDeleteConfirmation({
        isOpen: true,
        entryId,
        entryTitle: entry.title,
        isDeleting: false
      });
    }
  };

  const confirmDeleteEntry = async () => {
    if (!deleteConfirmation.entryId) return;

    setDeleteConfirmation(prev => ({ ...prev, isDeleting: true }));

    try {
      await entriesAPI.deleteEntry(deleteConfirmation.entryId);
      setEntries(prev => prev.filter(entry => entry.id !== deleteConfirmation.entryId));
      setDeleteConfirmation({
        isOpen: false,
        entryId: null,
        entryTitle: '',
        isDeleting: false
      });
    } catch (err: any) {
      console.error('Error deleting entry:', err);
      setError(err.response?.data?.message || 'Failed to delete entry');
      setDeleteConfirmation(prev => ({ ...prev, isDeleting: false }));
    }
  };

  const closeDeleteConfirmation = () => {
    if (!deleteConfirmation.isDeleting) {
      setDeleteConfirmation({
        isOpen: false,
        entryId: null,
        entryTitle: '',
        isDeleting: false
      });
    }
  };

  const getMoodColor = (score: number | null | undefined) => {
    if (!score || typeof score !== 'number') return 'bg-gray-400';
    if (score >= 8) return 'bg-green-500';
    if (score >= 6) return 'bg-blue-500';
    if (score >= 4) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getMoodLabel = (score: number | null | undefined) => {
    if (!score || typeof score !== 'number') return 'N/A';
    if (score >= 8) return 'Great';
    if (score >= 6) return 'Good';
    if (score >= 4) return 'Okay';
    return 'Rough';
  };

  const getMoodEmoji = (score: number | null | undefined) => {
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

  const truncateContent = (content: string | null | undefined, maxLength: number = 150) => {
    if (!content) return 'No content available';
    if (content.length <= maxLength) return content;
    return content.slice(0, maxLength) + '...';
  };

  const filteredEntries = entries.filter(entry => {
    const title = entry.title || '';
    const content = entry.formatted_content || '';
    return title.toLowerCase().includes(searchTerm.toLowerCase()) ||
           content.toLowerCase().includes(searchTerm.toLowerCase());
  });

  // Calendar view helpers
  const getCalendarData = (): CalendarData => {
    const data: CalendarData = {};
    const firstDay = new Date(calendarDate.getFullYear(), calendarDate.getMonth(), 1);
    const lastDay = new Date(calendarDate.getFullYear(), calendarDate.getMonth() + 1, 0);
    
    filteredEntries.forEach(entry => {
      const entryDate = new Date(entry.created_at);
      if (entryDate >= firstDay && entryDate <= lastDay) {
        const dateKey = entryDate.toISOString().split('T')[0];
        if (!data[dateKey]) {
          data[dateKey] = [];
        }
        data[dateKey].push(entry);
      }
    });
    
    return data;
  };

  const getDaysInMonth = () => {
    const year = calendarDate.getFullYear();
    const month = calendarDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    
    // Start from the first Sunday on or before the first day of the month
    startDate.setDate(startDate.getDate() - startDate.getDay());
    
    const days = [];
    const endDate = new Date(lastDay);
    endDate.setDate(endDate.getDate() + (6 - endDate.getDay()));
    
    for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
      days.push(new Date(d));
    }
    
    return days;
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCalendarDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(newDate.getMonth() - 1);
      } else {
        newDate.setMonth(newDate.getMonth() + 1);
      }
      return newDate;
    });
  };

  const isToday = (date: Date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isCurrentMonth = (date: Date) => {
    return date.getMonth() === calendarDate.getMonth();
  };

  const formatDateKey = (date: Date) => {
    return date.toISOString().split('T')[0];
  };

  if (isLoading && entries.length === 0) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading entries...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Your Journal Entries</h1>
          <p className="text-muted-foreground">
            {entries.length} {entries.length === 1 ? 'entry' : 'entries'} found
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          <Button
            onClick={() => setIsNewEntryModalOpen(true)}
            size="lg"
            className="flex items-center space-x-2"
          >
            <Plus className="h-5 w-5" />
            <span>New Entry</span>
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search entries..."
            value={searchTerm}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => setViewMode(viewMode === 'list' ? 'calendar' : 'list')}
        >
          {viewMode === 'list' ? (
            <>
              <Calendar className="h-4 w-4 mr-2" />
              Calendar View
            </>
          ) : (
            <>
              <List className="h-4 w-4 mr-2" />
              List View
            </>
          )}
        </Button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Content based on view mode */}
      {viewMode === 'list' ? (
        <>
          {/* List View */}
          {filteredEntries.length === 0 ? (
            <div className="text-center py-12">
              <div className="max-w-md mx-auto">
                <h3 className="text-lg font-medium mb-2">No entries found</h3>
                <p className="text-muted-foreground mb-6">
                  {searchTerm 
                    ? "Try adjusting your search terms or create a new entry to get started."
                    : "Create your first journal entry to get started on your mindfulness journey."
                  }
                </p>
                <Button onClick={() => setIsNewEntryModalOpen(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create First Entry
                </Button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEntries.map((entry) => (
            <div
              key={entry.id}
              className="bg-card border rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              {/* Entry Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold line-clamp-2 mb-1">
                    {entry.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {new Date(entry.created_at).toLocaleDateString()}
                  </p>
                </div>
                
                {/* Mood Indicator */}
                <div className="flex items-center space-x-2">
                  <div
                    className={`w-3 h-3 rounded-full ${getMoodColor(entry.mood_score)}`}
                    title={`Mood: ${getMoodLabel(entry.mood_score)} ${entry.mood_score ? `(${entry.mood_score}/10)` : ''}`}
                  />
                  <span className="text-xs text-muted-foreground">
                    {entry.mood_score || 'N/A'}{entry.mood_score ? '/10' : ''}
                  </span>
                </div>
              </div>

              {/* Entry Content Preview */}
              <div className="mb-4">
                <p className="text-sm text-muted-foreground line-clamp-3">
                  {truncateContent(entry.formatted_content)}
                </p>
              </div>

              {/* Emotions */}
              {entry.emotions && Array.isArray(entry.emotions) && entry.emotions.length > 0 && (
                <div className="mb-4">
                  <div className="flex flex-wrap gap-1">
                    {entry.emotions.slice(0, 3).map((emotion, index) => (
                      <span
                        key={index}
                        className="inline-block px-2 py-1 bg-secondary text-xs rounded-full"
                      >
                        {emotion?.name || 'Unknown'}
                      </span>
                    ))}
                    {entry.emotions.length > 3 && (
                      <span className="text-xs text-muted-foreground">
                        +{entry.emotions.length - 3} more
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Processing Status */}
              {entry.processing_status !== 'completed' && (
                <div className="mb-4">
                  <span className={`inline-block px-2 py-1 text-xs rounded-full ${{
                    'pending': 'bg-yellow-100 text-yellow-800',
                    'processing': 'bg-blue-100 text-blue-800',
                    'error': 'bg-red-100 text-red-800'
                  }[entry.processing_status] || 'bg-gray-100 text-gray-800'}`}>
                    {entry.processing_status}
                  </span>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t">
                <Link
                  to={`/entries/${entry.id}/edit`}
                  className="text-sm text-primary hover:underline flex items-center"
                >
                  <Edit className="h-3 w-3 mr-1" />
                  Edit
                </Link>
                
                <Button
                  onClick={() => handleDeleteEntry(entry.id)}
                  variant="ghost"
                  size="sm"
                  className="text-destructive hover:text-destructive h-auto p-1"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </div>
          ))}
            </div>
          )}

          {/* Load More */}
          {hasMore && filteredEntries.length > 0 && (
            <div className="text-center pt-6">
              <Button
                onClick={() => setPage(prev => prev + 1)}
                variant="outline"
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : null}
                Load More
              </Button>
            </div>
          )}
        </>
      ) : (
        <>
          {/* Calendar View */}
          <div className="space-y-4">
            {/* Calendar Navigation */}
            <div className="flex items-center justify-between bg-card p-4 rounded-lg border">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigateMonth('prev')}
                className="flex items-center space-x-1"
              >
                <ChevronLeft className="h-4 w-4" />
                <span>Previous</span>
              </Button>
              
              <h2 className="text-xl font-semibold">
                {calendarDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
              </h2>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigateMonth('next')}
                className="flex items-center space-x-1"
              >
                <span>Next</span>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            {/* Calendar Grid */}
            <div className="bg-card rounded-lg border overflow-hidden">
              {/* Day Headers */}
              <div className="grid grid-cols-7 bg-muted/50">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div key={day} className="p-3 text-center text-sm font-medium">
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar Days */}
              <div className="grid grid-cols-7">
                {getDaysInMonth().map((date, index) => {
                  const dateKey = formatDateKey(date);
                  const dayEntries = getCalendarData()[dateKey] || [];
                  const isCurrentMonthDay = isCurrentMonth(date);
                  const isTodayDate = isToday(date);

                  return (
                    <div
                      key={index}
                      className={`min-h-[120px] p-2 border-r border-b border-border/50 ${
                        !isCurrentMonthDay ? 'bg-muted/20 text-muted-foreground' : ''
                      } ${isTodayDate ? 'bg-primary/5' : ''}`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span
                          className={`text-sm font-medium ${
                            isTodayDate ? 'text-primary' : ''
                          }`}
                        >
                          {date.getDate()}
                        </span>
                        {isTodayDate && (
                          <div className="w-2 h-2 bg-primary rounded-full"></div>
                        )}
                      </div>

                      {/* Entries for this day */}
                      <div className="space-y-1">
                        {dayEntries.slice(0, 3).map((entry) => (
                          <div
                            key={entry.id}
                            className="text-xs p-1 bg-accent/80 rounded cursor-pointer hover:bg-accent transition-colors"
                            onClick={() => navigate(`/entries/${entry.id}/edit`)}
                            title={entry.title}
                          >
                            <div className="flex items-center space-x-1">
                              <span className="text-xs">{getMoodEmoji(entry.mood_score)}</span>
                              <span className="truncate">{entry.title}</span>
                            </div>
                          </div>
                        ))}
                        
                        {dayEntries.length > 3 && (
                          <div className="text-xs text-muted-foreground">
                            +{dayEntries.length - 3} more
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Load More - moved outside to avoid duplication */}
      {viewMode === 'list' && hasMore && filteredEntries.length > 0 && (
        <div className="text-center pt-6">
          <Button
            onClick={() => setPage(prev => prev + 1)}
            variant="outline"
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : null}
            Load More
          </Button>
        </div>
      )}

      {/* New Entry Modal */}
      <NewEntryModal
        isOpen={isNewEntryModalOpen}
        onClose={() => setIsNewEntryModalOpen(false)}
      />

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={deleteConfirmation.isOpen}
        onClose={closeDeleteConfirmation}
        onConfirm={confirmDeleteEntry}
        title="Delete Journal Entry"
        message={`Are you sure you want to delete "${deleteConfirmation.entryTitle}"? This entry will be moved to trash and can be permanently deleted later.`}
        confirmText="Delete Entry"
        confirmVariant="destructive"
        isLoading={deleteConfirmation.isDeleting}
        type="danger"
      />
    </div>
  );
}