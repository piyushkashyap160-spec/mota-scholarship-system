import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import ApplyScheme from './pages/ApplyScheme';
import ApplicantDashboard from './pages/ApplicantDashboard';
import AdminDashboard from './pages/AdminDashboard';
import AdminApplicationDetail from './pages/AdminApplicationDetail';
import AdminMeritRanking from './pages/AdminMeritRanking';
import { api } from './api/client';

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [activeTab, setActiveTab] = useState('home');
  const [selectedSchemeId, setSelectedSchemeId] = useState(1);
  const [selectedApplicationId, setSelectedApplicationId] = useState(null);
  const [initialLoading, setInitialLoading] = useState(true);

  // Initialize session or default to demo user
  useEffect(() => {
    async function initAuth() {
      const token = localStorage.getItem('mota_token');
      if (token) {
        try {
          const user = await api.auth.getMe();
          setCurrentUser(user);
          if (user.role === 'admin') {
            setActiveTab('admin-dashboard');
          } else {
            setActiveTab('applicant-dashboard');
          }
        } catch (_) {
          localStorage.removeItem('mota_token');
        }
      }
      setInitialLoading(false);
    }
    initAuth();
  }, []);

  const handleLoginSuccess = async (authData) => {
    try {
      const fullProfile = await api.auth.getMe();
      setCurrentUser(fullProfile);
      if (fullProfile.role === 'admin') {
        setActiveTab('admin-dashboard');
      } else {
        setActiveTab('applicant-dashboard');
      }
    } catch (_) {
      setCurrentUser({
        id: authData.user_id,
        email: authData.email,
        role: authData.role,
        full_name: authData.full_name,
      });
      if (authData.role === 'admin') {
        setActiveTab('admin-dashboard');
      } else {
        setActiveTab('applicant-dashboard');
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('mota_token');
    setCurrentUser(null);
    setActiveTab('home');
  };

  // Quick switch between Admin and Applicant for fast judging demo
  const handleSwitchDemo = async () => {
    try {
      if (currentUser?.role === 'admin') {
        // Switch to ST Applicant (Pooja Halba with active deficiency or Birsa Soren)
        let res;
        try {
          res = await api.auth.login('pooja.halba@stmail.in', 'scholar123');
        } catch (_) {
          try {
            res = await api.auth.login('birsa.soren@research.ac.in', 'scholar123');
          } catch (e) {
            res = await api.auth.login('sanjay.marandi@stmail.in', 'scholar123');
          }
        }
        localStorage.setItem('mota_token', res.access_token);
        await handleLoginSuccess(res);
      } else {
        // Switch to MoTA Admin
        const res = await api.auth.login('admin@mota.gov.in', 'admin123');
        localStorage.setItem('mota_token', res.access_token);
        await handleLoginSuccess(res);
      }
    } catch (err) {
      console.error('Demo switch error:', err);
    }
  };

  const handleSelectSchemeToApply = (schemeId) => {
    setSelectedSchemeId(schemeId);
    if (!currentUser) {
      setActiveTab('login');
    } else {
      setActiveTab('apply');
    }
  };

  const handleApplicationSubmitted = (newApp) => {
    setActiveTab('applicant-dashboard');
  };

  const handleSelectAdminApplication = (appId) => {
    setSelectedApplicationId(appId);
    setActiveTab('admin-detail');
  };

  if (initialLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-gov-navy border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-xs font-bold text-slate-700">Connecting to MoTA Digital Portal...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar
        currentUser={currentUser}
        onLogout={handleLogout}
        onSwitchDemo={handleSwitchDemo}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        {activeTab === 'home' && (
          <Home
            onSelectScheme={handleSelectSchemeToApply}
            onOpenLogin={() => setActiveTab('login')}
            currentUser={currentUser}
          />
        )}

        {activeTab === 'login' && (
          <Login onLoginSuccess={handleLoginSuccess} />
        )}

        {activeTab === 'apply' && (
          <ApplyScheme
            schemeId={selectedSchemeId}
            onBack={() => setActiveTab('home')}
            onSuccess={handleApplicationSubmitted}
            currentUser={currentUser}
          />
        )}

        {activeTab === 'applicant-dashboard' && (
          <ApplicantDashboard
            currentUser={currentUser}
            onNavigateApply={() => setActiveTab('home')}
          />
        )}

        {activeTab === 'admin-dashboard' && (
          <AdminDashboard
            onSelectApplication={handleSelectAdminApplication}
            onOpenMeritRanking={() => setActiveTab('merit-ranking')}
          />
        )}

        {activeTab === 'admin-detail' && (
          <AdminApplicationDetail
            applicationId={selectedApplicationId}
            onBack={() => setActiveTab('admin-dashboard')}
            onActionComplete={() => {}}
          />
        )}

        {activeTab === 'merit-ranking' && (
          <AdminMeritRanking
            onBack={() => setActiveTab('admin-dashboard')}
            onSelectApplication={handleSelectAdminApplication}
          />
        )}
      </main>

      {/* Official Government Footer */}
      <footer className="bg-gov-dark text-slate-400 text-xs py-8 border-t border-slate-800 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <p className="font-bold text-white">
              जनजातीय कार्य मंत्रालय <span className="text-slate-500">|</span> Ministry of Tribal Affairs
            </p>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Government of India • SIH 2025 Problem Statement 26239 Prototype
            </p>
          </div>
          <div className="text-center sm:text-right text-[11px] text-slate-500">
            <p>Designed for ST Student Empowerment & Fellowship Transparency</p>
            <p className="mt-0.5 font-mono">FastAPI + React + Tesseract OCR + SQLite/PostgreSQL Ready</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
