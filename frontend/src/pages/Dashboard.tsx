import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/Button';
import { Mic, Calendar, TrendingUp, Award } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { entriesAPI } from '../services/api';
import { EntryCard } from '../components/EntryCard';

/**
 * Dashboard page - main landing page after login
 * Shows quick stats and primary actions
 */
interface DashboardStats {
  total_entries: number;
  current_streak: number;
  this_month: number;
  mood_average: number | null;
}

interface RecentEntry {
  id: number;
  title: string;
  created_at: string;
  mood_score: number;
  mood_emoji: string;
}

export function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats>({
    total_entries: 0,
    current_streak: 0,
    this_month: 0,
    mood_average: null,
  });
  const [recentEntries, setRecentEntries] = useState<RecentEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const response = await entriesAPI.getStats();
      setStats(response.data.stats);
      setRecentEntries(response.data.recent_entries);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold mb-2">
          Welcome back, {user?.display_name || user?.username || 'there'}!
        </h1>
        <p className="text-muted-foreground">
          Ready to capture today's thoughts?
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card p-6 rounded-lg border">
          <div className="flex items-center justify-between mb-2">
            <Calendar className="h-5 w-5 text-muted-foreground" />
            <span className="text-2xl font-semibold">
              {isLoading ? '—' : stats.total_entries}
            </span>
          </div>
          <p className="text-sm text-muted-foreground">Total Entries</p>
        </div>

        <div className="bg-card p-6 rounded-lg border">
          <div className="flex items-center justify-between mb-2">
            <Award className="h-5 w-5 text-muted-foreground" />
            <span className="text-2xl font-semibold">
              {isLoading ? '—' : stats.current_streak}
            </span>
          </div>
          <p className="text-sm text-muted-foreground">Day Streak</p>
        </div>

        <div className="bg-card p-6 rounded-lg border">
          <div className="flex items-center justify-between mb-2">
            <TrendingUp className="h-5 w-5 text-muted-foreground" />
            <span className="text-2xl font-semibold">
              {isLoading ? '—' : stats.this_month}
            </span>
          </div>
          <p className="text-sm text-muted-foreground">This Month</p>
        </div>

        <div className="bg-card p-6 rounded-lg border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-2xl">😊</span>
            <span className="text-2xl font-semibold">
              {isLoading ? '—' : (stats.mood_average || '—')}
            </span>
          </div>
          <p className="text-sm text-muted-foreground">Avg Mood</p>
        </div>
      </div>

      {/* Primary Action */}
      <div className="bg-primary/5 p-8 rounded-lg text-center">
        <Mic className="h-12 w-12 text-primary mx-auto mb-4" />
        <h2 className="text-xl font-semibold mb-2">Start Today's Entry</h2>
        <p className="text-muted-foreground mb-4">
          Take 2 minutes to reflect on your day
        </p>
        <Button
          size="lg"
          onClick={() => navigate('/record')}
          className="flex items-center space-x-2 mx-auto"
        >
          <Mic className="h-5 w-5" />
          <span>Start Recording</span>
        </Button>
      </div>

      {/* Recent Entries Preview */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Recent Entries</h2>
          <Button variant="ghost" onClick={() => navigate('/entries')}>
            View All
          </Button>
        </div>
        
        {isLoading ? (
          <div className="bg-card p-6 rounded-lg border text-center">
            <p className="text-muted-foreground">Loading recent entries...</p>
          </div>
        ) : recentEntries.length === 0 ? (
          <div className="bg-card p-6 rounded-lg border text-center">
            <p className="text-muted-foreground">
              No entries yet. Start your first journal entry to see it here!
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {recentEntries.map((entry) => (
              <EntryCard
                key={entry.id}
                id={entry.id}
                title={entry.title}
                createdAt={entry.created_at}
                moodScore={entry.mood_score}
                moodEmoji={entry.mood_emoji}
                compact
              />
            ))}
          </div>
        )}
      </div>

      {/* Usage Info for Free Tier */}
      {user?.subscription_tier === 'free' && (
        <div className="bg-muted/50 p-4 rounded-lg">
          <p className="text-sm text-muted-foreground">
            Free tier: {isLoading ? '—' : stats.this_month}/5 entries used this month.{' '}
            <button className="text-primary hover:underline">
              Upgrade to Premium
            </button>{' '}
            for unlimited entries.
          </p>
        </div>
      )}
    </div>
  );
}