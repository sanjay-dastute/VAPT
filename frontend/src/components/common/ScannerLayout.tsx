import React from 'react';
import { Box, VStack, Heading, Text } from '@chakra-ui/react';

interface ScannerLayoutProps {
  title: string;
  description: string;
  children: React.ReactNode;
}

const ScannerLayout: React.FC<ScannerLayoutProps> = ({ title, description, children }) => {
  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="lg" mb={2}>{title}</Heading>
        <Text color="gray.600">{description}</Text>
      </Box>
      <Box bg="white" p={6} borderRadius="lg" boxShadow="sm">
        {children}
      </Box>
    </VStack>
  );
};

export default ScannerLayout;
