import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, className = '', hover = false, ...props }) => {
  return (
    <div
      className={`bg-white dark:bg-[#17171f] border border-gray-100 dark:border-[#27272e] rounded-xl p-5 shadow-sm ${
        hover ? 'hover:shadow-md hover:border-violet-200 dark:hover:border-violet-900/50 transition-all duration-200' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
