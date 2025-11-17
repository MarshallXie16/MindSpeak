import React, { useEffect, useState } from 'react';
import { analyticsAPI } from '../services/api';
import { Button } from '../components/ui/Button';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Calendar, TrendingUp, Heart, Activity } from 'lucide-react';

/**
 * Analytics Dashboard - data visualization for mood and emotion trends
 */

interface MoodHistoryData {
  data: Array<{
    date: string;
    avg_mood: number | null;
    entry_count: number;
    min_mood: number;
    max_mood: number;
  }>;
  summary: {
    overall_avg: number | null;
    total_entries: number;
    days_with_entries: number;
    trend: string;
  };
}

interface EmotionTrendsData {
  emotions: Array<{
    name: string;
    count: number;
    percentage: number;
    avg_confidence: number;
  }>;
  total_emotion_mentions: number;
  unique_emotions: number;
}

interface WeekdayMoodData {
  data: Array<{
    weekday: string;
    weekday_num: number;
    avg_mood: number | null;
    entry_count: number;
  }>;
  insights: string[];
}

interface WordFrequencyData {
  words: Array<{
    word: string;
    count: number;
    avg_mood_when_mentioned: number | null;
  }>;
  total_words: number;
  unique_words: number;
}

export function Analytics() {
  const [timeRange, setTimeRange] = useState<7 | 30 | 90>(30);
  const [moodHistory, setMoodHistory] = useState<MoodHistoryData | null>(null);
  const [emotionTrends, setEmotionTrends] = useState<EmotionTrendsData | null>(null);
  const [weekdayMood, setWeekdayMood] = useState<WeekdayMoodData | null>(null);
  const [wordFrequency, setWordFrequency] = useState<WordFrequencyData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [moodResp, emotionResp, weekdayResp, wordResp] = await Promise.all([
        analyticsAPI.getMoodHistory(timeRange),
        analyticsAPI.getEmotionTrends(timeRange),
        analyticsAPI.getMoodByWeekday(90), // Use 90 days for weekday patterns
        analyticsAPI.getWordFrequency(timeRange, 20),
      ]);

      setMoodHistory(moodResp.data);
      setEmotionTrends(emotionResp.data);
      setWeekdayMood(weekdayResp.data);
      setWordFrequency(wordResp.data);
    } catch (err) {
      console.error('Error loading analytics:', err);
      setError('Failed to load analytics data. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4', '#6366f1'];

  const getTrendIcon = (trend: string) => {
    if (trend === 'improving') return '📈';
    if (trend === 'declining') return '📉';
    if (trend === 'stable') return '➡️';
    return '—';
  };

  const hasData = moodHistory?.summary.total_entries && moodHistory.summary.total_entries > 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Analytics Dashboard</h1>
          <p className="text-muted-foreground">
            Visualize your mood patterns and emotional insights
          </p>
        </div>

        {/* Time Range Selector */}
        <div className="flex gap-2">
          <Button
            variant={timeRange === 7 ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTimeRange(7)}
          >
            7 days
          </Button>
          <Button
            variant={timeRange === 30 ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTimeRange(30)}
          >
            30 days
          </Button>
          <Button
            variant={timeRange === 90 ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTimeRange(90)}
          >
            90 days
          </Button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-destructive/10 p-4 rounded-lg">
          <p className="text-destructive">{error}</p>
          <Button variant="outline" size="sm" onClick={loadAnalyticsData} className="mt-2">
            Try Again
          </Button>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="bg-card p-12 rounded-lg border text-center">
          <p className="text-muted-foreground">Loading analytics data...</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !hasData && !error && (
        <div className="bg-card p-12 rounded-lg border text-center">
          <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No Data Yet</h2>
          <p className="text-muted-foreground">
            Create some journal entries to see your analytics here!
          </p>
        </div>
      )}

      {/* Analytics Content */}
      {!isLoading && hasData && (
        <>
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-card p-6 rounded-lg border">
              <div className="flex items-center justify-between mb-2">
                <Heart className="h-5 w-5 text-muted-foreground" />
                <span className="text-2xl font-semibold">
                  {moodHistory?.summary.overall_avg?.toFixed(1) || '—'}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">Avg Mood</p>
            </div>

            <div className="bg-card p-6 rounded-lg border">
              <div className="flex items-center justify-between mb-2">
                <Calendar className="h-5 w-5 text-muted-foreground" />
                <span className="text-2xl font-semibold">
                  {moodHistory?.summary.total_entries || 0}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">Total Entries</p>
            </div>

            <div className="bg-card p-6 rounded-lg border">
              <div className="flex items-center justify-between mb-2">
                <Activity className="h-5 w-5 text-muted-foreground" />
                <span className="text-2xl font-semibold">
                  {moodHistory?.summary.days_with_entries || 0}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">Days with Entries</p>
            </div>

            <div className="bg-card p-6 rounded-lg border">
              <div className="flex items-center justify-between mb-2">
                <TrendingUp className="h-5 w-5 text-muted-foreground" />
                <span className="text-2xl">
                  {getTrendIcon(moodHistory?.summary.trend || 'no_data')}
                </span>
              </div>
              <p className="text-sm text-muted-foreground capitalize">
                {moodHistory?.summary.trend?.replace('_', ' ') || 'No Trend'}
              </p>
            </div>
          </div>

          {/* Mood Over Time Chart */}
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Mood Over Time</h2>
            {moodHistory && moodHistory.data.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={moodHistory.data}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis domain={[0, 10]} />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value: any) => [value.toFixed(1), 'Mood']}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="avg_mood"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    name="Average Mood"
                    dot={{ fill: '#3b82f6' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-muted-foreground text-center py-8">No mood data available</p>
            )}
          </div>

          {/* Emotion Breakdown & Weekday Mood */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Emotion Breakdown */}
            <div className="bg-card p-6 rounded-lg border">
              <h2 className="text-xl font-semibold mb-4">Emotion Breakdown</h2>
              {emotionTrends && emotionTrends.emotions.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={emotionTrends.emotions.slice(0, 7)}
                      dataKey="count"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label={(entry) => entry.name}
                    >
                      {emotionTrends.emotions.slice(0, 7).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: any, name: string) => [`${value} mentions`, name]} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-muted-foreground text-center py-8">No emotion data available</p>
              )}
            </div>

            {/* Mood by Weekday */}
            <div className="bg-card p-6 rounded-lg border">
              <h2 className="text-xl font-semibold mb-4">Mood by Day of Week</h2>
              {weekdayMood && weekdayMood.data.filter(d => d.avg_mood !== null).length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={weekdayMood.data}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="weekday"
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value) => value.slice(0, 3)}
                    />
                    <YAxis domain={[0, 10]} />
                    <Tooltip formatter={(value: any) => [value?.toFixed(1) || 'N/A', 'Mood']} />
                    <Bar dataKey="avg_mood" fill="#8b5cf6" name="Average Mood" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-muted-foreground text-center py-8">Not enough data</p>
              )}
              {weekdayMood && weekdayMood.insights.length > 0 && (
                <div className="mt-4 space-y-2">
                  {weekdayMood.insights.map((insight, index) => (
                    <p key={index} className="text-sm text-muted-foreground">
                      💡 {insight}
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Common Words */}
          <div className="bg-card p-6 rounded-lg border">
            <h2 className="text-xl font-semibold mb-4">Common Themes & Topics</h2>
            {wordFrequency && wordFrequency.words.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {wordFrequency.words.slice(0, 12).map((word) => (
                  <div key={word.word} className="bg-muted/50 p-4 rounded-lg">
                    <div className="font-semibold text-lg">{word.word}</div>
                    <div className="text-sm text-muted-foreground">
                      {word.count} mentions
                    </div>
                    {word.avg_mood_when_mentioned && (
                      <div className="text-xs text-muted-foreground mt-1">
                        Mood: {word.avg_mood_when_mentioned.toFixed(1)}/10
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground text-center py-8">No word data available</p>
            )}
          </div>
        </>
      )}
    </div>
  );
}
