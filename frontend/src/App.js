import React, { useState, createContext } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Documents from './components/Documents';
import AIModels from './components/AIModels';
import SearchResults from './components/SearchResults';
import SearchBar from './components/SearchBar';
import SearchHistory from './components/SearchHistory';
import Analytics from './components/Analytics';
import { baseUrl, getApiRoute } from './constants';
import ReactMarkdown from 'react-markdown';

export const AppContext = createContext();

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
  },
});

function App() {
  const [selectedModel, setSelectedModel] = useState('deepseek');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamedResponse, setStreamedResponse] = useState('');

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (!query) return;
    setIsLoading(true);
    setStreamedResponse('');
    try {
      const res = await fetch(getApiRoute('/search'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, model: selectedModel, docType: 'resume' })
      });
      if (!res.body) throw new Error('No response body');
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let done = false;
      let fullText = '';
      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;
        if (value) {
          const chunk = decoder.decode(value);
          fullText += chunk;
          setStreamedResponse(fullText);
        }
      }
    } catch (e) {
      setStreamedResponse('Error: ' + e.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppContext.Provider value={{ selectedModel, setSelectedModel, handleSearch, isLoading, streamedResponse }}>
          <Routes>
            <Route path="/" element={
              <>
                <Header />
                <Box display="flex">
                  <Sidebar />
                  <Box flexGrow={1} sx={{ bgcolor: '#f5f5f5', minHeight: '100vh' }}>
                    <SearchBar />
                    <SearchResults />
                  </Box>
                </Box>
              </>
            } />
            <Route path="/dashboard" element={
              <>
                <Header />
                <Box display="flex">
                  <Sidebar />
                  <Box flexGrow={1} sx={{ bgcolor: '#f5f5f5', minHeight: '100vh' }}>
                    <SearchBar />
                    <SearchResults />
                  </Box>
                </Box>
              </>
            } />
            <Route path="/documents" element={
              <>
                <Header />
                <Box display="flex">
                  <Sidebar />
                  <Box flexGrow={1} sx={{ bgcolor: '#f5f5f5', minHeight: '100vh' }}>
                    <SearchBar />
                    <Documents />
                    <SearchResults />
                  </Box>
                </Box>
              </>
            } />
            <Route path="/ai-models" element={
              <>
                <Header />
                <Box display="flex">
                  <Sidebar />
                  <Box flexGrow={1} sx={{ bgcolor: '#f5f5f5', minHeight: '100vh' }}>
                    <SearchBar />
                    <AIModels />
                    <SearchResults />
                  </Box>
                </Box>
              </>
            } />
            <Route path="/search-history" element={
              <>
                <Header />
                <Box display="flex">
                  <Sidebar />
                  <Box flexGrow={1} sx={{ bgcolor: '#f5f5f5', minHeight: '100vh' }}>
                    <SearchBar />
                    <SearchHistory />
                  </Box>
                </Box>
              </>
            } />
            <Route path="/analytics" element={
              <>
                <Header />
                <Box display="flex">
                  <Sidebar />
                  <Box flexGrow={1} sx={{ bgcolor: '#f5f5f5', minHeight: '100vh' }}>
                    <SearchBar />
                    <Analytics />
                  </Box>
                </Box>
              </>
            } />
          </Routes>
        </AppContext.Provider>
      </Router>
    </ThemeProvider>
  );
}

export default App; 