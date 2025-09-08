'use client';

import { useState, useEffect } from 'react';

interface NotificationHook {
  unreadCount: number;
  loading: boolean;
  error: string | null;
  refreshCount: () => void;
}

export function useNotifications(apiUrl: string = 'http://localhost:8000'): NotificationHook {
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNotificationCount = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${apiUrl}/notifications/alerts`);
      
      if (response.ok) {
        const data = await response.json();
        const notifications = data.notifications || [];
        
        // Count unread notifications (assuming new notifications are unread)
        const unread = notifications.filter((n: any) => 
          n.type === 'critical' || n.type === 'warning'
        ).length;
        
        setUnreadCount(unread);
      } else {
        // Fallback to demo count
        setUnreadCount(4);
      }
    } catch (err) {
      console.error('Error fetching notification count:', err);
      setError('Failed to fetch notifications');
      // Fallback to demo count
      setUnreadCount(4);
    } finally {
      setLoading(false);
    }
  };

  const refreshCount = () => {
    fetchNotificationCount();
  };

  useEffect(() => {
    fetchNotificationCount();
    
    // Refresh every 2 minutes
    const interval = setInterval(fetchNotificationCount, 2 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  return {
    unreadCount,
    loading,
    error,
    refreshCount
  };
}