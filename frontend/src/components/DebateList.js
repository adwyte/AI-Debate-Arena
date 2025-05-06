import React from 'react';
import { List, ListItemButton, ListItemText, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';

export default function DebateList({ debates }) {
  const nav = useNavigate();

  return (
    <Paper>
      <List>
        {debates.map(d => (
          <ListItemButton key={d.id} onClick={() => nav(`/debates/${d.id}`)}>
            <ListItemText primary={d.topic} secondary={d.mode} />
          </ListItemButton>
        ))}
      </List>
    </Paper>
  );
}
