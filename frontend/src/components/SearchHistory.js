import React, { useEffect, useState } from 'react';
import { Box, Typography, Card, CardContent, Button, Collapse, IconButton } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { baseUrl, getApiRoute } from '../constants';


export default function SearchHistory() {
  const [history, setHistory] = useState([]);
  const [expandedItems, setExpandedItems] = useState({});

  const fetchHistory = () => {
    fetch(getApiRoute('/search-history'))     
 
      .then(res => res.json())
      .then(data => setHistory(data.history || []));
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleClear = async () => {
    await fetch((getApiRoute('/search-history')), { method: 'DELETE' });
    fetchHistory();
  };

  const toggleExpand = (index) => {
    setExpandedItems(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  return (
    <Box p={3}>
      <Box display="flex" alignItems="center" mb={2}>
        <Typography variant="h5" fontWeight="bold" flexGrow={1}>Search History</Typography>
        <Button variant="outlined" color="secondary" onClick={handleClear}>Clear History</Button>
      </Box>
      {history.length === 0 && <Typography>No search history found.</Typography>}
      {history.map((item, idx) => (
        <Card key={idx} sx={{ mb: 2, borderRadius: 2 }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="subtitle1" fontWeight="bold">{item.query}</Typography>
                <Typography variant="body2">Model: {item.model}</Typography>
                <Typography variant="body2">Doc Type: {item.docType}</Typography>
                <Typography variant="body2">Time: {item.timestamp}</Typography>
              </Box>
              <IconButton onClick={() => toggleExpand(idx)}>
                {expandedItems[idx] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
            <Collapse in={expandedItems[idx]}>
              <Box mt={2}>
                {item.results && (
                  <>
                    {item.results.responses && (
                      <Box>
                        <Typography variant="subtitle2" fontWeight="bold" mb={1}>Model Response:</Typography>
                        {Object.entries(item.results.responses).map(([model, response]) => (
                          <Box key={model} mb={2}>
                            <Typography variant="subtitle2" color="primary">{model}:</Typography>
                            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                              {response}
                            </Typography>
                          </Box>
                        ))}
                      </Box>
                    )}
                    {item.results.response && !item.results.responses && (
                      <Box>
                        <Typography variant="subtitle2" fontWeight="bold" mb={1}>Model Response:</Typography>
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                          {item.results.response}
                        </Typography>
                      </Box>
                    )}
                  </>
                )}
              </Box>
            </Collapse>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
} 