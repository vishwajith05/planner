import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { EmptyState } from '../../components/common/EmptyState';
import { apiGet, apiPost, apiPut } from '../../services/api';
import {
  Users2,
  Search,
  UserPlus,
  Check,
  X,
  Trophy,
  Flame,
  Send,
  Timer,
  Activity,
  Sparkles,
} from 'lucide-react';

interface FriendItem {
  id: string;
  email: string;
  full_name?: string;
  bio?: string;
  friendship_id: string;
}

interface PendingReq {
  friendship_id: string;
  requester_id: string;
  requester_email: string;
  requester_name?: string;
  sent_at: string;
}

export const FriendGrowthPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'friends' | 'challenges' | 'feed' | 'focus'>('friends');
  const [friends, setFriends] = useState<FriendItem[]>([]);
  const [pendingRequests, setPendingRequests] = useState<PendingReq[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Array<{ id: string; email: string; full_name?: string }>>([]);
  const [challenges, setChallenges] = useState<any[]>([]);
  const [activityFeed, setActivityFeed] = useState<any[]>([]);

  // Modals
  const [isChallengeModalOpen, setIsChallengeModalOpen] = useState(false);
  const [isEncourageModalOpen, setIsEncourageModalOpen] = useState(false);
  const [selectedFriend, setSelectedFriend] = useState<FriendItem | null>(null);
  const [encourageMsg, setEncourageMsg] = useState('');

  // Challenge form
  const [challengeTitle, setChallengeTitle] = useState('');
  const [challengeDesc, setChallengeDesc] = useState('');
  const [challengeDailyTarget, setChallengeDailyTarget] = useState('');

  const loadData = async () => {
    try {
      const [fData, pData, cData, feedData] = await Promise.all([
        apiGet<FriendItem[]>('/friends/'),
        apiGet<PendingReq[]>('/friends/requests/pending'),
        apiGet<any[]>('/friends/challenges'),
        apiGet<any[]>('/friends/feed'),
      ]);
      setFriends(fData || []);
      setPendingRequests(pData || []);
      setChallenges(cData || []);
      setActivityFeed(feedData || []);
    } catch {
      // Demo state
      setFriends([
        { id: 'f1', email: 'sarah.engineer@example.com', full_name: 'Sarah Chen', bio: 'Full-stack & AI dev', friendship_id: 'fs1' },
        { id: 'f2', email: 'marcus.cyber@example.com', full_name: 'Marcus Vance', bio: 'Cybersecurity Analyst', friendship_id: 'fs2' },
      ]);
      setChallenges([
        {
          id: 'c1',
          title: '30-Day Cybersecurity & LeetCode Sprint',
          description: 'Daily labs, 1 algorithm problem, and weekly architecture teardown',
          duration_days: '30',
          my_progress: '35',
          participants: [
            { user_id: 'me', name: 'You', progress_percent: '35', days_completed: '11' },
            { user_id: 'f1', name: 'Sarah Chen', progress_percent: '45', days_completed: '14' },
          ],
        },
      ]);
      setActivityFeed([
        {
          user_name: 'Sarah Chen',
          challenge_title: '30-Day Cybersecurity & LeetCode Sprint',
          progress: '45%',
          timestamp: '2 hours ago',
        },
      ]);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.length < 2) return;
    try {
      const res = await apiGet<any[]>(`/friends/search?q=${encodeURIComponent(searchQuery)}`);
      setSearchResults(res || []);
    } catch {
      setSearchResults([]);
    }
  };

  const sendRequest = async (email: string) => {
    try {
      await apiPost('/friends/request', { addressee_email: email });
      setSearchQuery('');
      setSearchResults([]);
      loadData();
    } catch {
      // handled
    }
  };

  const respondRequest = async (friendshipId: string, action: 'accept' | 'reject') => {
    try {
      await apiPut(`/friends/request/${friendshipId}/${action}`);
      loadData();
    } catch {
      // handled
    }
  };

  const handleSendEncouragement = async () => {
    if (!selectedFriend || !encourageMsg.trim()) return;
    try {
      await apiPost('/friends/encourage', {
        recipient_id: selectedFriend.id,
        message: encourageMsg.trim(),
      });
      setEncourageMsg('');
      setIsEncourageModalOpen(false);
    } catch {
      // handled
    }
  };

  const handleCreateChallenge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!challengeTitle.trim()) return;
    try {
      await apiPost('/friends/challenges', {
        title: challengeTitle.trim(),
        description: challengeDesc.trim() || undefined,
        daily_target: challengeDailyTarget.trim() || undefined,
        duration_days: 30,
        friend_ids: friends.map((f) => f.id),
      });
      setChallengeTitle('');
      setChallengeDesc('');
      setChallengeDailyTarget('');
      setIsChallengeModalOpen(false);
      loadData();
    } catch {
      // handled
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
            <Users2 className="text-violet-600" size={26} />
            Friend Growth & Accountability
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Achieve ambitious milestones together with peer motivation, shared challenges, and strict privacy
          </p>
        </div>

        {/* Tab switch */}
        <div className="bg-gray-100 dark:bg-gray-800 p-1 rounded-xl flex items-center gap-1 text-xs font-semibold">
          {(['friends', 'challenges', 'feed'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1.5 rounded-lg capitalize transition-all ${
                activeTab === tab
                  ? 'bg-white dark:bg-[#17171f] text-violet-600 dark:text-violet-400 shadow-sm'
                  : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Tab 1: Friends List & Search */}
      {activeTab === 'friends' && (
        <div className="space-y-6">
          {/* User Search & Discovery Bar */}
          <Card className="p-4">
            <form onSubmit={handleSearch} className="flex gap-2">
              <div className="relative flex-1">
                <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Discover users by email or full name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl pl-10 pr-4 py-2 text-sm outline-none dark:text-white"
                />
              </div>
              <Button type="submit" size="sm">
                Search
              </Button>
            </form>

            {searchResults.length > 0 && (
              <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800 space-y-2">
                <span className="text-xs font-bold text-gray-400 uppercase">Search Results</span>
                {searchResults.map((user) => (
                  <div
                    key={user.id}
                    className="flex items-center justify-between p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800/40 text-xs"
                  >
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white">{user.full_name || user.email}</p>
                      <p className="text-gray-400 text-[10px]">{user.email}</p>
                    </div>
                    <Button size="sm" onClick={() => sendRequest(user.email)} icon={<UserPlus size={14} />}>
                      Add Friend
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Pending Incoming Requests */}
          {pendingRequests.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-gray-900 dark:text-white">
                Pending Requests ({pendingRequests.length})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {pendingRequests.map((req) => (
                  <Card key={req.friendship_id} className="p-3.5 flex items-center justify-between">
                    <div>
                      <p className="text-xs font-bold text-gray-900 dark:text-white">
                        {req.requester_name || req.requester_email}
                      </p>
                      <p className="text-[10px] text-gray-400">{req.requester_email}</p>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Button
                        size="sm"
                        onClick={() => respondRequest(req.friendship_id, 'accept')}
                        icon={<Check size={14} />}
                      >
                        Accept
                      </Button>
                      <button
                        onClick={() => respondRequest(req.friendship_id, 'reject')}
                        className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-gray-100 dark:hover:bg-gray-800"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Friends List */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-gray-900 dark:text-white">
              My Growth Friends ({friends.length})
            </h3>
            {friends.length === 0 ? (
              <EmptyState
                icon={<Users2 size={28} />}
                title="No friends added yet"
                description="Search for your colleagues or study partners above to begin collaborating."
              />
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {friends.map((f) => (
                  <Card key={f.id} className="p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-violet-600 text-white font-bold text-sm flex items-center justify-center">
                        {f.full_name ? f.full_name[0] : f.email[0].toUpperCase()}
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-gray-900 dark:text-white">{f.full_name || f.email}</h4>
                        <p className="text-xs text-gray-400">{f.bio || f.email}</p>
                      </div>
                    </div>

                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => {
                        setSelectedFriend(f);
                        setIsEncourageModalOpen(true);
                      }}
                      icon={<Send size={14} />}
                    >
                      Cheer
                    </Button>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Shared Challenges */}
      {activeTab === 'challenges' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-gray-900 dark:text-white">Active Shared Challenges</h3>
            <Button onClick={() => setIsChallengeModalOpen(true)} size="sm" icon={<Trophy size={16} />}>
              Create Challenge
            </Button>
          </div>

          {challenges.map((ch) => (
            <Card key={ch.id} className="p-5 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-base font-bold text-gray-900 dark:text-white">{ch.title}</h4>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{ch.description}</p>
                </div>
                <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300">
                  {ch.duration_days} Days
                </span>
              </div>

              {/* Participants Progress Bars */}
              <div className="space-y-2 pt-2 border-t border-gray-100 dark:border-gray-800">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block">
                  Peer Leaderboard & Progress
                </span>
                {ch.participants &&
                  ch.participants.map((p: any, idx: number) => (
                    <div key={idx} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-gray-800 dark:text-gray-200">{p.name}</span>
                        <span className="font-bold text-violet-600">{p.progress_percent}%</span>
                      </div>
                      <div className="w-full bg-gray-100 dark:bg-gray-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-violet-600 h-full rounded-full transition-all duration-500"
                          style={{ width: `${p.progress_percent}%` }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Tab 3: Friends Activity Feed */}
      {activeTab === 'feed' && (
        <div className="space-y-3">
          <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Activity size={18} className="text-violet-600" />
            Friends Activity Stream
          </h3>
          {activityFeed.map((item, idx) => (
            <Card key={idx} className="p-4 flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-pink-100 dark:bg-pink-950/50 text-pink-600 flex items-center justify-center shrink-0">
                <Flame size={16} />
              </div>
              <div className="flex-1 text-xs">
                <p className="text-gray-800 dark:text-gray-200">
                  <span className="font-bold">{item.user_name}</span> completed target in{' '}
                  <span className="font-semibold text-violet-600 dark:text-violet-400">
                    {item.challenge_title}
                  </span>{' '}
                  ({item.progress})
                </p>
                <span className="text-[10px] text-gray-400 mt-0.5 block">{item.timestamp}</span>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Modal: Create Challenge */}
      <Modal isOpen={isChallengeModalOpen} onClose={() => setIsChallengeModalOpen(false)} title="Create Shared Challenge">
        <form onSubmit={handleCreateChallenge} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Challenge Title *
            </label>
            <input
              type="text"
              required
              placeholder="e.g., 30-Day Cybersecurity Bootcamp"
              value={challengeTitle}
              onChange={(e) => setChallengeTitle(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2.5 text-sm outline-none dark:text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Daily Target
            </label>
            <input
              type="text"
              placeholder="e.g., Study 1 hour + complete 1 lab"
              value={challengeDailyTarget}
              onChange={(e) => setChallengeDailyTarget(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2 text-xs outline-none dark:text-white"
            />
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-gray-100 dark:border-gray-800">
            <Button type="button" variant="secondary" onClick={() => setIsChallengeModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Start Challenge</Button>
          </div>
        </form>
      </Modal>

      {/* Modal: Send Encouragement */}
      <Modal
        isOpen={isEncourageModalOpen}
        onClose={() => setIsEncourageModalOpen(false)}
        title={`Send Cheer to ${selectedFriend?.full_name || 'Friend'}`}
      >
        <div className="space-y-4">
          <textarea
            rows={3}
            placeholder="You got this! Keep smashing your goals today! 🚀"
            value={encourageMsg}
            onChange={(e) => setEncourageMsg(e.target.value)}
            className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-3 text-sm outline-none dark:text-white resize-none"
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setIsEncourageModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSendEncouragement} icon={<Send size={14} />}>
              Send Cheer
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
