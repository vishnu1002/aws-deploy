import React, { useEffect, useState } from 'react';
import { Box, Typography, Card, CardContent, MenuItem, Select, FormControl, InputLabel, Grid, Button, Snackbar, Alert, TextField } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import { baseUrl, getApiRoute } from '../constants';

const docTypes = [
  { value: 'all', label: 'All' },
  { value: 'resume', label: 'Resume' },
  { value: 'policy', label: 'Policy Document' },
  { value: 'reports', label: 'Reports' },
];

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [searchName, setSearchName] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const fetchDocuments = () => {
    fetch(getApiRoute('/documents'))
      .then(res => res.json())
      .then(data => setDocuments(data.documents || []));
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const filteredDocuments = documents.filter(doc =>
    searchName.trim() === '' || doc.name.toLowerCase().includes(searchName.trim().toLowerCase())
  );

  const handleDownload = async (doc) => {
    try {
      const response = await fetch(getApiRoute(`/download-document/${doc.type}/${doc.name}`));
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = doc.name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setSnackbar({ open: true, message: 'Document downloaded successfully', severity: 'success' });
    } catch (error) {
      setSnackbar({ open: true, message: 'Failed to download document', severity: 'error' });
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Box p={3}>
      <Box display="flex" alignItems="center" mb={2}>
        <Typography variant="h5" fontWeight="bold" flexGrow={1}>Uploaded Documents</Typography>
        <TextField
          label="Search by Name"
          variant="outlined"
          size="small"
          value={searchName}
          onChange={e => setSearchName(e.target.value)}
          sx={{ minWidth: 200 }}
        />
      </Box>
      <Grid container spacing={2}>
        {filteredDocuments.length > 0 ? filteredDocuments.map((doc, idx) => (
          <Grid item xs={12} md={6} lg={4} key={idx}>
            <Card sx={{ mb: 2, borderRadius: 2 }}>
              <CardContent>
                <Box>
                  <Typography variant="subtitle1" fontWeight="bold">{doc.name}</Typography>
                  <Typography variant="body2">Type: {doc.type}</Typography>
                  <Typography variant="body2">Size: {doc.size}</Typography>
                  <Typography variant="body2">Last Modified: {doc.lastModified}</Typography>
                  <Box display="flex" justifyContent="flex-end" mt={2}>
                    <Button
                      variant="outlined"
                      onClick={() => handleDownload(doc)}
                      size="small"
                      sx={{
                        minWidth: 'auto',
                        p: 1,
                        '& .MuiButton-startIcon': {
                          margin: 0
                        }
                      }}
                    >
                      <DownloadIcon />
                    </Button>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )) : (
          <Grid item xs={12}><Typography>No documents found.</Typography></Grid>
        )}
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
} 