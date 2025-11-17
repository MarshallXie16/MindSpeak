# MindSpeak Product Backlog

**Last Updated:** 2025-11-16
**Vision:** Transform from passive journaling tool to active growth partner

---

## 🎯 Strategic Vision

### Current State: Basic Voice Journaling ✅
- Voice recording → AI transcription → Formatted entry → Basic insights

### Target State: Action-Driven Mental Wellness Platform
**Flow:** Set goals → Journal/reflect → AI insights → Actionable tasks → Proactive check-ins → Measure progress → Achieve goals

---

## 📊 Feature Prioritization Framework

### P0 - Critical Differentiators (Next 2-4 weeks)
Features that make us **not just another journaling app**

### P1 - Core Enhancement (Next 1-2 months)
Features that significantly improve user experience and retention

### P2 - Growth Features (Next 2-4 months)
Features that enable new user segments (therapists, premium tiers)

### P3 - Future Innovation (6+ months)
Advanced features requiring R&D or partnerships

---

## 🚀 P0 - Critical Differentiators

### P0.1: Data Visualization Dashboard
**Why:** Current competitors lack quantifiable, visual insights. This is our key differentiator.

**User Story:**
> "As a user, I want to see my emotional trends over time in visual charts so I can understand patterns I wouldn't notice from reading entries alone."

**Features:**
- [ ] Mood chart (line graph over past 7/30/90 days)
- [ ] Emotion frequency breakdown (pie chart or bar chart)
- [ ] Streak visualization (calendar heatmap)
- [ ] Word cloud from journal entries
- [ ] Mood vs. day-of-week correlation chart
- [ ] Export charts as images

**Technical Notes:**
- Frontend: Use `recharts` or `chart.js` for visualizations
- Backend: Add `/api/analytics/mood-history?days=30` endpoint
- Backend: Add `/api/analytics/emotion-trends` endpoint
- Cache expensive queries in Redis

**Acceptance Criteria:**
- User can view mood trends for past 30/90 days
- Charts are interactive (hover for details)
- Data updates in real-time after new entry
- Mobile-responsive charts

**Estimated Effort:** 3-5 days
**Dependencies:** None

---

### P0.2: Entity Extraction & Relationship Mapping
**Why:** Uncover hidden correlations between people/places/events and emotions. No competitor does this well.

**User Story:**
> "As a user, I want the app to identify when I mention specific people, places, or events and show me how my mood correlates with them over time."

**Features:**
- [ ] NLP entity extraction (people, places, events, activities)
- [ ] Entity tagging in entries (highlight mentions)
- [ ] Entity profile pages (show all mentions + associated moods)
- [ ] Correlation analysis: "You feel 20% more anxious when you mention 'Mom'"
- [ ] Entity timeline view
- [ ] Suggested tags based on past patterns

**Technical Notes:**
- Use spaCy or Claude's entity extraction capabilities
- Store entities in separate `entities` table with relationships
- Calculate mood correlations: `avg_mood_with_entity` vs `avg_mood_without_entity`
- Add database indexes for performance

**Example:**
```
Entry: "Had lunch with Sarah today. Felt anxious about the presentation."
Extracted Entities:
- Person: Sarah (mood: anxious)
- Event: presentation (mood: anxious)

Correlation Insight:
"You've mentioned 'Sarah' 5 times. Average mood: 6.2/10
You've mentioned 'presentation' 3 times. Average mood: 4.8/10"
```

**Acceptance Criteria:**
- Entities extracted from >90% of entries with >80% accuracy
- User can click entity to see all related entries
- Correlation insights shown when statistically significant (>5 mentions)
- User can manually add/remove entity tags

**Estimated Effort:** 5-7 days
**Dependencies:** None

---

### P0.3: Goal-Setting & Action Loop
**Why:** Moves from passive reflection to active improvement. Creates measurable impact.

**User Story:**
> "As a user, I want to set personal goals and have the AI provide specific, actionable next steps based on my journal entries."

**Features:**
- [ ] Goal creation with templates (e.g., "Be more confident", "Improve sleep")
- [ ] AI analyzes entries against goals
- [ ] Generates specific, actionable tasks (not just "try to be positive")
- [ ] Task tracking with reminders
- [ ] Progress measurement tied to mood/entity data
- [ ] Goal reflection prompts

**Flow:**
```
1. User sets goal: "I want to feel less anxious about work"
2. User journals: "Stressed about deadline again"
3. AI insight: "This is the 3rd time this week you've mentioned work stress"
4. AI action: "Try the 5-minute breathing exercise before your next meeting"
5. Create task: "Do breathing exercise at 2:45 PM today"
6. Follow-up check-in: "How did the breathing exercise go?"
7. Measure: Track anxiety mentions before/after intervention
```

**Technical Notes:**
- Add `goals` and `tasks` tables
- Integrate with calendar (Google Calendar API for task creation)
- Use Claude to generate context-aware action items
- Track task completion and correlate with mood changes

**Acceptance Criteria:**
- User can create custom goals or use templates
- AI generates at least 1 actionable task per week per goal
- Task completion tracked and correlated with mood
- Progress visualization for each goal

**Estimated Effort:** 7-10 days
**Dependencies:** P0.2 (entity extraction helpful for goal tracking)

---

### P0.4: Challenging Thinking Patterns (Therapeutic AI)
**Why:** Current AI is too validating. Real therapists challenge negative thought patterns.

**User Story:**
> "As a user, when I express self-defeating thoughts, I want the AI to gently challenge me with evidence-based therapeutic techniques."

**Features:**
- [ ] Detect cognitive distortions (all-or-nothing thinking, catastrophizing, etc.)
- [ ] Apply CBT/DBT techniques in responses
- [ ] Ask Socratic questions instead of just validating
- [ ] Reference past entries as counter-evidence
- [ ] Gradual tone (supportive but challenging)

**Examples:**
```
❌ Current: "You're feeling overwhelmed by work. That's completely valid."

✅ New: "You mentioned feeling overwhelmed. Last week you successfully
handled a similar deadline—what helped you then? Could those strategies
work now?"

❌ Current: "It's okay to feel anxious about the presentation."

✅ New: "You've given 5 presentations this year. In 4 of them, you noted
feeling anxious beforehand but satisfied afterward. What does that pattern
tell you?"
```

**Technical Notes:**
- Enhance Claude prompt with CBT/DBT framework
- Add pattern detection for common distortions
- Reference long-term memory (vector DB) for past evidence
- A/B test tone (supportive vs challenging)

**Acceptance Criteria:**
- Detect cognitive distortions in at least 3 categories
- Reference past entries when challenging current thoughts
- Maintain supportive tone (not preachy or dismissive)
- User feedback: "insightful" rating >70%

**Estimated Effort:** 5-7 days
**Dependencies:** P1.1 (vector database for past entry retrieval)

---

## 🔥 P1 - Core Enhancement

### P1.1: Long-Term Memory with Vector Database
**Why:** Enable semantic search and truly personalized insights over time.

**User Story:**
> "As a user, I want the AI to remember my journey across months and reference relevant past experiences in its insights."

**Features:**
- [ ] Vector database integration (Pinecone or Weaviate)
- [ ] Embed all journal entries on creation
- [ ] Semantic search: "Show me times I felt similar to today"
- [ ] AI references relevant past entries in insights
- [ ] Long-term pattern detection

**Technical Notes:**
- Use OpenAI `text-embedding-3-small` ($0.02/1M tokens)
- Store embeddings in Pinecone (free tier: 1GB, 100k vectors)
- Asynchronously embed entries after processing
- Query top-k similar entries when generating insights

**Example:**
```
Current entry: "Feeling anxious about new job"
Similar past entry (6 months ago): "Anxious about starting grad school"
Past insight worked: "Break it into small wins"

AI response: "This reminds me of when you started grad school and felt
similarly anxious. You mentioned that breaking things into small wins helped
then. Could that work here too?"
```

**Acceptance Criteria:**
- All entries embedded within 30 seconds of creation
- Semantic search returns relevant results (>80% user satisfaction)
- AI references past entries in at least 30% of insights
- Search across full history (<500ms response time)

**Estimated Effort:** 5-7 days
**Dependencies:** None

---

### P1.2: Proactive Check-Ins
**Why:** Creates accountability and fills gap between insights and action.

**User Story:**
> "As a user, I want the app to check in on me at meaningful moments based on my patterns and calendar events."

**Features:**
- [ ] Pattern-based check-ins (e.g., "You often feel anxious Sunday evenings")
- [ ] Event-based check-ins (e.g., "How did the interview go?")
- [ ] Task follow-ups (e.g., "Did you try the breathing exercise?")
- [ ] Customizable check-in schedule
- [ ] Push notifications + in-app notifications
- [ ] SMS option (premium feature)

**Triggers:**
- Recurring patterns (detected via analytics)
- Calendar events (after syncing Google/Apple calendar)
- Task completion reminders
- Significant mood changes
- Long gaps without journaling

**Technical Notes:**
- Background job scheduler (Celery with Redis)
- Notification service (Firebase Cloud Messaging for push)
- Calendar API integration (Google Calendar, Apple Calendar)
- Store user notification preferences

**Acceptance Criteria:**
- Check-ins sent within 5 minutes of trigger
- User can customize frequency and types
- Opt-out option per check-in type
- Track engagement rate (>40% response rate target)

**Estimated Effort:** 7-10 days
**Dependencies:** P0.3 (task tracking), P1.3 (calendar sync)

---

### P1.3: Calendar Integration
**Why:** Connect journaling to real-world events. Crucial for correlation analysis.

**User Story:**
> "As a user, I want my calendar events to automatically sync so the AI can correlate my mood with specific meetings, deadlines, or activities."

**Features:**
- [ ] Google Calendar OAuth integration
- [ ] Apple Calendar integration (via CalDAV)
- [ ] Outlook Calendar integration
- [ ] Auto-tag entries with calendar events from that day
- [ ] Correlation: "Your mood tends to drop before 1-on-1s with your manager"
- [ ] Event-based journaling prompts

**Privacy:**
- User controls which calendars sync
- Event titles only (not descriptions)
- Encrypted storage
- Can disable correlation analysis

**Technical Notes:**
- Google Calendar API (OAuth 2.0)
- Store events in `calendar_events` table
- Link entries to events via `entry_calendar_event` junction table
- Analyze mood patterns around event types

**Acceptance Criteria:**
- Successfully sync events from at least 1 calendar provider
- Events update daily via background job
- Correlations calculated for event types with >10 occurrences
- User can disconnect calendar anytime

**Estimated Effort:** 5-7 days
**Dependencies:** None

---

### P1.4: Advanced Search & Filtering
**Why:** Users need to find specific entries as history grows.

**User Story:**
> "As a user with 100+ entries, I want to quickly find entries by date, mood, emotion, or specific topics."

**Features:**
- [ ] Full-text search across all entries
- [ ] Filter by date range
- [ ] Filter by mood range (e.g., "Show entries where mood < 5")
- [ ] Filter by emotions (e.g., "Show all anxious entries")
- [ ] Filter by entities (e.g., "Show entries mentioning Sarah")
- [ ] Combined filters
- [ ] Save search queries

**Technical Notes:**
- Use PostgreSQL full-text search or Elasticsearch
- Add indexes: `(user_id, created_at)`, `(user_id, mood_score)`
- Pagination for large result sets

**Acceptance Criteria:**
- Search results return in <500ms
- Supports Boolean operators (AND, OR, NOT)
- Highlights search terms in results
- Mobile-friendly filter UI

**Estimated Effort:** 3-5 days
**Dependencies:** None

---

### P1.5: Text-Based Journaling
**Why:** Not every entry needs voice. Give users flexibility.

**User Story:**
> "As a user, sometimes I want to quickly type a short reflection instead of recording audio."

**Features:**
- [ ] Text editor with markdown support
- [ ] Same AI processing as voice entries
- [ ] Quick entry mode (single prompt + response)
- [ ] Import from other apps (Day One, etc.)

**Technical Notes:**
- Add `entry_type` field: `voice` or `text`
- Skip Whisper, go straight to Claude
- Reuse existing processing pipeline

**Acceptance Criteria:**
- Text entries process in <10 seconds
- Support basic markdown (bold, italic, lists)
- Character count and word count displayed
- Can switch between voice and text mid-entry

**Estimated Effort:** 2-3 days
**Dependencies:** None

---

## 💎 P2 - Growth Features

### P2.1: Therapist Dashboard (B2B Pivot)
**Why:** Opens new revenue stream. Addresses original vision of therapist integration.

**User Story:**
> "As a therapist, I want to view my client's emotional summaries and patterns without accessing their raw journal entries."

**Features:**
- [ ] Therapist account type
- [ ] Client-therapist linking (via invite code)
- [ ] Aggregate dashboard (mood trends, emotion breakdown, key themes)
- [ ] No access to raw entry text (privacy-first)
- [ ] Session prep summaries
- [ ] Progress tracking for therapeutic goals
- [ ] Billing/subscription for therapists

**Privacy Design:**
- Client must explicitly share with specific therapist
- Therapist sees: mood scores, emotion data, entity mentions, AI insights
- Therapist does NOT see: raw transcript, formatted content, audio
- Client can revoke access anytime
- All access logged and auditable

**Pricing:**
- $20-30/month per therapist (unlimited clients)
- or $5/month per client shared

**Technical Notes:**
- Add `therapists` table and `client_therapist_links` table
- Separate dashboard UI for therapists
- Add role-based permissions
- Aggregate queries optimized for performance

**Acceptance Criteria:**
- Therapist can view summary without seeing raw text
- Client controls exactly what data is shared
- Therapist dashboard loads in <2 seconds
- HIPAA compliance considerations documented

**Estimated Effort:** 10-14 days
**Dependencies:** P0.1 (data viz), P0.2 (entity mapping)

---

### P2.2: Habit & Activity Tracking
**Why:** Correlate mood with behaviors (sleep, exercise, diet, etc.)

**User Story:**
> "As a user, I want to log daily habits like sleep hours, exercise, and meals, so I can see how they affect my mood."

**Features:**
- [ ] Quick habit logger (checkboxes + sliders)
- [ ] Common habits: sleep hours, exercise, meals, caffeine, alcohol, medication
- [ ] Custom habit creation
- [ ] Correlation analysis: "Your mood is 15% higher on days you exercise"
- [ ] Habit streak tracking
- [ ] Integrate with Apple Health / Google Fit (auto-import)

**Technical Notes:**
- Add `habits` and `habit_logs` tables
- Daily habit prompt before/after journaling
- Statistical correlation (Pearson or Spearman)
- Health API integration (HealthKit for iOS, Google Fit for Android)

**Acceptance Criteria:**
- User can log habits in <30 seconds
- Correlations shown when statistically significant (p<0.05, n>20)
- Health data sync works for at least 1 platform
- Visualizations clear and actionable

**Estimated Effort:** 7-10 days
**Dependencies:** P0.1 (analytics engine)

---

### P2.3: Group Journaling & Shared Insights
**Why:** Enable accountability partners, couples therapy, support groups.

**User Story:**
> "As a user, I want to share my journal with my partner or accountability group and see our collective patterns."

**Features:**
- [ ] Create shared journal spaces
- [ ] Invite others to shared space
- [ ] Combined analytics dashboard
- [ ] Opt-in: share specific entries or just summary data
- [ ] Couples mode: see how your moods interact
- [ ] Support group mode: anonymized collective trends

**Use Cases:**
- Couples therapy: Track relationship dynamics
- Accountability groups: Goal progress tracking
- Family therapy: Multiple perspectives on shared events

**Privacy:**
- Granular sharing controls (summary only vs full entries)
- Anonymous mode for support groups
- Can leave group and remove data anytime

**Estimated Effort:** 10-14 days
**Dependencies:** P0.1 (analytics), P2.1 (sharing framework)

---

### P2.4: AI-Powered Journaling Prompts
**Why:** Combat writer's block. Increase engagement on slow days.

**User Story:**
> "As a user, when I don't know what to journal about, I want the AI to give me a thoughtful, personalized prompt."

**Features:**
- [ ] Daily prompt based on past patterns
- [ ] Follow-up prompts from previous entries
- [ ] Goal-aligned prompts
- [ ] Themed prompt packs (gratitude, CBT, relationship, career)
- [ ] Community-created prompts
- [ ] Prompt streaks

**Examples:**
```
Pattern-based:
"You mentioned feeling stressed 3 times this week. What's one thing you could
delegate or postpone?"

Follow-up:
"Last Monday you set a goal to be more assertive at work. How did that go?"

Goal-aligned:
"You want to improve sleep. What thoughts are keeping you up at night?"
```

**Technical Notes:**
- Add `prompts` table with tags and categories
- Use Claude to generate dynamic prompts based on user history
- A/B test prompt effectiveness (track completion rate)

**Acceptance Criteria:**
- Personalized prompts generated daily
- >60% completion rate on prompted entries
- User can skip or regenerate prompt
- Prompts feel relevant and thoughtful (user feedback >4/5)

**Estimated Effort:** 3-5 days
**Dependencies:** P1.1 (long-term memory for personalization)

---

### P2.5: Export & Data Portability
**Why:** User owns their data. Required for trust and potentially GDPR compliance.

**User Story:**
> "As a user, I want to export all my journal entries and insights in a portable format."

**Features:**
- [ ] Export to PDF (formatted journal book)
- [ ] Export to JSON (machine-readable)
- [ ] Export to Markdown (human-readable)
- [ ] Export to Day One format (for migration)
- [ ] Include charts and analytics in PDF
- [ ] Email export or download link
- [ ] Scheduled backups (premium)

**Privacy:**
- Encrypted exports
- Password-protected PDFs
- Secure download links that expire

**Technical Notes:**
- Use `WeasyPrint` or `ReportLab` for PDF generation
- Background job for large exports (>500 entries)
- S3 or local storage for export files

**Acceptance Criteria:**
- Export completes for 1000 entries in <2 minutes
- PDF is aesthetically pleasing and readable
- All data types included (entries, goals, habits, analytics)
- User receives notification when export ready

**Estimated Effort:** 5-7 days
**Dependencies:** None

---

## 🔮 P3 - Future Innovation

### P3.1: Voice AI Companion (Conversational Mode)
**Why:** Make journaling feel like talking to a therapist, not a notepad.

**Features:**
- [ ] Real-time conversational AI (voice in, voice out)
- [ ] AI asks follow-up questions during journaling
- [ ] Natural pauses and interruptions
- [ ] Emotional tone matching
- [ ] Multi-turn sessions

**Technical Notes:**
- OpenAI Realtime API or ElevenLabs for voice
- WebSocket for low-latency streaming
- Expensive: ~$0.10-0.20 per 10-minute session

**Estimated Effort:** 14-21 days

---

### P3.2: Predictive Mental Health Alerts
**Why:** Catch early warning signs of depression, anxiety spikes, burnout.

**Features:**
- [ ] ML model trained on longitudinal mood data
- [ ] Detect concerning patterns (e.g., sustained low mood, isolation mentions)
- [ ] Gentle alerts: "We've noticed your mood has been lower than usual..."
- [ ] Crisis resources (hotlines, therapist finder)
- [ ] Optional sharing with trusted contact

**Risks:**
- Ethical concerns (false positives, user dependency)
- Regulatory (medical device classification?)
- Privacy (sensitive predictions)

**Estimated Effort:** 21-30 days
**Dependencies:** Large dataset, medical advisory board

---

### P3.3: Multilingual Support
**Why:** Expand TAM beyond English speakers.

**Features:**
- [ ] Whisper supports 90+ languages
- [ ] Claude multilingual support
- [ ] UI localization (Spanish, French, Mandarin, etc.)
- [ ] Culturally-adapted prompts

**Estimated Effort:** 10-14 days per language

---

### P3.4: Insurance & Clinical Validation
**Why:** Get covered by health insurance as "digital therapeutic."

**Features:**
- [ ] Clinical trials showing efficacy
- [ ] FDA clearance (if needed)
- [ ] Insurance billing codes
- [ ] Prescription pathway

**Estimated Effort:** 12-24 months
**Dependencies:** Clinical partnerships, regulatory expertise

---

## 📋 Implementation Roadmap

### Sprint 1-2 (Weeks 1-4): Core Differentiation
- P0.1: Data Visualization Dashboard
- P0.2: Entity Extraction & Mapping
- P1.5: Text-Based Journaling

**Goal:** Show visual insights and entity correlations. Launch beta.

---

### Sprint 3-4 (Weeks 5-8): Active Growth Loop
- P0.3: Goal-Setting & Action Loop
- P0.4: Challenging Thinking Patterns
- P1.4: Advanced Search & Filtering

**Goal:** Transform from passive to active. Retain users.

---

### Sprint 5-6 (Weeks 9-12): Long-Term Value
- P1.1: Vector Database & Long-Term Memory
- P1.2: Proactive Check-Ins
- P1.3: Calendar Integration

**Goal:** Create compounding value over time. Reduce churn.

---

### Sprint 7+ (Months 4-6): Growth & Revenue
- P2.1: Therapist Dashboard (B2B)
- P2.2: Habit & Activity Tracking
- P2.4: AI-Powered Prompts
- P2.5: Export & Data Portability

**Goal:** Open new revenue streams. Scale.

---

## 🎨 Design Philosophy

### What Makes MindSpeak Different?

1. **Data-Driven, Not Just Emotional**
   - Rosebud/Mindsera: Validating and supportive
   - MindSpeak: Shows you the data, challenges your assumptions

2. **Action-Oriented, Not Just Reflective**
   - Daylio: Track mood passively
   - MindSpeak: Set goals → insights → tasks → check-ins → progress

3. **Connected, Not Isolated**
   - Most apps: Journal in a vacuum
   - MindSpeak: Ties to calendar, goals, therapist, real life

4. **Intelligent Memory, Not Session-Based**
   - Most apps: Each entry analyzed in isolation
   - MindSpeak: Remembers your journey, references past, shows growth

5. **Therapeutic, Not Just Supportive**
   - Most apps: "You're doing great!"
   - MindSpeak: "You said that last time too. What pattern do you notice?"

---

## 📊 Success Metrics

### North Star Metric
**Weekly Active Users with >3 Entries/Month**
- Indicates engagement beyond trial

### Key Metrics by Feature

**P0.1 Data Viz:**
- % users viewing analytics dashboard weekly >60%
- Avg time on analytics page >2 minutes

**P0.2 Entity Mapping:**
- % entries with extracted entities >90%
- % users clicking entity profiles >40%

**P0.3 Goal Loop:**
- % users with active goals >70%
- Task completion rate >50%

**P1.2 Proactive Check-Ins:**
- Response rate to check-ins >40%
- User satisfaction >4/5

**P2.1 Therapist Dashboard:**
- B2B MRR from therapists >$5k within 6 months
- Avg clients per therapist >5

---

## 🔄 Feedback Loops

1. **Weekly user interviews** (5 users)
2. **In-app feedback buttons** on each feature
3. **Usage analytics** (Mixpanel or Amplitude)
4. **A/B testing** on AI tone, prompts, UI
5. **Therapist advisory board** (for P2.1)

---

**Remember:** We're not building another journal app. We're building a **mental health growth partner** that uses data to drive real change.
