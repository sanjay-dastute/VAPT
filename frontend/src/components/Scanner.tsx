import React from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  VStack,
  Container,
  Heading,
  useToast,
} from '@chakra-ui/react';

const Scanner: React.FC = () => {
  const [scanType, setScanType] = React.useState('web');
  const [target, setTarget] = React.useState('');
  const [isScanning, setIsScanning] = React.useState(false);
  const toast = useToast();

  const handleScan = async () => {
    setIsScanning(true);
    try {
      const response = await fetch(`http://localhost:8000/scan/${scanType}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ target }),
      });

      if (!response.ok) throw new Error('Scan failed');

      const result = await response.json();
      toast({
        title: 'Scan Complete',
        description: `Found ${result.results.vulnerabilities.length} vulnerabilities`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error: any) {
      toast({
        title: 'Scan Failed',
        description: error?.message || 'An unknown error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <Container maxW="container.md" py={10}>
      <VStack spacing={6} align="stretch">
        <Heading size="lg">VAPT Scanner</Heading>
        <FormControl>
          <FormLabel>Scan Type</FormLabel>
          <Select value={scanType} onChange={(e) => setScanType(e.target.value)}>
            <option value="web">Web Application</option>
            <option value="mobile">Mobile Application</option>
            <option value="api">API</option>
            <option value="source_code">Source Code</option>
            <option value="blockchain">Blockchain</option>
          </Select>
        </FormControl>
        <FormControl>
          <FormLabel>Target</FormLabel>
          <Input
            placeholder="Enter target URL or path"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
          />
        </FormControl>
        <Button
          colorScheme="blue"
          isLoading={isScanning}
          loadingText="Scanning..."
          onClick={handleScan}
        >
          Start Scan
        </Button>
      </VStack>
    </Container>
  );
};

export default Scanner;
