import React, { useContext, useEffect, useState } from 'react';
import { AppContext } from '../App';
import { Box, Typography, Card, CardContent, Collapse, Alert } from '@mui/material';
import ReactMarkdown from 'react-markdown';

// Helper to split streamed markdown into model sections
function parseModelSections(markdown) {
  if (!markdown) return {};
  const sections = markdown.split(/(^## .*$)/m).filter(Boolean);
  const result = {};
  let currentModel = '';
  for (let i = 0; i < sections.length; i++) {
    if (sections[i].startsWith('## ')) {
      currentModel = sections[i].replace(/^## /, '').trim();
      if (!(currentModel in result)) result[currentModel] = '';
    } else if (currentModel) {
      result[currentModel] += sections[i];
    }
  }
  // Fallback: if no sections, show all in one card
  if (Object.keys(result).length === 0 && markdown.trim()) {
    result[''] = markdown;
  }
  return result;
}

export default function SearchResults() {
  const { streamedResponse, isLoading } = useContext(AppContext);
  const [showCursor, setShowCursor] = useState(true);
  const [modelContents, setModelContents] = useState({});
  const [open, setOpen] = useState(false);

  // Update modelContents as the stream grows
  useEffect(() => {
    setModelContents(parseModelSections(streamedResponse));
  }, [streamedResponse]);

  useEffect(() => {
    if (isLoading) {
      const interval = setInterval(() => setShowCursor(c => !c), 500);
      return () => clearInterval(interval);
    } else {
      setShowCursor(false);
    }
  }, [isLoading]);

  if (!streamedResponse && !isLoading) {
    return null;
  }

  const modelNames = Object.keys(modelContents);

  return (
    <Box p={3}>
      <Collapse in={isLoading}>
        <Alert severity="info" sx={{ mb: 2 }}>Thinking...</Alert>
      </Collapse>
      {isLoading && (
        <Box sx={{ fontSize: 22, color: '#888', mb: 1, ml: 1 }}>
          <span style={{ opacity: 0.7 }}>{showCursor ? '▋' : ' '}</span>
        </Box>
      )}
      {modelNames.map((model, idx) => (
        <Card key={model || idx} sx={{ mb: 2, borderRadius: 2 }}>
          <CardContent>
            {model && (
              <Typography variant="subtitle1" fontWeight="bold" mb={1}>{model}</Typography>
            )}
            <Box sx={{ fontFamily: 'monospace', fontSize: 16, whiteSpace: 'pre-wrap' }}>
              <ReactMarkdown>{modelContents[model]}</ReactMarkdown>
              {isLoading && idx === modelNames.length - 1 && (
                <span style={{ opacity: 0.7 }}>{showCursor ? '▋' : ' '}</span>
              )}
            </Box>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
} 