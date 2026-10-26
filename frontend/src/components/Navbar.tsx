import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Compass, LogOut, User as UserIcon, Shield } from 'lucide-react';

interface NavbarProps {
  onOpenProfile?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenProfile }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <header className="w-full bg-[#FFFFFF] border-b-2 border-[#111111] sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-3 sm:px-6 h-16 flex items-center justify-between gap-2">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 group shrink-0">
          <div className="w-8 h-8 sm:w-9 sm:h-9 bg-[#D9FF43] border-2 border-[#111111] flex items-center justify-center font-black text-base sm:text-lg brutal-shadow-sm group-hover:bg-[#111111] group-hover:text-[#D9FF43] transition-colors">
            CS
          </div>
          <div className="flex flex-col">
            <span className="font-heading font-black text-lg sm:text-xl tracking-tight leading-none text-[#111111]">
              CareerSync
            </span>
            <span className="text-[9px] sm:text-[10px] uppercase font-bold tracking-wider text-[#666666]">
              Govt Exam Tracker
            </span>
          </div>
        </Link>

        {/* Navigation Actions */}
        <div className="flex items-center gap-1.5 sm:gap-3">
          {user ? (
            <>
              {user.role === 'admin' ? (
                <Link
                  to="/admin"
                  className="inline-flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs font-bold uppercase bg-[#FF6B4A] text-white border-2 border-[#111111] brutal-shadow-sm hover:translate-x-[-1px] hover:translate-y-[-1px] transition-transform"
                >
                  <Shield size={14} />
                  <span className="hidden sm:inline">Admin Console</span>
                  <span className="sm:hidden">Admin</span>
                </Link>
              ) : null}

              {onOpenProfile && (
                <button
                  onClick={onOpenProfile}
                  className="inline-flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1.5 text-xs font-bold uppercase bg-[#F5F0E8] border-2 border-[#111111] brutal-shadow-sm hover:bg-[#D9FF43] transition-colors"
                  title="Edit Eligibility Profile"
                >
                  <UserIcon size={14} />
                  <span className="hidden sm:inline">Profile:</span>
                  <span className="font-mono bg-[#111111] text-white px-1.5 py-0.2 rounded-none text-[10px] sm:text-[11px]">
                    {user.student_profile?.category || 'STUDENT'}
                  </span>
                </button>
              )}

              <Link
                to="/dashboard"
                className="hidden md:inline-flex items-center gap-1 px-3 py-1.5 text-xs font-bold uppercase bg-[#FFFFFF] border-2 border-[#111111] hover:bg-[#E8E2D8]"
              >
                <Compass size={14} />
                Dashboard
              </Link>

              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1.5 text-xs font-bold uppercase bg-[#FFFFFF] border-2 border-[#111111] hover:bg-[#111111] hover:text-white transition-colors"
                title="Log Out"
              >
                <LogOut size={14} />
                <span className="hidden md:inline">Logout</span>
              </button>
            </>
          ) : (
            <>
              <Link
                to="/auth?mode=login"
                className="px-2.5 sm:px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-[#111111] hover:underline"
              >
                Log In
              </Link>
              <Link
                to="/auth?mode=register"
                className="px-3 sm:px-4 py-1.5 text-xs font-bold uppercase tracking-wider bg-[#D9FF43] text-[#111111] border-2 border-[#111111] brutal-shadow-sm hover:translate-x-[-2px] hover:translate-y-[-2px] hover:bg-[#c9f22e] transition-transform"
              >
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
