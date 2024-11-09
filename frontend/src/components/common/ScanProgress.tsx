import React from 'react';
import { Box, Progress, Text, VStack } from '@chakra-ui/react';

interface ScanProgressProps {
  progress: number;
  status: string;
}

const ScanProgress: React.FC<ScanProgressProps> = ({ progress, status }) => {
  return (
    <VStack w="100%" spacing={2}>
      <Progress
        value={progress}
        w="100%"
        colorScheme="blue"
        hasStripe
        isAnimated
      />
      <Text fontSize="sm" color="gray.600">
        {status}
      </Text>
    </VStack>
  );
};

export default ScanProgress;
