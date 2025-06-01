import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from './ui/Button';
import { LogOut, Mic, Calendar, User, Plus, Home } from 'lucide-react';
import { NewEntryModal } from './NewEntryModal';

/**
 * Main layout component with navigation header
 * Wraps all authenticated pages
 */
interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isNewEntryModalOpen, setIsNewEntryModalOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex items-center justify-between">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <Mic className="h-6 w-6 text-primary" />
              <span className="text-xl font-semibold">MindSpeak</span>
            </Link>

            {/* Navigation Links */}
            <div className="flex items-center space-x-6">
              <Button
                onClick={() => setIsNewEntryModalOpen(true)}
                size="sm"
                className="flex items-center space-x-1"
              >
                <Plus className="h-4 w-4" />
                <span>New Entry</span>
              </Button>
              
              <Link
                to="/dashboard"
                className="text-muted-foreground hover:text-foreground transition-colors flex items-center space-x-1"
              >
                <Home className="h-4 w-4" />
                <span>Dashboard</span>
              </Link>
              <Link
                to="/entries"
                className="text-muted-foreground hover:text-foreground transition-colors flex items-center space-x-1"
              >
                <Calendar className="h-4 w-4" />
                <span>Entries</span>
              </Link>
              <Link
                to="/profile"
                className="text-muted-foreground hover:text-foreground transition-colors flex items-center space-x-1"
              >
                <User className="h-4 w-4" />
                <span>Profile</span>
              </Link>
            </div>

            {/* User Menu */}
            <div className="flex items-center">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="flex items-center space-x-1"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </Button>
            </div>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>

      {/* Footer (TODO: Add footer content) */}
      <footer className="border-t mt-auto">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-sm text-muted-foreground">
            © 2024 MindSpeak. All rights reserved.
          </p>
        </div>
      </footer>

      {/* New Entry Modal */}
      <NewEntryModal
        isOpen={isNewEntryModalOpen}
        onClose={() => setIsNewEntryModalOpen(false)}
      />
    </div>
  );
}