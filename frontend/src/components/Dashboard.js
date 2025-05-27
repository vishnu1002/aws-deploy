import React, { useEffect, useState } from 'react';
import { Box, Typography, Grid, Card, CardContent } from '@mui/material';
import { baseUrl, getApiRoute } from '../constants';


function SummaryCard({ title, value }) {
  return (
    <Card sx={{ minWidth: 180, textAlign: 'center', borderRadius: 2 }}>
      <CardContent>
        <Typography variant="h6">{title}</Typography>
        <Typography variant="h4" fontWeight="bold">{value}</Typography>
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const [totalDocuments, setTotalDocuments] = useState(0);
  const [aiModels, setAiModels] = useState(0);
  const [recentDocuments, setRecentDocuments] = useState([]);
  const [recentSearches, setRecentSearches] = useState(0); 

  useEffect(() => {
    fetch(getApiRoute('/documents'))     
      .then(res => res.json())
      .then(data => {
        setTotalDocuments(data.documents.length);
        setRecentDocuments(data.documents.slice(0, 5));
      });
    fetch(getApiRoute('/models'))     
      .then(res => res.json())
      .then(data => setAiModels(data.models.length));
  }, []);

  return (
    <Box p={3}>
      {/* Dashboard*/}
      <Typography variant="h5" fontWeight="bold" mb={2}>Model Agnostic Enterprise Search Dashboard</Typography>
      <Grid container spacing={2} mb={3}>
        <Grid item><SummaryCard title="Total Documents" value={totalDocuments} /></Grid>
        <Grid item><SummaryCard title="Available AI Models" value={aiModels} /></Grid>
        <Grid item><SummaryCard title="Recent Searches" value={recentSearches} /></Grid>
      </Grid>
      <Typography variant="h6" mb={1}>Recent Documents</Typography>
      {recentDocuments.map((doc, idx) => (
        <Card key={idx} sx={{ mb: 1, borderRadius: 2 }}>
          <CardContent>{doc.name}</CardContent>
        </Card>
      ))}
    </Box>
  );
} 