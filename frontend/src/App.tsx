import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';

// Pages
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Recording } from './pages/Recording';
import { ProcessingEntry } from './pages/ProcessingEntry';
import { EntryEditor } from './pages/EntryEditor';
import { EntriesList } from './pages/EntriesList';
import { Profile } from './pages/Profile';

/**
 * Main App component with routing setup
 * Handles authentication flow and protected routes
 */
function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Recording route */}
          <Route
            path="/record"
            element={
              <ProtectedRoute>
                <Layout>
                  <Recording />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Processing route */}
          <Route
            path="/entries/:entryId/process"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProcessingEntry />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Entry editor route */}
          <Route
            path="/entries/:entryId/edit"
            element={
              <ProtectedRoute>
                <Layout>
                  <EntryEditor />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/entries"
            element={
              <ProtectedRoute>
                <Layout>
                  <EntriesList />
                </Layout>
              </ProtectedRoute>
            }
          />


          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Layout>
                  <Profile />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;