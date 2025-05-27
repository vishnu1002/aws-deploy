import React, { useEffect, useState, useContext } from 'react';
import { Box, Typography, Card, CardContent, MenuItem, Select, FormControl, InputLabel } from '@mui/material';
import { AppContext } from '../App';
import { baseUrl, getApiRoute } from '../constants';


export default function AIModels() {
  const [models, setModels] = useState([]);
  const { selectedModel, setSelectedModel } = useContext(AppContext);

  useEffect(() => {
    fetch(getApiRoute('/models'))
      .then(res => res.json())
      .then(data => setModels(data.models || []));
  }, []);

  return (
    <Box p={3}>
      <Typography variant="h5" fontWeight="bold" mb={2}>Available AI Models</Typography>
      <FormControl sx={{ minWidth: 300, mb: 3 }}>
        <InputLabel>Select AI Model</InputLabel>
        <Select
          value={selectedModel}
          label="Select AI Model"
          onChange={e => setSelectedModel(e.target.value)}
        >
          {models.map((model) => (
            <MenuItem key={model.value} value={model.value}>{model.label}</MenuItem>
          ))}
        </Select>
      </FormControl>
      <Box>
        {models.map((model) => (
          <Card key={model.value} sx={{ mb: 2, borderRadius: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight="bold">{model.label}</Typography>
              <Typography variant="body2">Value: {model.value}</Typography>
            </CardContent>
          </Card>
        ))}
        {models.length === 0 && (
          <Typography>No AI models found.</Typography>
        )}
      </Box>
    </Box>
  );
} 