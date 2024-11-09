import React, { useState } from 'react';
import {
  FormControl,
  FormLabel,
  Input,
  Button,
  VStack,
  Select,
  useToast,
  Textarea,
  Box,
} from '@chakra-ui/react';
import ScannerLayout from '../common/ScannerLayout';
import ScanProgress from '../common/ScanProgress';

const BlockchainScanner: React.FC = () => {
  const [contractAddress, setContractAddress] = useState('');
  const [network, setNetwork] = useState('ethereum');
  const [sourceCode, setSourceCode] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const toast = useToast();

  const handleScan = async () => {
    if (!contractAddress && !sourceCode) {
      toast({
        title: 'Error',
        description: 'Please provide either a contract address or source code',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setIsScanning(true);
    try {
      const response = await fetch('http://localhost:8000/scan/blockchain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contract_address: contractAddress,
          network,
          source_code: sourceCode,
        }),
      });
      if (!response.ok) throw new Error('Scan failed');
      toast({
        title: 'Success',
        description: 'Smart contract scan started successfully',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to start smart contract scan',
        status: 'error',
        duration: 3000,
      });
    }
    setIsScanning(false);
  };

  return (
    <ScannerLayout
      title="Blockchain Security Scanner"
      description="Analyze smart contracts for security vulnerabilities and common attack vectors"
    >
      <VStack spacing={6}>
        <FormControl>
          <FormLabel>Contract Address</FormLabel>
          <Input
            placeholder="0x..."
            value={contractAddress}
            onChange={(e) => setContractAddress(e.target.value)}
          />
        </FormControl>
        <FormControl>
          <FormLabel>Network</FormLabel>
          <Select value={network} onChange={(e) => setNetwork(e.target.value)}>
            <option value="ethereum">Ethereum Mainnet</option>
            <option value="bsc">Binance Smart Chain</option>
            <option value="polygon">Polygon</option>
          </Select>
        </FormControl>
        <FormControl>
          <FormLabel>Smart Contract Source Code</FormLabel>
          <Textarea
            placeholder="Paste Solidity source code here..."
            value={sourceCode}
            onChange={(e) => setSourceCode(e.target.value)}
            minH="200px"
          />
        </FormControl>
        {isScanning && (
          <ScanProgress
            progress={scanProgress}
            status="Scanning smart contract..."
          />
        )}
        <Button
          colorScheme="blue"
          onClick={handleScan}
          isLoading={isScanning}
          loadingText="Scanning"
          w="100%"
        >
          Start Smart Contract Scan
        </Button>
      </VStack>
    </ScannerLayout>
  );
};

export default BlockchainScanner;
