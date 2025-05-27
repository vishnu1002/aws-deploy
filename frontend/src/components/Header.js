import { AppBar, Toolbar, Typography, Box } from '@mui/material';

export default function Header() {
  return (
    <AppBar position="static" color="inherit" elevation={1} sx={{ zIndex: 1201 }}>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box display="flex" alignItems="center">
          <Box sx={{ bgcolor: '#1976d2', color: '#fff', px: 2, py: 1, borderRadius: 1, mr: 2, fontWeight: 'bold', fontSize: 20 }}>DC</Box>
        </Box>
        <Box flexGrow={1} display="flex" justifyContent="center" alignItems="center">
          <Typography variant="h6" color="inherit" noWrap sx={{ fontWeight: 'bold' }}>
            Model Agnostic Enterprise Search
          </Typography>
        </Box>
      </Toolbar>
    </AppBar>
  );
} 