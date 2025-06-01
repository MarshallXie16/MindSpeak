import React, { useState, useEffect } from 'react';
import { Save, Trash2, Plus, User, Settings, Target, Bell, Palette } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { userAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface UserProfile {
  id: number;
  email: string;
  username: string;
  display_name: string;
  timezone: string;
  locale: string;
  subscription_tier: string;
  created_at: string;
  is_verified: boolean;
}

interface UserPreferences {
  custom_ai_instructions: string | null;
  goals: Array<{ id: number; text: string; created_at: string }>;
  reminder_enabled: boolean;
  reminder_time: string | null;
  reminder_days: string[];
  theme: string;
  current_streak: number;
  longest_streak: number;
}

interface Goal {
  id: number;
  text: string;
  created_at: string;
}

export function Profile() {
  // @ts-ignore
  const { user: authUser, setUser } = useAuth();
  const [activeTab, setActiveTab] = useState<'profile' | 'preferences' | 'goals' | 'reminders'>('profile');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  
  // Profile state
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileForm, setProfileForm] = useState({
    display_name: '',
    timezone: '',
    locale: ''
  });

  // Preferences state
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [preferencesForm, setPreferencesForm] = useState({
    custom_ai_instructions: '',
    theme: 'light',
    reminder_enabled: false,
    reminder_time: '',
    reminder_days: [] as string[]
  });

  // Goals state
  const [goals, setGoals] = useState<Goal[]>([]);
  const [newGoal, setNewGoal] = useState('');

  useEffect(() => {
    loadProfileData();
  }, []);

  const loadProfileData = async () => {
    try {
      setIsLoading(true);
      const [profileResponse, preferencesResponse] = await Promise.all([
        userAPI.getProfile(),
        userAPI.getPreferences()
      ]);

      const profileData = profileResponse.data.user;
      const preferencesData = preferencesResponse.data.preferences;

      setProfile(profileData);
      setProfileForm({
        display_name: profileData.display_name || '',
        timezone: profileData.timezone || 'UTC',
        locale: profileData.locale || 'en'
      });

      setPreferences(preferencesData);
      setPreferencesForm({
        custom_ai_instructions: preferencesData.custom_ai_instructions || '',
        theme: preferencesData.theme || 'light',
        reminder_enabled: preferencesData.reminder_enabled || false,
        reminder_time: preferencesData.reminder_time || '',
        reminder_days: preferencesData.reminder_days || []
      });

      setGoals(preferencesData.goals || []);
    } catch (error) {
      console.error('Error loading profile data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveProfile = async () => {
    try {
      setIsSaving(true);
      const response = await userAPI.updateProfile(profileForm);
      setProfile(response.data.user);
      
      // Update auth context
      if (setUser && authUser) {
        setUser({ ...authUser, display_name: response.data.user.display_name });
      }
    } catch (error) {
      console.error('Error saving profile:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const savePreferences = async () => {
    try {
      setIsSaving(true);
      const response = await userAPI.updatePreferences(preferencesForm);
      setPreferences(response.data.preferences);
    } catch (error) {
      console.error('Error saving preferences:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const addGoal = async () => {
    if (!newGoal.trim()) return;

    try {
      const response = await userAPI.addGoal(newGoal.trim());
      setGoals(response.data.goals);
      setNewGoal('');
    } catch (error) {
      console.error('Error adding goal:', error);
    }
  };

  const removeGoal = async (goalId: number) => {
    try {
      const response = await userAPI.removeGoal(goalId);
      setGoals(response.data.goals);
    } catch (error) {
      console.error('Error removing goal:', error);
    }
  };

  const toggleReminderDay = (day: string) => {
    setPreferencesForm(prev => ({
      ...prev,
      reminder_days: prev.reminder_days.includes(day)
        ? prev.reminder_days.filter(d => d !== day)
        : [...prev.reminder_days, day]
    }));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Profile & Settings</h1>
        <p className="text-muted-foreground">
          Manage your account, preferences, and journaling goals
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-muted rounded-lg p-1">
        {[
          { id: 'profile', label: 'Profile', icon: User },
          { id: 'preferences', label: 'Preferences', icon: Settings },
          { id: 'goals', label: 'Goals', icon: Target },
          { id: 'reminders', label: 'Reminders', icon: Bell }
        ].map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors flex-1 justify-center ${
                activeTab === tab.id
                  ? 'bg-background text-foreground shadow-sm'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Icon className="h-4 w-4" />
              <span className="font-medium">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="bg-card rounded-lg border p-6">
        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Profile Information</h2>
              <div className="grid gap-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Email</label>
                    <Input value={profile?.email || ''} disabled />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Username</label>
                    <Input value={profile?.username || ''} disabled />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Display Name</label>
                  <Input
                    value={profileForm.display_name}
                    onChange={(e) => setProfileForm(prev => ({ ...prev, display_name: e.target.value }))}
                    placeholder="How should we address you?"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Timezone</label>
                    <select
                      value={profileForm.timezone}
                      onChange={(e) => setProfileForm(prev => ({ ...prev, timezone: e.target.value }))}
                      className="w-full px-3 py-2 border border-border rounded-md"
                    >
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">Eastern Time</option>
                      <option value="America/Chicago">Central Time</option>
                      <option value="America/Denver">Mountain Time</option>
                      <option value="America/Los_Angeles">Pacific Time</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Language</label>
                    <select
                      value={profileForm.locale}
                      onChange={(e) => setProfileForm(prev => ({ ...prev, locale: e.target.value }))}
                      className="w-full px-3 py-2 border border-border rounded-md"
                    >
                      <option value="en">English</option>
                      <option value="es">Español</option>
                      <option value="fr">Français</option>
                      <option value="zh">中文</option>
                    </select>
                  </div>
                </div>

                <div className="bg-muted/50 p-4 rounded-lg">
                  <p className="text-sm text-muted-foreground">
                    <strong>Account created:</strong> {profile?.created_at ? formatDate(profile.created_at) : 'Unknown'}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    <strong>Subscription:</strong> {profile?.subscription_tier || 'Free'}
                  </p>
                </div>
              </div>

              <Button
                onClick={saveProfile}
                disabled={isSaving}
                className="flex items-center space-x-2 mt-4"
              >
                <Save className="h-4 w-4" />
                <span>{isSaving ? 'Saving...' : 'Save Profile'}</span>
              </Button>
            </div>
          </div>
        )}

        {/* Preferences Tab */}
        {activeTab === 'preferences' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">AI & Interface Preferences</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Custom AI Instructions</label>
                  <Textarea
                    value={preferencesForm.custom_ai_instructions}
                    onChange={(e) => setPreferencesForm(prev => ({ ...prev, custom_ai_instructions: e.target.value }))}
                    placeholder="Tell the AI how you'd like it to process your journal entries..."
                    rows={4}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    These instructions help customize how AI analyzes your journal entries
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Theme</label>
                  <div className="flex space-x-3">
                    {[
                      { value: 'light', label: 'Light', icon: '☀️' },
                      { value: 'dark', label: 'Dark', icon: '🌙' },
                      { value: 'auto', label: 'Auto', icon: '⚡' }
                    ].map(theme => (
                      <button
                        key={theme.value}
                        onClick={() => setPreferencesForm(prev => ({ ...prev, theme: theme.value }))}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-md border transition-colors ${
                          preferencesForm.theme === theme.value
                            ? 'border-primary bg-primary/5'
                            : 'border-border hover:bg-accent'
                        }`}
                      >
                        <span>{theme.icon}</span>
                        <span className="text-sm">{theme.label}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {preferences && (
                  <div className="bg-muted/50 p-4 rounded-lg">
                    <h3 className="font-medium mb-2">Streak Progress</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Current Streak:</span>
                        <span className="ml-2 font-semibold">{preferences.current_streak} days</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Longest Streak:</span>
                        <span className="ml-2 font-semibold">{preferences.longest_streak} days</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <Button
                onClick={savePreferences}
                disabled={isSaving}
                className="flex items-center space-x-2 mt-4"
              >
                <Save className="h-4 w-4" />
                <span>{isSaving ? 'Saving...' : 'Save Preferences'}</span>
              </Button>
            </div>
          </div>
        )}

        {/* Goals Tab */}
        {activeTab === 'goals' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Personal Goals</h2>
              <p className="text-muted-foreground mb-4">
                Set goals that will help the AI provide more personalized insights
              </p>

              {/* Add New Goal */}
              <div className="flex space-x-2 mb-6">
                <Input
                  value={newGoal}
                  onChange={(e) => setNewGoal(e.target.value)}
                  placeholder="Enter a new goal..."
                  onKeyPress={(e) => e.key === 'Enter' && addGoal()}
                />
                <Button onClick={addGoal} disabled={!newGoal.trim()}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>

              {/* Goals List */}
              <div className="space-y-3">
                {goals.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Target className="h-8 w-8 mx-auto mb-2" />
                    <p>No goals set yet. Add your first goal above!</p>
                  </div>
                ) : (
                  goals.map((goal) => (
                    <div
                      key={goal.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div>
                        <p className="font-medium">{goal.text}</p>
                        <p className="text-xs text-muted-foreground">
                          Added {formatDate(goal.created_at)}
                        </p>
                      </div>
                      <Button
                        onClick={() => removeGoal(goal.id)}
                        variant="ghost"
                        size="sm"
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* Reminders Tab */}
        {activeTab === 'reminders' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">Journal Reminders</h2>
              
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="reminder-enabled"
                    checked={preferencesForm.reminder_enabled}
                    onChange={(e) => setPreferencesForm(prev => ({ 
                      ...prev, 
                      reminder_enabled: e.target.checked 
                    }))}
                    className="rounded"
                  />
                  <label htmlFor="reminder-enabled" className="text-sm font-medium">
                    Enable daily journal reminders
                  </label>
                </div>

                {preferencesForm.reminder_enabled && (
                  <>
                    <div>
                      <label className="block text-sm font-medium mb-2">Reminder Time</label>
                      <Input
                        type="time"
                        value={preferencesForm.reminder_time}
                        onChange={(e) => setPreferencesForm(prev => ({ 
                          ...prev, 
                          reminder_time: e.target.value 
                        }))}
                        className="w-40"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Reminder Days</label>
                      <div className="flex flex-wrap gap-2">
                        {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map(day => (
                          <button
                            key={day}
                            onClick={() => toggleReminderDay(day)}
                            className={`px-3 py-1 rounded-md text-sm transition-colors ${
                              preferencesForm.reminder_days.includes(day)
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-muted text-muted-foreground hover:bg-accent'
                            }`}
                          >
                            {day.charAt(0).toUpperCase() + day.slice(1, 3)}
                          </button>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </div>

              <Button
                onClick={savePreferences}
                disabled={isSaving}
                className="flex items-center space-x-2 mt-4"
              >
                <Save className="h-4 w-4" />
                <span>{isSaving ? 'Saving...' : 'Save Reminder Settings'}</span>
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}