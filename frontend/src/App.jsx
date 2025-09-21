import React, { useState, useEffect } from 'react';
import './App.css'; 

const phrases = [
  "Prepared for the interview?",
  "Let's ace the interview!"
];

function App() {
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
  const [currentText, setCurrentText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [typingSpeed, setTypingSpeed] = useState(75); // MODIFIED: Was 100

  useEffect(() => {
    const currentPhrase = phrases[currentPhraseIndex];

    if (!isDeleting && currentText === currentPhrase) {
      const pauseTimeout = setTimeout(() => {
        setIsDeleting(true);
      }, 2000);
      return () => clearTimeout(pauseTimeout);
    } 
    
    else if (isDeleting && currentText === '') {
      const pauseTimeout = setTimeout(() => {
        setIsDeleting(false);
        setCurrentPhraseIndex((prev) => (prev + 1) % phrases.length);
      }, 500); 
      return () => clearTimeout(pauseTimeout);
    }

    const mainTimeout = setTimeout(() => {
      if (isDeleting) {
        setTypingSpeed(35); // MODIFIED: Was 50 
        setCurrentText(currentPhrase.substring(0, currentText.length - 1));
      } else {
        setTypingSpeed(75); // MODIFIED: Was 100
        setCurrentText(currentPhrase.substring(0, currentText.length + 1));
      }
    }, typingSpeed); 

    return () => clearTimeout(mainTimeout);
    
  }, [currentText, isDeleting, currentPhraseIndex, typingSpeed, phrases]);

  return (
    <div className="landing-container">
      
      <div className="landing-promo">
        <div className="promo-content">
          <div className="animated-heading">
            <h1>
              {currentText}
              <span className="blinking-cursor">|</span>
            </h1>
          </div>
        </div>
      </div>

      <div className="landing-auth">
        <div className="auth-content">
          <h2 className="brand-logo">InterviewPrep</h2>
          <div className="button-group">
            <button className="btn btn-primary">Sign In</button>
            <button className="btn btn-secondary">Sign Up</button>
          </div>
        </div>
      </div>

    </div>
  );
}

export default App;