import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  isGlass?: boolean;
  isHoverable?: boolean;
}

const Card: React.FC<CardProps> = ({
  children,
  className = '',
  isGlass = false,
  isHoverable = false,
}) => {
  return (
    <motion.div
      whileHover={isHoverable ? { y: -5, transition: { duration: 0.2 } } : {}}
      className={`
        ${isGlass ? 'glassmorphism' : 'bg-card shadow-neuro'}
        rounded-2xl overflow-hidden
        ${className}
      `}
    >
      {children}
    </motion.div>
  );
};

export interface CardHeaderProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  icon?: React.ReactNode;
  className?: string;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  title,
  subtitle,
  icon,
  className = '',
}) => {
  return (
    <div className={`p-6 border-b border-divider ${className}`}>
      <div className="flex items-center">
        {icon && <div className="mr-3 text-primary">{icon}</div>}
        <div>
          {title && (
            <h3 className="text-lg font-semibold text-text">
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="text-sm text-text/60 mt-1">
              {subtitle}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export interface CardBodyProps {
  children: React.ReactNode;
  className?: string;
}

export const CardBody: React.FC<CardBodyProps> = ({
  children,
  className = '',
}) => {
  return <div className={`p-6 ${className}`}>{children}</div>;
};

export interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const CardFooter: React.FC<CardFooterProps> = ({
  children,
  className = '',
}) => {
  return (
    <div className={`p-6 border-t border-divider ${className}`}>
      {children}
    </div>
  );
};

export default Card;