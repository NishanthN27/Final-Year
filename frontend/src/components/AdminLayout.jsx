// src/components/AdminLayout.jsx

import React from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";
import {
  LayoutDashboard,
  ClipboardList,
  FileText,
  Users,
  Settings,
  Bell,
  Sun,
  Moon,
  LogOut,
} from "lucide-react";
import { motion } from "framer-motion";
import { useAuth } from "../contexts/AuthContext";

const AdminLayout = () => {
  const { isDark, toggleTheme } = useTheme();
  const { logout } = useAuth(); // Assuming you have an AuthContext to handle logout
  const location = useLocation();

  const getHeaderTitle = (pathname) => {
    switch (pathname) {
      case '/admin':
      case '/admin/':
        return {
          title: 'Admin Dashboard',
          subtitle: 'Interview System Management Center',
        };
      case '/admin/review-queue':
        return {
          title: 'Review Queue',
          subtitle: 'Manage pending interview questions',
        };
      case '/admin/rubrics':
        return {
          title: 'Rubric Editor',
          subtitle: 'Create and manage evaluation rubrics',
        };
      case '/admin/users':
        return {
          title: 'User Management',
          subtitle: 'View and manage system users',
        };
      default:
        return {
          title: 'Admin Panel',
          subtitle: 'Welcome',
        };
    }
  };

  const { title, subtitle } = getHeaderTitle(location.pathname);

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-slate-900">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 w-64 bg-white dark:bg-slate-800 shadow-lg border-r border-slate-200 dark:border-slate-700 p-6 flex flex-col justify-between">
        <div>
          <h2 className="text-xl font-extrabold tracking-tight text-slate-800 dark:text-white mb-8 flex items-center">
            <LayoutDashboard className="w-6 h-6 mr-2 text-slate-600" />
            Admin Panel
          </h2>
          <nav className="space-y-3">
            <Link
              to="/admin"
              className="flex items-center px-3 py-2 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
            >
              <LayoutDashboard className="w-5 h-5 mr-3 text-slate-600" /> Dashboard
            </Link>
            <Link
              to="/admin/review-queue"
              className="flex items-center px-3 py-2 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
            >
              <ClipboardList className="w-5 h-5 mr-3 text-slate-600" /> Review Queue
            </Link>
            <Link
              to="/admin/rubrics"
              className="flex items-center px-3 py-2 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
            >
              <FileText className="w-5 h-5 mr-3 text-slate-600" /> Rubrics
            </Link>
            <Link
              to="/admin/users"
              className="flex items-center px-3 py-2 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
            >
              <Users className="w-5 h-5 mr-3 text-slate-600" /> Users
            </Link>
          </nav>
        </div>

        {/* Settings button at the bottom */}
        <div className="mt-auto pt-6 border-t border-slate-200 dark:border-slate-700">
          <button
            onClick={() => alert('Settings will be implemented here.')} // Placeholder for settings functionality
            className="flex items-center w-full px-3 py-2 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition"
          >
            <Settings className="w-5 h-5 mr-3 text-slate-600" /> Settings
          </button>
        </div>
      </aside>

      {/* Main Content Area with Header */}
      <div className="flex-1 ml-0 lg:ml-64">
        {/* Header */}
        <header className="bg-white dark:bg-slate-800 shadow-md border-b border-slate-200 dark:border-slate-700 sticky top-0 z-40">
          <div className="px-6 py-6 flex justify-between items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h1 className="text-3xl font-extrabold tracking-tight text-slate-800 dark:text-white">
                {title}
              </h1>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{subtitle}</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="flex items-center space-x-4"
            >
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-slate-600 dark:text-slate-400">System Online</span>
              </div>

              {/* Theme Toggle Button */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
                title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDark ? (
                  <Sun className="w-5 h-5 text-slate-600 dark:text-slate-300" />
                ) : (
                  <Moon className="w-5 h-5 text-slate-600 dark:text-slate-300" />
                )}
              </button>

              {/* Sign Out Button */}
              <button
                onClick={logout}
                className={`font-semibold py-2 px-4 rounded-lg flex items-center transition-colors ${isDark
                    ? 'bg-slate-700 hover:bg-red-500 text-white'
                    : 'bg-red-300 hover:bg-red-500 text-white'
                  }`}
              >
                <LogOut className="w-5 h-5 mr-2" />
                Sign Out
              </button>
            </motion.div>
          </div>
        </header>

        {/* This is where the nested routes will be rendered */}
        <Outlet />
      </div>
    </div>
  );
};

export default AdminLayout;