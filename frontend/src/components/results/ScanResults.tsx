import React from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  Badge,
  Grid,
  GridItem,
  useColorModeValue,
} from '@chakra-ui/react';

interface Vulnerability {
  type: string;
  severity: string;
  description: string;
  details?: any;
}

interface ScanResultsProps {
  scanId: number;
  results: {
    vulnerabilities: Vulnerability[];
    scan_summary?: {
      total_vulnerabilities: number;
      high_severity: number;
      medium_severity: number;
      low_severity: number;
    };
  };
}

const ScanResults: React.FC<ScanResultsProps> = ({ results, scanId }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const summary = results.scan_summary || {
    total_vulnerabilities: results.vulnerabilities.length,
    high_severity: results.vulnerabilities.filter(v => v.severity === 'high').length,
    medium_severity: results.vulnerabilities.filter(v => v.severity === 'medium').length,
    low_severity: results.vulnerabilities.filter(v => v.severity === 'low').length,
  };

  return (
    <Box p={5} shadow="md" borderWidth="1px" bg={bgColor}>
      <VStack spacing={6} align="stretch">
        <Heading size="md">Scan Results #{scanId}</Heading>
        <Grid templateColumns="repeat(4, 1fr)" gap={4}>
          {Object.entries(summary).map(([key, value]) => (
            <GridItem key={key}>
              <Box p={3} borderWidth="1px" borderRadius="md">
                <Text fontSize="sm">{key.replace(/_/g, ' ').toUpperCase()}</Text>
                <Text fontSize="2xl" fontWeight="bold">{value}</Text>
              </Box>
            </GridItem>
          ))}
        </Grid>
      </VStack>
    </Box>
  );
};

export default ScanResults;
