import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Lock, User, Mail, LogIn, UserPlus, AlertCircle, CheckCircle2, ShieldCheck } from 'lucide-react';
import { setCredentials, setAuthMode } from '../../redux/authSlice';
import { loginUser, registerUser } from '../../api/complaintsApi';
import './AuthScreen.css';

export const AuthScreen = () => {
  const dispatch = useDispatch();
  const { authMode } = useSelector((state) => state.auth);

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSwitchMode = (mode) => {
    setError('');
    setSuccess('');
    setConfirmPassword('');
    dispatch(setAuthMode(mode));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const cleanUsername = username.trim();
    const cleanEmail = email.trim();

    if (!cleanUsername) {
      setError('Please enter your username');
      return;
    }

    if (authMode === 'register') {
      if (!cleanEmail) {
        setError('Please enter your email address');
        return;
      }
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(cleanEmail)) {
        setError('Please enter a valid email address');
        return;
      }
    }

    if (!password) {
      setError('Please enter your password');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      return;
    }
    if (authMode === 'register' && password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      if (authMode === 'login') {
        const data = await loginUser({
          username: cleanUsername,
          password: password,
        });
        dispatch(setCredentials({ user: data.user }));
      } else {
        const data = await registerUser({
          username: cleanUsername,
          email: cleanEmail.toLowerCase(),
          password: password,
        });
        setPassword('');
        setEmail('');
        setConfirmPassword('');
        setSuccess(data.message || 'Account created successfully!');
        dispatch(setAuthMode('login'));
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else if (Array.isArray(detail)) {
        setError(detail[0]?.msg || 'Validation failed. Please verify your input.');
      } else {
        setError(
          authMode === 'login'
            ? 'Invalid username or password'
            : 'Registration failed.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-screen-container">
      {/* Background ambient elements */}
      <div className="auth-ambient-blob blob-1" />
      <div className="auth-ambient-blob blob-2" />

      <div className="auth-screen-card">
        {/* Branding header */}
        <div className="auth-screen-brand">
          <div className="auth-screen-logo">
            <ShieldCheck size={28} />
          </div>
          <div>
            <h1>Pharma Complaint</h1>
            <p>AI-Powered Complaint and Risk Assessment</p>
          </div>
        </div>

        {/* Tab switcher */}
        <div className="auth-screen-tabs">
          <button
            type="button"
            className={`auth-screen-tab ${authMode === 'login' ? 'active' : ''}`}
            onClick={() => handleSwitchMode('login')}
          >
            <LogIn size={15} />
            Sign In
          </button>
          <button
            type="button"
            className={`auth-screen-tab ${authMode === 'register' ? 'active' : ''}`}
            onClick={() => handleSwitchMode('register')}
          >
            <UserPlus size={15} />
            Register
          </button>
        </div>

        {/* Alerts */}
        {error && (
          <div className="auth-screen-alert error">
            <AlertCircle size={18} className="alert-icon" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="auth-screen-alert success">
            <CheckCircle2 size={18} className="alert-icon" />
            <span>{success}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="auth-screen-form" noValidate>
          <div className="auth-fields-group">
            <div className="auth-field">
              <label htmlFor="auth-username">
                {authMode === 'login' ? 'Username or Email' : 'Username'}
              </label>
              <div className="auth-field-input-wrap">
                <User size={16} className="auth-field-icon" />
                <input
                  id="auth-username"
                  type="text"
                  placeholder={authMode === 'login' ? 'Enter username or email' : 'Enter your username '}
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoFocus
                  required
                />
              </div>
            </div>

            {authMode === 'register' && (
              <div className="auth-field">
                <label htmlFor="auth-email">Email Address</label>
                <div className="auth-field-input-wrap">
                  <Mail size={16} className="auth-field-icon" />
                  <input
                    id="auth-email"
                    type="email"
                    placeholder="Ex:- xzy@pharma.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                </div>
              </div>
            )}

            <div className="auth-field">
              <label htmlFor="auth-password">Password</label>
              <div className="auth-field-input-wrap">
                <Lock size={16} className="auth-field-icon" />
                <input
                  id="auth-password"
                  type="password"
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            {authMode === 'register' && (
              <div className="auth-field">
                <label htmlFor="auth-confirm-password">Confirm Password</label>
                <div className="auth-field-input-wrap">
                  <Lock size={16} className="auth-field-icon" />
                  <input
                    id="auth-confirm-password"
                    type="password"
                    placeholder="Re-enter your password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                  />
                </div>
              </div>
            )}
          </div>

          <button
            type="submit"
            className="auth-screen-submit"
            disabled={loading}
          >
            {loading ? (
              <span className="auth-spinner" />
            ) : authMode === 'login' ? (
              <>
                <LogIn size={17} />
                Sign In to Dashboard
              </>
            ) : (
              <>
                <UserPlus size={17} />
                Create Account
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AuthScreen;
