import React, { useState } from 'react';
import {
  Box,
  Input,
  Button,
  VStack,
  useToast,
  Text,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
} from '@chakra-ui/react';

interface ScanResult {
  type: string;
  severity: string;
  description: string;
  location: string;
}

interface ScanStatus {
  id: string;
  status: string;
  findings: ScanResult[];
}

const WebScanner: React.FC = () => {
  const [targetUrl, setTargetUrl] = useState('');
  const [scanResults, setScanResults] = useState<ScanResult[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const toast = useToast();

  const startScan = async () => {
    if (!targetUrl) {
      toast({
        title: 'Error',
        description: 'Please enter a target URL',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsScanning(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/scanners/web', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ target_url: targetUrl }),
      });

      if (!response.ok) {
        throw new Error('Failed to start scan');
      }

      const data = await response.json();

      toast({
        title: 'Success',
        description: `Scan started: Scan started for ${targetUrl}`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // Get scan results
      const statusResponse = await fetch(`http://localhost:8000/api/v1/scanners/web/${data.scan_id}`);
      if (!statusResponse.ok) {
        throw new Error('Failed to get scan results');
      }

      const statusData: ScanStatus = await statusResponse.json();
      setScanResults(statusData.findings);

    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to start scan',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsScanning(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'red';
      case 'high':
        return 'orange';
      case 'medium':
        return 'yellow';
      case 'low':
        return 'green';
      default:
        return 'gray';
    }
  };

  return (
    <VStack spacing={4} align="stretch" p={4}>
      <Text fontSize="2xl">Web Vulnerability Scanner</Text>
      <Text>Scan web applications for security vulnerabilities using AI-powered detection</Text>

      <Box>
        <Input
          placeholder="https://example.com"
          value={targetUrl}
          onChange={(e) => setTargetUrl(e.target.value)}
          mb={4}
        />
        <Button
          colorScheme="blue"
          onClick={startScan}
          isLoading={isScanning}
          width="100%"
        >
          Start Scan
        </Button>
      </Box>

      {scanResults.length > 0 && (
        <Box overflowX="auto">
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Type</Th>
                <Th>Severity</Th>
                <Th>Description</Th>
                <Th>Location</Th>
              </Tr>
            </Thead>
            <Tbody>
              {scanResults.map((result, index) => (
                <Tr key={index}>
                  <Td>{result.type}</Td>
                  <Td>
                    <Badge colorScheme={getSeverityColor(result.severity)}>
                      {result.severity}
                    </Badge>
                  </Td>
                  <Td>{result.description}</Td>
                  <Td>{result.location}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}
    </VStack>
  );
};

export default WebScanner;
