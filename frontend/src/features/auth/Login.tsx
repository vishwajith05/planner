import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../../components/common/Button';
import { BrainCircuit, Mail, Lock, ArrowRight, AlertCircle } from 'lucide-react';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading, error } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate('/');
    } catch {
      // error is handled in store
    }
  };

  const handleDemoLogin = async () => {
    setEmail('demo@planwise.ai');
    setPassword('DemoPassword123!');
    try {
      await login('demo@planwise.ai', 'DemoPassword123!');
      navigate('/');
    } catch {
      // If demo account doesn't exist yet, auto register demo
      try {
        const { register } = useAuthStore.getState();
        await register('demo@planwise.ai', 'DemoPassword123!', 'Demo Explorer');
        navigate('/');
      } catch {
        // handled
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-violet-50/50 via-white to-indigo-50/30 dark:from-[#0f0f13] dark:via-[#14141c] dark:to-[#0f0f13]">
      <div className="w-full max-w-md bg-white dark:bg-[#17171f] rounded-2xl shadow-xl border border-gray-100 dark:border-[#27272e] p-8">
        {/* Brand */}
        <div className="flex flex-col items-center text-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-violet-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-violet-500/30 mb-3">
            <BrainCircuit size={28} />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Welcome back</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Log in to your PlanWise AI workspace
          </p>
        </div>

        {error && (
          <div className="mb-6 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/40 text-rose-700 dark:text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle size={16} className="shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="email"
                required
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl pl-10 pr-4 py-2.5 text-sm focus:ring-2 focus:ring-violet-500 outline-none dark:text-white"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="password"
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl pl-10 pr-4 py-2.5 text-sm focus:ring-2 focus:ring-violet-500 outline-none dark:text-white"
              />
            </div>
          </div>

          <Button type="submit" className="w-full mt-2" disabled={isLoading} icon={<ArrowRight size={16} />}>
            {isLoading ? 'Signing In...' : 'Sign In'}
          </Button>

          <Button
            type="button"
            variant="secondary"
            onClick={handleDemoLogin}
            className="w-full"
          >
            Explore with Demo Account
          </Button>
        </form>

        <p className="text-center text-xs text-gray-500 dark:text-gray-400 mt-6">
          Don't have an account?{' '}
          <Link to="/register" className="font-semibold text-violet-600 dark:text-violet-400 hover:underline">
            Create account
          </Link>
        </p>
      </div>
    </div>
  );
};
