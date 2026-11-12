import React, { useState, useEffect } from 'react';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { useTaskStore } from '../../store/taskStore';
import { apiPost } from '../../services/api';
import { PomodoroMode } from '../../types';
import {
  Timer,
  Play,
  Pause,
  RotateCcw,
  Coffee,
  CheckCircle2,
  Sparkles,
} from 'lucide-react';

export const FocusPage: React.FC = () => {
  const { tasks, fetchTasks } = useTaskStore();
  const [mode, setMode] = useState<PomodoroMode>('focus');
  const [selectedTaskId, setSelectedTaskId] = useState<string>('');
  const [completedSessions, setCompletedSessions] = useState(2);

  const modeDurations = {
    focus: 25 * 60,
    short_break: 5 * 60,
    long_break: 15 * 60,
  };

  const [timeLeft, setTimeLeft] = useState(modeDurations.focus);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, []);

  useEffect(() => {
    let interval: any = null;
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && isActive) {
      setIsActive(false);
      handleSessionComplete();
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive, timeLeft]);

  const handleSessionComplete = async () => {
    if (mode === 'focus') {
      setCompletedSessions((prev) => prev + 1);
      try {
        await apiPost('/focus/sessions', {
          task_id: selectedTaskId || undefined,
          duration_minutes: 25,
          mode: 'focus',
        });
      } catch {
        // fallback
      }
    }
    // Switch to break
    switchMode(mode === 'focus' ? 'short_break' : 'focus');
  };

  const switchMode = (newMode: PomodoroMode) => {
    setMode(newMode);
    setIsActive(false);
    setTimeLeft(modeDurations[newMode]);
  };

  const resetTimer = () => {
    setIsActive(false);
    setTimeLeft(modeDurations[mode]);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const totalTime = modeDurations[mode];
  const progressPercent = ((totalTime - timeLeft) / totalTime) * 100;
  const strokeDashoffset = 565 - (565 * progressPercent) / 100;

  return (
    <div className="space-y-6 max-w-2xl mx-auto animate-fade-in text-center">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white tracking-tight flex items-center justify-center gap-2">
          <Timer className="text-violet-600" size={26} />
          Pomodoro & Deep Focus
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Eliminate distractions with timed sprints and cognitive rest intervals
        </p>
      </div>

      {/* Mode Switcher */}
      <div className="inline-flex bg-gray-100 dark:bg-gray-800 p-1.5 rounded-2xl gap-1">
        {(['focus', 'short_break', 'long_break'] as const).map((m) => (
          <button
            key={m}
            onClick={() => switchMode(m)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              mode === m
                ? 'bg-white dark:bg-[#17171f] text-violet-600 dark:text-violet-400 shadow-sm'
                : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            {m === 'focus' ? 'Focus (25m)' : m === 'short_break' ? 'Short Break (5m)' : 'Long Break (15m)'}
          </button>
        ))}
      </div>

      {/* Circular SVG Timer */}
      <Card className="p-8 flex flex-col items-center justify-center">
        <div className="relative w-64 h-64 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90">
            {/* Background Ring */}
            <circle
              cx="128"
              cy="128"
              r="90"
              className="text-gray-100 dark:text-gray-800"
              strokeWidth="10"
              stroke="currentColor"
              fill="transparent"
            />
            {/* Animated Progress Ring */}
            <circle
              cx="128"
              cy="128"
              r="90"
              className="text-violet-600 dark:text-violet-500 transition-all duration-500 ease-linear"
              strokeWidth="10"
              strokeDasharray={565}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              stroke="currentColor"
              fill="transparent"
            />
          </svg>

          {/* Time Display */}
          <div className="absolute flex flex-col items-center">
            <span className="text-5xl font-black text-gray-900 dark:text-white tracking-tighter">
              {formatTime(timeLeft)}
            </span>
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-widest mt-1">
              {mode.replace('_', ' ')}
            </span>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3 mt-6">
          <Button
            size="lg"
            onClick={() => setIsActive(!isActive)}
            className="w-32 shadow-lg shadow-violet-500/20"
            icon={isActive ? <Pause size={18} /> : <Play size={18} />}
          >
            {isActive ? 'Pause' : 'Start'}
          </Button>

          <button
            onClick={resetTimer}
            title="Reset"
            className="p-3 rounded-xl text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <RotateCcw size={20} />
          </button>
        </div>
      </Card>

      {/* Linked Task Selector */}
      <Card className="p-4 text-left">
        <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
          Link to Active Task (Optional)
        </label>
        <select
          value={selectedTaskId}
          onChange={(e) => setSelectedTaskId(e.target.value)}
          className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl px-3.5 py-2.5 text-sm outline-none dark:text-white"
        >
          <option value="">No linked task (free focus)</option>
          {tasks.filter((t) => !t.is_completed).map((t) => (
            <option key={t.id} value={t.id}>
              {t.title} ({t.category})
            </option>
          ))}
        </select>
        <div className="flex items-center justify-between text-xs text-gray-400 mt-2 px-1">
          <span>Completed focus blocks today:</span>
          <span className="font-bold text-violet-600 dark:text-violet-400">
            {completedSessions} sessions ({completedSessions * 25} mins)
          </span>
        </div>
      </Card>
    </div>
  );
};
