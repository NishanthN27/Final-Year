import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Send, Mic, Paperclip, X, FileText, LoaderCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import GeminiSidebar from '../components/GeminiSidebar';
import { useTheme } from '../contexts/ThemeContext';
import { uploadResume, startInterview } from '../services/sessionApi';
import ErrorMessage from '../components/ErrorMessage';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';

const CandidateDashboardPage = () => {
  const { user, token, isLoading: isAuthLoading } = useAuth();
  const { isDark } = useTheme();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [resumeText, setResumeText] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isProcessed, setIsProcessed] = useState(false); // New state

  const handleTextChange = (e) => {
    setResumeText(e.target.value);
    if (resumeFile) setResumeFile(null);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setResumeFile(file);
      setResumeText('');
    }
  };

  const handleFileDismiss = () => {
    setResumeFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSubmit = async () => {
    setError(null);
    if (!token) {
      setError("Authentication error. Please log in again.");
      return;
    }

    const hasText = resumeText.trim() !== '';
    const hasFile = resumeFile !== null;
    if (!hasText && !hasFile) return;

    setIsLoading(true);
    try {
      let response;
      if (hasFile) {
        // Flow 1: Upload file, then get text
        const uploadResponse = await uploadResume(resumeFile, token);
        response = await startInterview({ file_url: uploadResponse.file_url }, token);
      } else {
        // Flow 2: Get "processed" text (in this case, just confirm)
        response = await startInterview({ resume_text: resumeText }, token);
      }
      
      console.log("Resume processed.");
      
      // Set the text area to the extracted text
      setResumeText(response.raw_text);
      setResumeFile(null); // Clear the file input
      setIsProcessed(true); // Mark as processed
      
      // TODO: Navigate to the next step
      // navigate('/interview/session-id');

    } catch (err) {
      setError(err.detail || "An unexpected error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const canSubmit = (resumeText.trim() !== '' || resumeFile !== null) && !isLoading && !isAuthLoading && !isProcessed;

  if (isAuthLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-white dark:bg-slate-900">
        <LoadingSpinner text="Authenticating..." />
      </div>
    );
  }

  return (
    <div className={`flex min-h-screen ${isDark ? 'dark' : ''}`}>
      <GeminiSidebar
        isCollapsed={isSidebarCollapsed}
        setIsCollapsed={setIsSidebarCollapsed}
      />
      <main className="flex-1 flex flex-col bg-white dark:bg-slate-900 transition-colors duration-300">
        <div className="flex-1 flex flex-col items-center w-full px-4 pb-4 overflow-y-auto">
          <div className="w-full max-w-4xl mx-auto flex flex-col justify-between h-full">
            <div className="pt-16">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
              >
                <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-slate-700 via-slate-500 to-slate-700 dark:from-slate-200 dark:via-slate-400 dark:to-slate-200 mb-4">
                  Hello, {user?.firstName || 'Candidate'}.
                </h1>
                <h2 className="text-4xl font-semibold text-slate-500 dark:text-slate-400">
                  Ready to start your interview?
                </h2>
              </motion.div>
            </div>
            
            <div className="mt-auto w-full pt-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
              >
                {error && <ErrorMessage message={error} onRetry={handleSubmit} />}
                
                {isProcessed && !error && (
                  <div className="mb-3 ml-2 p-3 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-lg text-sm font-semibold">
                    Resume processed successfully! The text is now visible below.
                  </div>
                )}

                {resumeFile && !isProcessed && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-3 ml-2 flex"
                  >
                    <div className="bg-slate-200 dark:bg-slate-700 rounded-lg p-2 flex items-center text-sm">
                       <FileText className="w-4 h-4 mr-2 text-slate-600 dark:text-slate-300" />
                       <span className="text-slate-800 dark:text-white font-medium">{resumeFile.name}</span>
                       <button onClick={handleFileDismiss} className="ml-2 p-1 rounded-full hover:bg-slate-300 dark:hover:bg-slate-600" disabled={isLoading}>
                         <X className="w-4 h-4 text-slate-600 dark:text-slate-300"/>
                       </button>
                    </div>
                  </motion.div>
                )}

                <div className="relative">
                  <textarea
                    rows="1"
                    value={resumeText}
                    onChange={handleTextChange}
                    // Disable if loading, or if analysis is complete
                    disabled={isLoading || isAuthLoading || isProcessed}
                    placeholder={isProcessed ? "Resume text is loaded." : (resumeFile ? "File attached. Press the arrow to start." : "Paste resume, or upload a file...")}
                    className="w-full pl-12 pr-24 py-4 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-white border-2 border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition resize-none disabled:cursor-not-allowed no-scrollbar"
                    onInput={(e) => {
                      e.target.style.height = 'auto';
                      e.target.style.height = `${e.target.scrollHeight}px`;
                    }}
                  />
                  <div className="absolute left-3 top-1/2 -translate-y-1/2 flex items-center">
                    {/* Hide paperclip if text is present, loading, or processed */}
                    {!resumeText && !isLoading && !isProcessed && (
                        <>
                            <input
                                type="file"
                                id="resume-upload"
                                className="hidden"
                                onChange={handleFileChange}
                                ref={fileInputRef}
                                accept=".pdf,.doc,.docx,.txt"
                            />
                            <label htmlFor="resume-upload" className="p-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 transition-colors cursor-pointer">
                                <Paperclip className="w-5 h-5" />
                            </label>
                        </>
                    )}
                  </div>
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center space-x-2">
                    <button className="p-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 transition-colors" disabled={isLoading || isAuthLoading || isProcessed}>
                      <Mic className="w-5 h-5" />
                    </button>
                    <button
                      onClick={handleSubmit}
                      disabled={!canSubmit}
                      className="p-2 rounded-full bg-blue-500 text-white transition-colors disabled:bg-slate-300 dark:disabled:bg-slate-600 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                      {isLoading ? <LoaderCircle className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                    </button>
                  </div>
                </div>
              </motion.div>
               <p className="text-center text-xs text-slate-500 dark:text-slate-400 mt-2 px-4">
                This is an AI-powered interview system. Your responses will be recorded and analyzed.
              </p>
            </div>

          </div>
        </div>
      </main>
    </div>
  );
};

export default CandidateDashboardPage;