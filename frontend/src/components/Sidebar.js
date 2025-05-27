import { Drawer, List, ListItem, ListItemIcon, ListItemText, Button, Box, Divider, Snackbar, Alert } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import DescriptionIcon from '@mui/icons-material/Description';
import MemoryIcon from '@mui/icons-material/Memory';
import HistoryIcon from '@mui/icons-material/History';
import BarChartIcon from '@mui/icons-material/BarChart';
import { useNavigate, useLocation } from 'react-router-dom';
import { baseUrl, getApiRoute } from '../constants';
import { useState } from 'react';

const navItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, route: '/dashboard' },
  { text: 'Documents', icon: <DescriptionIcon />, route: '/documents' },
  { text: 'AI Models', icon: <MemoryIcon />, route: '/ai-models' },
  { text: 'Search History', icon: <HistoryIcon />, route: '/search-history' },
  { text: 'Analytics', icon: <BarChartIcon />, route: '/analytics' },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const handleUpload = async (e) => {
    const files = e.target.files;
    if (!files.length) return;
    if (files.length > 20) {
      setSnackbar({
        open: true,
        message: 'You can only upload up to 20 files at a time.',
        severity: 'error'
      });
      return;
    }
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    formData.append('docType', 'resume'); // Default to resume type
    
    try {
      const res = await fetch(getApiRoute('/upload-documents'), {
        method: 'POST',
        body: formData
      });
      
      if (res.ok) {
        const data = await res.json();
        setSnackbar({
          open: true,
          message: data.message || 'Upload successful!',
          severity: 'success'
        });
        // Refresh the documents list by navigating to documents page
        navigate('/documents');
      } else {
        const error = await res.json();
        setSnackbar({
          open: true,
          message: error.detail || 'Upload failed.',
          severity: 'error'
        });
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Upload error. Please try again.',
        severity: 'error'
      });
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Drawer variant="permanent" anchor="left" sx={{ width: 240, flexShrink: 0, '& .MuiDrawer-paper': { width: 240, boxSizing: 'border-box' } }}>
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <input
          id="upload-input"
          type="file"
          accept="application/pdf"
          multiple
          style={{ display: 'none' }}
          onChange={handleUpload}
        />
        <label htmlFor="upload-input">
          <Button variant="contained" color="primary" component="span" sx={{ m: 2, mb: 1, borderRadius: 2, fontWeight: 'bold' }}>
            Upload Documents
          </Button>
        </label>
        <Divider />
        <List>
          {navItems.map((item) => (
            <ListItem 
              button 
              key={item.text} 
              sx={{ borderRadius: 1, mb: 0.5, bgcolor: location.pathname === item.route ? '#e3f2fd' : 'inherit' }}
              onClick={() => navigate(item.route)}
              selected={location.pathname === item.route}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItem>
          ))}
        </List>
        <Box flexGrow={1} />
        <Box sx={{ p: 2, bgcolor: '#f5f5f5', textAlign: 'center', fontSize: 12, color: '#555' }}>
          All systems operational
        </Box>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Drawer>
  );
} 