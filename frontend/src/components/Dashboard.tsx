import React from 'react';
import { Box, Grid, Heading, Text } from '@chakra-ui/react';
import ScannerCard from './ScannerCard';

const Dashboard: React.FC = () => {
  return (
    <Box p={8}>
      <Heading mb={6}>VAPT Scanner Dashboard</Heading>
      <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={6}>
        <ScannerCard
          title="Web Scanner"
          description="Scan web applications for vulnerabilities"
          icon="🌐"
          scanType="web"
        />
        <ScannerCard
          title="API Scanner"
          description="Test API endpoints for security issues"
          icon="🔌"
          scanType="api"
        />
        <ScannerCard
          title="Mobile Scanner"
          description="Analyze mobile applications"
          icon="📱"
          scanType="mobile"
        />
        <ScannerCard
          title="Smart Contract Scanner"
          description="Analyze blockchain smart contracts"
          icon="⛓️"
          scanType="smart_contract"
        />
      </Grid>
    </Box>
  );
};

export default Dashboard;
