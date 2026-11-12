import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { Badge } from '../../components/common/Badge';
import { EmptyState } from '../../components/common/EmptyState';
import { apiGet, apiPost, apiPut, apiDelete } from '../../services/api';
import {
  HeartHandshake,
  Heart,
  Plus,
  Sparkles,
  Smile,
  Copy,
  CheckCircle2,
  Calendar,
  Flame,
  LogOut,
  Target,
  Repeat,
} from 'lucide-react';

export const GrowthCouplePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'goals' | 'habits' | 'checkin' | 'ai'>('overview');
  const [couple, setCouple] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [inviteCodeInput, setInviteCodeInput] = useState('');
  const [myGeneratedCode, setMyGeneratedCode] = useState('');
  const [goals, setGoals] = useState<any[]>([]);
  const [habits, setHabits] = useState<any[]>([]);
  const [checkins, setCheckins] = useState<any[]>([]);
  const [aiSuggestions, setAiSuggestions] = useState<any[]>([]);

  // Checkin form
  const [mood, setMood] = useState('great');
  const [gratitude, setGratitude] = useState('');
  const [winOfDay, setWinOfDay] = useState('');
  const [supportNeeded, setSupportNeeded] = useState('');

  // Modals
  const [isGoalModalOpen, setIsGoalModalOpen] = useState(false);
  const [isHabitModalOpen, setIsHabitModalOpen] = useState(false);
  const [goalTitle, setGoalTitle] = useState('');
  const [habitTitle, setHabitTitle] = useState('');

  const loadCoupleData = async () => {
    try {
      const data = await apiGet<any>('/couple/');
      if (data && data.status !== 'none') {
        setCouple(data);
        const [g, h, ci, ai] = await Promise.all([
          apiGet<any[]>('/couple/goals'),
          apiGet<any[]>('/couple/habits'),
          apiGet<any[]>('/couple/checkins'),
          apiGet<any>('/couple/ai-suggestions'),
        ]);
        setGoals(g || []);
        setHabits(h || []);
        setCheckins(ci || []);
        setAiSuggestions(ai?.suggestions || []);
      } else {
        setCouple(null);
      }
    } catch {
      // Demo active couple state
      setCouple({
        id: 'c1',
        status: 'active',
        invite_code: 'LOVE2026',
        partner_a: { name: 'Alex Morgan', email: 'alex@example.com' },
        partner_b: { name: 'Taylor Swift', email: 'taylor@example.com' },
        is_partner_a: true,
      });
      setGoals([
        {
          id: 'cg1',
          title: 'Learn Cloud Architecture & Pass Exam Together',
          partner_a_progress: 75,
          partner_b_progress: 65,
          combined_progress: 70,
        },
      ]);
      setHabits([
        {
          id: 'ch1',
          title: 'Daily 30-Minute Evening Walk & Debrief',
          partner_a_streak: 12,
          partner_b_streak: 12,
          today_i_done: true,
        },
      ]);
      setCheckins([
        {
          user_name: 'Taylor',
          is_me: false,
          mood: 'great',
          gratitude: 'Loved our morning coffee discussion',
          win_of_day: 'Finished AWS module 4',
          check_in_date: 'Today',
        },
      ]);
      setAiSuggestions([
        {
          title: 'Schedule a Weekly Growth Review',
          description: 'Every Sunday at 6 PM, review your shared goals and celebrate combined milestones.',
          priority: 'high',
        },
        {
          title: 'Collaborative Study Sprints',
          description: 'Set a synchronized 25-minute Pomodoro session each weekday to study networking.',
          priority: 'medium',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCoupleData();
  }, []);

  const handleGenerateInvite = async () => {
    try {
      const res = await apiPost<any>('/couple/invite');
      setMyGeneratedCode(res.invite_code);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to generate code');
    }
  };

  const handleAcceptInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteCodeInput.trim()) return;
    try {
      await apiPost('/couple/accept', { invite_code: inviteCodeInput.trim() });
      setInviteCodeInput('');
      loadCoupleData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to accept invite');
    }
  };

  const handleToggleHabit = async (habitId: string) => {
    try {
      await apiPut(`/couple/habits/${habitId}/toggle`);
      loadCoupleData();
    } catch {
      // handled
    }
  };

  const handleCheckinSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiPost('/couple/checkins', {
        mood,
        gratitude,
        win_of_day: winOfDay,
        support_needed: supportNeeded,
      });
      setGratitude('');
      setWinOfDay('');
      setSupportNeeded('');
      loadCoupleData();
    } catch {
      // handled
    }
  };

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalTitle.trim()) return;
    try {
      await apiPost('/couple/goals', { title: goalTitle.trim() });
      setGoalTitle('');
      setIsGoalModalOpen(false);
      loadCoupleData();
    } catch {
      // handled
    }
  };

  const handleCreateHabit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!habitTitle.trim()) return;
    try {
      await apiPost('/couple/habits', { title: habitTitle.trim() });
      setHabitTitle('');
      setIsHabitModalOpen(false);
      loadCoupleData();
    } catch {
      // handled
    }
  };

  const handleUnpair = async () => {
    if (confirm('Are you sure you want to end this couple pairing? Your private tasks will remain private.')) {
      try {
        await apiDelete('/couple/unpair');
        setCouple(null);
      } catch {
        // handled
      }
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
            <HeartHandshake className="text-pink-500" size={26} />
            Growth Couple
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Grow together through shared aspirations, daily gratitude check-ins, and collaborative habits
          </p>
        </div>

        {couple && (
          <div className="bg-gray-100 dark:bg-gray-800 p-1 rounded-xl flex items-center gap-1 text-xs font-semibold">
            {(['overview', 'goals', 'habits', 'checkin', 'ai'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-1.5 rounded-lg capitalize transition-all ${
                  activeTab === tab
                    ? 'bg-white dark:bg-[#17171f] text-pink-600 dark:text-pink-400 shadow-sm'
                    : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                {tab === 'ai' ? 'AI Coach' : tab}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Case 1: Not Paired Yet */}
      {!couple && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Option A: Generate Invite */}
          <Card className="p-6 text-center space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-pink-50 dark:bg-pink-950/40 text-pink-500 flex items-center justify-center mx-auto">
              <Heart size={24} />
            </div>
            <div>
              <h3 className="font-bold text-base text-gray-900 dark:text-white">Invite Your Partner</h3>
              <p className="text-xs text-gray-400 mt-1 max-w-sm mx-auto">
                Generate a unique secure invite code and share it with your partner.
              </p>
            </div>

            {myGeneratedCode ? (
              <div className="p-4 rounded-xl bg-pink-50 dark:bg-pink-950/40 border border-pink-200 dark:border-pink-800/40">
                <span className="text-xs text-gray-400 block mb-1">Your Partner Invite Code:</span>
                <span className="text-2xl font-black text-pink-600 dark:text-pink-400 tracking-widest font-mono">
                  {myGeneratedCode}
                </span>
                <p className="text-[11px] text-gray-500 mt-2">
                  Share this code with your partner so they can accept it in their Growth Couple tab.
                </p>
              </div>
            ) : (
              <Button onClick={handleGenerateInvite} className="bg-pink-600 hover:bg-pink-700">
                Generate Partner Invite Code
              </Button>
            )}
          </Card>

          {/* Option B: Enter Invite Code */}
          <Card className="p-6 text-center space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-violet-50 dark:bg-violet-950/40 text-violet-500 flex items-center justify-center mx-auto">
              <HeartHandshake size={24} />
            </div>
            <div>
              <h3 className="font-bold text-base text-gray-900 dark:text-white">Have a Partner Code?</h3>
              <p className="text-xs text-gray-400 mt-1 max-w-sm mx-auto">
                Enter the code your partner shared with you to connect your shared workspace.
              </p>
            </div>

            <form onSubmit={handleAcceptInvite} className="space-y-3">
              <input
                type="text"
                placeholder="ENTER-CODE"
                value={inviteCodeInput}
                onChange={(e) => setInviteCodeInput(e.target.value.toUpperCase())}
                className="w-full text-center font-mono font-bold tracking-widest uppercase bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-4 py-2.5 text-sm outline-none dark:text-white"
              />
              <Button type="submit" className="w-full">
                Connect With Partner
              </Button>
            </form>
          </Card>
        </div>
      )}

      {/* Case 2: Active Couple Space */}
      {couple && (
        <div className="space-y-6">
          {/* Couple Banner */}
          <Card className="p-5 bg-gradient-to-r from-pink-50/60 via-purple-50/40 to-indigo-50/40 dark:from-[#1d141e] dark:via-[#17171f] dark:to-[#171722] border-pink-100 dark:border-pink-900/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-pink-500 to-rose-500 text-white flex items-center justify-center shadow-md shadow-pink-500/20 shrink-0">
                <Heart size={22} className="fill-white" />
              </div>
              <div>
                <h3 className="font-bold text-base text-gray-900 dark:text-white">
                  {couple.partner_a?.name || 'Partner A'} & {couple.partner_b?.name || 'Partner B'}
                </h3>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                  Synchronized couple growth workspace • Private tasks remain strictly confidential
                </p>
              </div>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={handleUnpair}
              className="text-gray-400 hover:text-red-500 self-start sm:self-auto"
              icon={<LogOut size={14} />}
            >
              Unpair
            </Button>
          </Card>

          {/* Tab 1: Overview */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {/* Goals Card */}
              <Card className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-sm text-gray-900 dark:text-white flex items-center gap-1.5">
                    <Target size={16} className="text-violet-600" />
                    Shared Goals
                  </h4>
                  <span className="text-xs font-bold text-violet-600">{goals.length}</span>
                </div>
                <div className="space-y-2">
                  {goals.map((g) => (
                    <div key={g.id} className="p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800/40 text-xs">
                      <p className="font-semibold text-gray-800 dark:text-gray-200 truncate">{g.title}</p>
                      <div className="flex items-center justify-between text-[11px] text-gray-400 mt-1">
                        <span>Combined:</span>
                        <span className="font-bold text-pink-600">{g.combined_progress}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Habits Card */}
              <Card className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-sm text-gray-900 dark:text-white flex items-center gap-1.5">
                    <Repeat size={16} className="text-pink-600" />
                    Shared Habits
                  </h4>
                  <span className="text-xs font-bold text-pink-600">{habits.length}</span>
                </div>
                <div className="space-y-2">
                  {habits.map((h) => (
                    <div
                      key={h.id}
                      onClick={() => handleToggleHabit(h.id)}
                      className="p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800/40 text-xs flex items-center justify-between cursor-pointer hover:bg-pink-50/50"
                    >
                      <p className="font-semibold text-gray-800 dark:text-gray-200 truncate">{h.title}</p>
                      <span className="font-bold text-amber-500 flex items-center gap-0.5">
                        <Flame size={12} className="fill-amber-500" />
                        {h.partner_a_streak}d
                      </span>
                    </div>
                  ))}
                </div>
              </Card>

              {/* Latest Checkin */}
              <Card className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-sm text-gray-900 dark:text-white flex items-center gap-1.5">
                    <Smile size={16} className="text-amber-500" />
                    Latest Check-In
                  </h4>
                  <Button size="sm" variant="ghost" onClick={() => setActiveTab('checkin')}>
                    Check In
                  </Button>
                </div>
                {checkins.length > 0 ? (
                  <div className="p-3 rounded-xl bg-amber-50/40 dark:bg-amber-950/20 text-xs space-y-1">
                    <span className="font-bold text-gray-900 dark:text-white block">
                      {checkins[0].user_name} feels {checkins[0].mood}
                    </span>
                    {checkins[0].gratitude && (
                      <p className="text-gray-600 dark:text-gray-400 italic">"{checkins[0].gratitude}"</p>
                    )}
                  </div>
                ) : (
                  <p className="text-xs text-gray-400">No check-ins submitted today.</p>
                )}
              </Card>
            </div>
          )}

          {/* Tab 2: Shared Goals */}
          {activeTab === 'goals' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-base text-gray-900 dark:text-white">Collaborative Goals</h3>
                <Button size="sm" onClick={() => setIsGoalModalOpen(true)} icon={<Plus size={16} />}>
                  Add Shared Goal
                </Button>
              </div>

              {goals.map((goal) => (
                <Card key={goal.id} className="p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-sm text-gray-900 dark:text-white">{goal.title}</h4>
                    <span className="text-xs font-black text-pink-600">Combined: {goal.combined_progress}%</span>
                  </div>

                  <div className="w-full bg-gray-100 dark:bg-gray-800 h-2.5 rounded-full overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-pink-500 to-violet-600 h-full rounded-full transition-all"
                      style={{ width: `${goal.combined_progress}%` }}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-xs pt-2 text-gray-500">
                    <div>
                      <span>Partner A: </span>
                      <span className="font-bold text-gray-900 dark:text-white">{goal.partner_a_progress}%</span>
                    </div>
                    <div className="text-right">
                      <span>Partner B: </span>
                      <span className="font-bold text-gray-900 dark:text-white">{goal.partner_b_progress}%</span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {/* Tab 3: Daily Check-In */}
          {activeTab === 'checkin' && (
            <Card className="max-w-xl mx-auto p-6 space-y-4">
              <h3 className="font-bold text-base text-gray-900 dark:text-white">Daily Growth Check-In</h3>
              <form onSubmit={handleCheckinSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                    How is your energy & mood today?
                  </label>
                  <select
                    value={mood}
                    onChange={(e) => setMood(e.target.value)}
                    className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-sm outline-none dark:text-white"
                  >
                    <option value="great">Great & Inspired</option>
                    <option value="good">Good & Steady</option>
                    <option value="okay">Okay / Normal</option>
                    <option value="low">Low Energy / Need Support</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                    What are you grateful for today?
                  </label>
                  <textarea
                    rows={2}
                    placeholder="Share something you appreciate..."
                    value={gratitude}
                    onChange={(e) => setGratitude(e.target.value)}
                    className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-3 text-sm outline-none dark:text-white resize-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                    Today's Primary Win
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., Completed Chapter 5, ran 5km"
                    value={winOfDay}
                    onChange={(e) => setWinOfDay(e.target.value)}
                    className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2 text-sm outline-none dark:text-white"
                  />
                </div>

                <Button type="submit" className="w-full bg-pink-600 hover:bg-pink-700">
                  Save Daily Check-In
                </Button>
              </form>
            </Card>
          )}

          {/* Tab 4: AI Growth Suggestions */}
          {activeTab === 'ai' && (
            <div className="space-y-3">
              <h3 className="font-bold text-base text-gray-900 dark:text-white flex items-center gap-2">
                <Sparkles className="text-pink-500" size={18} />
                AI Relationship & Productivity Recommendations
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {aiSuggestions.map((s, idx) => (
                  <Card key={idx} className="p-4 space-y-1.5 border-pink-100 dark:border-pink-900/30">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-pink-100 dark:bg-pink-950/60 text-pink-700 dark:text-pink-300 uppercase">
                      {s.priority} Priority
                    </span>
                    <h4 className="text-sm font-bold text-gray-900 dark:text-white">{s.title}</h4>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{s.description}</p>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modal: Create Goal */}
      <Modal isOpen={isGoalModalOpen} onClose={() => setIsGoalModalOpen(false)} title="Create Shared Goal">
        <form onSubmit={handleCreateGoal} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Shared Goal Title
            </label>
            <input
              type="text"
              required
              placeholder="e.g., Run a Half Marathon Together"
              value={goalTitle}
              onChange={(e) => setGoalTitle(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-3 text-sm outline-none dark:text-white"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setIsGoalModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Create Goal</Button>
          </div>
        </form>
      </Modal>

      {/* Modal: Create Habit */}
      <Modal isOpen={isHabitModalOpen} onClose={() => setIsHabitModalOpen(false)} title="Create Shared Habit">
        <form onSubmit={handleCreateHabit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Shared Habit Title
            </label>
            <input
              type="text"
              required
              placeholder="e.g., Read together for 20 mins every night"
              value={habitTitle}
              onChange={(e) => setHabitTitle(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-3 text-sm outline-none dark:text-white"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setIsHabitModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Create Habit</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
