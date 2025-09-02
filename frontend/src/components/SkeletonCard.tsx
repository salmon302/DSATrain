import React from 'react';
import { Card, CardContent, Grid, Box, Skeleton } from '@mui/material';

interface Props {
  variant?: 'grid' | 'list';
}

const SkeletonCard: React.FC<Props> = ({ variant = 'grid' }) => {
  if (variant === 'list') {
    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <Skeleton variant="text" width="60%" height={26} />
              <Box display="flex" gap={1} mt={1}>
                <Skeleton variant="rounded" width={60} height={24} />
                <Skeleton variant="rounded" width={80} height={24} />
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box display="flex" gap={1}>
                <Skeleton variant="rounded" width={90} height={24} />
                <Skeleton variant="rounded" width={70} height={24} />
              </Box>
            </Grid>
            <Grid item xs={12} md={3}>
              <Box display="flex" gap={1} justifyContent="flex-end" alignItems="center">
                <Skeleton variant="circular" width={24} height={24} />
                <Skeleton variant="text" width={80} />
                <Skeleton variant="text" width={80} />
                <Skeleton variant="rounded" width={80} height={32} />
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
          <Skeleton variant="text" width="70%" height={28} />
          <Skeleton variant="circular" width={24} height={24} />
        </Box>
        <Box display="flex" gap={1} mb={2}>
          <Skeleton variant="rounded" width={60} height={24} />
          <Skeleton variant="rounded" width={80} height={24} />
          <Skeleton variant="rounded" width={110} height={24} />
        </Box>
        <Box display="flex" gap={1} mb={2}>
          <Skeleton variant="rounded" width={90} height={24} />
          <Skeleton variant="rounded" width={120} height={24} />
          <Skeleton variant="rounded" width={70} height={24} />
        </Box>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Skeleton variant="text" width={140} />
          <Skeleton variant="rounded" width={80} height={32} />
        </Box>
      </CardContent>
    </Card>
  );
};

export default SkeletonCard;
