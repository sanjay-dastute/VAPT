import React from 'react';
import { Box, Flex, Button, Heading, Stack } from '@chakra-ui/react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <Box bg="white" px={4} boxShadow="sm">
      <Flex h={16} alignItems="center" justifyContent="space-between">
        <Heading size="md" color="brand.500">VAPT Scanner</Heading>
        <Stack direction="row" spacing={4}>
          <Button as={Link} to="/" variant="ghost">Web</Button>
          <Button as={Link} to="/api" variant="ghost">API</Button>
          <Button as={Link} to="/mobile" variant="ghost">Mobile</Button>
          <Button as={Link} to="/source" variant="ghost">Source Code</Button>
          <Button as={Link} to="/blockchain" variant="ghost">Blockchain</Button>
        </Stack>
      </Flex>
    </Box>
  );
};

export default Navbar;
