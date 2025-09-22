import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext'; // To get logout function

const CandidateDashboardPage = () => {
  const { logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center text-center p-4">
      <div className="bg-white p-10 rounded-lg shadow-lg max-w-lg w-full">
        <div className="mb-4">
          <svg className="w-16 h-16 text-blue-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-14 0h14z"></path>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L15.232 5.232z"></path>
          </svg>
        </div>
        <h1 className="text-3xl font-bold text-gray-800 mb-2">
          Dashboard Under Construction
        </h1>
        <p className="text-gray-600 mb-6">
          The dashboard for candidates is currently being developed. Please check back later!
        </p>
        <button
          onClick={logout}
          className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition-colors duration-300"
        >
          Sign Out
        </button>
      </div>
    </div>
  );
};

export default CandidateDashboardPage;