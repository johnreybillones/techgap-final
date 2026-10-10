import { cn } from '@/lib/utils';
import { HTMLAttributes } from 'react';

type BadgeVariant = 'green' | 'blue' | 'amber' | 'slate' | 'red' | 'mock';

interface BadgeProps extends HTMLAttributes<'span' extends keyof JSX.IntrinsicElements ? 'span' : never> {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

export function Badge({ variant = 'slate', children, className }: {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span className={cn(`badge-${variant}`, className)}>
      {children}
    </span>
  );
}
