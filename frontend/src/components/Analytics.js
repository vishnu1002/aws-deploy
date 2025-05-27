import React, { useEffect, useState } from 'react';
import { Box, Typography, Grid, Card, CardContent } from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { baseUrl, getApiRoute } from '../constants';


export default function Analytics() {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [totalDocuments, setTotalDocuments] = useState(0);

  useEffect(() => {
    fetch(getApiRoute('/analytics'))     
     
      .then(res => res.json())
      .then(data => setAnalyticsData(data));

    fetch(getApiRoute('/documents')) 
      .then(res => res.json())
      .then(data => setTotalDocuments(data.documents.length));
  }, []);

  return (
    <Box p={3}>
      <Typography variant="h5" fontWeight="bold" mb={2}>
        Analytics
      </Typography>
      {analyticsData ? (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card sx={{ background: '#fff', boxShadow: 2, borderRadius: 2 }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight="bold" mb={2}>BLEU Scores</Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={analyticsData.bleuScores}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="model" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="score" fill="#1976d2" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ background: '#fff', boxShadow: 2, borderRadius: 2 }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight="bold" mb={2}>ROUGE-L Scores</Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={analyticsData.rougeScores}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="model" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="score" fill="#388e3c" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ background: '#fff', boxShadow: 2, borderRadius: 2 }}>
              <CardContent>
                <Typography variant="subtitle1" fontWeight="bold" mb={2}>Latencies (s)</Typography>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={analyticsData.latencies}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="model" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="latency" fill="#fbc02d" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          {/* Total Documents Section */}
          <Grid item xs={12}>
            <Card sx={{ background: '#fff', boxShadow: 2, borderRadius: 2, mt: 2 }}>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" mb={1}>
                  Total Documents
                </Typography>
                <Typography variant="h4" color="primary" textAlign="center">
                  {totalDocuments}
                </Typography>
                <Typography variant="body1" color="text.secondary" textAlign="center">
                  Total Documents in System
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      ) : (
        <Typography variant="body1">
          Select "compare" model and click on Analytics to view comparison metrics.
        </Typography>
      )}
    </Box>
  );
} 