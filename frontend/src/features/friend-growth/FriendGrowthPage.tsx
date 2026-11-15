import React, { useEffect, useState, useRef } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { EmptyState } from '../../components/common/EmptyState';
import { apiGet, apiPost, apiPut, apiDelete } from '../../services/api';
import { useAuthStore } from '../../store/authStore';
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
  MessageSquare,
  Shield,
  Target,
  RefreshCw,
  Bell,
  Heart,
  TrendingUp,
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

interface ChatMessage {
  id: string;
  sender_id: string;
  sender_name: string;
  recipient_id: string;
  recipient_name?: string;
  content: string;
  is_read: boolean;
  created_at: string;
}

interface Conversation {
  friend_id: string;
  friend_name: string;
  friend_email: string;
  last_message?: string;
  last_message_at?: string;
  last_message_sender_id?: string;
  unread_count: number;
}

export const FriendGrowthPage: React.FC = () => {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'overview' | 'messages' | 'friends' | 'challenges' | 'feed'>('overview');

  // Stats & Overview
  const [overviewStats, setOverviewStats] = useState({
    total_friends: 0,
    active_friends: 0,
    pending_requests: 0,
    active_challenges: 0,
    total_messages: 0,
  });
  const [aiCoach, setAiCoach] = useState<{
    recommendation: string;
    inactive_members: Array<{ name: string; challenge: string; progress: number }>;
    suggested_actions: string[];
  } | null>(null);

  // Friends & Requests
  const [friends, setFriends] = useState<FriendItem[]>([]);
  const [pendingRequests, setPendingRequests] = useState<PendingReq[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Array<{ id: string; email: string; full_name?: string }>>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Challenges & Feed
  const [challenges, setChallenges] = useState<any[]>([]);
  const [activityFeed, setActivityFeed] = useState<any[]>([]);

  // Messaging & Conversations
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeChatFriend, setActiveChatFriend] = useState<FriendItem | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [msgInput, setMsgInput] = useState('');
  const [isSendingMsg, setIsSendingMsg] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Modals
  const [isChallengeModalOpen, setIsChallengeModalOpen] = useState(false);
  const [challengeTitle, setChallengeTitle] = useState('');
  const [challengeDesc, setChallengeDesc] = useState('');
  const [challengeDuration, setChallengeDuration] = useState('30');
  const [selectedFriendIds, setSelectedFriendIds] = useState<string[]>([]);

  const loadData = async () => {
    try {
      const [fData, pData, cData, feedData, statsData, coachData, convsData] = await Promise.all([
        apiGet<FriendItem[]>('/friends'),
        apiGet<PendingReq[]>('/friends/requests/pending'),
        apiGet<any[]>('/friends/challenges'),
        apiGet<any[]>('/friends/feed'),
        apiGet<any>('/friends/overview'),
        apiGet<any>('/friends/coach'),
        apiGet<Conversation[]>('/friends/conversations'),
      ]);
      setFriends(fData || []);
      setPendingRequests(pData || []);
      setChallenges(cData || []);
      setActivityFeed(feedData || []);
      if (statsData) setOverviewStats(statsData);
      if (coachData) setAiCoach(coachData);
      if (convsData) setConversations(convsData);
    } catch {
      // Fallback empty
      setFriends([]);
      setPendingRequests([]);
      setChallenges([]);
      setActivityFeed([]);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Poll messages every 6 seconds if on messaging tab and friend is selected
  useEffect(() => {
    if (activeTab === 'messages' && activeChatFriend) {
      loadChatMessages(activeChatFriend.id);
      const interval = setInterval(() => {
        loadChatMessages(activeChatFriend.id);
      }, 6000);
      return () => clearInterval(interval);
    }
  }, [activeTab, activeChatFriend]);

  const loadChatMessages = async (friendId: string) => {
    try {
      const msgs = await apiGet<ChatMessage[]>(`/friends/conversations/${friendId}/messages`);
      setChatMessages(msgs || []);
    } catch (err) {
      console.error('Failed to load chat messages:', err);
    }
  };

  const handleSelectFriendChat = (f: FriendItem) => {
    setActiveChatFriend(f);
    loadChatMessages(f.id);
    // Refresh conversation unread status
    apiGet<Conversation[]>('/friends/conversations').then((res) => {
      if (res) setConversations(res);
    });
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeChatFriend || !msgInput.trim() || isSendingMsg) return;

    const content = msgInput.trim();
    setMsgInput('');
    setIsSendingMsg(true);

    try {
      await apiPost('/friends/messages', {
        recipient_id: activeChatFriend.id,
        message: content,
      });
      await loadChatMessages(activeChatFriend.id);
      // Refresh conversations list
      const updatedConvs = await apiGet<Conversation[]>('/friends/conversations');
      if (updatedConvs) setConversations(updatedConvs);
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
      console.error('Failed to send message:', err);
    } finally {
      setIsSendingMsg(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.length < 2) return;
    setIsSearching(true);
    try {
      const res = await apiGet<any[]>(`/friends/search?q=${encodeURIComponent(searchQuery)}`);
      setSearchResults(res || []);
    } catch {
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const sendRequest = async (email: string) => {
    try {
      await apiPost('/friends/request', { addressee_email: email });
      setSearchQuery('');
      setSearchResults([]);
      loadData();
    } catch (err) {
      console.error('Failed to send friend request:', err);
    }
  };

  const respondRequest = async (friendshipId: string, action: 'accept' | 'reject') => {
    try {
      await apiPut(`/friends/request/${friendshipId}/${action}`, {});
      loadData();
    } catch (err) {
      console.error('Failed to respond to request:', err);
    }
  };

  const handleCreateChallenge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!challengeTitle.trim()) return;

    try {
      await apiPost('/friends/challenges', {
        title: challengeTitle.trim(),
        description: challengeDesc.trim() || undefined,
        duration_days: parseInt(challengeDuration) || 30,
        friend_ids: selectedFriendIds,
      });
      setChallengeTitle('');
      setChallengeDesc('');
      setSelectedFriendIds([]);
      setIsChallengeModalOpen(false);
      loadData();
    } catch (err) {
      console.error('Failed to create challenge:', err);
    }
  };

  const handleUpdateChallengeProgress = async (challengeId: string, currentPct: number) => {
    const nextPct = Math.min(100, currentPct + 10);
    try {
      await apiPut(`/friends/challenges/${challengeId}/progress`, {
        progress_percent: nextPct,
      });
      loadData();
    } catch (err) {
      console.error('Failed to update progress:', err);
    }
  };

  const totalUnreadAll = conversations.reduce((sum, c) => sum + (c.unread_count || 0), 0);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
            <Users2 className="text-violet-600" size={26} />
            Friends Growth & Accountability
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Build habits together, track shared progress, and stay accountable with peer motivation
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="secondary"
            onClick={loadData}
            icon={<RefreshCw size={14} />}
          >
            Sync
          </Button>
          <Button
            size="sm"
            onClick={() => setIsChallengeModalOpen(true)}
            icon={<Trophy size={14} />}
          >
            New Challenge
          </Button>
        </div>
      </div>

      {/* Overview Stat Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Card className="p-3.5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-violet-100 dark:bg-violet-900/40 text-violet-600 flex items-center justify-center font-bold">
            <Users2 size={18} />
          </div>
          <div>
            <span className="text-xs text-gray-400 block">Total Friends</span>
            <span className="text-lg font-extrabold text-gray-900 dark:text-white">
              {overviewStats.total_friends}
            </span>
          </div>
        </Card>

        <Card className="p-3.5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-950/50 text-emerald-600 flex items-center justify-center font-bold">
            <TrendingUp size={18} />
          </div>
          <div>
            <span className="text-xs text-gray-400 block">Active Friends</span>
            <span className="text-lg font-extrabold text-gray-900 dark:text-white">
              {overviewStats.active_friends}
            </span>
          </div>
        </Card>

        <Card className="p-3.5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-amber-100 dark:bg-amber-950/50 text-amber-600 flex items-center justify-center font-bold">
            <Trophy size={18} />
          </div>
          <div>
            <span className="text-xs text-gray-400 block">Active Challenges</span>
            <span className="text-lg font-extrabold text-gray-900 dark:text-white">
              {overviewStats.active_challenges}
            </span>
          </div>
        </Card>

        <Card className="p-3.5 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-950/50 text-blue-600 flex items-center justify-center font-bold">
            <MessageSquare size={18} />
          </div>
          <div>
            <span className="text-xs text-gray-400 block">Messages</span>
            <span className="text-lg font-extrabold text-gray-900 dark:text-white">
              {overviewStats.total_messages}
            </span>
          </div>
        </Card>
      </div>

      {/* Tab Switcher */}
      <div className="flex items-center gap-2 border-b border-gray-100 dark:border-gray-800 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveTab('overview')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
            activeTab === 'overview'
              ? 'bg-violet-600 text-white shadow-sm'
              : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <Sparkles size={14} />
          Overview & AI Coach
        </button>

        <button
          onClick={() => setActiveTab('messages')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 relative ${
            activeTab === 'messages'
              ? 'bg-violet-600 text-white shadow-sm'
              : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <MessageSquare size={14} />
          Messages Inbox
          {totalUnreadAll > 0 && (
            <span className="ml-1 px-1.5 py-0.2 bg-rose-500 text-white rounded-full text-[10px] font-black">
              {totalUnreadAll}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('friends')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
            activeTab === 'friends'
              ? 'bg-violet-600 text-white shadow-sm'
              : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <Users2 size={14} />
          Friends Directory
          {pendingRequests.length > 0 && (
            <span className="ml-1 px-1.5 py-0.2 bg-violet-200 dark:bg-violet-800 text-violet-800 dark:text-violet-200 rounded-full text-[10px] font-bold">
              {pendingRequests.length}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveTab('challenges')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
            activeTab === 'challenges'
              ? 'bg-violet-600 text-white shadow-sm'
              : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <Trophy size={14} />
          Growth Challenges
        </button>

        <button
          onClick={() => setActiveTab('feed')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
            activeTab === 'feed'
              ? 'bg-violet-600 text-white shadow-sm'
              : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <Activity size={14} />
          Activity Feed
        </button>
      </div>

      {/* ── TAB 1: OVERVIEW & AI GROUP COACH ─────────────────────────────────── */}
      {activeTab === 'overview' && (
        <div className="space-y-5">
          {/* AI Group Coach Banner */}
          <Card className="p-5 bg-gradient-to-r from-violet-900/20 via-indigo-900/10 to-transparent border-violet-200/50 dark:border-violet-800/40">
            <div className="flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-violet-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-violet-600/30">
                <Sparkles size={20} />
              </div>
              <div className="space-y-1.5 flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-bold text-gray-900 dark:text-white">
                    AI Group Momentum Coach
                  </h3>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300">
                    Live Insights
                  </span>
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
                  {aiCoach?.recommendation || 'Analyzing your peer network progress and team consistency...'}
                </p>

                {aiCoach?.suggested_actions && aiCoach.suggested_actions.length > 0 && (
                  <div className="pt-2 flex flex-wrap gap-2">
                    {aiCoach.suggested_actions.map((act, i) => (
                      <span
                        key={i}
                        className="text-[11px] font-semibold px-2.5 py-1 rounded-lg bg-white dark:bg-gray-800 border border-violet-200 dark:border-violet-800 text-violet-700 dark:text-violet-300 flex items-center gap-1"
                      >
                        ✓ {act}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </Card>

          {/* Quick Actions & Recent Challenges */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="p-4 space-y-3">
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                Accountability Quick Links
              </h4>
              <div className="space-y-2">
                <div
                  onClick={() => setActiveTab('messages')}
                  className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 hover:bg-violet-50 dark:hover:bg-violet-950/30 cursor-pointer flex items-center justify-between transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <MessageSquare size={16} className="text-violet-600" />
                    <span className="text-xs font-semibold text-gray-800 dark:text-gray-200">
                      Open Friend Conversations
                    </span>
                  </div>
                  <Badge variant="medium">{overviewStats.total_messages} messages</Badge>
                </div>

                <div
                  onClick={() => setActiveTab('challenges')}
                  className="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/40 hover:bg-violet-50 dark:hover:bg-violet-950/30 cursor-pointer flex items-center justify-between transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <Trophy size={16} className="text-amber-500" />
                    <span className="text-xs font-semibold text-gray-800 dark:text-gray-200">
                      View Active Challenges
                    </span>
                  </div>
                  <Badge variant="urgent">{overviewStats.active_challenges} active</Badge>
                </div>
              </div>
            </Card>

            <Card className="p-4 space-y-3">
              <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                Pending Peer Requests ({pendingRequests.length})
              </h4>
              {pendingRequests.length === 0 ? (
                <p className="text-xs text-gray-400 py-3">No pending friend requests.</p>
              ) : (
                <div className="space-y-2">
                  {pendingRequests.map((req) => (
                    <div
                      key={req.friendship_id}
                      className="flex items-center justify-between p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800/40 text-xs"
                    >
                      <div>
                        <p className="font-bold text-gray-900 dark:text-white">
                          {req.requester_name || req.requester_email}
                        </p>
                        <p className="text-[10px] text-gray-400">{req.requester_email}</p>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Button
                          size="sm"
                          onClick={() => respondRequest(req.friendship_id, 'accept')}
                          icon={<Check size={12} />}
                        >
                          Accept
                        </Button>
                        <button
                          onClick={() => respondRequest(req.friendship_id, 'reject')}
                          className="p-1 rounded-lg text-gray-400 hover:text-red-500"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        </div>
      )}

      {/* ── TAB 2: MESSAGING INBOX & 2-WAY CHAT ─────────────────────────────── */}
      {activeTab === 'messages' && (
        <Card className="p-0 overflow-hidden min-h-[500px] flex flex-col md:flex-row border border-gray-100 dark:border-gray-800 shadow-sm">
          {/* Left: Conversations List */}
          <div className="w-full md:w-80 border-r border-gray-100 dark:border-gray-800 p-4 space-y-3 shrink-0 bg-gray-50/50 dark:bg-[#15151e]">
            <div className="flex items-center justify-between pb-2 border-b border-gray-200 dark:border-gray-800">
              <h3 className="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-1.5">
                <MessageSquare size={16} className="text-violet-600" />
                Conversations ({friends.length})
              </h3>
            </div>

            {friends.length === 0 ? (
              <p className="text-xs text-gray-400 py-6 text-center">
                Add friends to start messaging and sharing progress.
              </p>
            ) : (
              <div className="space-y-1.5 max-h-[460px] overflow-y-auto">
                {friends.map((f) => {
                  const conv = conversations.find((c) => c.friend_id === f.id);
                  const isSelected = activeChatFriend?.id === f.id;

                  return (
                    <div
                      key={f.id}
                      onClick={() => handleSelectFriendChat(f)}
                      className={`p-3 rounded-xl cursor-pointer transition-all flex items-center justify-between ${
                        isSelected
                          ? 'bg-violet-600 text-white shadow-sm'
                          : 'bg-white dark:bg-[#1a1a24] hover:bg-gray-100 dark:hover:bg-gray-800/60'
                      }`}
                    >
                      <div className="flex items-center gap-2.5 overflow-hidden">
                        <div
                          className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
                            isSelected
                              ? 'bg-white text-violet-600'
                              : 'bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300'
                          }`}
                        >
                          {(f.full_name || f.email)[0].toUpperCase()}
                        </div>
                        <div className="overflow-hidden">
                          <p
                            className={`text-xs font-bold truncate ${
                              isSelected ? 'text-white' : 'text-gray-900 dark:text-white'
                            }`}
                          >
                            {f.full_name || f.email}
                          </p>
                          <p
                            className={`text-[10px] truncate ${
                              isSelected ? 'text-violet-100' : 'text-gray-400'
                            }`}
                          >
                            {conv?.last_message || 'Tap to chat'}
                          </p>
                        </div>
                      </div>

                      {conv && conv.unread_count > 0 && !isSelected && (
                        <span className="px-1.5 py-0.5 rounded-full bg-violet-600 text-white text-[10px] font-black">
                          {conv.unread_count}
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Right: Active Chat Area */}
          <div className="flex-1 flex flex-col justify-between bg-white dark:bg-[#17171f] min-h-[400px]">
            {activeChatFriend ? (
              <>
                {/* Chat Top Banner */}
                <div className="p-3.5 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between bg-gray-50/60 dark:bg-gray-800/20">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-full bg-violet-600 text-white flex items-center justify-center text-xs font-bold">
                      {(activeChatFriend.full_name || activeChatFriend.email)[0].toUpperCase()}
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-gray-900 dark:text-white">
                        {activeChatFriend.full_name || activeChatFriend.email}
                      </h4>
                      <span className="text-[10px] text-gray-400">{activeChatFriend.email}</span>
                    </div>
                  </div>
                  <span className="text-[10px] font-semibold text-emerald-500 flex items-center gap-1">
                    ● Connected
                  </span>
                </div>

                {/* Messages Stream */}
                <div className="flex-1 p-4 space-y-3 overflow-y-auto max-h-[380px]">
                  {chatMessages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center py-12 text-gray-400">
                      <MessageSquare size={32} className="mb-2 opacity-40 text-violet-600" />
                      <p className="text-xs font-medium">No messages yet in this conversation.</p>
                      <p className="text-[10px] text-gray-400">Send an encouragement or check in on their goals!</p>
                    </div>
                  ) : (
                    chatMessages.map((msg) => {
                      const isMe = msg.sender_id === user?.id;

                      return (
                        <div
                          key={msg.id}
                          className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}
                        >
                          <div
                            className={`max-w-[75%] p-3 rounded-2xl text-xs leading-relaxed ${
                              isMe
                                ? 'bg-violet-600 text-white rounded-tr-none'
                                : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white rounded-tl-none'
                            }`}
                          >
                            <p>{msg.content}</p>
                          </div>
                          <span className="text-[9px] text-gray-400 mt-1 px-1">
                            {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                          </span>
                        </div>
                      );
                    })
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Bottom Input Box */}
                <form
                  onSubmit={handleSendMessage}
                  className="p-3 border-t border-gray-100 dark:border-gray-800 flex items-center gap-2"
                >
                  <input
                    type="text"
                    required
                    placeholder={`Message ${activeChatFriend.full_name?.split(' ')[0] || 'friend'}...`}
                    value={msgInput}
                    onChange={(e) => setMsgInput(e.target.value)}
                    className="flex-1 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2 text-xs outline-none dark:text-white"
                  />
                  <Button
                    type="submit"
                    size="sm"
                    disabled={!msgInput.trim() || isSendingMsg}
                    icon={<Send size={14} />}
                  >
                    Send
                  </Button>
                </form>
              </>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center p-8 text-gray-400">
                <MessageSquare size={36} className="text-violet-500 mb-2 opacity-50" />
                <h4 className="text-sm font-bold text-gray-700 dark:text-gray-300">
                  Select a Conversation
                </h4>
                <p className="text-xs text-gray-400 max-w-xs mt-1">
                  Choose a friend from the left sidebar to send and receive real-time messages.
                </p>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* ── TAB 3: FRIENDS DIRECTORY & SEARCH ───────────────────────────────── */}
      {activeTab === 'friends' && (
        <div className="space-y-6">
          {/* Search Card */}
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
              <Button type="submit" size="sm" disabled={isSearching}>
                {isSearching ? 'Searching...' : 'Search'}
              </Button>
            </form>

            {searchResults.length > 0 && (
              <div className="mt-4 pt-3 border-t border-gray-100 dark:border-gray-800 space-y-2">
                <span className="text-xs font-bold text-gray-400 uppercase">Search Results</span>
                {searchResults.map((u) => (
                  <div
                    key={u.id}
                    className="flex items-center justify-between p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800/40 text-xs"
                  >
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white">
                        {u.full_name || u.email}
                      </p>
                      <p className="text-gray-400 text-[10px]">{u.email}</p>
                    </div>
                    <Button size="sm" onClick={() => sendRequest(u.email)} icon={<UserPlus size={14} />}>
                      Add Friend
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Friends List */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-gray-900 dark:text-white">
              My Growth Friends ({friends.length})
            </h3>
            {friends.length === 0 ? (
              <EmptyState
                icon={<Users2 size={28} />}
                title="No friends added yet"
                description="Search for study or work partners above to start collaborating."
              />
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {friends.map((f) => (
                  <Card key={f.id} className="p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-violet-600 text-white font-bold text-sm flex items-center justify-center">
                        {(f.full_name || f.email)[0].toUpperCase()}
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-gray-900 dark:text-white">
                          {f.full_name || f.email}
                        </h4>
                        <p className="text-xs text-gray-400">{f.email}</p>
                      </div>
                    </div>

                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => {
                        handleSelectFriendChat(f);
                        setActiveTab('messages');
                      }}
                      icon={<MessageSquare size={14} />}
                    >
                      Chat
                    </Button>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── TAB 4: GROWTH CHALLENGES ────────────────────────────────────────── */}
      {activeTab === 'challenges' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-gray-900 dark:text-white">
              Active Growth Challenges ({challenges.length})
            </h3>
            <Button onClick={() => setIsChallengeModalOpen(true)} size="sm" icon={<Trophy size={16} />}>
              Create Challenge
            </Button>
          </div>

          {challenges.length === 0 ? (
            <EmptyState
              icon={<Trophy size={32} />}
              title="No shared challenges"
              description="Create a 30-day coding, reading, or fitness sprint and invite your peers."
              actionLabel="Start Challenge"
              onAction={() => setIsChallengeModalOpen(true)}
            />
          ) : (
            challenges.map((ch) => (
              <Card key={ch.id} className="p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-base font-bold text-gray-900 dark:text-white">{ch.title}</h4>
                    {ch.description && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{ch.description}</p>
                    )}
                  </div>
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300">
                    {ch.duration_days} Days
                  </span>
                </div>

                {/* Leaderboard */}
                <div className="space-y-2 pt-2 border-t border-gray-100 dark:border-gray-800">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-gray-400 uppercase tracking-wider block">
                      Participants Progress
                    </span>
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => handleUpdateChallengeProgress(ch.id, parseInt(ch.my_progress || '0'))}
                    >
                      +10% Daily Check-in
                    </Button>
                  </div>

                  {ch.participants &&
                    ch.participants.map((p: any, idx: number) => {
                      const pct = parseInt(p.progress_percent || '0');
                      return (
                        <div key={idx} className="space-y-1">
                          <div className="flex items-center justify-between text-xs">
                            <span className="font-semibold text-gray-800 dark:text-gray-200">
                              {p.name || 'Participant'}
                            </span>
                            <span className="font-bold text-violet-600">{pct}%</span>
                          </div>
                          <div className="w-full bg-gray-100 dark:bg-gray-800 h-2 rounded-full overflow-hidden">
                            <div
                              className="bg-violet-600 h-full rounded-full transition-all duration-500"
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {/* ── TAB 5: ACTIVITY FEED ────────────────────────────────────────────── */}
      {activeTab === 'feed' && (
        <div className="space-y-3">
          <h3 className="text-base font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Activity size={18} className="text-violet-600" />
            Friends Activity Stream
          </h3>

          {activityFeed.length === 0 ? (
            <EmptyState
              icon={<Activity size={28} />}
              title="No recent activity"
              description="When you or your friends check in to challenges, updates will appear here."
            />
          ) : (
            activityFeed.map((item, idx) => (
              <Card key={idx} className="p-4 flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-violet-100 dark:bg-violet-900/50 text-violet-600 flex items-center justify-center font-bold text-xs shrink-0">
                  {item.user_name ? item.user_name[0].toUpperCase() : 'U'}
                </div>
                <div className="flex-1 text-xs">
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {item.user_name}{' '}
                    <span className="font-normal text-gray-500 dark:text-gray-400">
                      updated progress to {item.progress}% in
                    </span>{' '}
                    <span className="font-bold text-violet-600">{item.challenge_title}</span>
                  </p>
                  {item.timestamp && (
                    <span className="text-[10px] text-gray-400">
                      {new Date(item.timestamp).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {/* ── Modal: Create Challenge ─────────────────────────────────────────── */}
      <Modal isOpen={isChallengeModalOpen} onClose={() => setIsChallengeModalOpen(false)} title="Create Growth Challenge">
        <form onSubmit={handleCreateChallenge} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Challenge Title *
            </label>
            <input
              type="text"
              required
              placeholder="e.g., 30-Day Cybersecurity & LeetCode Sprint"
              value={challengeTitle}
              onChange={(e) => setChallengeTitle(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2.5 text-sm outline-none dark:text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Description & Rules
            </label>
            <textarea
              rows={2}
              placeholder="Daily expectations, targets, and milestones..."
              value={challengeDesc}
              onChange={(e) => setChallengeDesc(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2 text-xs outline-none dark:text-white resize-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Duration (Days)
            </label>
            <input
              type="number"
              min={7}
              max={100}
              value={challengeDuration}
              onChange={(e) => setChallengeDuration(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white"
            />
          </div>

          {friends.length > 0 && (
            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                Invite Friends
              </label>
              <div className="space-y-1 max-h-32 overflow-y-auto">
                {friends.map((f) => (
                  <label
                    key={f.id}
                    className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 text-xs cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedFriendIds.includes(f.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedFriendIds([...selectedFriendIds, f.id]);
                        } else {
                          setSelectedFriendIds(selectedFriendIds.filter((id) => id !== f.id));
                        }
                      }}
                      className="w-4 h-4 rounded text-violet-600"
                    />
                    <span>{f.full_name || f.email}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-3 border-t border-gray-100 dark:border-gray-800">
            <Button type="button" variant="secondary" onClick={() => setIsChallengeModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Launch Challenge</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
