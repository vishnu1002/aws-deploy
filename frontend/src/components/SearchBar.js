import React, { useState, useContext } from 'react';
import { Box, TextField, Button, InputAdornment, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { AppContext } from '../App';

export default function SearchBar() {
  const { selectedModel, setSelectedModel, handleSearch } = useContext(AppContext);
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setOpen(true);
    await handleSearch(query);
    setOpen(false);
  };

  return (
    <>
      <Box component="form" onSubmit={handleSubmit} display="flex" alignItems="center" mb={3}>
        <TextField
          fullWidth
          placeholder="Ask a question about your data..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
              </InputAdornment>
            ),
            sx: { borderRadius: 2, bgcolor: '#fff' }
          }}
          sx={{ mr: 2 }}
        />
        <FormControl sx={{ minWidth: 180, mr: 2 }}>
          <InputLabel>AI Model</InputLabel>
          <Select
            value={selectedModel}
            label="AI Model"
            onChange={e => setSelectedModel(e.target.value)}
          >
            <MenuItem value="deepseek">DeepSeek</MenuItem>
            <MenuItem value="llama">LLaMA</MenuItem>
            <MenuItem value="qwen">Qwen</MenuItem>
            <MenuItem value="compare">Compare All</MenuItem>
          </Select>
        </FormControl>
        <Button variant="contained" color="primary" sx={{ height: 48, borderRadius: 2, fontWeight: 'bold', px: 4 }} type="submit">
          Search
        </Button>
      </Box>
    </>
  );
} 