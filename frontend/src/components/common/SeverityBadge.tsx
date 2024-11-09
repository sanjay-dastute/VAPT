import React from 'react';
import { Badge } from '@chakra-ui/react';

interface SeverityBadgeProps {
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
}

const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity }) => {
  const colorScheme = {
    critical: 'red',
    high: 'orange',
    medium: 'yellow',
    low: 'green',
    info: 'blue',
  }[severity];

  return (
    <Badge colorScheme={colorScheme} px={2} py={1} borderRadius="full">
      {severity.toUpperCase()}
    </Badge>
  );
};

export default SeverityBadge;
