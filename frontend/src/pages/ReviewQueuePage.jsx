import React, { useState, useEffect } from 'react';
import { reviewQueueApi, handleApiError } from '../services/adminApi';
import ReviewQueueItem from '../components/ReviewQueueItem';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useTheme } from '../contexts/ThemeContext';
import {
  ClipboardList,
  FileText,
  Users,
} from 'lucide-react';

const ReviewQueuePage = () => {
  const { isDark } = useTheme();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: 'all',
    domain: 'all',
    difficulty: 'all',
    search: ''
  });
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0
  });

  // Load review queue items
  const loadItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (filters.status !== 'all') params.status = filters.status;
      if (filters.domain !== 'all') params.domain = filters.domain;
      if (filters.difficulty !== 'all') params.difficulty = filters.difficulty;
      if (filters.search) params.search = filters.search;

      const data = await reviewQueueApi.getItems(params);
      setItems(data.items || []);
      setStats(data.stats || stats);
    } catch (err) {
      const errorInfo = handleApiError(err);
      setError(errorInfo.error);
    } finally {
      setLoading(false);
    }
  };

  // Load items on component mount and filter changes
  useEffect(() => {
    loadItems();
  }, [filters]);

  // Handle approve action
  const handleApprove = async (itemId, reviewNotes) => {
    try {
      await reviewQueueApi.approveItem(itemId, reviewNotes);
      await loadItems(); // Refresh the list
    } catch (err) {
      const errorInfo = handleApiError(err);
      setError(errorInfo.error);
    }
  };

  // Handle reject action
  const handleReject = async (itemId, reviewNotes) => {
    try {
      await reviewQueueApi.rejectItem(itemId, reviewNotes);
      await loadItems(); // Refresh the list
    } catch (err) {
      const errorInfo = handleApiError(err);
      setError(errorInfo.error);
    }
  };

  // Handle edit action (placeholder for now)
  const handleEdit = (item) => {
    // TODO: Implement edit functionality
    console.log('Edit item:', item);
    alert('Edit functionality will be implemented in the next phase');
  };

  // Handle delete action
  const handleDelete = async (itemId) => {
    if (!confirm('Are you sure you want to delete this item?')) return;
    
    try {
      await reviewQueueApi.deleteItem(itemId);
      await loadItems(); // Refresh the list
    } catch (err) {
      const errorInfo = handleApiError(err);
      setError(errorInfo.error);
    }
  };

  // Handle filter changes
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  // Clear all filters
  const clearFilters = () => {
    setFilters({
      status: 'all',
      domain: 'all',
      difficulty: 'all',
      search: ''
    });
  };

  return (
    <div className={`p-6 ${isDark ? 'dark' : ''}`}>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className={`p-6 rounded-2xl shadow-xl border ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white/70 backdrop-blur-sm border-white/20'} transition-all duration-300 transform hover:-translate-y-1`}>
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-slate-500 to-slate-600 rounded-xl flex items-center justify-center mr-4">
              <ClipboardList className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className={`text-2xl font-bold ${isDark ? 'text-white' : 'text-slate-800'}`}>{stats.total}</div>
              <div className={`font-medium ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>Total Items</div>
            </div>
          </div>
        </div>
        <div className={`p-6 rounded-2xl shadow-xl border ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white/70 backdrop-blur-sm border-white/20'} transition-all duration-300 transform hover:-translate-y-1`}>
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-xl flex items-center justify-center mr-4">
              <ClipboardList className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className={`text-2xl font-bold ${isDark ? 'text-yellow-400' : 'text-yellow-600'}`}>{stats.pending}</div>
              <div className={`font-medium ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>Pending Review</div>
            </div>
          </div>
        </div>
        <div className={`p-6 rounded-2xl shadow-xl border ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white/70 backdrop-blur-sm border-white/20'} transition-all duration-300 transform hover:-translate-y-1`}>
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center mr-4">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className={`text-2xl font-bold ${isDark ? 'text-green-400' : 'text-green-600'}`}>{stats.approved}</div>
              <div className={`font-medium ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>Approved</div>
            </div>
          </div>
        </div>
        <div className={`p-6 rounded-2xl shadow-xl border ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white/70 backdrop-blur-sm border-white/20'} transition-all duration-300 transform hover:-translate-y-1`}>
          <div className="flex items-center">
            <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-pink-500 rounded-xl flex items-center justify-center mr-4">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className={`text-2xl font-bold ${isDark ? 'text-red-400' : 'text-red-600'}`}>{stats.rejected}</div>
              <div className={`font-medium ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>Rejected</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className={`${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white/70 backdrop-blur-sm border-white/20'} p-6 rounded-2xl shadow-xl border mb-8`}>
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex-1 min-w-64">
            <input
              type="text"
              placeholder="Search questions..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className={`w-full px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ${isDark ? 'bg-slate-700 border-slate-600 text-white placeholder-slate-400' : 'bg-white/70 border-slate-300 text-slate-900 placeholder-slate-500 hover:bg-white/90'}`}
            />
          </div>
          <select
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className={`px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ${isDark ? 'bg-slate-700 border-slate-600 text-white' : 'bg-white/70 border-slate-300 text-slate-900 hover:bg-white/90'}`}
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
          <select
            value={filters.domain}
            onChange={(e) => handleFilterChange('domain', e.target.value)}
            className={`px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ${isDark ? 'bg-slate-700 border-slate-600 text-white' : 'bg-white/70 border-slate-300 text-slate-900 hover:bg-white/90'}`}
          >
            <option value="all">All Domains</option>
            <option value="programming">Programming</option>
            <option value="algorithms">Algorithms</option>
            <option value="data-structures">Data Structures</option>
            <option value="system-design">System Design</option>
            <option value="databases">Databases</option>
          </select>
          <select
            value={filters.difficulty}
            onChange={(e) => handleFilterChange('difficulty', e.target.value)}
            className={`px-4 py-3 border rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ${isDark ? 'bg-slate-700 border-slate-600 text-white' : 'bg-white/70 border-slate-300 text-slate-900 hover:bg-white/90'}`}
          >
            <option value="all">All Difficulties</option>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
          <button
            onClick={clearFilters}
            className={`px-6 py-3 border rounded-xl transition-all duration-200 font-medium ${isDark ? 'text-slate-300 border-slate-600 bg-slate-700 hover:bg-slate-600' : 'text-slate-600 hover:text-slate-800 border-slate-300 bg-white/70 hover:bg-white/90'}`}
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <ErrorMessage
          message={error}
          onRetry={loadItems}
          className="mb-6"
        />
      )}

      {/* Loading State */}
      {loading && (
        <LoadingSpinner size="large" text="Loading review queue..." />
      )}

      {/* Items List */}
      {!loading && (
        <div className="space-y-6">
          {items.length === 0 ? (
            <div className={`text-center py-16 rounded-2xl shadow-xl border ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white/70 backdrop-blur-sm border-white/20'}`}>
              <div className={`text-6xl mb-6 ${isDark ? 'text-slate-400' : 'text-slate-400'}`}>📝</div>
              <h3 className={`text-xl font-semibold mb-3 ${isDark ? 'text-white' : 'text-slate-800'}`}>No items found</h3>
              <p className={`max-w-md mx-auto ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
                {Object.values(filters).some(f => f !== 'all' && f !== '')
                  ? 'Try adjusting your filters to see more results.'
                  : 'The review queue is empty.'}
              </p>
            </div>
          ) : (
            items.map((item) => (
              <ReviewQueueItem
                key={item.id}
                item={item}
                onApprove={handleApprove}
                onReject={handleReject}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default ReviewQueuePage;