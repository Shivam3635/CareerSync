import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import type { Category, Gender, QualificationLevel, QualificationStatus } from '../types';
import { UserCheck, ArrowRight, Sparkles, AlertCircle } from 'lucide-react';

export const AuthPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialMode = searchParams.get('mode') === 'register' ? 'register' : 'login';
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);

  const { login, register, demoLogin, user } = useAuth();
  const navigate = useNavigate();

  // If already logged in, redirect to appropriate destination
  useEffect(() => {
    if (user) {
      if (user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    }
  }, [user, navigate]);

  // Sync mode with URL param
  const handleModeChange = (newMode: 'login' | 'register') => {
    setMode(newMode);
    setSearchParams({ mode: newMode });
    setError('');
  };

  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [dob, setDob] = useState('2000-01-01');
  const [gender, setGender] = useState<Gender>('male');
  const [category, setCategory] = useState<Category>('GEN');
  const [domicileState, setDomicileState] = useState('Uttar Pradesh');
  const [highestQual, setHighestQual] = useState<QualificationLevel>('Graduate');
  const [qualStatus, setQualStatus] = useState<QualificationStatus>('completed');
  const [degree, setDegree] = useState('Bachelor of Science');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const loggedUser = await login(email, password);
      if (loggedUser.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      setError(err.message || 'Login failed. Please verify your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await register({
        email,
        password,
        full_name: fullName,
        date_of_birth: dob,
        gender,
        category,
        domicile_state: domicileState,
        highest_qualification: highestQual,
        qualification_status: qualStatus,
        degree,
      });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please check the inputs.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoAuth = async () => {
    setLoading(true);
    setError('');
    try {
      await demoLogin('student');
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Demo login failed. Make sure demo accounts are seeded.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F0E8] text-[#111111]">
      <Navbar />

      <main className="flex-1 max-w-xl w-full mx-auto px-4 py-10 sm:py-16">
        {/* Candidate Quick Demo Box */}
        <div className="bg-[#FFFFFF] border-2 border-[#111111] brutal-shadow p-4 mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="font-mono text-[11px] font-black uppercase tracking-wider text-[#111111] flex items-center gap-1.5">
              <Sparkles size={14} className="text-[#FF6B4A]" />
              Candidate Quick Preview
            </span>
            <span className="text-[10px] font-bold bg-[#D9FF43] border border-[#111111] px-1.5 py-0.2">
              Student Demo
            </span>
          </div>

          <p className="text-xs text-[#555555] mb-3">
            Want to test instant eligibility evaluation before creating an account?
          </p>

          <button
            type="button"
            onClick={handleDemoAuth}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 py-2.5 px-3 bg-[#D9FF43] text-[#111111] border-2 border-[#111111] brutal-shadow-sm font-bold text-xs uppercase tracking-wider hover:translate-x-[-1px] hover:translate-y-[-1px] active:translate-x-[1px] active:translate-y-[1px] transition-transform cursor-pointer"
          >
            <UserCheck size={16} />
            <span>Explore as Candidate (1-Click Demo)</span>
          </button>
        </div>

        {/* Auth Box */}
        <div className="bg-[#FFFFFF] border-3 border-[#111111] brutal-shadow-lg p-6 sm:p-8">
          {/* Segmented Control */}
          <div className="grid grid-cols-2 border-2 border-[#111111] p-1 bg-[#F5F0E8] mb-6">
            <button
              type="button"
              onClick={() => handleModeChange('login')}
              className={`py-2 text-xs font-black uppercase tracking-wider transition-colors ${
                mode === 'login'
                  ? 'bg-[#111111] text-[#D9FF43] border-2 border-[#111111] brutal-shadow-sm'
                  : 'text-[#555555] hover:text-[#111111]'
              }`}
            >
              Log In
            </button>
            <button
              type="button"
              onClick={() => handleModeChange('register')}
              className={`py-2 text-xs font-black uppercase tracking-wider transition-colors ${
                mode === 'register'
                  ? 'bg-[#111111] text-[#D9FF43] border-2 border-[#111111] brutal-shadow-sm'
                  : 'text-[#555555] hover:text-[#111111]'
              }`}
            >
              Create Account
            </button>
          </div>

          {error && (
            <div className="mb-5 p-3 bg-[#FFF0ED] border-2 border-[#111111] text-xs font-bold text-[#D12E00] flex items-start gap-2">
              <AlertCircle size={16} className="shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          {mode === 'login' ? (
            <form onSubmit={handleLoginSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-black uppercase tracking-wider mb-1 text-[#111111]">
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="aspirant@example.com"
                  className="w-full p-2.5 bg-white border-2 border-[#111111] text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
                />
              </div>

              <div>
                <label className="block text-xs font-black uppercase tracking-wider mb-1 text-[#111111]">
                  Password
                </label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full p-2.5 bg-white border-2 border-[#111111] text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 mt-2 bg-[#D9FF43] text-[#111111] font-heading font-black text-sm uppercase tracking-wider border-2 border-[#111111] brutal-shadow hover:bg-[#c9f22e] active:translate-x-[2px] active:translate-y-[2px] transition-all flex items-center justify-center gap-2"
              >
                <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
                <ArrowRight size={18} />
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegisterSubmit} className="space-y-4 text-xs font-bold text-[#111111]">
              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Full Name <span className="text-[#FF6B4A]">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Priya Patel"
                  className="w-full p-2 bg-white border-2 border-[#111111] text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block uppercase tracking-wider mb-1">
                    Email <span className="text-[#FF6B4A]">*</span>
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="priya@example.com"
                    className="w-full p-2 bg-white border-2 border-[#111111] text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
                  />
                </div>
                <div>
                  <label className="block uppercase tracking-wider mb-1">
                    Password <span className="text-[#FF6B4A]">*</span>
                  </label>
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Min 6 characters"
                    className="w-full p-2 bg-white border-2 border-[#111111] text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block uppercase tracking-wider mb-1">
                    Date of Birth <span className="text-[#FF6B4A]">*</span>
                  </label>
                  <input
                    type="date"
                    required
                    value={dob}
                    onChange={(e) => setDob(e.target.value)}
                    className="w-full p-2 bg-white border-2 border-[#111111] font-mono text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
                  />
                </div>
                <div>
                  <label className="block uppercase tracking-wider mb-1">
                    Gender <span className="text-[#FF6B4A]">*</span>
                  </label>
                  <select
                    value={gender}
                    onChange={(e) => setGender(e.target.value as Gender)}
                    className="w-full p-2 bg-white border-2 border-[#111111] font-bold text-sm brutal-shadow-sm focus:outline-none"
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block uppercase tracking-wider mb-1">
                    Category <span className="text-[#FF6B4A]">*</span>
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value as Category)}
                    className="w-full p-2 bg-white border-2 border-[#111111] font-bold text-sm brutal-shadow-sm focus:outline-none"
                  >
                    <option value="GEN">General (UR)</option>
                    <option value="OBC">OBC (Non-Creamy)</option>
                    <option value="SC">SC</option>
                    <option value="ST">ST</option>
                    <option value="EWS">EWS</option>
                  </select>
                </div>
                <div>
                  <label className="block uppercase tracking-wider mb-1">
                    State of Domicile <span className="text-[#FF6B4A]">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={domicileState}
                    onChange={(e) => setDomicileState(e.target.value)}
                    placeholder="e.g. Uttar Pradesh, Delhi"
                    className="w-full p-2 bg-white border-2 border-[#111111] text-sm brutal-shadow-sm focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block uppercase tracking-wider mb-1">
                    Highest Qualification <span className="text-[#FF6B4A]">*</span>
                  </label>
                  <select
                    value={highestQual}
                    onChange={(e) => setHighestQual(e.target.value as QualificationLevel)}
                    className="w-full p-2 bg-white border-2 border-[#111111] font-bold text-sm brutal-shadow-sm focus:outline-none"
                  >
                    <option value="10th">10th Standard</option>
                    <option value="12th">12th Standard</option>
                    <option value="Graduate">Bachelor / Graduate</option>
                    <option value="Post Graduate">Master / Post Graduate</option>
                    <option value="Doctorate">Doctorate</option>
                  </select>
                </div>
                <div>
                  <label className="block uppercase tracking-wider mb-1">
                    Qualification Status <span className="text-[#FF6B4A]">*</span>
                  </label>
                  <select
                    value={qualStatus}
                    onChange={(e) => setQualStatus(e.target.value as QualificationStatus)}
                    className="w-full p-2 bg-white border-2 border-[#111111] font-bold text-sm brutal-shadow-sm focus:outline-none"
                  >
                    <option value="completed">Completed Degree</option>
                    <option value="appearing">Final Year / Appearing</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Degree / Stream
                </label>
                <input
                  type="text"
                  value={degree}
                  onChange={(e) => setDegree(e.target.value)}
                  placeholder="e.g. B.Tech Computer Science, B.Com"
                  className="w-full p-2 bg-white border-2 border-[#111111] text-sm brutal-shadow-sm focus:outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 mt-3 bg-[#D9FF43] text-[#111111] font-heading font-black text-sm uppercase tracking-wider border-2 border-[#111111] brutal-shadow hover:bg-[#c9f22e] active:translate-x-[2px] active:translate-y-[2px] transition-all flex items-center justify-center gap-2"
              >
                <span>{loading ? 'Creating Profile...' : 'Complete Registration'}</span>
                <ArrowRight size={18} />
              </button>
            </form>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
};
