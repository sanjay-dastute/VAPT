import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
  colors: {
    brand: {
      50: '#f7fafc',
      500: '#2D3748',
      900: '#1a202c',
    },
    accent: {
      500: '#00A3C4',
    }
  },
  styles: {
    global: {
      body: {
        bg: 'gray.50',
      }
    }
  }
});

export default theme;
