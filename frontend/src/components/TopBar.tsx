import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Search, School, User as UserIcon, LogOut, CheckCircle2 } from 'lucide-react';

export const TopBar: React.FC = () => {
  const { user, logout } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');

  const getRoleLabel = () => {
    switch (user?.role) {
      case 'ADMIN': return 'Admin';
      case 'INCHARGE': return 'School Incharge';
      case 'CLASS_TEACHER': return 'Class Teacher';
      case 'SUBJECT_TEACHER': return 'Subject Teacher';
      case 'STUDENT': return 'Student';
      default: return user?.role;
    }
  };

  return (
    <header className="topbar">
      <div className="search-box">
        <Search size={16} color="var(--muted)" />
        <input
          type="text"
          placeholder="Search by Question ID (e.g. Q-8K3F2A, MTH-12...) or text..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        {user?.school_name && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: 'var(--ink-secondary)' }}>
            <School size={16} color="var(--primary)" />
            <span style={{ fontWeight: 600 }}>{user.school_name}</span>
            {user.school_code && (
              <span className="id-chip" title="School Code">{user.school_code}</span>
            )}
          </div>
        )}

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: 34,
            height: 34,
            borderRadius: '50%',
            background: 'var(--primary-light)',
            color: 'var(--primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 600,
            fontSize: '14px'
          }}>
            {user?.full_name?.charAt(0) || <UserIcon size={16} />}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '13px', fontWeight: 600 }}>{user?.full_name}</span>
              {user?.status === 'ACTIVE' ? (
                <span title="Active Account"><CheckCircle2 size={13} color="var(--ok)" /></span>
              ) : (
                <span className="badge badge-unverified" style={{ fontSize: '10px', padding: '2px 6px' }}>Pending</span>
              )}
            </div>
            <span style={{ fontSize: '11px', color: 'var(--muted)' }}>{getRoleLabel()}</span>
          </div>
        </div>

        <button
          onClick={logout}
          className="btn btn-secondary btn-sm"
          title="Sign out"
          style={{ padding: '6px 10px' }}
        >
          <LogOut size={15} />
        </button>
      </div>
    </header>
  );
};
