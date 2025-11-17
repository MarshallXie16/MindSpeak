# Analytics Dashboard - Technical Design

## Overview
The Analytics Dashboard provides data-driven insights through interactive visualizations of mood trends, emotion patterns, and behavioral correlations.

## Backend API Design

### Endpoint 1: Mood History
**Route:** `GET /api/analytics/mood-history`

**Query Parameters:**
- `days` (optional, default=30): Number of days to look back (7, 30, 90)

**Response:**
```json
{
  "data": [
    {
      "date": "2025-11-16",
      "avg_mood": 7.5,
      "entry_count": 3,
      "min_mood": 6,
      "max_mood": 9
    }
  ],
  "summary": {
    "overall_avg": 7.2,
    "total_entries": 45,
    "days_with_entries": 28,
    "trend": "improving"  // or "declining", "stable"
  }
}
```

**SQL Logic:**
```sql
SELECT
  DATE(created_at) as date,
  AVG(mood_score) as avg_mood,
  COUNT(*) as entry_count,
  MIN(mood_score) as min_mood,
  MAX(mood_score) as max_mood
FROM journal_entries
WHERE user_id = ?
  AND is_deleted = FALSE
  AND mood_score IS NOT NULL
  AND created_at >= DATE('now', '-? days')
GROUP BY DATE(created_at)
ORDER BY date ASC
```

---

### Endpoint 2: Emotion Trends
**Route:** `GET /api/analytics/emotion-trends`

**Query Parameters:**
- `days` (optional, default=30)

**Response:**
```json
{
  "emotions": [
    {
      "name": "happy",
      "count": 45,
      "percentage": 22.5,
      "avg_confidence": 0.78
    },
    {
      "name": "anxious",
      "count": 38,
      "percentage": 19.0,
      "avg_confidence": 0.82
    }
  ],
  "total_emotion_mentions": 200,
  "unique_emotions": 15
}
```

**Logic:**
- Parse JSON emotions field from all entries
- Aggregate counts and calculate percentages
- Sort by count descending

---

### Endpoint 3: Mood by Weekday
**Route:** `GET /api/analytics/mood-by-weekday`

**Query Parameters:**
- `days` (optional, default=90)

**Response:**
```json
{
  "data": [
    {
      "weekday": "Monday",
      "weekday_num": 0,
      "avg_mood": 6.2,
      "entry_count": 12
    },
    {
      "weekday": "Tuesday",
      "weekday_num": 1,
      "avg_mood": 7.1,
      "entry_count": 13
    }
  ],
  "insights": [
    "Your mood is highest on Fridays (8.2/10)",
    "Your mood tends to dip on Mondays (6.2/10)"
  ]
}
```

---

### Endpoint 4: Word Frequency
**Route:** `GET /api/analytics/word-frequency`

**Query Parameters:**
- `days` (optional, default=30)
- `limit` (optional, default=50): Top N words

**Response:**
```json
{
  "words": [
    {"word": "work", "count": 45, "avg_mood_when_mentioned": 6.1},
    {"word": "family", "count": 32, "avg_mood_when_mentioned": 7.8}
  ],
  "total_words": 5420,
  "unique_words": 1240
}
```

**Logic:**
- Extract words from formatted_content
- Filter out stopwords (the, a, an, I, you, etc.)
- Calculate mood correlation per word

---

## Database Optimizations

### Indexes Needed
```sql
CREATE INDEX idx_entries_user_date ON journal_entries(user_id, created_at);
CREATE INDEX idx_entries_user_mood ON journal_entries(user_id, mood_score);
```

### Performance Considerations
- Cache results for 5 minutes (future: Redis)
- Limit query to reasonable time ranges
- Paginate word frequency results

---

## Frontend Design

### Component Structure
```
src/pages/Analytics.tsx
  ├── components/
  │   ├── MoodLineChart.tsx       (recharts LineChart)
  │   ├── EmotionPieChart.tsx     (recharts PieChart)
  │   ├── WeekdayBarChart.tsx     (recharts BarChart)
  │   ├── WordCloudVisualization.tsx  (react-wordcloud)
  │   ├── StatCard.tsx            (reusable metric card)
  │   └── TimeRangeSelector.tsx   (7/30/90 day toggle)
```

### Layout
```
┌─────────────────────────────────────────────────────┐
│  Analytics Dashboard                    [7d][30d][90d]│
├─────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Avg Mood │  │  Entries │  │  Streak  │          │
│  │   7.2    │  │    45    │  │    12    │          │
│  └──────────┘  └──────────┘  └──────────┘          │
├─────────────────────────────────────────────────────┤
│  Mood Over Time                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │     Line Chart (mood vs date)               │   │
│  └─────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────┤
│  ┌──────────────────────┐  ┌──────────────────────┐│
│  │ Emotion Breakdown    │  │ Mood by Day of Week  ││
│  │  Pie Chart           │  │  Bar Chart           ││
│  └──────────────────────┘  └──────────────────────┘│
├─────────────────────────────────────────────────────┤
│  Common Themes & Topics                             │
│  ┌─────────────────────────────────────────────┐   │
│  │        Word Cloud                            │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## State Management

### Analytics Page State
```typescript
interface AnalyticsState {
  timeRange: 7 | 30 | 90;
  moodHistory: MoodHistoryData | null;
  emotionTrends: EmotionTrendsData | null;
  weekdayMood: WeekdayMoodData | null;
  wordFrequency: WordFrequencyData | null;
  loading: boolean;
  error: string | null;
}
```

### Data Fetching Strategy
- Fetch all analytics data when page loads
- Refetch when timeRange changes
- Show loading skeleton during fetch
- Handle empty states gracefully

---

## Error Handling

### Backend Errors
- Return 200 with empty arrays if no data
- Handle database query errors gracefully
- Log errors for debugging

### Frontend Errors
- Show user-friendly error messages
- Provide "Try Again" button
- Show empty state if no data available

---

## Edge Cases to Handle

1. **No entries yet**
   - Show empty state with prompt to create first entry
   - Don't show charts (causes UI issues)

2. **Single entry**
   - Charts should still render (single data point)
   - Avoid "not enough data" errors

3. **Missing mood scores**
   - Filter out entries without mood_score
   - Handle if all entries lack mood data

4. **JSON parsing errors**
   - Safely parse emotions field
   - Skip entries with malformed JSON

5. **Large datasets**
   - Limit queries to reasonable ranges
   - Paginate word frequency results

---

## Testing Strategy

### Backend Tests
```python
def test_mood_history_empty_data()
def test_mood_history_single_entry()
def test_mood_history_7_days()
def test_mood_history_30_days()
def test_mood_history_null_mood_scores()
def test_emotion_trends_aggregation()
def test_emotion_trends_malformed_json()
def test_weekday_mood_calculation()
def test_word_frequency_stopword_filtering()
def test_word_frequency_mood_correlation()
```

### Frontend Manual Testing
- [ ] Charts render with sample data
- [ ] Time range selector updates charts
- [ ] Empty state shows when no data
- [ ] Loading states appear during fetch
- [ ] Responsive on mobile (320px width)
- [ ] Tooltips work on hover
- [ ] No console errors

---

## Performance Targets

- Analytics page load: < 2 seconds
- API response time: < 500ms per endpoint
- Chart render time: < 100ms
- Memory usage: < 50MB for page

---

## Future Enhancements (Not in P0.1)

- Export charts as PNG
- Download data as CSV
- Mood streak calendar heatmap
- Correlation matrix (mood vs entities)
- Trend predictions
- Comparison mode (this month vs last month)

---

## Dependencies

**Backend:**
- None (uses existing SQLAlchemy)

**Frontend:**
- `recharts` - Charting library (MIT license)
- Optional: `react-wordcloud` - Word cloud component

---

## Implementation Checklist

Backend:
- [x] Create analytics.py blueprint
- [x] Implement mood-history endpoint
- [x] Implement emotion-trends endpoint
- [x] Implement mood-by-weekday endpoint
- [x] Implement word-frequency endpoint
- [x] Write tests for all endpoints (23 tests, all passing)
- [x] Register blueprint

Frontend:
- [x] Install recharts
- [x] Create Analytics.tsx page
- [x] Create MoodLineChart component (integrated in Analytics.tsx)
- [x] Create EmotionPieChart component (integrated in Analytics.tsx)
- [x] Create WeekdayBarChart component (integrated in Analytics.tsx)
- [ ] Create WordCloud component (optional - using word list instead)
- [x] Create TimeRangeSelector (integrated in Analytics.tsx)
- [x] Create StatCard component (integrated in Analytics.tsx)
- [x] Add route and navigation
- [x] Test with real data

Documentation:
- [ ] Update memory.md
- [ ] Update tasks.md
- [ ] Add API examples to README
