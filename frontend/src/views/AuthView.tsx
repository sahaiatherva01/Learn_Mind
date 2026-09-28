import React, { useState } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { BrainCircuit } from 'lucide-react';

export const AuthView: React.FC = () => {
  const { login } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [loginMethod, setLoginMethod] = useState<'email' | 'roll_number' | 'teacher_code'>('email');
  const [registerRole, setRegisterRole] = useState<'student' | 'teacher' | 'school'>('student');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Form Fields
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [schoolCode, setSchoolCode] = useState('');
  const [rollNumber, setRollNumber] = useState('');
  const [teacherCode, setTeacherCode] = useState('');
  const [schoolName, setSchoolName] = useState('');
  const [teacherRole, setTeacherRole] = useState<'SUBJECT_TEACHER' | 'CLASS_TEACHER'>('SUBJECT_TEACHER');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      let payload: any = { password };
      if (loginMethod === 'email') payload.email = email.trim().toLowerCase();
      else if (loginMethod === 'roll_number') {
        payload.roll_number = rollNumber.trim().toUpperCase();
        payload.school_code = schoolCode.trim().toUpperCase();
      } else if (loginMethod === 'teacher_code') {
        payload.teacher_code = teacherCode.trim().toUpperCase();
      }

      const res = await api.login(payload);
      login(res.access_token, res.user);
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMsg(null);
    try {
      if (registerRole === 'student') {
        const res = await api.registerStudent({
          school_code: schoolCode.trim().toUpperCase(),
          full_name: fullName.trim(),
          password,
          email: email ? email.trim().toLowerCase() : undefined,
          roll_number: rollNumber ? rollNumber.trim().toUpperCase() : undefined,
          teacher_code: teacherCode ? teacherCode.trim().toUpperCase() : undefined,
        });
        login(res.access_token, res.user);
      } else if (registerRole === 'teacher') {
        await api.registerTeacher({
          school_code: schoolCode.trim().toUpperCase(),
          email: email.trim().toLowerCase(),
          full_name: fullName.trim(),
          password,
          role: teacherRole,
        });
        setSuccessMsg('Registration submitted! Your account is pending approval from your school Incharge.');
        setMode('login');
      } else if (registerRole === 'school') {
        const res = await api.registerSchool({
          school_name: schoolName.trim(),
          school_code: schoolCode.trim().toUpperCase(),
          board: 'ICSE_ISC',
          admin_name: fullName.trim(),
          admin_email: email.trim().toLowerCase(),
          admin_password: password,
          wing_name: 'Senior Academic Wing',
        });
        login(res.access_token, res.user);
      }
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'var(--bg)',
      padding: '24px',
    }}>
      <div style={{
        maxWidth: '480px',
        width: '100%',
        background: 'var(--surface)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--line)',
        boxShadow: 'var(--shadow-lg)',
        padding: '36px 32px',
      }}>
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: 'var(--radius-md)',
            background: 'var(--primary)',
            color: 'var(--primary-ink)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '12px',
          }}>
            <BrainCircuit size={28} />
          </div>
          <h1 style={{ fontSize: '22px', fontWeight: 700 }}>Learn_Mind</h1>
          <p style={{ fontSize: '13px', color: 'var(--muted)', marginTop: '4px' }}>
            Academic Intelligence Platform for ICSE / ISC / JEE / NEET
          </p>
        </div>

        {/* Mode Toggle (Login vs Register) */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          background: 'var(--line-light)',
          padding: '4px',
          borderRadius: 'var(--radius-md)',
          marginBottom: '24px',
        }}>
          <button
            type="button"
            className={`btn btn-sm ${mode === 'login' ? 'btn-primary' : ''}`}
            onClick={() => { setMode('login'); setError(null); }}
            style={{
              background: mode === 'login' ? 'var(--surface)' : 'transparent',
              color: mode === 'login' ? 'var(--ink)' : 'var(--muted)',
              border: mode === 'login' ? '1px solid var(--line)' : 'none',
              boxShadow: mode === 'login' ? 'var(--shadow-sm)' : 'none',
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={`btn btn-sm ${mode === 'register' ? 'btn-primary' : ''}`}
            onClick={() => { setMode('register'); setError(null); }}
            style={{
              background: mode === 'register' ? 'var(--surface)' : 'transparent',
              color: mode === 'register' ? 'var(--ink)' : 'var(--muted)',
              border: mode === 'register' ? '1px solid var(--line)' : 'none',
              boxShadow: mode === 'register' ? 'var(--shadow-sm)' : 'none',
            }}
          >
            Create Account
          </button>
        </div>

        {error && (
          <div style={{
            background: 'var(--bad-bg)',
            color: 'var(--bad)',
            border: '1px solid rgba(214, 51, 108, 0.2)',
            padding: '10px 14px',
            borderRadius: 'var(--radius-md)',
            marginBottom: '18px',
            fontSize: '13px',
          }}>
            {error}
          </div>
        )}

        {successMsg && (
          <div style={{
            background: 'var(--ok-bg)',
            color: 'var(--ok)',
            border: '1px solid rgba(47, 158, 68, 0.2)',
            padding: '10px 14px',
            borderRadius: 'var(--radius-md)',
            marginBottom: '18px',
            fontSize: '13px',
          }}>
            {successMsg}
          </div>
        )}

        {/* LOGIN FORM */}
        {mode === 'login' && (
          <form onSubmit={handleLogin}>
            {/* Login Method Tabs */}
            <div style={{ display: 'flex', gap: '6px', marginBottom: '16px' }}>
              <button
                type="button"
                className={`btn btn-sm ${loginMethod === 'email' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setLoginMethod('email')}
                style={{ flex: 1, fontSize: '12px', padding: '6px 4px' }}
              >
                Email
              </button>
              <button
                type="button"
                className={`btn btn-sm ${loginMethod === 'roll_number' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setLoginMethod('roll_number')}
                style={{ flex: 1, fontSize: '12px', padding: '6px 4px' }}
              >
                Roll Number
              </button>
              <button
                type="button"
                className={`btn btn-sm ${loginMethod === 'teacher_code' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setLoginMethod('teacher_code')}
                style={{ flex: 1, fontSize: '12px', padding: '6px 4px' }}
              >
                Teacher Code
              </button>
            </div>

            {loginMethod === 'email' && (
              <div className="form-group">
                <label className="form-label">Email Address</label>
                <input
                  type="email"
                  className="input"
                  placeholder="name@school.edu"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            )}

            {loginMethod === 'roll_number' && (
              <>
                <div className="form-group">
                  <label className="form-label">School Code</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="e.g. STXAVIER"
                    required
                    value={schoolCode}
                    onChange={(e) => setSchoolCode(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Student Roll Number</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="e.g. ROLL-10A-042"
                    required
                    value={rollNumber}
                    onChange={(e) => setRollNumber(e.target.value)}
                  />
                </div>
              </>
            )}

            {loginMethod === 'teacher_code' && (
              <div className="form-group">
                <label className="form-label">Teacher-Issued Code</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g. TC-MATHS-991"
                  required
                  value={teacherCode}
                  onChange={(e) => setTeacherCode(e.target.value)}
                />
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="input"
                placeholder="••••••••"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '12px' }}
            >
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>
          </form>
        )}

        {/* REGISTER FORM */}
        {mode === 'register' && (
          <form onSubmit={handleRegister}>
            {/* Role Select Tabs */}
            <div style={{ display: 'flex', gap: '6px', marginBottom: '16px' }}>
              <button
                type="button"
                className={`btn btn-sm ${registerRole === 'student' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setRegisterRole('student')}
                style={{ flex: 1, fontSize: '12px' }}
              >
                Student
              </button>
              <button
                type="button"
                className={`btn btn-sm ${registerRole === 'teacher' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setRegisterRole('teacher')}
                style={{ flex: 1, fontSize: '12px' }}
              >
                Teacher
              </button>
              <button
                type="button"
                className={`btn btn-sm ${registerRole === 'school' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setRegisterRole('school')}
                style={{ flex: 1, fontSize: '12px' }}
              >
                New School
              </button>
            </div>

            {registerRole === 'school' && (
              <div className="form-group">
                <label className="form-label">School Name</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g. St. Xavier's Senior High School"
                  required
                  value={schoolName}
                  onChange={(e) => setSchoolName(e.target.value)}
                />
              </div>
            )}

            <div className="form-group">
              <label className="form-label">School Code</label>
              <input
                type="text"
                className="input"
                placeholder="e.g. STXAVIER"
                required
                value={schoolCode}
                onChange={(e) => setSchoolCode(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                className="input"
                placeholder="Your full name"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>

            {registerRole !== 'student' && (
              <div className="form-group">
                <label className="form-label">Official Email Address</label>
                <input
                  type="email"
                  className="input"
                  placeholder="name@school.edu"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            )}

            {registerRole === 'student' && (
              <>
                <div className="form-group">
                  <label className="form-label">Email (Optional)</label>
                  <input
                    type="email"
                    className="input"
                    placeholder="student@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Roll Number (Optional)</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="e.g. ROLL-10A-042"
                    value={rollNumber}
                    onChange={(e) => setRollNumber(e.target.value)}
                  />
                </div>
              </>
            )}

            {registerRole === 'teacher' && (
              <div className="form-group">
                <label className="form-label">Requested Teaching Role</label>
                <select
                  className="select"
                  value={teacherRole}
                  onChange={(e: any) => setTeacherRole(e.target.value)}
                >
                  <option value="SUBJECT_TEACHER">Subject Teacher</option>
                  <option value="CLASS_TEACHER">Class Teacher</option>
                </select>
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                className="input"
                placeholder="At least 6 characters"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '12px' }}
            >
              {loading ? 'Creating...' : registerRole === 'school' ? 'Register School & Incharge' : 'Create Account'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
