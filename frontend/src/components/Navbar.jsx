import React from 'react';
import { Award, Shield, User, LogOut, FileText, CheckCircle2, ChevronRight, Home, BarChart3, Users, Building2 } from 'lucide-react';


export default function Navbar({ currentUser, onLogout, onSwitchDemo, activeTab, setActiveTab }) {
  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
      {/* Official Government of India Tricolor Ribbon */}
      <div className="h-1.5 w-full flex">
        <div className="flex-1 bg-amber-500" />
        <div className="flex-1 bg-white" />
        <div className="flex-1 bg-emerald-600" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between min-h-[5.5rem] py-2.5 gap-4">
          {/* Brand & Emblem */}
          <div className="flex items-center space-x-3.5 cursor-pointer select-none flex-shrink-0" onClick={() => setActiveTab('home')}>
            <div className="w-12 h-12 rounded-xl bg-gov-navy flex items-center justify-center text-white shadow-md flex-shrink-0">
              <Award className="w-7 h-7 text-amber-400" />
            </div>
            <div className="flex flex-col justify-center">
              <div className="flex items-center space-x-2 mb-0.5">
                <span className="text-[10px] font-bold uppercase tracking-wider text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                  Government of India
                </span>
                <span className="text-[10px] font-semibold text-slate-400">SIH-26239</span>
              </div>
              <h1 className="text-sm sm:text-base lg:text-lg font-bold text-gov-navy leading-tight whitespace-nowrap">
                जनजातीय कार्य मंत्रालय <span className="text-slate-400 font-normal">|</span> Ministry of Tribal Affairs
              </h1>
              <p className="text-[11px] sm:text-xs text-slate-500 font-medium leading-normal mt-0.5 whitespace-nowrap">
                National Fellowship & Scholarship Portal (Scheduled Tribes)
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            <button
              onClick={() => setActiveTab('home')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'home'
                  ? 'bg-gov-navy text-white'
                  : 'text-slate-700 hover:text-gov-navy hover:bg-slate-100'
              }`}
            >
              <span className="flex items-center space-x-1.5">
                <Home className="w-4 h-4" />
                <span>Schemes</span>
              </span>
            </button>

            {currentUser?.role === 'applicant' && (
              <>
                <button
                  onClick={() => setActiveTab('apply')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'apply'
                      ? 'bg-gov-navy text-white'
                      : 'text-slate-700 hover:text-gov-navy hover:bg-slate-100'
                  }`}
                >
                  <span className="flex items-center space-x-1.5">
                    <FileText className="w-4 h-4" />
                    <span>Apply Online</span>
                  </span>
                </button>
                <button
                  onClick={() => setActiveTab('applicant-dashboard')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'applicant-dashboard'
                      ? 'bg-gov-navy text-white'
                      : 'text-slate-700 hover:text-gov-navy hover:bg-slate-100'
                  }`}
                >
                  <span className="flex items-center space-x-1.5">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>My Applications</span>
                  </span>
                </button>
              </>
            )}

            {currentUser?.role === 'admin' && (
              <>
                <button
                  onClick={() => setActiveTab('admin-dashboard')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'admin-dashboard'
                      ? 'bg-gov-navy text-white'
                      : 'text-slate-700 hover:text-gov-navy hover:bg-slate-100'
                  }`}
                >
                  <span className="flex items-center space-x-1.5">
                    <BarChart3 className="w-4 h-4" />
                    <span>Scrutiny Portal</span>
                  </span>
                </button>
                <button
                  onClick={() => setActiveTab('merit-ranking')}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'merit-ranking'
                      ? 'bg-gov-navy text-white'
                      : 'text-slate-700 hover:text-gov-navy hover:bg-slate-100'
                  }`}
                >
                  <span className="flex items-center space-x-1.5">
                    <Users className="w-4 h-4" />
                    <span>Assistive Merit Ranking</span>
                  </span>
                </button>
              </>
            )}

            {currentUser?.role === 'institution' && (
              <button
                onClick={() => setActiveTab('institution-dashboard')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'institution-dashboard'
                    ? 'bg-indigo-900 text-white shadow'
                    : 'text-slate-700 hover:text-indigo-900 hover:bg-slate-100'
                }`}
              >
                <span className="flex items-center space-x-1.5">
                  <Building2 className="w-4 h-4" />
                  <span>Nodal Verification Desk</span>
                </span>
              </button>
            )}
          </nav>

          {/* User Profile & Demo Switcher */}
          <div className="flex items-center space-x-3">
            {currentUser ? (
              <div className="flex items-center space-x-3">
                <div className="text-right hidden sm:block">
                  <div className="text-xs font-bold text-slate-800 flex items-center justify-end space-x-1">
                    {currentUser.role === 'admin' ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
                        <Shield className="w-3 h-3 mr-1" /> MoTA Admin Officer
                      </span>
                    ) : currentUser.role === 'institution' ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-indigo-100 text-indigo-800 border border-indigo-200">
                        <Building2 className="w-3 h-3 mr-1" /> Institution Nodal Officer
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                        <User className="w-3 h-3 mr-1" /> ST Applicant
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-500 font-medium truncate max-w-[160px]">
                    {currentUser.full_name}
                  </div>
                </div>

                <button
                  onClick={onLogout}
                  title="Logout"
                  className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setActiveTab('login')}
                  className="px-4 py-2 text-sm font-medium text-gov-navy bg-white border border-gov-navy rounded-lg hover:bg-blue-50 transition-colors shadow-sm"
                >
                  Login / Register
                </button>
              </div>
            )}

            {/* Judge Demo Quick Switcher Dropdown */}
            <div className="hidden lg:flex items-center pl-2 border-l border-slate-200 space-x-1.5">
              <span className="text-[11px] font-bold text-slate-500">Demo Role:</span>
              <select
                value={
                  currentUser?.email === 'admin@mota.gov.in' ? 'admin' :
                  currentUser?.email === 'nodal@iitd.ac.in' ? 'iitd' :
                  currentUser?.email === 'nodal@cuj.ac.in' ? 'cuj' :
                  'applicant'
                }
                onChange={(e) => onSwitchDemo(e.target.value)}
                className="px-2 py-1 text-xs font-semibold rounded-lg bg-slate-100 hover:bg-slate-200 text-gov-navy border border-slate-300 focus:outline-hidden cursor-pointer"
                title="Quickly switch between evaluation personas"
              >
                <option value="applicant">ST Applicant (Birsa Soren)</option>
                <option value="admin">MoTA Admin (Scrutiny Desk)</option>
                <option value="iitd">Institution Officer (IIT Delhi)</option>
                <option value="cuj">Institution Officer (Central Univ Jharkhand)</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
