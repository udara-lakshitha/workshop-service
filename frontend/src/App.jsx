import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = "http://localhost:8000/api";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [role, setRole] = useState(localStorage.getItem('role') || '');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const [workshops, setWorkshops] = useState([]);
  const [selectedWs, setSelectedWs] = useState(null);
  const [registrations, setRegistrations] = useState([]);
  const [onlyAvailable, setOnlyAvailable] = useState(false);

  const [newUser, setNewUser] = useState({ username: '', password: '', role: 'STAFF' });
  const [newWs, setNewWs] = useState({ code: '', title: '', instructor: '', date_time: '', capacity: 10 });
  const [regForm, setRegForm] = useState({ attendee_name: '', attendee_email: '' });
  const [error, setError] = useState('');

  const authHeaders = { headers: { Authorization: `Bearer ${token}` } };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      const res = await axios.post(`${API_BASE}/auth/login`, formData);
      setToken(res.data.access_token);
      setRole(res.data.role);
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('role', res.data.role);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  const handleLogout = () => {
    setToken('');
    setRole('');
    localStorage.clear();
  };

  const fetchWorkshops = async () => {
    if (!token || role === 'ADMIN') return;
    try {
      const res = await axios.get(`${API_BASE}/workshops?only_available=${onlyAvailable}`, authHeaders);
      setWorkshops(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchWorkshops();
  }, [token, role, onlyAvailable]);

  const fetchRegistrations = async (wsId) => {
    try {
      const res = await axios.get(`${API_BASE}/workshops/${wsId}/registrations`, authHeaders);
      setRegistrations(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const createAccount = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/users`, newUser, authHeaders);
      alert('User created successfully');
      setNewUser({ username: '', password: '', role: 'STAFF' });
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create user');
    }
  };

  const createWorkshop = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/workshops`, newWs, authHeaders);
      alert('Workshop created');
      fetchWorkshops();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create workshop');
    }
  };

  const registerAttendee = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/registrations`, { ...regForm, workshop_id: selectedWs.id }, authHeaders);
      alert('Attendee Registered!');
      fetchWorkshops();
      fetchRegistrations(selectedWs.id);
    } catch (err) {
      alert(err.response?.data?.detail || 'Registration failed');
    }
  };

  const cancelReg = async (id) => {
    try {
      await axios.post(`${API_BASE}/registrations/${id}/cancel`, {}, authHeaders);
      fetchWorkshops();
      fetchRegistrations(selectedWs.id);
    } catch (err) {
      alert(err.response?.data?.detail || 'Cancellation failed');
    }
  };

  if (!token) {
    return (
      <div style={{ padding: 40, fontFamily: 'sans-serif', maxWidth: 400, margin: 'auto' }}>
        <h2>Workshop Portal Login</h2>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <form onSubmit={handleLogin}>
          <div><input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 8 }} /></div>
          <div><input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} style={{ width: '100%', marginBottom: 10, padding: 8 }} /></div>
          <button type="submit" style={{ width: '100%', padding: 10, background: '#0070f3', color: '#fff', border: 'none' }}>Login</button>
        </form>
        <p style={{ fontSize: 12, color: '#666', marginTop: 20 }}>
          Default Logins: admin/admin123 | manager/manager123 | staff/staff123
        </p>
      </div>
    );
  }

  return (
    <div style={{ padding: 30, fontFamily: 'sans-serif', maxWidth: 1000, margin: 'auto' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #ccc', paddingBottom: 10 }}>
        <h2>Community Center Portal ({role})</h2>
        <button onClick={handleLogout}>Logout</button>
      </header>

      {role === 'ADMIN' && (
        <section style={{ marginTop: 20 }}>
          <h3>Create Staff / Manager Account</h3>
          <form onSubmit={createAccount} style={{ display: 'flex', gap: 10 }}>
            <input placeholder="Username" value={newUser.username} onChange={e => setNewUser({ ...newUser, username: e.target.value })} required />
            <input type="password" placeholder="Password" value={newUser.password} onChange={e => setNewUser({ ...newUser, password: e.target.value })} required />
            <select value={newUser.role} onChange={e => setNewUser({ ...newUser, role: e.target.value })}>
              <option value="STAFF">STAFF</option>
              <option value="MANAGER">MANAGER</option>
              <option value="ADMIN">ADMIN</option>
            </select>
            <button type="submit">Create User</button>
          </form>
        </section>
      )}

      {(role === 'MANAGER' || role === 'STAFF') && (
        <main>
          {role === 'MANAGER' && (
            <section style={{ marginTop: 20, background: '#f5f5f5', padding: 15 }}>
              <h3>Add New Workshop</h3>
              <form onSubmit={createWorkshop} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <input placeholder="Code (e.g. POT-101)" value={newWs.code} onChange={e => setNewWs({ ...newWs, code: e.target.value })} required />
                <input placeholder="Title" value={newWs.title} onChange={e => setNewWs({ ...newWs, title: e.target.value })} required />
                <input placeholder="Instructor" value={newWs.instructor} onChange={e => setNewWs({ ...newWs, instructor: e.target.value })} required />
                <input type="datetime-local" value={newWs.date_time} onChange={e => setNewWs({ ...newWs, date_time: e.target.value })} required />
                <input type="number" placeholder="Capacity" value={newWs.capacity} onChange={e => setNewWs({ ...newWs, capacity: +e.target.value })} required />
                <button type="submit" style={{ gridColumn: 'span 2' }}>Create Workshop</button>
              </form>
            </section>
          )}

          <section style={{ marginTop: 30 }}>
            <h3>Workshops</h3>
            <label>
              <input type="checkbox" checked={onlyAvailable} onChange={e => setOnlyAvailable(e.target.checked)} /> Show seats available only
            </label>
            <table border={1} cellPadding={8} style={{ width: '100%', marginTop: 10, borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Title</th>
                  <th>Instructor</th>
                  <th>Capacity</th>
                  <th>Booked</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {workshops.map((w) => (
                  <tr key={w.id}>
                    <td>{w.code}</td>
                    <td>{w.title}</td>
                    <td>{w.instructor}</td>
                    <td>{w.capacity}</td>
                    <td>{w.active_registrations_count} / {w.capacity}</td>
                    <td>
                      <button onClick={() => { setSelectedWs(w); fetchRegistrations(w.id); }}>
                        Manage Registrations
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          {selectedWs && (
            <section style={{ marginTop: 30, border: '2px solid #0070f3', padding: 15 }}>
              <h3>Registrations for {selectedWs.title} ({selectedWs.code})</h3>
              
              <h4>Register Attendee</h4>
              <form onSubmit={registerAttendee} style={{ display: 'flex', gap: 10 }}>
                <input placeholder="Name" value={regForm.attendee_name} onChange={e => setRegForm({ ...regForm, attendee_name: e.target.value })} required />
                <input type="email" placeholder="Email" value={regForm.attendee_email} onChange={e => setRegForm({ ...regForm, attendee_email: e.target.value })} required />
                <button type="submit">Register</button>
              </form>

              <h4 style={{ marginTop: 20 }}>Registration History & Audit Trail</h4>
              <table border={1} cellPadding={6} style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Registered By User ID</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {registrations.map((r) => (
                    <tr key={r.id}>
                      <td>{r.attendee_name}</td>
                      <td>{r.attendee_email}</td>
                      <td>{r.status}</td>
                      <td>{r.registered_by_id}</td>
                      <td>
                        {r.status === 'ACTIVE' && (
                          <button onClick={() => cancelReg(r.id)} style={{ color: 'red' }}>Cancel</button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}
        </main>
      )}
    </div>
  );
}