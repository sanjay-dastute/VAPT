import React from 'react';
import {
  Box,
  VStack,
  Heading,
  Text,
  useColorModeValue,
} from '@chakra-ui/react';

interface ScannerCardProps {
  title: string;
  description: string;
  icon: string;
  scanType: string;
}

const ScannerCard: React.FC<ScannerCardProps> = ({
  title,
  description,
  icon,
  scanType,
}) => {
  const bg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  return (
    <Box
      p={6}
      bg={bg}
      borderWidth="1px"
      borderColor={borderColor}
      borderRadius="lg"
      shadow="sm"
      _hover={{ shadow: 'md', transform: 'translateY(-2px)' }}
      transition="all 0.2s"
      cursor="pointer"
      onClick={() => console.log(`Starting ${scanType} scan...`)}
    >
      <VStack spacing={4} align="start">
        <Text fontSize="2xl">{icon}</Text>
        <Heading size="md">{title}</Heading>
        <Text color="gray.600">{description}</Text>
      </VStack>
    </Box>
  );
};

export default ScannerCard;
