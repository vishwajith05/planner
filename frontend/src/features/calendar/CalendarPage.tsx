import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Badge } from '../../components/common/Badge';
import { Modal } from '../../components/common/Modal';
import { apiGet, apiPost } from '../../services/api';
import { CalendarEvent, Task } from '../../types';
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Clock,
  AlertTriangle,
  Plus,
  CheckCircle,
} from 'lucide-react';

export const CalendarPage: React.FC = () => {
  const [view, setView] = useState<'day' | 'week' | 'agenda'>('week');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [conflicts, setConflicts] = useState<Array<{ event_a: string; event_b: string; message: string }>>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [isFixed, setIsFixed] = useState(false);

  const fetchCalendar = async () => {
    try {
      const data = await apiGet<{ events: CalendarEvent[]; conflicts: Array<{ event_a: string; event_b: string; message: string }> }>('/calendar/events');
      setEvents(data.events || []);
      setConflicts(data.conflicts || []);
    } catch {
      // Demo events if endpoint is empty
      setEvents([
        {
          id: '1',
          user_id: 'user1',
          title: 'Deep Work: Core Architecture',
          start_time: new Date(Date.now() + 1000 * 60 * 60 * 2).toISOString(),
          end_time: new Date(Date.now() + 1000 * 60 * 60 * 4).toISOString(),
          is_fixed: true,
          color: '#8B5CF6',
          created_at: new Date().toISOString(),
        },
        {
          id: '2',
          user_id: 'user1',
          title: 'Team Sync & Milestone Review',
          start_time: new Date(Date.now() + 1000 * 60 * 60 * 5).toISOString(),
          end_time: new Date(Date.now() + 1000 * 60 * 60 * 6).toISOString(),
          is_fixed: false,
          color: '#3B82F6',
          created_at: new Date().toISOString(),
        },
      ]);
    }
  };

  useEffect(() => {
    fetchCalendar();
  }, [currentDate]);

  const handleCreateEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !startTime || !endTime) return;

    try {
      await apiPost('/calendar/events', {
        title,
        start_time: new Date(startTime).toISOString(),
        end_time: new Date(endTime).toISOString(),
        is_fixed: isFixed,
      });
      setTitle('');
      setStartTime('');
      setEndTime('');
      setIsModalOpen(false);
      fetchCalendar();
    } catch {
      // handled
    }
  };

  const getWeekDays = () => {
    const days = [];
    const startOfWeek = new Date(currentDate);
    startOfWeek.setDate(currentDate.getDate() - currentDate.getDay());
    for (let i = 0; i < 7; i++) {
      const d = new Date(startOfWeek);
      d.setDate(startOfWeek.getDate() + i);
      days.push(d);
    }
    return days;
  };

  const nextPeriod = () => {
    const d = new Date(currentDate);
    d.setDate(d.getDate() + (view === 'day' ? 1 : 7));
    setCurrentDate(d);
  };

  const prevPeriod = () => {
    const d = new Date(currentDate);
    d.setDate(d.getDate() - (view === 'day' ? 1 : 7));
    setCurrentDate(d);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight">
            Calendar & Time Blocking
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Schedule fixed commitments and prevent overlapping work slots
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* View Switcher */}
          <div className="bg-gray-100 dark:bg-gray-800 p-1 rounded-xl flex items-center gap-1 text-xs font-semibold">
            {(['day', 'week', 'agenda'] as const).map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`px-3 py-1.5 rounded-lg capitalize transition-all ${
                  view === v
                    ? 'bg-white dark:bg-[#17171f] text-violet-600 dark:text-violet-400 shadow-sm'
                    : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                {v}
              </button>
            ))}
          </div>

          <Button onClick={() => setIsModalOpen(true)} size="sm" icon={<Plus size={16} />}>
            Block Time
          </Button>
        </div>
      </div>

      {/* Conflict Detection Banner */}
      {conflicts.length > 0 && (
        <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/40 text-amber-800 dark:text-amber-300 flex items-start gap-3">
          <AlertTriangle size={20} className="shrink-0 mt-0.5 text-amber-600" />
          <div className="text-xs">
            <h4 className="font-bold text-sm">Schedule Conflicts Detected</h4>
            <ul className="list-disc list-inside mt-1 space-y-0.5">
              {conflicts.map((c, idx) => (
                <li key={idx}>{c.message}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Date Navigation Strip */}
      <div className="flex items-center justify-between p-3 rounded-xl bg-white dark:bg-[#17171f] border border-gray-100 dark:border-gray-800 shadow-sm">
        <div className="flex items-center gap-2">
          <button
            onClick={prevPeriod}
            className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <ChevronLeft size={18} />
          </button>
          <span className="text-sm font-bold text-gray-900 dark:text-white">
            {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
          </span>
          <button
            onClick={nextPeriod}
            className="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            <ChevronRight size={18} />
          </button>
        </div>

        <Button variant="ghost" size="sm" onClick={() => setCurrentDate(new Date())}>
          Today
        </Button>
      </div>

      {/* Week Grid */}
      {view === 'week' && (
        <div className="grid grid-cols-7 gap-2">
          {getWeekDays().map((day, idx) => {
            const isToday = day.toDateString() === new Date().toDateString();
            return (
              <div
                key={idx}
                className={`p-3 rounded-xl min-h-[360px] flex flex-col border ${
                  isToday
                    ? 'bg-violet-50/40 dark:bg-violet-950/20 border-violet-200 dark:border-violet-900/40'
                    : 'bg-white dark:bg-[#17171f] border-gray-100 dark:border-gray-800'
                }`}
              >
                <div className="text-center pb-2 border-b border-gray-100 dark:border-gray-800/60 mb-2">
                  <span className="text-[11px] font-semibold text-gray-400 block uppercase">
                    {day.toLocaleDateString('en-US', { weekday: 'short' })}
                  </span>
                  <span
                    className={`inline-block w-7 h-7 leading-7 rounded-full text-xs font-bold mt-0.5 ${
                      isToday
                        ? 'bg-violet-600 text-white'
                        : 'text-gray-900 dark:text-white'
                    }`}
                  >
                    {day.getDate()}
                  </span>
                </div>

                <div className="space-y-1.5 flex-1 overflow-y-auto">
                  {events.map((ev) => (
                    <div
                      key={ev.id}
                      className="p-2 rounded-lg bg-violet-100 dark:bg-violet-900/40 text-violet-800 dark:text-violet-200 text-xs border border-violet-200 dark:border-violet-800/40"
                    >
                      <p className="font-semibold truncate">{ev.title}</p>
                      <p className="text-[10px] text-violet-600 dark:text-violet-400 mt-0.5">
                        {new Date(ev.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Agenda View */}
      {(view === 'agenda' || view === 'day') && (
        <Card className="divide-y divide-gray-100 dark:divide-gray-800 p-0 overflow-hidden">
          {events.length > 0 ? (
            events.map((ev) => (
              <div key={ev.id} className="p-4 flex items-center justify-between hover:bg-gray-50/50 dark:hover:bg-gray-800/30">
                <div className="flex items-center gap-3">
                  <div className="w-2.5 h-10 rounded-full bg-violet-600" />
                  <div>
                    <h4 className="text-sm font-bold text-gray-900 dark:text-white">{ev.title}</h4>
                    <p className="text-xs text-gray-400 flex items-center gap-1 mt-0.5">
                      <Clock size={12} />
                      {new Date(ev.start_time).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })} -{' '}
                      {new Date(ev.end_time).toLocaleTimeString([], { timeStyle: 'short' })}
                    </p>
                  </div>
                </div>
                <Badge variant={ev.is_fixed ? 'urgent' : 'info'}>
                  {ev.is_fixed ? 'Locked Slot' : 'Flexible'}
                </Badge>
              </div>
            ))
          ) : (
            <div className="p-8 text-center text-sm text-gray-400">
              No calendar events scheduled for this period.
            </div>
          )}
        </Card>
      )}

      {/* Create Event Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Block Time / Add Event">
        <form onSubmit={handleCreateEvent} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
              Event Title
            </label>
            <input
              type="text"
              required
              placeholder="e.g., Focus Block or Client Meeting"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3.5 py-2.5 text-sm outline-none dark:text-white"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                Start Time
              </label>
              <input
                type="datetime-local"
                required
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1">
                End Time
              </label>
              <input
                type="datetime-local"
                required
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl px-3 py-2 text-xs outline-none dark:text-white"
              />
            </div>
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={isFixed}
              onChange={(e) => setIsFixed(e.target.checked)}
              className="w-4 h-4 rounded text-violet-600 focus:ring-violet-500"
            />
            <span className="text-xs text-gray-700 dark:text-gray-300 font-medium">
              Fixed Commitment (Cannot be rescheduled by AI)
            </span>
          </label>

          <div className="flex justify-end gap-2 pt-3 border-t border-gray-100 dark:border-gray-800">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Save Slot</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
