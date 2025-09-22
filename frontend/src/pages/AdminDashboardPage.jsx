import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { useTheme } from "../contexts/ThemeContext";
import {
  ClipboardList,
  FileText,
  Users,
  TrendingUp,
  CheckCircle,
  Activity,
  BarChart3,
  Zap, // Make sure to import Zap
  Bell
} from "lucide-react";
import LoadingSpinner from "../components/LoadingSpinner"; // Make sure to import LoadingSpinner

const AdminDashboardPage = () => {
  const { isDark } = useTheme();
  const [stats, setStats] = useState({
    pendingReviews: 12,
    activeRubrics: 8,
    totalUsers: 1245,
    approvedToday: 7,
  });

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading data
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 800);
    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return (
      <div className={`min-h-screen flex ${isDark ? 'bg-slate-900' : 'bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50'}`}>
        <div className="flex-1 flex items-center justify-center">
          <LoadingSpinner text="Loading dashboard..." />
        </div>
      </div>
    );
  }

  return (
    <main className="px-6 py-6">
      
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-8"
      >
        <div className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 p-6 text-center">
          <h2 className="text-xl font-bold text-slate-800 dark:text-white mb-2">
            Welcome to the Interview System
          </h2>
          <p className="text-slate-600 dark:text-slate-300 text-sm max-w-2xl mx-auto">
            Manage interview questions, review submissions, and configure evaluation rubrics.
          </p>
        </div>
      </motion.div>

      {/* Action Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        
        {/* Review Queue */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="group bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-xl shadow-md border border-slate-200 dark:border-slate-700 hover:shadow-xl hover:border-blue-200 transition-all duration-300 transform hover:-translate-y-1"
        >
          <div className="p-6">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                <ClipboardList className="w-6 h-6 text-white" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-1">
                  Review Queue
                </h3>
                <p className="text-slate-600 dark:text-slate-300 text-sm">
                  Review and approve pending interview questions
                </p>
              </div>
            </div>
            <div className="bg-blue-50 dark:bg-blue-900/30 rounded-lg p-3 mb-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">Pending Reviews</span>
                <span className="text-xl font-bold text-blue-600 dark:text-blue-400">12</span>
              </div>
            </div>
            <Link
              to="/admin/review-queue"
              className="block w-full text-center py-3 px-4 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 shadow-md transition"
            >
              View Review Queue
            </Link>
          </div>
        </motion.div>

        {/* Rubrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="group bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-xl shadow-md border border-slate-200 dark:border-slate-700 hover:shadow-xl hover:border-emerald-200 transition-all duration-300 transform hover:-translate-y-1"
        >
          <div className="p-6">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-1">
                  Evaluation Rubrics
                </h3>
                <p className="text-slate-600 dark:text-slate-300 text-sm">
                  Create and manage evaluation criteria
                </p>
              </div>
            </div>
            <div className="bg-emerald-50 dark:bg-emerald-900/30 rounded-lg p-3 mb-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-emerald-700 dark:text-emerald-300">Active Rubrics</span>
                <span className="text-xl font-bold text-emerald-600 dark:text-emerald-400">8</span>
              </div>
            </div>
            <Link
              to="/admin/rubrics"
              className="block w-full text-center py-3 px-4 rounded-lg text-sm font-semibold text-white bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 shadow-md transition"
            >
              Manage Rubrics
            </Link>
          </div>
        </motion.div>
      </div>

      {/* Enhanced Stats Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="mt-8"
      >
        <h3 className="text-xl font-bold text-slate-800 dark:text-white mb-6 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2 text-slate-600" />
          System Overview
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.7 }}
            className="p-6 bg-white dark:bg-slate-800 rounded-xl shadow-md border border-slate-200 dark:border-slate-700 hover:shadow-lg transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 bg-slate-600 rounded-lg flex items-center justify-center">
                <ClipboardList className="w-5 h-5 text-white" />
              </div>
              <TrendingUp className="w-4 h-4 text-green-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">Pending Reviews</p>
              <h4 className="text-2xl font-bold text-slate-800 dark:text-white">{stats.pendingReviews}</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">+15% from last week</p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.8 }}
            className="p-6 bg-white dark:bg-slate-800 rounded-xl shadow-md border border-slate-200 dark:border-slate-700 hover:shadow-lg transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 bg-slate-600 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <CheckCircle className="w-4 h-4 text-green-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">Active Rubrics</p>
              <h4 className="text-2xl font-bold text-slate-800 dark:text-white">{stats.activeRubrics}</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">+2 this month</p>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.9 }}
            className="p-6 bg-white dark:bg-slate-800 rounded-xl shadow-md border border-slate-200 dark:border-slate-700 hover:shadow-lg transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="w-10 h-10 bg-slate-600 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5 text-white" />
              </div>
              <Activity className="w-4 h-4 text-green-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">Total Users</p>
              <h4 className="text-2xl font-bold text-slate-800 dark:text-white">{stats.totalUsers.toLocaleString()}</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">+23% growth</p>
            </div>
          </motion.div>
        </div>
      </motion.div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
          className="bg-white dark:bg-slate-800 rounded-xl shadow-md border border-slate-200 dark:border-slate-700 p-6"
        >
          <h4 className="text-lg font-bold text-slate-800 dark:text-white mb-4 flex items-center">
            <Bell className="w-5 h-5 mr-2 text-slate-600" />
            Recent Activity
          </h4>
          <div className="space-y-3">
            <div className="flex items-center p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
              <CheckCircle className="w-4 h-4 text-green-500 mr-3" />
              <span className="text-sm text-slate-700 dark:text-slate-300">{stats.approvedToday} questions approved today</span>
            </div>
            <div className="flex items-center p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
              <FileText className="w-4 h-4 text-slate-600 mr-3" />
              <span className="text-sm text-slate-700 dark:text-slate-300">2 new rubrics created this week</span>
            </div>
            <div className="flex items-center p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
              <Activity className="w-4 h-4 text-slate-600 mr-3" />
              <span className="text-sm text-slate-700 dark:text-slate-300">System backup completed successfully</span>
            </div>
          </div>
        </motion.div>
      </div>

    </main>
  );
};

export default AdminDashboardPage;