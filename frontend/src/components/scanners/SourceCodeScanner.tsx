import React, { useState } from 'react';
import {
  FormControl,
  FormLabel,
  Input,
  Button,
  VStack,
  Select,
  Checkbox,
  useToast,
  HStack,
  Text,
  Box,
} from '@chakra-ui/react';
import ScannerLayout from '../common/ScannerLayout';

const SourceCodeScanner: React.FC = () => {
  const [repository, setRepository] = useState('');
  const [language, setLanguage] = useState('python');
  const [scanSecrets, setScanSecrets] = useState(true);
  const [scanVulnerabilities, setScanVulnerabilities] = useState(true);
  const [isScanning, setIsScanning] = useState(false);
  const toast = useToast();

  const handleScan = async () => {
    if (!repository) {
      toast({
        title: 'Error',
        description: 'Please enter a repository URL',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setIsScanning(true);
    try {
      const response = await fetch('http://localhost:8000/scan/source', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repository,
          language,
          scan_secrets: scanSecrets,
          scan_vulnerabilities: scanVulnerabilities,
        }),
      });
      if (!response.ok) throw new Error('Scan failed');
      toast({
        title: 'Success',
        description: 'Source code scan started successfully',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to start source code scan',
        status: 'error',
        duration: 3000,
      });
    }
    setIsScanning(false);
  };

  return (
    <ScannerLayout
      title="Source Code Scanner"
      description="Analyze source code for security vulnerabilities, secrets, and best practices"
    >
      <VStack spacing={6}>
        <FormControl>
          <FormLabel>Repository URL</FormLabel>
          <Input
            placeholder="https://github.com/username/repo"
            value={repository}
            onChange={(e) => setRepository(e.target.value)}
          />
        </FormControl>
        <FormControl>
          <FormLabel>Primary Language</FormLabel>
          <Select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="go">Go</option>
            <option value="ruby">Ruby</option>
            <option value="php">PHP</option>
          </Select>
        </FormControl>
        <Box w="100%">
          <Text mb={2} fontWeight="medium">Scan Options</Text>
          <VStack align="start" spacing={2}>
            <Checkbox
              isChecked={scanSecrets}
              onChange={(e) => setScanSecrets(e.target.checked)}
            >
              Scan for Hardcoded Secrets
            </Checkbox>
            <Checkbox
              isChecked={scanVulnerabilities}
              onChange={(e) => setScanVulnerabilities(e.target.checked)}
            >
              Scan for Security Vulnerabilities
            </Checkbox>
          </VStack>
        </Box>
        <Button
          colorScheme="blue"
          onClick={handleScan}
          isLoading={isScanning}
          loadingText="Scanning"
          w="100%"
        >
          Start Source Code Scan
        </Button>
      </VStack>
    </ScannerLayout>
  );
};

export default SourceCodeScanner;
