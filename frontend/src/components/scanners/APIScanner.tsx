import React, { useState } from 'react';
import {
  FormControl,
  FormLabel,
  Input,
  Button,
  VStack,
  Select,
  useToast,
} from '@chakra-ui/react';
import ScannerLayout from '../common/ScannerLayout';

const APIScanner: React.FC = () => {
  const [target, setTarget] = useState('');
  const [method, setMethod] = useState('GET');
  const [isScanning, setIsScanning] = useState(false);
  const toast = useToast();

  const handleScan = async () => {
    if (!target) {
      toast({
        title: 'Error',
        description: 'Please enter an API endpoint',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setIsScanning(true);
    try {
      const response = await fetch('http://localhost:8000/scan/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target, method }),
      });
      if (!response.ok) throw new Error('Scan failed');
      toast({
        title: 'Success',
        description: 'API scan started successfully',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to start API scan',
        status: 'error',
        duration: 3000,
      });
    }
    setIsScanning(false);
  };

  return (
    <ScannerLayout
      title="API Security Scanner"
      description="Scan REST APIs for security vulnerabilities and misconfigurations"
    >
      <VStack spacing={6}>
        <FormControl>
          <FormLabel>API Endpoint</FormLabel>
          <Input
            placeholder="https://api.example.com/v1"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
          />
        </FormControl>
        <FormControl>
          <FormLabel>HTTP Method</FormLabel>
          <Select value={method} onChange={(e) => setMethod(e.target.value)}>
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </Select>
        </FormControl>
        <Button
          colorScheme="blue"
          onClick={handleScan}
          isLoading={isScanning}
          loadingText="Scanning"
          w="100%"
        >
          Start API Scan
        </Button>
      </VStack>
    </ScannerLayout>
  );
};

export default APIScanner;
