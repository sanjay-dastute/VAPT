import React from 'react';
import { ChakraProvider, Box, VStack } from '@chakra-ui/react';
import WebScanner from './components/scanners/WebScanner';

function App() {
  return (
    <ChakraProvider>
      <Box p={4}>
        <VStack spacing={4}>
          <WebScanner />
        </VStack>
      </Box>
    </ChakraProvider>
  );
}

export default App;
