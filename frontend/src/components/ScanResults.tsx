import React from 'react';
import {
  Box,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Heading,
  Text,
  VStack
} from '@chakra-ui/react';

interface Vulnerability {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  location: string;
  remediation?: string;
}

interface ScanResultsProps {
  results: Vulnerability[];
  scanType: string;
  target: string;
}

const ScanResults: React.FC<ScanResultsProps> = ({ results, scanType, target }) => {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'green';
      case 'medium': return 'yellow';
      case 'high': return 'orange';
      case 'critical': return 'red';
      default: return 'gray';
    }
  };

  return (
    <Box p={4}>
      <VStack spacing={4} align="stretch">
        <Heading size="lg">{scanType} Scan Results</Heading>
        <Text>Target: {target}</Text>

        {results.length === 0 ? (
          <Box p={4} bg="green.50" borderRadius="md">
            <Text color="green.600">No vulnerabilities found.</Text>
          </Box>
        ) : (
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Severity</Th>
                <Th>Title</Th>
                <Th>Description</Th>
                <Th>Location</Th>
                <Th>Remediation</Th>
              </Tr>
            </Thead>
            <Tbody>
              {results.map((vuln) => (
                <Tr key={vuln.id}>
                  <Td>
                    <Badge colorScheme={getSeverityColor(vuln.severity)}>
                      {vuln.severity.toUpperCase()}
                    </Badge>
                  </Td>
                  <Td>{vuln.title}</Td>
                  <Td>{vuln.description}</Td>
                  <Td>{vuln.location}</Td>
                  <Td>{vuln.remediation || 'N/A'}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}
      </VStack>
    </Box>
  );
};

export default ScanResults;
