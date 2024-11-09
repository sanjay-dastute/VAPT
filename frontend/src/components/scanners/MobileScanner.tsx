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
} from '@chakra-ui/react';
import ScannerLayout from '../common/ScannerLayout';

const MobileScanner: React.FC = () => {
  const [appFile, setAppFile] = useState<File | null>(null);
  const [platform, setPlatform] = useState('android');
  const [deepScan, setDeepScan] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const toast = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAppFile(e.target.files[0]);
    }
  };

  const handleScan = async () => {
    if (!appFile) {
      toast({
        title: 'Error',
        description: 'Please select an application file',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setIsScanning(true);
    const formData = new FormData();
    formData.append('file', appFile);
    formData.append('platform', platform);
    formData.append('deepScan', String(deepScan));

    try {
      const response = await fetch('http://localhost:8000/scan/mobile', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) throw new Error('Scan failed');
      toast({
        title: 'Success',
        description: 'Mobile app scan started successfully',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to start mobile app scan',
        status: 'error',
        duration: 3000,
      });
    }
    setIsScanning(false);
  };

  return (
    <ScannerLayout
      title="Mobile Application Scanner"
      description="Scan mobile applications (Android APK/iOS IPA) for security vulnerabilities"
    >
      <VStack spacing={6}>
        <FormControl>
          <FormLabel>Upload Application</FormLabel>
          <Input
            type="file"
            accept=".apk,.ipa"
            onChange={handleFileChange}
            p={1}
          />
        </FormControl>
        <FormControl>
          <FormLabel>Platform</FormLabel>
          <Select value={platform} onChange={(e) => setPlatform(e.target.value)}>
            <option value="android">Android</option>
            <option value="ios">iOS</option>
          </Select>
        </FormControl>
        <HStack>
          <Checkbox
            isChecked={deepScan}
            onChange={(e) => setDeepScan(e.target.checked)}
          >
            Enable Deep Scan
          </Checkbox>
        </HStack>
        <Button
          colorScheme="blue"
          onClick={handleScan}
          isLoading={isScanning}
          loadingText="Scanning"
          w="100%"
        >
          Start Mobile App Scan
        </Button>
      </VStack>
    </ScannerLayout>
  );
};

export default MobileScanner;
