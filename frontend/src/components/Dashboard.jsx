import React, { useEffect, useState } from 'react';
import './Dashboard.css';

const Dashboard = () => {
  const [userInfo, setUserInfo] = useState(null);
  const [permissions, setPermissions] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);
  const [mfaStatus, setMfaStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          window.location.href = '/login';
          return;
        }

        const headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };

        // Fetch user info
        const userResponse = await fetch('/api/v1/users/me', { headers });
        if (!userResponse.ok) {
          throw new Error('Failed to fetch user info');
        }
        const userData = await userResponse.json();
        setUserInfo(userData);

        // Fetch permissions
        const permissionsResponse = await fetch('/api/v1/permissions/me', { headers });
        if (permissionsResponse.ok) {
          const permissionsData = await permissionsResponse.json();
          setPermissions(permissionsData.permissions || []);
        }

        // Fetch system status
        const statusResponse = await fetch('/api/v1/status', { headers });
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          setSystemStatus(statusData);
        }

        // Fetch MFA status
        const mfaResponse = await fetch('/api/v1/mfa/status', { headers });
        if (mfaResponse.ok) {
          const mfaData = await mfaResponse.json();
          setMfaStatus(mfaData);
        }

      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError('Failed to load dashboard data');
        if (error.message.includes('fetch user info')) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>NoxSuite Dashboard</h1>
          <div className="user-actions">
            <span className="welcome-text">Welcome, {userInfo?.username}</span>
            <span className="user-role">{userInfo?.role}</span>
            <button onClick={handleLogout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        {/* User Info Card */}
        <div className="dashboard-card user-info-card">
          <h3>👤 User Profile</h3>
          <div className="user-details">
            <div className="detail-row">
              <span className="label">Username:</span>
              <span className="value">{userInfo?.username}</span>
            </div>
            <div className="detail-row">
              <span className="label">Email:</span>
              <span className="value">{userInfo?.email}</span>
            </div>
            <div className="detail-row">
              <span className="label">Role:</span>
              <span className={`value role-badge ${userInfo?.role}`}>
                {userInfo?.role}
              </span>
            </div>
            <div className="detail-row">
              <span className="label">Last Login:</span>
              <span className="value">
                {userInfo?.last_login ? new Date(userInfo.last_login).toLocaleString() : 'N/A'}
              </span>
            </div>
          </div>
        </div>

        {/* Security Status Card */}
        <div className="dashboard-card security-card">
          <h3>🔒 Security Status</h3>
          <div className="security-details">
            <div className="security-item">
              <span className="security-label">Multi-Factor Authentication:</span>
              <span className={`security-status ${mfaStatus?.mfa_enabled ? 'enabled' : 'disabled'}`}>
                {mfaStatus?.mfa_enabled ? '✅ Enabled' : '⚠️ Disabled'}
              </span>
            </div>
            <div className="security-item">
              <span className="security-label">Account Status:</span>
              <span className="security-status enabled">✅ Active</span>
            </div>
            <div className="security-item">
              <span className="security-label">Session:</span>
              <span className="security-status enabled">✅ Authenticated</span>
            </div>
          </div>
        </div>

        {/* System Status Card */}
        <div className="dashboard-card system-status-card">
          <h3>🖥️ System Status</h3>
          {systemStatus && (
            <div className="system-details">
              {Object.entries(systemStatus.services).map(([service, status]) => (
                <div key={service} className="system-item">
                  <span className="system-label">{service}:</span>
                  <span className={`system-status ${status === 'operational' ? 'operational' : 'error'}`}>
                    {status === 'operational' ? '✅' : '❌'} {status}
                  </span>
                </div>
              ))}
              <div className="metrics">
                <div className="metric">
                  <span>Uptime: {systemStatus.metrics?.uptime}</span>
                </div>
                <div className="metric">
                  <span>Response Time: {systemStatus.metrics?.response_time_ms}ms</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Permissions Card */}
        <div className="dashboard-card permissions-card">
          <h3>🛡️ Your Permissions</h3>
          <div className="permissions-list">
            {permissions.length > 0 ? (
              permissions.map((permission, index) => (
                <span key={index} className="permission-badge">
                  {permission}
                </span>
              ))
            ) : (
              <p>No specific permissions assigned</p>
            )}
          </div>
        </div>

        {/* Quick Actions Card */}
        <div className="dashboard-card actions-card">
          <h3>⚡ Quick Actions</h3>
          <div className="action-buttons">
            <button className="action-button">
              📊 View Analytics
            </button>
            <button className="action-button">
              ⚙️ Settings
            </button>
            {userInfo?.role === 'admin' && (
              <button 
                className="action-button admin"
                onClick={() => window.location.href = '/admin'}
              >
                🔧 Admin Panel
              </button>
            )}
            <button className="action-button">
              📋 Logs
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
