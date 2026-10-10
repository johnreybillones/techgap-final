'use client';

import { cn } from '@/lib/utils';
import { ButtonHTMLAttributes, forwardRef } from 'react';

interface Button3DProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline' | 'blue' | 'amber' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

const Button3D = forwardRef<HTMLButtonElement, Button3DProps>(
  ({ variant = 'primary', size = 'md', className, children, ...props }, ref) => {
    const variantClass = {
      primary: 'btn-3d-primary',
      outline: 'btn-3d-outline',
      blue: 'btn-3d-blue',
      amber: 'btn-3d-amber',
      ghost: 'inline-flex items-center justify-center gap-2 font-semibold rounded-xl transition-all duration-150 cursor-pointer text-[#007041] hover:bg-[#F0FDF4] px-4 py-2',
    }[variant];

    const sizeClass = {
      sm: 'btn-sm',
      md: 'btn-md',
      lg: 'btn-lg',
    }[size];

    return (
      <button
        ref={ref}
        className={cn(variantClass, sizeClass, 'disabled:opacity-50 disabled:cursor-not-allowed disabled:active:transform-none', className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button3D.displayName = 'Button3D';

export { Button3D };
export default Button3D;
