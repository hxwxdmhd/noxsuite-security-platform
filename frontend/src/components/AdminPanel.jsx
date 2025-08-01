import React, { useEffect, useState } from 'react';

const AdminPanel = () => {
  const [adminData, setAdminData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          window.location.href = '/login';
          return;
        }
        
        const response = await fetch('/api/v1/admin/dashboard', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setAdminData(data);
        } else if (response.status === 403) {
          setError('You do not have admin privileges');
        } else {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
      } catch (error) {
        setError('Error connecting to server');
        console.error('Error fetching admin data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAdminData();
  }, []);
  
  if (loading) {
    return <div>Loading admin panel...</div>;
  }
  
  if (error) {
    return <div className="error-message">{error}</div>;
  }
  
  return (
    <div className="admin-panel-container">
      <h1>Admin Dashboard</h1>
      <div className="admin-stats">
        <div className="stat-card">
          <h3>Active Users</h3>
          <p className="stat-value">{adminData?.active_users}</p>
        </div>
        <div className="stat-card">
          <h3>System Health</h3>
          <p className="stat-value">{adminData?.system_health}</p>
        </div>
        <div className="stat-card">
          <h3>Security Alerts</h3>
          <p className="stat-value">{adminData?.security_alerts}</p>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
